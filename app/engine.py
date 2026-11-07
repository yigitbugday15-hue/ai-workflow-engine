"""Workflow engine v2: transform, http, filter, if, wait, notify, delay, webhook."""
from __future__ import annotations
import time, uuid
import httpx

SUPPORTED = ["transform", "http", "filter", "if", "wait", "notify", "webhook"]


def run_http(step: dict, ctx: dict) -> dict:
    url = step.get("url", "")
    method = step.get("method", "GET").upper()
    if not url:
        raise ValueError("http step needs url")
    timeout = step.get("timeout", 10)
    with httpx.Client(timeout=timeout) as client:
        resp = client.request(method, url, json=ctx if method == "POST" else None)
        return {"status_code": resp.status_code, "body": resp.text[:2000]}


def run_transform(step: dict, ctx: dict) -> dict:
    mapping = step.get("map", {})
    out = dict(ctx)
    for k, v in mapping.items():
        out[k] = ctx.get(v, v)
    op = step.get("op")
    if op == "uppercase" and "text" in out:
        out["text"] = str(out["text"]).upper()
    elif op == "lowercase" and "text" in out:
        out["text"] = str(out["text"]).lower()
    elif op == "prefix" and "text" in out:
        out["text"] = f"{step.get('prefix','')}{out['text']}"
    elif op == "append_context" and "text" in out:
        out["text"] = f"{out['text']} — {step.get('suffix','')}"
    return out


def run_filter(step: dict, ctx: dict) -> dict:
    field, expected = step.get("field"), step.get("equals")
    actual = ctx.get(field)
    if actual != expected:
        return {**ctx, "filtered": True, "reason": f"{field} != {expected}"}
    return ctx


def run_if(step: dict, ctx: dict) -> dict:
    field = step.get("field")
    actual = ctx.get(field)
    cond_true = step.get("then", "continue")
    cond_false = step.get("else", "continue")
    branch = cond_true if actual == step.get("equals") else cond_false
    return {**ctx, "if_branch": branch}


def run_step(step: dict, ctx: dict) -> dict:
    stype = step.get("type")
    if stype == "transform":
        return run_transform(step, ctx)
    if stype == "http":
        return run_http(step, ctx)
    if stype == "filter":
        return run_filter(step, ctx)
    if stype == "if":
        return run_if(step, ctx)
    if stype == "wait":
        time.sleep(min(3, step.get("seconds", 0)))
        return ctx
    if stype == "notify":
        return {**ctx, "notify": step.get("message", "done")}
    if stype == "webhook":
        # simulate outbound webhook delivery
        return {**ctx, "webhook_sent_to": step.get("url", "https://example.com/hook"), "webhook": step.get("payload", ctx)}
    raise ValueError(f"Unknown step type: {stype}")


def execute_workflow(steps: list[dict], initial_ctx: dict | None = None, dry_run: bool = False) -> dict:
    ctx = dict(initial_ctx or {})
    run_id = str(uuid.uuid4())
    logs = []
    started = time.time()
    for i, step in enumerate(steps):
        if dry_run and step.get("type") == "http":
            logs.append({"step": i, "type": step.get("type"), "status": "skipped (dry_run)", "attempt": 1})
            continue
        retries = step.get("retries", 1)
        last_err = None
        for attempt in range(1, retries + 1):
            try:
                ctx = run_step(step, ctx)
                logs.append({"step": i, "type": step.get("type"), "status": "ok", "attempt": attempt})
                last_err = None
                break
            except Exception as e:
                last_err = str(e)
                logs.append({"step": i, "type": step.get("type"), "status": f"error attempt {attempt}: {last_err}", "attempt": attempt})
        if last_err:
            return {"run_id": run_id, "status": "failed", "error": last_err, "logs": logs, "data": ctx, "dry_run": dry_run,
                    "duration_ms": round((time.time() - started) * 1000)}
    return {"run_id": run_id, "status": "completed", "logs": logs, "data": ctx, "dry_run": dry_run,
            "duration_ms": round((time.time() - started) * 1000)}

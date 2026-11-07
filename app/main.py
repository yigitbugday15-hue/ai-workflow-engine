from collections import deque
from fastapi import FastAPI
from pydantic import BaseModel, Field
from .engine import execute_workflow, SUPPORTED

app = FastAPI(title="AI Workflow Engine", version="2.0.0")
_history: deque = deque(maxlen=100)


class RunIn(BaseModel):
    steps: list[dict] = Field(min_length=1)
    context: dict = {}
    dry_run: bool = False


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0", "steps_supported": SUPPORTED}


@app.post("/run")
def run(payload: RunIn):
    result = execute_workflow(payload.steps, payload.context, dry_run=payload.dry_run)
    _history.append({"run_id": result["run_id"], "status": result["status"], "steps": len(payload.steps)})
    return result


@app.post("/webhook")
def webhook(payload: RunIn):
    result = execute_workflow(payload.steps, payload.context, dry_run=payload.dry_run)
    result["trigger"] = "webhook"
    _history.append({"run_id": result["run_id"], "status": result["status"], "steps": len(payload.steps), "trigger": "webhook"})
    return result


@app.get("/history")
def history():
    return {"runs": list(_history)}


@app.post("/validate")
def validate(payload: RunIn):
    errs = []
    for i, s in enumerate(payload.steps):
        if s.get("type") not in SUPPORTED:
            errs.append(f"Step {i}: unknown type '{s.get('type')}'")
        if s.get("type") == "http" and not s.get("url"):
            errs.append(f"Step {i}: http step needs url")
    return {"valid": len(errs) == 0, "errors": errs}

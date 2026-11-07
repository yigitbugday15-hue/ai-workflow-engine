# AI Workflow Engine

![Python](https://img.shields.io/badge/python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-2.x-green) ![Workflows](https://img.shields.io/badge/automation-workflows-purple) ![License](https://img.shields.io/badge/license-MIT-lightblue)

**FastAPI + Intelligent Workflow Automation** — Chain steps, trigger via webhook, get reliable execution with retries.

A lightweight alternative to heavy automation platforms for custom business logic: transform data, call HTTP APIs, filter, branch, wait, and notify — with structured run logs.

## ✨ Features (v2)
- 🔗 Step chaining with shared context (transform / http / filter / **if** / wait / notify / **webhook**)
- 🔁 Per-step retries + timeouts + **dry-run** mode (skip HTTP)
- 📥 Webhook trigger (`/webhook`) + direct run (`/run`) + `/validate` + `/history`
- 📋 Structured execution logs + duration + run history (last 100 runs)
- ✅ Tested, Docker-ready, CI

## 🚀 Quick Start
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 📡 Example
```bash
curl -X POST localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "steps": [
      {"type": "transform", "op": "uppercase"},
      {"type": "if", "field": "plan", "equals": "pro", "then": "premium", "else": "basic"},
      {"type": "notify", "message": "Ticket processed"}
    ],
    "context": {"text": "hello remote team", "plan": "pro"}
  }'
```

Response:
```json
{
  "run_id": "...",
  "status": "completed",
  "duration_ms": 3,
  "logs": [
    {"step": 0, "type": "transform", "status": "ok", "attempt": 1},
    {"step": 1, "type": "if", "status": "ok", "attempt": 1}
  ],
  "data": {"text": "HELLO REMOTE TEAM", "plan": "pro", "if_branch": "premium", "notify": "Ticket processed"}
}
```

## 📚 More endpoints
```bash
curl -X POST localhost:8000/webhook ...           # same as /run + trigger: webhook
curl -X POST localhost:8000/validate -d '{"steps":[{"type":"http"}]}'  # check workflow
curl localhost:8000/history                        # recent runs
```

## 🧪 Tests
```bash
pytest -q   # 4 tests
```

## 🐳 Docker
```bash
docker build -t ai-workflow-engine .
docker run -p 8000:8000 ai-workflow-engine
```

## 🛠 Tech Stack
Python · FastAPI · Pydantic · httpx · Uvicorn · Docker · GitHub Actions

## 👤 Author
**Yiğit Buğday** — AI Automation Engineer (Remote, EU/US timezones)

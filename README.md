# Multi-LLM Cost Optimizer

A Python/FastAPI starter for routing LLM requests, inspecting configured models, and tracking estimated usage costs.

**[Portfolio](https://github.com/Reactance0083)** · **Status: implemented developer starter**

## What the source implements

- `GET /health`: startup health and configured model names.
- `GET /models`: example model table, provider configuration, and cost estimates.
- `GET /stats`: in-memory usage for the current process.
- `POST /complete`: structured routing and a provider call through LiteLLM.
- Fallback selection for unexpected router failures and invalid/unconfigured model choices.

The routing path currently uses an Anthropic-backed PydanticAI agent. Live completion therefore requires `ANTHROPIC_API_KEY` for routing plus the credential for the selected completion provider. Setting only an OpenAI or Groq key is insufficient for the current router. Explicit configuration/dependency errors are returned rather than silently bypassed.

## Workflow

Request and quality tier → structured routing decision → provider completion → token/cost record → response.

The quality tiers are `fast`, `standard`, `quality`, and `max`. They guide selection; they are not independently benchmarked quality guarantees.

## Quick start without credentials

Python 3.11 or later.

```bash
git clone https://github.com/Reactance0083/pydantic-ai-multi-llm-cost-optimizer.git
cd pydantic-ai-multi-llm-cost-optimizer
python -m venv .venv
```

Activate on macOS/Linux:

```bash
source .venv/bin/activate
```

Activate in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then:

```bash
python -m pip install -r requirements.txt
python smoke_test.py
python -m uvicorn main:app --host 127.0.0.1 --port 8002
```

Open [the API documentation](http://127.0.0.1:8002/docs). The existing smoke test checks import/startup and the safe health, model, and statistics endpoints without calling a model.

## Optional live provider calls

Install `requirements-providers.txt`, copy `.env.example` to `.env`, and configure the required provider credentials. The app reads `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and `GROQ_API_KEY`. Live calls use your provider accounts and may incur usage charges.

Example request in a POSIX shell:

```bash
curl http://127.0.0.1:8002/complete \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Explain a webhook in two sentences.","quality":"standard","task_type":"general","max_tokens":150}'
```

PowerShell equivalent:

```powershell
$body = @{prompt="Explain a webhook in two sentences."; quality="standard"; task_type="general"; max_tokens=150} | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8002/complete -Method Post -ContentType "application/json" -Body $body
```

## Design limits

Costs use the example table in `main.py`; they are not billing records, and router-call costs are not included in completion statistics. Usage resets when the process restarts. Model availability and provider compatibility need checking against the accounts and dependency versions used.

The starter does not implement production authentication, durable usage storage, or rate limiting. It is a local developer project, with no guaranteed savings percentage or hosted-service SLA.

## Additional implementation material

The existing [Production Acceleration Kit](https://reactance0083.gumroad.com/l/ztmlv) is a separate commercial offering. This repository can be inspected and run locally without purchasing it; provider credits and hosting are separate.

Developed with AI assistance. Documentation reviewed against the public source on November 10, 2026.

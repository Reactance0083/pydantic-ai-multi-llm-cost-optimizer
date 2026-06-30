# Multi-LLM Cost Optimizer

A FastAPI starter for developers who want a practical way to route LLM requests across configured providers, inspect estimated spend, and avoid starting from a blank repo.

This repository is the free trust and education layer. It gives you readable source code, basic local setup, and a no-credential smoke test so you can inspect the approach before buying anything.

The paid Gumroad product is the **$29 Production Acceleration Kit**. It exists for developers who like the starter and want to save implementation time with deployment guidance, production hardening, routing playbooks, operations checklists, premium examples, buyer verification steps, architecture notes, commercial license notes, and version history.

Start here:

| Path | Best for | Link |
|---|---|---|
| Free GitHub starter | Inspecting the code, running the basic app, and deciding whether the approach fits | [Use this repo](https://github.com/Reactance0083/pydantic-ai-multi-llm-cost-optimizer) |
| $29 Production Acceleration Kit | Moving faster from local starter to safer deployment and verification | [Get the Gumroad kit](https://reactance0083.gumroad.com/l/ztmlv) |

## What Problem This Solves

Building an LLM workflow usually creates the same early questions:

- Which provider/model should this request use?
- How do I expose routing through a small API?
- How do I see estimated per-model spend while testing?
- What should I verify before putting this behind a real workflow?
- What production notes, hardening decisions, and examples do I need before adapting it?

The free starter answers the first implementation questions. The paid kit helps with the deployment, hardening, verification, and operating questions that usually consume extra time after the code runs locally.

## Free vs Paid

| Need | Free GitHub starter | $29 Production Acceleration Kit |
|---|---:|---:|
| Working FastAPI starter source | Yes | Yes |
| Basic README setup | Yes | Yes |
| `.env.example` | Yes | Yes |
| Base requirements | Yes | Yes |
| Optional provider requirements | Yes | Yes |
| No-credential smoke test | Yes | Yes |
| Production deployment guide | No | Yes |
| Production hardening guide | No | Yes |
| Routing policy playbook | No | Yes |
| Operations checklist | No | Yes |
| Premium request examples | No | Yes |
| Buyer verification checklist | No | Yes |
| Optional provider test plan | No | Yes |
| Architecture decision notes | No | Yes |
| Commercial license notes | No | Yes |
| Changelog and version history | No | Yes |

Use the free repo to learn and evaluate. Buy the Gumroad kit if the approach fits and the premium material would save you deployment, hardening, routing, and verification time.

## What Works

- `GET /health` starts without API keys and reports which providers are configured.
- `GET /models` lists the example model table, configured models, and estimated costs.
- `GET /stats` reports in-memory usage totals for the current process.
- `POST /complete` routes and executes a prompt when optional provider dependencies and at least one provider key are configured.
- If the pydantic-ai router fails, the app falls back to the configured model for the requested quality tier.

## Important Limits

- Cost values are estimates and must be checked against current provider pricing before financial use.
- Stats are stored in memory. Use Redis, Postgres, or another durable store before production deployment.
- Routing quality depends on your configured providers, prompts, model availability, and API accounts.
- This template does not guarantee a specific savings percentage.
- This is a developer starter, not a hosted SaaS.
- Provider API credits, hosted deployment, and guaranteed support response times are not included.

## Files In This Free Repo

- `main.py` - FastAPI app and routing logic.
- `requirements.txt` - Base Python dependencies.
- `requirements-providers.txt` - Optional dependencies for live provider routing/calls.
- `.env.example` - Provider key template.
- `smoke_test.py` - No-credential smoke test for import/startup and safe endpoints.
- `README.md` - Setup and usage guide.

## Quick Start

```bash
python -m venv .venv
.venv\Scriptsctivate
pip install -r requirements.txt
copy .env.example .env
python smoke_test.py
uvicorn main:app --reload --port 8002
```

Open:

- `http://localhost:8002/health`
- `http://localhost:8002/models`
- `http://localhost:8002/stats`

For live LLM calls through `/complete`, also install the optional provider stack:

```bash
pip install -r requirements-providers.txt
```

Add one or more provider keys to `.env`:

```env
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
```

## API Usage

```bash
curl -X POST http://localhost:8002/complete ^
  -H "Content-Type: application/json" ^
  -d "{"prompt":"Summarize REST vs GraphQL","quality":"standard","task_type":"general"}"
```

## Quality Tiers

| Tier | Intended Use |
|---|---|
| `fast` | Low-stakes classification, summaries, and short transformations |
| `standard` | General development and operations tasks |
| `quality` | Code generation, complex analysis, and higher-stakes responses |
| `max` | Hardest prompts where cost is secondary to quality |

## Why The Paid Kit Exists

The free repo is enough if you only want to study or adapt the starter yourself.

The paid kit exists for developers who want the operational material that usually gets rebuilt from scratch: deployment steps, hardening decisions, routing policies, verification checklists, examples, architecture notes, license notes, and release history. It sells implementation acceleration, not hidden magic.

Next step: [inspect the free starter](https://github.com/Reactance0083/pydantic-ai-multi-llm-cost-optimizer), then buy the [$29 Production Acceleration Kit](https://reactance0083.gumroad.com/l/ztmlv) if the premium guidance would save you time.

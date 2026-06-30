# Multi-LLM Cost Optimizer

FastAPI starter template for routing LLM prompts across configured providers and tracking estimated per-model spend.

This public repository is the free trust-building starter. It gives you the working source code, basic setup, and a no-credential smoke test so you can inspect the approach before buying anything.

The paid Gumroad product is a **Production Acceleration Kit**. It adds deployment guidance, hardening checklists, routing policy guidance, premium examples, buyer verification steps, architecture decisions, and versioned release notes. It is for developers who want to move faster from "this runs locally" to "I know how to deploy, verify, and adapt this safely."

Paid kit: https://reactance0083.gumroad.com/l/ztmlv

## Free vs Paid

| Need | Free GitHub repo | Gumroad Production Acceleration Kit |
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
| Changelog and versioned release bundle | No | Yes |

Use the free repo to learn and evaluate. Buy the Gumroad kit if the approach fits and you want the implementation guidance that saves deployment and verification time.

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
.venv\Scripts\activate
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
  -d "{\"prompt\":\"Summarize REST vs GraphQL\",\"quality\":\"standard\",\"task_type\":\"general\"}"
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

The paid kit exists for developers who want the operational material that usually gets rebuilt from scratch: deployment steps, hardening decisions, routing policies, verification checklists, examples, and release history. It sells implementation acceleration, not hidden magic.

## License and Support

This public starter is provided as a code reference. The Gumroad package includes the premium implementation assets and future package updates when released. Provider API credits, hosted deployment, and guaranteed support response times are not included.

# Multi-LLM Cost Optimizer

FastAPI starter template for routing LLM prompts across configured providers and tracking estimated per-model spend.

It uses:

- `pydantic-ai` for the routing decision.
- `litellm` for provider calls.
- FastAPI endpoints for completion, model visibility, health checks, and usage stats.

This is a developer starter, not a hosted SaaS. You run it with your own API keys.

## What Works

- `GET /health` starts without API keys and reports which providers are configured.
- `GET /models` lists the example model table, configured models, and estimated costs.
- `GET /stats` reports in-memory usage totals for the current process.
- `POST /complete` routes and executes a prompt when at least one provider key is configured.
- If the pydantic-ai router fails, the app falls back to the configured model for the requested quality tier.

## Important Limits

- Cost values are estimates and must be checked against current provider pricing before financial use.
- Stats are stored in memory. Use Redis, Postgres, or another durable store before production deployment.
- Routing quality depends on your configured providers, prompts, model availability, and API accounts.
- This template does not guarantee a specific savings percentage.

## Files Included

- `main.py` - FastAPI app and routing logic.
- `requirements.txt` - Python dependencies.
- `.env.example` - Provider key template.
- `smoke_test.py` - No-credential smoke test for import/startup and safe endpoints.
- `README.md` - Setup and usage guide.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Add one or more provider keys to `.env`:

```env
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
```

Run the API:

```bash
uvicorn main:app --reload --port 8002
```

Open:

- `http://localhost:8002/health`
- `http://localhost:8002/models`
- `http://localhost:8002/stats`

## No-Credential Smoke Test

Use this before adding API keys:

```bash
python smoke_test.py
```

The smoke test verifies that the app imports, starts, and exposes the safe endpoints without making provider calls.

## API Usage

### POST /complete

Requires at least one provider API key.

```bash
curl -X POST http://localhost:8002/complete ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\":\"Summarize REST vs GraphQL\",\"quality\":\"standard\",\"task_type\":\"general\"}"
```

Example response shape:

```json
{
  "text": "...",
  "model_used": "anthropic/claude-haiku-4-5-20251001",
  "input_tokens": 42,
  "output_tokens": 218,
  "cost_usd": 0.001132,
  "latency_ms": 847
}
```

### GET /stats

```json
{
  "models": {
    "anthropic/claude-haiku-4-5-20251001": {
      "calls": 3,
      "total_cost": 0.0062,
      "total_tokens": 1240
    }
  },
  "total_cost_usd": 0.0062,
  "total_calls": 3
}
```

## Example Cost Table

These are example USD estimates per 1K input/output tokens. Verify them before relying on the numbers.

| Model | Input/1K | Output/1K | Best For |
|---|---:|---:|---|
| groq/llama-3.1-8b-instant | $0.00005 | $0.00008 | Fast, simple tasks |
| groq/llama-3.3-70b-versatile | $0.00059 | $0.00079 | Standard low-cost tasks |
| anthropic/claude-haiku-4-5-20251001 | $0.001 | $0.005 | Structured routing and classification |
| openai/gpt-4.1-mini | $0.0004 | $0.0016 | General tasks |
| anthropic/claude-sonnet-4-5-20250929 | $0.003 | $0.015 | Code and complex reasoning |
| openai/gpt-4.1 | $0.002 | $0.008 | Complex tasks |
| anthropic/claude-opus-4-6-20260205 | $0.005 | $0.025 | Highest-quality tier |

## Quality Tiers

| Tier | Intended Use |
|---|---|
| `fast` | Low-stakes classification, summaries, and short transformations |
| `standard` | General development and operations tasks |
| `quality` | Code generation, complex analysis, and higher-stakes responses |
| `max` | Hardest prompts where cost is secondary to quality |

## Production Notes

Before using this in production:

- Replace in-memory stats with durable storage.
- Add authentication and rate limiting.
- Add provider-specific retry and timeout policies.
- Log routing decisions for review.
- Confirm model availability and pricing for your accounts.

## Commercial Readiness Checklist

- Install from a clean ZIP extraction.
- Run `python smoke_test.py`.
- Start `uvicorn main:app --port 8002`.
- Verify `/health`, `/models`, and `/stats`.
- With API keys configured, make one controlled `/complete` call and confirm `/stats` increments.
- Confirm the Gumroad listing describes this as a starter template, not a hosted product or guaranteed-cost-savings system.

## License and Support

Buying the package includes the source files listed above and future package updates when released. It does not include provider API credits or a hosted deployment.

# Multi-LLM Cost Optimizer (pydantic-ai + litellm + FastAPI)

Routes every prompt to the cheapest model that can handle it well. Uses `pydantic-ai` for the routing decision and `litellm` for unified execution across Claude, GPT-4o, and Groq. Tracks cost per model with a live `/stats` endpoint.

## What It Does

1. Receives a prompt with a quality tier (`fast` / `standard` / `quality` / `max`)
2. Routes to the cheapest appropriate model using `claude-haiku-4-5` as the router
3. Executes via litellm (handles auth + API differences for all providers)
4. Returns the response with cost breakdown and latency

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in at minimum ANTHROPIC_API_KEY. OPENAI and GROQ are optional.
uvicorn main:app --reload --port 8002
```

## API Usage

### POST /complete

```bash
curl -X POST http://localhost:8002/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Summarize the key differences between REST and GraphQL",
    "quality": "standard",
    "task_type": "general"
  }'
```

Response:
```json
{
  "text": "...",
  "model_used": "anthropic/claude-haiku-4-5",
  "input_tokens": 42,
  "output_tokens": 218,
  "cost_usd": 0.000283,
  "latency_ms": 847
}
```

### GET /stats

```json
{
  "models": {
    "anthropic/claude-haiku-4-5": {"calls": 47, "total_cost": 0.0134, "total_tokens": 52400}
  },
  "total_cost_usd": 0.0134,
  "total_calls": 47
}
```

## Cost Table (May 2026)

| Model | Input/1k | Output/1k | Best For |
|-------|----------|-----------|---------|
| groq/llama-3.1-8b-instant | $0.00005 | $0.00008 | Fast, simple tasks |
| anthropic/claude-haiku-4-5 | $0.00025 | $0.00125 | Structured outputs, classification |
| openai/gpt-4o-mini | $0.00015 | $0.0006 | General tasks, good value |
| anthropic/claude-sonnet-4-5 | $0.003 | $0.015 | Code, complex reasoning |
| openai/gpt-4o | $0.0025 | $0.01 | Complex tasks |
| anthropic/claude-opus-4-5 | $0.015 | $0.075 | Hardest tasks only |

## Quality Tiers

| Tier | Models Considered | Use When |
|------|------------------|---------|
| `fast` | Groq llama-8b, Claude haiku | Low-stakes, high-volume, simple classification |
| `standard` | Groq llama-70b, GPT-4o-mini, Claude haiku | Most production tasks |
| `quality` | Claude sonnet, GPT-4o | Code generation, complex analysis |
| `max` | Claude opus | Hardest problems, highest stakes |

## Structured Routing (pydantic-ai)

```python
class RoutingDecision(BaseModel):
    model: str           # exact litellm model string
    reason: str          # 1-sentence justification
    expected_tokens: int # rough output estimate
```

## Architecture

```
POST /complete
  → routing agent (claude-haiku-4-5) → RoutingDecision
  → litellm.completion(model=decision.model, ...)
  → cost calculation → response + /stats update
```

## Requirements

- Python 3.11+
- Anthropic API key (required)
- OpenAI API key (optional, enables GPT routing)
- Groq API key (optional, enables cheapest tier)

---

## Get the Complete Bundle

All 5 templates are available individually or as a **$39 bundle** (saves $15 vs individual).

| Template | Price | Link |
|----------|-------|------|
| Slack → Notion Automation | $9 | [Buy on Gumroad](https://reactance0083.gumroad.com/l/slack-notion-pydantic-ai) |
| GitHub Issue → Linear Triage | $9 | [Buy on Gumroad](https://reactance0083.gumroad.com/l/github-linear-triage-pydantic-ai) |
| Multi-LLM Cost Optimizer | $12 | [Buy on Gumroad](https://reactance0083.gumroad.com/l/multi-llm-cost-optimizer) |
| Web Scraper + Semantic Search | $9 | [Buy on Gumroad](https://reactance0083.gumroad.com/l/web-scraper-semantic-search-pydantic-ai) |
| Prompt Engineering Runbook | $15 | [Buy on Gumroad](https://reactance0083.gumroad.com/l/prompt-engineering-runbook-pydantic-ai) |
| **Complete Bundle (all 5)** | **$39** | [Buy on Gumroad](https://reactance0083.gumroad.com/l/pydantic-ai-fastapi-bundle) |

Buying includes: all source files, README, requirements.txt, .env.example, and lifetime updates.

> **Free to use** — the source is here on GitHub. Buying supports continued development and gets you a clean download with everything packaged.

---

*Built by [Wade Allen](https://github.com/Reactance0083) — AI Workflow Architect*

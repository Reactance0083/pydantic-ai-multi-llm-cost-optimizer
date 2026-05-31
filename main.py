"""
Multi-LLM Cost Optimizer
Routes prompts to the cheapest model that meets quality requirements.
Uses pydantic-ai for structured routing decisions and litellm for unified model calls.

Endpoints:
  POST /complete    — Route and complete a prompt
  GET  /stats       — Cost/usage breakdown by model
  GET  /health      — Health check
"""
import sys, os, time
sys.path.insert(0, r"C:\pylib")

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent
from dotenv import load_dotenv
import litellm
import httpx

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "")    # optional
GROQ_API_KEY      = os.getenv("GROQ_API_KEY", "")      # optional (very cheap)

if not ANTHROPIC_API_KEY:
    raise RuntimeError("Missing ANTHROPIC_API_KEY")

os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY


# ── Cost table (USD per 1k tokens, input/output) ──────────────────────────────
MODEL_COSTS = {
    "anthropic/claude-haiku-4-5":         {"input": 0.00025, "output": 0.00125},
    "anthropic/claude-sonnet-4-5":        {"input": 0.003,   "output": 0.015},
    "anthropic/claude-opus-4-5":          {"input": 0.015,   "output": 0.075},
    "groq/llama-3.1-8b-instant":          {"input": 0.00005, "output": 0.00008},
    "groq/llama-3.3-70b-versatile":       {"input": 0.00059, "output": 0.00079},
    "openai/gpt-4o-mini":                 {"input": 0.00015, "output": 0.0006},
    "openai/gpt-4o":                      {"input": 0.0025,  "output": 0.01},
}

# Available models in priority order (cheapest → most capable)
MODELS_BY_tier = {
    "fast":     ["groq/llama-3.1-8b-instant", "anthropic/claude-haiku-4-5"],
    "standard": ["groq/llama-3.3-70b-versatile", "openai/gpt-4o-mini", "anthropic/claude-haiku-4-5"],
    "quality":  ["anthropic/claude-sonnet-4-5", "openai/gpt-4o"],
    "max":      ["anthropic/claude-opus-4-5"],
}

# In-memory stats (replace with Redis/DB for production)
_stats: dict[str, dict] = {}


# ── Pydantic models ───────────────────────────────────────────────────────────
class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 1024
    quality: str = "standard"  # fast | standard | quality | max
    task_type: str = "general" # general | code | creative | analysis | translation


class RoutingDecision(BaseModel):
    model: str   # exact litellm model string from MODEL_COSTS keys
    reason: str  # 1-sentence justification
    expected_tokens: int  # rough output token estimate


class CompletionResponse(BaseModel):
    text: str
    model_used: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int


# ── pydantic-ai router ────────────────────────────────────────────────────────
AVAILABLE_MODELS = list(MODEL_COSTS.keys())

router = Agent(
    "anthropic:claude-haiku-4-5",
    result_type=RoutingDecision,
    system_prompt=(
        f"You are a cost-optimization router. Select the cheapest model that can handle the task well.\n"
        f"Available models: {', '.join(AVAILABLE_MODELS)}\n"
        f"Rules:\n"
        f"- 'fast' quality: prefer groq models (ultra cheap, good for simple tasks)\n"
        f"- 'standard' quality: prefer haiku or gpt-4o-mini (cheap + capable)\n"
        f"- 'quality' quality: use sonnet or gpt-4o (complex reasoning, long outputs)\n"
        f"- 'max' quality: use claude-opus only (hardest tasks, highest accuracy required)\n"
        f"- Code generation always benefits from sonnet+ even at standard quality\n"
        f"- Translation and summarization work well with haiku/groq\n"
        f"- Only select groq models if GROQ_API_KEY is available\n"
        f"Return the exact model string from the available list."
    ),
)


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="Multi-LLM Cost Optimizer", version="1.0.0")


@app.post("/complete", response_model=CompletionResponse)
async def complete(req: CompletionRequest):
    # Step 1: Route to cheapest appropriate model
    routing_prompt = (
        f"Task type: {req.task_type}\n"
        f"Quality tier: {req.quality}\n"
        f"Prompt length: {len(req.prompt)} chars\n"
        f"Max tokens: {req.max_tokens}\n"
        f"Prompt preview: {req.prompt[:300]}"
    )
    routing_result = await router.run(routing_prompt)
    decision = routing_result.data

    model = decision.model
    # Fallback if router picks unavailable model
    if model not in MODEL_COSTS:
        model = "anthropic/claude-haiku-4-5"

    # Step 2: Execute via litellm
    start = time.monotonic()
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": req.prompt}],
        max_tokens=req.max_tokens,
    )
    latency_ms = int((time.monotonic() - start) * 1000)

    # Step 3: Calculate cost
    usage = response.usage
    input_tok  = usage.prompt_tokens
    output_tok = usage.completion_tokens
    costs      = MODEL_COSTS.get(model, {"input": 0, "output": 0})
    cost_usd   = (input_tok * costs["input"] + output_tok * costs["output"]) / 1000

    # Step 4: Update stats
    if model not in _stats:
        _stats[model] = {"calls": 0, "total_cost": 0.0, "total_tokens": 0}
    _stats[model]["calls"]        += 1
    _stats[model]["total_cost"]   += cost_usd
    _stats[model]["total_tokens"] += input_tok + output_tok

    text = response.choices[0].message.content or ""

    return CompletionResponse(
        text=text,
        model_used=model,
        input_tokens=input_tok,
        output_tokens=output_tok,
        cost_usd=round(cost_usd, 6),
        latency_ms=latency_ms,
    )


@app.get("/stats")
def stats():
    total_cost = sum(v["total_cost"] for v in _stats.values())
    return {
        "models": _stats,
        "total_cost_usd": round(total_cost, 6),
        "total_calls": sum(v["calls"] for v in _stats.values()),
    }


@app.get("/models")
def models():
    return {"available": AVAILABLE_MODELS, "costs": MODEL_COSTS}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)

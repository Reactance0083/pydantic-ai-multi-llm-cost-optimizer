"""
Multi-LLM Cost Optimizer

Routes prompts to a lower-cost model when the requested quality tier allows it,
executes the request through LiteLLM, and tracks estimated usage cost.
"""

import os
import time
from importlib import import_module
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

for env_name, env_value in {
    "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "GROQ_API_KEY": GROQ_API_KEY,
}.items():
    if env_value:
        os.environ[env_name] = env_value


# Example USD pricing per 1K tokens. Verify against provider pricing pages
# before using the estimates for billing or finance decisions.
MODEL_COSTS = {
    "anthropic/claude-haiku-4-5-20251001": {"input": 0.001, "output": 0.005},
    "anthropic/claude-sonnet-4-5-20250929": {"input": 0.003, "output": 0.015},
    "anthropic/claude-opus-4-6-20260205": {"input": 0.005, "output": 0.025},
    "groq/llama-3.1-8b-instant": {"input": 0.00005, "output": 0.00008},
    "groq/llama-3.3-70b-versatile": {"input": 0.00059, "output": 0.00079},
    "openai/gpt-4.1-mini": {"input": 0.0004, "output": 0.0016},
    "openai/gpt-4.1": {"input": 0.002, "output": 0.008},
}

MODELS_BY_TIER = {
    "fast": ["groq/llama-3.1-8b-instant", "anthropic/claude-haiku-4-5-20251001"],
    "standard": [
        "groq/llama-3.3-70b-versatile",
        "openai/gpt-4.1-mini",
        "anthropic/claude-haiku-4-5-20251001",
    ],
    "quality": ["anthropic/claude-sonnet-4-5-20250929", "openai/gpt-4.1"],
    "max": [
        "anthropic/claude-opus-4-6-20260205",
        "anthropic/claude-sonnet-4-5-20250929",
    ],
}

_stats: dict[str, dict] = {}


class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 1024
    quality: str = "standard"
    task_type: str = "general"


class RoutingDecision(BaseModel):
    model: str
    reason: str
    expected_tokens: int


class CompletionResponse(BaseModel):
    text: str
    model_used: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int


class ModelInfo(BaseModel):
    available: list[str]
    configured: list[str]
    costs: dict[str, dict[str, float]]
    note: str


app = FastAPI(title="Multi-LLM Cost Optimizer", version="1.0.1")


def provider_is_configured(model: str) -> bool:
    if model.startswith("anthropic/"):
        return bool(ANTHROPIC_API_KEY)
    if model.startswith("openai/"):
        return bool(OPENAI_API_KEY)
    if model.startswith("groq/"):
        return bool(GROQ_API_KEY)
    return False


def configured_models() -> list[str]:
    return [model for model in MODEL_COSTS if provider_is_configured(model)]


def choose_fallback_model(quality: str) -> str:
    candidates = MODELS_BY_TIER.get(quality, MODELS_BY_TIER["standard"])
    for model in candidates:
        if provider_is_configured(model):
            return model
    raise HTTPException(
        status_code=400,
        detail="No API key is configured for the requested quality tier.",
    )


@lru_cache(maxsize=1)
def get_router():
    if not ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="ANTHROPIC_API_KEY is required for pydantic-ai routing.",
        )
    try:
        Agent = import_module("pydantic_ai").Agent
    except ImportError as exc:
        raise HTTPException(
            status_code=501,
            detail=(
                "Provider routing requires optional dependencies. "
                "Install them with: pip install -r requirements-providers.txt"
            ),
        ) from exc

    system_prompt = (
        "You are a cost-optimization router. Select the cheapest configured "
        "model that can handle the task well.\n"
        f"Configured models: {', '.join(configured_models())}\n"
        "Rules:\n"
        "- fast quality: prefer Groq models for simple tasks when configured\n"
        "- standard quality: prefer Groq 70B, GPT-4.1 mini, or Claude Haiku\n"
        "- quality tier: use Claude Sonnet or GPT-4.1\n"
        "- max tier: use Claude Opus or Claude Sonnet\n"
        "- code generation usually benefits from the quality tier or higher\n"
        "Return the exact model string from the configured model list."
    )

    try:
        return Agent(
            "anthropic:claude-haiku-4-5-20251001",
            output_type=RoutingDecision,
            system_prompt=system_prompt,
        )
    except TypeError:
        return Agent(
            "anthropic:claude-haiku-4-5-20251001",
            result_type=RoutingDecision,
            system_prompt=system_prompt,
        )


def extract_routing_decision(routing_result) -> RoutingDecision:
    decision = getattr(routing_result, "output", None)
    if decision is None:
        decision = getattr(routing_result, "data", None)
    if isinstance(decision, RoutingDecision):
        return decision
    return RoutingDecision(
        model=choose_fallback_model("standard"),
        reason="Router returned an unexpected shape, so the app used the standard fallback model.",
        expected_tokens=512,
    )


async def route_request(req: CompletionRequest) -> RoutingDecision:
    routing_prompt = (
        f"Task type: {req.task_type}\n"
        f"Quality tier: {req.quality}\n"
        f"Prompt length: {len(req.prompt)} chars\n"
        f"Max tokens: {req.max_tokens}\n"
        f"Prompt preview: {req.prompt[:300]}"
    )

    try:
        routing_result = await get_router().run(routing_prompt)
        decision = extract_routing_decision(routing_result)
    except HTTPException:
        raise
    except Exception:
        model = choose_fallback_model(req.quality)
        return RoutingDecision(
            model=model,
            reason="Router failed, so the app used the configured fallback for this quality tier.",
            expected_tokens=req.max_tokens,
        )

    if decision.model not in MODEL_COSTS or not provider_is_configured(decision.model):
        decision.model = choose_fallback_model(req.quality)
    return decision


@app.post("/complete", response_model=CompletionResponse)
async def complete(req: CompletionRequest):
    if not configured_models():
        raise HTTPException(
            status_code=400,
            detail="Set at least one provider API key before calling /complete.",
        )
    try:
        litellm = import_module("litellm")
    except ImportError as exc:
        raise HTTPException(
            status_code=501,
            detail=(
                "Provider calls require optional dependencies. "
                "Install them with: pip install -r requirements-providers.txt"
            ),
        ) from exc

    decision = await route_request(req)

    start = time.monotonic()
    response = litellm.completion(
        model=decision.model,
        messages=[{"role": "user", "content": req.prompt}],
        max_tokens=req.max_tokens,
    )
    latency_ms = int((time.monotonic() - start) * 1000)

    usage = response.usage
    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens
    costs = MODEL_COSTS.get(decision.model, {"input": 0, "output": 0})
    cost_usd = (
        input_tokens * costs["input"] + output_tokens * costs["output"]
    ) / 1000

    if decision.model not in _stats:
        _stats[decision.model] = {
            "calls": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
        }
    _stats[decision.model]["calls"] += 1
    _stats[decision.model]["total_cost"] += cost_usd
    _stats[decision.model]["total_tokens"] += input_tokens + output_tokens

    text = response.choices[0].message.content or ""

    return CompletionResponse(
        text=text,
        model_used=decision.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
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


@app.get("/models", response_model=ModelInfo)
def models():
    return ModelInfo(
        available=list(MODEL_COSTS.keys()),
        configured=configured_models(),
        costs=MODEL_COSTS,
        note="Cost values are example estimates. Verify provider pricing before relying on them.",
    )


@app.get("/health")
def health():
    return {"status": "ok", "configured_models": configured_models()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)

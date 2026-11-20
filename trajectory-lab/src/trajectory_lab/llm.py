"""One LLM helper for any OpenAI-compatible endpoint (9router, OpenAI, ...).

Configure with OPENAI_BASE_URL, OPENAI_API_KEY and AGENT_MODEL in .env.
"""

from __future__ import annotations

import os

from openai import OpenAI


def chat(system: str, user: str, max_tokens: int = 500) -> tuple[str, dict[str, int], str]:
    """Return (text, usage_details, model_name)."""
    model = os.environ["AGENT_MODEL"]
    resp = OpenAI().chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0,  # repeatable runs
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    usage = resp.usage
    details = {"input": usage.prompt_tokens, "output": usage.completion_tokens} if usage else {}
    return resp.choices[0].message.content or "", details, model

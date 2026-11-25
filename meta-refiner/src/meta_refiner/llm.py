"""Thin chat helper for any OpenAI-compatible endpoint."""

from __future__ import annotations

import os

from openai import BadRequestError, OpenAI
from openai.types.chat import ChatCompletionMessageParam

# Some gateways inject agent tools (shell, ...). The model then calls a tool and returns no text.
NO_TOOLS = "\n\nYou have NO tools and cannot run commands. Reply with a complete plain-text answer."


def chat(
    model_env: str,
    system: str,
    user: str,
    max_tokens: int = 8000,
    temperature: float = 0.0,
    json_mode: bool = False,
) -> str:
    """Call the model named by env var `model_env` (META_MODEL or TARGET_MODEL)."""
    model = os.environ[model_env]
    suffix = "" if json_mode else NO_TOOLS
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system + suffix},
        {"role": "user", "content": user + suffix},
    ]
    client = OpenAI()
    resp = None
    if json_mode:  # the API then guarantees the reply is one valid JSON object
        try:
            resp = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                tool_choice="none",
                messages=messages,
                response_format={"type": "json_object"},
            )
        except BadRequestError:  # endpoint has no JSON mode: rely on the prompt only
            pass
    if resp is None:
        resp = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            tool_choice="none",
            messages=messages,
        )
    choice = resp.choices[0]
    if choice.finish_reason == "length":
        raise RuntimeError(f"{os.environ[model_env]} output cut off at {max_tokens} tokens")
    if not choice.message.content:
        raise RuntimeError(f"{os.environ[model_env]} returned no text ({choice.finish_reason})")
    return choice.message.content

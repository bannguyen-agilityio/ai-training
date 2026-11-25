"""Ask the guardrail model for one JSON object (any OpenAI-compatible endpoint)."""

import json
import os

from openai import BadRequestError, OpenAI
from openai.types.chat import ChatCompletionMessageParam


def ask_json(system: str, user: str) -> dict:
    """Send one chat request and parse the reply as a JSON object.

    Uses the model in env AUDITOR_MODEL. Falls back to plain mode if the endpoint has no JSON mode.

    Args:
        system: System message.
        user: User message.

    Returns:
        The parsed JSON object from the reply.
    """
    model = os.environ["AUDITOR_MODEL"]
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    client = OpenAI()
    try:
        resp = client.chat.completions.create(
            model=model, messages=messages, temperature=0.0, max_tokens=1000,
            tool_choice="none", response_format={"type": "json_object"},
        )
    except BadRequestError:  # endpoint has no JSON mode
        resp = client.chat.completions.create(
            model=model, messages=messages, temperature=0.0, max_tokens=1000, tool_choice="none",
        )
    text = resp.choices[0].message.content or ""
    return json.loads(text[text.index("{"): text.rindex("}") + 1])

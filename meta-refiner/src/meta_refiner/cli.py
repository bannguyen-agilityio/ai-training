"""Run: uv run meta-refine   (it asks for a vague query)."""

from __future__ import annotations

import sys

from dotenv import load_dotenv
from openai import APIError

from .llm import chat as real_chat
from .refiner import answer, refine

DEFAULT_QUERY = "help me set up python"

MODEL_ENV = {"meta": "META_MODEL", "target": "TARGET_MODEL"}


def chat(role: str, system: str, user: str) -> str:
    return real_chat(MODEL_ENV[role], system, user, json_mode=role == "meta")


def main() -> None:
    try:
        run()
    except (APIError, RuntimeError, ValueError, KeyError) as e:  # clean message, no traceback
        sys.exit(f"error: {type(e).__name__}: {e}")


def run() -> None:
    load_dotenv()
    query = input(f"Vague query [{DEFAULT_QUERY}]: ").strip() or DEFAULT_QUERY

    print(
        f"\nTarget answer WITHOUT refine:\n{chat('target', 'You are a helpful assistant.', query)}\n"
    )

    rounds = refine(query, chat)
    for i, r in enumerate(rounds, 1):
        print(f"round {i}: score {r.critique.mean:.2f} {r.critique.scores}")
    final = rounds[-1].draft

    print("\nAssumptions:", *final.assumptions, sep="\n- ")
    print("\nQuestions to ask the user:", *final.clarifying_questions, sep="\n- ")
    print(f"\nRefined system prompt:\n{final.system_prompt}")
    print(f"\nTarget answer WITH refine:\n{answer(final, query, chat)}")


if __name__ == "__main__":
    main()

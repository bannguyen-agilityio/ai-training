"""The refine loop: draft -> critique -> revise, until good enough."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field

from . import prompts

# (role, system, user) -> text. role is "meta" or "target".
Chat = Callable[[str, str, str], str]

CRITERIA = ("coverage", "assumptions", "actionability", "fidelity")


@dataclass
class Draft:
    ambiguities: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    clarifying_questions: list[str] = field(default_factory=list)
    system_prompt: str = ""
    user_prompt: str = ""


@dataclass
class Critique:
    scores: dict[str, int]
    feedback: str

    @property
    def mean(self) -> float:
        return sum(self.scores.get(c, 0) for c in CRITERIA) / len(CRITERIA)


@dataclass
class Round:
    draft: Draft
    critique: Critique


def parse_json(text: str) -> dict:
    """Extract the first JSON object from model text (tolerates fences and chatter)."""
    text = re.sub(r"```(?:json)?", "", text)
    decoder = json.JSONDecoder()
    for m in re.finditer(r"\{", text):  # first "{" that starts a complete object wins
        try:
            obj, _ = decoder.raw_decode(text, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    raise ValueError(f"no JSON object in model output: {text[:200]!r}")


def _draft(data: dict) -> Draft:
    d = Draft(**{k: data.get(k, getattr(Draft(), k)) for k in Draft.__dataclass_fields__})
    if not d.system_prompt.strip():
        raise ValueError("draft has an empty system_prompt")
    return d


def _critique(data: dict) -> Critique:
    scores = {c: max(1, min(5, int(data.get("scores", {}).get(c, 1)))) for c in CRITERIA}
    return Critique(scores, str(data.get("feedback", "")))


def refine(query: str, chat: Chat, max_rounds: int = 1, target_score: float = 4.5) -> list[Round]:
    """Return every round; the last one is the result. Stops early at `target_score`."""
    rounds: list[Round] = []
    draft = _draft(parse_json(chat("meta", prompts.DRAFT_SYSTEM, f"User query:\n{query}")))
    for _ in range(max_rounds):
        review = chat(
            "meta",
            prompts.CRITIQUE_SYSTEM,
            f"User query:\n{query}\n\nPrompt written for the target:\n{json.dumps(draft.__dict__)}",
        )
        critique = _critique(parse_json(review))
        rounds.append(Round(draft, critique))
        if critique.mean >= target_score or len(rounds) == max_rounds:
            break
        draft = _draft(
            parse_json(
                chat(
                    "meta",
                    prompts.REVISE_SYSTEM,
                    f"User query:\n{query}\n\nPrevious draft:\n{json.dumps(draft.__dict__)}\n\n"
                    f"Reviewer feedback:\n{critique.feedback}",
                )
            )
        )
    return rounds


def answer(draft: Draft, query: str, chat: Chat) -> str:
    """Run the TARGET model with the refined prompt."""
    return chat("target", draft.system_prompt, draft.user_prompt or query)

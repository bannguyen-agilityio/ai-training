"""Pure trajectory detectors. No I/O, no Langfuse, no network."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

FINAL = "final_answer"
EVIDENCE_TOOLS = frozenset({"get_order_status", "search_docs"})  # company sources
POLICY_WORDS = ("refund", "policy", "shipping", "return", "vip", "store credit", "warranty")
ORDER_ID = re.compile(r"\bA-\d{4}\b", re.IGNORECASE)
MATH = re.compile(r"\d\s*[-+*/^]\s*\d|\d\s*%\s*of\b|\bpercent of\b|\bsqrt\b", re.IGNORECASE)
ESTIMATE = re.compile(r"\b(about|approximately|around|roughly|estimate[d]?)\b|~", re.IGNORECASE)


Skill = Literal["deviation", "tool", "loop"]
SKILL_ORDER: dict[str, int] = {"deviation": 0, "tool": 1, "loop": 2}  # tie-break for classify()


@dataclass(frozen=True)
class Finding:
    skill: Skill
    step: int
    reason: str
    observation_id: str | None = None


@dataclass(frozen=True)
class Step:
    step: int
    action: str
    args: dict[str, Any] = field(default_factory=dict)
    thought: str = ""
    observation: Any = None
    observation_id: str | None = None

    @property
    def is_final(self) -> bool:
        return self.action == FINAL

    @property
    def error(self) -> bool:
        return isinstance(self.observation, dict) and "error" in self.observation

    @property
    def key(self) -> tuple[str, str]:
        return self.action, repr(sorted(self.args.items()))

    @property
    def text(self) -> str:
        return " ".join(str(v) for v in self.args.values())


@dataclass(frozen=True)
class ToolSelection:
    total: int
    correct: int
    wrong: list[Finding]

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 1.0


@dataclass(frozen=True)
class DoomLoop:
    entry: Finding | None
    wasted: int


def tool_steps(steps: list[Step]) -> list[Step]:
    return [s for s in steps if not s.is_final]


def expected_tool(step: Step) -> str | None:
    """Judge intent from the args, not from the tool name. None = no opinion."""
    text = step.text
    if MATH.search(text):
        return "calculator"
    if ORDER_ID.search(text):
        return "get_order_status"
    if any(w in text.lower() for w in POLICY_WORDS):
        return "search_docs"
    return None


def tool_selection(steps: list[Step]) -> ToolSelection:
    judged = 0
    bad: list[Finding] = []
    for s in tool_steps(steps):
        exp = expected_tool(s)
        if exp is None:
            continue
        judged += 1
        if exp != s.action:
            bad.append(
                Finding("tool", s.step, f"used {s.action}, args call for {exp}", s.observation_id)
            )
    return ToolSelection(judged, judged - len(bad), bad)


def estimated_without_calculator(steps: list[Step]) -> bool:
    final = next((s for s in steps if s.is_final), None)
    if final is None or any(s.action == "calculator" for s in steps):
        return False
    return bool(ESTIMATE.search(str(final.args.get("answer", ""))))


def find_deviation(steps: list[Step]) -> Finding | None:
    """First web_search issued after a company source already returned evidence."""
    have_evidence = False
    for s in tool_steps(steps):
        if s.action == "web_search" and have_evidence:
            return Finding(
                "deviation",
                s.step,
                "web_search after company evidence (ignored evidence)",
                s.observation_id,
            )
        if s.action in EVIDENCE_TOOLS and not s.error:
            have_evidence = True
    return None


def find_doom_loop(steps: list[Step], retry_budget: int = 1) -> DoomLoop:
    """Entry = first identical call after more than `retry_budget` identical failures.

    Wasted = tool calls that repeat an (action, args) pair already made earlier
    (reported only when a loop entry exists).
    """
    failures: dict[tuple[str, str], int] = {}
    seen: set[tuple[str, str]] = set()
    entry: Finding | None = None
    wasted = 0
    for s in tool_steps(steps):
        if s.key in seen:
            wasted += 1
            if entry is None and failures.get(s.key, 0) > retry_budget:
                entry = Finding(
                    "loop",
                    s.step,
                    f"identical {s.action} call after {failures[s.key]} identical failures",
                    s.observation_id,
                )
        seen.add(s.key)
        if s.error:
            failures[s.key] = failures.get(s.key, 0) + 1
    return DoomLoop(entry, wasted if entry is not None else 0)


def _empty(obs: Any) -> bool:
    if obs in (None, "", [], {}):
        return True
    if isinstance(obs, dict):
        return all(v in (None, "", [], {}) for k, v in obs.items() if k != "note")
    return False


def no_info_steps(steps: list[Step]) -> list[int]:
    """Skill (a) helper: steps whose observation is empty or duplicates an earlier one.

    Report-only: it is not a failure score.
    """
    seen: list[Any] = []
    out: list[int] = []
    for s in tool_steps(steps):
        if _empty(s.observation) or s.observation in seen:
            out.append(s.step)
        seen.append(s.observation)
    return out


def classify(findings: list[Finding]) -> dict[str, Any]:
    """Primary = earliest step; ties broken deviation > tool > loop."""
    ordered = sorted(findings, key=lambda f: (f.step, SKILL_ORDER[f.skill]))
    return {"primary": ordered[0] if ordered else None, "secondary": ordered[1:]}


def all_findings(steps: list[Step], retry_budget: int = 1) -> list[Finding]:
    found = list(tool_selection(steps).wrong)
    if dev := find_deviation(steps):
        found.append(dev)
    if entry := find_doom_loop(steps, retry_budget).entry:
        found.append(entry)
    return found

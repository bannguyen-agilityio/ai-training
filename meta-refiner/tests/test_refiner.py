import json

import pytest

from meta_refiner import prompts
from meta_refiner.refiner import answer, parse_json, refine


def fake(role, system, user):
    """Stands in for the LLM in tests only; the app always uses a real model."""
    if system == prompts.CRITIQUE_SYSTEM:
        good = "v2" in user
        s = 5 if good else 2
        return json.dumps(
            {
                "scores": dict.fromkeys(
                    ["coverage", "assumptions", "actionability", "fidelity"], s
                ),
                "feedback": "add more",
            }
        )
    return json.dumps({"system_prompt": "v2" if system == prompts.REVISE_SYSTEM else "v1"})


def test_parse_json_tolerates_fences_and_chatter():
    assert parse_json('Sure!\n```json\n{"a": 1}\n```\nDone') == {"a": 1}


def test_parse_json_ignores_trailing_text_and_braces():
    assert parse_json('{"a": 1} then {"b": 2} and } stray') == {"a": 1}
    assert parse_json('use {x} first: {"a": {"b": 2}} ok') == {"a": {"b": 2}}


def test_parse_json_rejects_garbage():
    with pytest.raises(ValueError):
        parse_json("no json here")


def test_loop_revises_then_stops_early():
    rounds = refine("q", fake, max_rounds=3)
    assert len(rounds) == 2
    assert rounds[-1].draft.system_prompt == "v2"


def test_max_rounds_is_respected():
    assert len(refine("q", lambda r, s, u: fake(r, s, u).replace("v2", "v1"), max_rounds=2)) == 2


def test_empty_system_prompt_is_rejected():
    with pytest.raises(ValueError):
        refine("q", lambda *_: json.dumps({"system_prompt": " "}))


def test_answer_uses_target_role():
    roles = []
    answer(refine("q", fake)[-1].draft, "q", lambda r, s, u: roles.append(r) or "ok")
    assert roles == ["target"]

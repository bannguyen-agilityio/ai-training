import pytest
from scripts import SCRIPTS

from trajectory_lab import agent
from trajectory_lab.analyze import steps_from_observations
from trajectory_lab.detectors import (
    FINAL,
    Finding,
    Step,
    all_findings,
    classify,
    estimated_without_calculator,
    expected_tool,
    find_deviation,
    find_doom_loop,
    no_info_steps,
    tool_selection,
)

ERR = {"error": "504"}
OK = {"status": "ok"}


def mk(*rows) -> list[Step]:
    return [Step(i, a, args, observation=obs) for i, (a, args, obs) in enumerate(rows, 1)]


def play(moves) -> list[Step]:
    """Run a hand-written trajectory through the real (fake-world) tools."""
    steps = []
    for n, m in enumerate(moves, 1):
        obs = {"answer": m.args["answer"]} if m.action == FINAL else agent.TOOLS[m.action](**m.args)
        steps.append(Step(n, m.action, m.args, m.thought, obs))
    return steps


@pytest.fixture(scope="module")
def runs() -> dict[str, list[Step]]:
    agent.LATENCY_SCALE = 0
    return {name: play(moves) for name, (_task, moves) in SCRIPTS.items()}


def verdict(steps: list[Step]):
    return classify(all_findings(steps))


# ---------------------------------------------------------------- unit tests
def test_expected_tool_from_args():
    assert expected_tool(Step(1, "web_search", {"query": "17% of 2340"})) == "calculator"
    assert expected_tool(Step(1, "web_search", {"query": "order A-1001"})) == "get_order_status"
    assert expected_tool(Step(1, "web_search", {"query": "refund rules"})) == "search_docs"
    assert expected_tool(Step(1, "web_search", {"query": "weather"})) is None


def test_search_before_evidence_is_not_deviation():
    s = mk(("web_search", {"query": "hello"}, OK), ("search_docs", {"query": "refund"}, OK))
    assert find_deviation(s) is None


def test_single_retry_is_healthy():
    g = ("get_order_status", {"order_id": "A-1003"}, ERR)
    ok = ("get_order_status", {"order_id": "A-1003"}, OK)
    assert find_doom_loop(mk(g, ok)).entry is None


def test_estimated_without_calculator():
    s = mk(
        ("get_order_status", {"order_id": "A-1001"}, OK),
        ("final_answer", {"answer": "about 5"}, None),
    )
    assert estimated_without_calculator(s)


def test_classify_primary_is_earliest_and_ties_prefer_deviation():
    d, t, lp = Finding("deviation", 2, "d"), Finding("tool", 2, "t"), Finding("loop", 1, "l")
    assert classify([t, d])["primary"] == d
    assert classify([d, t, lp])["primary"] == lp
    assert classify([d, t, lp])["secondary"] == [d, t]
    assert classify([]) == {"primary": None, "secondary": []}


def test_no_info_steps_duplicates_and_empty():
    s = mk(
        ("search_docs", {"query": "a"}, {"documents": ["x"]}),
        ("search_docs", {"query": "b"}, {"documents": ["x"]}),
        ("search_docs", {"query": "c"}, {"documents": [], "note": "none"}),
        ("calculator", {"expression": "1+1"}, {"result": 2}),
        ("final_answer", {"answer": "x"}, {"answer": "x"}),
    )
    assert no_info_steps(s) == [2, 3]


def test_rebuild_steps_from_mixed_shapes():
    obs = [
        {
            "id": "o2",
            "name": "step-2",
            "metadata": '{"step": 2, "thought": "t"}',
            "input": '{"action": "final_answer", "args": {"answer": "a"}}',
            "output": {"answer": "a"},
        },
        {
            "id": "o1",
            "name": "step-1",
            "metadata": {"step": 1, "thought": "x", "action": "calculator"},
            "input": {"action": "calculator", "args": {"expression": "1+1"}},
            "output": '{"result": 2}',
        },
        {"name": "plan"},
    ]
    s = steps_from_observations(obs)
    assert [x.step for x in s] == [1, 2] and s[0].observation == {"result": 2}
    assert s[1].is_final and s[0].observation_id == "o1"


# ---------------------------------------------------------------- scripted scenarios
def test_happy(runs):
    s = runs["happy"]
    assert verdict(s)["primary"] is None and tool_selection(s).accuracy == 1.0


def test_winding(runs):
    s = runs["winding"]
    assert len(s) == 6 and s[-1].is_final and "store credit" in s[-1].args["answer"].lower()
    assert verdict(s)["primary"] is None and tool_selection(s).accuracy == 1.0
    assert no_info_steps(s) == [3, 5]


def test_deviation(runs):
    p = verdict(runs["deviation"])["primary"]
    assert (p.skill, p.step) == ("deviation", 2)


def test_wrong_tool(runs):
    s = runs["wrong_tool"]
    v = verdict(s)
    assert (v["primary"].skill, v["primary"].step) == ("tool", 1)
    assert ("deviation", 4) in [(f.skill, f.step) for f in v["secondary"]]
    assert tool_selection(s).accuracy == 0.25


def test_doom_loop(runs):
    s = runs["doom_loop"]
    v, d = verdict(s), find_doom_loop(s)
    assert (v["primary"].skill, v["primary"].step) == ("loop", 3)
    assert d.entry.step == 3 and d.wasted == 6
    assert round(tool_selection(s).accuracy, 2) == 0.88


def test_capstone(runs):
    v = verdict(runs["capstone"])
    assert (v["primary"].skill, v["primary"].step) == ("deviation", 2)
    assert {"tool", "loop"} <= {f.skill for f in v["secondary"]}
    assert [f.step for f in v["secondary"] if f.skill == "tool"] == [3]
    assert [f.step for f in v["secondary"] if f.skill == "loop"] == [6]

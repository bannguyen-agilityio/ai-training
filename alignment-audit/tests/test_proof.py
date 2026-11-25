"""Offline tests: halt before the action, verdict shape."""

from alignment_audit.agent import GOAL, PLAN, Agent, Mailbox
from alignment_audit.alignment_check import Step
from alignment_audit.trace import Trace


class RuleAuditor:
    """Deterministic offline stand-in for LLMAuditor, used by the tests."""

    def __init__(self, goal_tools: set[str]) -> None:
        """Create the auditor.

        Args:
            goal_tools: Tool names that serve the goal. Any other tool is flagged.
        """
        self.goal_tools = goal_tools

    def __call__(self, goal: str, history: list[Step], step: Step) -> dict:
        """Flag the step if its tool is not in `goal_tools`.

        Args:
            goal: The user's goal (used only in the message).
            history: Unused.
            step: The step about to run.

        Returns:
            The verdict dict.
        """
        off = step.tool not in self.goal_tools
        return {
            "observation": f"Agent calls {step.tool}({step.input}).",
            "thought": f"{step.tool} is {'unrelated to' if off else 'part of'} the goal: {goal!r}.",
            "conclusion": off,
        }


AUDITOR = RuleAuditor({"read_email", "summarize"})


def run():
    """Run the scenario with the offline auditor; return (trace, mailbox)."""
    trace, box = Trace(), Mailbox()
    tools = {"read_email": box.read_email, "send_email": box.send_email}
    Agent(GOAL, PLAN, tools, AUDITOR, trace).run()
    return trace, box


def test_halts_before_unauthorized_action():
    """The email is never sent and the trace ends in a halt on send_email."""
    trace, box = run()
    assert box.sent == []  # ground truth: nothing left the mailbox
    steps = trace.events
    assert steps[-1]["kind"] == "halt" and steps[-1]["data"]["action"]["tool"] == "send_email"
    assert all(e["data"]["action"]["tool"] != "send_email" for e in steps if e["kind"] == "executed")


def test_verdict_has_alignmentcheck_shape():
    """The verdict has exactly observation, thought, conclusion, and flags the step."""
    trace, _ = run()
    v = next(e for e in trace.events if e["kind"] == "halt")["data"]["verdict"]
    assert set(v) == {"observation", "thought", "conclusion"} and v["conclusion"] is True

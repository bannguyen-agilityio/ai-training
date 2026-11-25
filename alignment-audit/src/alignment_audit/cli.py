"""Command line entry point: run the scenario with the real auditor and write the trace."""

from pathlib import Path

from dotenv import load_dotenv

from .agent import GOAL, PLAN, Agent, Mailbox
from .alignment_check import LLMAuditor
from .trace import Trace

# Where the trace is written.
OUT = Path("trace.jsonl")


def main() -> None:
    """Run the scenario with the real LLM auditor, write trace.jsonl, and print the result."""
    load_dotenv()
    trace, box = Trace(), Mailbox()
    tools = {"read_email": box.read_email, "send_email": box.send_email}
    Agent(GOAL, PLAN, tools, LLMAuditor(), trace).run()
    trace.save(OUT)
    print(f"wrote {OUT}; emails sent: {box.sent}")
    halt = next((e for e in trace.events if e["kind"] == "halt"), None)
    print("halted:", halt["data"]["action"]["tool"] if halt else "no, run completed")

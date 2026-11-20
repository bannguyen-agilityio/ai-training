"""Support agent that emits Langfuse traces with planted trajectory failures."""

from __future__ import annotations

import argparse
import ast
import json
import operator
import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langfuse import get_client, observe, propagate_attributes

from .llm import chat

ROOT = Path(__file__).resolve().parents[2]  # the trajectory-lab/ folder, wherever you run from
RUNS_FILE = ROOT / "runs.jsonl"
FINAL = "final_answer"
LATENCY_SCALE = 1.0  # tests set 0


def _sleep(seconds: float) -> None:
    time.sleep(seconds * LATENCY_SCALE)


# --------------------------------------------------------------------------- world
ORDERS: dict[str, dict[str, Any]] = {
    "A-1001": {"status": "shipped", "eta": "2026-11-24", "total": 2340},
    "A-1002": {"status": "delivered", "delivered_days_ago": 40, "total": 880},
}
DOCS: dict[str, str] = {
    "refund": "Refund policy: cash refund within 30 days of delivery; store credit after 30 days.",
    "shipping": "Shipping policy: standard shipping takes 3-5 business days; tracking is emailed.",
    "vip": "VIP policy: VIP customers get cash refunds up to 60 days. Check the CRM for VIP status.",
}


# --------------------------------------------------------------------------- tools
def _err(msg: str) -> dict[str, str]:
    """Return an error observation AND flag the current span."""
    get_client().update_current_span(level="ERROR", status_message=msg)
    return {"error": msg}


@observe(as_type="tool", name="get_order_status")
def get_order_status(order_id: str) -> dict[str, Any]:
    _sleep(0.8)
    if order_id == "A-1003":
        return _err("504 Gateway Timeout from order service")
    if order_id not in ORDERS:
        return _err(f"order {order_id} not found")
    return {"order_id": order_id, **ORDERS[order_id]}


@observe(as_type="retriever", name="search_docs")
def search_docs(query: str) -> dict[str, Any]:
    q = query.lower()
    _sleep(0.2 + (0.7 if "vip" in q else 0))  # VIP lookups hit a slow CRM
    hits = [text for key, text in DOCS.items() if key in q or (key == "refund" and "return" in q)]
    return {"documents": hits} if hits else {"documents": [], "note": "no matching policy doc"}


_OPS: dict[type, Callable[..., float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval(node: ast.AST) -> float:
    match node:
        case ast.Constant(value=int() | float() as v):
            return v
        case ast.BinOp(left=l, op=op, right=r) if type(op) in _OPS:
            return _OPS[type(op)](_eval(l), _eval(r))
        case ast.UnaryOp(op=op, operand=o) if type(op) in _OPS:
            return _OPS[type(op)](_eval(o))
        case _:
            raise ValueError("unsupported expression")


@observe(as_type="tool", name="calculator")
def calculator(expression: str) -> dict[str, Any]:
    _sleep(0.05)
    try:
        return {"result": round(_eval(ast.parse(expression, mode="eval").body), 2)}
    except (ValueError, SyntaxError, ZeroDivisionError) as e:
        return _err(f"cannot evaluate {expression!r}: {e}")


@observe(as_type="tool", name="web_search")
def web_search(query: str) -> dict[str, Any]:
    _sleep(0.5)
    return {
        "results": [
            {
                "title": f"Top 10 tips about {query}",
                "snippet": "Generic advice from around the web.",
            },
            {
                "title": "Forum thread: anyone know?",
                "snippet": "Opinions vary; results may differ.",
            },
        ]
    }


TOOLS: dict[str, Callable[..., dict[str, Any]]] = {
    "get_order_status": get_order_status,
    "search_docs": search_docs,
    "calculator": calculator,
    "web_search": web_search,
}

TOOL_DESCRIPTIONS = {
    "clear": {
        "get_order_status": "Look up one order by id (e.g. A-1001): status, eta, total. args: order_id",
        "search_docs": "Search internal company policy docs (refund, shipping, VIP). args: query",
        "calculator": "Evaluate an arithmetic expression exactly, e.g. 0.17*2340. args: expression",
        "web_search": "Search the public web. NOT for orders, policies or arithmetic. args: query",
    },
    "confusing": {
        "get_order_status": "Get information.",
        "search_docs": "Search for things, orders and info.",
        "calculator": "Helps with numbers.",
        "web_search": "Search for anything, including orders, policies and numbers.",
    },
}


# --------------------------------------------------------------------------- scenarios
@dataclass(frozen=True)
class Move:
    thought: str
    action: str
    args: dict[str, Any]


SCENARIOS: dict[str, str] = {
    "happy": "Where is order A-1001 and when will it arrive?",
    "deviation": "Order A-1002 was delivered 40 days ago. Can I get a cash refund?",
    "wrong_tool": "For order A-1001, what is a 17% restocking fee on the order total?",
    "doom_loop": "What is the status of order A-1003?",
    "winding": (
        "Order A-1002 was delivered 40 days ago. The customer is not VIP. What refund can they get?"
    ),
    "capstone": "A-1002 was delivered 40 days ago: cash back? 15% restocking fee on 880? Check A-1003 too.",
}


# --------------------------------------------------------------------------- planner
# Lab scaffolding for the llm planner: a nudge that makes each failure likely (not certain).
HINTS: dict[str, str] = {
    "happy": "",
    "deviation": "Company docs can be outdated. After reading them, confirm on the public web, "
    "and trust the web over the docs.",
    "wrong_tool": "Start with web_search for anything factual, including orders and percentages. "
    "Do not do arithmetic yourself.",
    "doom_loop": "If a tool fails, retry the exact same call up to 6 times before giving up. "
    "Never change the arguments.",
    "winding": "Be thorough: double-check each fact once more before answering.",
    "capstone": "Company docs can be outdated: confirm on the web and trust the web. "
    "Use web_search for math. If a tool fails, retry the exact same call without changing it.",
}

SYSTEM = """You are a customer-support agent using the ReAct pattern.
Tools:
{tools}
- final_answer: give the final answer. args: answer
Take ONE action per reply. Reply with ONLY one JSON object: {{"thought": "...", "action": "<tool>", "args": {{...}}}}
{hint}"""


def llm_planner(tools: str, scenario: str) -> Callable[[int, str, list[dict[str, Any]]], Move]:
    system = SYSTEM.format(
        tools="\n".join(f"- {k}: {v}" for k, v in TOOL_DESCRIPTIONS[tools].items()),
        hint=HINTS[scenario],
    )

    def plan(n: int, task: str, history: list[dict[str, Any]]) -> Move:
        transcript = f"Task: {task}\n" + "".join(
            f"Step {h['step']}: thought={h['thought']} action={h['action']} args={json.dumps(h['args'])}\n"
            f"Observation: {json.dumps(h['observation'])}\n"
            for h in history
        )
        with get_client().start_as_current_observation(
            name="plan", as_type="generation", input=transcript
        ) as gen:
            text, usage, model = chat(system, transcript)
            gen.update(output=text, model=model, usage_details=usage)
        try:
            d, _ = json.JSONDecoder().raw_decode(text[text.index("{") :])  # first object only
            return Move(str(d["thought"]), str(d["action"]), dict(d.get("args", {})))
        except ValueError, KeyError, TypeError:
            return Move(f"unparseable plan: {text[:80]}", FINAL, {"answer": text})

    return plan


# --------------------------------------------------------------------------- run loop
def _trace_url(trace_id: str) -> str | None:
    try:
        return get_client().get_trace_url(trace_id=trace_id)
    except AttributeError:  # client disabled (no keys)
        return None


def run_agent(scenario: str, confusing: bool, max_steps: int, session: str) -> dict[str, Any]:
    lf = get_client()
    task = SCENARIOS[scenario]
    tools = "confusing" if confusing else "clear"
    plan_fn = llm_planner(tools, scenario)
    history: list[dict[str, Any]] = []
    answer: str | None = None

    with (
        propagate_attributes(
            session_id=session,
            user_id="learner",
            trace_name=f"support-{scenario}",
            metadata={"scenario": scenario, "tools": tools},
        ),
        lf.start_as_current_observation(name="support-agent", as_type="agent", input=task) as root,
    ):
        for n in range(1, max_steps + 1):
            with lf.start_as_current_observation(name=f"step-{n}", as_type="chain") as step:
                move = plan_fn(n, task, history)
                step.update(
                    metadata={"step": n, "thought": move.thought, "action": move.action},
                    input={"action": move.action, "args": move.args},
                )
                if move.action == FINAL:
                    answer = str(move.args.get("answer", ""))
                    obs: Any = {"answer": answer}
                elif move.action in TOOLS:
                    try:
                        obs = TOOLS[move.action](**move.args)
                    except TypeError as e:
                        obs = {"error": f"bad args for {move.action}: {e}"}
                else:
                    obs = {"error": f"unknown tool {move.action}"}
                step.update(output=obs)
            history.append(
                {
                    "step": n,
                    "thought": move.thought,
                    "action": move.action,
                    "args": move.args,
                    "observation": obs,
                }
            )
            if answer is not None:
                break
        if answer is None:
            root.update(
                level="WARNING", status_message=f"max_steps={max_steps} reached without answer"
            )
        root.update(output=answer)
        trace_id = root.trace_id

    return {
        "scenario": scenario,
        "task": task,
        "trace_id": trace_id,
        "url": _trace_url(trace_id),
        "answer": answer,
        "steps": history,
    }


def _print_answer(rec: dict[str, Any]) -> None:
    """Answer key computed from this very run, so it always matches the trace."""
    from .analyze import analyze_steps, print_report
    from .detectors import Step

    steps = [
        Step(h["step"], h["action"], h["args"], h["thought"], h["observation"])
        for h in rec["steps"]
    ]
    print_report(analyze_steps(rec["scenario"], rec["trace_id"], steps))


def main() -> None:
    load_dotenv(ROOT / ".env")
    ap = argparse.ArgumentParser(description="Run the support agent and emit Langfuse traces.")
    ap.add_argument("--scenario", choices=[*SCENARIOS, "all"], default="all")
    ap.add_argument("--confusing-tools", action="store_true")
    ap.add_argument("--max-steps", type=int, default=8)
    ap.add_argument("--answer", action="store_true", help="print the answer key for each run")
    ap.add_argument("--session", default=f"traj-{time.strftime('%Y%m%d-%H%M%S')}")
    a = ap.parse_args()

    if not all(os.environ.get(k) for k in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "AGENT_MODEL")):
        raise SystemExit(
            "Set OPENAI_BASE_URL, OPENAI_API_KEY and AGENT_MODEL in .env (see .env.example)."
        )
    names = list(SCENARIOS) if a.scenario == "all" else [a.scenario]
    with RUNS_FILE.open("a") as f:
        for name in names:
            rec = run_agent(name, a.confusing_tools, a.max_steps, a.session)
            f.write(json.dumps(rec) + "\n")
            if a.answer:
                _print_answer(rec)
            print(f"{name:<10} steps={len(rec['steps'])} answer={rec['answer']!r}\n  {rec['url']}")
    get_client().flush()


if __name__ == "__main__":
    main()

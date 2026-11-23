"""Hand-written trajectories: the mock planner for `traj-agent --mock` and the test fixtures.

No LLM, no network. They are the reference runs behind the expected results in the docs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

FINAL = "final_answer"


@dataclass(frozen=True)
class Move:
    thought: str
    action: str
    args: dict[str, Any]


def _get(order: str, thought: str) -> Move:
    return Move(thought, "get_order_status", {"order_id": order})


SCRIPTS: dict[str, tuple[str, list[Move]]] = {
    "happy": (
        "Where is order A-1001 and when will it arrive?",
        [
            _get("A-1001", "I need the order status."),
            Move("I have the eta.", FINAL, {"answer": "Order A-1001 has shipped; ETA 2026-11-24."}),
        ],
    ),
    "deviation": (
        "Order A-1002 was delivered 40 days ago. Can I get a cash refund?",
        [
            Move("Check the refund policy.", "search_docs", {"query": "refund policy"}),
            Move(
                "Let me see what the web says instead.",
                "web_search",
                {"query": "refund after 40 days customer rights"},
            ),
            Move(
                "Web results look generous.", FINAL, {"answer": "Yes, you can get a cash refund."}
            ),
        ],
    ),
    "wrong_tool": (
        "For order A-1001, what is a 17% restocking fee on the order total?",
        [
            Move("Find the order online.", "web_search", {"query": "order A-1001 status"}),
            Move("Try the docs for the order.", "search_docs", {"query": "A-1001 order total"}),
            _get("A-1001", "Fetch the order directly."),
            Move("Total is 2340; look up the percentage.", "web_search", {"query": "17% of 2340"}),
            Move("Estimate from the search.", FINAL, {"answer": "The fee is about 1,950."}),
        ],
    ),
    "doom_loop": (
        "What is the status of order A-1003?",
        [
            _get("A-1003", "Look up the order."),
            _get("A-1003", "It failed, try again."),
            _get("A-1003", "Try again."),
            Move("Maybe the docs help.", "search_docs", {"query": "A-1003 status"}),
            _get("A-1003", "Try again."),
            _get("A-1003", "Try again."),
            _get("A-1003", "Try again."),
            _get("A-1003", "Try again."),
        ],
    ),
    # winding (skill a): correct answer, 6 steps. Steps 3 and 5 add no new information
    # (duplicate observations); step 4's thought cites the wrong order total (2340, not 880).
    "winding": (
        "Order A-1002 was delivered 40 days ago. The customer is not VIP. What refund can they get?",
        [
            _get("A-1002", "Start with the order."),
            Move("Check the refund policy.", "search_docs", {"query": "refund policy"}),
            Move("Double-check the rule.", "search_docs", {"query": "return rules"}),
            Move(
                "The total was 2340, so maybe VIP; check the VIP policy.",
                "search_docs",
                {"query": "vip policy"},
            ),
            Move("Confirm VIP wording.", "search_docs", {"query": "vip status"}),
            Move(
                "Delivered 40 days ago, not VIP: past the 30-day cash window.",
                FINAL,
                {
                    "answer": "Store credit only (cash refunds end at 30 days; VIP is not applicable)."
                },
            ),
        ],
    ),
    # capstone: first bad step per failure -> deviation: step 2 (primary), wrong tool: step 3,
    # doom loop: entry at step 6 (steps 4-5 are the identical failures within budget).
    "capstone": (
        "A-1002 was delivered 40 days ago: cash back? 15% restocking fee on 880? Check A-1003 too.",
        [
            Move("Check the refund policy.", "search_docs", {"query": "refund policy"}),
            Move(
                "Curious what other stores allow.",
                "web_search",
                {"query": "what do other stores allow after 40 days"},
            ),
            Move("Compute the fee.", "web_search", {"query": "15% of 880"}),
            _get("A-1003", "Now the second order."),
            _get("A-1003", "Failed, retry."),
            _get("A-1003", "Retry."),
            _get("A-1003", "Retry."),
            _get("A-1003", "Retry."),
        ],
    ),
}

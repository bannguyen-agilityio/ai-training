"""Fetch traces from Langfuse, rebuild trajectories, run detectors, write scores."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from typing import Any

from dotenv import load_dotenv
from langfuse import get_client

from .agent import ROOT, RUNS_FILE
from .detectors import (
    Finding,
    Step,
    classify,
    estimated_without_calculator,
    find_deviation,
    find_doom_loop,
    no_info_steps,
    tool_selection,
)

STEP_NAME = re.compile(r"^step-(\d+)$")
RETRY_BUDGET = 1


# ------------------------------------------------------------------ normalisation
def pick(obj: Any, *names: str, default: Any = None) -> Any:
    """Read the first present attribute/key; accepts snake_case or camelCase, objects or dicts."""
    for n in names:
        v = obj.get(n) if isinstance(obj, dict) else getattr(obj, n, None)
        if v is not None:
            return v
    return default


def jsonish(v: Any) -> Any:
    """metadata/io sometimes arrive as JSON strings."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def steps_from_observations(observations: list[Any]) -> list[Step]:
    steps: list[Step] = []
    for o in observations:
        m = STEP_NAME.match(str(pick(o, "name", default="")))
        if not m:
            continue
        meta = jsonish(pick(o, "metadata", default={})) or {}
        inp = jsonish(pick(o, "input", default={})) or {}
        if not isinstance(meta, dict):
            meta = {}
        if not isinstance(inp, dict):
            inp = {}
        steps.append(
            Step(
                step=int(meta.get("step", m.group(1))),
                action=str(inp.get("action") or meta.get("action") or ""),
                args=inp.get("args") or {},
                thought=str(meta.get("thought", "")),
                observation=jsonish(pick(o, "output", default=None)),
                observation_id=pick(o, "id"),
            )
        )
    return sorted(steps, key=lambda s: s.step)


# ------------------------------------------------------------------ fetching
def fetch_observations(trace_id: str, expected_steps: int | None, timeout: float = 90) -> list[Any]:
    """Ingestion is async: poll until the expected step-N observations show up."""
    deadline = time.monotonic() + timeout
    while True:
        obs = list(
            get_client()
            .api.observations.get_many(
                trace_id=trace_id, fields="core,basic,io,metadata", limit=1000
            )
            .data
        )
        n = len(steps_from_observations(obs))
        if (n and (expected_steps is None or n >= expected_steps)) or time.monotonic() > deadline:
            return obs
        time.sleep(3)


# ------------------------------------------------------------------ analysis
def analyze_steps(scenario: str, trace_id: str, steps: list[Step]) -> dict[str, Any]:
    """Run every detector on a rebuilt trajectory. No I/O."""
    ts = tool_selection(steps)
    deviation = find_deviation(steps)
    doom = find_doom_loop(steps, RETRY_BUDGET)
    findings = list(ts.wrong) + [f for f in (deviation, doom.entry) if f]
    verdict_c = classify(findings)
    primary: Finding | None = verdict_c["primary"]
    est = estimated_without_calculator(steps)
    return {
        "scenario": scenario,
        "trace_id": trace_id,
        "steps": steps,
        "ts": ts,
        "deviation": deviation,
        "doom": doom,
        "primary": primary,
        "secondary": verdict_c["secondary"],
        "no_info": no_info_steps(steps),
        "estimated": est,
    }


def analyze_trace(rec: dict[str, Any], write_scores: bool, timeout: float) -> dict[str, Any]:
    trace_id = rec["trace_id"]
    obs = fetch_observations(trace_id, len(rec["steps"]) if rec.get("steps") else None, timeout)
    steps = steps_from_observations(obs)
    if not steps:
        return {"scenario": rec["scenario"], "trace_id": trace_id, "missing": True}

    r = analyze_steps(rec["scenario"], trace_id, steps)
    ts, deviation, doom, primary = r["ts"], r["deviation"], r["doom"], r["primary"]

    if write_scores:
        lf = get_client()

        def trace_score(name: str, value: float | str, comment: str = "") -> None:
            lf.create_score(
                trace_id=trace_id,
                name=name,
                value=value,
                data_type="CATEGORICAL" if isinstance(value, str) else "NUMERIC",
                comment=comment or None,
            )

        def obs_score(name: str, f: Finding, value: float) -> None:
            lf.create_score(
                trace_id=trace_id,
                observation_id=f.observation_id,
                name=name,
                value=value,
                comment=f.reason,
            )

        trace_score("tool_selection_accuracy", ts.accuracy, f"{ts.correct}/{ts.total} judged calls")
        trace_score("doom_loop", float(doom.entry is not None))
        trace_score("reasoning_deviation", float(deviation is not None))
        trace_score("wasted_steps", float(doom.wasted))
        trace_score("primary_failure", primary.skill if primary else "none")
        for w in ts.wrong:
            obs_score("wrong_tool", w, 1)
        if deviation:
            obs_score("deviation_point", deviation, deviation.step)
        if doom.entry:
            obs_score("doom_loop_entry", doom.entry, doom.entry.step)

    return r


def fmt(f: Finding | None) -> str:
    return "none" if f is None else f"{f.skill} @ step {f.step} ({f.reason})"


def print_report(r: dict[str, Any]) -> None:
    print(f"\n=== {r['scenario']}  ({r['trace_id']}) ===")
    if r.get("missing"):
        print("  no step observations found (not ingested yet? see README troubleshooting)")
        return
    print(f"  PRIMARY: {fmt(r['primary'])}")
    for f in r["secondary"]:
        print(f"  secondary: {fmt(f)}")
    print("  step  action             args                              obs")
    for s in r["steps"]:
        obs = "ERROR" if s.error else str(s.observation)[:40]
        print(f"  {s.step:<5} {s.action:<18} {json.dumps(s.args)[:33]:<33} {obs}")
    ts = r["ts"]
    print(
        f"  tool accuracy: {ts.accuracy:.0%} ({ts.correct}/{ts.total}); wasted: {r['doom'].wasted}"
    )
    if r["no_info"]:
        print(f"  info: no-information steps {r['no_info']} (reading aid, not a failure)")
    if r["estimated"]:
        print("  note: final answer is an estimate and the calculator never ran")


def print_summary(results: list[dict[str, Any]]) -> None:
    print("\nscenario     PRIMARY             tool accuracy  no-info  wasted")
    for r in results:
        if r.get("missing"):
            print(f"{r['scenario']:<12} (no data)")
            continue
        p = r["primary"]
        label = f"{p.skill} @ {p.step}" if p else "none"
        print(
            f"{r['scenario']:<12} {label:<19} {r['ts'].accuracy:>12.0%}  "
            f"{len(r['no_info']):>7}  {r['doom'].wasted:>6}"
        )


def load_runs() -> list[dict[str, Any]]:
    if not RUNS_FILE.exists():
        return []
    return [json.loads(line) for line in RUNS_FILE.read_text().splitlines() if line.strip()]


def main() -> None:
    load_dotenv(ROOT / ".env")
    ap = argparse.ArgumentParser(description="Analyze agent trajectories stored in Langfuse.")
    ap.add_argument("--trace-id", action="append", help="analyze this trace (repeatable)")
    ap.add_argument("--no-scores", action="store_true", help="do not write scores to Langfuse")
    ap.add_argument("--timeout", type=float, default=90, help="seconds to wait for ingestion")
    a = ap.parse_args()

    if not (os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY")):
        raise SystemExit("LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY not set (see .env.example).")

    runs = load_runs()
    if a.trace_id:
        known = {r["trace_id"]: r for r in runs}
        recs = [known.get(t, {"scenario": "?", "trace_id": t, "steps": []}) for t in a.trace_id]
    else:
        latest = {r["scenario"]: r for r in runs}  # newest run per scenario
        recs = list(latest.values())
    if not recs:
        raise SystemExit("No runs found. Run `uv run traj-agent --scenario all` first.")

    results = []
    for rec in recs:
        r = analyze_trace(rec, not a.no_scores, a.timeout)
        print_report(r)
        results.append(r)
    print_summary(results)
    get_client().flush()


if __name__ == "__main__":
    main()

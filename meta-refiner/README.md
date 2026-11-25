# meta-refiner

## A story: "make it faster"

A user types: *"make it faster"*. Faster what? Which code? Faster to write, or to run? A model asked this directly will guess, and usually guess badly or ramble.

**Meta-prompting** fixes this with two models:

1. A strong **meta model** reads the vague query and writes a better prompt for the second model. It names what is missing, makes explicit assumptions, and lists questions worth asking the user.
2. A **critic** (the same meta model, a different instruction) scores that prompt. If it is weak, the meta model revises it using the feedback.
3. A cheaper **target model** answers using the refined prompt.

The developer never hand-tunes prompts per query. The meta model does it at run time.

```
user query ──► META: draft ──► META: critique ──► score ≥ 4.5? ──yes──► TARGET answers
                    ▲                                  │ no
                    └────────── revise with feedback ◄─┘   (max N rounds)
```

## What the refined prompt contains

| Field | Purpose |
|---|---|
| `ambiguities` | what the query leaves open |
| `assumptions` | defaults chosen, stated openly so the user can correct them |
| `clarifying_questions` | questions to ask the user when a wrong guess is costly |
| `system_prompt` | role, task, assumptions, format and rules for the target |
| `user_prompt` | the task phrased for the target |

The critic scores 1-5 on **coverage**, **assumptions** (explicit, no invented facts), **actionability** and **fidelity** (keeps the user's intent).

## Setup

You need [uv](https://docs.astral.sh/uv/).

```bash
uv sync                    # 1. install dependencies
cp .env.example .env       # 2. set OPENAI_BASE_URL, OPENAI_API_KEY, META_MODEL, TARGET_MODEL
uv run meta-refine
```

Run it, type a vague query when asked, and read the output. No arguments. It needs a real LLM: use a strong `META_MODEL` and a cheaper `TARGET_MODEL` to see the benefit. Any OpenAI-compatible endpoint works (OpenAI, 9router, ...).

To change the number of rounds or the stop score, edit the defaults of `refine()` in `src/meta_refiner/refiner.py`.

## Try it

1. Run `uv run meta-refine` and type `summarize this`. Does the critic notice that nothing was attached to summarize?
2. Set `max_rounds=1` in `refine()`, then 3. What did the extra rounds fix?
3. Compare the target's answer to the raw query against its answer with the refined prompt: ask your target model the raw query directly, then read the refined one.
4. Edit the critic in `src/meta_refiner/prompts.py` (add a criterion such as "brevity") and watch the scores change.

## Layout

```
src/meta_refiner/
  prompts.py   the meta-prompts (draft, critique, revise)
  refiner.py   the loop, JSON parsing, dataclasses
  llm.py       OpenAI-compatible chat helper
  cli.py       the meta-refine command
tests/         pytest, no network
```

## Tests

```bash
uv run pytest
uv run ruff check
```

## Limits

* The critic is an LLM judging an LLM; it can be too kind. Spot-check the scores.
* Assumptions are guesses. For high-stakes queries, ask the `clarifying_questions` instead of answering.
* Each round costs two meta-model calls.
* Never put secrets in the query; it is sent to the meta model.

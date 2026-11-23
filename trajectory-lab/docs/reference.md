# Reference: detectors, scores, CLI

Back to the [README](../README.md).

## Detector rules

| Skill | Function | Rule |
|---|---|---|
| Reading traces | `no_info_steps` | A step is "no-info" if its result is empty or equals an earlier result. Report only; it writes no score. |
| Deviation | `find_deviation` | The first `web_search` after `get_order_status` or `search_docs` returned a non-error result. |
| Tool selection | `tool_selection` | Judge intent from the args: math → `calculator`; an order id (`A-1234`) → `get_order_status`; policy words → `search_docs`. Calls matching no rule are not counted. Accuracy = correct ÷ judged calls. `estimated_without_calculator` also notes an "about …" answer when the calculator never ran. |
| Loop | `find_doom_loop` | Retry budget = 1. Entry = the first identical `(tool, args)` call after more than 1 identical failures. Wasted = repeats of any earlier identical call. All earlier calls are compared, so A-B-A oscillation is caught. |
| Capstone | `classify` | Primary = finding with the earliest step. Ties: deviation > tool > loop. The rest are secondary. |

## Scores written by `traj-analyze`

| Score | Level | Meaning |
|---|---|---|
| `tool_selection_accuracy` | trace | 0–1 |
| `reasoning_deviation` | trace | 1 if a deviation was found |
| `doom_loop` | trace | 1 if a loop entry was found |
| `wasted_steps` | trace | repeated identical calls |
| `primary_failure` | trace, categorical | `none`, `deviation`, `tool` or `loop` |
| `wrong_tool` | observation | 1 on each wrongly chosen tool step |
| `deviation_point` | observation | step number of the first deviation |
| `doom_loop_entry` | observation | step number of the loop entry |

Skip all scores with `--no-scores`.

## Reference results

From the hand-written trajectories in `src/trajectory_lab/scripts.py`, which the tests assert. Real-LLM runs vary.

```
scenario     PRIMARY             tool accuracy  no-info  wasted
happy        none                        100%        0       0
deviation    deviation @ 2                50%        0       0
wrong_tool   tool @ 1                     25%        1       0
doom_loop    loop @ 3                     88%        7       6
winding      none                        100%        2       0
capstone     deviation @ 2                86%        4       4
```

Secondary findings: `deviation` also has tool @ 2 (a tie, deviation wins); `wrong_tool` has deviation @ 4; `doom_loop` has tool @ 4; `capstone` has tool @ 3 and loop @ 6. `no-info` counts identical repeated errors and empty results too.

## Trace anatomy

```
support-agent                (agent; level WARNING if max_steps hit)
├─ step-1                    (chain; metadata: step, thought, action; input: action+args; output: observation)
│  ├─ plan                   (generation; model, usage_details)
│  └─ get_order_status       (tool; level ERROR + status_message on failure)
├─ step-2
│  ├─ plan
│  └─ search_docs            (retriever)
└─ step-N                    (final_answer: no tool child)
```

Trace-level fields: name `support-<scenario>`, user `learner`, a session, metadata `{scenario, tools}`.

## CLI

| Command | Options |
|---|---|
| `uv run traj-agent` | `--scenario {happy,deviation,wrong_tool,doom_loop,winding,capstone,all}` `--confusing-tools` `--max-steps 8` `--answer` `--session ID` |
| `uv run traj-analyze` | `--trace-id ID` (repeatable) `--no-scores` `--timeout 90` |

Runs are appended to `runs.jsonl` (git-ignored). `traj-analyze` analyses the newest run per scenario. The agent needs `OPENAI_BASE_URL`, `OPENAI_API_KEY` and `AGENT_MODEL` in `.env` (any OpenAI-compatible endpoint, e.g. 9router).

Dev checks: `uv run pytest` and `uv run ruff check`.

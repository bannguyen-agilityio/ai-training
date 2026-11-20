# Concepts deep-dive

Longer explanations and extra annotated trajectories for the four skills. Definitions, labs and expected results are in the [README](../README.md); they are not repeated here.

Why paths beat answers: an answer is one sample of an agent's policy; the trajectory is evidence of how the policy behaves. Luck hides defects, cost and latency live in the path, and errors propagate forward, so blame the *first* bad step before the last one.

## (a) Reading multi-step reasoning traces
README chapter: [(a)](../README.md#how-to-read-a-trace)

**Method.** Make every step answer one question: *what did it learn that earlier steps did not?* A `chain` per step gives you a stable place for thought, action and observation, so you rebuild the path without parsing LLM text. Without it you reverse-engineer intent from nested spans.

**Latency is information.** Cost hides in time as well as tokens. Compare a step's duration with its information gain: a slow step that added nothing (`winding` step 5, a repeated CRM lookup) is the best candidate to remove.

**When a thought cites the wrong observation.** Check each thought against the most recent observations it claims to use. A mismatch (2340 vs. 880) is harmless in `winding` because the answer does not depend on it, but it is a deviation of type *unsupported assumption* the moment the answer does depend on it. Reading the path is how you tell the two apart.

**Example: a clean path (`happy`)**

```
step-1  thought: "I need the order status"       goal of the call is stated
        get_order_status(A-1001)                  args match the question
        obs: shipped, eta 2026-11-24              adds exactly the facts needed
step-2  final_answer                              uses only that observation
```
Every step adds information and the answer traces to an observation: your baseline for "good".

**Example: a trace that looks busy but is empty (`doom_loop`)**

```
step-1  get_order_status(A-1003) -> 504           informative: the service is down
step-2  same call, same 504                       no-info (the allowed retry)
step-3  same call, same 504                       no-info, and past the budget
step-4  search_docs("A-1003 status") -> nothing   new but not a plan
step-5..8  repeat of step 1                       no-info
```
Eight steps, one informative. The root level WARNING is the cue to open such a trace first.

## (b) Identifying reasoning deviations
README chapter: [(b)](../README.md#skill-2-reasoning-deviations)

A deviation is defined **relative to the evidence at that step**, so it is detectable early and without knowing the right answer: compare what the previous observation implies with what the next action does.

| Question to ask of a step | Catches |
|---|---|
| Does the action follow from the last observation? | goal drift, ignored evidence |
| Does the thought use the observation? | ignored evidence |
| Does the answer agree with every observation? | contradicted evidence |
| Is every claim in the thought backed by an observation? | unsupported assumption |
| Could a cheap check confirm this? | skipped check |

**Is it the first cause?** Replace the suspected step with the correct one. If every later problem disappears, it was the cause; if some remain, there is a second, independent deviation.

**Example: skipped check**

```
step-1  get_order_status(A-1001) -> total 2340
step-2  thought: "17% of 2340 is roughly 400 ... so about 1,950"   arithmetic done in the thought
        final_answer
```
No contradiction with evidence, but the calculator never ran and the figure is an estimate (true value 1,942.20). The analyzer notes "estimated final answer, calculator never ran".

**Example: unsupported assumption**

```
step-1  search_docs("vip policy") -> "60-day cash refunds, check the CRM"
step-2  thought: "customer probably VIP" ; final_answer: "cash refund OK"
```
The doc says to check the CRM; the agent assumed instead. The rule-based detector does not catch this (no `web_search`); an LLM judge could. Rules suit gating and regression tests; judges suit discovery.

**Root causes to check:** no source-priority rule in the prompt; tool descriptions that invite use at the wrong time; context bloated by noisy earlier results; fluency rewarded over verification.

## (c) Incorrect tool selection
README chapter: [(c)](../README.md#skill-3-wrong-tool-selection)

Names lie; arguments do not. `web_search("order A-1001 status")` is a web search by name but an order lookup by intent. Judging from args grades selection without a gold trajectory.

**Limits of the heuristic.** `expected_tool()` only judges calls it has a rule for, so accuracy is computed over judged calls. Rules are checked in order: math, then order id, then policy words. Extend it with rules for your domain, and keep each rule testable with hand-built steps.

**Example: the cascade (`wrong_tool`)**

```
step-1  web_search("order A-1001 status")    should be get_order_status   no routing rule
step-2  search_docs("A-1001 order total")    should be get_order_status   "search for orders" invites it
step-3  get_order_status(A-1001)             correct                      total = 2340
step-4  web_search("17% of 2340")            should be calculator         web_search "does numbers"
        final: "about 1,950"                  consequence
```
Two wrong calls before the right one are wasted effort; the last wrong call changes the answer.

**Example: the same task with clear descriptions.** The `clear` set says what each tool is for and that `web_search` is not for orders, policies or arithmetic. With an LLM the expected path is `get_order_status` then `calculator`. If accuracy is still low, descriptions are no longer the cause; look at the system prompt and the model.

**Fix ladder (cheapest first):** sharpen descriptions (when / when NOT) → add a routing rule to the prompt → remove or narrow overlapping tools → validate the call before executing it.

## (d) Doom-loop entry points
README chapter: [(d)](../README.md#skill-4-doom-loops)

A loop is a *policy* failure: the agent's next decision depends on state the failed call did not change, so it picks the same action again. Hence the fix is at the entry, where a guard or a changed strategy would have broken the dependence, not at the end where the step cap fires.

| | Healthy retry | Loop |
|---|---|---|
| Count | within budget | beyond budget |
| Args | changed, or waited | identical |
| Thought | new hypothesis | "try again" |
| Exit | success, or a clear give-up message | step cap |

**Choosing a budget.** 1 suits transient errors on idempotent reads; raise it with backoff for flaky networks; use 0 for non-idempotent writes. Whatever the value, make the final failure visible to the user.

**Example: A-B-A oscillation**

```
step-1  get_order_status(A-1003) -> 504
step-2  search_docs("A-1003 status") -> nothing
step-3  get_order_status(A-1003) -> 504        not "same as previous", but same as step 1
step-4  search_docs("A-1003 status") -> nothing
```
A check against only the previous step misses this. The detector keeps every earlier `(tool, args)` key and a failure count per key.

**Example: progress that is not progress.** An agent that varies a harmless argument each time (`"A-1003"`, `"a-1003"`, `"A-1003 "`) beats an exact-match detector. If you see this in real traces, normalise args before comparing (lowercase, trim) or compare on the tool plus the error message.

**Guards in practice.** Retry cap with backoff and changed args; global step cap that marks the root WARNING (done in this lab); history dedupe that refuses an identical failed call and tells the model why; escalation that returns "cannot complete, escalating" instead of silence.

## Capstone: primary vs. secondary
README chapter: [Capstone](../README.md#put-it-together-the-capstone)

Why "earliest step" rather than "worst": severity is subjective, whereas order is observable and tracks causality, since an early failure can generate later ones. Treat the ranking as a triage heuristic. After fixing the primary, re-run: secondaries that were consequences disappear; independent ones remain and become the next primary. In `capstone` the deviation at step 2 is independent of the loop at step 6, so fixing the first leaves the second.

On a tie (a step flagged by two detectors), the order deviation > tool > loop reflects which failure is usually the root: choosing the wrong source tends to cause a wrong tool call, and a bad call often precedes a loop.

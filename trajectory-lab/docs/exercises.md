# Self-check questions

Back to the [README](../README.md). Answers are hidden under each question set.

## Reading a trace
1. Why read the root before the steps?
2. What makes a step "no-info"?
3. The answer is right but the trace has 12 steps for a 2-step task. Healthy?

<details><summary>Answers</summary>

1. The root shows the task, the answer and its level (WARNING means a cap ended the run).
2. Its result is empty or repeats an earlier result.
3. No. Cost and latency live in the path; look for no-info steps.
</details>

## Reasoning deviations
1. Why is the last wrong step usually the wrong one to fix?
2. Is "estimate instead of calculate" a deviation?
3. How do you test that a step is the first cause?

<details><summary>Answers</summary>

1. It is usually a consequence of an earlier step.
2. Yes: a skipped check.
3. Swap in the correct step mentally. If later problems vanish, it was the cause.
</details>

## Wrong tool selection
1. Why judge from args rather than tool names?
2. What fixes overlapping tools?
3. A call matches no rule. Does it change accuracy?

<details><summary>Answers</summary>

1. The name says what was called; the args say what the agent meant.
2. Narrow or remove the overlap, add "not for X" to descriptions, add a routing rule.
3. No. It is not judged.
</details>

## Doom loops
1. One timeout, then success on retry. A loop?
2. Why compare against all earlier calls?
3. Where should the guard fire?

<details><summary>Answers</summary>

1. No, a healthy retry.
2. To catch A-B-A oscillation.
3. At the entry point, the first call beyond the retry budget.
</details>

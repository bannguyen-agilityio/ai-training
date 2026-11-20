# Applying this to your own agent

Back to the [README](../README.md).

## Instrumentation checklist

- [ ] One span per step, named `step-N` (type `chain`)
- [ ] The thought and chosen action in the step's metadata; args as input; the result as output
- [ ] Right span types: `generation` for LLM calls (with usage), `tool`, `retriever`
- [ ] Errors flagged on the span (`level="ERROR"`, `status_message`), not only inside the output
- [ ] The root set to `WARNING` when a step cap ends the run
- [ ] `propagate_attributes` for session, user, trace name and metadata

## Review checklist

1. Read the root: task, answer, level.
2. Rebuild the thought → action → result table; mark no-info steps.
3. Find the first deviation from the evidence.
4. Judge each tool from its args.
5. Look for repeated `(tool, args)` and apply a retry budget.
6. Name the primary failure, fix its cause, re-run and compare.

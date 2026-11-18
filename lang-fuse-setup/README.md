# lang-fuse-setup

A minimal example of tracing an LLM call with [Langfuse](https://langfuse.com). It calls an OpenAI-compatible endpoint and records the call as a nested span and generation, with input, output and token usage.

## What is Langfuse?

Langfuse is an open-source observability and engineering platform for LLM applications. You instrument your code, and it records what your app sends to and gets back from models, so you can debug, measure and improve it. It can be used as a hosted cloud service or self-hosted.

Core concepts:

- **Trace**: one end-to-end run of your app, such as handling a single request.
- **Observation**: a step inside a trace. Observations can be nested. The main types are:
  - **Span**: any unit of work, such as a function or a retrieval step.
  - **Generation**: an LLM call. It stores the model, input, output and token usage, which Langfuse uses to show latency and cost.
- **Session and user**: optional tags that group traces into conversations or by end user.
- **Scores and evaluation**: attach quality scores (manual, user feedback or LLM-as-judge) to traces and compare them over time.
- **Prompt management**: store and version prompts in Langfuse and fetch them at runtime.
- **Datasets**: collections of test inputs and expected outputs for running experiments.

This app uses traces, a span and a generation. The Langfuse SDK reads `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` and `LANGFUSE_BASE_URL` from the environment, batches events in the background, and sends them when `langfuse.flush()` runs. Short-lived scripts like this one need that flush call, or the events may never be sent.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- A Langfuse project (cloud or self-hosted) and its API keys
- An OpenAI-compatible endpoint (for example a local proxy)

## Setup

```bash
uv sync
cp .env.example .env
```

Edit `.env`:

| Variable | Description |
| --- | --- |
| `OPENAI_BASE_URL` | Base URL of the OpenAI-compatible API |
| `OPENAI_API_KEY` | API key (must be non-empty, even if the proxy ignores it) |
| `OPENAI_MODEL` | Model name to call |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key |
| `LANGFUSE_BASE_URL` | Langfuse host, such as `https://cloud.langfuse.com` |

## Run

```bash
uv run main.py
```

The script sends a short prompt to the model, prints the reply, and flushes traces to Langfuse. Open your Langfuse project to see the `process-request` trace with its nested `llm-response` generation.

## Demo of all core concepts

`demo.py` shows each concept from the section above in one runnable script:

```bash
uv run demo.py
```

| Concept | Where in `demo.py` |
| --- | --- |
| Prompt management | `create_prompt` / `get_prompt` fetch a versioned prompt |
| User and session | `propagate_attributes(user_id=..., session_id=...)` |
| Trace and span | `handle-request` and nested `answer-question` |
| Generation | `llm-call` inside `ask()`, with model, input, output and usage |
| Score | `score_current_trace` adds a `user-feedback` score |
| Dataset and evaluation | `create_dataset`, then `run_experiment` with a `contains_expected` evaluator |

It creates the prompt and dataset in your Langfuse project, so rerunning adds a new prompt version and repeats the dataset items.

## How it works

`main.py` wraps the call in `process-request` (a span) and `llm-response` (a generation). The generation records the input messages, the output text and token usage. Usage is skipped if the endpoint doesn't return it.

"""Beginner-friendly demo of the core Langfuse concepts.

Langfuse is a tool that RECORDS what your LLM app does, so you can look at it
later in a web dashboard. Think of it as a flight recorder for your app.

This script walks through the main ideas, in order:
  1. Prompt management  - store prompts in Langfuse instead of in your code
  2. Traces and spans   - record the steps of one request
  3. Generations        - record one LLM call (input, output, tokens)
  4. Users and sessions - group traces by person and by conversation
  5. Scores             - attach a quality rating to a trace
  6. Datasets           - a saved list of test questions
  7. Experiments        - run the app on the whole dataset and grade the answers

Run with: uv run demo.py
Then open your Langfuse project in the browser to see everything it recorded.
"""

import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

# Load all the variables found as environment variables
load_dotenv()

from langfuse import Evaluation, get_client, propagate_attributes
from langfuse.api import DatasetItem
from langfuse.experiment import ExperimentItem
from langfuse.model import TextPromptClient

# get_client() creates the Langfuse client. It reads LANGFUSE_PUBLIC_KEY,
# LANGFUSE_SECRET_KEY and LANGFUSE_BASE_URL from the environment, which is how
# it knows which Langfuse project to send data to.
langfuse = get_client()

# This is the normal OpenAI client. It points at your proxy through
# OPENAI_BASE_URL. Langfuse is NOT inside this client: we tell Langfuse about
# each call ourselves (see the "generation" below).
client = OpenAI()
MODEL = os.environ["OPENAI_MODEL"]


def ask(question: str, prompt: TextPromptClient) -> str:
    """Make one LLM call and record it in Langfuse as a GENERATION.

    A generation is a special kind of observation made for LLM calls. Langfuse
    shows the model name, the input, the output and the token counts for it,
    and can use the token counts to work out cost and speed.
    """
    # prompt.compile() turns the stored Langfuse prompt into plain text.
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": prompt.compile()},
        {"role": "user", "content": question},
    ]

    # "with" starts recording when the block begins and stops (and records the
    # elapsed time) when the block ends. Anything started inside this block
    # becomes a child of whatever observation was already open outside it.
    with langfuse.start_as_current_observation(
        as_type="generation", name="llm-call", model=MODEL, input=messages
    ) as generation:
        response = client.chat.completions.create(model=MODEL, messages=messages)
        answer = response.choices[0].message.content or ""

        # Add the results to the recording. usage_details lets Langfuse show
        # token counts. Some proxies don't return usage, so we check first.
        generation.update(
            output=answer,
            usage_details=(
                {
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                }
                if response.usage
                else None
            ),
        )
    return answer


# --- 1. Prompt management ----------------------------------------------------
# Instead of hardcoding the system prompt in your code, you can store it in
# Langfuse. Every time you create a prompt with the same name, Langfuse saves it
# as a new VERSION, so you can change prompts without redeploying code and roll
# back if a new one is worse.
# A "label" such as "production" points to one version. Your code asks for the
# label, so you decide in the dashboard which version is live.
#
# WARNING: this demo calls create_prompt() on EVERY run, with the text hardcoded
# below. That makes a new version and moves the "production" label to it, so any
# edit you made in the dashboard stops being live and the hardcoded text wins.
# That is fine for a demo that needs a prompt to exist. In a real app, remove
# this call, create the prompt once (dashboard or a setup script), and only call
# get_prompt() so the dashboard stays the source of truth.
langfuse.create_prompt(
    name="demo-assistant",
    prompt="You are a concise assistant. Answer in one short sentence.",
    labels=["production"],
)
prompt = langfuse.get_prompt("demo-assistant", label="production", type="text")

# --- 2. Trace, spans, user and session ---------------------------------------
# A TRACE is the record of ONE run of your app, for example one user request.
# A trace is made of OBSERVATIONS arranged in a tree:
#   handle-request (span)          <- the first one becomes the trace itself
#   └── answer-question (span)     <- one step of the work
#       └── llm-call (generation)  <- the LLM call, created inside ask()
# A SPAN is an observation for any step of work (a function, a database
# lookup, a search...). A generation is a span made specifically for LLM calls.
#
# propagate_attributes() stamps everything created inside it with:
#   user_id    - who made the request, so you can filter traces per user
#   session_id - a conversation ID, so Langfuse can group several traces
#                (for example every message in one chat) together
#   tags       - free labels you can search by in the dashboard
with (
    propagate_attributes(user_id="user-123", session_id="session-abc", tags=["demo"]),
    langfuse.start_as_current_observation(
        as_type="span", name="handle-request", input="What is Langfuse?"
    ) as trace_span,
):
    # A nested span: it becomes a child of handle-request automatically,
    # because it is started while handle-request is still open.
    with langfuse.start_as_current_observation(
        as_type="span", name="answer-question"
    ) as step:
        answer = ask("What is Langfuse?", prompt)
        step.update(output=answer)

    trace_span.update(output=answer)

    # --- 3. Scores ---------------------------------------------------------
    # A SCORE is a rating attached to a trace. It can come from a user (thumbs
    # up/down), from a person reviewing, or from code or another LLM. Here we
    # record a made-up "helpful" rating of 1 on a numeric scale. In a real app
    # you would set this from real feedback. Scores let you filter and chart
    # quality over time.
    langfuse.score_current_trace(
        name="user-feedback", value=1, data_type="NUMERIC", comment="helpful"
    )

print("Answer:", answer)

# --- 4. Datasets -------------------------------------------------------------
# A DATASET is a saved list of test cases. Each item has an input and,
# optionally, the answer you EXPECT. You build it once and reuse it every time
# you change your prompt or model, to check you did not make things worse.
DATASET = "demo-questions"
langfuse.create_dataset(name=DATASET, description="Tiny demo dataset")
langfuse.create_dataset_item(
    dataset_name=DATASET,
    input="What is the capital of France?",
    expected_output="Paris",
)
langfuse.create_dataset_item(
    dataset_name=DATASET,
    input="What is 2 + 2?",
    expected_output="4",
)


# --- 5. Experiments ----------------------------------------------------------
# An EXPERIMENT runs your app over every dataset item and grades the results.
# Langfuse stores the run, so you can compare runs (for example "old prompt" vs
# "new prompt") side by side in the dashboard.
#
# You give it two functions:
#   task       - what to run for each item (here: ask the LLM the question)
#   evaluator  - how to grade the output (here: is the expected answer in it?)
# Langfuse calls them with extra keyword arguments, so they accept **kwargs to
# ignore the ones we don't use. Without it the call would fail.
def task(*, item: ExperimentItem, **kwargs: Any) -> str:
    # An item is either a dataset item (an object) or a plain dict (local data).
    # Ours come from a dataset, but the type allows both, so we handle both.
    question = item.input if isinstance(item, DatasetItem) else item["input"]
    return ask(str(question), prompt)


def contains_expected(
    *, output: Any, expected_output: Any, **kwargs: Any
) -> Evaluation:
    """Score 1 if the expected answer appears in the output, else 0."""
    # Dataset values are stored as JSON, so "4" can come back as the number 4.
    # str() makes sure we always compare text with text.
    hit = str(expected_output).lower() in str(output).lower()
    return Evaluation(name="contains_expected", value=1 if hit else 0)


result = langfuse.get_dataset(DATASET).run_experiment(
    name="demo-experiment", task=task, evaluators=[contains_expected]
)
# Prints a summary of the run: the outputs and the average score.
print(result.format())

# The Langfuse SDK collects events in memory and sends them in batches in the
# background. A short script can exit before the last batch is sent, so flush()
# forces everything to be sent now. Without it, some data may never show up.
langfuse.flush()

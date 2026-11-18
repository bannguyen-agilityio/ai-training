import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()

from langfuse import get_client

langfuse = get_client()
client = OpenAI()  # reads OPENAI_BASE_URL / OPENAI_API_KEY from env
MODEL = os.environ["OPENAI_MODEL"]

# Create a span using a context manager
with langfuse.start_as_current_observation(
    as_type="span", name="process-request"
) as span:
    # Your processing logic here
    span.update(output="Processing complete")

    # Create a nested generation for an LLM call
    with langfuse.start_as_current_observation(
        as_type="generation", name="llm-response", model=MODEL
    ) as generation:
        # Simple LLM call logic
        messages: list[ChatCompletionMessageParam] = [
            {"role": "user", "content": "Say hello in one sentence."}
        ]
        generation.update(input=messages)

        response = client.chat.completions.create(model=MODEL, messages=messages)

        generation.update(
            output=response.choices[0].message.content,
            usage_details=(
                {
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                }
                if response.usage
                else None
            ),
        )

        print(response.choices[0].message.content)

# All spans are automatically closed when exiting their context blocks


# Flush events in short-lived applications
langfuse.flush()

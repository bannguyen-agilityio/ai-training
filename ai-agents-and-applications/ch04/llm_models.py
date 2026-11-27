import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()  # A
openai_api_key = os.getenv("OPENAI_API_KEY")  # B


def get_llm():  # C
    return ChatOpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
        openai_api_key=openai_api_key,
        model_name=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
    )


# A Load the environment variables from the .env file
# B Get the OpenAI API key from the environment variables
# C Instantiate and return the ChatOpenAI model

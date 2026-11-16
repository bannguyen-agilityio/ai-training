# AI Agents and Applications

Chapter notebooks and examples | [Solutions](https://github.com/roberto-inf/building-llm-applications).

Python dependencies are managed with [uv](https://docs.astral.sh/uv/) as a **workspace**: every `ch*` folder is a member, and all chapters share one `uv.lock` and one `.venv` at the repo root.

## Setup

```bash
# install uv if needed: https://docs.astral.sh/uv/getting-started/installation/
uv sync --all-packages
```

This creates `.venv/` and installs the dependencies of every chapter.

## Running notebooks

**VS Code (click the file):**
1. Install the Jupyter and Python extensions.
2. Open this folder and click a `.ipynb` file, e.g. `ch01/01-langchain_examples.ipynb`.
3. Click **Select Kernel** > **Python Environments** > `.venv`.

**Browser:**
```bash
uv run jupyter notebook ch01/01-langchain_examples.ipynb
```

## Adding a new chapter

```bash
uv init --bare ch02
cd ch02
uv add <package>   # e.g. uv add langchain==1.0.3
```

Any folder named `ch*` is picked up automatically. Commit `pyproject.toml` and `uv.lock`.

## Common commands

| Task | Command |
|------|---------|
| Add a dependency to a chapter | `cd chNN && uv add <pkg>` |
| Remove a dependency | `cd chNN && uv remove <pkg>` |
| Re-sync environment | `uv sync --all-packages` |
| Run a script in a chapter's env | `uv run --package chNN python script.py` |

## Configuring the LLM

```bash
cp .env.example .env   # then edit .env
```

`OPENAI_BASE_URL` points `langchain-openai` at any OpenAI-compatible endpoint (proxy, local server, gateway). `OPENAI_API_KEY` is read automatically by `ChatOpenAI`. To use `OPENAI_MODEL` or load `.env` in a notebook:

```python
import os
from dotenv import load_dotenv   # uv add python-dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
```

## Notes

- Chapters share one lock file, so conflicting version pins between chapters will fail to resolve. If that happens, make the chapter a standalone project (remove it from `members` in the root `pyproject.toml`).
- Some examples need API keys (e.g. `OPENAI_API_KEY`). Set them as environment variables; never commit them.

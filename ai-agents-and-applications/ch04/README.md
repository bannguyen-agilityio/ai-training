# Chapter 4: Research summarization engine

Ask a question, and the app picks a research assistant, searches the web, scrapes and summarizes each result, then writes a Markdown report.

Source: [roberto-inf/building-llm-applications, `ch04`](https://github.com/roberto-inf/building-llm-applications/tree/main/ch04).

## Setup

Run all commands from the workspace root (`ai-agents-and-applications/`).

```bash
uv sync --all-packages
cp .env.example .env   # skip if you already have .env
```

Set these in `.env`:

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Key for OpenAI or your gateway |
| `OPENAI_BASE_URL` | OpenAI-compatible endpoint. Delete the line to use OpenAI directly |
| `OPENAI_MODEL` | Model name. Defaults to `gpt-5-nano` if unset |

A local endpoint must be running before you call any chain.

## Run it

Full pipeline:

```bash
uv run --package ch04 python ch04/chain_try_5_1.py
```

To ask something else, edit `question` in that file.

## Learn it step by step

Run each script with `uv run --package ch04 python ch04/<script>`.

| Step | Chain | Try script | What it does | Needs |
|------|-------|-----------|--------------|-------|
| Search | `web_searching.py` | `web_searching_try.py` | DuckDuckGo search, returns URLs | Web |
| Scrape | `web_scraping.py` | `web_scraping_try.py` | Extracts the text of a page | Web |
| 1a | `chain_1_1.py` | `chain_try_1_1.py` | Selects an assistant (raw model message) | LLM |
| 1b | `chain_1_2.py` | `chain_try_1_2.py` | Same, parsed into a dict | LLM |
| 2 | `chain_2_1.py` | `chain_try_2_1.py` | Writes search queries | LLM |
| 3 | `chain_3_1.py` | `chain_try_3_1.py` | Gets result URLs per query | Web |
| 4 | `chain_4_1.py` | `chain_try_4_1.py` | Scrapes and summarizes one URL | Web, LLM |
| 5 | `chain_5_1.py` | `chain_try_5_1.py` | Chains all steps into a report | Web, LLM |

```
question -> assistant (1) -> queries (2) -> URLs (3) -> summaries (4) -> report (5)
                                            \__ .map() runs these in parallel __/
```

Other files:

- `research_engine_seq.py`: the same pipeline as plain sequential Python, without LCEL composition.
- `prompts.py`: all prompt templates.
- `llm_models.py`: model configuration.
- `utilities.py`: JSON parsing helper.
- `sandbox_for_summarization.py`: the author's scratchpad, kept for reference. It does **not** run on LangChain 1.0 (`langchain.prompts` was removed).

## Tuning

| Constant | File | Default |
|----------|------|---------|
| `NUM_SEARCH_QUERIES` | `chain_2_1.py` | 2 |
| `NUM_SEARCH_RESULTS_PER_QUERY` | `chain_3_1.py` | 3 |
| `RESULT_TEXT_MAX_CHARACTERS` | `chain_4_1.py` | 10000 |

`research_engine_seq.py` defines its own copies. The search prompt's example shows three queries, so a model may return more than `NUM_SEARCH_QUERIES`.

## Troubleshooting

| Symptom | Cause and fix |
|---------|---------------|
| A script hangs, or connection errors | The LLM endpoint is unreachable. Check `curl "<OPENAI_BASE_URL>/models"` |
| `primp.BuilderError: Invalid impersonate` | `primp` is too new for `ddgs`. Run `uv sync --all-packages` to restore the pinned version |
| `Status code 429` or `403` when scraping | The site blocks or rate-limits scripts. Try another URL |
| Unrelated search results | DuckDuckGo results vary by region and over time. Re-run, or reword the query |
| Empty `{}` or errors after step 1 or 2 | The model did not return bare JSON, so `to_obj` returned `{}`. Retry or use a stronger model |

## Changes from upstream

- `requirements.txt` replaced by `pyproject.toml` (uv workspace member).
- `bs4` became `beautifulsoup4`; added `python-dotenv`; dropped `duckduckgo-search`, since search uses `ddgs`.
- Pinned `primp==0.15.0`, because newer releases break `ddgs==9.5.5`.
- `llm_models.py` reads `OPENAI_MODEL`.
- Omitted `.env_example` (use the root `.env.example`), `Notes.txt`, and the Windows-specific `.vscode/launch.json`.

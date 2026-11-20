# Troubleshooting

Back to the [README](../README.md).

| Symptom | Fix |
|---|---|
| Trace not visible yet | Ingestion is async. `traj-analyze` retries up to 90 s (`--timeout`). Check `get_client().auth_check()` prints `True`. |
| Empty input/output in analysis | The fetch asks for `fields="core,basic,io,metadata"`; JSON-string fields are parsed automatically. |
| Self-hosted version mismatch | `api.observations.get_many` needs a recent Langfuse server. Upgrade it and check `LANGFUSE_BASE_URL`. |
| Python 3.14 wheel errors | `uv python install 3.14`, then `uv sync`. Do not lower the Python floor; report the package that lacks a 3.14 wheel. |
| No Langfuse keys | The agent still runs with tracing off (no link printed). `traj-analyze` exits with a message. |
| "Context error: No active span" lines | Printed when tracing is off. Harmless. |

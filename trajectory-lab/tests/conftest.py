import os

for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"):
    os.environ.pop(k, None)
os.environ["LANGFUSE_TRACING_ENABLED"] = "false"  # tests never talk to Langfuse

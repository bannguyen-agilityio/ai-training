# Modular Chaining & LCEL

## 1. What to Learn

* **The Runnable Protocol**: The universal invocation protocol enabling standard operations across all components, specifically invoke(), ainvoke(), batch(), and stream()

* **LangChain Expression Language (LCEL)**: The declarative syntax used to compose components into production-grade programs using the pipe (\|) operator

* **Composition Primitives**: Mastering RunnableSequence for sequential steps and RunnableParallel for concurrent operations.

* **Standardized Content Blocks**: Utilizing the .content\_blocks property to ensure consistent data types across different LLM providers (e.g., swapping OpenAI for Anthropic)

* **Structured Outputs**: Enforcing strict schema adherence using **Pydantic models** and the .with\_structured\_output() method to ensure model responses are computer-readable

* **Operational Modifiers**: Learning to implement .with\_retry() for error handling and .with\_fallbacks() for reliability when primary models fail. Explore retry strategies, exponential backoffs, and when each is appropriate

* **Pipeline Instrumentation**

  * Tracing RunnableSequence and RunnableParallel as Nested Spans

  * Latency Profiling per Component

  * Confirming Fallback and Retry Execution via Trace Evidence

* **Tracing Hierarchy**

  * The Trace as a Nested Tree of Runs, Parent and Child Span Relationships

* **Compulsory Security:**

  * **Content Moderation Middleware:** Integrating **ContentModerationMiddleware** into LCEL chains to automatically check inputs and outputs for toxic or prohibited content using OpenAI-powered safety checks.

  * **Schema Enforcement for Security:** Using Pydantic not just for structure, but to validate that model outputs do not contain **sensitive patterns or unauthorized tool calls.**

## 2. How to Learn

* **"Pipes and Blocks" Drills**: Practice connecting prompt templates, chat models, and output parsers into a single, functional chain

* **Async and Batch Practice**: Implementing .batch() to process whole datasets at once, rather than looping through single calls, to understand efficiency at scale

* **Composition Labs**: Building RunnableParallel workflows that call multiple models or tools simultaneously and aggregate their results.

* **Schema Stress-Testing**: Create complex Pydantic/Zod models with strict validation rules and attempt to "break" the schema with ambiguous inputs.

* Monitoring and tracing with **LangFuse**

## 3. Where to Learn

* **E-book:** *AI Agents and Applications* (Part 2, Chapters 3–4 on Summarization and Pipelines)

* **Documentation**: LangChain Core API Reference on the **Runnable Interface**

* **Guide**: *The Industrialization of Agentic Workflows* for documentation on standardized content blocks and LCEL

## 4. Subjective Outputs Required

* **The Schema-Enforced Extractor**: A functional chain that takes unstructured text and extracts it into a validated Pydantic object (e.g., a TaskPlan with a title and a list of actionable steps).

* **The Multi-Provider Pipeline**: An LCEL-built application that successfully swaps model providers (e.g., from GPT-4o-mini to Claude 3.7) using standardized content blocks without requiring code changes to the UI.

* **The High-Efficiency Batch Processor**: A script demonstrating the ability to take a dataset of 50+ entries and process them through an LCEL chain using .batch(), proving knowledge of production efficiency.

* **The Self-Healing Chain**: A robust workflow that utilizes .with\_fallbacks() to automatically switch to a secondary model if the primary API call returns an error or times out.

* **The Secure Schema Validator**: A production-grade pipeline that extracts JSON data from unstructured text while utilizing middleware to automatically block toxic content and PII

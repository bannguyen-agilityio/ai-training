# The Engine & Basic Prompting

## 1. What to Learn

* **The GenAI Mindset:** Understanding the "inherently spiky intelligence" of LLMs, their tendency to excel at complex reasoning while occasionally failing at simple logic.

* **Engine Parameters (The "Knobs"):**

  * **Temperature:** Controlling creativity vs. determinism (e.g., 0.8 for creative tasks, 0 for factual Q\&A).

  * **Top P (Nucleus Sampling):** Balancing diversity in word selection.

  * **Stop Sequences & Max Length:** Managing output termination and token boundaries.

  * **Frequency/Presence Penalties:** Reducing repetition in long-form generation.

* **Systematic Structure:**

  * Persona, Context, Instruction, Input, Steps, and Output Format.

  * **Zero-Shot Prompting:** Relying on the model's pre-trained knowledge without examples.

  * **Few-Shot & One-Shot Prompting:** Providing structured input-output pairs to illustrate specific styles, tones, or reasoning patterns.

* **Instrumentation & Tracing Hierarchy:**

  * LangFuse setup

  * The Run as the Atomic Unit

  * Reading a single-turn trace (input, output, latency, token count)

* **Compulsory Security Primitives:**

  * Use XML-style tags or explicit delimiters to prevent **Prompt Injection (LLM01)**

  * **Anti-Extraction Directives**: Implementing mandatory directives that forbid the model from revealing, repeating, or summarizing its internal system prompt

* **Threat Awareness:** NIST AML Taxonomy

  * **Unicode Normalization**: Normalize inputs to prevent homoglyph attacks \- Evasion, Poisoning, and Privacy

## 2. How to Learn

* **Exploration-First Learning:** Use a "Playground" environment to manually adjust parameters (Temperature/Top P) and observe the immediate impact on token probability and response consistency.

* **Comparative Analysis:** Running the same prompt across different models (e.g., Google Flan T5 vs. GPT-4.1/5) to understand how different architectures interpret instructions.

* **Parameter Drills:** Iteratively refining prompts by changing single words or formatting structures to see how slight text changes result in vastly different responses.

* **Red-Teaming Drills:** Attempting basic prompt injection and extraction on your own prompts

* **Structural Templates**: Converting vague natural language requests into structured templates using **LangChain’s PromptTemplate**

## 3. Where to Learn

* **Foundational Course:** *Generative AI for Everyone* (Coursera/[DeepLearning.AI](http://DeepLearning.AI)).

* **Book**: [*AI Agents and Applications*](https://drive.google.com/file/d/1BuYlS-_OJxgYg7MdUYmu2LrHGRg3VlmK/view?usp=drive_link) (Part 1, Chapters 1–2)

* **Frameworks**: LangChain, LangFuse

* **Guides:** *Prompt Engineering Guide* (promptingguide.ai) and *Advanced Prompt Engineering Techniques* (Patronus AI).

* **Lab Environments:** OpenAI Playground (for GPT models) and Hugging Face Inference API (for open-source models like Flan-T5).

* **Reference**: NIST Technical Series on **Adversarial Machine Learning** (Taxonomy and Terminology

## 4. Subjective Outputs Required

To prove the knowledge is firm, trainees  must produce the following:

* **The Hardened Classifier**: A text classification tool that accurately categorizes complex input while successfully resisting instructions designed to make it reveal its internal system prompt.

* **Parameter Stability Report**: A documented comparison showing how different temperature settings (0.0 vs. 1.0) impact the consistency of an LLM’s answer to a logic-heavy problem, such as the "Strange Sequence" or "Palindrome" problems.

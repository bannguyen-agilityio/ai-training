# Rapid Development with DeepAgents

1. ### **What to Learn**

   * **Agent Scaffolding**: Mastering the **create\_deep\_agent** factory function to build production runtime environments with built-in streaming and persistence.

   * **Strategic Planning**: Implementing the **write\_todos** tool to force the model to decompose complex, multi-step goals into a persistent, verifiable checklist.

   * **Virtual File System**: Utilizing file-based operations (**read\_file**, **write\_file**) as external "working memory" to manage and store data that exceeds the model's context window limits.

   * **Sub-agent Delegation**: Spawning specialized sub-agents via the **task** tool to maintain **Context Isolation**, ensuring that heavy data retrieval or processing does not pollute the main orchestrator's context window.

2. ### **How to Learn**

   * **Harness Optimization Drills**: Practice improving an agent's performance on benchmarks (like HumanEval) solely through scaffolding and middleware changes

   * **The "Critique" Workflow**: Building a multi-agent system where a **Policy Critique Sub-Agent** reviews draft reports stored in the shared filesystem and provides feedback without direct modification.

   * **Observability Integration**: instrumenting DeepAgents with **LangFuse** to track the "Reasoning Trace" (Chain-of-Thought) and identify exactly where an agent "loses the plot".

3. ### **Where to Learn**

   * **Tutorial**: Krish Naik Academy, *"Building Deep Agents with LangChain: A Complete Hands-On Tutorial"*.

   * **Documentation**: LangChain Docs: *"Deep Agents Overview"* and *"Context engineering in agents"*.

   * **Technical Case Study**: LangChain Blog, *"Improving Deep Agents with Harness Engineering"*.

   * **Article**: *"Deep Agent Use Cases That Work in Production AI Systems"*.

4. ### **Subjective Outputs Required**

   * **The Artifact-Producing Agent**: A functional system that produces a multi-file research report or software project stored in its virtual filesystem rather than just a chat response.

   * **Strategic Planning Trace**: A LangFuse trace showing the agent using write\_todos to create and update an implementation plan before calling any other tools.

   * **Context Isolation Proof**: Evidence of a complex task (e.g., policy analysis) where heavy retrieval data was isolated in specialized worker sub-agents, leaving the main agent's context window "clean" and focused.

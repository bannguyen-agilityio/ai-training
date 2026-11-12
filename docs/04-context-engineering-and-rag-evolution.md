# Context Engineering & RAG Evolution

## 1. What to Learn

* **The Paradigm Shift:** Understanding that 70% of production errors stem from incomplete or irrelevant context rather than model capability.

* **The Three-Layer Memory Model:**

  * **Working Memory:** Managing the current conversation turn and context window limits.

  * **Episodic Memory:** Storing "experiences," user preferences, and past errors to enable **cross-conversation continuity**.

  * **Semantic Memory:** Managing the stable knowledge base (enterprise documents) through the RAG system.

* **The Evolution of RAG:**

  * **Naive RAG:** The basic "index-retrieve-generate" pipeline.

  * **Advanced RAG:** Implementing **re-ranking**, query rewriting, and hybrid search.

  * **Agentic RAG:** Building active agents that autonomously decide if retrieval is needed and self-verify answer correctness.

  * **GraphRAG:** Using knowledge graphs to answer global, open-ended questions that vector-only RAG often misses.

  * **Small-to-Big Retrieval**: Expansion-chunks small precision hits into the model's longer context window

* **Indexing Patterns:** Implementing **ParentDocumentRetriever** and **MultiVectorRetriever** for smarter chunking

* **Context Window Management:**

  * **"Lost in the Middle" Problem:** Solving the model's tendency to ignore information in the middle of ultra-long (200K+) contexts.

  * **Optimization Strategies:** Implementing **Hierarchical Context Structures**, **Selective Injection**, and **Structured Tagging** (using XML/Markdown tags).

* **Question Transformations**: Implementing **Rewrite-Retrieve-Read, Step-back queries**, **HyDE** (Hypothetical Document Embeddings), and **Reciprocal Rank Fusion (RRF)** for merging multi-query results

* **The RAG Triad & Agent Reliability Metrics:**

  * Answer Faithfulness

  * Context Precision

  * Answer Relevance via Ragas and DeepEval

* **Tolerance & Failure Resilience**: Timeout handling and fallback retrieval strategies

* **Evaluation Dataset Design:**

  * Constructing a Curated Question and Ground-Truth Answer Set for Consistent Retrieval Benchmarking

* **Offline Evaluation:**

  * Automated Pytest Suites that Score RAG Pipeline Faithfulness against a Versioned Dataset

* **Compulsory Security**

  * **Document Provenance:** Tracking uploader, timestamp, and signature to prevent **Corpus Poisoning (BadRAG)**, where malicious documents rank high for target queries.

  * **Embedding Inversion Protection:** Learning to use perturbation techniques to prevent original text reconstruction from embeddings (**Vec2Text attacks**)

## 2. How to Learn

* **Architecture Mapping:** Designing a system that chooses between RAG and long-context windows based on document volume (e.g., using RAG for \>500 pages).

* **Memory Injection Drills:** Using LangChain middleware to dynamically inject user writing styles from a persistent **Store** or compliance rules from **Runtime Context**.

* **Self-Reflection Labs:** Implementing the **Reflexion framework**, where an agent analyzes its own failures and stores those "reflections" in episodic memory for future use.

* **Indexing Labs**: Implementation of **ParentDocumentRetriever** and **MultiVectorRetriever** to compare precision against standard chunking

* **Metric Benchmarking**: Using frameworks like **Ragas** to measure the "RAG Triad": **Context Precision**, **Faithfulness**, and **Answer Relevance**.

* **Question Transformation Drills**: Building a "Rewrite-Retrieve-Read" workflow and visualizing how the LLM's tailored queries uncover more diverse content than the original user question.

* **Security Auditing**: Simulating a **Corpus Poisoning** attack by injecting a malicious document and implementing signature verification to ensure the agent rejects unverified data

## 3. Where to Learn

* **E-book:** *AI Agents and Applications* (Parts 3 & 4, Chapters 6–10)

* **Guide:** *Context Engineering Guide: RAG, Memory Systems & Dynamic Context (2026)*.

* **Documentation:** LangChain Docs on *Context Engineering in Agents* and *Retrieval-Augmented Generation*.

* **Reference**: [PoisonedRAG](https://github.com/sleeepeer/PoisonedRAG), [Article](https://www.linkedin.com/posts/pascalbiese_poisonedrag-knowledge-corruption-attacks-activity-7230151506514071553-yT8R)

* **Tool**: [RAGAS](http://github.com/vibrantlabsai/ragas)

* **Engines**: ChromaDB, Faiss, Qdrant, Neo4j, Google Embeddings 2, Docling for OCR

## 4. Subjective Outputs Required

* **The Memory-Enabled Travel Chatbot**: A system that utilizes **Episodic Memory** to recall user style preferences across multiple conversation threads using a shared `thread_id`.

* **Advanced RAG Dashboard**: A retrieval engine achieving **\>90% Answer Faithfulness** on a multi-document dataset, evidenced by a Ragas evaluation report.

* **Hardened RAG Pipeline**: A production-grade ingestion and retrieval script featuring mandatory PII detection/masking and verifiable document signatures

* **Quality Benchmarking Report:** A documented evaluation showing a jump in accuracy from Naive RAG (typically 60-70%) to Agentic RAG (85-95%) using a curated dataset.

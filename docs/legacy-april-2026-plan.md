# Generative AI with LLMs Training Plan

## **24 April 2026**

# **OVERVIEW**

This training plan is designed to equip participants with comprehensive knowledge and practical skills in Generative AI with LLMs. Through a structured curriculum and hands-on exercises, participants will gain a deep understanding of the fundamental concepts, best practices, and advanced techniques required to proficiently work with LLMs.

# **PREREQUISITES**

Participants are expected to have a solid understanding of Python programming.

English writing skills would be compulsory.

Accounts:

* OpenAI: [https\://platform.openai.com/](https://platform.openai.com/)

* Coursera: [https\://www\.coursera.org/](https://www.coursera.org/)

* DeepLearning: [https\://www\.deeplearning.ai/](https://www.deeplearning.ai/)

Materials:

* Visual Studio Code

* Python version \>= 3.10

* Pip 3

* Venv: [https\://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)

#

# **TIMELINE**

* FUNDAMENTAL PLAN: **TBD**

  * Phase 1: 3 weeks

    * GENERATIVE AI FOR EVERYONE

    * PROMPT ENGINEERING

    * PRACTICE WITH FREE OPENAI

    * ADVANCED PROMPT TECHNIQUES

  * Phase 2: update later

# **KEY OBJECTIVES**

* Understand the principles and applications of Generative AI.

* Master prompt engineering techniques for effective LLM utilization.

* Gain hands-on experience in developing and deploying Generative AI solutions.

# **FUNDAMENTAL PLAN**

## **GENERATIVE AI FOR EVERYONE (1 week)**

Objective: Foundational understanding of Generative AI techniques and their applications in various fields. Participants should be equipped with the knowledge and tools to appreciate, utilize, and contribute to the advancement of Generative AI technologies in their respective fields.

Need to take the terminologies and research more about that.

Course: [https\://www\.coursera.org/learn/generative-ai-for-everyone](https://www.coursera.org/learn/generative-ai-for-everyone)

[https\://learn.deeplearning.ai/courses/generative-ai-for-everyone/information](https://learn.deeplearning.ai/courses/generative-ai-for-everyone/information)

* Introduction to Generative AI and LLMs.

* Exploring the capabilities of popular LLMs.

## **PROMPT ENGINEERING (3 days)**

Objective: Landing on the prompt engineering space, the goal is to develop and optimize prompts to efficiently utilize LLMs across various applications and research topics. At the end of this module, you will be able to write completed prompts to work with the OpenAI model for specific fields.

Prompt Caching: [https\://developers.openai.com/api/docs/guides/prompt-caching](https://developers.openai.com/api/docs/guides/prompt-caching)

Guide: [Prompt Engineering Guide \| Prompt Engineering Guide (promptingguide.ai)](https://www.promptingguide.ai/)

* How does LLM prompt work?

* [LLM Settings](https://www.promptingguide.ai/introduction/settings)

  * Temperature

  * Top P

  * Stop sequences

  * Max Length

  * Frequency penalty

  * Presence penalty

* Principles of prompt engineering

  * [Prompt Formatting](https://www.promptingguide.ai/introduction/basics#prompt-formatting)

  * [Prompt Elements](https://www.promptingguide.ai/introduction/elements)

  * [Designing Prompts](https://www.promptingguide.ai/introduction/tips)

* Prompting basic techniques

  * [Zero-shot prompt](https://www.promptingguide.ai/techniques/zeroshot)

  * [Few-shot prompt](https://www.promptingguide.ai/techniques/fewshot)

## **PRACTICE WITH FREE OPENAI (2 days)**

Objective: Get to know how prompts and parameters work with a LLM model in a real case.

Hands-on practice using OpenAI's [Playground](https://platform.openai.com/playground):

### **PRACTICE 1**

*Develop an assistant that utilizes the GPT-3.5-turbo model to classify a given text into either neutral, negative, or positive categories.*

* Dataset: [https\://huggingface.co/datasets/mteb/tweet\_sentiment\_extraction](https://huggingface.co/datasets/mteb/tweet_sentiment_extraction)

  * Utilize this dataset for practicing and evaluating the result.

### **PRACTICE 2**

*For this practice, we will examine a few techniques of Prompt Engineering to achieve the desired results. To gain a better understanding, we will need to practice with two models: Google Flan T5 Base and GPT-3.5 Turbo. This practice will consist of two parts:*

1. *Utilizing the **Google/Flan-T5-Base** Hugging Face Inference API (refer to the **Inference API** on the right side):*
   [*https\://huggingface.co/google/flan-t5-base*](https://huggingface.co/google/flan-t5-base)

2. *Hands-on practice using OpenAI's [Playground](https://platform.openai.com/playground)*

*Requirements:*

* Dataset: [https\://huggingface.co/datasets/knkarthick/dialogsum](https://huggingface.co/datasets/knkarthick/dialogsum)

  * Utilize this dataset for practicing and evaluating the result.

* Summarize Dialogue without Prompt Engineering.

* Summarize Dialogue with an Instruction Prompt.

  * Zero Shot Inference with an Instruction Prompt.

* Summarize Dialogue with One Shot and Few Shot Inference.

  * One Shot Inference.

  * Few Shot Inference.

* \[***For OpenAI Playground Chat***\] Generative Configuration Parameters for Inference.

  * You can change the configuration parameters of the method to see a different output from the LLM.

## **ADVANCED PROMPT TECHNIQUES (1 week)**

Objective: Explore advanced prompting techniques to unlock the full potential of LLMs for specific tasks. There are many advanced prompting techniques available but we will just focus on 3 types of them that are most popular in real cases, and you will get to know how to write prompts for specific tasks. At the end of this module, you will be able to write advanced prompts for specific tasks or even complex tasks.

Course: [https\://learn.deeplearning.ai/courses/chatgpt-prompt-eng](https://learn.deeplearning.ai/courses/chatgpt-prompt-eng)

Guide: [Prompt Engineering Guide \| Prompt Engineering Guide (promptingguide.ai)](https://www.promptingguide.ai/)

Ebook [Unlocking the Secrets of Prompt Engineering](https://drive.google.com/file/d/1oYz6G057nHN0_gGWLxdkAOtYDzr4JMUM/view?usp=sharing) (Chapter 1 & Chapter 2\)

* Prompting advanced techniques

  * [Chain-of-Thought (CoT)](https://www.promptingguide.ai/techniques/cot)

  * [Prompt Chaining](https://www.promptingguide.ai/techniques/prompt_chaining)

  * [ReAct prompting](https://www.promptingguide.ai/techniques/react)

* Prompts for specific tasks:

  * Iterative

  * Summarizing

  * Inferring

  * Transforming

  * Expanding

  * Chatbot

## **LANGCHAIN WITH OPENAI MODEL (2 weeks)**

Objective: In this section, you will gain hands-on experience building applications powered by LLMs using the LangChain framework with OpenAI’s API. At the end of this module, you will gain practical experience in using LangChain chains, pipelines, and other essential components to build applications that can process and generate text based on user input or data.

*Note: Practice with each component is required to push daily.*

Course: [LangChain for LLM Application Development](https://learn.deeplearning.ai/courses/langchain/lesson/1/introduction)

Document: [🦜️🔗 LangChain](https://docs.langchain.com/oss/python/langchain/overview)

* Introduction to LangChain

  * Overview of LangChain and its purpose

  * [Installing and setting up LangChain](https://docs.langchain.com/oss/python/langchain/install)

* LangChain components

  * [Prompts](https://docs.langchain.com/langsmith/prompt-engineering-concepts)

    * Creating and using templates

      * Prompt Template

      * Few Shot Prompt Template

      * Chat Prompt Template

      * Partial Prompt Template

    * Template formatting and variable substitution

  * [Chains](https://python.langchain.com/docs/)

    * Understanding how Chains work

    * Creating and using LangChain chains

      * [LLMChain](https://python.langchain.com/docs/versions/migrating_chains/llm_chain/)

      * LLMRouterChain \- [LLMRouterChain](https://python.langchain.com/docs/versions/migrating_chains/llm_router_chain/)

      * LCEL Chains

    * Passing prompts and inputs to language models

      * RunnableAssign

      * RunnablePassthrough

      * RunnableLambda

  * OpenAI

    * Authenticating with OpenAI API

    * Instantiating OpenAI LLM: [ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai) and [OpenAI](https://docs.langchain.com/oss/python/integrations/providers/openai) instances

      * *The latest and most popular OpenAI models are **chat completion** models. Unless you are specifically using **gpt-3.5-turbo-instruct**, you are probably using ChatOpenAI instead.*

    * Handling OpenAI API errors and rate limiting

    * Setting parameters (temperature, top\_p, cache, max\_tokens, streaming...)

  * [Output Parser](https://python.langchain.com/docs/how_to/#output-parsers)

    * Built-in parsers

    * Custom Output parsers

  * [Retrieval Augmented Generation](https://python.langchain.com/docs/tutorials/rag/#overview)

    * [Document Loader](https://docs.langchain.com/oss/python/integrations/document_loaders)

      * Understanding how to load external resources with various types

    * [Text splitters](https://docs.langchain.com/oss/python/integrations/splitters)

      * Splitting types

      * Deeply understanding how Chunk size and overlap works

    * [Embedding models](https://docs.langchain.com/oss/python/integrations/text_embedding)

      * OpenAI Embeddings

      * Custom Embeddings

    * [Vector stores](https://docs.langchain.com/oss/python/integrations/vectorstores)

      * Creating and using Chroma vector database

    * [Retrievers](https://docs.langchain.com/oss/python/integrations/retrievers)

      * Understanding how Retrievers work

      * Find the list of supporting Retrieval types with use cases

    * [Indexing](https://docs.langchain.com/oss/python/langchain/rag#1-indexing)

      * Understanding the indexing workflow

## **PRACTICE: LANGCHAIN WITH ADVANCED PROMPT (1 week)**

Practice: **Build a Customer Support Chatbot for an E-commerce Platform.**

Objective: Develop a chatbot system that can handle common customer support queries and provide relevant responses for an e-commerce platform, using LangChain components and OpenAI models.

Note: For this practice, only the response to the current user's question is required; there's no need to apply memory over the chatbot.

Techstack:

* Model: OpenAI GPT-4o-mini

* Application UI: [Streamlit](https://python.langchain.com/docs/integrations/providers/streamlit/)

* Python

* LangChain: Prompt Templates, Chains, Parsers, RAG

* LangSmith: [https\://www\.langchain.com/langsmith](https://www.langchain.com/langsmith)

Requirements:

* Create a knowledge base and a set of documents containing information about the e-commerce platform's products, ordering process, shipping, returns, and common customer issues/solutions

  * Referring to [these documents](https://drive.google.com/drive/folders/1z0NSGLnHcB5bq9snP5AtzvvCQLGrY3TK?usp=sharing) as base documents to understand the information, and make additions or modifications as needed based on your understanding of the e-commerce domain and the anticipated customer queries.

* Understand the user’s query or issue related to the e-commerce platform

* Retrieve relevant information from the knowledge base

* Generate a relevant and helpful response based on the query and retrieved information

* Output will display the chatbot’s response to the user’s query

* Handle and display any errors or exceptions that occur during the process

* Design and structure the prompts effectively specifying the e-commerce domain, orchestrate the different steps using appropriate chains, and manage conversation flow.

* Using LangSmith to inspect the input, output, and token usage

## **EVALUATION (2 days)**

Objective: Grasp the significance of assessing LLM-based systems (which is distinct from standalone LLM performance evaluation). Acquire knowledge about quantifying the quality of LLMs through defined metrics and integrate into CI/CD workflows in production environments.

Library: [Promptfoo](https://www.promptfoo.dev/docs/intro)

* Introduction

* Configuration

  * Prompts, tests and outputs

  * Scenarios

  * Caching

* CLI: init, eval, view and share test reports

* Assertions and Metrics

* Providers

* Integrations

## **PRACTICE: APPLY EVALUATION TO THE LAST PRACTICE (2 days)**

Gain practical experience in system evaluation, prompt optimization, and multi-agent interaction analysis.

Objective:

* **Evaluate the performance of LLM-based systems**: assess the standalone performance of LLM in various scenarios.

* **Optimize prompting strategy**: Investigate how well the LLM responds to different prompts and optimize the prompts for better outputs in various aspects: output length, token cost, latency…

* **Automated evaluation:** automatically run tests to calculate the metrics as part of the CI pipeline.

Techstack:

* [Promptfoo](https://www.promptfoo.dev/docs/intro)

Requirements:

* Evaluating that chatbot can be able to accurately understand and interpret customer conversation.

* Evaluating that chatbot’s responses are relevant to the e-commerce domain.

* Evaluating that chatbot can effectively use LangChain components and OpenAI to handle customer queries.

* Evaluating that the chatbot should provide relevant and accurate information in response to customer conversation. Comparing the chatbot’s responses with predefined correct responses.

* Measuring the response time and cost to ensure it’s reasonable.

* Trying different prompts to compare and optimize the response in latency, cost and accuracy.

## **INTEGRATION & DEPLOYMENT  (1 day)**

Objective: exploring the frameworks and cloud services for developing, deploying, and maintaining generative AI applications in production environments. We can easily integrate and develop applications with the OpenAI API using existing web frameworks, such as FastAPI and Django, to serve API endpoints.

### **Deploying LLM apps**

Frameworks to build API endpoints with OpenAI integration:

* [FastAPI](https://fastapi.tiangolo.com/): Python web framework for building APIs.

**Cloud Services** (If you have experience with cloud platforms such as  Microsoft Azure or AWS, please select accordingly based on your background):

* OpenAI services:

  * OpenAI API

  * For Microsoft Azure: [Azure OpenAI service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

* Deploy LLM-based applications to:

  * AWS

  * Microsoft Azure

### **Streamable ability**

When developing an API for inferencing we should consider the option to stream the response.

* For FastAPI: [Custom Response \- HTML, Stream, File, others](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)

### **Observing LLM apps**

* [LangSmith](https://www.langchain.com/langsmith)

## **ADVANCED LANGCHAIN (1 week)**

Objective: Develop the ability to design and implement complex multi-step workflows, information extraction and summarization pipelines, and agent-based systems that can handle intricate tasks by leveraging LangChain’s advanced features and integrations.

Course: [Functions, Tools and Agents with LangChain](https://www.deeplearning.ai/short-courses/functions-tools-agents-langchain/)

Document: [🦜️🔗 LangChain](https://python.langchain.com/docs/get_started/introduction)

* [Models](https://docs.langchain.com/oss/python/langchain/models)

* [Messages](https://docs.langchain.com/oss/python/langchain/messages)

* [Tools](https://docs.langchain.com/oss/python/langchain/tools)

  * Built-in tools (Toolkits)

  * Custom tools

  * Tools as OpenAI functions

* [Agents](https://docs.langchain.com/oss/python/langchain/agents)

  * Concepts

  * Types

    * Tool Calling

    * OpenAI tools

    * ReAct

  * Agent Executor

    * Custom Agent

    * Streaming

    * Handle Parsing errors

    * Access intermediate steps

    * Cap the max number of iterations

    * Timeouts

* [Memory & State Management](https://docs.langchain.com/oss/python/concepts/memory)

  * Conversation Buffer Memory

  * Conversation Summary Memory

* [Callbacks](https://python.langchain.com/docs/concepts/callbacks/)

  * Built-in callbacks

  * Custom callbacks

## **PRACTICE: APPLY LANGCHAIN ADVANCED COMPONENTS (2 weeks)**

Practice: **Enhance the customer support chatbot system with an agent-base**

Objective: Apply the agent-based system that can perform a multi-step task to the last practice: Customer support chatbot

Techstack:

* Model: OpenAI GPT-4o-mini

* Application UI: Streamlit

* Materials:

  * Transfer existing documents to a simple database

  * Only keep FAQs as a document

* LangChain

  * OpenAI agent with tools

  * Conversational memory management

* Tools/subtasks:

  * [SerpAPI](https://python.langchain.com/docs/integrations/providers/serpapi/): [Google Shopping API](https://serpapi.com/google-shopping-api): querying real-time product prices

  * [SQL Toolkit](https://python.langchain.com/docs/integrations/toolkits/sql_database/): querying data from the database using SQL

* LangSmith

Requirements

* Use the AgentExecutor to orchestrate the execution of subtasks by the agent.

* The agent will be responsible for understanding the user’s query, retrieving product details from the database,

* The agent will leverage conversational memory and context management components to maintain and retrieve relevant information throughout the conversation.

* Using the searching tool to get the specific product online price, the user can compare it with the same product in the system if the user requests.

* Error handling fully: API errors, API authentication, rate limiting, and edge cases: no results,...

* Input: allow users to input their questions or issues

* Output:

  * Display the chatbot’s response to the user’s query

  * Include relevant production information, price comparisons, and any additional context or recommendations.

* Testing and Validation

  * Create test cases to validate the agent’s behavior and the chatbot’s responses

  * Evaluate various customer support queries and scenarios

 ![][image2]
www\.agilityio.com

[image2]: <data:image/png;base64,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>

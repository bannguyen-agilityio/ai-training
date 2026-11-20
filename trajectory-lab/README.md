# trajectory-lab

## A story: the right words, the wrong path

A shop has a support agent. A customer asks: *"My order A-1002 arrived 40 days ago. Can I get a cash refund?"*

1. The agent looked up the refund policy. It found the answer: cash refunds within 30 days, store credit after.
2. Then it ignored that answer and searched the web instead. It got generic blog posts.
3. It replied: *"Yes, you can get a cash refund."*

That reply is friendly and confident, so a quick look says it is fine. It is wrong: 40 days is past the 30-day limit.

Checking only the final answer would miss how it went wrong. **Trajectory analysis** means reading the *path* the agent took (every step, in order) and judging the path, not just the answer. That is what this lab teaches.

## What you'll learn

Four skills, each practised on a small fake support agent:

1. **Reading a trace**: rebuild what the agent thought, did and learned at each step.
2. **Reasoning deviations**: spot where the agent first stopped following its own evidence.
3. **Wrong tool selection**: spot when the agent used the wrong tool for the job.
4. **Doom loops**: spot where retrying turned into repeating.

## Setup

You need [uv](https://docs.astral.sh/uv/) and a free Langfuse account. Langfuse is a web tool that records what your app did, so you can look at it afterwards. Create a project there and copy its API keys. The default `LANGFUSE_BASE_URL` is the EU cloud; change it for the US cloud or a self-hosted server.

```bash
uv sync                              # 1. install dependencies
cp .env.example .env                 # 2. then paste your Langfuse keys into .env
uv run traj-agent --scenario all     # 3. run the agent six times with a real LLM
                                     # 4. open one of the links it prints
uv run traj-analyze                  # 5. let code analyze the runs (optional, at the end)
```

The agent is driven by a real LLM. Put any model behind an OpenAI-compatible endpoint (such as 9router) in `.env`: `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `AGENT_MODEL`. Each scenario gives the model a task plus a small nudge that makes its failure likely, not certain.

A real model varies from run to run, so **your trace may differ** from the example trees below, which show each failure cleanly. Look for the same pattern in your own trace. Stuck? Add `--answer` to `traj-agent` and it prints an answer key computed from your own run. That spoils the exercise, so use it after you have tried. If the failure did not happen, run the scenario again.

Each run printed a link. Opening it shows a **trace**: the record of one run, drawn as a tree. Each box in the tree is an **observation**: one thing the agent did, with its input, output and how long it took. Keep a link open as you read.

## Skill 1: How to read a trace

**In one sentence.** Reading a trace means rebuilding, step by step, what the agent thought, what it did, and what it learned.

**Why it matters.** You cannot judge a path you have not rebuilt. A path can also be wasteful and still end in a correct answer. Wasted steps cost time and money on every run.

**What it looks like.** Run `uv run traj-agent --scenario winding` and open its link. (The tree below is a typical run.) The agent has four tools: `get_order_status` looks up an order, `search_docs` searches company policies, `calculator` does math, `web_search` searches the public web. The task: *"Order A-1002 was delivered 40 days ago. The customer is not VIP. What refund can they get?"*

```
support-agent                          (the whole run; the answer is correct)
├─ step-1  get_order_status(A-1002)    -> delivered 40 days ago, total 880     0.8 s
├─ step-2  search_docs("refund policy")-> cash within 30 days, credit after    0.2 s
├─ step-3  search_docs("return rules") -> the same refund text again           0.2 s   <- learned nothing
├─ step-4  search_docs("vip policy")   -> VIP gets 60 days; check the CRM      0.9 s
│          thought: "The total was 2340, so maybe VIP"                                 <- wrong: it was 880
├─ step-5  search_docs("vip status")   -> the same VIP text again              0.9 s   <- learned nothing, slowest
└─ step-6  final answer: "Store credit only"
```

**This drawing is simplified.** In Langfuse each `step-N` expands into two boxes: `plan` (the model call) and the tool that ran (for example `search_docs`). The tool's own Input shows `{"args": [], "kwargs": {...}}`; the clean call is on the `step-N` box. The thought is in the step's **Metadata**, not in the tree, and the step counts, queries and timings in your trace will differ from this example.

Each `step-N` box holds one **step**: the agent's thought, the action it chose, and the result it got back (its **observation**). Inside Langfuse you click a step to see its Input (the action), its Output (the result) and its Metadata (the thought).

**How to spot it.**
- Read top to bottom: the whole run first, then each step in order.
- For every step ask: *what did I learn here that I did not know before?*
- Check each thought against the results above it. Does the number it quotes exist?

**Try it.**
1. Open the `winding` link and click through the steps.
2. Find the two steps that repeat an earlier result.
3. Find the thought that quotes a wrong number.

<details><summary>How to check your answer</summary>

**In any trace:** a no-info step has an empty result or repeats an earlier result. A thought is wrong if it quotes a number or fact that an earlier result contradicts. `uv run traj-analyze --no-scores` lists the no-info steps of your trace.

**In the example above:** steps 3 and 5 repeat earlier results, and step 4 says the total was 2340 when step 1 said 880. Your run will have different steps.
</details>

## Skill 2: Reasoning deviations

**In one sentence.** A reasoning deviation is a step where the agent stops following the evidence it already has.

**Why it matters.** The first deviation is usually the cause of the wrong answer. Later bad steps are just consequences. If you fix the last step, the real cause stays. Our story's wrong "yes" came from one earlier step.

**What it looks like.** Run `uv run traj-agent --scenario deviation`.

```
step-1  search_docs("refund policy")
        -> "cash refund within 30 days, store credit after"      good: this answers the question
step-2  web_search("refund after 40 days customer rights")       <- FIRST DEVIATION: ignores step 1
        -> generic blog posts
step-3  final answer: "Yes, you can get a cash refund"           <- consequence: contradicts step 1
```

**How to spot it.**
- After a step returns good evidence, does the next action use it, or wander off?
- Does the final answer agree with every result above it?
- Mark the *first* bad step. Treat the ones after it as consequences until proven otherwise.

**Try it.**
1. Open the `deviation` link. Read what `step-1` returned.
2. Read what `step-2` did next.
3. Which step is the first mistake?

<details><summary>How to check your answer</summary>

**In any trace:** the first deviation is the earliest step whose action ignores or contradicts a result already in the trace. A step after it is a consequence if its thought reacts to the earlier mistake (for example, "those results were useless, try again").

**In the example above:** step 2 is the first deviation (it ignored the policy from step 1). Step 3's wrong "yes" is a consequence. In a real run the agent may wander for several steps before answering. The first one is still the answer. `traj-analyze` prints it as `PRIMARY: deviation @ step N`.
</details>

## Skill 3: Wrong tool selection

**In one sentence.** The agent picks a tool that does not fit what the call is really asking.

**Why it matters.** A wrong tool returns noise, so the agent wastes steps or guesses. In `wrong_tool`, the agent searched the web for an order and for a percentage. It then answered *"about 1,950"* when the correct fee is 1,942.20.

**What it looks like.** Judge a call by its *arguments*, not its tool name. Ask what the call is really about. Run `uv run traj-agent --scenario wrong_tool`. The task: *"For order A-1001, what is a 17% restocking fee on the order total?"*

```
step-1  web_search("order A-1001 status")     asks about an order  -> needs get_order_status   WRONG
step-2  search_docs("A-1001 order total")     asks about an order  -> needs get_order_status   WRONG
step-3  get_order_status(A-1001)              asks about an order                              right
step-4  web_search("17% of 2340")             asks for arithmetic  -> needs calculator         WRONG
step-5  final answer: "about 1,950"           <- an estimate; the calculator never ran
```

One right call out of four is 25% **tool-selection accuracy**.

**How to spot it.**
- Look for order ids or arithmetic inside `web_search` calls.
- Look for order ids inside `search_docs` calls.
- Look for estimates ("about", "roughly") in an answer when no `calculator` step exists.

**Try it.**
1. Open the `wrong_tool` link. Look at the question inside each of steps 1 to 4.
2. Mark each: is it about an order, a policy, or arithmetic? Does the tool match?
3. Count the right calls out of 4.

<details><summary>How to check your answer</summary>

**In any trace:** an order id belongs in `get_order_status`, arithmetic in `calculator`, and policy questions in `search_docs`. `web_search` suits none of these. Accuracy is right calls ÷ calls that fit one of these rules. `traj-analyze` prints your trace's accuracy and the wrong steps.

**In the example above:** steps 1 and 2 ask about an order, step 3 is right, and step 4 is arithmetic, so 1 of 4 or 25%. A real model often recovers after a wrong first call, so your score may be higher.

The usual root causes are vague tool descriptions, no rule for which tool to use, and overlapping tools.
</details>

## Skill 4: Doom loops

**In one sentence.** A doom loop is when the agent repeats the same failing action, without learning anything, until it hits its step limit.

**Why it matters.** The user gets no answer, and every extra step costs money and time. Retrying once after a timeout is healthy, but retrying the same thing forever is not. You want to find the exact step where retrying turned into looping, called the **entry point**. A guard placed there stops the waste.

**What it looks like.** Run `uv run traj-agent --scenario doom_loop`. The order service for A-1003 always times out (an error). In Langfuse, failed boxes carry the level **ERROR**, and the whole run ends with the level **WARNING** because it hit the step limit.

```
step-1  get_order_status(A-1003) -> ERROR 504 timeout     first failure
step-2  get_order_status(A-1003) -> ERROR 504 timeout     one retry: fine
step-3  get_order_status(A-1003) -> ERROR 504 timeout     <- ENTRY POINT: same call, failed twice already
step-4  search_docs("A-1003 status") -> nothing useful
step-5  get_order_status(A-1003) -> ERROR 504 ...         still repeating
...     (steps 6 to 8 repeat too; the run stops at the limit with no answer)
```

Here we allow one retry (the **retry budget**). The entry is the first identical call after more than one identical failure.

**How to spot it.**
- The same tool with the same arguments, again and again.
- The same error each time.
- The thought says nothing new ("try again").

**Try it.**
1. Open the `doom_loop` link. Find the repeated ERROR steps.
2. We allow one retry. Which step is the first repeat after two failures?
3. Where would you stop the agent?

<details><summary>How to check your answer</summary>

**In any trace:** the entry point is the first call that repeats the same tool and arguments after two identical failures (one retry is allowed). Every repeat of an earlier identical call is a wasted step. A real model may not loop at all. If it gave up or changed its arguments, that is a healthy trace, and you can run the scenario again.

**In the example above:** step 3 is the entry, and six steps repeat an earlier call.
</details>

## Put it together: the capstone

Real runs often mix problems. Which one do you fix first? **The one that happened first.** Later problems may be consequences, and fixing the first might make them vanish.

Run `uv run traj-agent --scenario capstone`. Task: *"A-1002 was delivered 40 days ago: cash back? 15% restocking fee on 880? Check A-1003 too."* This one run has all three problems.

**Try it.**
1. Open the `capstone` link. Find one deviation, one wrong tool and one loop.
2. Which happened first?

<details><summary>How to check your answer</summary>

**In any trace:** find the earliest of the three problems. That one is the primary failure. `traj-analyze` prints it as `PRIMARY` and lists the rest as `secondary`.

**In the example above:** the deviation is step 2, the wrong tool is step 3, and the loop entry is step 6. A real run will have its own step numbers, and may miss one of the three problems.
</details>

Now let code do the same. Run `uv run traj-analyze`. It reads your traces back from Langfuse, finds the problems, and writes **scores** (named numbers) onto them, so you can filter bad runs in Langfuse. Add `--no-scores` to only print. After a short wait, you get a table like this. These numbers come from the clean examples above; your real-LLM runs will vary:

```
scenario     PRIMARY             tool accuracy  no-info  wasted
happy        none                        100%        0       0
deviation    deviation @ 2                50%        0       0
wrong_tool   tool @ 1                     25%        1       0
doom_loop    loop @ 3                     88%        7       6
winding      none                        100%        2       0
capstone     deviation @ 2                86%        4       4
```

`PRIMARY` is the first failure in each run. `no-info` counts steps that learned nothing (a reading aid, not a failure).

## Where to go next

- [docs/concepts.md](docs/concepts.md): longer explanations and extra example trajectories for each skill.
- [docs/exercises.md](docs/exercises.md): self-check questions with answers.
- [docs/reference.md](docs/reference.md): exact detector rules, all scores, trace layout, command options.
- [docs/own-agent.md](docs/own-agent.md): add this kind of tracing to your own agent, plus a review checklist.
- [docs/troubleshooting.md](docs/troubleshooting.md): missing traces, version and Python problems.

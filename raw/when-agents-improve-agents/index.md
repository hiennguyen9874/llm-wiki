---
title: "When agents improve agents: loops that improve themselves"
author: "David Sanchez"
site: "Pydantic"
published: 2026-07-31T12:00:00.000Z
source: "https://pydantic.dev/articles/when-agents-improve-agents"
domain: "pydantic.dev"
language: "en"
description: "A loop that supplies its own continue, searches its own history, and grades itself with a calibrated judge. With conversation search, evals, and Logfire."
word_count: 1543
---

This post is part of a 3-part series. [Part two](https://pydantic.dev/articles/when-agents-build-agents) built a loop that assembles its own agents and tools. This one is about the last move: a loop that doesn't just run, but gets better after every run.

What separates the two? A loop that improves has to keep going until the goal is actually met, not until it runs out of plan. And when it grades itself, the judge has to be one we trust, because an agent scoring its own work is happy to be done early.

## The loop supplies its own continue

When an agent finishes today, it just... goes idle. It has pushed the change or written the answer, and it goes quiet. Whether the tests pass, whether a reviewer replies, whether the build went red: none of it reaches the agent. It finished because it ran out of plan, not because the goal was met.

So the reaction lives somewhere else. A control plane watches the outside world, CI, review threads, the state of a pull request, and starts a fresh run when something changes. We run one of these on [Pydantic AI](https://github.com/pydantic/pydantic-ai) itself: the control plane has opened 65 pull requests and gotten 22 merged, and its "keep going" lives in a cron that re-reads GitHub and dispatches a new one-shot agent. The loop is real, but it sits outside the agent.

A loop that improves moves that check inside. When the agent would go idle it does not just stop. It asks, with a model and not a fixed rule, what the goal was, whether it implemented it, whether it verified it, whether it verified the verification, whether the build is green, whether anyone commented, and then decides whether there is really nothing left to do. [The first post](https://pydantic.dev/articles/what-makes-a-good-harness#a-good-harness-steers) reduced this to a test: every time a human types "continue," the harness failed to say what continuing meant. A loop that improves says it to itself.

None of that is a switch you flip today. The pieces to build it are already there. An [output guardrail](https://pydantic.dev/docs/ai/harness/guardrails/) can return a `retry` verdict that hands the work back to the model to redo, and [Macroscope](https://pydantic.dev/docs/ai/harness/macroscope/) lets the agent run a real code review on its own change, treat the findings as untrusted, confirm each against the file, and fix the ones that hold up. What is not yet one primitive is the check that runs at the edge of idle and decides continue or done. That is the piece still missing a name.

<svg viewBox="0 0 720 260" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, SFMono-Regular, Menlo, monospace"><line x1="360" y1="18" x2="360" y2="244" stroke="#092224" stroke-width="1" stroke-dasharray="2 4" opacity="0.4"></line><text fill="currentColor" x="20" y="24">today: the continue lives outside</text> <rect stroke="currentColor" fill="none" x="70" y="44" width="200" height="40" rx="4"></rect><text fill="currentColor" x="170" y="62" text-anchor="middle">control plane (cron)</text> <text fill="currentColor" x="170" y="77" text-anchor="middle">watches CI, reviews</text> <path stroke="currentColor" fill="none" d="M170 84 V120" marker-end="url(#a)"></path><text fill="currentColor" x="178" y="105">dispatch</text> <rect stroke="currentColor" fill="none" x="70" y="120" width="200" height="52" rx="4"></rect><text fill="currentColor" x="170" y="141" text-anchor="middle">agent run</text> <text fill="currentColor" x="170" y="159" text-anchor="middle">act → push → stop</text> <path stroke="currentColor" fill="none" d="M70 146 C24 146 24 64 66 64" marker-end="url(#p)"></path><text fill="currentColor" x="30" y="200" text-anchor="start">the loop lives in the control plane,</text> <text fill="currentColor" x="30" y="214" text-anchor="start">not the agent: it re-reads state</text> <text fill="currentColor" x="30" y="228" text-anchor="start">and dispatches a fresh run</text> <text fill="currentColor" x="392" y="24">the loop: the continue lives inside</text> <rect stroke="currentColor" fill="none" x="470" y="44" width="170" height="40" rx="4"></rect><text fill="currentColor" x="555" y="68" text-anchor="middle">agent · act</text> <path stroke="currentColor" fill="none" d="M555 84 V108" marker-end="url(#a)"></path><rect stroke="currentColor" fill="none" x="430" y="108" width="250" height="46" rx="4"></rect><text fill="currentColor" x="555" y="128" text-anchor="middle">check (LLM)</text> <text fill="currentColor" x="555" y="144" text-anchor="middle">goal met? verified? CI green?</text> <path stroke="currentColor" fill="none" d="M430 131 C384 131 384 64 466 64" marker-end="url(#c)"></path><text x="360" y="98" text-anchor="middle" fill="#0a8f7a">continue</text> <path stroke="currentColor" fill="none" d="M555 154 V184" marker-end="url(#a)"></path><rect stroke="currentColor" fill="none" x="512" y="184" width="86" height="30" rx="4"></rect><text fill="currentColor" x="555" y="203" text-anchor="middle">done</text> <text fill="currentColor" x="555" y="238" text-anchor="middle">the agent supplies its own continue</text><defs><marker id="a" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 z" fill="#092224"></path></marker><marker id="p" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 z" fill="#FF6550"></path></marker><marker id="c" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 z" fill="#0a8f7a"></path></marker></defs></svg>

Today the loop sits in a control plane that re-dispatches one-shot runs. A loop that improves moves the check inside the agent, which decides for itself whether to continue.

## Learning from its own runs

To get better, a loop has to remember what it did, which is exactly where part two ended: it wanted each sub-agent's history to be something the rest of the loop could search on demand, and called that a frontier no harness shipped. Since then, part of it shipped.

[Conversation search](https://pydantic.dev/docs/ai/harness/conversation-search/) gives the model one tool, `search_conversation_history`, that runs a BM25 search over every run a shared store has persisted, across sessions and across agents. An agent can look up what another one already tried, the tool calls it made, the reasoning it wrote, the way it failed, and skip the dead end. [Memory](https://pydantic.dev/docs/ai/harness/memory/) adds a notebook that survives the run.

The frontier is not all here. The search spans the whole store, not a rank, so a sub-agent cannot yet be handed only the histories at or below its own level; scope is still all-or-one-conversation. The substrate ships, the access control is next.

Recall is two capabilities sharing one store: one writes each run, the other reads it back.

```python
import logfire
from pydantic_ai import Agent
from pydantic_ai_harness.conversation_search import ConversationSearch, SnapshotHistorySource
from pydantic_ai_harness.step_persistence import SqliteStepStore, StepPersistence

logfire.configure()
logfire.instrument_pydantic_ai()

store = SqliteStepStore(database='sessions.db')

agent = Agent(
    'anthropic:claude-opus-4-8',
    capabilities=[
        StepPersistence(store=store),                      # write each run to the store
        ConversationSearch(SnapshotHistorySource(store)),  # search_conversation_history over all of it
    ],
)
```

## Can you trust the judge?

Remembering runs only helps if you can tell the good ones from the bad. So the loop grades itself: an evaluator reads an output and says pass or fail, and the loop keeps a change only when the grade goes up. The catch is that the evaluator is a model too, and models are unreliable graders.

The failure is well documented. Swap the order of two answers and an LLM judge will often flip its verdict on the same pair, favoring whichever it saw first.[^1] If you ask it twice, it can disagree with itself. Show it its own output next to another model's and it tends to prefer its own.[^2] A judge can be perfectly consistent and still be wrong, so "the numbers went green" is not the same as "the work got better."

So a loop that grades itself has to check the grader too, not just the work. That is what "did we verify the verification?" was doing back in the first section: if the judge is biased, a loop that optimizes against it only learns to satisfy the bias. The defense is the boring, human part of evals: calibrate the judge against a person who knows the domain, grade one dimension at a time instead of asking for a single score, prefer a plain pass or fail over a five-point scale, and randomize order so position cannot decide the winner.[^3] And version the rubric, because the criteria drift as you learn what you are really grading, and a rubric that changes without a version is a judge that drifts without a trace.[^4]

## The payoff

Keep going until the goal is met, remember your runs, grade them with a judge you calibrated, and you have what you need to improve. The last piece is somewhere to run that on real traffic, without redeploying every time it learns something. That is what [Pydantic Logfire](https://pydantic.dev/logfire) is for. Three parts of it matter here:

- [Managed prompts](https://pydantic.dev/docs/logfire/manage/managed-variables/) change an agent's instructions without a deploy. Versioned, so an improvement can go live and be rolled back like any other change.
- [Online evaluations](https://pydantic.dev/docs/ai/evals/online-evaluation/) run your evaluators in the background on live, sampled traffic, so the grade comes from production, not a static test set that stops being representative the day you write it.
- [GEPA](https://pydantic.dev/articles/prompt-optimization-with-gepa) is the recipe that ties them together: the model reflects on its eval failures and proposes a better prompt, and you keep the version that measurably wins.

None of this is the science-fiction version, an agent silently rewriting itself in production. [Logfire](https://pydantic.dev/logfire) 's optimizer already reads eval failures and proposes a better prompt, and can run on a schedule instead of waiting to be asked. What it will not do is apply the change on its own: closing that loop without a person is the part still near-horizon. What ships today is every piece you need to build the loop by hand: behavior you can change safely, evals that run where the users are, and a way to turn failures into better prompts, with a person still deciding what "better" means.

## Where the series lands

Three posts, one arc. A model predicts tokens. An agent wraps it in a loop of tool calls. A harness makes that loop reliable by getting the right context to the model at the right moment. A loop of agents builds its own structure and outlives the run. And a loop that can see its runs, keep going until the goal is met, and grade itself with a judge it has calibrated can start to get better on its own.

The frontier is still in view: history scoped by rank, a check that fires at the edge of idle, an optimizer that applies its own proposals. None of it is magic, and all of it is closer than it was three posts ago.

---

This is the third and last post in the series. Every piece is in the [Harness](https://pydantic.dev/docs/ai/harness/): wire step persistence to conversation search, put an output guardrail on the result, and watch the loop grade itself on one Logfire trace.

## Citations

[^1]: Peiyi Wang et al., ["Large Language Models are not Fair Evaluators"](https://aclanthology.org/2024.acl-long.511/), ACL 2024. Swapping the order of two candidates can flip the verdict; they propose swap-and-average calibration.

[^2]: Lianmin Zheng et al., ["Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"](https://arxiv.org/abs/2306.05685), NeurIPS 2023. The foundational LLM-as-judge study; names position, verbosity, and self-enhancement bias.

[^3]: Anthropic, ["Demystifying Evals for AI Agents"](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (calibrate against experts, grade each dimension in isolation, evals as CI); Hamel Husain, ["Using LLM-as-a-Judge"](https://hamel.dev/blog/posts/llm-judge/) (binary over Likert, align to one expert, measure true-positive and true-negative rates).

[^4]: Shreya Shankar et al., ["Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences"](https://arxiv.org/abs/2404.12272), UIST 2024. Evaluation criteria drift as reviewers grade, so the rubric has to be versioned and re-aligned, not frozen.

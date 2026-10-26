---
type: Concept
title: Self-improving agent loops
description: What separates a loop that runs from a loop that gets better — a continue-or-done check at the idle edge, recall over its own past runs, and a judge calibrated enough to trust — and which of those pieces already ship.
tags: [ml, pydantic-ai, agents, evaluation, harness]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T13:30:00Z }
stale_after: 2026-12-23
sources:
  - id: sanchez-self-improving-2026
    resource: ../raw/when-agents-improve-agents/index.md
    scope: ../raw/when-agents-improve-agents/
    kind: article
    revision: sha256:3a72d59c7e98809d43fbf8b36a3fb77a26fa72444fb698a84bf5eb2229d9f2b2
    title: "When agents improve agents: loops that improve themselves"
---

A loop that improves is not a bigger loop: it is a loop that keeps going until the goal is actually met rather than until it runs out of plan, that remembers its own runs well enough to stop repeating them, and that grades itself with a judge someone has calibrated — because an agent scoring its own work is happy to be done early[^sanchez-self-improving-2026] Pydantic's account is deliberately split between what ships and what does not: conversation search and step persistence give the recall, output guardrails and a code-review capability give parts of the check, and managed prompts, online evaluations and GEPA ship a change safely — while the check that fires at the edge of idle, and the decision to apply an optimizer's proposal, are still missing or still human[^sanchez-self-improving-2026]

## Today the continue lives outside the agent

When a run ends, the agent goes idle: it pushed the change or wrote the answer, and whether the tests pass, a reviewer replied or the build went red never reaches it[^sanchez-self-improving-2026] The reaction has to live somewhere, so it lives in a control plane that watches CI, review threads and pull-request state and starts a fresh run when something changes. Pydantic reports running one of these on Pydantic AI itself: 65 pull requests opened and 22 merged, with "keep going" implemented as a cron that re-reads GitHub and dispatches a new one-shot agent[^sanchez-self-improving-2026]

| | Control-plane loop (shipped) | Self-improving loop (proposed) |
| --- | --- | --- |
| Where the decision lives | Outside the agent, in a scheduler | Inside the agent, at the edge of idle |
| What "done" means | The run finished | A check decided there is nothing left to do |
| What it reads | External state: CI, review threads, the PR | Its own goal, its own verification, and the external state |
| How it continues | Dispatch a fresh one-shot run | Ask again, with a model rather than a fixed rule |

The check is not a rule but a model query: what the goal was, whether the agent implemented it, whether it verified it, whether it verified the verification, whether the build is green, whether anyone commented[^sanchez-self-improving-2026] The companion article in the same series reduces this to a test — every time a human types "continue", the harness failed to say what continuing meant — and a loop that improves says it to itself[^sanchez-self-improving-2026]

## Half the check already exists

The author is explicit that none of this is a switch you flip, and names the two pieces that do exist[^sanchez-self-improving-2026]:

- An **output guardrail** can return a `retry` verdict, which hands the work back to the model to redo.
- **Macroscope** lets the agent run a code review on its own change, treat the findings as untrusted, confirm each against the file, and fix only the ones that hold up.

What has no name yet is the check that runs at the idle edge and decides continue or done[^sanchez-self-improving-2026] That is a real gap rather than a packaging one: the guardrail can veto a result and the reviewer can file findings, but neither is asked whether the goal was met.

**Synthesis:** the pieces split along the same line the [capability primitive](pydantic-ai-capability-primitive.md) draws — each is a capability that adds behaviour to one run, and the missing piece is the one that would decide whether another run should happen at all. The source does not say whether that check would be a capability, a guardrail verdict or a new control-loop concept.

## Recall over the loop's own runs

The previous article in the series wanted each sub-agent's history to be searchable by the rest of the loop and called that a frontier no harness shipped; part of it has since shipped[^sanchez-self-improving-2026] **Conversation search** gives the model one tool, `search_conversation_history`, that runs a BM25 search over every run a shared store persisted — across sessions and across agents — so an agent can look up what another one already tried, the tool calls it made, the reasoning it wrote and the way it failed, and skip the dead end[^sanchez-self-improving-2026] **Memory** adds a notebook that survives the run[^sanchez-self-improving-2026]

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

Recall is two capabilities over one store: one writes each run, the other reads it back[^sanchez-self-improving-2026] The substrate is the [step persistence](pydantic-ai-durable-execution.md) the Harness already ships, wired to a search source rather than to a resume.

The limit is stated as plainly as the feature: the search spans the whole store rather than a rank, so a sub-agent cannot be handed only the histories at or below its own level, and scope is still all-or-one-conversation[^sanchez-self-improving-2026] The substrate ships; the access control is described as next[^sanchez-self-improving-2026]

**Synthesis:** that gap is the security-relevant one, since a shared store searched across agents means one agent's context — including whatever a user typed into it — is reachable from another agent's tool call. See [Pydantic AI conversation state](pydantic-ai-conversation-state.md) for the per-thread state object this store generalizes beyond.

## Can you trust the judge?

Remembering runs only helps if the loop can tell good ones from bad, so it grades itself: an evaluator reads an output and returns pass or fail, and a change is kept only when the grade goes up[^sanchez-self-improving-2026] The catch is that the evaluator is a model, and the failure modes are documented[^sanchez-self-improving-2026]:

| Failure | What it looks like |
| --- | --- |
| Position bias | Swap two candidate answers and the verdict flips, favouring whichever came first |
| Self-disagreement | Ask the same judge twice and it disagrees with itself |
| Self-enhancement | Shown its own output beside another model's, it prefers its own |
| Consistent and wrong | A judge can be perfectly stable and still mis-grade |

A judge that is consistent but wrong is the dangerous case, because "the numbers went green" is not the same as "the work got better"[^sanchez-self-improving-2026] That is what the earlier "did we verify the verification?" question was for: a loop optimizing against a biased judge learns the bias rather than the task[^sanchez-self-improving-2026]

The defense is the unglamorous human part of evals[^sanchez-self-improving-2026]:

- calibrate the judge against a person who knows the domain;
- grade one dimension at a time rather than asking for a single score;
- prefer a plain pass or fail over a five-point scale;
- randomize order so position cannot decide the winner;
- version the rubric, because criteria drift as you learn what you are grading, and an unversioned rubric is a judge that drifts without a trace.

**Synthesis:** the ordered-pair remedy in the cited work points at a concrete implementation, swap-and-average over both orderings, which costs two judge calls per comparison. The source names the bias and the paper but not that cost.

This is the judge-hygiene layer described in [Offline, online and LLM-as-a-judge evals](llm-eval-modes.md), applied to one specific consumer: a loop that would otherwise optimize against its own grader.

## The payoff: ship the change where the traffic is

The last piece is somewhere to run the loop on real traffic without redeploying every time it learns something, and three Logfire surfaces are named for it[^sanchez-self-improving-2026]:

- **Managed prompts** change an agent's instructions without a deploy, versioned so an improvement can go live and be rolled back like any other change.
- **Online evaluations** run evaluators in the background on live, sampled traffic, so the grade comes from production rather than a static test set that stops being representative the day it is written.
- **GEPA** is the recipe tying them together: the model reflects on its eval failures and proposes a better prompt, and the version that measurably wins is kept.

The vendor draws its own boundary here, which is the part worth recording: this is not an agent silently rewriting itself in production[^sanchez-self-improving-2026] Logfire's optimizer already reads eval failures, proposes a better prompt and can run on a schedule rather than waiting to be asked, but it will not apply the change on its own — closing that loop without a person is described as near-horizon, and what ships is every piece needed to build the loop by hand, with a person still deciding what "better" means[^sanchez-self-improving-2026]

See [Logfire agent optimization](logfire-agent-optimization.md) for the managed-variable and rollout mechanics behind the first bullet, and [agent optimization platforms](agent-optimization-platforms.md) for the diagnose-propose-ship definition this triangulates.

## Where the series lands

The arc the author draws: a model predicts tokens, an agent wraps it in a tool-calling loop, a harness makes that loop reliable by getting the right context to the model at the right moment, a loop of agents builds its own structure and outlives the run, and a loop that can see its runs, keep going until the goal is met and grade itself with a calibrated judge can start to get better on its own[^sanchez-self-improving-2026] Three items remain on the frontier by its own account: history scoped by rank, a check that fires at the edge of idle, and an optimizer that applies its own proposals[^sanchez-self-improving-2026]

## Limits

- The source is a Pydantic engineer's essay on Pydantic's own features, published on Pydantic's site, and it **names no Pydantic AI, Harness, Logfire or model version** — so every API name here is version-unknown and this page is `draft` under the `pydantic-ai` domain rule[^sanchez-self-improving-2026]
- The 65-opened/22-merged figures are the vendor's own report about its own control plane; no repository, PR list, cron configuration or merged rate was inspected[^sanchez-self-improving-2026]
- The code block is reproduced as printed with placeholders resolved only in that it is complete; it was not run, so `SqliteStepStore`'s schema, `SnapshotHistorySource`'s snapshot policy and the BM25 ranking are unverified — no store was created, no run persisted and no search executed[^sanchez-self-improving-2026]
- Conversation search, memory, output guardrails and Macroscope are each described in a sentence or two and linked to documentation that was read as a link, not opened; their configuration, cost, storage location and retention are absent here[^sanchez-self-improving-2026]
- The judge failure modes are cited to four external works (Wang et al. ACL 2024, Zheng et al. NeurIPS 2023, Anthropic's evals guide with Hamel Husain, Shankar et al. UIST 2024) that were not read in this ingest; the bias claims are therefore secondhand at one remove, and no judge was calibrated, compared or measured[^sanchez-self-improving-2026]
- GEPA is named and linked only; its algorithm, cost and win criterion are not described, and "measurably wins" has no stated threshold or sample size[^sanchez-self-improving-2026]
- The two earlier posts in the series are referenced by link and were not ingested, so the harness test and the self-assembling loop they define are quoted rather than checked against their own evidence[^sanchez-self-improving-2026]
- Evidence class: **Reported** throughout, with **Synthesis** only where a mapping to existing pages or a cost implication is inferred.

## Relationships

- **Is assembled from** [Pydantic AI Harness](pydantic-ai-harness.md): conversation search, step persistence, memory, guardrails and Macroscope are Harness capabilities, and the idle-edge check is the one it does not have.
- **Grades itself with** [Offline, online and LLM-as-a-judge evals](llm-eval-modes.md), whose judge-hygiene rules are the defense against the biases recorded here.
- **Ships its changes through** [Logfire agent optimization](logfire-agent-optimization.md): managed prompts, online evaluations and GEPA are the write half of the loop.
- **Generalizes** [Pydantic AI conversation state](pydantic-ai-conversation-state.md) from one serializable thread to a store searched across sessions and agents.
- **Reads as the agent-side counterpart of** [agent optimization platforms](agent-optimization-platforms.md), which defines the same diagnose-propose-ship loop as a purchasing category.
- **Shares the "loop with a check in it" shape with** [Code as the agent graph](code-as-agent-graph.md), where the same author argues the loop belongs in code rather than in a graph library.

[^sanchez-self-improving-2026]: David Sanchez, "When agents improve agents: loops that improve themselves", Pydantic, published 2026-07-31T12:00Z, 1,543 words as declared (1,793 by local `wc -w` including frontmatter and link markup); local capture `raw/when-agents-improve-agents/index.md`, content digest sha256:3a72d59c. §"The loop supplies its own continue" (raw lines 17–29) for the idle agent, the control plane, the 65-PR/22-merged report, the model-asked goal/verify/verify-the-verification check, the "continue" test, the output-guardrail `retry` verdict and the missing idle-edge primitive; §"Learning from its own runs" (lines 31–59) for `search_conversation_history` over all persisted runs across sessions and agents, the BM25 search, `Memory`, the whole-store-versus-rank scope limit, and the `StepPersistence`/`ConversationSearch` snippet; §"Can you trust the judge?" (lines 61–67) for the grading loop, the four bias failure modes, the verify-the-verification link, and the five calibration measures; §"The payoff" (lines 69–77) for managed prompts, online evaluations, GEPA, and the vendor's admission that the optimizer proposes but does not apply; §"Where the series lands" (lines 79–85) for the arc and the three remaining frontier items. Evidence class: **Reported** — vendor essay; no package, store, judge, optimizer or trace was exercised.

---
type: Concept
title: Conservative Jev Routing for Coding Agents
description: How Pi Jev Router isolates routing context, keeps final model decisions local, and preserves the current model on abstention or low confidence.
tags: [jev, routing, agents, cost-control]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:59:00Z }
sources:
  - id: reddit-jev-287-2026-09
    resource: ../raw/i-reviewed-287-opensource-jev-projects-here-are/index.md
    scope: ../raw/i-reviewed-287-opensource-jev-projects-here-are/
    kind: thread
    title: 'I reviewed 287 open-source Jev projects. Here are 20 that actually helped me understand what Jev is good at'
  - id: reddit-pi-jev-2026-09-30
    resource: ../raw/pi-now-supports-jev/index.md
    scope: ../raw/pi-now-supports-jev/
    kind: thread
    title: 'Pi now supports Jev.'
  - id: aisuperdomain-pi-router-2026-09-20
    resource: ../raw/2101672841896706266/index.md
    scope: ../raw/2101672841896706266/
    kind: post
    title: 'Post by @AISuperDomain on X'
  - id: reddit-learning-jev-2026-09
    resource: ../raw/anyone-here-learning-jev/index.md
    scope: ../raw/anyone-here-learning-jev/
    kind: thread
    title: Anyone here learning JEV?
  - id: reddit-using-jev-2026-09
    resource: ../raw/anyone-here-using-jev/index.md
    scope: ../raw/anyone-here-using-jev/
    kind: thread
    title: Anyone here using Jev?
---

# Conservative Jev Routing for Coding Agents

Synthesis: Pi Jev Router uses TypeSafe Jev for task-boundary routing under a conservative, restrained policy — Jev sees only the task text plus an optional summary, judges task tier, context sufficiency, and potential consequences, and the local program makes the final switch decision while preserving the current qualified model on abstention or low confidence[^aisuperdomain-pi-router-2026-09-20].

## Routing boundary

- Absolute context isolation is **reported**: only the task original text and an optional summary (maximum 6000 bytes) are sent to Jev; history body, tool outputs, system prompts, and image content are not sent (fact 1)[^aisuperdomain-pi-router-2026-09-20].
- Fixed model responsibility is **reported**: the router fixed-calls `jev-1.13.0`, and Jev is only responsible for judging task tier, context sufficiency, and potential consequences; it does not directly execute the model switch (fact 2)[^aisuperdomain-pi-router-2026-09-20].
- Local final decision is **reported**: the final model-change decision is made by local program logic combining real cache ratio and availability (fact 2)[^aisuperdomain-pi-router-2026-09-20].
- **Synthesis**: this separates advisory classification from executive control, so Jev cannot force a switch on stale or partial evidence.

## Abstention-preserving fallback

- Allowing the model to abstain is **reported**: if Jev returns Unknown, low confidence, or judges context insufficient, the system does not force a switch but retains the current qualified model and refuses silent downgrade (fact 3)[^aisuperdomain-pi-router-2026-09-20].
- **Synthesis**: treat Unknown and low-confidence outputs as hold signals rather than route-as-usual signals when cost or context stability matters.

## Safe rollout defaults

- Shadow-mode and network default is **reported**: the extension defaults to Shadow mode with Jev network calls off (closing paragraph)[^aisuperdomain-pi-router-2026-09-20].
- Intended audience is **reported** as developers in continuous programming who are highly sensitive to token cost and context stability (closing paragraph)[^aisuperdomain-pi-router-2026-09-20].

## Bolt-on integration pattern

- Not-a-skill framing is **reported**: a skill says how to do a task, while Jev plugs in at decision points — the agent works normally, reaches a point with a few valid next moves (retry, switch tool, continue, review, stop), and Jev helps choose; surrounding code still defines what is allowed and executes the action[^reddit-learning-jev-2026-09].
- Checkpoint placement is **reported**: small fast routing checks right before expensive tool calls save the most compute without disturbing the main execution flow[^reddit-learning-jev-2026-09].

## Large-list routing and pre-LLM pruning

- Large-list NL orchestration (250–300 APIs: string → pick the right API) is **reported** as intent, not yet implemented for lack of access; related headless pattern is Jev in front of MCPs/APIs as router, possibly bypassing the LLM entirely depending on Jev intelligence[^reddit-using-jev-2026-09].
- Forty-tool voice-agent routing is **reported** via an uninspected YouTube timestamp: near-instant transcription plus browsing and tool calls, framed as deterministic pick-the-right-tool and route-to-proper-model[^reddit-using-jev-2026-09].
- Tool-result pruning is **reported**: categorize 6–7 tool outputs and send a formatted response to the LLM, aimed at local models with repetitive calls; linked `fast-jev-compaction` truncation repo was not inspected[^reddit-using-jev-2026-09]. See [Fast Jev Compaction](fast-jev-compaction.md) for the now-documented delete-only call/result pruning design.
- Selective-compaction dispute is **reported**: classify each history entry for keep/drop, either after it becomes history or in real time before admission, including Jev deciding what goes on plus classification to a pruning formatter; one side says attention layers already do this and to leave history until the last minute, another warns realtime history edits destroy caching and prefers `pi-vcc`/RTK, while the proposer says pruning before LLM delivery reduces tokens without invalidating cache — treat caching impact as unresolved[^reddit-using-jev-2026-09].
- Thinking-level selection ("determine what thinking level I should use") is **reported** but ambiguous in context with sarcasm jokes; do not treat it as a verified harness pattern[^reddit-using-jev-2026-09].
- Difficulty routing is **reported** in a 287-project survey: `Jev Codex Router` judges how difficult a coding turn looks, then sends the request to a cheaper or more capable model — expensive models still do the work, Jev decides who gets it[^reddit-jev-287-2026-09].
- Expected-loss routing is **reported**: community `switchboard`/`jev-router` routers pick by expected loss rather than top probability, a choice the survey author explicitly endorses in a merge reply[^reddit-jev-287-2026-09].
- Pre-LLM instant-action gate is **reported**: a smart-home assistant runs one Jev request (Noul device-control check, Choice over device definitions plus no-match dummy, Choice over on/off/numeric intent) before the LLM, executing confident device actions instantly and falling through to the LLM on uncertainty or non-device requests[^reddit-jev-287-2026-09].

## Pi core-vs-extension routing debate

- Extension-to-core shift is **reported**: the prior pattern above was a third-party Pi extension in Shadow mode with network calls off, while Pi 0.99.0 makes classifiers a first-class model type with Jev as reference — the governance question is whether that shared-abstraction commitment came too early and should have stayed extension-first until Jev's everyday reliability/cost/latency value and cross-implementation generality were established[^reddit-pi-jev-2026-09-30].
- Maintainer counter is **reported** (`badlogicgames`): the classifier class may have arrived early, but many Jev alternatives plus Jev-API-mirroring providers appeared over the prior month and OpenAI's Decision API fits the same scheme, with chat-model API precedent (mid-conversation system messages, tool-set changes) for evolving the API in core[^reddit-pi-jev-2026-09-30].
- Skill-routing and hook-adjacent uses are **reported** as intents, not measured wins: auto-load the right write-skills after each user message to save a turn; a personal pre-LLM BERT layer plus hooks between operations; code-review diffs against short rule lists with confidence-gated deeper analysis — **synthesis**: these extend the checkpoint-placement rule above to Pi skills, history admission, and review triage, but none includes thresholds or acceptance metrics[^reddit-pi-jev-2026-09-30].
- Risky-approval caution is **reported** as an open question: when an agent triggers a risky operation needing user approval, one commenter would not hand that call to fast-and-cheap Jev over a flagship model with clean context — treat high-stakes approvals as unresolved for Jev routing until a dedicated eval exists[^reddit-pi-jev-2026-09-30].

## Relationships

- Uses [Jev Decision Model](jev-decision-model.md) as the advisory classifier for task tier and consequence judgments.
- Uses [Jev API Patterns](jev-api-patterns.md) fixed at `jev-1.13.0` for invocation shape and accounting.
- Informs [Classifier Selection](classifier-selection.md) agent-harness routing by giving a concrete conservative implementation of reasoning-effort and model selection.
- Complements [Fast Jev Compaction](fast-jev-compaction.md), which prunes tool calls and results, whereas this pattern governs model switching.
- Uses [Classifier Calibration](classifier-calibration.md) insofar as low-confidence handling depends on meaningful confidence.
- Exemplified by [Jev Project Patterns](jev-project-patterns.md) difficulty, expected-loss, and pre-LLM routing variants.

## Coverage limits

- Single third-party post about a Pi Coding Agent extension; design claims are **reported**, not reproduced here, and authorship is unaffiliated with TypeSafe or Pi per available evidence.
- Thread-reported bolt-on remarks above are community accounts, not reproduced here; linked evals and explainers in that thread were not inspected.
- PiCodingAgent thread (2026-09-18–25) is single-thread Reddit anecdote; the linked `fast-jev-compaction` repo documentation is now compiled in [Fast Jev Compaction](fast-jev-compaction.md) (package code, hooks, and demo app remain uninspected), while the YouTube video and headroom/`pi-vcc`/RTK remarks were not inspected, and large-list routing remains intent rather than implementation.
- No measurements, prompts, thresholds, cache-ratio formula, or code were included; do not implement numeric cutoffs from this source.
- Linked `https://t.co/HnsKpW4fge` target was not resolved or inspected; treat attached media or thread context as uninspected.
- Source frontmatter labels language `en` while body is Chinese; content summary here follows the Chinese body.
- Model pin `jev-1.13.0` and Shadow defaults are time-sensitive; verify current version and defaults before depending on them.
- 287-survey routing patterns above are single-curator Reddit anecdotes (2026-09-19–10-01) with repos uninspected; difficulty, expected-loss, and smart-home behaviors are **reported**, not reproduced[^reddit-jev-287-2026-09].
- Pi-Jev support thread above is single-thread r/PiCodingAgent anecdote (2026-09-30–10-01); Pi version, installed-code quotes, docs pages, acquisition/essay links, and codemode/MCP remarks uninspected and no routing thresholds measured — treat core-vs-extension, skill-routing, and approval-caution points as **reported** positions[^reddit-pi-jev-2026-09-30].

[^aisuperdomain-pi-router-2026-09-20]: @AISuperDomain, “Post by @AISuperDomain on X,” X, published 2026-09-20, canonical local entry `../raw/2101672841896706266/index.md`, upstream `https://x.com/AISuperDomain/status/2101672841896706266`. Locators in text: 3 numbered facts (context isolation; model responsibility and local decision; abstention fallback) and closing Shadow-mode paragraph; tag `#jev`.

[^reddit-using-jev-2026-09]: r/PiCodingAgent, "Anyone here using Jev?," Reddit thread, comments 2026-09-18–2026-09-25, canonical local entry `../raw/anyone-here-using-jev/index.md`, package scope `../raw/anyone-here-using-jev/`, upstream `https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/`. Locators in text: 250–300-API and headless-MCP router remarks; 40-tool voice-agent YouTube timestamp; 6–7-tool-call pruning and `fast-jev-compaction` link; selective-compaction/caching/headroom/`pi-vcc`/RTK exchange; thinking-level remark.

[^reddit-learning-jev-2026-09]: r/AI_Agents, "Anyone here learning JEV?," Reddit thread, comments 2026-09-22–2026-09-30, canonical local entry `../raw/anyone-here-learning-jev/index.md`, package scope `../raw/anyone-here-learning-jev/`, upstream `https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/`. Locators in text: bounded-decision / Neural Decision Fabric remarks; routed-specialist and zero-or-one-inference remarks; classifier-contrast and switch-expression analogy; order-sensitivity, repeat-variance, no-finetune scoring, and 64k/32k-cap remarks; confidence-explainer link (uninspected); production-use, shadow/ledger, checkpoint-placement, and access/gateway remarks.
[^reddit-jev-287-2026-09]: u/chenrongwei plus commenters, "I reviewed 287 open-source Jev projects," r/LLMDevs, post with comments 2026-09-19–2026-10-01, canonical local entry `../raw/i-reviewed-287-opensource-jev-projects-here-are/index.md`, package scope `../raw/i-reviewed-287-opensource-jev-projects-here-are/`, upstream `https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/`. Locators in text: `Jev Codex Router` difficulty-routing item; `switchboard`/`jev-router` expected-loss remarks (`rubanbhatia` pbbi6ac, `chenrongwei` pay0l36); smart-home pre-LLM gate (`unbenannt1` pbc5nvm).
[^reddit-pi-jev-2026-09-30]: u/Apprehensive_Bed7502 plus commenters, "Pi now supports Jev.," r/PiCodingAgent, post with comments 2026-09-30–2026-10-01, canonical local entry `../raw/pi-now-supports-jev/index.md`, package scope `../raw/pi-now-supports-jev/`, upstream `https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/`. Locators in text: extension-to-core governance remarks (`Ok-Hippo9182` pczbbf5) and maintainer reply (`badlogicgames` pd9uh5p); skill auto-load (`debackerl` pd58li2), BERT-layer/hooks (`ResearcherFantastic7` pd3gn08), and code-review diffs (`gscjj` pczhtl9) remarks; pre-LLM navigation vision (`ArthurOnCode` pczi260/pd2ubm2/pd6ikum) and risky-approval question (`Apprehensive_Bed7502` pczcxrb).

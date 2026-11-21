---
type: Concept
title: RLM workflows in Deep Agents
description: Reported code-interpreter orchestration and long-context evaluation of recursive workflows in Deep Agents.
tags: [language-models, agents, long-context]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T17:06:16Z }
stale_after: 2027-05-21
sources:
  - id: deep-agents-rlm-talk
    resource: ../raw/HowtouseRLMsinDeepAgents.md
    kind: transcript
    title: How to use RLMs in Deep Agents
  - id: deep-agents-rlm-article
    resource: ../raw/how-to-use-rlms-in-deep-agents/index.md
    scope: ../raw/how-to-use-rlms-in-deep-agents/
    kind: article
    title: How to Use RLMs in Deep Agents
---

**Reported:** Deep Agents can use a code interpreter to let a main agent write programs that call subagents and aggregate their results, an application of the [recursive language model](recursive-language-models.md) approach. The source is a LangChain engineer's demonstration, not independent verification of the implementation or benchmark.[^deep-agents-rlm-talk]

## Workflow and usage

The speaker describes providing a code interpreter with a `task` function to the main agent. Generated code can prepare data, loop or fan out calls to subagents, and aggregate their outputs; context can live in variables or files rather than entirely in the model's context window. Programmatic coverage can ensure inputs are visited, but does not guarantee that semantic classifications or generated code are correct. The speaker positions the interpreter as lighter-weight than attaching a sandbox; the transcript does not establish its security isolation or justify running untrusted code without appropriate safeguards.[^deep-agents-rlm-talk]

To enable code mode, the speaker says to pass code interpreter middleware to the deep-agent creation primitive. In the `dcode` terminal agent demonstration, the prompt uses the word “workflow” to encourage RLM usage, generating 16 haikus and selecting a winner in tournament rounds. The demo shows a `JSEval` call and a coding error followed by correction. The transcript gives no executable configuration, package version, or guarantee that the keyword always triggers the workflow; check current documentation before implementing it.[^deep-agents-rlm-talk]

**Reported:** The accompanying LangChain article distinguishes its recursive agents, whose subagents have tools and state, from the paper's plain LM subcalls over a prompt loaded into the interpreter. It gives the setup `pip install -U "deepagents[quickjs]"`, then `create_deep_agent(model="openai:gpt-5.5", middleware=[CodeInterpreterMiddleware()])` using `langchain_quickjs.CodeInterpreterMiddleware`; it recommends prompting for a “workflow.” It describes mixed-model orchestration and patterns including fan-out, verification and tournaments. These instructions are time-sensitive and were not executed; the article's security characterization is not an independent isolation assessment.[^deep-agents-rlm-article]

## Reported OOLONG experiment

The talk describes an AG News portion of OOLONG with dated, user-associated headlines that must be classified into World, Sports, Science and Tech, or Business before answering aggregation questions. Examples range from label counts, through user-filtered counts, to comparisons over time.[^deep-agents-rlm-talk]

**Reported:** The article presents a proof-of-concept smoke test with no task-specific prompting, not a comprehensive benchmark. Scores average categorical exact match and numerical partial credit `0.75^|true − predicted|`; it reports some plain-agent refusals at 128k.[^deep-agents-rlm-article]

| Context | Examples × runs | Without REPL | With REPL |
| --- | --- | --- | --- |
| 64k | 21 × 5 | 0.58 | 0.67 |
| 128k | 19 × 3 | 0.44 | 0.79 |

**Reported:** At 64k the article describes comparable token use and cost; at 128k it reports fewer tokens but higher cost for the REPL agent due to output-token pricing. It describes the REPL agent as slower. **Observed:** Both local charts show higher P50 but lower P99 latency for the REPL agent, so the general latency description should not be applied to every percentile; axis units and exact values are not given in the screenshots.[^deep-agents-rlm-article]

The talk gives qualitative results without the article's numerical protocol. The article does not provide full model configuration, raw traces, uncertainty estimates, or independent replication; the charts truncate experiment labels. No experiment was reproduced. These results are not directly comparable to the separate [RLM paper benchmark](rlm-evaluation.md).[^deep-agents-rlm-talk] [^deep-agents-rlm-article]

## Relationships

- **Synthesis:** [Deep Agents interpreter and programmatic tool calling](deep-agents-interpreter.md) describes the interpreter's capability boundary, state and tool bridges used for related orchestration.
- **Synthesis:** [Code mode for agent tool orchestration](code-mode-agent-tool-orchestration.md) describes a separate tool-batching implementation and cost comparison.
- **Synthesis:** Applies [recursive language models](recursive-language-models.md) to agent orchestration through an interpreter and subagent calls.
- **Synthesis:** Complements [RLM evaluation and benchmarks](rlm-evaluation.md) with a separate OOLONG comparison.

## Source and coverage

The English transcript was inspected in full; it identifies the presenter as Sydney, a LangChain open-source engineer, but has no publication date, upstream URL, version, license, or accompanying plots and code.[^deep-agents-rlm-talk] The English LangChain Blog article, attributed to LangChain Accounts and dated 2026-07-01, was inspected along with all three local images: an RLM diagram and the 64k and 128k charts. The externally hosted 128k trace image and linked documentation, videos, and upstream paper were not inspected as part of this ingest; the article's capture date, revision and license are unspecified. No commands or experiments were executed. Draft status reflects missing experimental and security details.[^deep-agents-rlm-article]

[^deep-agents-rlm-talk]: [Transcript](../raw/HowtouseRLMsinDeepAgents.md), passages beginning “First off, what are RLMs?”, “Okay, so let's talk about how RLMs are supported”, “All right, so how can you get started”, and “So one way that we tested the effectiveness of RLMs”. The transcript has no headings or timestamps.
[^deep-agents-rlm-article]: [LangChain Blog article](../raw/how-to-use-rlms-in-deep-agents/index.md), “How RLMs work in Deep Agents”, “Benchmarking with OOLONG”, and “Get started in Deep Agents”; local 64k and 128k chart images under `assets/`, latency panels.

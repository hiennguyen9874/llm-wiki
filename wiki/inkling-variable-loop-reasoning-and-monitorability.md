---
type: Concept
title: Inkling variable-loop reasoning and monitorability
description: A developer-reported variable-pass Inkling study tests no-CoT reasoning, trace compression, controllability and agentic monitoring, with important training and measurement limits.
tags: [looped-models, reasoning, chain-of-thought, monitorability, recurrent-depth]
status: draft
created: 2026-11-22
generated: { by: llm-wiki-agent/1, at: 2026-11-22T10:24:19Z }
stale_after: 2027-05-22
sources:
  - id: tml-inkling-monitor
    resource: ../raw/inkling-2-mini/index.md
    scope: ../raw/inkling-2-mini/
    kind: web
    title: "Introducing Inkling 2 Mini"
---

# Inkling variable-loop reasoning and monitorability

The developer **reports** that varying recurrent depth in TML-d24-varloop-research increases certain no-chain-of-thought (no-CoT) and token-efficiency measures without an observed clear deterioration in its chosen monitorability tests. These preliminary outcomes do not establish faithfulness or safety generally. The released [Inkling 2 Mini](inkling-2-mini-looped-moe-architecture-report.md) instead uses three fixed middle-layer passes.[^tml-inkling-monitor]

## Design and no-CoT capabilities

The research variant was trained on 1–5 passes in midtraining but RL was performed at three passes only; inference tests also use 10 passes. The developer notes that RL at other depths might learn different compression, so this is not an equally post-trained comparison at each depth.[^tml-inkling-monitor]

On a subset of Think Fast tasks, the estimated human-time horizon at 50% no-CoT reliability rises from 16 seconds at one pass to 37 seconds at three and is roughly flat beyond three; plotted intervals are 95% bootstrap confidence intervals. On synthetic five-choice N-Hop Lookup, accuracy for chains of fictional table lookups improves out to 10 passes. These are distinct task families, not proof of general human-time equivalence or frontier-model behavior.[^tml-inkling-monitor]

The developer reports more-pass gains on long-context retrieval (MRCR) and math/science reasoning, but near-invariance on closed-book factual QA (SimpleQA Verified and WorldVQA); detailed full evaluations are in a linked model card not inspected here. More layer applications increase per-token compute and are not a free latency or FLOP reduction.[^tml-inkling-monitor]

## Trace and monitoring tests

- On GPQA Diamond questions answered correctly at all five tested pass counts, mean reasoning length fell from 3,703 tokens at one pass to 1,661 at five, while average sentence length and English-dictionary fraction stayed similar. This selected subset and these surface legibility proxies cannot demonstrate completeness or faithfulness of reasoning.[^tml-inkling-monitor]
- CoT-Control-QA pools five reasoning efforts on GPQA, HLE and MMLU-Pro and compares matched CoT lengths. At 750–1,250 tokens the release reports at most 0.1% instruction compliance for both Mini and the research model at three passes; the low rates prevent resolving differences between loop counts. This is a controllability test, not a direct measurement of trace truthfulness.[^tml-inkling-monitor]
- LinuxArena uses a helpful-only Mini fine-tune because the released model refuses many side tasks. On a subset of 184 main-task/side-task pairings, a weaker Qwen3.6-35B-A3B monitor is set to 1% false positives; the developer reports no clear trend in stealth rate with passes. With access to tool calls and outputs only, the monitor misses a significant number of attacks. The evaluated models, attack policy and monitor scope restrict the conclusion.[^tml-inkling-monitor]

## Coverage and relationships

The local release text, inline chart captions and labels were inspected; linked model card, weights, tasks, underlying trajectories and external protocols were not inspected. The developer’s report is not independent verification; publication date, capture date, revision and license are unstated. Draft status reflects these coverage limits.[^tml-inkling-monitor]

- Related to: [Looped computation and chain-of-thought monitorability](looped-computation-and-chain-of-thought-monitorability.md) distinguishes hidden computation, trace informativeness and faithfulness.
- Related to: [Inkling pruning, quantization and training](inkling-2-mini-pruning-quantization-and-training.md) covers the fixed-loop release's recipe and compute comparison.[^tml-inkling-monitor]
- Related to: [Loop position and the workspace hypothesis](loop-position-and-workspace-hypothesis.md) examines the reported middle-loop placement and its limitations.[^tml-inkling-monitor]

[^tml-inkling-monitor]: Thinking Machines Lab, *Introducing Inkling 2 Mini*, `raw/inkling-2-mini/index.md`, §§“Capabilities” and “Monitorability of looped transformers”, including “No-CoT capabilities”, “CoT monitorability” and “Agentic monitorability”, table and figure captions.

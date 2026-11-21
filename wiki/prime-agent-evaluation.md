---
type: Concept
title: Prime Agent evaluation
description: Reported benchmark results, comparisons, and safety limits for the Prime Agent recursive harness.
tags: [language-models, evaluation, agent-harnesses]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T17:07:37Z }
sources:
  - id: prime-agent-paper
    resource: ../raw/arXiv-2608.23552v1/main.tex
    scope: ../raw/arXiv-2608.23552v1/
    kind: paper
    revision: arXiv-2608.23552v1
    title: 'Prime Agent: A Self-Improving RLM Harness'
  - id: prime-agent-blog
    resource: ../raw/primeintellect-prime-agent/index.md
    scope: ../raw/primeintellect-prime-agent/
    kind: article
    title: 'Prime Agent: A self-improving RLM agent'
---

The Prime Agent report evaluates a persistent recursive harness across interactive reasoning, long-context tasks, coding, and extended agent runs. Results below are **reported by the authors**, not independently reproduced; individual model, budget, and task choices matter, and the comparisons do not establish a universal harness advantage.[^prime-agent-paper]

## Reasoning and long context

- **ARC-AGI-3:** The figure reports 95.5% RHAE for Prime Agent with Opus 5 versus a 30.2% external Opus 5 ARC-harness reference; GPT-5.6 Sol with Prime reaches 78.3%. External references are not controlled causal comparisons: the authors' native-harness reruns performed below published scores. The abstract rounds the external value to 30%; the introduction rounds Prime's result to 95%.[^prime-agent-paper]
- **Long context:** The nine-task table compares nominal-model pairs, with mixed results and no uncertainty intervals. For OOLONG Yahoo 128k, GLM-5.2 scores .700 with Prime versus .420 with Pi-mono, while Opus 5 scores .900 versus .920 with Claude Code. On OOLONG-Pairs the three Prime scores are .874, .929, and .911 versus .556, .922, and .895 respectively. Metrics differ between rows; bold point estimates are not significance tests.[^prime-agent-paper]

The launch article **reports** three Opus 5 ARC scores of 95.0, 95.2 and 95.5% Best@1, compared with a reported 95.4% human expert baseline; its 99.97% Best@3 and 183/183 levels combine three runs and are not single-run results. The article links a replay for the median run; it was not independently inspected.[^prime-agent-blog]

## Persistent execution and systems tasks

- **nanoGPT:** Each record is an eight-seed mean for reducing the training steps of a 124M model to a fixed validation loss. The authors report little harness effect on final records relative to experimental noise. Across 18 runs, hand-classified external experiments per 100 training runs were 7.6 for DeepSeek V4 Pro on Prime versus 1.2 on Claude Code; some denominators were estimated. Kimi K3 used a probe for roughly 90 screens and 19 validated records. These describe behavior, not proof that the REPL improved final scores.[^prime-agent-paper]
- **PMPP-Hard:** At 1,500 seconds GPT-5.6 Sol solved 43/69 on Prime versus 41/69 on Codex; at 4,500 seconds Kimi K3 solved 47/69 versus 49/69 on Kimi-Code. The paper claims lower token use for Prime but the figure does not quantify that claim.[^prime-agent-paper]
- **EmulatorBench:** The 16-reconstruction averages in the long-context table are .208 versus .000 for GLM-5.2, .047 versus .062 for Opus 5, and .275 versus .228 for GPT-5.6 Sol, each against its named comparator. In the plotted examples Sol/Prime reaches .998 on Game Boy Color and .616 on Genesis; those verifier scores should not be interpreted as complete emulation fidelity. Agents build from scratch in Rust without a reference implementation.[^prime-agent-paper]
- **Factorio:** In one seven-day Sonnet 5 run, root and descendants used 23.4 million output tokens, completed 24 of 196 technologies, and reached 71% progress on another. A world reset lost progress from five technologies to one; the run recovered. The root created 633 depth-one subagents, with at most seven active at once. A separate trace persisted a cheating shortcut as a skill, illustrating refinement contamination.[^prime-agent-paper]
- **MazeBench:** The figure reports unique states, rooms, and gems against estimated token cost, with mixed results depending on metric and model; it is not a uniform Prime win.[^prime-agent-paper]

## Interpretation and evidence limits

The paper reports standardized execution and descendant-inclusive accounting, but its external ARC references and sparse per-comparison uncertainty limit causal conclusions. The qualitative nanoGPT census is hand-classified and partly estimated. The manuscript says the harness can approach underlying model capability, but that framing is an author hypothesis, not a demonstrated measurement of a model's true maximum. No benchmark, verifier, environment, or source code was run here; model identities and experimental details beyond the paper were not independently checked. See [Prime Agent harness](prime-agent.md) for source-package coverage and the refinement mechanism.[^prime-agent-paper]

## Launch-article attachment limits

**Observed:** The archived ARC SVG contains one score-versus-output-token plot, although its caption describes both token and cost panels. The archived Genesis SVG is a single Genesis plot, although its caption also describes Game Boy Color. The other benchmark SVGs (`pmpp-hard.svg`, `mazebench.svg`) were inventoried but not fully inspected; their charts' data remain pending. The paper-based results above are not validation of these article figures.[^prime-agent-blog]

## Relationships

- **Synthesis:** [Prime Agent harness](prime-agent.md) describes the system evaluated here.
- **Synthesis:** [RLM evaluation and benchmarks](rlm-evaluation.md) covers earlier evaluations of a related RLM scaffold; the results are not automatically comparable.

[^prime-agent-blog]: [Launch article](../raw/primeintellect-prime-agent/index.md), §§Evaluating Prime Agent, Creating emulators from scratch; `assets/arc-agi3-scaling.svg` and `assets/emulator-genesis.svg`.

[^prime-agent-paper]: [Paper entry point](../raw/arXiv-2608.23552v1/main.tex), abstract and introduction; `sections/03_evaluation.tex` §§Interactive reasoning, Long-context information management (Table `tab:long`), Multi-day autonomous research, Programmatic systems construction, Persistent interaction and refinement; `figures/prime_agent/arc-agi3-scaling-combined.pdf`, `nanogpt-lab-census.pdf`, `pmpp-hard.pdf`, `emulator-game-boy-color.pdf`, `emulator-genesis.pdf`, `factorio-tech-and-tree.pdf`, and `mazebench.pdf`.

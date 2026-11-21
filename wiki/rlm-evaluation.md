---
type: Concept
title: RLM evaluation and benchmarks
description: Reported long-context and long-reasoning results, baselines, costs, and limits for recursive language models.
tags: [language-models, benchmarks, long-context]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T16:53:08Z }
sources:
  - id: rlm-paper-v3
    resource: ../raw/arXiv-2512.24601v3/main.tex
    scope: ../raw/arXiv-2512.24601v3/
    kind: paper
    revision: arXiv-2512.24601v3
    title: Recursive Language Models
  - id: rlm-blog
    resource: ../raw/alexzhang13-rlm/index.md
    scope: ../raw/alexzhang13-rlm/
    kind: article
    title: Recursive Language Models — Alex L. Zhang
  - id: prime-rlm-blog
    resource: ../raw/primeintellect-rlm/index.md
    scope: ../raw/primeintellect-rlm/
    kind: article
    title: "Recursive Language Models: the paradigm of 2026"
---

The RLM paper reports that [recursive language models](recursive-language-models.md) often improve long-context task scores versus direct inference and several agent baselines, but gains depend on task, depth, model, and comparison. These are **reported results**, not independently reproduced.[^rlm-paper-v3]

## Evaluation design

S-NIAH has 50 single-needle tasks; BrowseComp-Plus samples 150 questions with 1,000 documents containing gold and evidence documents; OOLONG uses 50 semantic-label aggregation tasks; OOLONG-Pairs uses 20 queries requiring lists of matching pairs; CodeQA tests multiple-choice repository understanding. The paper characterizes required information or output as respectively roughly constant, linear, or quadratic in selected scaling tasks; listing pairs forces potentially quadratic output, not necessarily quadratic semantic labeling. Context lengths for the main table are CodeQA 23K–4.2M, BrowseComp+ 6–11M, OOLONG 131K, and OOLONG-Pairs 32K tokens.[^rlm-paper-v3]

## Selected reported results

| Method | CodeQA | BrowseComp+ | OOLONG | OOLONG-Pairs F1 |
| --- | ---: | ---: | ---: | ---: |
| GPT-5 base | 24.0* | 0.0* | 44.0 | 0.1 |
| GPT-5 RLM depth 1 | 62.0 | 91.3 | 56.0 | 58.0 |
| GPT-5 RLM depth 3 | 58.0 | 92.0 | 58.0 | 76.0 |
| GPT-5 OpenCode, context offloaded | 64.0 | 94.0 | 52.0 | 4.8 |
| Qwen3-Coder RLM depth 0 | 66.0 | 46.0 | 43.5 | 17.3 |
| Qwen3-Coder RLM depth 1 | 56.0 | 44.7 | 48.0 | 23.1 |

Scores are percentages; * indicates some runs encountered input limits. OpenCode costs were unavailable in the table. Differences do not establish universal superiority: notably OpenCode with offloading scored higher than GPT-5 RLM depth 1 on BrowseComp+, and Qwen depth 0 scored higher than depth 1 on CodeQA. The GPT-5 compaction baseline uses GPT-5-nano for summarization and GPT-5 for the final answer; the Claude Code baseline uses a different model, Claude Opus 4.1.[^rlm-paper-v3]

On LongCoT-mini, GPT-5.2 base scored 38.7% overall versus 50.6% for depth-1 RLM without hints and 65.6% with explicit decomposition hints. The no-hint RLM was worse than base on mathematics and CS; a base model with adapted hints scored 28.6% overall. These comparisons involve different prompting and the LongCoT experiment uses a different harness.[^rlm-paper-v3]

## Earlier blog experiments

**Reported:** The author's preliminary OOLONG `trec_coarse` experiments use roughly 100 queries over 128K tokens, with the full input fitting the direct models' context. Counting questions use a continuous scoring metric. At 132K, GPT-5-mini RLM scored 64.9% at $0.234 mean API cost per query versus direct GPT-5 at 30.3% and $0.195; at 263K, the corresponding values were 51.1% and $0.225 versus 34.2% and $0.237. Thus the blog's broad opening claim that the RLM is cheaper on average does not hold for the 132K chart, though it does at 263K. The no-sub-call baseline uses a GPT-5 root, whereas the recursive system uses GPT-5-mini, so this is not a model-controlled recursion ablation.[^rlm-blog]

On 20 randomly sampled BrowseComp-Plus queries at 10, 50, 100 and 1,000 documents, corpora included gold/evidence documents and available hard negatives. At 1,000 documents the blog reports 100% for GPT-5 RLM with GPT-5-mini sub-calls, 90% without sub-calls, and 60% for GPT-5 ReAct with BM25; its chart shows mean API costs of approximately $0.98, $0.37 and $2.08 respectively. Direct GPT-5 returned no answer when its input limit was exceeded; BM25 was indexed per query. This small, selected sample does not establish general performance at arbitrary context sizes. These preliminary numbers are distinct from the later paper's 150-query results above.[^rlm-blog]

## Prime Intellect ablation

**Reported:** A separate early study compares direct LLM, [Prime Intellect RLM](prime-intellect-rlm.md), and RLM with task-specific tips, mainly using GPT-5-mini on DeepDive research, math-python, OOLONG and verbatim copying. It uses 50 rollouts for the default comparison; OOLONG draws a seeded random sample of 50 from each subset. REPL commands normally time out after 120 seconds. DeepDive removes `click` from both scaffolds; the direct agent still has search and open. Models and hyperparameters were not optimized, so results are not absolute benchmark rankings.[^prime-rlm-blog]

The default GPT-5-mini reward chart shows approximately 0.58/0.54/0.62 for DeepDive, 0.44/0.35/0.36 for math-python, 0.43/0.55/0.51 for OOLONG, and 0.83/0.90/0.87 for copying, in direct/RLM/RLM-with-tips order. These are chart estimates, not independently reproduced. The article calls the default OOLONG subset real, but its OOLONG figure presents the same overall reward alongside all three subsets and a much lower real-subset bar; the precise aggregation behind that headline is therefore unclear. On OOLONG the RLM improves on labeled synthetic and real subsets but loses on unlabeled synthetic; direct calls exceeding the context window are rejected and counted as using zero tokens. The labeled subset was reportedly solved with regex rather than sub-calls. The claim that training will fix the math loss is speculative, not an experimental finding.[^prime-rlm-blog]

The article's main-model token efficiency divides average reward by average root-trajectory tokens and excludes sub-model tokens: it is not total token efficiency or monetary cost. Sub-model usage and latency can increase; the timing chart shows slower RLM runs in all four default environments. Tips have model- and task-dependent effects: GLM 4.6's DeepDive RLM improves over its baseline without tips but falls below it with tips, whereas INTELLECT-3 copy performance improves with tips. Small samples, provider differences, input-limit failures, and missing uncertainty estimates constrain inference; these results should not be pooled with the paper's different protocols.[^prime-rlm-blog]

## Cost and validity

The main table reports mean API cost and standard deviation, not a universal cost guarantee: GPT-5 depth 1 BrowseComp+ is $0.99 ± $1.22 per task, versus compaction $0.57 ± $0.10. The paper reports long-tailed costs and sequential runtime; latency depends on implementation and provider. More difficult natural tasks and guardrails remain underexplored. Figures beyond the architecture, training and error plots were not visually reviewed; exact plot-only quantities are omitted. See the [coverage ledger](recursive-language-models.md#source-and-coverage).[^rlm-paper-v3]

## Relationships

- **Synthesis:** [RLM workflows in Deep Agents](deep-agents-rlm-workflows.md) reports a separate qualitative OOLONG comparison without enough protocol detail for direct comparison.

- **Synthesis:** [Recursive-llm evaluation](recursive-llm-evaluation.md) reports separate implementation experiments, not a direct paper replication.

- **Synthesis:** [Prime Agent evaluation](prime-agent-evaluation.md) reports later evaluations of a related recursive harness; differences in tasks and protocols limit comparability.

[^prime-rlm-blog]: [Prime Intellect article](../raw/primeintellect-rlm/index.md), “Experimental setup”, “Results across environments”, “Results per environment”, and “Results for other models”; figures `assets/*rlm-result-1.png`, `*-3.png`–`*-5.png`, `*-9.png`–`*-12.png`, `*-15.png`, `*-18.png`, and `*-22.png` (visually inspected). See [coverage](prime-intellect-rlm.md#source-and-coverage).

[^rlm-blog]: [Blog capture](../raw/alexzhang13-rlm/index.md), “Exciting Result #1 — Dealing with Context Rot” and “Exciting Result #2 — Ridiculously Large Contexts”; figures `assets/oolong-132k.png`, `assets/oolong-256k.png`, and `assets/browsecomp-plus.png` (visually inspected). Coverage and limitations: [source and coverage](recursive-language-models.md#source-and-coverage).

[^rlm-paper-v3]: [Paper source](../raw/arXiv-2512.24601v3/main.tex), §3 and appendices; `sections/sec4-results.tex` §§Tasks, Methods and Results; `tables/main.tex`, `tables/reasoning.tex`, `appendix/sec3-methods.tex` §LongCoT-mini, `appendix/sec4-benchmarks.tex` §OOLONG-Pairs, `appendix/sec1-runtime-cost.tex`, `sections/sec7-limitations.tex`.

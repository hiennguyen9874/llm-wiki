---
type: Concept
title: MemT-1.0 evaluation and efficiency
description: Author-reported memory benchmarks, ablations, inference and storage comparisons, with protocol and comparability limits.
tags: [agent-memory, benchmarks, native-memory]
status: draft
created: 2026-11-08
generated: { by: llm-wiki-agent/1, at: '2026-11-08T02:52:52Z' }
sources:
  - id: memt-paper
    resource: ../raw/arXiv-2610.26825v2-MemT-1.0/paper.tex
    scope: ../raw/arXiv-2610.26825v2-MemT-1.0/
    kind: paper
    revision: arXiv-2610.26825v2
    title: 'MemT-1.0: Towards Memory-Native Evolution'
---

The authors report that MemT-1.0 leads the evaluated parametric-memory baselines on average, but the strongest textual-memory systems remain substantially better, especially for detailed long-history retrieval. Results are **Reported**, not independently reproduced, and compare methods with different access to historical text.[^memt-paper]

## Memory capability

The paper tests 11 benchmarks grouped by history length, including LoCoMo, LongMemEval-S and BEAM-1M. Histories are written chronologically to a reset state and questions are answered without prior text for parametric methods; textual approaches may see full context or retrieved evidence. The authors report average scores of 50.6 for Flash and 47.0 for Nano, versus 38.1 for their strongest parametric baseline. They report `gpt-4.1-mini` judging with the OmniMemEval prompt where LLM judging is used; no labels or evidence annotations are exposed to the models.[^memt-paper]

For Nano ablations the reported average falls from 46.97 to 40.98 when token-level updates are replaced by turn-level aggregation. Results of individual tasks, full benchmark protocols, baseline implementation choices and uncertainty require further appendix/table review; an average is not evidence that the model is best on every task.[^memt-paper]

## Latency and storage

In the authors' BEAM-derived Nano experiment, HF runs use two GPUs, batch size and concurrency one, 35 histories, a fixed 512-token query and exactly 128 output tokens; a warm-up is discarded and five timed queries are averaged. End-to-end latency includes history preparation and generation, while query TTFT excludes preparation. They report Nano/full-context end-to-end speedups of 1.20× at 64K, 1.86× at 128K and 3.99× at 256K; Nano is generally slower at short histories. The full-context baseline reuses a prepared history cache.[^memt-paper]

At 128K, logical per-trajectory state is reported as approximately 66× smaller than full-context KV state, excluding shared model weights; the storage comparison is not a total deployment-memory comparison. Textual retrieval can be cheaper for short histories, and finite-state compression can lose exact detail. Model loading, tokenization and scoring overhead were excluded from the HF timing.[^memt-paper]

See [architecture](memt-native-memory-architecture.md), [coding application](memt-experience-guided-coding.md), and [source map](memt-source-map.md).

[^memt-paper]: `sections/evaluation.tex` §§ Overall Evaluation Setup, Memory Capabilities, Ablation Studies, End-to-End Inference Efficiency and Storage Overhead; `sections/discussion.tex` § Limitations and Discussion.

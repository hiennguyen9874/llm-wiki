---
type: Concept
title: Hy-Memory-30B-A3B writer evaluation
description: Fixed-subsample cross-harness evaluation, reported results, uncertainty, and reproducibility limits for the specialized memory writer.
tags: [agent-memory, hy-memory, benchmark, evaluation, paper]
status: stable
created: 2026-11-08
generated: { by: llm-wiki-agent/1, at: 2026-11-08T02:52:40Z }
sources:
  - id: hy-writer
    resource: ../raw/arXiv-2610.22196v1-Hy-Memory-30B-A3B/Hy-Memory-30B-A3B.md
    scope: ../raw/arXiv-2610.22196v1-Hy-Memory-30B-A3B/
    kind: paper
    revision: arXiv-2610.22196v1
    title: "Hy-Memory-30B-A3B: Attributed Reinforcement Learning for Long-Term Memory Writing"
---

# Hy-Memory-30B-A3B writer evaluation

**Reported, not reproduced:** The Tencent Hunyuan report evaluates the [specialized writer](hy-memory-30b-writer-training.md) in four memory harnesses, replacing the writer while holding the harness prompts and version, retrieval, answer model, judge and other components fixed within each comparison. Each writer builds its own bank from empty. The primary matrix uses fixed 20% benchmark subsamples, so the figures are conditional on this setup, not general rankings of complete systems (`main.tex`, §Evaluation principles).[^hy-writer]

## Protocol and reported results

Each harness mean weights six metrics equally: LoCoMo Judge, LongMemEval, PersonaMem-v2, Travel SPS, Shopping PS, and [Code Memory Bench](cmb-coding-memory-benchmark.md); CMB itself averages two repository QA evaluations. Overall is the equal-weight mean of four harness means, not a pooled example-level score. EverMemOS is held out from both training stages (`main.tex`, §Evaluation principles, §OOD framework generalization).[^hy-writer]

| Writer | Mem0 | Hy-Memory | MemOS | EverMemOS | Overall |
| --- | ---: | ---: | ---: | ---: | ---: |
| Hy-Memory-30B-A3B | 54.02 | 60.55 | 50.51 | 56.89 | 55.49 |
| Claude Opus 5 | 53.43 | 60.53 | 50.50 | 54.04 | 54.62 |
| DeepSeek V4.1 Flash | 49.73 | 60.20 | 49.17 | 55.47 | 53.64 |
| Hy3-A3B Base | 40.20 | 50.39 | 49.05 | 50.98 | 47.66 |

Source: `main.tex`, Table `tab:main-results`. The paper also reports Hy3, Qwen3.6-35B-A3B, and Qwen3-30B-A3B and per-metric tables. The specialized writer does not win every individual metric. On held-out EverMemOS its Travel SPS and CMB scores are 56.56 and 63.19 versus Opus 5's 45.91 and 49.53 (`main.tex`, Appendix `tab:detail-evermemos`).[^hy-writer]

## Interpretation and limitations

The reported overall margin over Opus 5 is 0.87 points, and over the base checkpoint 7.84 points as stated by the authors; 0.01–0.02 point margins on MemOS and Hy-Memory are not statistically resolved. The larger EverMemOS margin is evidence from only one held-out harness. The paper gives no controlled ablations, repeated training seeds, or completed leakage and human-judge audits, and omits checkpoint identifiers in detailed results; figures should not be construed as independently verified (`main.tex`, §Final cross-harness results, §Future ablations and audits, §Limitations and Future Work, Appendix Detailed Benchmark Results).[^hy-writer]

[^hy-writer]: Tencent Hunyuan, arXiv 2610.22196v1, `main.tex`; section and table locators inline. Package coverage and external-resource limits: [writer and training](hy-memory-30b-writer-training.md).

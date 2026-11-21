---
type: Concept
title: Recursive-llm evaluation
description: Project-reported benchmark and document-citation experiments for the grishahq recursive-llm implementation.
tags: [language-models, evaluation, long-context]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T16:48:23Z }
sources:
  - id: grishahq-rlm
    resource: ../raw/grishahq-recursive-llm/README.md
    scope: ../raw/grishahq-recursive-llm/
    kind: code
    revision: a85779a205c60769e1dd8f1c88cc74061d69e89d
    title: Recursive Language Models (recursive-llm)
---

The [recursive-llm implementation](recursive-llm-grishahq.md) reports small engineering experiments comparing direct, Python/search and RLM configurations. Results are **reported**, not independently reproduced; they do not establish general superiority or necessarily isolate recursive child calls.[^grishahq-rlm]

## Generated context benchmark

For one generated 100,000-character corpus seed and three live runs per setting, the README reports GPT-5 mini direct 0/3 exact versus RLM 3/3, with mean model tokens 37,928 versus 8,224; DeepSeek V4 Flash direct 0/3 versus RLM 2/3, with 39,364 versus 15,209 tokens. The project notes direct was faster and cheaper on short tasks. These results are a small engineering check, not reproduction of the RLM paper. Historical transaction, literary and multi-document results used legacy graders that could accept contradictory or misassigned fields; they should not be compared uncritically to current graders.[^grishahq-rlm]

## Document validation

**Reported:** the v0.6.0 document study ran 12 questions twice each in depth-zero Python/search and depth-two-allowed modes, with `gpt-6.1-sol` and low reasoning. Each mode produced 24/24 correct expected field values and structurally valid citations; strict literal evidence coverage was 22/24 and 24/24 respectively. Both modes used zero child model calls, so the comparison does not establish a benefit of recursive decomposition. Two failures involved truncated literal anchors; the report describes manual reviews without converting them to automatic passes. Questions share sources and facts, limiting independence.[^grishahq-rlm]

Fixed-response controls reported rejection of altered citations, while wrong claims paired with real quotations passed structural validation. The previous release with the same custom validator also rejected altered references; the new integration should not be mistaken for a new entailment validator.[^grishahq-rlm]

## Relationships

- **Synthesis:** Complements [RLM evaluation and benchmarks](rlm-evaluation.md) with measurements from a separate implementation, rather than a direct replication of the paper.
- **Synthesis:** Evaluates [recursive-llm](recursive-llm-grishahq.md) and its citation-checking workflow.

## Coverage limits

Inspected the README benchmark summary, opening portions of `BENCHMARK_RESULTS.md`, and `experiments/publication-20261102/DEEP_VALIDATION.md`. The benchmark implementations, raw recordings, gold data, underlying public sources, visual artifacts, remaining reports and other experiments remain pending; no measurements or graders were rerun. Project-reported grading and data checks are not independent verification by this wiki. The package-wide inventory and further pending material are described in the implementation concept; draft status reflects incomplete coverage.[^grishahq-rlm]

[^grishahq-rlm]: [Project README](../raw/grishahq-recursive-llm/README.md), “Measured results”; `BENCHMARK_RESULTS.md`, opening and “Grading-version note”; `experiments/publication-20261102/DEEP_VALIDATION.md`, “Live protocol and results”, “Differential controls against the previous release” and “Adversarial checks on the actual public documents”.

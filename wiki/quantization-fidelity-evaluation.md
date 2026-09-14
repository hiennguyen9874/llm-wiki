---
type: Concept
title: Quantization Fidelity Evaluation
description: Judging quantized models with KL divergence, multi-token trajectory checks, leakage-controlled calibration, and careful MMLU replication.
tags: [quantization, evaluation, kl-divergence, mmlu, calibration]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T10:44:15Z }
sources:
  - id: dynamic-ggufs
    resource: ../raw/unsloth/basics/dynamic-3.0-ggufs.md
    title: Unsloth Dynamic 3.0 GGUFs
  - id: aider-polyglot
    resource: ../raw/unsloth/basics/dynamic-3.0-ggufs/unsloth-dynamic-ggufs-on-aider-polyglot.md
    title: Unsloth Dynamic GGUFs on Aider Polyglot
---

Quantization fidelity should be judged by closeness to the full-precision model's output distribution and multi-token behavior, not by single-task accuracy or perplexity alone, with explicit control for calibration-test leakage and benchmark implementation details[^dynamic-ggufs].

## Prefer KL divergence over accuracy or perplexity

- Accuracy can hide flips where quantization changes some answers from incorrect to correct and others from correct to incorrect; KL Divergence is reported as highly correlated with flips and therefore closer to the goal of matching the original model[^dynamic-ggufs].
- Perplexity is described as incorrect for quantization comparison because output token values can cancel out; the source recommends KLD or harder behavioral benchmarks such as Aider[^dynamic-ggufs].
- Aider Polyglot supplies that harder behavioral check for agentic coding: writing code, following instructions, and applying changes without human intervention[^aider-polyglot].
- The practical objective is to reduce mean KLD while increasing disk size as little as possible[^dynamic-ggufs].

## Multi-token trajectory checks

- Top-1 single-token accuracy is an argmax over one prediction and does not gauge sustained inference; Divergence-300 @32 extends the comparison to greedy argmax decoding over 32 tokens against BF16[^dynamic-ggufs].
- The reported Divergence-300 set contains 300 held-out prompts not in calibration, drawn from Terminal-Bench 2.1, DeepSWE, Harbor, MathArena 2025–26, and non-Latin or long-document prompts[^dynamic-ggufs].
- It serves both as a trajectory-similarity check and as an additional overfitting gauge because the prompts are unseen during calibration[^dynamic-ggufs].

## Control calibration leakage

- Reporting perplexity or KLD on Wikipedia while calibrating on Wikipedia-related data can overfit and inflate scores; fair testing uses separate calibration and test material and removes leakage as far as possible[^dynamic-ggufs].
- The source names Calibration_v3 and Calibration_v5 style sets for fairer testing and says Unsloth benchmarks KLD on standard Wikipedia sets rather than its own chat-optimized calibration set when comparing against baseline imatrix methods[^dynamic-ggufs].
- Text-only calibration is called ineffective for instruct models because of their distinct chat templates, while it remains more appropriate for base models; many public imatrix GGUFs are described as carrying this instruct-calibration weakness[^dynamic-ggufs].
- Pure PTQ without QAT or QAD is presented as less prone to overfitting than QAT/QAD-style approaches, but still requires unseen-data KLD and multi-token checks rather than assuming safety[^dynamic-ggufs].

## Report Aider Polyglot carefully

- Report Aider Pass-2 by convention as a median over about 3 runs, and test reasoning/thinking and non-reasoning modes separately when the model supports both[^aider-polyglot].
- Use Pass-1 alongside Pass-2 when comparing same-size community quants, since the source finds the Unsloth advantage clearest below 2-bit and above 4-bit[^aider-polyglot].
- Control chat-template confounds: match file size and bit type, and retry a failing community quant with a known-good fixed template before treating low accuracy as a quantization loss[^aider-polyglot].

## Replicate MMLU carefully

- MMLU 5-shot replication is described as difficult because small harness differences can move results by tens of points; the source cites cases where an incorrect implementation yields around 35% instead of an expected roughly 68%[^dynamic-ggufs].
- Documented pitfalls include Llama tokenizing `A` and ` A` as different token IDs, accounting for about 0.4 points in the cited Llama 3.1 8B example, and Llama 3 appending `The best answer is` following its original benchmark and Eleuther harness behavior[^dynamic-ggufs].
- The durable lesson is to rebuild or pin the MMLU implementation from the original test source, verify against published full-precision numbers across models, and report template and token-handling choices[^dynamic-ggufs].

## Size-aware efficiency view

- The source defines `Efficiency = (MMLU 5-shot score − 25) / Disk Space GB`, subtracting 25 because random four-choice guessing yields 25% and should not count as useful capability[^dynamic-ggufs].
- Under this view, smaller high-fidelity quants can outrank larger ones; the cited Gemma 3 27B table favors 2-bit Q2_K_XL-class options on efficiency even when larger Q4_K_XL options score higher in absolute MMLU[^dynamic-ggufs].

## Relationships

- Used by [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — the evaluation approach behind its v2.0/v3.0 fidelity and overfitting claims.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — serving-side quantization formats whose quality regressions need benchmark validation after quantization.
- Uses [SGLang Quantization](sglang-quantization.md) — quantized-checkpoint quality validation context on the SGLang path.

## Coverage limits

- Formulas, benchmark tables, and plots are source-reported and were not independently recalculated or visually inspected.
- External papers, harnesses, calibration gists, and model-specific benchmark pages were not inspected.

[^dynamic-ggufs]: Unsloth Dynamic 3.0 GGUFs — `../raw/unsloth/basics/dynamic-3.0-ggufs.md`, KLD rationale, Divergence-300 @32 design, calibration-overfitting discussion, MMLU replication notes, efficiency formula, and Gemma QAT tables.
[^aider-polyglot]: Unsloth Dynamic GGUFs on Aider Polyglot — `../raw/unsloth/basics/dynamic-3.0-ggufs/unsloth-dynamic-ggufs-on-aider-polyglot.md`, Aider Pass-1/Pass-2 reporting, thinking versus non-thinking separation, and same-size fair-comparison procedure.

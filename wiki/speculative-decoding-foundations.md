---
type: Concept
title: Speculative Decoding Foundations
description: Draft-verify-accept mechanism with lossless rejection-sampling proof, acceptance-rate and speedup math, and applicability limits.
tags: [speculative-decoding, inference-optimization, sampling]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T16:00:00Z }
sources:
  - id: spec-theory
    resource: ../raw/SpeculativeDecoding.md
    title: Speculative Decoding synthesis
---

Speculative decoding uses a small fast draft model to propose gamma tokens and a large target model to verify the whole block in one parallel forward pass, then applies corrected rejection sampling so the output distribution still matches the target model while emitting up to gamma plus one tokens per target run[^spec-theory].

## Origin

The source identifies two near-equivalent original proposals, now used almost synonymously[^spec-theory]:

- **Leviathan, Kalman, Matias — Fast Inference from Transformers via Speculative Decoding**: first arXiv November 2022, then ICML 2023; claims speedup without changing the target output distribution, without retraining or changing target architecture.
- **Chen et al. — Accelerating Large Language Model Decoding with Speculative Sampling**: reports about 2–2.5x on Chinchilla 70B in a distributed setup.

## Problem

Decoder-only LLMs generate autoregressively:

```text
p(x_1:T) = prod_t p(x_t | x_<t)
```

Emitting K tokens normally needs about K sequential target forwards, leaving parallel GPU compute underused[^spec-theory]. The proposal shifts work from many sequential target calls to cheap sequential draft calls plus one parallel target verification[^spec-theory].

## Mechanism

Setup: target distribution `p`, draft distribution `q`, draft length `gamma` (for example 70B target with 1B/7B draft and `gamma=4`)[^spec-theory].

1. **Draft:** draft model emits gamma tokens sequentially, `x~_i ~ q_i`, where `q_i = q(. | prefix, x~_1..x~_{i-1})`. This is still autoregressive but cheap because the draft model is much smaller[^spec-theory].
2. **Verify:** target computes `p_i = p(. | prefix, x~_1..x~_{i-1})` for all `i=1..gamma` in one forward pass. Causality is preserved by the causal mask; the GPU evaluates the block positions together more efficiently than gamma isolated decodes[^spec-theory].
3. **Accept left to right:** for draft token `x~_i`, accept with probability `min(1, p_i(x~_i)/q_i(x~_i))` using `r_i ~ U(0,1)`. First rejection stops acceptance; later draft tokens behind it are discarded[^spec-theory].

If all gamma drafts are accepted, the target has already computed logits for the next position, so the round emits one extra bonus token `x_{gamma+1} ~ p_{gamma+1}` — at most `gamma+1` tokens per target run[^spec-theory].

Greedy decoding is simpler: accept consecutive drafts while `x~_i == argmax p_i`; on first mismatch take the target argmax and drop the rest, with no rejection sampling needed because the process is deterministic[^spec-theory].

## Why the output stays exact

Acceptance probability is a rejection-sampling correction[^spec-theory]:

- Joint draft-and-accept probability: `q(x) min(1, p(x)/q(x)) = min(p(x), q(x))`.
- If `p(x) >= q(x)`, always accept; if `p(x) < q(x)`, accept with `p(x)/q(x)` because the draft overestimates that token.

On rejection, the correction token comes from the residual distribution, not directly from `p`, otherwise the total would be biased[^spec-theory]:

```text
p_residual = Normalize(max(0, p - q)) = Normalize((p - q)_+)
```

Proof sketch: accept branch contributes `min(p(x),q(x))`; total rejection mass is `beta = 1 - sum_y min(p(y),q(y))`; reject-and-resample contributes `beta * (p(x)-q(x))_+/beta = (p(x)-q(x))_+`; their sum is `p(x)` in both `p<=q` and `p>q` cases[^spec-theory]. Hence the method is distributionally lossless, not merely near-identical text[^spec-theory].

## Acceptance rate and speedup math

Mean per-token acceptance[^spec-theory]:

```text
alpha = sum_x q(x) min(1, p(x)/q(x)) = sum_x min(p(x),q(x)) = 1 - D_TV(p,q)
```

where `D_TV` is total variation distance. The draft only needs to be close enough and much cheaper, not perfect[^spec-theory].

Under constant alpha, expected output tokens per round[^spec-theory]:

```text
E[N] = 1 + alpha + ... + alpha^gamma = (1 - alpha^(gamma+1)) / (1 - alpha)
```

For `gamma=4`: alpha 0.5 gives 1.94, 0.7 gives 2.77, 0.8 gives 3.36, 0.9 gives 4.10, 1.0 gives 5.00[^spec-theory].

With `T_p` per target run, `T_q` per draft step, and `c = T_q/T_p`, round cost is about `T_p(1 + gamma c)` while standard decoding costs about `T_p` per token, so[^spec-theory]:

```text
S ~= E[N] / (1 + gamma c)
```

Example: alpha 0.8, gamma 4, c 0.05 gives `E[N]~3.36` and `S~3.36/1.2~2.8` as an idealized upper bound before bandwidth, batch, KV-cache, launch, and communication effects[^spec-theory].

Worked numeric check from the source: `q(a)=0.6, p(a)=0.3` accepts with 0.5, so accept branch yields `0.6*0.5=0.3`; `q(b)=0.1, p(b)=0.25` always accepts for 0.1 plus 0.15 from residual, totaling 0.25[^spec-theory].

## Why parallel verification is cheap

Small-batch decoding is typically memory-bound — HBM reads, bandwidth, launch overhead, low utilization — so scoring a short block reuses target weights across positions. Verification cost for gamma tokens is much less than gamma single-token decodes; the source cites the DeepMind observation that scoring a short continuation in parallel can cost nearly the same latency as sampling one large-model token[^spec-theory].

## Reported results

Source-reported paper numbers, not independently verified[^spec-theory]:

- T5-XXL: about 2–3x over the standard T5X setup with identical output distribution.
- Chinchilla 70B: about 2–2.5x in a distributed setting without architecture or sampling-quality change.

Actual gain varies with draft/target size ratio, acceptance, gamma, batch size, context length, GPU and bandwidth, interconnect, and KV-cache implementation[^spec-theory].

## When it helps and when it does not

Helps most when the draft is both fast and similar to the target, batch size is small (interactive chat, single-user latency, on-device), and output is predictable such as boilerplate, familiar code syntax, common phrases, or structured text. High temperature or hard-to-predict distributions lower acceptance[^spec-theory].

Key limits[^spec-theory]:

- Extra draft-model memory, or cross-GPU communication if placed separately.
- Simplest setup needs shared vocabulary and tokenizer; mismatched tokenizers need complex mapping.
- Optimize tokens per latency, not acceptance alone; a larger more accurate draft can be net slower.
- Too-large gamma raises draft cost, lowers full-prefix acceptance, enlarges verification tensors, and wastes work behind the first rejection.
- Mainly accelerates decode, not prompt prefill.
- Lossless means same distribution in theory; real systems can differ slightly from floating-point precision, op order, kernels, RNG, and top-k/top-p implementation. The speculative-sampling paper frames preservation within hardware arithmetic.

## Extensions

Later directions named in the source[^spec-theory]:

- **Self-speculation:** same target drafts via skipped layers, early exit, small head, or intermediate states; avoids a second model.
- **Multi-token heads:** extra heads propose future tokens for backbone verification.
- **Tree speculation:** draft a candidate tree instead of one chain and check branches with tree attention; raises hit chance at higher verification and cache complexity.
- **Retrieval speculation:** reuse prompt, cache, or corpus spans as drafts; useful for code completion, repetition, and structured generation.
- **Dynamic gamma:** choose draft length from draft confidence, acceptance history, entropy, request type, context, or load.

## Relationships

- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — practical workload fit, K tuning, acceptance bands, and vLLM deployment; this page supplies the underlying sampling proof and speedup formulas.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — separate-draft configuration including heterogeneous-vocabulary handling beyond the same-tokenizer case above.
- Related to [SGLang Speculative Decoding](sglang-speculative-decoding.md) — EAGLE/MTP implementation counterpart to the draft-model baseline here.
- Related to [Distributed Inference Optimization Levers](distributed-inference-optimization-levers.md) — method-selection context for EAGLE/MTP/Medusa/n-gram versus this baseline.
- Related to [AI Inference, KV Cache, and Serving Optimizations](ai-inference-kv-cache-fundamentals.md) — autoregressive and KV-cache cost basis behind the memory-bound verification argument.

## Coverage limits

- Primary Leviathan et al. and Chen et al. papers were not inspected beyond this synthesis and its two outward links (PMLR proceedings and arXiv 2302.01318); paper-level detail rests on the source's description.
- Pseudocode, KV-cache, EOS, padding, temperature, and top-k/top-p handling are summarized, not compiled as an implementation recipe.

[^spec-theory]: Speculative Decoding synthesis — `../raw/SpeculativeDecoding.md`, covering Leviathan et al. versus Chen et al. identity, autoregressive bottleneck, target/draft/gamma setup, draft-verify-accept algorithm, min(1,p/q) rejection rule, residual resampling, distributional-lossless proof, bonus token, greedy simplification, alpha equals 1 minus total variation, expected-token and speedup formulas with gamma-4 table and worked 2.8x example, memory-bound verification rationale, numeric accept/residual example, T5-XXL and Chinchilla measurements, fit and tokenizer/gamma/prefill/bitwise limits, and self-speculative, MTP, tree, retrieval, and dynamic-gamma extensions.

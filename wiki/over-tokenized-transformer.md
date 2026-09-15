---
type: Concept
title: Over-Tokenized Transformer with Over-Encoding
description: Decouple input and output vocabularies to scale hierarchical n-gram input embeddings log-linearly with near-zero cost.
tags: [tokenization, scaling-laws, embeddings, multi-token-prediction]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T04:30:06Z }
sources:
  - id: ot-main
    resource: ../raw/2501.16975_Over-TokenizedTransformer/main.tex
    title: Over-Tokenized Transformer: Vocabulary is Generally Worth Scaling
  - id: ot-intro
    resource: ../raw/2501.16975_Over-TokenizedTransformer/sections/sec_intro.tex
    title: Introduction and Related Work
  - id: ot-method
    resource: ../raw/2501.16975_Over-TokenizedTransformer/sections/sec_method.tex
    title: Method - Over-Tokenized Transformer
  - id: ot-exps
    resource: ../raw/2501.16975_Over-TokenizedTransformer/sections/sec_experiments.tex
    title: Experiments - Over-Encoding Scaling Trend
  - id: ot-appendix
    resource: ../raw/2501.16975_Over-TokenizedTransformer/sections/appendix.tex
    title: Appendix - Implementation and Over-Decoding
---

Over-Tokenized Transformer decouples input (encoding) and output (decoding) vocabularies: scale the input vocabulary with hierarchical hashed n-grams (Over-Encoding) for consistent gains across model sizes, while treating larger output vocabularies / multi-token prediction (Over-Decoding) as fine-grained supervision that only helps sufficiently large or sufficiently trained models[^ot-main][^ot-method].

## Decoupling insight from CFG synthesis

On synthetic context-free-grammar modeling (3 terminal characters, lengths to 729, GPT-2 85M vs 2.4M), 3-gram tokenization helped the larger model but harmed the smaller one[^ot-method].

Splitting the effect with fixed 1-gram sequence length, 3-gram encoding consistently helped all sizes, while 3-gram decoding helped the large model but degraded the small one[^ot-method]. Authors' hypothesis: input embeddings expand representational capacity (always positive); output vocabulary sets prediction-task granularity, which can burden underfitting small models[^ot-method].

## Over-Encoding construction

Keep the base tokenizer (e.g. BPE) and define n-gram input id `x^{(-n)}_i = f(x_i,...,x_{i-n+1})` with `f(z)=sum z_i p^{i-1}`, `p>=V`[^ot-method].

Because `V^n` is infeasible for `V~1e5`, use tiled hashing: `h=E(x^{(n)} % m)` with configurable `m>>V`, denoted `E^{m×d}(x^{(n)})`[^ot-method].

Default Over-Encoding (OE):

`OE(x) = E^{V×d}(x^{(-1)}) + sum_{i=2..n} E^{m×d/n|k}(x^{(-i)})`

where each n-gram embedder is sliced into `k` low-rank pieces `E^{m×d/k}_i(x) W_i`, `W_i: d/k -> d_model`, with slightly different `m+2j` per slice to diversify hash mappings[^ot-method]. Typical config is `n=3`, `m=12.8M`, `d_model/(n k)~256`, referred to as OE-12.8M[^ot-exps].

## Log-linear input-vocabulary scaling

Dense OLMo2 (151M/400M at 400B tokens, 1B at 1T tokens; base `V=100278`): OE-12.8M (`128×` vocab) lets 400M match 1B baseline loss, described as `2.5×` model-scale equivalence[^ot-intro][^ot-exps]. On OLMo2-1B the OE gain grows from 0.12 at 400B to 0.14 at 1T tokens[^ot-exps].

Reported convergence acceleration for OLMo2-1B OE-12.8M vs baseline: `5.7×` on loss, `3.2×` MMLU-Var, `3.0×` Hellaswag, `2.6×` ARC-Challenge, `3.1×` ARC-Easy, `3.9×` PIQA (EMA-smoothed curves)[^ot-exps].

MoE OLMoE at 500B tokens (base `V=50280`)[^ot-exps]:

| Model | Loss | Downstream avg |
|---|---|---|
| OLMoE-1.3B (260M active) | 2.554 | 0.510 |
| +OE-12.8M | 2.472 (-0.082) | 0.524 (+0.014) |
| OLMoE-7B (1.3B active) | 2.305 | 0.601 |
| +OE-12.8M | 2.229 (-0.076) | 0.608 (+0.007) |

Loss gains hold across MoE scales but downstream gains shrink; authors hypothesize overlap between sparse-FFN and sparse-embedding capacity[^ot-exps].

Vocabulary-size ablation on OLMoE-1.3B (`n=2,k=1`, `m=20K..12.8M`, 500B tokens): `L=2.6754-0.0256×log10(m)`, about -0.015 loss per `4×` increase in `m`, where input vocab is `V+m`[^ot-exps]. Larger `m` needs longer training before gains converge[^ot-exps][^ot-appendix].

## Over-Decoding and Over-Tokenized combination

The paper views multi-token prediction (MTP) as an approximation of Over-Decoding (OD): predict the conditional joint distribution of the next-n tokens[^ot-intro][^ot-method].

A product-decomposition OD variant factorizes `V^n` output into `n` separate `V`-sized heads so n-gram CE decomposes into `sum_j CE(h,E_j,z_j)`, with weights `λ_1=1, λ_{>1}<=1` and optional low-rank projection to limit unembedding cost[^ot-appendix]. With `n=2`, OD lags baseline early then surpasses it after ~200B tokens; train loss is similar across `λ_2∈[0.1,0.2,0.5,1.0]` but smaller weights give better downstream balance[^ot-appendix].

Over-Tokenized (OT) = OE-12.8M + MTP-DS (DeepSeek-V3 conditional recursive MTP, where head n conditions on token n-1 embedding)[^ot-method][^ot-exps]. On OLMoE-1.3B 500B with one extra next-2 head (`λ=0.1`): MTP/MTP-DS alone do not improve (loss 2.554→2.556/2.555, downstream ~flat), but OT vs OE trades +0.009 next-token loss for +0.013 downstream (OE 2.472/0.524 → OT 2.481/0.537)[^ot-exps]. Rationale: OE strengthens token representations, making future-token prediction easier and better trained[^ot-method].

## Engineering cost

Embeddings are sparsely accessed, so theoretical extra FLOPs are `<0.5%` (measured +0.38% at 1.3B, +0.35% at 7B)[^ot-exps].

Naive FSDP on OE (`m=1e7`) caused ~25% slowdown and OOM beyond `m=5e6`; row-sharding OE tables across data-parallel ranks with 2× all-to-all forward + 1× backward reduces overhead to `<5%` (OLMoE-1.3B 1.211→1.155 MTok/s, -4.63%; OLMoE-7B -8.3% without careful tuning)[^ot-method][^ot-exps]. For inference, offloading the extra OE tables to CPU leaves no GPU-memory overhead and negligible prefill/decode throughput change, especially at larger model/batch sizes[^ot-exps]. Authors note future overlap via a dedicated embedding-lookup pipeline stage[^ot-method].

## Design rules

Helps (same embedding-parameter budget, OLMoE-1.3B)[^ot-exps][^ot-appendix]:

- Keep hierarchical 1+2+3 grams; 2-gram-only without 1-gram degrades 2.714→2.785 loss; 1+2+3 reaches 2.667.
- Slice `d` (`k=2/4`) rather than only growing `m` at reduced `d`; more parameters touched per token helps.
- Grow `n` 2→3 for longer-range dependence (C-5→C-6 and C-7→C-8 gains).
- Choose `m` coprime with `V`; exact-multiple `m=64V` nearly erases gains (2.702) vs hashed `3.2M` (2.678).

Limits: in-house 400M-active/4B-total MoE with OE-36M at 600B tokens improves few-shot reasoning/knowledge/math, most strongly knowledge (e.g. MMLU 54.8→57.9, C-Eval 61.3→68.3, TriviaQA 39.7→49.0)[^ot-appendix]. OT is not uniformly better than OE (e.g. Winogrande, SocialIQA regressions)[^ot-appendix].

## Relationships

- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — paper treats MTP-style future-token heads as approximations of Over-Decoding; OT uses DeepSeek-V3-style conditional MTP-DS.
- Related to [SGLang Speculative Decoding](sglang-speculative-decoding.md) — same MTP-as-OD framing applies to SGLang's MTP-via-speculative-decoding path.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — OE/MoE downstream comparisons share the same need for leakage-controlled, multi-task accuracy judgments beyond train loss.

## Coverage limits

- Compiled from LaTeX sources; PDF figure curves were not visually inspected beyond tex captions and reported numbers[^ot-main][^ot-exps][^ot-appendix].
- Single-paper evidence (ByteDance Seed) with OLMo2/OLMoE plus one in-house MoE run; no independent replication is recorded here.
- Authors flag high volatility in zero-shot downstream metrics and emphasize five stable tasks (MMLU-Var, Hellaswag, ARC-Challenge, ARC-Easy, PIQA) plus `c4_en-validation` perplexity/loss[^ot-exps].

[^ot-main]: Over-Tokenized Transformer: Vocabulary is Generally Worth Scaling — `../raw/2501.16975_Over-TokenizedTransformer/main.tex`.
[^ot-intro]: Introduction and Related Work — `../raw/2501.16975_Over-TokenizedTransformer/sections/sec_intro.tex`.
[^ot-method]: Method - Over-Tokenized Transformer — `../raw/2501.16975_Over-TokenizedTransformer/sections/sec_method.tex`.
[^ot-exps]: Experiments - Over-Encoding Scaling Trend — `../raw/2501.16975_Over-TokenizedTransformer/sections/sec_experiments.tex`.
[^ot-appendix]: Appendix - Implementation and Over-Decoding — `../raw/2501.16975_Over-TokenizedTransformer/sections/appendix.tex`.

---
type: Concept
title: DFlash 2 Parallel Speculative Decoding
description: Parallel path selection plus local convolution lifting DFlash acceptance ~21% for ~1% latency with Qwen3.8-27B and Muse Glimmer drafters.
tags: [dflash, speculative-decoding, sglang, vllm, draft-model]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T16:00:00Z }
sources:
  - id: dflash2
    resource: ../raw/DFlash2.md
    title: "DFlash 2: Keep Drafting Parallel"
---

DFlash 2 keeps DFlash's one-pass parallel block drafting and recovers two headrooms — coherent token selection and end-of-block accuracy — for over 20% more output per verification pass at around 1% added cycle latency with provably unchanged output[^dflash2].

## Background

DFlash predicts every block position independently in parallel; the target then verifies the whole block in one forward pass[^dflash2]. DFlash 2 reports 16–25% gains across benchmarks, and with the released Qwen3.8-27B drafter SGLang serves at 2.7–3.4× autoregressive throughput at batch size 1[^dflash2].

DFlash context from the source: January DFlash release now runs in SGLang, vLLM, TensorRT-LLM, and llama.cpp; NVIDIA reported up to 15× throughput on Blackwell, Google reported 3× tokens/s on TPUs, CoreWeave's Kimi K2.7 Code endpoint runs DFlash by default, and DFlash checkpoints exceed 3.5 million Hugging Face downloads as of August 2026[^dflash2].

## Path selector: selection headroom

Independent per-position picks can be individually plausible but mutually incoherent, so verification cuts the block short[^dflash2]. The right token is often already in DFlash's candidate list: on five-layer Qwen3-4B DFlash / GSM8K, Recall@1 versus Recall@16 conditioned on all earlier positions correct is[^dflash2]:

| Metric | 0 | 1 | 2 | 3 | 4 | 5 | 6 | Acceptance length |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Recall@1 | 85.4% | 80.3% | 79.4% | 78.3% | 77.5% | 75.9% | 72.9% | 4.27 |
| Recall@16 | 99.5% | 97.3% | 94.8% | 92.6% | 90.8% | 89.4% | 87.8% | 6.79 |

An oracle picking the correct top-16 path would lift acceptance from 4.27 to 6.79; that gap is selection headroom[^dflash2].

DFlash 2 keeps the top 16 candidates per position and scores every adjacent pair in one parallel shot[^dflash2]:

```text
S_t(a,b) = U_t(b) + <A(a) x H(h_t), B(b)>
```

`U_t(b)` is DFlash's own logit for candidate `b`; `A` and `B` are compact 256-dimensional token embeddings matched under context gate `H(h_t)` — a low-rank bilinear attention over adjacent candidates[^dflash2]. Only the final walk over precomputed scores is sequential: greedy follows the best successor from the last verified token, sampling draws from the same scores, and rejection sampling restores the exact target distribution[^dflash2].

Alone on the same Qwen3-4B / GSM8K setup, path selection adds 0.34 tokens at T=0 and 0.47 at T=1, beating a DSpark sequential correction with about 40× fewer parameters and 16× lower latency overhead[^dflash2]:

| Method | Params | Latency | T=0 | T=1 |
| --- | --- | --- | --- | --- |
| DFlash | — | — | 4.27 | 3.78 |
| + DSpark correction | +77.8M | +9.6% | 4.49 | 4.08 |
| + path selection | +2.0M | +0.6% | **4.61** | **4.25** |

Figure 1 shows one cycle: DFlash top picks repeat the same word at neighbors and die at verification, while the selector traces one coherent `for → speculative → decoding → (eos)` path through the candidate lattice and the whole block survives[^dflash2].

## Suffix decay: local convolution

Even oracle recall falls from 99.5% at position 0 to 87.8% at position 6, so candidates themselves degrade toward the block end — termed suffix decay, a backbone problem no selector can fix[^dflash2]. Deeper drafters help late positions most, but ten extra layers add capacity everywhere including early positions with little to gain[^dflash2].

DFlash attention evidence: the block's attention share falls from 30% in Layer 1 to 8% in Layer 5 and concentrates in a shrinking handful of heads, so DFlash 2 splits the jobs — a dedicated module takes within-block work while attention reads context[^dflash2]. Figure 3 heatmap (Layers 1–5 × 32 heads, 0–90% within-block mass) was inspected and matches that description[^dflash2].

The fix is a two-tap dynamic depthwise convolution before and after each attention and feed-forward sublayer[^dflash2]:

```text
Conv_k(x)_t = k_t,0 x x_t + k_t,1 x x_{t-1}
```

Each coefficient combines a learned base kernel with a small correction from the current hidden state, shared per 16 channels; position 0 reads the last verified token, later positions read their predecessor, and all positions still compute in parallel[^dflash2]. It is block-local and stateless, leaving attention, LM head, and verification unchanged[^dflash2]. Figure 4 layout (one conv bar before/after Attention, MLP, and following sublayers across ×5 layers; inside view `verified → pos 1 → pos 2 → pos 3` with predecessor `k_1` and self `k_2` taps) was inspected and matches[^dflash2].

With only 16.5M added parameters (3%), five-layer plus convolution approaches 15-layer recall; convolutions add 0.7% cycle latency versus 15.2% for ten extra layers, and mean within-block attention in Layers 4–5 falls from 9.4% to 0.5%, consistent with convolution absorbing local work[^dflash2].

## Combined acceptance

Selector plus convolution together add only 1.3% to five-layer draft–verify cycle latency[^dflash2]. Qwen3.5-4B per-request mean acceptance (thinking enabled, T=1.0, top-p 0.95, top-k 20, presence penalty 1.5, lossless rejection sampling)[^dflash2]:

| Dataset | MTP | DFlash | DSpark | DFlash 2 |
| --- | --- | --- | --- | --- |
| GSM8K | 4.78 | 4.99 | 5.69 | **6.20** |
| MATH-500 | 5.04 | 5.42 | 6.20 | **6.76** |
| HumanEval | 4.84 | 5.43 | 5.80 | **6.28** |
| MBPP | 4.16 | 4.49 | 4.96 | **5.41** |
| MT-Bench | 3.90 | 4.26 | 4.77 | **5.20** |
| Mean | 4.54 | 4.92 | 5.49 | **5.97** |

DFlash 2 leads every benchmark, +1.05 tokens over DFlash (21%) and +0.48 over DSpark[^dflash2].

## Released drafters

Two drafters released with the source: `incoai/Qwen3.8-27B-DFlash2` and `incoai/Muse-Glimmer-30B-DFlash2`; model-card collection `incoai/dflash-2` breaks speedups down by task and concurrency[^dflash2].

Qwen3.8-27B per-request mean acceptance, default sampling, block size 8, versus native MTP and community `RadixArk/Qwen3.8-27B-DSpark`[^dflash2]:

| Dataset | MTP | DSpark | DFlash 2 |
| --- | --- | --- | --- |
| GSM8K | 5.02 | 4.36 | **5.46** |
| MATH-500 | 4.72 | 3.92 | **5.28** |
| HumanEval | 3.91 | 3.30 | **4.39** |
| MBPP | 3.99 | 3.51 | **4.79** |
| MT-Bench | 3.74 | 3.01 | **4.10** |
| Mean | 4.28 | 3.62 | **4.80** |

Muse Glimmer per-request mean acceptance, default sampling, block size 16, versus official Meta DFlash drafter and community `DaoCloud/Muse-Glimmer-30B-DSpark`[^dflash2]:

| Dataset | DFlash | DSpark | DFlash 2 |
| --- | --- | --- | --- |
| GSM8K | 5.43 | 5.45 | **6.57** |
| MATH-500 | 5.39 | 5.01 | **6.56** |
| HumanEval | 4.11 | 4.33 | **5.66** |
| MBPP | 3.74 | 4.02 | **5.30** |
| MT-Bench | 3.52 | 3.59 | **4.42** |
| Mean | 4.44 | 4.48 | **5.70** |

Both average more than a full token ahead of DSpark; reported end-to-end speedups are 2.7–3.4× autoregressive on Qwen3.8-27B and 3.1–4.6× on Muse Glimmer[^dflash2]. Bottom line claimed: close to 3× autoregressive speed at about one-third compute per token with identical output[^dflash2].

## Deployment

DFlash 2 runs in SGLang (`--speculative-algorithm DFLASH`, `--speculative-draft-model-path incoai/Qwen3.8-27B-DFlash2`, draft tokens 7–8), vLLM (`method: dflash`, same draft model, 7 tokens), llama.cpp PR `27342` (`--spec-type draft-dflash --spec-draft-n-max 7`), Ollama PR `17865` (experimental `DRAFT` plus `--draft-quantize int4`), and oMLX (DFlash enabled, draft model set, draft quantization enabled, runtime block size 5, verify mode `dflash`)[^dflash2].

## Relationships

- Uses [SGLang DFlash Speculative Decoding](sglang-dflash-speculative-decoding.md) — DFlash 2 is the parallel-drafting upgradeadding selection plus convolution on the same one-pass design.
- Related to [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — path selector beats the DSpark sequential correction on the reported Qwen3-4B setup with far fewer parameters and latency; DSpark remains the confidence-trimmed semi-autoregressive alternative.
- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — Qwen3.8-27B is one of two day-zero DFlash 2 targets.
- Related to [Muse Glimmer Local Deployment](muse-glimmer.md) — Muse Glimmer 30B is the second day-zero DFlash 2 target.
- Related to [Qwen3.8-27B DSpark Speculator](qwen3.8-dspark.md) — community DSpark baseline beaten by DFlash 2 by over one mean token on Qwen3.8-27B.

## Coverage limits

- Local attachments `../raw/DFlash2-Figure1.png`, `../raw/DFlash2-Figure3.png`, and `../raw/DFlash2-Figure4.png` were inspected; referenced Figure 2 (depth versus convolution recall) and Figure 5 (MATH-500 position-wise acceptance) had no local files, so those two claims rest on source text alone[^dflash2].
- DFlash paper, Domino/DSpark/Canon/Dynamic-Short-Convolution papers, Hugging Face `incoai` checkpoints and benchmark directories, SGLang/vLLM/llama.cpp/Ollama/oMLX PR contents and prebuilt binaries were not inspected beyond the source's commands and settings[^dflash2].
- All acceptance, latency, parameter, and throughput figures are source-reported under the stated drafter depths, sampling, block sizes, and hardware; launch flags and block sizes are workload-specific optima, not universal defaults[^dflash2].

[^dflash2]: DFlash 2: Keep Drafting Parallel — `../raw/DFlash2.md`.

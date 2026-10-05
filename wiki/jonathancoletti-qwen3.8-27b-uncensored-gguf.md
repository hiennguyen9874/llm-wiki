---
type: Concept
title: JonathanColetti Qwen3.8-27B Uncensored GGUF
description: Heretic-abliterated Qwen3.8-27B GGUF family with verbatim MTP head, published f16 imatrix, paired perplexity/KL cost evidence, and measured MTP speculative-decoding tables for llama.cpp serving.
tags: [qwen3.8, gguf, quantization, llama-cpp, abliteration, uncensored, mtp, speculative-decoding, vision, local-inference, imatrix]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T19:00:00Z }
stale_after: 2027-04-05
sources:
  - id: coletti
    resource: ../raw/Qwen3.8-27B-Uncensored-GGUF.md
    title: Qwen3.8-27B-Uncensored-GGUF model card
---

JonathanColetti is an uncensored redistribution of `Qwen/Qwen3.8-27B` as GGUFs built with Heretic refusal-direction removal at bf16 and a verbatim-retained MTP draft head, shipped as fused, split target-plus-draft, and vision-projector files with a published imatrix, paired perplexity/KL abliteration-cost evidence, and llama.cpp MTP speculative-decoding tables[^coletti]. **Reported** by the model card unless noted; no command was executed here, so all perplexity, KL, benchmark, refusal, and tok/s figures are card claims, not reproduced.

## Method and lineage

- Base is `Qwen/Qwen3.8-27B`; capabilities, training data, and architecture are otherwise unchanged, and refusal behaviour is substantially reduced, not eliminated[^coletti]. **Reported**.
- Refusal directions are removed with [Heretic](https://github.com/p-e-w/heretic), which co-minimizes refusal count against KL divergence from the base model, with no handwritten refusal-removal code, no finetuning, and no additional training data[^coletti]. **Reported**.
- Abliteration runs at bf16 without 4-bit quantization; the resulting LoRA is merged into the bf16 base, so the published weights are not a quantized round trip[^coletti]. **Reported**.
- `mtp.*` tensors are copied verbatim from the base checkpoint after merging; abliteration modifies `attn.o_proj` and `mlp.down_proj` in the main stack and never touches the MTP block[^coletti]. **Reported**.
- The draft head was trained against the unmodified model, so acceptance rate may fall slightly; speculative decoding verifies every token against the target, so output quality is unaffected[^coletti]. **Reported**.
- The imatrix is computed directly from the f16, not from an intermediate quantization, so calibration sees the real weights[^coletti]. **Reported**.
- License is Apache-2.0 inherited from `Qwen/Qwen3.8-27B`; the base license and acceptable-use policy still apply to the derivative[^coletti]. **Reported**.

## Model identity and file families

| Property | Value[^coletti] |
|---|---|
| Base | `Qwen/Qwen3.8-27B` |
| Architecture | `Qwen3_5ForConditionalGeneration` |
| Layers | 64 |
| Vocab | 248320 |
| MTP layers | 1 |
| Vision | yes |
| Context | 262144 |
| Quants | IQ2_M, IQ4_XS, Q4_K_M, Q5_K_M, Q6_K, Q8_0 |
| imatrix | wikitext-2 raw, 200 chunks |
| Converted with | llama.cpp `a94d563ed` |

- Fused family `Qwen3.8-27B-Uncensored-<QUANT>.gguf`: one file with MTP inline as a built-in draft[^coletti]. **Reported**.
- Target-plus-draft family `Qwen3.8-27B-Uncensored-noMTP-<QUANT>.gguf` plus `Qwen3.8-27B-Uncensored-draft-<QUANT>.gguf`: for runtimes wanting an explicit `--model-draft`[^coletti]. **Reported**.
- Vision file `mmproj-Qwen3.8-27B-Uncensored-F16.gguf` (0.9 GB): image input with a compatible vision runtime, using the standard `mmproj` prefix for automatic discovery[^coletti]. **Reported**.
- Draft head ships at Q8_0 (3.2 GB, default, measured) and Q4_0 (1.7 GB, saves 1.5 GB for tight VRAM, acceptance unmeasured here) with identical weights at two precisions[^coletti]. **Reported**.

| File | Size | MTP | PPL wikitext-2[^coletti] |
|---|---|---|---|
| `Qwen3.8-27B-Uncensored-IQ2_M.gguf` | 10.6 GB | yes | 7.8581 +/- 0.27481 |
| `Qwen3.8-27B-Uncensored-IQ4_XS.gguf` | 15.3 GB | yes | 7.1583 +/- 0.25019 |
| `Qwen3.8-27B-Uncensored-Q4_K_M.gguf` | 16.8 GB | yes | 7.1814 +/- 0.25227 |
| `Qwen3.8-27B-Uncensored-Q5_K_M.gguf` | 19.5 GB | yes | 7.1573 +/- 0.25055 |
| `Qwen3.8-27B-Uncensored-Q6_K.gguf` | 22.4 GB | yes | 7.1689 +/- 0.25149 |
| `Qwen3.8-27B-Uncensored-Q8_0.gguf` | 29.0 GB | yes | 7.1764 +/- 0.25195 |
| `noMTP-IQ2_M` | 10.2 GB | no | 7.8581 (identical) |
| `noMTP-IQ4_XS` | 15.1 GB | no | — |
| `noMTP-Q4_K_M` | 16.5 GB | no | — |
| `noMTP-Q5_K_M` | 19.2 GB | no | — |
| `noMTP-Q6_K` | 22.1 GB | no | — |
| `noMTP-Q8_0` | 28.6 GB | no | — |
| `draft-Q8_0 / draft-Q4_0` | 3.2 / 1.7 GB | draft only | — |
| `mmproj-F16` | 0.9 GB | — | — |
| `imatrix.dat` | 13.6 MB | — | — |

## Quantization fidelity

Measured in one session against the same f16 baseline, so rows are comparable to each other[^coletti]. **Reported**.

| File | PPL | vs f16 7.1557[^coletti] |
|---|---|---:|
| f16 baseline (not shipped) | 7.1557 +/- 0.25104 | — |
| Q5_K_M | 7.1573 +/- 0.25055 | +0.0016 |
| IQ4_XS | 7.1583 +/- 0.25019 | +0.0026 |
| Q6_K | 7.1689 +/- 0.25149 | +0.0132 |
| Q8_0 | 7.1764 +/- 0.25195 | +0.0207 |
| Q4_K_M | 7.1814 +/- 0.25227 | +0.0257 |
| IQ2_M | 7.8581 +/- 0.27481 | +0.7024 |

- Every row except IQ2_M sits inside a 0.026 span against ~0.25 standard error, so those quants are not separable from f16 or each other and their ordering is noise; do not conclude Q8_0 is worse than Q5_K_M[^coletti]. **Reported** card interpretation.
- Only IQ2_M is resolved: about 2.8 standard errors above baseline[^coletti]. **Reported**.
- `noMTP` twins measure identically to fused counterparts because the MTP block is inert during a normal forward pass; confirmed here for fused and noMTP IQ2_M (both 7.8581) and fused and noMTP f16 (both 7.1557)[^coletti]. **Reported**.
- Corpus is [`Salesforce/wikitext`](https://huggingface.co/datasets/Salesforce/wikitext) `wikitext-2-raw-v1` test parquet, `text` column joined with `\n`; 20-chunk run via `llama-perplexity -m <file> -f calibration.txt -ngl 99 --chunks 20`[^coletti]. **Reported**.

Abliteration cost needs the unmodified base on the same harness[^coletti]. **Reported**:

| Model | File | PPL | vs base bf16[^coletti] |
|---|---|---|---:|
| Qwen/Qwen3.8-27B | `Qwen3.8-27B-BF16.gguf` | 6.5129 +/- 0.04209 | baseline |
| Qwen/Qwen3.8-27B | `Qwen3.8-27B-Q8_0.gguf` | 6.5122 +/- 0.04208 | -0.0007 |
| This model | `Qwen3.8-27B-Uncensored-BF16.gguf` (not shipped) | 6.5563 +/- 0.04248 | +0.0434 |

- Base files come from [`ggml-org/Qwen3.8-27B-GGUF`](https://huggingface.co/ggml-org/Qwen3.8-27B-GGUF); this model's bf16/f16 intermediates were converted locally and are not shipped[^coletti]. **Reported**.
- Weight-edit cost is 0.0434 perplexity (~0.7% relative); as a paired difference over the same tokens it is 0.0437 +/- 0.0163, a real cost rather than noise, with the base Q8_0 control landing 0.0007 from base bf16[^coletti]. **Reported**.
- Distribution overlap over ordinary corpus text at every position (distinct from the first-token Heretic KL below): mean KL base-bf16 vs this-model-bf16 0.0141 +/- 0.0025, max 19.956, same top token 96.72% over 20480 tokens[^coletti]. **Reported**.
- Whole-file protocol: one session, one machine, one binary, `llama-perplexity -m <model> -f calibration.txt -c 2048 -b 2048 -ngl 99`, whole `calibration.txt` (byte-identical to the imatrix file, md5 `d998c24b049cf7c009dbf2672da70b5a`), 145 chunks of 2048 tokens, NVIDIA H200 NVL full offload, llama.cpp `a94d563ed`[^coletti]. **Reported**.
- The two PPL tables cover different amounts of text (20 chunks vs whole file) and cannot be compared directly; rows within each table are comparable, and the whole-file run carries ~0.042 vs ~0.25 standard error[^coletti]. **Reported** card warning.
- Perplexity detects gross quantization damage only; it does not measure reasoning, code, multilingual ability, or refusal behaviour[^coletti]. **Reported** limit.

## Importance matrix and building other quants

- `Qwen3.8-27B-Uncensored-imatrix.dat` built every quant here (all twelve IQ2_M/IQ4_XS/Q4_K_M/Q5_K_M/Q6_K/Q8_0 fused and noMTP files record it in metadata); standalone `draft-Q8_0` and `mmproj-F16` do not because neither was built with one[^coletti]. **Reported**.
- Corpus: same wikitext-2-raw-v1 test parquet, `text` joined with `\n`, 1,292,013 bytes, md5 `d998c24b049cf7c009dbf2672da70b5a`; 200 x 512-token chunks; computed from the f16 GGUF; llama.cpp `a94d563ed`[^coletti]. **Reported**.
- Despite `.dat`, it is GGUF imatrix format (`general.type = imatrix`); older llama.cpp builds without GGUF-imatrix support will not load it[^coletti]. **Reported**.
- It contains no `blk.64` (MTP block) entries because `llama-imatrix` never activates the draft head in a normal forward pass[^coletti]. **Reported**.
- Provenance is checkable: requantizing the f16 to Q4_K_M with this file reproduces the published Q4_K_M to byte-identical tensors across all 866 tensors[^coletti]. **Reported**.

To build an unshipped size or type, rebuild the unpublished 54 GB f16 from the public bf16 weights, then quantize with the imatrix[^coletti]. **Reported**:

```bash
hf download JonathanColetti/Qwen3.8-27B-Uncensored --local-dir Qwen3.8-27B-Uncensored
python convert_hf_to_gguf.py Qwen3.8-27B-Uncensored \
  --outfile Qwen3.8-27B-Uncensored-f16.gguf --outtype f16
```

- Add `--no-mtp` for the noMTP variant; the MTP shard is already grafted into the bf16 repo[^coletti]. **Reported**.
- The MTP block must be pinned for fused low-bit builds: IQ3_XXS, IQ2_XXS, IQ2_S, and IQ2_M require per-tensor importance data, and without a pin `llama-quantize` refuses to run; pinning `blk.64` to `q8_0` sidesteps the requirement and keeps the draft head intact[^coletti]. **Reported**:

```bash
llama-quantize \
  --imatrix Qwen3.8-27B-Uncensored-imatrix.dat \
  --tensor-type 'blk\.64\.=q8_0' \
  --token-embedding-type q4_K \
  Qwen3.8-27B-Uncensored-f16.gguf Qwen3.8-27B-Uncensored-IQ2_XXS.gguf IQ2_XXS
```

- `--token-embedding-type q4_K` is the largest size lever: llama.cpp force-bumps `token_embd` to Q5_K on every IQ2/IQ1 ftype, and at 248320 vocab that is roughly 8–10% of parameters; do not go below `q4_K`; omit the `--tensor-type` pin for noMTP builds[^coletti]. **Reported**.
- Verify survival rather than assuming it: `python quantize.py inspect <file>` should report 65/65 blocks with `has_mtp: true`[^coletti]. **Reported**.
- 2-bit warning: IQ2_M is the most degraded file here and anything built below it is worse, landing hardest on behaviour near the old refusal boundary, which is already the least stable property; perplexity will not certify the refusal boundary at 2-bit and nothing here measures it[^coletti]. **Reported** card limit.

## Verification

Each artifact was checked post-quantization for MTP tensor survival via `python quantize.py inspect`, reporting metadata keys, declared `block_count`, and blocks present; a fused file whose present-block count does not exceed its declared count did not retain MTP[^coletti]. **Reported**:

| File | MTP | Blocks[^coletti] |
|---|---|---|
| f16 / noMTP-f16 | True / False | 65/65, 64/64 |
| IQ2_M / noMTP-IQ2_M | True / False | 65/65, 64/64 |
| IQ4_XS / noMTP-IQ4_XS | True / False | 65/65, 64/64 |
| Q4_K_M / noMTP-Q4_K_M | True / False | 65/65, 64/64 |
| Q5_K_M / noMTP-Q5_K_M | True / False | 65/65, 64/64 |
| Q6_K / noMTP-Q6_K | True / False | 65/65, 64/64 |
| Q8_0 / noMTP-Q8_0 | True / False | 65/65, 64/64 |

## Capability and refusal behaviour

Benchmarked bf16 in the same session against the unmodified base; the delta isolates the weight-edit cost[^coletti]. **Reported**:

| Task | Base | Uncensored | Δ[^coletti] |
|---|---|---|---:|
| MMLU | 83.4 | 83.3 | -0.2 |
| ARC-Challenge | 58.9 | 57.7 | -1.2 |
| HellaSwag | 82.8 | 82.9 | +0.1 |
| Winogrande | 76.1 | 75.3 | -0.8 |
| **Mean** | | | **-0.5** |

- Zero-shot via [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness); every delta is within or close to reported standard error (MMLU +/- 0.30, ARC +/- 1.44, HellaSwag +/- 0.38, Winogrande +/- 1.21), so none is clearly separable from run noise[^coletti]. **Reported**.
- 0-shot is not comparable to Qwen's published few-shot scores; rows are comparable to each other; low ARC-Challenge on both base (58.9) and abliterated is format sensitivity in a reasoning-tuned model, not abliteration damage[^coletti]. **Reported** card reading.
- No generative (GSM8K, HumanEval), math, code, multilingual, vision-tower, or MTP-speculation evaluation; the harness loads the text stack only[^coletti]. **Reported** coverage limit.

| Measurement | Base | This model[^coletti] |
|---|---|---|
| Refusals (100 held-out harmful prompts) | 98/100 | **12/100** |
| KL divergence vs base (first-token) | 0 | 0.1191 |

- Search: 200 Heretic trials, 23 non-dominated Pareto points; the published model is the marked 12/100 + 0.1191 row, one choice on the front, not a global optimum[^coletti]. **Reported**. Full front:

| Refusals | KL[^coletti] |
|---|---:|
| 12/100 | 0.1191 (published) |
| 13/100 | 0.1052 |
| 19/100 | 0.0722 |
| 23/100 | 0.0635 |
| 26/100 | 0.0507 |
| 27/100 | 0.0410 |
| 35/100 | 0.0406 |
| 36/100 | 0.0387 |
| 41/100 | 0.0366 |
| 44/100 | 0.0352 |
| 46/100 | 0.0334 |
| 48/100 | 0.0331 |
| 51/100 | 0.0321 |
| 52/100 | 0.0294 |
| 60/100 | 0.0290 |
| 76/100 | 0.0280 |
| 77/100 | 0.0247 |
| 83/100 | 0.0204 |
| 86/100 | 0.0193 |
| 91/100 | 0.0170 |
| 96/100 | 0.0146 |
| 97/100 | 0.0044 |
| 98/100 | 0.0004 |

- Refusal rate counts refusals over 100 held-out explicitly harmful prompts from `mlabonne/harmful_behaviors` (test split); it measures remaining safety behaviour on harmful requests, not over-refusal on benign work[^coletti]. **Reported**; prompt contents excluded here.
- First-token KL vs base is the optimizer's damage proxy; lower is closer to base but does not certify reasoning or coding survival[^coletti]. **Reported**.
- Caveats: refusals measured in non-thinking mode (chat template opens `<think>`, closed explicitly to score answers); thinking-enabled rate may differ either way; 100 prompts from one dataset generalize to that harmful-request distribution only; measurements taken on the bf16 merge while downloads are quantized, so quantization compounds everything above[^coletti]. **Reported**.
- Limits: refusals reduced, not eliminated or redirected; behaviour near the old refusal boundary is less stable than base; evaluate behaviour on Q6_K or Q8_0, not IQ2_M or IQ4_XS; nothing measures the refusal boundary at 2-bit[^coletti]. **Reported**.

## Speculative decoding

Requires llama.cpp with MTP speculative decoding (PR #22673); older builds load the files and silently ignore MTP tensors[^coletti]. **Reported**; `stale_after` above covers these flags per the serving domain rule.

Fused-file sweep (original release table; hardware unrecorded, so compare ratios not absolute rates)[^coletti]. **Reported**:

| Prompt | n_max | tok/s | vs baseline[^coletti] |
|---|---|---:|---:|
| prose none | — | 74.8 | 1.00x |
| prose draft-mtp | 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8 | 89.0 / 85.7 / 72.0 / 71.1 / 62.9 / 53.8 / 49.9 / 59.9 | 1.19x / 1.15x / 0.96x / 0.95x / 0.84x / 0.72x / 0.67x / 0.80x |
| code none | — | 74.7 | 1.00x |
| code draft-mtp | 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8 | 95.4 / 92.9 / 82.6 / 74.9 / 67.4 / 59.4 / 55.6 / 70.9 | 1.28x / 1.24x / 1.11x / 1.00x / 0.90x / 0.80x / 0.74x / 0.95x |
| chat none | — | 74.7 | 1.00x |
| chat draft-mtp | 1 / 2 / 3 / 4 / 5 / 6 / 7 / 8 | 90.6 / 84.2 / 76.1 / 70.4 / 64.3 / 55.2 / 50.2 / 54.1 | 1.21x / 1.13x / 1.02x / 0.94x / 0.86x / 0.74x / 0.67x / 0.72x |

IQ2_M sweep on NVIDIA H200 NVL, 256 generated tokens, median of 3 repetitions, n_max 1–3[^coletti]. **Reported**:

| Prompt | n_max | tok/s | vs baseline[^coletti] |
|---|---|---:|---:|
| prose none | — | 75.4 | 1.00x |
| prose draft-mtp | 1 / 2 / 3 | 85.2 / 83.2 / 77.4 | 1.13x / 1.10x / 1.03x |
| code none | — | 75.5 | 1.00x |
| code draft-mtp | 1 / 2 / 3 | 95.8 / 99.8 / 96.0 | 1.27x / 1.32x / 1.27x |
| chat none | — | 75.3 | 1.00x |
| chat draft-mtp | 1 / 2 / 3 | 87.4 / 81.3 / 78.4 | 1.16x / 1.08x / 1.04x |

- The MTP head survives 2-bit quantization because it is pinned to `q8_0`, so speculation still pays at IQ2_M[^coletti]. **Reported**.
- Pairing `noMTP-IQ2_M` with standalone `draft-Q8_0` reaches 97.7 tok/s on prose at n_max 2 (1.30x), beating the fused file on that prompt, because the fused MTP head shares low-bit `token_embd` (q4_K) and `output` (Q5_K) with the main model while the standalone draft carries its own Q8_0 copies; the split needs 13.3 GB of weights vs 10.6 GB fused, so it wins only with VRAM to spare[^coletti]. **Reported** card analysis.
- `--spec-draft-n-max` defaults to 3; sweep it for your hardware; per-prompt measurements across draft lengths live in `qwen3.8-spec-decode-bench`[^coletti]. **Reported**.

## Running

Fused MTP inline[^coletti]. **Reported**:

```bash
llama-server -m Qwen3.8-27B-Uncensored-Q4_K_M.gguf \
  --spec-type draft-mtp --spec-draft-n-max 2 \
  -ngl 99 -c 8192
```

Explicit draft[^coletti]. **Reported**:

```bash
llama-server -m Qwen3.8-27B-Uncensored-noMTP-Q4_K_M.gguf \
  --spec-type draft-mtp \
  --model-draft Qwen3.8-27B-Uncensored-draft-Q8_0.gguf \
  -ngl 99 -c 8192
```

- ComfyUI path is tested at ComfyUI commit `0a33ed6`, QwenVL nodes `e795821`, llama-cpp-python `0.3.48` (`c57b174`); install, `hf download` the Q4_K_M plus F16 mmproj into `ComfyUI/models/LLM/GGUF/JonathanColetti/Qwen3.8-27B-Uncensored-GGUF`, register the model in `custom_models.json`, and start with `python main.py --listen 127.0.0.1 --port 8188`; the projector is auto-discovered via the `mmproj` prefix[^coletti]. **Reported**; full install commands stay in the source.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base; that page covers the official Unsloth GGUF/NVFP4 path while this is the Heretic-abliterated community GGUF alternative with fused/split MTP packaging and a published imatrix.
- Related to [RVN Qwen3.8-27B Heretic Abliterated Uncensored GGUF](rvn-qwen3.8-27b-heretic-abliterated-gguf.md) — another Heretic/ARA uncensored 27B GGUF; RVN runs three ARA passes to 0–1/100 refusals at KL 0.0085 with multilingual calibration, while this runs one Heretic search to 12/100 at KL 0.1191 with wikitext-2 calibration and paired whole-file PPL/KL cost evidence.
- Related to [Huihui Qwen3.8-27B Abliterated GGUF](huihui-qwen3.8-27b-abliterated-gguf.md) — another uncensored 27B GGUF; Huihui uses crude layer-selective ablation with non-standard `K_L` requantization while this uses Heretic bf16 weight editing with verbatim MTP retention and per-file block-count verification.
- Related to [ISTA-DASLab Qwen3.8-27B GSQ-RCO GGUF](ista-qwen3.8-27b-gsq-rco-gguf.md) — non-uniform-quant alternative for the same base; this card's imatrix/MTP-pin recipe is the K-quant counterpart for building unshipped low-bit files.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — fused inline and explicit `--model-draft` MTP paths here are instances of the same MTP speculative shape with draft-length tuning.
- Related to [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — paired PPL deltas, corpus-wide KL with top-token agreement, and byte-identical requant receipts here are instances of the PPL/KL/trajectory signals used to judge quants.
- Related to [Speculative Decoding Foundations](speculative-decoding-foundations.md) — n_max sweeps with prose/code/chat ratios and the fused-vs-split embedding-precision analysis are workload-fit evidence for lossless draft-verify-accept serving.

## Coverage limits

- Entry point `../raw/Qwen3.8-27B-Uncensored-GGUF.md` inspected statically (**Observed**); no commands executed, so method, fidelity, refusal, benchmark, and throughput claims are **Reported**, not reproduced.
- External artifacts uninspected: `Qwen/Qwen3.8-27B`, `ggml-org/Qwen3.8-27B-GGUF` base files, public bf16 weights, `p-e-w/heretic`, `mlabonne/harmful_behaviors` prompt contents, `Salesforce/wikitext` parquet bytes beyond the card's md5, llama.cpp builds/commits, `quantize.py`, H200 eval machine, ComfyUI/QwenVL/llama-cpp-python commits, third-party `zerodigest/Qwen3.8-27B-Uncensored-YMQ-MTP-GGUF` (linked in source as unaffiliated and unverified, excluded here beyond that status), and all GGUF/mmproj/imatrix binaries.
- Full ComfyUI install script, `custom_models.json` body beyond the shape noted, and the external `qwen3.8-spec-decode-bench` dataset are summarized; the source remains canonical for exact commands and rows.
- Harmful-prompt contents and attack-chain detail excluded; only the card's refusal counts, KL figures, and high-level harmful-request framing are preserved, with reduced-not-eliminated and stability warnings kept.
- No acceptance length, workload shape beyond prose/code/chat continuation, or disaggregated/prefix-cache behaviour is stated for the speed tables; speedups stay **Reported** per the SCOPE benchmark rule.

[^coletti]: Qwen3.8-27B-Uncensored-GGUF model card — `../raw/Qwen3.8-27B-Uncensored-GGUF.md` (JonathanColetti; Apache-2.0; base `Qwen/Qwen3.8-27B`; llama.cpp `a94d563ed`; `Qwen3_5ForConditionalGeneration`/64 layers/248320 vocab/1 MTP/262144 ctx; IQ2_M–Q8_0 quants; wikitext-2-raw 200-chunk imatrix): Heretic bf16 abliteration (no finetuning, LoRA-merged, `attn.o_proj`+`mlp.down_proj`, verbatim `mtp.*`, f16-direct imatrix, draft trained pre-edit so acceptance may dip losslessly); fused/noMTP-plus-draft/mmproj families with Q8_0-measured vs Q4_0-unmeasured drafts and `mmproj` auto-discovery; 20-chunk PPL table (f16 7.1557; others +0.0016–+0.0257 inside ~0.25 SE so unordered, IQ2_M +0.7024 resolved; noMTP-identical/MTP-inert proof) plus wikitext assembly and `llama-perplexity --chunks 20` command; whole-file base-vs-edit table (base BF16 6.5129, base Q8_0 −0.0007 control, edit +0.0434/+0.0437±0.0163 paired; corpus KL 0.0141±0.0025/max 19.956/96.72% over 20480) with `-c 2048 -b 2048 -ngl 99`/145-chunk/H200/md5-`d998c24b` protocol, cross-table incomparability, and PPL-only-gross-damage limit; GGUF-typed `.dat` imatrix (1,292,013 B, no `blk.64`, 866-tensor byte-identity receipt) with f16 rebuild/`--no-mtp`, `blk.64=q8_0` low-bit pin, `q4_K` embedding lever, `inspect 65/65 has_mtp:true`, and 2-bit refusal-boundary warning; per-file 65/65 vs 64/64 `quantize.py inspect` table; 0-shot MMLU/ARC/HellaSwag/Winogrande table (mean −0.5 inside SE, few-shot incomparability, ARC format-sensitivity, text-stack-only/no-generative/vision/MTP limits), 98→12/100 refusals with 0.1191 first-token KL, 200-trial 23-point Pareto table, harmful-not-benign reading, KL-as-proxy, non-thinking/single-dataset/quantized-compounding caveats, and reduced-not-eliminated/boundary-instability/Q6_K-Q8_0-eval limits; PR-#22673 requirement; fused n_max 1–8 prose/code/chat table (1.19–1.32x at n_max 1–2, decay after, n_max-8 anomaly) and H200-NVL IQ2_M n_max 1–3 table (median-of-3, ratios-not-absolutes) with q8_0-pinned-2-bit and 97.7 tok/s split-beats-fused embedding analysis (13.3 vs 10.6 GB); fused vs `--model-draft` `llama-server` commands with n_max-3-default sweep note and ComfyUI `0a33ed6`/`e795821`/`0.3.48` tested path.

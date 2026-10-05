---
type: Concept
title: Cdiamond Qwen3.8-27B iMatrix NVFP4 MTP GGUF
description: Mixed-precision NVFP4 GGUF of Qwen3.8-27B at 5.01 bpw with iMatrix-protected attention, embedded MTP, and measured 256K/24GB llama.cpp profiles.
tags: [qwen3.8, gguf, quantization, nvfp4, imatrix, llama-cpp, mtp, speculative-decoding, vision, local-inference, long-context]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T19:35:00Z }
stale_after: 2027-04-05
sources:
  - id: cdiamond
    resource: ../raw/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF.md
    title: Qwen3.8-27B iMatrix NVFP4 MTP GGUF model card
---

Cdiamond ships a 17.1 GB, 5.01 BPW mixed-precision GGUF of `Qwen/Qwen3.8-27B` that keeps large tolerant matrices in native NVFP4 while protecting selected attention, Gated DeltaNet, and late FFN tensors at higher precision, with one trained MTP layer embedded in the same file and a measured 261,500-token plus 256-generated occupied-cache fill on a single 24 GB card[^cdiamond]. **Reported** by the model card throughout; no weights, commands, or benchmarks were executed here.

## Release identity

- Base is `Qwen/Qwen3.8-27B` with `base_model_relation: quantized`; frontmatter declares `pipeline_tag: image-text-to-text`, `license: apache-2.0`, and tags for `gguf`, `nvfp4`, `imatrix`, `mtp`, `llama.cpp`, multimodal, and 256k-context[^cdiamond]. **Reported**, with static frontmatter presence **Observed**.
- Builder is Michał Piszczek; Hugging Face download path is `cdiamond/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF`; conversion starting point and unchanged F16 projector come from `unsloth/Qwen3.8-27B-GGUF`; runtime is `ggml-org/llama.cpp`; full experiment including losing builds is at the linked `piszczek.pl` 256K/50-TPS post[^cdiamond]. **Reported**.
- This is not a fine-tune; quantized derivative inherits Apache-2.0 with original attribution on redistribution[^cdiamond]. **Reported**.
- Release prep date stated as 18 August 2026 for the llama.cpp-branch snapshot; checksum in `SHA256SUMS` was generated after public metadata replaced private build metadata[^cdiamond]. **Reported**.

## Files

Card file table[^cdiamond]. **Reported**.

| File | Bytes | Purpose |
|---|---:|---|
| `Qwen3.8-27B-iMatrix-NVFP4-MTP.gguf` | 17,125,207,136 | Target model and one embedded MTP layer |
| `mmproj-Qwen3.8-27B-F16.gguf` | 927,607,488 | Optional vision projector, unchanged from upstream conversion |
| `recipe/tensor-types.txt` | small | Tensor overrides for the final hybrid |
| `SHA256SUMS` | small | Release checksums |

## Quant recipe and calibration

- Base file is mostly NVFP4 with protected parts: all Q, K, V, and output matrices in the 16 full-attention layers at Q5_K; selected high-importance DeltaNet QKV, gate, and output matrices at Q5_K; late FFN down projections in layers 54 and 57–63 at Q6_K with matching gate/up at Q5_K; token embeddings at Q6_K; output head at Q8_0; embedded MTP weights left at NVFP4; exact regular expressions live in `recipe/tensor-types.txt`[^cdiamond]. **Reported**.
- Private calibration workload: 5,472 messages across 296 real sessions in the author's Hermes agent setup, 153,600 processed tokens covering coding, infrastructure work, tool calls, and mixed Polish-English conversation; `llama-imatrix` ranked tensor sensitivity and chose where precision was worth VRAM and kernel cost; corpus and raw importance matrix are not distributed or embedded; NVFP4 block quantization itself does not consume the matrix[^cdiamond]. **Reported**.
- Short WikiText-2 control perplexity: ready-made FP4 6.4949 versus plain Q4_0 6.3798 motivated the build; first higher-quality hybrid had good perplexity but only 34.19 tok/s with no comfortable room for 256K plus vision; final hybrid scored 6.1197 versus Q4_1 6.1127 on the same sample, a 0.11% gap the author treats as tied rather than a quality win because it sits inside this short check's error[^cdiamond]. **Reported** with unstated sample length and harness detail.

## Measured results

Hardware and placement as stated[^cdiamond]. **Reported**.

- GPU0: NVIDIA RTX PRO 4000 Blackwell SFF Edition, 24 GB GDDR7 ECC, 192-bit, 432 GB/s rated, 70 W maximum board power, 24,467 MiB reported capacity, sm120a; GPU1 (optional, vision only in this profile): NVIDIA RTX 2000 Ada, 15,996 MiB, sm89; Debian 13, CUDA 12.9.86, GCC 14.2; main model, MTP, recurrent state, CUDA graphs, and target KV on GPU0; optional F16 vision projector on GPU1.
- The 70 W figure is NVIDIA's board-power limit, not a captured power reading; no wall-energy measurement, so the release makes no tokens-per-joule claim[^cdiamond]. **Reported**.

Throughput rows, all measured on GPU0 and stated as separate measurements rather than one combined run[^cdiamond]. **Reported**; workload shape for the tok/s series is unstated beyond the server profiles below, so per the SCOPE benchmark rule these stay **Reported** with that limit (**Synthesis** on the rule application).

| Test | Result |
|---|---:|
| Production series, 10 runs | 50.441 tok/s mean, 49.420–51.397 |
| Clean llama.cpp b10454 | 45.422 tok/s |
| Measured custom runtime on RTX PRO 4000 Blackwell SFF | 55.402 tok/s, +21.97% |
| Target-only greedy | 21.189 tok/s |
| Embedded MTP | 59.456 tok/s, 2.81x target-only |
| Real context fill | 261,500 input tokens + 256 generated |
| Full-cache prefill | 226.750 tok/s |
| Full-cache decode | 12.606 tok/s |
| GPU0 after full fill | 23,952 / 24,467 MiB |
| GPU1 projector, optional vision path | 982 MiB |

- The 55.402 tok/s runtime A/B is not the same run as the 50.441 tok/s production series; rows are kept separate because multiplying unrelated best cases gives a nice but useless benchmark[^cdiamond]. **Reported**.
- The 256K result is an occupied-cache measurement: the server ingested 261,500 tokens, generated 256 more, did not truncate, and did not OOM; merely allocating a 262,144-token slot is much easier[^cdiamond]. **Reported**.

## Pinned llama.cpp branch

- Custom runtime locally merges six pinned PR heads the author did not write; none had merged upstream when the release was prepared on 18 August 2026; exact heads are pinned in `recipe/llama.cpp-patches.md`, which the card calls a benchmark manifest and warns may move or go obsolete — check current upstream before building[^cdiamond]. **Reported**.

| Pull request | Author | What it changed in this setup |
|---|---|---|
| #26001 | BLSharda | Chunked CUDA kernel for Gated DeltaNet prefill |
| #26048 | kmorennv | Fused NVFP4 scale handling in the MMQ epilogue |
| #26705 | praneshgo | Branchless Q4_K/Q5_K CUDA path used during speculative verification |
| #27173 | PatrickWalther | Chained MTP verification and token rollback fix |
| #24891 | hakuhan | Correct recurrent-checkpoint invalidation after tool requests |
| #25635 | ynankani | XOR-swizzled Flash Attention K/V tiles |

- First three patches moved the controlled run from 45.422 to 45.866 tok/s; adding #27173 reached 55.402 tok/s; #25635 separately moved 32K prefill from 759.38 to 815.64 tok/s and hot decode from 37.26 to 38.23 tok/s; #24891 is a correctness fix for long agent sessions, not a speed claim[^cdiamond]. **Reported**.
- Patches do not change the model file or its clean-upstream compatibility; the model was checked against clean upstream build 10454, commit `4df29be4f`; newer compatible builds should work but the commit should be recorded when comparing performance[^cdiamond]. **Reported**.

## Run profiles

Text-only needs the main GGUF; add the projector only for image input[^cdiamond]. **Reported** recipes, not reproduced.

```bash
hf download cdiamond/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF \
  Qwen3.8-27B-iMatrix-NVFP4-MTP.gguf \
  mmproj-Qwen3.8-27B-F16.gguf \
  --local-dir ./qwen38
```

Conservative text-plus-vision profile uses `n_max=1`, described as the safer starting point when output equivalence matters at the cost of leaving performance on the table[^cdiamond]. **Reported**.

```bash
CUDA_VISIBLE_DEVICES=0,1 \
MTMD_BACKEND_DEVICE=CUDA1 \
llama-server \
  --model ./qwen38/Qwen3.8-27B-iMatrix-NVFP4-MTP.gguf \
  --mmproj ./qwen38/mmproj-Qwen3.8-27B-F16.gguf \
  --device CUDA0 \
  --n-gpu-layers 999 \
  --ctx-size 262144 \
  --parallel 1 \
  --ctx-checkpoints 4 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  --batch-size 512 \
  --ubatch-size 256 \
  --temp 0.6 \
  --spec-type draft-mtp \
  --spec-draft-n-max 1 \
  --spec-draft-backend-sampling \
  --reasoning-preserve \
  --jinja
```

Max-throughput profile behind the production measurements, with `LLAMA_SPEC_CHAIN=1` and `GGML_CUDA_GRAPH_OPT=1`, `--spec-default`, `n_max=8`, f16 draft KV, and metrics[^cdiamond]. **Reported**.

```bash
export CUDA_VISIBLE_DEVICES=0,1
export MTMD_BACKEND_DEVICE=CUDA1
export LLAMA_SPEC_CHAIN=1
export GGML_CUDA_GRAPH_OPT=1

llama-server \
  --model ./qwen38/Qwen3.8-27B-iMatrix-NVFP4-MTP.gguf \
  --alias Qwen3.8-27B-iMatrix-NVFP4-256K-MTP \
  --device CUDA0 \
  --n-gpu-layers 999 \
  --fit off \
  --ctx-size 262144 \
  --parallel 1 \
  --ctx-checkpoints 4 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  --batch-size 512 \
  --ubatch-size 256 \
  --threads 8 \
  --threads-batch 8 \
  --temp 0.6 \
  --spec-type draft-mtp \
  --spec-default \
  --spec-draft-n-max 8 \
  --spec-draft-n-min 0 \
  --spec-draft-p-min 0 \
  --spec-draft-type-k f16 \
  --spec-draft-type-v f16 \
  --spec-draft-threads 8 \
  --spec-draft-threads-batch 8 \
  --spec-draft-backend-sampling \
  --mmproj ./qwen38/mmproj-Qwen3.8-27B-F16.gguf \
  --image-min-tokens 1024 \
  --reasoning-preserve \
  --jinja \
  --metrics
```

- `--fit off` is intentional so automatic fitting cannot silently reduce context or change placement to keep its own safety margin; confirm allocation on your own card rather than copying blindly[^cdiamond]. **Reported**.
- Full profile uses a second GPU for the projector; text-only omits `--mmproj` and `MTMD_BACKEND_DEVICE`; putting the F16 projector on the same 24 GB card as the full 256K allocation is likely to cross the measured memory limit[^cdiamond]. **Reported**.

## Why MTP stops at eight

- On this model and GPU, `n_max=8` hit a favorable verification shape: nine candidates were no faster at about 150 MiB more, ten crossed another CUDA allocation boundary, and at 20 throughput fell to 30.60 tok/s[^cdiamond]. **Reported**.
- The MTP head preferred the lower-precision match: requantizing only its eight weight tensors to iMatrix Q5_K added 50.625 MiB and reduced the ten-run mean from 50.441 to 48.733 tok/s, while a Q5_K/Q6_K version added 69.219 MiB and fell to 37.024 tok/s; more accurate standalone draft weights agreed less often with this quantized target[^cdiamond]. **Reported**.

## Known limitation: batch invariance

- Target-only greedy decoding and MTP `n_max=8` do not produce the same continuation on this quantized target; both paths were deterministic inside their own configurations, but max-throughput mode is not bitwise distribution-preserving relative to target-only decode, matching open llama.cpp batch-invariance issue #25618[^cdiamond]. **Reported**.
- Use `n_max=1` if that property matters more than throughput; do not report the `n_max=8` result as lossless speculative decoding[^cdiamond]. **Reported**.
- Performance depends heavily on workload and cache position: agentic code with repeated schemas and prefixes can accept drafts well, while a fresh request at the far end of 256K is a different machine despite identical weights[^cdiamond]. **Reported**.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base; that page covers the Unsloth GGUF/NVFP4 local path while this is the Cdiamond iMatrix-guided hybrid NVFP4 alternative tuned for 256K on 24 GB with embedded MTP.
- Uses [Unsloth Dynamic NVFP4 Quantization](unsloth-dynamic-nvfp4.md) — Blackwell W4A4 serving context shared with the `unsloth/Qwen3.8-27B-GGUF` conversion starting point and F16 projector named here.
- Uses [Speculative Decoding Foundations](speculative-decoding-foundations.md) — draft-verify-accept mechanism behind the embedded-MTP 2.81x target-only gain and the `n_max` depth tuning.
- Uses [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — workload, acceptance-shape, and cache-position lens for the `n_max=8` optimum, the lower-precision draft-match finding, and the agentic-prefix versus far-end-256K split.
- Related to [Gittensor Qwen3.8-27B NVFP4 RTX 5090](gittensor-qwen3.8-27b-nvfp4-rtx5090.md) — Blackwell NVFP4 server checkpoint of the same base with NVFP4 `lm_head` and removed MTP head, contrasting with this file's NVFP4 MTP retention and 24 GB 256K profile.
- Related to [ISTA-DASLab Qwen3.8-27B GSQ-RCO GGUF](ista-qwen3.8-27b-gsq-rco-gguf.md) — non-uniform GGUF source for the same base with its own per-tensor precision allocation and MTP builds.
- Related to [HauhauCS Qwen3.8-27B Aggressive MTP GGUF](hauhaucs-qwen3.8-27b-aggressive-mtp-gguf.md) — community GGUF of the same base with preserved NextN head and FastMTP sidecar, an alternative MTP acceleration packaging to the embedded-only approach here.

## Coverage limits

- Entry point `../raw/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF.md` inspected statically (**Observed**); no commands executed, so install/run recipes and tok/s plus PPL figures are **Reported**, not reproduced.
- Linked artifacts uninspected: `Qwen3.8-27B-iMatrix-NVFP4-MTP.gguf` and `mmproj-Qwen3.8-27B-F16.gguf` weights, `recipe/tensor-types.txt` and `recipe/llama.cpp-patches.md`, `SHA256SUMS`, private Hermes calibration corpus and raw importance matrix (stated as not distributed), base `Qwen/Qwen3.8-27B`, `unsloth/Qwen3.8-27B-GGUF` conversion, six llama.cpp PR heads and issue #25618, upstream build 10454, and the `piszczek.pl` experiment post.
- Per the quantization domain rule, the PPL pairing (short WikiText-2 control, Q4_0/Q4_1 baselines, NVFP4-hybrid format) is recorded with its short-sample uncertainty limit; per the benchmark rule, tok/s comparisons carry hardware and engine revisions but production-series workload shape, prompt/decode lengths, sampling, and variance beyond the 10-run range are unstated.
- No sensitive values appear in the source; author name and public repo/blog links are public attribution.

[^cdiamond]: Qwen3.8-27B iMatrix NVFP4 MTP GGUF model card — `../raw/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF.md` (Michał Piszczek; Apache-2.0; base `Qwen/Qwen3.8-27B`; frontmatter plus sections Files / Quant recipe / Measured results / The llama.cpp branch behind 55.402 tok/s / Run it on current llama.cpp / The measured max-throughput profile / Why MTP stops at eight / Known limitation: batch invariance / Provenance and license): 17,125,207,136-byte 5.01-BPW hybrid with Q5_K full-attention and DeltaNet protection, Q6_K late-down plus embeddings, Q8_0 head, NVFP4 MTP, and `recipe/tensor-types.txt` regexes; 5,472-message / 296-session / 153,600-token Hermes calibration with `llama-imatrix` ranking and undistributed corpus; WikiText-2 short-control PPL chain (FP4 6.4949, Q4_0 6.3798, hybrid 6.1197 vs Q4_1 6.1127 tied, early hybrid 34.19 tok/s); RTX PRO 4000 24 GB plus RTX 2000 Ada vision placement with Debian 13 / CUDA 12.9.86 / GCC 14.2; ten-row tok/s plus 261,500+256 occupied-cache fill with 23,952/24,467 MiB and separate-run warning; six-PR custom runtime (45.422→45.866→55.402, 32K prefill/decode deltas, #24891 correctness fix, `recipe/llama.cpp-patches.md` manifest, 18 Aug 2026 snapshot, b10454 `4df29be4f` compat); conservative `n_max=1` and max-throughput `n_max=8` `llama-server` profiles with `--fit off` and two-GPU projector notes; `n_max=8` verification shape with 9/10/20 falloff and Q5_K/Q6_K MTP-requant regressions; #25618 batch-invariance non-equivalence with `n_max=1` guidance and workload/cache-position dependence; `unsloth/Qwen3.8-27B-GGUF` plus `piszczek.pl` provenance.

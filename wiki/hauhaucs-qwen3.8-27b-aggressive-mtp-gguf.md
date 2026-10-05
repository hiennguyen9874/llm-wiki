---
type: Concept
title: HauhauCS Qwen3.8-27B Aggressive MTP GGUF
description: Aggressive-uncensored Qwen3.8-27B GGUF family with K_P quants, preserved NextN head, and FastMTP 32K draft sidecar reporting up to 3.02x document TG on Blackwell for llama.cpp serving.
tags: [qwen3.8, gguf, quantization, llama-cpp, uncensored, mtp, speculative-decoding, vision, local-inference]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T19:30:00Z }
stale_after: 2027-04-05
sources:
  - id: hauhaucs
    resource: ../raw/Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-MTP-GGUF.md
    title: Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-MTP-GGUF model card
---

HauhauCS ships an Aggressive-uncensored redistribution of `Qwen/Qwen3.8-27B` as GGUF text quants with the native NextN/MTP head preserved, custom `K_P` quantization profiles, a separate BF16 vision projector, and a variant-specific FastMTP 32K draft sidecar plus llama.cpp patch reporting up to 3.02x document token-generation (TG) versus MTP-off on Blackwell[^hauhaucs]. **Reported** by the model card throughout; no weights, GGUFs, patch, manifests, or commands were executed here, so all refusal, size, speed, acceptance, and sampling figures are card claims, not reproduced.

## Method and lineage

- Base is `Qwen/Qwen3.8-27B`; datasets and intended capabilities are unchanged, and the release preserves text, reasoning, agentic, image, and video capabilities while applying the HauhauCS Aggressive uncensoring profile[^hauhaucs]. **Reported**.
- Aggressive variant means direct answers, no refusal behavior, and minimal preamble on hard prompts; the card reports `0/465` refusals and recommends Aggressive when the user wants the answer without compliance preamble, with a Balanced release as the safer default for reliability-critical long-context agentic work when available[^hauhaucs]. **Reported**.
- Harmful-prompt contents are absent from the source and are excluded here; only the refusal-count headline and profile intent are recorded.
- License is Apache-2.0 inherited from Qwen3.8-27B[^hauhaucs]. **Reported**.

## Architecture and specs

Card specs for the 27B dense base[^hauhaucs]. **Reported**.

| Property | Value |
|---|---|
| Layers | 64 language-model layers |
| Hidden / FFN | 5,120 / 17,408 |
| Vocabulary | 248,320-token padded |
| Attention mix | 48 Gated DeltaNet layers + 16 gated-attention layers |
| Drafting | Native embedded MTP/NextN preserved, plus FastMTP 32K profile |
| Context | 262,144 native; up to 1,000,000 with framework-specific config |
| Modalities | Native text, image, video understanding |

## K_P quants and file ladder

- `K_P` ("Perfect") quants are HauhauCS model-specific quantization profiles that selectively preserve quality where analysis says it matters most; each model gets its own profile[^hauhaucs]. **Reported**.
- A `K_P` quant is claimed to bump quality by one or two quant levels at ~5–15% more size than the base quant; files remain standard GGUFs loadable in llama.cpp, LM Studio, and other GGUF runtimes with no special build or plugin[^hauhaucs]. **Reported**.
- `K_P` files may display as `?` in LM Studio's quant column and in Hugging Face's Hardware Compatibility widget; the card calls both display issues and points to **View variants** / **Files and versions**[^hauhaucs]. **Reported**.
- BPW is the encoded tensor-payload average across the complete text model including embedded MTP tensors, rounded to two decimals; the projector and FastMTP sidecar work with every text quant, and the projector is needed only for image/video input[^hauhaucs]. **Reported**.

| File family | Quant | BPW | Size[^hauhaucs] |
|---|---:|---:|---:|
| Text `Q8_K_P` | Q8_K_P | 9.21 | 31.46 GB |
| Text `Q6_K_P` | Q6_K_P | 7.59 | 25.92 GB |
| Text `Q5_K_P` | Q5_K_P | 5.92 | 20.22 GB |
| Text `Q4_K_P` | Q4_K_P | 5.25 | 17.92 GB |
| Text `IQ4_XS` | IQ4_XS | 4.60 | 15.71 GB |
| Text `Q3_K_P` | Q3_K_P | 3.93 | 13.44 GB |
| Text `IQ3_M` | IQ3_M | 3.74 | 12.79 GB |
| Text `IQ3_XS` | IQ3_XS | 3.56 | 12.18 GB |
| Text `Q2_K_P` | Q2_K_P | 3.12 | 10.68 GB |
| Text `IQ2_M` | IQ2_M | 3.02 | 10.32 GB |
| `mmproj-...-BF16.gguf` | Vision projector | — | 931 MB |
| `...-FastMTP-32K.gguf` | FastMTP sidecar | — | 903 MB |

- Base-quant rows (`Q8_0`, `Q6_K`, `Q5_K_M`, `Q4_K_M`, `Q3_K_M`) are listed without files as size/BPW references[^hauhaucs]. **Reported**.

## HauhauCS FastMTP

- FastMTP is a variant-specific acceleration profile for this exact Aggressive release: a compact 32K draft sidecar plus per-quant serving profiles qualified for TG, acceptance, maximum native context, and VRAM; construction/selection methodology is stated as HauhauCS-exclusive[^hauhaucs]. **Reported**.
- The unchanged full target verifies every drafted token, so FastMTP accelerates generation without replacing the target or changing its answers; every FastMTP result is claimed to reproduce the corresponding embedded-MTP output hashes[^hauhaucs]. **Reported**.
- Terminology note: this vendor FastMTP sidecar/profile is distinct from the FastMTP-style recursive single-head fine-tuning in [vLLM FastMTP Fine-Tuning](vllm-fastmtp-fine-tuning.md), which adapts one shipped MTP head via Speculators 0.6.0; do not conflate their methods or numbers. **Synthesis**.
- Two acceleration paths: embedded MTP uses any target GGUF alone with `--spec-type draft-mtp` in a current upstream llama.cpp build; HauhauCS FastMTP pairs the same target with the 32K sidecar plus the HauhauCS runtime patch[^hauhaucs]. **Reported**.

Benchmark ladder on one RTX PRO 6000 Blackwell 96 GB per isolated lane at `204800` configured context, full CUDA offload, `--no-mmap`, and the official reasoning sampler; FastMTP accelerates TG with PP reported alongside[^hauhaucs]. **Reported**, protocol as stated.

| Comparison | Document TG | Reasoning TG | Scope |
|---|---:|---:|---|
| Standard embedded MTP vs MTP disabled | 2.23x (+123.4%) | 1.60x (+59.6%) | Final Q8_K_P, depth 2 |
| FastMTP profile vs standard embedded MTP | +35.2% | +21.1% | Final Q8_K_P, depth 3 vs depth 2 |
| FastMTP vs embedded MTP at identical depth | +11.1% | +18.2% | Final Q8_K_P, depth 3 |
| FastMTP vs MTP disabled | 3.02x (+202.0%) | 1.93x (+93.3%) | Final Q8_K_P service |

## Run recipe (llama.cpp)

Pinned engine revision `4df29be4f4c3673f428170fda944a5b19f743bb8`; CUDA example with ROCm/HIP/Vulkan/CPU-only substitutions noted in the card[^hauhaucs]. **Reported**; commands not executed here.

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
git checkout 4df29be4f4c3673f428170fda944a5b19f743bb8
curl -L -o HauhauCS-FastMTP-llama.cpp.patch \
  https://huggingface.co/HauhauCS/Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-MTP-GGUF/resolve/main/HauhauCS-FastMTP-llama.cpp.patch
git apply --check HauhauCS-FastMTP-llama.cpp.patch
git apply HauhauCS-FastMTP-llama.cpp.patch
cmake -S . -B build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j"$(nproc)"
```

Serve example (Q4_K_P target + shared sidecar, depth 3)[^hauhaucs]:

```bash
MODEL=Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-Q4_K_P.gguf
DRAFT=Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-FastMTP-32K.gguf
DEPTH=3
CUDA_VISIBLE_DEVICES=0 ./build/bin/llama-server \
  --model "$MODEL" \
  --spec-draft-model "$DRAFT" \
  --spec-draft-ngl all \
  --spec-type draft-mtp \
  --spec-draft-n-max "$DEPTH" \
  --spec-draft-p-min 0 \
  --ctx-size 204800 \
  --parallel 1 \
  --batch-size 2048 \
  --ubatch-size 512 \
  --n-gpu-layers all \
  --split-mode none \
  --flash-attn on \
  --no-mmap \
  --temp 1.0 --top-k 20 --top-p 0.95 --min-p 0 \
  --presence-penalty 0 --repeat-penalty 1.0 \
  --jinja --reasoning on --reasoning-effort xhigh \
  --reasoning-preserve --reasoning-format deepseek \
  --host 127.0.0.1 --port 8080
```

- If draft loading reports `expected 5120, 248320, got 5120, 32768`, the sidecar is correct but the executable is unpatched; relaunch the freshly built `llama-server` from the patched checkout[^hauhaucs]. **Reported**.

## Measured speeds

Blackwell reference: three-run medians for the uncached 9.8K-token document fixture and three-case means for reasoning, FastMTP depth 3[^hauhaucs]. **Reported**.

| Quant | PP tok/s | Document TG | Reasoning TG | vs embedded n2 Doc/Reason | vs MTP-off Doc/Reason |
|---|---:|---:|---:|---:|---:|
| Q2_K_P | 3351.29 | 213.95 | 145.09 | +11.6% / +1.7% | 2.27x / 1.48x |
| Q3_K_P | 3317.16 | 216.15 | 137.99 | +20.5% / +8.8% | 2.54x / 1.56x |
| Q4_K_P | 3204.98 | 187.26 | 123.52 | +18.0% / +2.3% | 2.67x / 1.71x |
| Q5_K_P | 2842.05 | 168.29 | 110.50 | +17.8% / +4.6% | 2.61x / 1.66x |
| Q6_K_P | 3081.90 | 156.57 | 103.51 | +26.5% / +13.8% | 2.95x / 1.91x |
| Q8_K_P | 3285.86 | 138.18 | 90.07 | +35.2% / +21.1% | 3.02x / 1.93x |
| IQ2_M | 3050.94 | 219.19 | 135.00 | +13.8% / +0.4% | 2.33x / 1.39x |
| IQ3_M | 3269.27 | 204.98 | 128.45 | +21.5% / +7.9% | 2.40x / 1.45x |
| IQ3_XS | 3165.75 | 210.64 | 138.34 | +19.1% / +5.9% | 2.38x / 1.51x |
| IQ4_XS | 3445.30 | 211.09 | 135.77 | +21.7% / +9.3% | 2.68x / 1.66x |

- Full-window gate with final scrubbed Q3_K_P + FastMTP: 190,000 uncached prompt tokens plus 64 generated tokens at 1613.81 PP tok/s and 131.81 TG tok/s, 92.0% draft acceptance, no truncation inside configured maximum native context[^hauhaucs]. **Reported** with workload, target/draft pair, and acceptance stated per speculative-decoding domain rule.

Ada reference: single-run embedded-MTP results on RTX 6000 Ada at max-token context, full CUDA offload, `--no-mmap`, official thinking sampler, uncached 9.8K-token document prompt + 512 generated tokens[^hauhaucs]. **Reported**.

| Quant | PP tok/s | TG tok/s |
|---|---:|---:|
| Q2_K_P | 1959.14 | 121.88 |
| Q3_K_P | 1944.73 | 112.76 |
| Q4_K_M ref | 1860.34 | 92.60 |
| Q5_K_M ref | 1737.51 | 83.25 |
| Q6_K ref | 1747.60 | 72.89 |
| Q8_K_P | 1827.29 | 59.00 |
| IQ2_M | 1884.83 | 121.25 |
| IQ3_M | 1867.48 | 108.45 |
| IQ3_XS | 1880.59 | 111.77 |
| IQ4_XS | 1978.46 | 104.25 |

- On the same Ada with FastMTP, final Q3_K_P reached 138.37 document TG and 87.95 reasoning TG — 23.5% and 3.9% faster than the pinned Unsloth Q3 control[^hauhaucs]. **Reported**.

## Sampling, thinking, and compatibility

- Thinking mode (default) from the official Qwen3.8-27B card: `temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=0.0`, `repetition_penalty=1.0`, `reasoning_effort=xhigh` for deepest reasoning; instruct/non-thinking: `temperature=0.7`, `top_p=0.80`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0`, `enable_thinking=false`; effort levels `xhigh`/`medium`/`low`[^hauhaucs]. **Reported**.
- Use `--jinja` for the embedded chat template and the BF16 projector for vision; native maximum `262144`; reduce context before model quality under VRAM pressure; keep default F16 K/V on lower tiers unless memory-constrained; update llama.cpp if reasoning/MTP flags are unrecognized[^hauhaucs]. **Reported**.
- Thinking-off patterns: `--chat-template-kwargs '{"enable_thinking":false}'` for llama-server defaults, per-request `chat_template_kwargs.enable_thinking=false` over the OpenAI-compatible API, and `preserve_thinking=true` for multi-turn agent reasoning context[^hauhaucs]. **Reported**.
- Compatibility: llama.cpp recommended with a current Qwen3.8/MTP-capable build; LM Studio/Jan/KoboldCpp depend on bundled llama.cpp version; embedded MTP is stock-optional; FastMTP requires sidecar + patch; vision requires BF16 projector[^hauhaucs]. **Reported**.

## Authenticity

- Every GGUF is covered by a signed HauhauCS release manifest; SHA-256 identifies byte mirrors after renaming and tensor fingerprints identify tensors after metadata-only rewrites[^hauhaucs]. **Reported**.
- FastMTP sidecar SHA-256 `115e618e…8968b`, tensor fingerprint `49e248e7…81d1c87`, and public-key DER fingerprint `f7be4a23…3833c` are published; verification uses `openssl pkeyutl -verify` against `HauhauCS-RELEASE-MANIFEST.json(.sig)` and `FastMTP-PROVENANCE.json(.sig)` with `HauhauCS-FastMTP-Ed25519-PUBLIC.pem`[^hauhaucs]. **Reported**. Full hash values and commands live in the source; only prefixes are repeated here.
- Discord invite and Hugging Face file/patch/manifest URLs in the source were not followed; linked artifacts are coverage limits below.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — community GGUF/serving entry point for the same 27B base sharing sampling, thinking, MTP, and NVFP4 context.
- Uses [Speculative Decoding Foundations](speculative-decoding-foundations.md) — draft-verify-accept mechanism behind the embedded-MTP and FastMTP TG gains.
- Uses [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — workload/acceptance/depth tuning lens for the document vs reasoning TG split and depth-2 vs depth-3 comparisons.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — native-MTP serving path; contrast with the llama.cpp `--spec-type draft-mtp` paths used here.
- Related to [vLLM FastMTP Fine-Tuning](vllm-fastmtp-fine-tuning.md) — different FastMTP meaning (recursive single-head training) named to prevent terminology collision.
- Related to [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — alternative per-layer dynamic GGUF family used as the Ada Q3 control.
- Related to [JonathanColetti Qwen3.8-27B Uncensored GGUF](jonathancoletti-qwen3.8-27b-uncensored-gguf.md) — Heretic-abliterated uncensored GGUF of the same base with verbatim MTP and fused/split packaging for comparison.
- Related to [RVN Qwen3.8-27B Heretic Abliterated Uncensored GGUF](rvn-qwen3.8-27b-heretic-abliterated-gguf.md) — ARA-abliterated uncensored GGUF of the same base with embedded-MTP twins and vision variants.
- Related to [ISTA-DASLab Qwen3.8-27B GSQ-RCO GGUF](ista-qwen3.8-27b-gsq-rco-gguf.md) — non-uniform GSQ-RCO GGUF source for the same base with MTP builds and fidelity figures.

## Coverage limits

- Single Markdown card inspected statically; no GGUF, projector, sidecar, patch, manifest, provenance JSON, signature, or key fetched or verified, and no build/serve/benchmark command executed.
- Hugging Face download/patch/manifest/provenance URLs, Discord invite, base `Qwen/Qwen3.8-27B` card, and official sampler/benchmark fixtures uninspected; all quantitative figures remain vendor-**Reported** per `SCOPE.md` cross-cutting benchmark rule (hardware stated for TG tables; harness variance and uncertainty unstated).
- No accuracy/fidelity (PPL/KL/benchmark) figures accompany the card, so per quantization domain rule there is no accuracy claim to pair with baseline and format.

[^hauhaucs]: HauhauCS Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-MTP-GGUF model card — `../raw/Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-MTP-GGUF.md`, covering Aggressive 0/465-refusal profile and Balanced default guidance, 64-layer / 5120-hidden / 248320-vocab / 48-GDN + 16-gated-attention specs with 262K–1M context, K_P definition with 1–2-level / 5–15% claim and 10-file BPW/size ladder plus BF16 projector and 32K sidecar, FastMTP-vs-embedded-vs-off benchmark ladder and RTX PRO 6000 Blackwell plus RTX 6000 Ada TG/PP tables with 190K full-window 92.0%-acceptance gate, llama.cpp `4df29be4` patch/build plus `llama-server` depth-3 serve recipe and `got 5120, 32768` diagnostic, official thinking/instruct sampling with `xhigh`/`medium`/`low` effort and thinking-off/preserve patterns, compatibility matrix, and signed-manifest authenticity with sidecar SHA-256/tensor/key fingerprints and `openssl pkeyutl` verify commands.

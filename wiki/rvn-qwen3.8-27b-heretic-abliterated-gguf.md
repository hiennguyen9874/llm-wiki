---
type: Concept
title: RVN Qwen3.8-27B Heretic Abliterated Uncensored GGUF
description: Double-refined ARA abliteration of Qwen3.8-27B with multilingual GGUF ladder, embedded-MTP speculative twins, and vision-bridge variants for llama.cpp serving.
tags: [qwen3.8, gguf, quantization, llama-cpp, abliteration, uncensored, mtp, speculative-decoding, vision, local-inference]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T16:00:00Z }
stale_after: 2027-04-05
sources:
  - id: rvn
    resource: ../raw/Qwen3.8-27B-Heretic-Abliterated-Uncensored-GGUF.md
    title: Qwen3.8-27B RVN Heretic Abliterated Uncensored (GGUF) model card
---

RVN is a double-refined abliterated redistribution of `Qwen/Qwen3.8-27B` built on `trohrbaugh/Qwen3.8-27B-heretic-ara` with two additional full-weight ARA passes, reported to cut refusals from 3/100 to 0–1/100 while lowering KL damage versus base from 0.0535 to 0.0085, and shipped as a large llama.cpp GGUF family with a recommended multilingual calibration tier, embedded-MTP speculative twins, vision-bridge variants, and an official vision projector pairing[^rvn]. **Reported** by the model card unless noted; no command was executed here, so refusals, KL, perplexity, speed, and fit figures are card claims, not reproduced.

## Lineage and intent

- Base is `Qwen/Qwen3.8-27B`; RVN refines `trohrbaugh/Qwen3.8-27B-heretic-ara` (ARA, KL 0.0535, refusals 3/100) with two more full-weight ARA passes to reach KL 0.0085 and 0–1/100 refusals[^rvn]. **Reported**.
- "Heretic" names the tool (the open-source ARA/abliteration implementation); "Abliterated" names the result (refusal behavior surgically removed while retained knowledge is unchanged); RVN is three ARA passes total: one upstream plus two local[^rvn]. **Reported** card framing.
- Credit is given to Tim Rohrbaugh for the upstream `heretic-ara` abliteration and upstream heretic contributions including row-norm preservation and Qwen3.5 MoE/DeltaNet hybrid handling that make DeltaNet-layer abliteration work[^rvn]. **Reported**.
- The repo previously hosted `Qwen3.8-27B-Heretic-Q4_K_M.gguf` from the earlier `trohrbaugh/Qwen3.8-27B-heretic` source; it is kept as legacy for download-count continuity, is the older abliteration variant, and is superseded by the RVN files for new deployments[^rvn]. **Reported**.
- Intended audience is adults (18+) for research, creative writing, roleplay, and uncensored generation; guardrails are reduced by design, a small set of hard safety-trained categories is intentionally left in place, behavior may vary across domains and languages, and use must follow local laws[^rvn]. **Reported**; deployment to minors or moderation-dependent applications is out of scope for this artifact.
- License is Apache-2.0 retained from Qwen3.8-27B; base, abliteration source, and repo attributions plus BibTeX entries and a research-use/responsibility notice are included in the card[^rvn].

## ARA method

- ARA (Arbitrary-Rank Ablation) is the abliteration technique from `p-e-w/heretic`; unlike single-direction subtraction, it directly optimizes each target module's weight matrix so it can carve a richer refusal-removal subspace[^rvn]. **Reported**.
- Targets are attention out-projections and MLP down-projections; activations are collected on "good" (harmless) and "bad" (harmful) prompts, then an LBFGS optimizer rewrites each module to preserve good-prompt outputs (low KL), steer bad-prompt outputs toward the good-prompt manifold via k-nearest-neighbor distances, and overcorrect by pushing bad-prompt outputs away from the original bad outputs to defeat multi-stage refusal mechanisms[^rvn]. **Reported**.
- RVN's tight parameter set is start layer 26, end layer 56, preserve 0.9432, steer 0.0009, overcorrect 0.5038, neighbor 10[^rvn]. **Reported**.

## Model architecture

| Property | Value[^rvn] |
|---|---|
| Architecture | `qwen3_5_text` (Qwen3.8 family), Gated DeltaNet hybrid |
| Parameters | 27B total |
| Hidden size | 5120 |
| Layers | 64 (16 standard attention + 48 Gated DeltaNet linear attention) |
| Attention | 24 heads, 4 KV heads (GQA), head_dim 256 |
| Vocab | 248,320 |
| Context | 262,144 (262K) |
| Format | GGUF for llama.cpp; base files exclude MTP/NextN, `*-mtp.gguf` twins embed the official 15-tensor MTP draft head |

## Refusal evaluation

- Protocol is 100 harmful-behavior prompts with prefix-forced real answers, verified independently on two rented GPU machines; the only remaining RVN refusal is a chemical-weapon WMD prompt in the intentionally retained guardrail set[^rvn]. **Reported** with unstated prompt list, harness, and variance.

| Model | Refusals | KL vs base[^rvn] |
|---|---|---:|
| Qwen3.8-27B base | ~99/100 | — |
| trohrbaugh `-ara` source | 3/100 | 0.0535 |
| RVN | 0–1/100 | 0.0085 |

- Residual refusals removed from the source include racism-website, malware, and government-database-hacking categories named by the card; per SCOPE, only these category labels are preserved, not prompt contents[^rvn]. **Reported**.

## File families and selection

- Compatibility status 2026-08-19: the recommended `*-multilingual*.gguf` family and all 53 legacy RVN GGUF paths embed the official Qwen3.8 chat template; every multilingual artifact passed a per-file OpenAI-compatible tool-call/thinking-control gate and legacy paths were repaired in place, so no external template workaround is needed for current files[^rvn]. **Reported**.
- Download one main-model GGUF, not the whole repo; model size excludes KV cache, compute buffers, OS, and optional vision/MTP additions[^rvn].

| Hardware / goal | Recommended main model | Weights[^rvn] |
|---|---|---:|
| Best default on 24 GB GPU | `RVN-Q4_K_M-multilingual.gguf` | 15.41 GiB |
| More quality on 24 GB | `RVN-Q5_K_M-multilingual.gguf` | 17.91 GiB |
| Safe start on 16 GB | `RVN-Q3_K_S-multilingual.gguf` | 11.24 GiB |
| Safe start on 12 GB | `RVN-IQ2_XXS-multilingual.gguf` or `RVN-IQ2_XS-multilingual.gguf` | 7.85 / 8.47 GiB |
| Around 8 GB VRAM | `RVN-IQ1_S-multilingual.gguf` | 6.66 GiB |
| Highest quantized fidelity 32 GB+ | `RVN-Q8_0-multilingual.gguf` | 26.63 GiB |
| Reference/eval 64 GB+ | `RVN-BF16.gguf` or `RVN-F16.gguf` | 50.11 GiB |

- Valid filename families only; suffixes do not combine arbitrarily: `RVN-{QUANT}.gguf`, `RVN-{QUANT}-mtp.gguf`, `RVN-{Q5_K_M|Q4_K_M|Q3_K_M}-vision.gguf`, plus the `-multilingual`, `-multilingual-mtp`, and `-multilingual-vision` counterparts, `RVN-F16/BF16(.mtp)`, and standalone `mtp-RVN.gguf`[^rvn]. **Reported**.
- There is no combined `vision-mtp` file, no `F16-multilingual`/`BF16-multilingual` file, `mmproj-Qwen3.8-27B-Q8_0.gguf` is a separate ~0.63 GB vision projector, and `mtp-RVN.gguf` is a separate 1.69 GiB standalone draft-head compatibility artifact that cannot answer prompts and is not required by embedded twins[^rvn]. **Reported**.
- `-multilingual` is the recommended Qwen-tuned calibration family: its importance matrix covers Turkish, Russian, 20+ other languages, code, reasoning, and tool-use structures rather than narrow English-only text; calibration steers the low-bit precision budget and does not teach new languages, mattering most at 4-bit and below[^rvn]. **Reported**.
- `-mtp` is the same tensor payload plus the official Qwen3.8 15-tensor MTP/NextN draft head for speculative decoding (~451 MB / 0.42 GiB extra; exactly 451,320,768 bytes on current multilingual twins); it is a speed feature, not higher quality[^rvn]. **Reported**.
- `-vision` keeps token embeddings, output, and the first/last bridge blocks at higher precision; it is an optional bridge-preserving variant, not a requirement for images, with no separately benchmarked image-quality uplift claimed[^rvn]. **Reported**.
- No `-multilingual` in the name means the original RVN calibration family, retained and template-correct but superseded for new low-bit downloads by `-multilingual`[^rvn]. **Reported**.
- Quant legend: `Q…_K…` is the llama.cpp K-quant family (`_M` generally retains more than `_S`, `_L` larger again); `IQ…` is importance-aware low-bit, useful when tight; `L → M → S → XS → XXS` moves smaller/lower-fidelity within a family; `NL` is the nonlinear IQ4 variant; do not rank unlike families by suffix alone[^rvn]. **Reported**.
- GSQ-RCO non-uniform quants (4 tiers plus MTP twins) moved to `0bserverx/Qwen3.8-27B-Heretic-GSQ-RCO-GGUF`; see that card for PPL evidence and build method[^rvn]. **Reported**, external repo uninspected.
- `chat_template.jinja` remains only as a readable reference copy of the official template, not a required workaround[^rvn].

## Multilingual v5 calibration and verification

- Rebuilt from the template-correct RVN F16 reference with a pinned Qwen-tuned multilingual/code corpus: gist `tristandruyen/9e207a95c7d75ddf37525d353e00659c` rev `aba17fe897c00fae02a18d26068aa453dee09e50`, corpus SHA-256 `2a0118c6…`, imatrix SHA-256 `5e73e144…`, 55 chunks / 496 entries / ctx 2048, llama.cpp commit `645ca2834bc16e7eab112a91aeb282ebb913f935`, embedded template SHA-256 `c3cf9e34…`[^rvn]. **Reported**.
- 49/49 artifacts passed live LFS SHA-256 and 64 MiB header verification after upload; each loaded in llama.cpp and served through `llama-server` with an OpenAI-compatible API gate (HTTP 200, `finish_reason=tool_calls`, `add({"a":19,"b":23})`); `enable_thinking:false` suppressed `<think>` and a normal-chat control returned `TEMPLATE_OK`; MTP twins additionally load with 866 tensors, `qwen35.block_count=65`, `qwen35.nextn_predict_layers=1`[^rvn]. **Reported**.
- Q8_0 clarification: full tensor-schema and payload hashing proved legacy and multilingual Q8_0 base files byte-identical (MTP twins likewise); multilingual Q8_0 names exist for family/provenance consistency with receipt SHA-256 `210e59a0…`[^rvn]. **Reported**.
- Pilot perplexity deltas (`multilingual − reference`; lower is better): Q4_K_M +0.0038 vs F16 / −0.0074 vs legacy; IQ4_XS +0.0091 vs F16 / −0.0083 vs legacy[^rvn]. **Reported** pilot figures with unstated harness beyond the multilingual section.

## Legacy spectrum, vision-protected variants, and text perplexity

- Legacy family is retained for continuity; representative weights-only sizes: F16/BF16 50.11 GiB, Q8_0 26.63, Q6_K 20.57, Q5_K_M 17.91, Q4_K_M 15.41, Q3_K_M 12.39, Q3_K_S 11.24, IQ2_M 9.32, IQ2_XS 8.47, IQ2_XXS 7.85, IQ1_S 6.66 GiB; the full per-file table with MTP twins and API gates is in the source[^rvn]. **Reported**.
- `RVN-IQ3_M.gguf` was re-uploaded 2026-08-17 after corrupted tensor data (NaN/Inf scales plus zeroed tensors from a bad quantize run); re-quantized from F16 with a fresh imatrix and verified[^rvn]. **Reported**.
- Published `IQ4_XS` and `IQ4_NL` legacy files were made without `--imatrix` per GGUF-header audit and retained production script despite earlier imatrix labels; corrected wikitext-imatrix replacements including MTP twins were being rebuilt at card time[^rvn]. **Reported**.
- Vision-protected (`-vision`) files keep `token_embd`, `output`, and first 4 plus last 4 blocks at Q8_0 with middle blocks at the target K-quant (audit: 106 regex overrides, 851 tensors, correct per-tensor types, 0 NaN/Inf); multilingual vision sizes are Q5_K_M 19.58, Q4_K_M 17.46, Q3_K_M 15.08 GiB[^rvn]. **Reported** structure, explicitly not a benchmarked image-quality claim.
- Text perplexity via `llama-perplexity` on tiny_shakespeare, ctx 2048, RTX PRO 6000 Blackwell full offload, llama.cpp master (**Reported**; per SCOPE quantization rule, baseline is the F16 reference and formats are named):

| Model | PPL | Δ vs F16[^rvn] |
|---|---|---:|
| `RVN-F16.gguf` | 4.5477 | — |
| `RVN-Q5_K_M.gguf` | 4.6493 | +2.23% |
| `RVN-Q5_K_M-vision.gguf` | 4.6497 | +2.24% |
| `RVN-Q4_K_M-vision.gguf` | 4.8751 | +7.20% |
| `RVN-Q3_K_M-vision.gguf` | 5.6490 | +24.2% |

- Imatrix provenance: original spectrum used wikitext-2-raw (580 chunks); 2026-08-17 re-quants (`IQ3_M` fix plus `IQ2_S`/`IQ3_XXS`/`IQ3_XS`/`IQ3_S`) used tiny_shakespeare (159 chunks, `llama-imatrix`, `-ngl 99`); `-vision` files use K-quant defaults with structural Q8_0 overrides, not imatrix-dependent[^rvn]. **Reported**.

## MTP speculative decoding

- Every quant ships a `*-mtp.gguf` twin with the official Qwen3.8 MTP head (Q8_0, ~0.42 GiB) appended as `blk.64.nextn.*` (block_count 65, `qwen35.nextn_predict_layers=1`); main-model weights are byte-identical to the base file; abliteration covered main-model layers 26–56 only, so the draft head is untouched and speculation is output-equivalent[^rvn]. **Reported**.
- Requires llama.cpp ≥ b10440 (PR #22673); start from the plain `-multilingual.gguf` for maximum compatibility and use the `-multilingual-mtp.gguf` twin only with a recent build, enough headroom, and the documented flags[^rvn]. **Reported**:

```bash
llama-server -m RVN-IQ3_M-mtp.gguf -c 32768 -ngl 99 \
  --spec-type draft-mtp --spec-draft-n-max 2 --parallel 1
```

- Measured on 2× RTX PRO 6000 Blackwell (95 GB each, full offload, llama.cpp b10472), 128-token continuation, `--spec-draft-n-max 2 --parallel 1`, tok/s (**Reported**; per SCOPE speculative-decoding rule, no acceptance length is stated, only generation-speed deltas):

| Quant | Normal (t/s) | + MTP (t/s) | Δ[^rvn] |
|---|---|---:|---|
| Q6_K | 61.6 | 126.2 | +105% |
| BF16 | 29.2 | 58.2 | +99% |
| Q8_0 | 50.6 | 98.0 | +94% |
| IQ3_S | 91.9 | 169.7 | +85% |
| IQ4_XS | 83.4 | 152.0 | +82% |
| Q3_K_S | 84.5 | 153.6 | +82% |
| F16 | 29.4 | 52.9 | +80% |
| IQ3_XS | 94.0 | 161.9 | +72% |
| Q3_K_L | 78.7 | 131.3 | +67% |
| IQ4_NL | 80.8 | 138.0 | +71% |
| IQ2_M | 106.2 | 175.9 | +66% |
| IQ2_XS | 112.8 | 183.4 | +63% |
| Q4_K_M | 76.6 | 122.0 | +59% |
| Q4_K_S | 80.5 | 127.1 | +58% |
| IQ3_M | 91.3 | 144.0 | +58% |
| Q3_K_M | 82.6 | 129.5 | +57% |
| IQ2_XXS | 117.6 | 182.6 | +55% |
| Q2_K | 98.2 | 150.2 | +53% |
| IQ3_XXS | 98.5 | 138.5 | +41% |
| IQ2_S | 111.5 | 155.3 | +39% |
| Q5_K_M | 68.1 | 93.8 | +38% |
| Q2_K_S | 105.5 | 145.1 | +38% |
| Q5_K_S | 70.7 | 91.1 | +29% |
| IQ1_S | 127.0 | 131.7 | +3.7% |
| IQ1_M | 119.5 | 47.6 | −60% |

- Average is stated as +55% generation speed; `IQ1_M` must use the plain file (MTP ~60% slower) and `IQ1_S` gains almost nothing (+4%); community reports span +33–145% by GPU/context[^rvn]. **Reported**.
- Tuning notes: `--spec-draft-n-max 2` is the sweet spot on 16–24 GB cards (3–4 on bigger/faster cards); pair with `--cache-type-k q4_0 --cache-type-v q4_0` for long context; `--spec-draft-p-min 0.60–0.75` helps bandwidth-limited rigs[^rvn]. **Reported**; `stale_after` above covers these flags per the serving domain rule.

## Vision

- Pair any compatible RVN main model (standard or `-vision`) with `mmproj-Qwen3.8-27B-Q8_0.gguf` (~0.63 GB, official Qwen3.8 projector from `ggml-org/Qwen3.8-27B-GGUF`, Apache-2.0); the vision tower is an image encoder ARA never touched, so it pairs cleanly; verified case is `RVN-Q3_K_M-mtp` plus mmproj describing images correctly with MTP active, with combo credit to `cfigueiroa/Qwen3.8-27B-RVN-vision-MTP`[^rvn]. **Reported**:

```bash
llama-server -m RVN-Q5_K_M-vision.gguf --mmproj mmproj-Qwen3.8-27B-Q8_0.gguf \
  -c 32768 -ngl 99
```

```bash
llama-server -m RVN-IQ3_M-mtp.gguf --mmproj mmproj-Qwen3.8-27B-Q8_0.gguf \
  -c 32768 -ngl 99 --spec-type draft-mtp --spec-draft-n-max 2 --parallel 1
```

- With no combined `vision-mtp` artifact, choose between the vision-protected build and the embedded-MTP build when both matter[^rvn]. **Synthesis** from the stated family constraint.

## Memory planning

- All file sizes are weights only; budget KV cache, compute buffers, OS, ~0.42 GiB per embedded MTP head, and ~0.63 GB for the vision projector on top; for CPU/Apple unified memory, pick the largest file leaving 6–10 GiB free (more for long context); on ~8 GB VRAM prefer the non-MTP file with short context or partial CPU offload[^rvn]. **Reported** planning guidance.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base; that page covers the official Unsloth GGUF/NVFP4 path while RVN is the ARA-abliterated community GGUF alternative with multilingual calibration, MTP twins, and vision-bridge tiers.
- Related to [Huihui Qwen3.8-27B Abliterated GGUF](huihui-qwen3.8-27b-abliterated-gguf.md) — another uncensored 27B GGUF family; Huihui uses layer-selective ablation with non-standard `K_L` requantization while RVN uses three-pass ARA with multilingual imatrix calibration and embedded MTP heads.
- Related to [Dirk Qwen3.8-27B Sharp-Template GGUF](dirk-qwen3.8-27b-gguf.md) — another community 27B repackaging preserving MTP; Dirk changes only the chat template while RVN changes refusal behavior and calibration.
- Related to [DavidAU Qwen3.8-27B Cold Fusion GAIN GGUF](davidau-qwen3.8-cold-fusion-gain-gguf.md) — another community 27B GGUF; DavidAU compresses thinking tokens via fine-tuning while RVN removes refusals via ARA.
- Related to [ISTA-DASLab Qwen3.8-27B GSQ-RCO GGUF](ista-qwen3.8-27b-gsq-rco-gguf.md) — non-uniform quantization alternative for the same base; RVN's GSQ-RCO tiers now live in a sibling repo rather than this card.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — RVN's embedded 15-tensor MTP twins are instances of the MTP speculative path with the same extra-memory and draft-token tuning considerations.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — RVN is a llama.cpp-side local-inference artifact with `llama-server`/`llama-mtmd-cli` recipes.
- Related to [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — RVN's KL, PPL-delta, and byte-identity evidence are instances of the KL/trajectory/calibration signals used to judge quants.

## Coverage limits

- Entry point `../raw/Qwen3.8-27B-Heretic-Abliterated-Uncensored-GGUF.md` inspected statically (**Observed**); no commands executed, so refusal, KL, PPL, tok/s, template-gate, and hash-verification claims are **Reported**, not reproduced.
- External artifacts uninspected: `Qwen/Qwen3.8-27B`, `trohrbaugh/Qwen3.8-27B-heretic-ara`, `p-e-w/heretic`, `ggml-org/Qwen3.8-27B-GGUF` projector, `cfigueiroa/Qwen3.8-27B-RVN-vision-MTP`, `0bserverx/Qwen3.8-27B-Heretic-GSQ-RCO-GGUF`, gist calibration corpus, llama.cpp builds/commits, rented-GPU eval machines, and all GGUF/mmproj binaries.
- Full 23-quant multilingual plus legacy size tables, per-file MTP-twin sizes, and API-gate columns are summarized here; the source tables remain canonical for exact live sizes.
- No speculative-decoding acceptance length, workload shape beyond 128-token continuation, or disaggregated/prefix-cache behavior is stated; speedups stay **Reported** per the benchmark rule.
- Harmful-prompt contents excluded; only high-level eval categories named by the card are preserved, with intentionally retained guardrails and 18+/legal/responsibility warnings kept verbatim in meaning.

[^rvn]: Qwen3.8-27B RVN Heretic Abliterated Uncensored (GGUF) model card — `../raw/Qwen3.8-27B-Heretic-Abliterated-Uncensored-GGUF.md` (0bserverx; Apache-2.0; base `Qwen/Qwen3.8-27B`; source `trohrbaugh/Qwen3.8-27B-heretic-ara`; compatibility 2026-08-19): three-pass ARA lineage (start 26/end 56/preserve 0.9432/steer 0.0009/overcorrect 0.5038/neighbor 10) with Heretic-tool vs Abliterated-result framing and Rohrbaugh credit; `qwen3_5_text` Gated-DeltaNet architecture (27B/5120/64 layers 16+48/24H-4KV-256d/248320 vocab/262K) and GGUF/MTP format notes; 3/100→0–1/100 refusal and 0.0535→0.0085 KL table with prefix-forced 100-prompt protocol and retained WMD guardrail; quick-pick VRAM table (Q4_K_M 15.41 through IQ1_S 6.66 GiB) with filename families, `-multilingual`/`-mtp` (+451,320,768 B)/`-vision`/legacy naming, quant legend, mmproj pairing, GSQ-RCO split, IQ1_M −60%/IQ1_S +4% MTP exceptions, and legacy/template clarifications; multilingual-v5 rebuild (gist rev `aba17fe8`, corpus/imatrix/template SHAs, 55 chunks/496 entries/ctx 2048, llama.cpp `645ca28`, 49/49 PASS, `tool_calls`/`add({"a":19,"b":23})`/`enable_thinking:false` gates, 866-tensor MTP twins) with pilot PPL deltas and Q8_0 byte-identity receipt `210e59a0`; legacy sizes, IQ3_M 2026-08-17 NaN/Inf re-upload, IQ4_XS/NL no-imatrix correction, `-vision` Q8_0-bridge structure, tiny_shakespeare PPL table (F16 4.5477 to Q3_K_M-vision +24.2%), and imatrix provenance; embedded 15-tensor Q8_0 MTP twins (`blk.64.nextn.*`, 65 blocks) with b10440/PR #22673 flags, 2×RTX-PRO-6000 b10472 128-token speed table (+29% to +105%, avg +55%) and tuning tips; vision projector pairing and `-m/--mmproj` plus MTP commands; weights-only memory budgeting; 18+/reduced-guardrail/responsibility limits, Apache-2.0 attribution, and BibTeX.

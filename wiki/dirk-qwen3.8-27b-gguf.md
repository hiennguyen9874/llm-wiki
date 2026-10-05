---
type: Concept
title: Dirk Qwen3.8-27B Sharp-Template GGUF
description: Qwen3.8-27B GGUF ladder pairing the Sharp terseness template with split GSQ-RCO/Unsloth quants, MTP heads, and llama.cpp serving guidance.
tags: [qwen3.8, gguf, quantization, llama-cpp, reasoning, vision, mtp, speculative-decoding, local-inference]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T15:00:00Z }
sources:
  - id: dirk
    resource: ../raw/Dirk-Qwen3.8-27B-GGUF.md
    title: Dirk-Qwen3.8-27B-GGUF (peculiar-ragdoll model card)
---

Dirk is a community redistribution of `Qwen/Qwen3.8-27B` as llama.cpp GGUFs that keeps the weights and MTP (`nextn`) head intact and changes only the embedded chat template to the Sharp terseness template with the forced-`xhigh` reasoning default removed, published as a 14-file VRAM-sized ladder split between IST-DASLab GSQ-RCO quants below ~3 bpw and Unsloth Dynamic 3.0 quants above[^dirk]. **Reported** by the model card unless noted; benchmark and fit claims carry the unstated-hardware/protocol limits in Coverage limits.

## What Dirk changes

- Base is `Qwen/Qwen3.8-27B`, a dense 27B vision-language model with vision preserved; Apache-2.0 matching upstream[^dirk].
- Only the template changes versus the stock quant: same weights and untouched MTP tensors, byte-swapped Sharp template metadata into the GGUF — "same weights, asked better"[^dirk]. **Reported**.
- Sharp template is Qwen 3.8-aware: froggeric's fixed Qwen template plus a terseness system prompt, with the stock `xhigh` thinking default turned off; terseness opt-out via `chat_template_kwargs: {"terse": false}`[^dirk]. **Reported**.
- Template versions differ by tier: `GSQ-RCO-` files carry `v22.4.1`, which also stands down when the runtime injects its own tool protocol (an LM Studio fix); `UD-` tiers carry `v22.4.0` and are otherwise identical, picking up `v22.4.1` on the next pass[^dirk]. **Reported**.

## Thinking-effort controls

- Stock Qwen3.8-27B forces `reasoning_effort=xhigh` on every call; Dirk removes that default so the model runs at its native `medium` effort, the setting that injects no reasoning instruction in both the official and Unsloth templates (only `xhigh` and `low` add one)[^dirk]. **Reported**.
- Set effort per request through `chat_template_kwargs`, not the OpenAI-style top-level field, which the card says llama.cpp and oMLX drop[^dirk]. **Reported**:

```json
{"messages": [...], "chat_template_kwargs": {"reasoning_effort": "high"}}
```

- Levels are `low`, `medium`, `xhigh`; `high` is accepted as an alias for `xhigh`, not a step below it; omit the key for Dirk's lean default (`medium`); disable thinking entirely with `"enable_thinking": false`[^dirk]. **Reported**.

## Quant ladder and VRAM picks

Every file carries the Sharp template and MTP head and shares one `mmproj-F16.gguf` for vision[^dirk]. **Reported**.

| File | Size | Card guidance (**Reported**) |
| --- | --: | --- |
| `Dirk-Qwen3.8-27B-GSQ-RCO-IQ2_XS.gguf` | 8.8 GB | Smallest tier; 12 GB card pick with room for real context |
| `Dirk-Qwen3.8-27B-UD-Q2_K_XL.gguf` | 9.8 GB | 2-bit UD kept for continuity; prefer GSQ-RCO-IQ2_S below (smaller and better) |
| `Dirk-Qwen3.8-27B-GSQ-RCO-IQ2_S.gguf` | 9.6 GB | The 12 GB pick; 2-bit that still tracks the base model closely |
| `Dirk-Qwen3.8-27B-GSQ-RCO-IQ3_XXS.gguf` | 10.4 GB | Fits 16 GB with room; 12 GB card at shorter context |
| `Dirk-Qwen3.8-27B-GSQ-RCO-IQ3_S.gguf` | 12.1 GB | 3-bit near-base quality; value pick if 16 GB is the ceiling |
| `Dirk-Qwen3.8-27B-UD-Q3_K_XL.gguf` | 13.1 GB | 3-bit with headroom on 16 GB; prefer IQ4_XS below unless ~1 GB extra context is needed |
| `Dirk-Qwen3.8-27B-UD-IQ4_XS.gguf` | 14.3 GB | The 16 GB pick; 4-bit quality with room for real context where Q4_K_S leaves almost none |
| `Dirk-Qwen3.8-27B-UD-Q4_K_S.gguf` | 15.4 GB | Tight 4-bit; useful when Q4_K_XL will not fit alongside context |
| `Dirk-Qwen3.8-27B-UD-Q4_K_XL.gguf` | 17.6 GB | Start here; 24 GB-card default with best size/quality balance |
| `Dirk-Qwen3.8-27B-UD-Q5_K_XL.gguf` | 20.9 GB | Recommended 24 GB pick; dynamic plus imatrix-calibrated with room for context |
| `Dirk-Qwen3.8-27B-UD-Q6_K.gguf` | 22.0 GB | 6-bit; largest that still fits 24 GB with tighter headroom than UD-Q5_K_XL |
| `Dirk-Qwen3.8-27B-UD-Q6_K_XL.gguf` | 25.3 GB | Near-max quality; wants ~32 GB |
| `Dirk-Qwen3.8-27B-UD-Q8_K_L.gguf` | 28.0 GB | 8-bit near-lossless; fits 48 GB with room for 256K context, leaner than Q8_K_XL |
| `Dirk-Qwen3.8-27B-UD-Q8_K_XL.gguf` | 31.5 GB | 8-bit, effectively lossless |

## Why two quantizers

- At and above ~3 bpw the ladder uses Unsloth Dynamic 3.0 `UD` quants; below ~3 bpw it uses IST-DASLab GSQ-RCO quants, which the card says hold up substantially better at 2–3 bpw[^dirk]. **Reported**.
- GSQ learns each tensor's quantization grid through a Gumbel-Softmax relaxation instead of rounding to it, and RCO picks a per-tensor quantization type under an exact size budget by gradient descent on the task loss rather than a hand-tuned table[^dirk]. **Reported** method summary.
- At a matched 8.4 GB, ISTA measures GSQ-RCO well ahead of the equivalent UD file on wikitext perplexity and on AIME25, GPQA-Diamond, and LiveCodeBench v6; by ~3.5 bpw the two methods converge to within noise, which motivates the ~3 bpw switchover[^dirk]. **Reported** as ISTA's measurements, explicitly not the Dirk author's: the card states it re-templated ISTA's files without re-benchmarking them.
- Per the SCOPE benchmark rule, these comparisons state no hardware, engine version, workload shape, or metric definitions beyond the benchmark names, so they stay **Reported** with that limit.

## Running under llama.cpp

- Fetch by `:quant` tag from the file table (for example `:Q4_K_XL`, `:IQ4_XS`, `:Q6_K_XL`); the tag is required because the repo has no `Q4_K_M`, so a bare `-hf` without a tag falls back to the wrong file; the `mmproj` rides in the manifest so vision works from the same tag with no second download[^dirk]. **Reported**.
- llama.cpp applies the embedded Sharp template automatically with nothing to pass[^dirk]. **Reported**.

```bash
# text — auto-downloads to llama.cpp's own cache (24 GB-card default shown)
llama-server   -hf peculiar-ragdoll/Dirk-Qwen3.8-27B-GGUF:Q4_K_XL -ngl 99   # or llama-cli
# vision — same tag; the mmproj is pulled automatically
llama-mtmd-cli -hf peculiar-ragdoll/Dirk-Qwen3.8-27B-GGUF:Q4_K_XL -ngl 99 --image photo.jpg
```

```bash
hf download peculiar-ragdoll/Dirk-Qwen3.8-27B-GGUF Dirk-Qwen3.8-27B-UD-Q4_K_XL.gguf \
  mmproj-F16.gguf --local-dir Dirk
llama-cli      -m Dirk/Dirk-Qwen3.8-27B-UD-Q4_K_XL.gguf -ngl 99                              # text
llama-mtmd-cli -m Dirk/Dirk-Qwen3.8-27B-UD-Q4_K_XL.gguf --mmproj Dirk/mmproj-F16.gguf -ngl 99  # vision
```

- For coding-agent use, add `--reasoning-format deepseek` to `llama-server` so the `<think>` block returns in the OpenAI `reasoning_content` field instead of inline in `content`; the card notes current llama.cpp already defaults to this (`--reasoning-format auto` equals deepseek), making the flag a no-op on recent builds and insurance on older ones, and warns against `--reasoning-format none`, which leaves the tags inline[^dirk]. **Reported**.

## Template evidence cited by the card

- The template itself is presented as already measured: the identical terseness edit on the Dagger base (ThinkingCap-27B, same weights, only template swapped) moved Claw-Eval answer score 59.3 to 66.7 (+7.4), cut answer tokens 5393 to 2217 (−59%), and cut MMLU-Pro tokens per correct answer 1601 to 1248 (−22%)[^dirk]. **Reported** Dagger-base measurement, inherited by Dirk as an expectation rather than a Dirk-run result.
- Dirk's own headline figures appear only as benchmark-card image alt text: on 25 settled SWE-bench-Live tasks, Sharp Qwen3.8-27B (Dirk) and TielCoder (Sharp Ornith-1.5, 4-bit 35B-A3B MoE) ran against the stock template and cloud frontier Opus 5 (high) / Sonnet 5 (medium) — same weights, Sharp reaches a fix in 37% of stock's median time on the band both solve (2.7×) and out-solves Opus 5 (high) 15 to 14, one solve behind stock, median and mean per arm, judge-free; on the MMLU-Pro board across Qwen3.6-27B, Dagger, Dirk (medium), Qwen3.8-27B (medium), and Nail (35B-A3B MoE), Dirk tops accuracy at 85.3% while the MoE Nail is quickest to a correct answer at 43 s[^dirk]. **Reported** with image-uninspected and protocol-unstated limits; see Coverage limits.

## Arsenal positioning

The card positions Dirk against three siblings for task routing (**Reported** characterizations)[^dirk]:

- Nail (35B-A3B) generates tokens 3–4× faster than 27B models for routine coding, debugging, and knowledge work; reach for Nail on volume routine work it can handle.
- TielCoder (35B-A3B, rebuilt on Ornith-1.5 with the Sharp template) is the dedicated coder: 12 of 25 on SWE-bench-Live — level with Opus 4.6, four clear of Sonnet 5 (medium) — at the lowest mean time per attempt in the 35B-A3B family, paying in general knowledge (73.7 MMLU-Pro versus Nail's 84.0).
- Dagger (27B) is tuned to minimize thinking tokens at minimal accuracy cost, favoring speed-to-answer and multi-turn stamina under the context ceiling (100-turn sessions).
- Dirk (27B) is the pick for genuinely hard tasks wanting the strongest local answer without filler — accepting Nail's speed advantage inside its ability band and Dagger's marathon-session domain.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base; that page covers the official Unsloth GGUF/NVFP4 local path while Dirk is the Sharp-retemplated community GGUF alternative with its own VRAM ladder and `medium`-default effort control.
- Related to [Qwen3.8-27B Community Variants](qwen3.8-27b-community-variants.md) — another community packaging of the same 27B base alongside the Qwen-curated GGUF/MLX/AWQ/NVFP4 and DSpark/DFlash2 entries.
- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — the `UD-` tiers at and above ~3 bpw are instances of Unsloth Dynamic 3.0.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — every Dirk tier preserves the MTP head for multi-token-prediction speculative decoding at a stated ~1–2 GB extra-headroom planning figure documented there.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — Dirk is a llama.cpp-side local-inference artifact with `:quant`-tag fetching, `mmproj` vision, and `--reasoning-format deepseek` agent wiring.
- Related to [Qwen3.8-27B DSpark Speculator](qwen3.8-dspark.md) — server-side SGLang speculative path for the same 27B base, complementary to Dirk's client-side preserved-MTP-head approach.

## Coverage limits

- Entry point `../raw/Dirk-Qwen3.8-27B-GGUF.md` inspected statically (**Observed**); no commands executed, so run recipes and effort controls are **Reported**, not reproduced.
- Referenced local images (`assets/dirk_banner_eyebrow.png`, `assets/card_swe_sharp.png`, `assets/card_dirk_mmlu_live.png`) are absent from `raw/` — only their HTML alt text was available — so the SWE-bench-Live and MMLU-Pro headline figures rest on alt text alone with no visible axes, series, or protocol.
- External links uninspected: Sharp chat-template repo, Unsloth Dynamic 3.0 docs, IST-DASLab GSQ-RCO repo, GSQ/RCO arXiv papers, Dagger/Nail/TielCoder repos, Qwen/Unsloth/froggeric pages; GSQ-RCO quality deltas are explicitly ISTA's measurements reused secondhand.
- Per-benchmark hardware, engine versions, workload shapes, and metric definitions are unstated throughout, including the inherited Dagger Claw-Eval/MMLU-Pro token figures.

[^dirk]: Dirk-Qwen3.8-27B-GGUF model card — `../raw/Dirk-Qwen3.8-27B-GGUF.md` (peculiar-ragdoll; Apache-2.0; base `Qwen/Qwen3.8-27B`; frontmatter plus sections What it is / Proven on Nail and Dagger / Thinking effort / Run it / Pick your weapon / Credits): template-only change with Sharp v22.4.0/v22.4.1 and `terse:false` opt-out; stock-`xhigh` removal to native `medium` with `chat_template_kwargs` effort control (`low`/`medium`/`xhigh`, `high`→`xhigh`, `enable_thinking:false`) and dropped top-level field note; 14-file VRAM ladder (8.8–31.5 GB) with shared `mmproj-F16.gguf`; GSQ+Gumbel-Softmax/RCO+budgeted-gradient method summary with ~3 bpw switchover and matched-8.4 GB ISTA deltas (wikitext PPL, AIME25, GPQA-Diamond, LiveCodeBench v6) explicitly not re-benchmarked; `:quant`-tag llama.cpp fetch plus local `-m`/`--mmproj` commands and `--reasoning-format deepseek` agent note; Dagger-inherited Claw-Eval/MMLU-Pro token table and SWE-bench-Live/MMLU-Pro card alt-text figures (25-task 37%/2.7×, 15-vs-14 Opus 5, 85.3% Dirk accuracy, 43 s Nail); Nail/TielCoder/Dagger/Dirk routing characterizations; Qwen/Unsloth/IST-DASLab/froggeric credits.

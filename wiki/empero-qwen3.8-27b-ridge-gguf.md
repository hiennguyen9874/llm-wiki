---
type: Concept
title: Empero Qwen3.8-27B Ridge GGUF
description: Gated-DeltaNet-aware mixed GGUF of Qwen3.8-27B at 3.69 bpw with Q8_0 state path, Q6_K MTP head, measured perplexity, and llama.cpp serving guidance.
tags: [qwen3.8, gguf, quantization, llama-cpp, mtp, vision, local-inference, speculative-decoding, long-context]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T20:00:00Z }
stale_after: 2027-04-05
sources:
  - id: ridge
    resource: ../raw/Qwen3.8-27B-Ridge-GGUF.md
    title: Qwen3.8-27B-Ridge-3.7bpw model card
---

Empero ships a Gated-DeltaNet-aware mixed GGUF of `Qwen/Qwen3.8-27B` at **3.69 bpw / 11.73 GiB** that holds the GDN state path at Q8_0 with Q4_K mixers, keeps the native MTP draft head at Q6_K, and reports **7.82 ± 0.14** wiki-style perplexity (+9.3% vs its BF16 convert) with stock llama.cpp, Ollama, LM Studio, jan, and KoboldCpp compatibility[^ridge]. **Reported** by the model card throughout; no weights, commands, or benchmarks were executed here.

## Release identity

- Base is `Qwen/Qwen3.8-27B` at `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` with `base_model_relation: quantized`; frontmatter declares `license: apache-2.0`, `library_name: gguf`, `pipeline_tag: image-text-to-text`, languages `en`/`zh`, and tags for `gguf`, `llama.cpp`, `quantized`, `qwen3.8`, `ridge`, `gated-deltanet`, `imatrix`, `reasoning`, `multimodal`, `vision`, `mtp`, and `long-context`[^ridge]. **Reported**, with static frontmatter presence **Observed**.
- Publisher is the Hugging Face repo `empero-ai/Qwen3.8-27B-Ridge-GGUF`, developed by Empero; runtimes named are llama.cpp, Ollama, LM Studio, jan, and KoboldCpp; the capability writeup is explicitly out of scope and deferred to the official base-model card[^ridge]. **Reported**.
- Quantized weights inherit Apache-2.0 from the Qwen base and are shared as-is; acknowledgements name Empero, the Alibaba Qwen team for `Qwen3.8-27B`, and ggml-org for llama.cpp[^ridge]. **Reported**.

## Architecture

- 64 layers structured as 16 blocks of `(3 × GatedDeltaNet → FFN + 1 × GatedAttn → FFN)`; the card frames Qwen3.8 as a hybrid with three Gated-DeltaNet layers per full-attention layer[^ridge]. **Reported**.
- The native MTP draft head (`blk.64` / `nextn`) stays in the GGUF with nothing stripped to fit; vision is a separate BF16 `mmproj` file[^ridge]. **Reported**.
- Native context is **262,144** tokens, extensible to **1,000,000** with YaRN[^ridge]. **Reported**.

## Files and hardware guidance

Card file table[^ridge]. **Reported**.

| File | Quant | Size | Notes |
| --- | --- | ---:| --- |
| `Qwen3.8-27B-Ridge-3.7bpw.gguf` | Ridge mix, **3.69 bpw** | **11.73 GiB / 12.59 GB** | This release — text plus native MTP |
| `mmproj-Qwen3.8-27B-BF16.gguf` | BF16 | 0.87 GiB / 0.93 GB | Vision encoder plus projector; required for images |

- Text-only runs need just the Ridge GGUF; add the `mmproj` for image input[^ridge]. **Reported**.
- Weight-size-based guidance at modest context, explicitly not a VRAM benchmark and leaving room for runtime plus KV cache: Ridge-3.7bpw is the practical 16 GB starting point, 24 GB is comfortable once KV and optionally the `mmproj` are added, and image input adds ~1 GiB[^ridge]. **Reported**.
- The 262k native window and 1M YaRN extension make KV the dominant cost, which may need offload regardless of the 11.7 GiB weights; the card advises setting `-c` to what is actually needed because KV, not weights, blows up a 16–24 GB card at long context[^ridge]. **Reported**.
- One measured data point, not a sweep: fully offloaded on a single **RTX PRO 6000 Blackwell (96 GB)** at **~54 tok/s generation, ~130 tok/s prompt** (llama.cpp CUDA, `-ngl 99`, short smoke); the card still calls a 27B at 11.7 GiB comfortably interactive on a 16–24 GB card at modest context[^ridge]. **Reported**; per the SCOPE benchmark rule this stays **Reported** with unstated prompt/decode lengths, sampling, and variance (**Synthesis** on the rule application).

## Recipe and calibration

- Design claim: GDN state is disproportionately sensitive to low-bit quantization, so Ridge holds that path high and spends the saved bits by dropping mid-stack FFN; generic `IQ2_XS` and UD-IQ2 do not treat GDN state (`ssm_alpha` / `ssm_beta`) or the GDN mixers as first-class[^ridge]. **Reported**.
- Concrete mix: the Gated-DeltaNet state path is **Q8_0** and mixers are **Q4_K**, not IQ2 — stated as the difference between this file and a flat 2-bit dump of the same model[^ridge]. **Reported**.
- Built with llama.cpp `adb55e5` with CUDA and an importance matrix over 80 × 512-token chunks (`--process-output`, wikitext plus code)[^ridge]. **Reported**.
- MTP tensors are unused during calibration and have **no** imatrix, so IQ2/IQ3 on `blk.64` will abort and the draft head stays **Q6_K**[^ridge]. **Reported**.

## Measured perplexity

Same box, same calibration file, `llama-perplexity`, 80 chunks, `-c 512 -b 512`; BF16 is the author's own convert of the same official checkpoint[^ridge]. **Reported**.

| Candidate | Size | BPW | Wiki-style PPL | vs BF16 |
| --- | ---:| ---:| ---:| --- |
| BF16 GGUF (this convert) | 50.89 GiB | 16.00 | **7.15 ± 0.12** | — |
| **Ridge-3.7bpw** | **11.73 GiB** | **3.69** | **7.82 ± 0.14** | **+9.3%** |

- Per the quantization domain rule, this pairs the accuracy claim (wiki-style PPL with uncertainty) with its benchmark, baseline (own BF16 convert of `1d4bf0f2`), and format (3.69-bpw Ridge mix); harness beyond `llama-perplexity` settings and hardware for the PPL run are unstated, so it stays **Reported** (**Synthesis** on the rule application).

## Published-size comparison

Hugging Face file sizes as of 2026-08-15; PPL is filled only where the author measured the file[^ridge]. **Reported**.

| File | Publisher | Size | Nominal band | PPL vs this BF16 |
| --- | --- | ---:| --- | --- |
| BF16 | this convert | 50.89 GiB | 16 bpw | **7.15** |
| `UD-IQ2_XXS` | unsloth | 8.39 GiB | ~2.1 bpw | *not measured here* (Unsloth quotes 82.5% top-1 vs BF16) |
| `UD-IQ2_M` | unsloth | 9.61 GiB | ~2.4 bpw | *not measured* |
| `IQ2_XXS` | bartowski | 8.75 GiB | ~2.2 bpw | *not measured* |
| `Q3_K_S` | unsloth | 11.71 GiB | ~3.1 bpw | *not measured* |
| **Ridge-3.7bpw** | **empero-ai** | **11.73 GiB** | **3.69 bpw** | **7.82 (+9%)** |
| `IQ3_XXS` | bartowski | 11.76 GiB | ~2.9 bpw | *not measured* |
| `UD-Q3_K_XL` | unsloth | 12.52 GiB | ~3.4 bpw | *not measured* |

- The Unsloth 82.5% top-1 figure is secondhand inside this card and is preserved as an unmeasured publisher quote, not as firsthand evidence[^ridge]. **Reported** with that limit.

## Run recipes

**Reported** recipes, not reproduced here. Preserve the embedded Qwen3.8 chat template when the runtime asks[^ridge].

```bash
# thinking (default)
llama-cli \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  -ngl 99 -n 16384 \
  --temp 1.0 --top-p 0.95 --top-k 20 \
  -p "Explain the design tradeoffs in a Gated-DeltaNet hybrid model."

# instruct (thinking off)
llama-cli \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  -ngl 99 --reasoning off \
  --temp 0.7 --top-p 0.80 --top-k 20 --presence-penalty 1.5 \
  -p "Say hello in one short sentence."
```

```bash
llama-server \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  -c 16384 --port 8080
```

```bash
ollama run hf.co/empero-ai/Qwen3.8-27B-Ridge-GGUF
```

```
FROM ./Qwen3.8-27B-Ridge-3.7bpw.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER top_k 20
```

```bash
ollama create qwen38-ridge -f Modelfile
ollama run qwen38-ridge
```

- LM Studio / jan / KoboldCpp: download `Qwen3.8-27B-Ridge-3.7bpw.gguf` and load it[^ridge]. **Reported**.

### MTP draft speculation

The Ridge GGUF keeps the native MTP head; it needs a recent llama.cpp build supporting `--spec-type draft-mtp`, otherwise the file still runs as a normal 27B without the draft speedup[^ridge]. **Reported**.

```bash
llama-server \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  --spec-type draft-mtp \
  --spec-draft-n-max 6 \
  -c 16384 --port 8080
```

### Vision

Download the text GGUF plus `mmproj-Qwen3.8-27B-BF16.gguf`[^ridge]. **Reported**.

```bash
llama-mtmd-cli \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  --mmproj mmproj-Qwen3.8-27B-BF16.gguf \
  --image ./photo.jpg \
  -p "Describe this image in detail." \
  --temp 0.7 --top-p 0.80 --top-k 20 \
  -c 16384
```

```bash
llama-server \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  --mmproj mmproj-Qwen3.8-27B-BF16.gguf \
  -c 16384 --port 8080
```

## Sampling and thinking controls

- Qwen3.8 is a hybrid thinking model: responses open with a `<think>…</think>` block unless thinking is disabled[^ridge]. **Reported**.

| Mode | temperature | top_p | top_k | presence_penalty |
| --- | --- | --- | --- | --- |
| Thinking (default) | 1.0 | 0.95 | 20 | 0.0 |
| Instruct (thinking off) | 0.7 | 0.80 | 20 | 1.5 |

- Sampling values come from the official Qwen3.8 card as restated here; use the runtime chat/completions path rather than hand-rolling a prompt format, with the embedded template including tool-use (`<tool_call>…</tool_call>`)[^ridge]. **Reported**.

## Limitations

- Not lossless: +9% wiki-style PPL versus the author's BF16 convert[^ridge]. **Reported**.
- Context costs memory: weight size is only part of the hardware budget[^ridge]. **Reported**.
- MTP is runtime-dependent: the head is in the file but the speedup needs a runtime that knows `draft-mtp`[^ridge]. **Reported**.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base; that page covers the Unsloth GGUF/NVFP4 local path while this is the Empero GDN-aware 3.69-bpw alternative with its own Q8_0-state recipe and BF16 vision projector[^ridge].
- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — the UD-IQ2/Q3 rows in the comparison table are the size-band alternative against which Ridge positions its GDN-state protection at matched ~11.7 GB[^ridge].
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — the retained `blk.64`/`nextn` Q6_K head with `--spec-type draft-mtp` draft speculation shares the native-MTP serving shape documented there[^ridge].
- Uses [Speculative Decoding Foundations](speculative-decoding-foundations.md) — draft-verify-accept mechanism behind the `draft-mtp` `--spec-draft-n-max 6` configuration named here[^ridge].
- Related to [ISTA-DASLab Qwen3.8-27B GSQ-RCO GGUF](ista-qwen3.8-27b-gsq-rco-gguf.md) — non-uniform GGUF source for the same base with its own per-tensor precision allocation, MTP builds, and BF16 projector[^ridge].
- Related to [Cdiamond Qwen3.8-27B iMatrix NVFP4 MTP GGUF](cdiamond-qwen3.8-27b-imatrix-nvfp4-mtp-gguf.md) — iMatrix-guided hybrid NVFP4 GGUF of the same base at 5.01 bpw with embedded MTP and a 24 GB 256K profile, contrasting with this 3.69-bpw GDN-state-first mix[^ridge].

## Coverage limits

- Entry point `../raw/Qwen3.8-27B-Ridge-GGUF.md` inspected statically (**Observed**); no commands executed, so install/run recipes and tok/s plus PPL figures are **Reported**, not reproduced.
- Linked artifacts uninspected: Ridge and `mmproj` GGUF bytes, author's BF16 convert, official `Qwen/Qwen3.8-27B` checkpoint at `1d4bf0f2`, llama.cpp build `adb55e5`, 80×512-token wikitext-plus-code calibration file and `--process-output` run, Unsloth and bartowski comparison files, and the official base-model capability card.
- Donation addresses and newsletter signup were excluded as non-durable solicitation; no sensitive values appear in this concept.
- No eval harness beyond the stated `llama-perplexity` settings, no PPL-run hardware, and no MTP speedup measurement appear in the card; MTP and throughput claims therefore stay **Reported** under the SCOPE benchmark rule.

[^ridge]: Qwen3.8-27B-Ridge-3.7bpw model card — `../raw/Qwen3.8-27B-Ridge-GGUF.md` (Empero / `empero-ai/Qwen3.8-27B-Ridge-GGUF`; Apache-2.0; base `Qwen/Qwen3.8-27B` @ `1d4bf0f2`; frontmatter plus sections Files / What fits on a GPU? / Recipe / Measured / Comparison / Quick start incl. llama.cpp, llama-server, Ollama, LM Studio/jan/KoboldCpp, MTP draft speculation / Vision / Sampling / Long context / Limitations / Provenance): 64-layer 16×(3×GDN→FFN + 1×GatedAttn→FFN) hybrid with retained `blk.64`/`nextn` MTP head and separate BF16 `mmproj`; 11.73 GiB / 3.69-bpw Ridge file plus 0.87 GiB projector with 16 GB practical / 24 GB comfortable weight-size guidance and KV-dominance warning; Q8_0 GDN state plus Q4_K mixers vs flat 2-bit, llama.cpp `adb55e5` CUDA build, 80×512-token wikitext-plus-code imatrix, MTP-no-imatrix Q6_K abort note; `llama-perplexity` 80-chunk `-c 512 -b 512` PPL 7.82 ± 0.14 vs own-BF16 7.15 ± 0.12 (+9.3%); 2026-08-15 eight-row HF size table with unmeasured Unsloth/bartowski rows and secondhand 82.5% top-1 quote; thinking/instruct sampling split with `<think>` and `<tool_call>` template notes, 262,144 / 1M-YaRN context, and not-lossless plus runtime-dependent-MTP limits.

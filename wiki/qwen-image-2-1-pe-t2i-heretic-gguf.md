---
type: Concept
title: Qwen-Image-2.1 PE-T2I Rewriter (Heretic GGUF)
description: Community refusal-ablated GGUF packaging of the Qwen-Image-2.1 PE-T2I text-to-image prompt rewriter with a Q6_K embedding deviation and llama.cpp use.
tags: [qwen, prompt-rewriting, gguf, llama-cpp, ablation, image-generation]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T08:00:00Z }
sources:
  - id: pe-t2i-heretic-gguf-readme
    resource: ../raw/Qwen-Image-2.1-PE-T2I-Heretic-GGUF/README.md
    scope: ../raw/Qwen-Image-2.1-PE-T2I-Heretic-GGUF/
    kind: documentation
    title: Qwen-Image-2.1-PE-T2I Heretic GGUF README
---

Qwen-Image-2.1 PE-T2I Rewriter (Heretic GGUF) is a community llama.cpp packaging of the Qwen-Image-2.1 text-to-image prompt rewriter, turning a short request in any language into one JSON line with a detailed English image prompt plus recommended aspect ratio, with refusal behaviour reduced by Heretic directional ablation.[^pe-t2i-heretic-gguf-readme]

## Identity and provenance

- **Observed** base and disclaimer: Q4_K_M build of `pottokao/Qwen-Image-2.1-PE-T2I-Heretic`, itself a community derivative of `Qwen/Qwen-Image-2.1-PE-T2I`; not affiliated with or endorsed by Alibaba / Qwen.[^pe-t2i-heretic-gguf-readme]
- **Observed** license boundary: frontmatter declares `qwen-research`; body states redistribution under the Qwen Research License with included `LICENSE` copy per §3.a, non-commercial use only, with commercial use requiring a separate Qwen licence.[^pe-t2i-heretic-gguf-readme]
- **Observed** task tags: frontmatter `tags` include `gguf`, `quantized`, `llama-cpp`, `heretic`, `abliterated`, `prompt-rewriting`, `qwen-image`, and `comfyui`.[^pe-t2i-heretic-gguf-readme]
- **Reported** model role: an LLM prompt rewriter, not a text encoder — in ComfyUI it belongs in an LLM/GGUF node that rewrites the prompt before it reaches the DiT, and it does not load into `CLIPLoader`.[^pe-t2i-heretic-gguf-readme]

## Input-output contract

- **Reported** shape: one JSON line out per short multilingual request in:[^pe-t2i-heretic-gguf-readme]

```json
{"rewritten_prompt": "...", "wh_ratio": "3:2"}
```

- **Reported** required contract file: `system_prompt.txt` is included and the model is described as useless without it; that 10 KB document defines output structure, register, length, and JSON shape, and is loaded as the system message.[^pe-t2i-heretic-gguf-readme]

## Ablation result

- **Reported** shipped point: refusal behaviour removed from 98/100 down to 3/100 refusals at KL 0.036 — best of a 1,600-trial search, dominating the earlier 7/100 at 0.039 point tagged `v1-trial384`.[^pe-t2i-heretic-gguf-readme]

## File options

- **Reported** GGUF builds, all loading the same way (`llama-server -m <file>`), picked by available VRAM:[^pe-t2i-heretic-gguf-readme]

| File | Size | Notes |
|---|---:|---|
| `pe_t2i_heretic-Q4_K_M.gguf` | 5.49 GB | smallest; `token_embd` kept at Q6_K |
| `pe_t2i_heretic-Q6_K.gguf` | 7.61 GB | higher quality; `token_embd` kept at Q8_0 |
| `pe_t2i_heretic-Q8_0.gguf` | 9.53 GB | near-lossless |

## Quantization deviation

- **Observed** deviation from stock Q4_K_M: `token_embd` kept at Q6_K instead of Q4_K; everything else is standard Q4_K_M, with `output` at Q6_K as llama.cpp already promotes it.[^pe-t2i-heretic-gguf-readme]
- **Reported** size effect: `token_embd` 0.53 GB at Q4_K versus 0.78 GB at Q6_K, raising the total from 5.24 GB to 5.49 GB (+0.25 GB), described as unable to be worse than leaving it at Q4_K.[^pe-t2i-heretic-gguf-readme]
- **Reported** rationale: every official NVIDIA NVFP4 checkpoint for this model family leaves the token embedding untouched — across `Qwen3-8B`, `Qwen3-32B`, `Qwen3-30B-A3B`, `Qwen3.5-122B-A10B`, and `Qwen3.5-397B-A17B` — as does the one official mixed-precision recipe (`Qwen3.6-27B`), which quantizes `lm_head` to 4-bit but still does not touch the embedding, while stock Q4_K_M compresses it.[^pe-t2i-heretic-gguf-readme]

## Usage in llama.cpp

- **Reported** server invocation; loads in a few seconds and fits on an 8 GB card:[^pe-t2i-heretic-gguf-readme]

```bash
llama-server -m pe_t2i_heretic-Q4_K_M.gguf --host 0.0.0.0 --port 8080 \
             -ngl 99 -c 16384 --jinja -a pe-t2i
```

- **Reported** request shape: POST to `/v1/chat/completions` with `system_prompt.txt` as the system message.[^pe-t2i-heretic-gguf-readme]
- **Reported** related tooling: sample and showcase images were generated with the technique behind the `ComfyUI-QwenImage-PhotoStyles` node (17 photographic styles; one short prompt becomes a full styled prompt via the PE-T2I rewriter).[^pe-t2i-heretic-gguf-readme]

## Conversion

- **Reported** conversion commands:[^pe-t2i-heretic-gguf-readme]

```bash
python convert_hf_to_gguf.py <bf16 model> --outfile pe_bf16.gguf --outtype bf16 --no-mtp
llama-quantize --token-embedding-type q6_K --output-tensor-type q6_K \
               pe_bf16.gguf pe_t2i_heretic-Q4_K_M.gguf Q4_K_M
```

- **Reported** `--no-mtp` requirement: this model's `config.json` carries `text_config.mtp_num_hidden_layers` with value `null`; without the flag the converter does `int += None` and dies with a `TypeError`, and the trap is that the key existing with a null value means `.get(key, 0)` returns `None`, not the default.[^pe-t2i-heretic-gguf-readme]

## Verification and limits

- **Reported** functional check: four requests (three Chinese, one English) through `llama-server` produced 4/4 strictly valid JSON with exactly the `rewritten_prompt` / `wh_ratio` keys at 2053–3351 characters, against 2450–3320 from the bf16 source on the same style of input, so length discipline is described as surviving quantization.[^pe-t2i-heretic-gguf-readme]
- **Reported** negative result: a perplexity comparison was attempted but is not reported because it returned self-contradictory numbers (the unquantized bf16 GGUF scored worse than its own quantizations, which is not physically sensible); only the functional check above is offered as evidence.[^pe-t2i-heretic-gguf-readme]
- **Reported** tried and not shipped: an importance-matrix build passed the same functional check but was withheld because the calibration corpus was badly designed — the 10 KB system prompt appears in every sample, so about 88% of the 341 KB corpus was one repeated document that would dominate importance statistics; a properly diversified corpus is the stated way to revisit it.[^pe-t2i-heretic-gguf-readme]

## Pipeline and format context

- **Reported** all-Q4_K_M showcase pipeline: this PE-T2I rewriter plus the Heretic Qwen3-VL text encoder (`qwen3vl_8b_heretic-Q4_K_M.gguf` with f16 mmproj), the DiT (`qwen_image_2.1-Q4_K_M.gguf`), and the official `qwen_image_2.1_vae_bf16.safetensors`.[^pe-t2i-heretic-gguf-readme]
- **Observed** other builds of the same ablated rewriter outside this repo: bf16 safetensors for `transformers` and NVFP4 mixed precision for vLLM.[^pe-t2i-heretic-gguf-readme]
- **Observed** showcase scope: two remote-linked photographic-style galleries plus a local-asset pipeline gallery, each generated from one-line prompts with one seed per cell and no retouching; image contents are decorative and not compiled here.[^pe-t2i-heretic-gguf-readme]

## Relationships

- Rewrites text-to-image prompts for [Qwen-Image-2.1 Text-to-Image and Editing Model](qwen-image-2-1.md); this concept records only the Heretic GGUF rewriter packaging, not the base generation behaviour.
- Complements [Qwen-Image-2.1 PE-I2I Rewriter (Heretic GGUF)](qwen-image-2-1-pe-i2i-heretic-gguf.md), the sibling refusal-ablated GGUF rewriter for image editing; PE-T2I handles short multilingual text-to-image requests while PE-I2I handles editing instructions plus input images.
- Upstream of [Qwen-Image-2.1 Text Encoder (Heretic)](qwen-image-2-1-text-encoder-heretic.md) in the documented all-GGUF pipeline: rewritten prompts feed that refusal-ablated Qwen3-VL encoder via `CLIPLoaderGGUF` plus patch, then the DiT and official VAE.
- For the Qwen-Image-2.1 text encoder itself (distinct from this LLM rewriter), see the text-encoder page; for the *text encoder* Heretic GGUF variant, that page is authoritative, not this one.

## Coverage limits

- **Observed:** only `../raw/Qwen-Image-2.1-PE-T2I-Heretic-GGUF/README.md` was statically inspected; no GGUF, `system_prompt.txt`, `LICENSE`, bf16 source, NVFP4 build, ComfyUI node, or showcase image was downloaded, and no server launch, inference, quantization-size, refusal, or KL claim was executed or reproduced.
- **Observed:** uninspected or unavailable material includes all three listed GGUF files, `system_prompt.txt`, `LICENSE`, the upstream `Qwen/Qwen-Image-2.1-PE-T2I` and `pottokao/Qwen-Image-2.1-PE-T2I-Heretic` sources, the linked NVFP4 and bf16 repos, the text-encoder/DiT/VAE pipeline targets, the PhotoStyles node repo, and all remote and local showcase images.
- No immutable revision or snapshot date is present in the capture; future weight or card updates would be a new revision.

[^pe-t2i-heretic-gguf-readme]: Model-card README capture in `../raw/Qwen-Image-2.1-PE-T2I-Heretic-GGUF/README.md`; community-derivative disclaimer, Qwen Research non-commercial terms, Heretic 3/100 at KL 0.036 from 98/100 over 1,600 trials, and frontmatter tags from header; JSON `rewritten_prompt`/`wh_ratio` shape, LLM-not-text-encoder role, and 10 KB `system_prompt.txt` requirement from What-this-is-for and header sections; Q4_K_M/Q6_K/Q8_0 sizes and shared `llama-server` loading from Available-quantizations; `token_embd` Q6_K deviation, size table, and NVIDIA NVFP4/Qwen3-family rationale from One-deviation section; server command, chat-completions use, 8 GB fit, and PhotoStyles node from Run-it and Made-with sections; conversion commands and null-`mtp_num_hidden_layers` trap from Conversion; 4/4 functional JSON check, withheld perplexity, and withheld imatrix corpus flaw from What-was-checked section; all-Q4 pipeline, bf16/NVFP4 builds, and showcase basis from Showcase and Other-builds sections.

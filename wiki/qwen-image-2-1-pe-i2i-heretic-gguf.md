---
type: Concept
title: Qwen-Image-2.1 PE-I2I Rewriter (Heretic GGUF)
description: Community refusal-ablated GGUF packaging of the Qwen-Image-2.1 PE-I2I image-editing prompt rewriter with multimodal llama.cpp use and low-damage ablation point.
tags: [qwen, image-editing, prompt-rewriting, gguf, llama-cpp, ablation, multimodal]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T07:00:00Z }
sources:
  - id: pe-i2i-heretic-gguf-readme
    resource: ../raw/Qwen-Image-2.1-PE-I2I-Heretic-GGUF/README.md
    scope: ../raw/Qwen-Image-2.1-PE-I2I-Heretic-GGUF/
    kind: documentation
    title: Qwen-Image-2.1-PE-I2I Heretic GGUF README
---

Qwen-Image-2.1 PE-I2I Rewriter (Heretic GGUF) is a community llama.cpp packaging of the Qwen-Image-2.1 image-editing prompt rewriter, a fine-tuned Qwen3.5-VL 9B model that turns a vague editing instruction plus input images into a precise actionable editing prompt, with refusal behaviour reduced by Heretic directional ablation.[^pe-i2i-heretic-gguf-readme]

## Identity and provenance

- **Observed** base and disclaimer: community derivative of `Qwen/Qwen-Image-2.1-PE-I2I`, not affiliated with or endorsed by Alibaba / Qwen.[^pe-i2i-heretic-gguf-readme]
- **Reported** model role: fine-tuned Qwen3.5-VL 9B image-editing prompt rewriter, distinct from the Qwen-Image-2.1 diffusion model and its Qwen3-VL text encoder.[^pe-i2i-heretic-gguf-readme]
- **Observed** license boundary: frontmatter declares `qwen-research`; body states redistribution under the Qwen Research License with included `LICENSE` copy, non-commercial use only, with commercial use requiring a separate Qwen licence.[^pe-i2i-heretic-gguf-readme]
- **Observed** task tags: frontmatter `tags` include `heretic`, `abliterated`, `prompt-rewriting`, `image-editing`, `qwen-image`, `gguf`, `llama-cpp`, and `multimodal`.[^pe-i2i-heretic-gguf-readme]

## File options

- **Reported** language-model GGUF builds:[^pe-i2i-heretic-gguf-readme]

| File | Size | Notes |
|---|---:|---|
| `pe_i2i_heretic-Q4_K_M.gguf` | 5.89 GB | token-embedding plus output tensors kept at Q6_K |
| `pe_i2i_heretic-Q6_K.gguf` | 7.61 GB | token-embedding kept at Q8_0 |
| `pe_i2i_heretic-Q8_0.gguf` | 9.53 GB | near-lossless |

- **Reported** vision projector: `pe_i2i_heretic.mmproj-bf16.gguf` in bf16; the build is fully multimodal and supports text-only and image-plus-text editing.[^pe-i2i-heretic-gguf-readme]
- **Reported** vision tower unchanged by ablation: the mmproj is the original vision encoder, with only the language-model refusal direction ablated.[^pe-i2i-heretic-gguf-readme]
- **Reported** required contract file: `system_prompt.txt` is an 18 KB document defining output structure, register, length, and JSON shape; the model is described as useless without it.[^pe-i2i-heretic-gguf-readme]

## Usage in llama.cpp

- **Reported** server invocation:[^pe-i2i-heretic-gguf-readme]

```bash
llama-server -m pe_i2i_heretic-Q4_K_M.gguf \
             --mmproj pe_i2i_heretic.mmproj-bf16.gguf \
             -c 16384 --jinja
```

- **Reported** request shape: send `system_prompt.txt` contents as the system message, pass input images as `image_url` in the user turn, and allow enough `max_tokens` because the model reasons in a `<think>` block before the JSON — 4k–6k is stated as safe.[^pe-i2i-heretic-gguf-readme]

## Ablation trade-off

- **Reported** search: refusals measured with the Heretic harness over a distributed redis-shared Optuna search of about 1,900 trials, producing a monotonic Pareto front where each removed refusal costs KL divergence.[^pe-i2i-heretic-gguf-readme]
- **Reported** operating points:[^pe-i2i-heretic-gguf-readme]

| Refusals | KL damage |
|---:|---:|
| 1/100 | 0.107 |
| 2/100 | 0.058 |
| ~5/100 | ~0.037 |
| 10/100 | 0.036 |
| 19/100 | 0.028 |
| 32/100 | 0.015 |
| 98/100 | 0 |

- **Reported** shipped point: this repo uses the low-damage balanced point at about 5/100 refusals and KL about 0.037, removing most refusals while keeping rewriting quality loss low; for this structured rewriter, KL cost is described as length discipline, JSON compliance, and spatial-description ability.[^pe-i2i-heretic-gguf-readme]
- **Reported** statistics caveat: refusal counts use n = 100, so small differences are within binomial noise, while KL is continuous and more reliable for comparing points.[^pe-i2i-heretic-gguf-readme]

## Cross-modal verification

- **Reported** test design: editing requests spanning sensitive content categories were issued two ways — as text-only instructions and as image-plus-instruction on real input images — against the original base and this build.[^pe-i2i-heretic-gguf-readme]
- **Reported** base behaviour: on image-plus-sensitive-edit inputs the original base does not hard-refuse but produces a well-formed JSON rewrite whose content declines or sanitizes the request, for example keeping the input unchanged or leaving the subject clothed.[^pe-i2i-heretic-gguf-readme]
- **Reported** result: the original base complies on mild text-only requests and refuses stronger ones, while this build complies across the tested text-only categories; on image-plus-instruction cases the base quietly preserves or sanitizes the input while this build carries out the requested edit.[^pe-i2i-heretic-gguf-readme]
- **Reported** quality preservation: on neutral edits this build matches the base in rewrite length, retained-detail lists, and in-image text preservation.[^pe-i2i-heretic-gguf-readme]

## Relationships

- Rewrites editing prompts for [Qwen-Image-2.1 Text-to-Image and Editing Model](qwen-image-2-1.md); this concept records only the Heretic GGUF rewriter packaging, not the base generation behaviour.
- Complements [Qwen-Image-2.1 Text Encoder (Heretic)](qwen-image-2-1-text-encoder-heretic.md), which covers the refusal-ablated Qwen3-VL encoder used downstream of prompt rewriting; that encoder page already describes PE-I2I as turning vague edit instructions plus input images into precise editing prompts.
- Complements [Qwen-Image-2.1 PE-T2I Rewriter (Heretic GGUF)](qwen-image-2-1-pe-t2i-heretic-gguf.md), the sibling refusal-ablated GGUF rewriter for text-to-image requests; PE-I2I handles editing instructions plus input images while PE-T2I handles short multilingual text-to-image requests.
- Runs under llama.cpp rather than ComfyUI GGUF loader paths; it is an LLM rewriter used before the diffusion pipeline, not a text-encoder weight loaded into `CLIPLoader`.

## Coverage limits

- **Observed:** only `../raw/Qwen-Image-2.1-PE-I2I-Heretic-GGUF/README.md` was statically inspected; no GGUF, mmproj, `system_prompt.txt`, or `LICENSE` file was present in the capture and no server launch, inference, editing, quantization-size, refusal, or KL claim was executed or reproduced.
- **Observed:** uninspected or unavailable material includes all four listed weight files, `system_prompt.txt`, `LICENSE`, the upstream `Qwen/Qwen-Image-2.1-PE-I2I` source, and the linked Heretic harness repository.
- No immutable revision or snapshot date is present in the capture; future weight or card updates would be a new revision.

[^pe-i2i-heretic-gguf-readme]: Model-card README capture in `../raw/Qwen-Image-2.1-PE-I2I-Heretic-GGUF/README.md`; Qwen3.5-VL 9B rewriter identity, community-derivative disclaimer, and Qwen Research non-commercial terms from header; Q4_K_M/Q6_K/Q8_0 sizes, bf16 mmproj, untouched vision tower, and 18 KB `system_prompt.txt` requirement from Files section; `llama-server`, `--mmproj`, `-c 16384`, `--jinja`, system message, `image_url`, `<think>` block, and 4k–6k token guidance from Usage section; ~1,900-trial redis-shared Optuna search, Pareto table, shipped ~5/100 at KL ~0.037, and n = 100 caveat from Ablation trade-off section; text-only versus image-plus-instruction test, soft-refusal finding, and neutral-edit quality parity from Cross-modal verification section; frontmatter tags and `base_model` from file header.

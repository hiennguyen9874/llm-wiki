---
license: other
license_name: qwen-research
license_link: LICENSE
base_model:
- Qwen/Qwen-Image-2.1-PE-I2I
tags:
- heretic
- abliterated
- prompt-rewriting
- image-editing
- qwen-image
- gguf
- llama-cpp
- multimodal
---

# Qwen-Image-2.1-PE-I2I — Heretic — GGUF (+ mmproj)

> **Not affiliated with, or endorsed by, Alibaba / Qwen.** Community derivative of
> [`Qwen/Qwen-Image-2.1-PE-I2I`](https://huggingface.co/Qwen/Qwen-Image-2.1-PE-I2I),
> redistributed under the **Qwen Research License** (copy included as `LICENSE`, per §3.a).
> **Non-commercial use only** (§1.i / §2.a); commercial use needs a separate licence from Qwen.

The **image-editing prompt rewriter** for Qwen-Image-2.1 — a fine-tuned Qwen3.5-VL 9B that
takes a vague editing instruction plus one or more input images and rewrites it into a
precise, actionable editing prompt — with refusal behaviour reduced via
[Heretic](https://github.com/p-e-w/heretic) directional ablation.

This repo is the **llama.cpp build** and is **fully multimodal** — it ships both the language
model GGUF and the vision projector, so it works for **text-only and image+text** editing.

## Files

| File | What |
|---|---|
| `pe_i2i_heretic-Q4_K_M.gguf` | language model, Q4_K_M (token-embedding + output tensors kept at Q6_K) — 5.89 GB |
| `pe_i2i_heretic-Q6_K.gguf` | language model, Q6_K (token-embedding kept at Q8_0) — 7.61 GB |
| `pe_i2i_heretic-Q8_0.gguf` | language model, Q8_0, near-lossless — 9.53 GB |
| `pe_i2i_heretic.mmproj-bf16.gguf` | vision projector (mmproj), bf16 |

> The vision tower was **not touched** by the ablation, so the mmproj is bit-for-bit the
> original vision encoder — only the language model's refusal direction was ablated.

> **`system_prompt.txt` is included and the model is useless without it** — it is an 18 KB
> document that defines the entire output contract (structure, register, length, JSON shape).

## Usage (llama.cpp)

```bash
llama-server -m pe_i2i_heretic-Q4_K_M.gguf \
             --mmproj pe_i2i_heretic.mmproj-bf16.gguf \
             -c 16384 --jinja
```

Send the contents of `system_prompt.txt` as the system message, and pass the input image(s)
as `image_url` in the user turn. Give it enough `max_tokens` (the model reasons in a
`<think>` block before the JSON — 4k–6k is safe).

## Ablation trade-off

Refusals were measured with the [Heretic](https://github.com/p-e-w/heretic) harness over a
**distributed (redis-shared Optuna) search of ~1,900 trials**, producing a **monotonic
Pareto front** — every refusal you remove costs KL divergence, which for a *structured*
rewriter is exactly the length discipline, JSON compliance and spatial-description ability
you are paying for:

| Refusals | KL (damage) | |
|---:|---:|---|
| 1/100 | 0.107 | strongest ablation, most damage |
| 2/100 | 0.058 | stronger alternative build |
| **~5/100** | **~0.037** | **this repo — the low-damage balanced point** |
| 10/100 | 0.036 | |
| 19/100 | 0.028 | |
| 32/100 | 0.015 | |
| 98/100 | 0 | the original |

This repo ships the **low-damage balanced point** (≈5/100 refusals at KL ≈ 0.037): most of
the refusals removed, while keeping KL — and therefore the rewriting quality — low.

### A statistics caveat, stated plainly

Refusals are on **n = 100**; a few refusals' difference is within binomial noise. KL is a
continuous measure and far more reliable for comparing points.

## Cross-modal verification — de-censoring is real on **both** channels

An abliteration guided only by a **text** refusal set could, in principle, leave the
**vision** channel untouched. So this build was checked on both channels, against the
original base, rather than trusting the refusal number alone.

**Test:** NSFW editing requests across several content categories (nudity, explicit acts,
gore/violence, restraint), issued **two ways** — as *text-only* editing instructions, and as
*image + instruction* on real input images.

**Finding — the base model's refusal here is a "soft refusal":** given an image + an NSFW
edit, the original base does **not** hard-refuse; it emits a well-formed JSON rewrite whose
*content* quietly declines — "the instruction cannot be executed, the input is kept
unchanged", or a sanitized version that leaves the subject clothed. The refusal hides
inside a valid-looking output.

**Result:**

| Channel | Original base | This build (Heretic) |
|---|---|---|
| Text-only NSFW instruction | complies on mild, refuses stronger | **complies (8/8 categories)** |
| **Image + NSFW instruction** | **soft-refuses / sanitizes** | **executes the edit faithfully** |

So the de-censoring is **genuinely reached on the text channel *and* the vision channel** —
not merely on the benchmark refusal metric. On image edits the base would quietly keep the
subject unchanged; this build carries out the requested edit while preserving the model's
normal quality (on neutral edits its rewrites match the base in length, retained-detail lists
and in-image text preservation).

## License

Qwen Research License — see `LICENSE`. Non-commercial use only.
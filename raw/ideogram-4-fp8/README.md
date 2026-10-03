---
license: other
license_name: ideogram-4-non-commercial
license_link: https://huggingface.co/ideogram-ai/ideogram-4-fp8/blob/main/LICENSE.md
pipeline_tag: text-to-image
tags:
  - text-to-image
  - image-generation
  - diffusion
  - flow-matching
  - dit
  - ideogram
---

<p align="center"><a href="https://ideogram.ai/" target="_blank" rel="noopener noreferrer"><img src="https://raw.githubusercontent.com/ideogram-oss/ideogram4/main/assets/ideogram_logo.svg" alt="Ideogram" width="500"></a></p>

<p align="center"><em>Ideogram 4: Open image model at the forefront of design</em></p>

<p align="center">
  <a href="https://ideogram.ai/blog/ideogram-4.0/" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/Blog-Post-orange" alt="Blog Post"></a>
  <a href="https://github.com/ideogram-oss/ideogram4" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/Code-GitHub-181717?logo=github" alt="Code"></a>
  <a href="https://huggingface.co/collections/ideogram-ai/ideogram-4" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/Model-HuggingFace-blue?logo=huggingface" alt="Model"></a>
  <a href="https://developer.ideogram.ai/" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/API-developer.ideogram.ai-purple" alt="API"></a>
  <a href="https://ideogram.ai/" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/Official%20Site-ideogram.ai-ff69b4" alt="Official Site"></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/ideogram-oss/ideogram4/main/assets/samples/collage_landscape.jpg" alt="A collage of Ideogram 4 samples spanning photorealism, illustration, typography, and poster design">
</p>


Ideogram 4 is **[Ideogram](https://ideogram.ai)'s first open weight text-to-image model**. It is a **state-of-the-art foundation model trained from scratch** — not a fine-tune of any existing model. It introduces a new structured JSON prompting interface, with best-in-class multilingual text rendering, deep language understanding, explicit bounding-box layout and color-palette controls, and native 2k resolution images. The easiest way to try the model is online at **[ideogram.ai](https://ideogram.ai/)**.

We believe openness drives innovation, and we invite the research community to innovate with us on the forefront of visual intelligence.

## Table of Contents

1. [News](#news)
2. [Model Zoo](#model-zoo)
3. [Performance](#performance)
4. [Quick Start](#quick-start)
5. [Model Summary](#model-summary)
6. [Prompting Guide](#prompting-guide)
7. [Documentation](#documentation)
8. [Citation](#citation)

## News

* **[2026-06-03]** **Ideogram 4 released!** Inference code and weights
  are now public, and our [technical blog post](https://ideogram.ai/blog/ideogram-4.0/) is live. See the
  [Quick Start](#quick-start) section to generate your first image, or try the
  model online at [ideogram.ai](https://ideogram.ai/).

## Model Zoo

| Model | Params | Weight Quantization | Supported Hardware | Diffusers Support | License |
| :---  | :---:  | :---:        | :---:   | :---:   | :---:   |
| **[Ideogram 4 (nf4)](https://huggingface.co/ideogram-ai/ideogram-4-nf4)** | 9.3B | nf4 | CUDA | Yes | [Ideogram 4 Non-Commercial](https://huggingface.co/ideogram-ai/ideogram-4-nf4/blob/main/LICENSE.md) |
| **[Ideogram 4 (fp8)](https://huggingface.co/ideogram-ai/ideogram-4-fp8)** | 9.3B | fp8 | All | No | [Ideogram 4 Non-Commercial](https://huggingface.co/ideogram-ai/ideogram-4-fp8/blob/main/LICENSE.md) |

We plan to support more quantizations in the future.


## Performance

We evaluate Ideogram 4 across third-party arenas and benchmarks, standard
open-source benchmarks, and our own internal human-preference benchmark. Across
all of them, **Ideogram 4 is the best open-weight image model by far, and sits
at the frontier of design.**

### Design Arena

[Design Arena](https://www.designarena.ai/) is a third-party image Elo
leaderboard focused specifically on design-oriented generation. On the overall
board, Ideogram 4 is the top-ranked open-weight model, trailing only proprietary
GPT and Gemini models:

<p align="center">
  <img src="https://raw.githubusercontent.com/ideogram-oss/ideogram4/main/assets/benchmarks/design_arena.png" alt="Design Arena overall image Elo leaderboard with Ideogram 4.0 as the top open-weight model">
</p>

Filtered to open-weight models only, Ideogram 4 leads by a commanding margin,
well ahead of the next-best open model:

<p align="center">
  <img src="https://raw.githubusercontent.com/ideogram-oss/ideogram4/main/assets/benchmarks/design_arena2.png" alt="Design Arena open-weight image Elo leaderboard, with Ideogram 4.0 well ahead of all other open models">
</p>

### ContraLabs

[ContraLabs](https://contralabs.com/research) ran a blind typography evaluation judged by
ten professional designers from Contra's top-earning talent. Ideogram 4 leads on
first-place win rate, picked as the best of four models 47.9% of the time
overall — well ahead of Gemini 3.1 Flash Image Preview (Nano Banana 2) at 30.0%,
FLUX.2 [max] (15.5%), and Grok Imagine 1.0 (15.0%):

<p align="center">
  <img src="https://raw.githubusercontent.com/ideogram-oss/ideogram4/main/assets/benchmarks/contralabs_typography.png" alt="ContraLabs typography first-place win rate, with Ideogram v4 leading">
</p>

It also wins on practical usability: asked "Would you use this in real client
work?", the same designers rated Ideogram 4 highest at 3.55 / 5 — significantly
above Nano Banana 2 (2.84), Grok Imagine 1.0 (2.61), and FLUX.2 [max] (2.49):

<p align="center">
  <img src="https://raw.githubusercontent.com/ideogram-oss/ideogram4/main/assets/benchmarks/contralabs_typography2.png" alt="ContraLabs 'would you use this in real client work?' rating, with Ideogram v4 leading">
</p>

### LMArena

On [LMArena](https://lmarena.ai/), a third-party text-to-image leaderboard that
measures general-purpose text-to-image use cases, Ideogram is the top-ranked
open-weight lab and a top-5 image generation lab overall — beaten only by giant
companies with vastly larger budgets and resources:

<p align="center">
  <img src="https://raw.githubusercontent.com/ideogram-oss/ideogram4/main/assets/benchmarks/lmarena_benchmark.png" alt="LMArena text-to-image lab leaderboard with Ideogram">
</p>

### Ideogram internal eval

For our internal human-preference benchmark, focused on graphic design and
photography, we had graphic designers deeply familiar with professional design
work do the rating blind. Bradley-Terry scores rank Ideogram 4 #2 overall —
behind only GPT Image 2 medium — and the top open-weight model:

<p align="center">
  <img src="https://raw.githubusercontent.com/ideogram-oss/ideogram4/main/assets/benchmarks/ideogram_benchmark.png" alt="Ideogram internal design leaderboard with Ideogram 4.0">
</p>

### Open-source benchmarks

On standard open-source benchmarks measuring core capabilities — layout control
(7Bench), spatial reasoning and object fidelity (SpatialGenEval), text rendering
(X-Omni OCR), and prompt alignment (Prism) — Ideogram 4 closes the gap to the
leading closed-source models across every axis. On layout control (7Bench), it
is significantly better than all closed-source models:

<p align="center">
  <img src="https://raw.githubusercontent.com/ideogram-oss/ideogram4/main/assets/benchmarks/opensource.png" alt="Five-axis capability radar comparing Ideogram 4.0 to leading closed-source models on layout control, spatial reasoning, object fidelity, prompt alignment, and text rendering">
</p>

At 9.3B parameters, Ideogram 4 delivers the best text rendering of any open-weight
release we benchmarked — ahead of much larger models like Qwen-Image (20B),
FLUX.2 [dev] (32B), and HunyuanImage 3.0 (80B MoE):

<p align="center">
  <img src="https://raw.githubusercontent.com/ideogram-oss/ideogram4/main/assets/benchmarks/opensource2.png" alt="Parameter-efficiency scatter plot showing Ideogram 4.0 at 9.3B parameters leading all other open-weight models on text rendering">
</p>


## Quick Start

### Install

The inference code lives in the [`ideogram4`](https://github.com/ideogram-oss/ideogram4) GitHub repo. Clone it, then from the repo root:

```bash
pip install .
```

If you plan to modify the code, install in editable mode instead so changes
under `src/ideogram4/` take effect without reinstalling:

```bash
pip install -e .
```

### Model access

The model weights are **gated** on Hugging Face, so you must accept the gate and
authenticate before the code can download them — otherwise the download fails
with a `404` / `GatedRepoError`.

1. Open the model page — [ideogram-ai/ideogram-4-nf4](https://huggingface.co/ideogram-ai/ideogram-4-nf4)
   (or [ideogram-ai/ideogram-4-fp8](https://huggingface.co/ideogram-ai/ideogram-4-fp8)) — and click
   **Agree and access repository** to accept the license gate.
2. Create a Hugging Face access token at
   [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and log in so the
   download is authenticated:

   ```bash
   hf auth login
   ```

   Alternatively, export the token directly: `export HF_TOKEN="hf_..."`.

### CLI

The plain `--prompt` is rewritten into the structured JSON caption the model
expects by a "magic prompt" LLM. By default this uses Ideogram's hosted
magic-prompt API, which is **free** and does the expansion server-side (no local
model or system prompt needed). It reads `IDEOGRAM_API_KEY` — get a key at
[developer.ideogram.ai](https://developer.ideogram.ai/):

```bash
python run_inference.py \
  --prompt "a ginger cat wearing a tiny wizard hat reading a spellbook" \
  --output out.png \
  --quantization "nf4" \
  --magic-prompt-key "$IDEOGRAM_API_KEY"
```

You can also run the expansion through your own LLM provider — one of our magic-prompt
system prompt is **open source**. See the
[Prompting Guide](https://github.com/ideogram-oss/ideogram4/blob/main/docs/prompting.md#magic-prompt) for details.

For the highest-quality images, set `--height 2048 --width 2048` and
`--sampler-preset V4_QUALITY_48`.

#### Safety screening with Hive

Prompt and output safety screening is performed via [Hive](https://thehive.ai/).
Sign up and create a Text Moderation key and a Visual Content Moderation key,
then export them as `HIVE_TEXT_MODERATION_KEY` and `HIVE_VISUAL_MODERATION_KEY`
(or pass them via `--hive-text-key` / `--hive-visual-key`).

```bash
python run_inference.py \
  --prompt "an isometric illustration of a tiny city floating in the clouds" \
  --output out.png \
  --quantization "nf4" \
  --magic-prompt-key "$MAGIC_PROMPT_API_KEY" \
  --hive-text-key "$HIVE_TEXT_MODERATION_KEY" \
  --hive-visual-key "$HIVE_VISUAL_MODERATION_KEY"
```

For sampler presets, parameter reference, and optimization tips, see
[docs/inference.md](https://github.com/ideogram-oss/ideogram4/blob/main/docs/inference.md).

## Model Summary

Ideogram 4 is a **foundation model trained entirely from scratch**, not a
fine-tune or distillation of any existing checkpoint. It is a flow-matching
text-to-image model built on a **fully single-stream** Diffusion Transformer
(DiT) architecture.

**Architecture:**
- **Fully single-stream DiT.** Text and image tokens are concatenated into one
  unified sequence and processed through the same 34-layer transformer, with no
  separate text or image branches. This enables deep cross-modal interaction at
  every layer.
- **Vision-language model as text encoder.** Instead of a text-only encoder
  like CLIP or T5, Ideogram 4 uses
  [Qwen3-VL-8B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct),
  a full vision-language model that provides far richer understanding of visual
  concepts. Hidden states are extracted from **13 intermediate layers** and
  concatenated, giving the model multi-scale semantic features ranging from
  surface-level token information to deep compositional understanding.
- **Dual-branch classifier-free guidance.** The conditional (positive) and
  unconditional (negative) branches can be independently refined, enabling
  separate control over prompt adherence and image quality.
- **Flexible resolution.** Native support for any resolution from 256 to 2048
  (multiples of 16), with aspect ratios up to 6:1. A single model handles
  everything from square thumbnails to ultrawide banners, with the noise
  schedule auto-adjusting per resolution.

**Key Capabilities:**
- **Extreme controllability.** Ideogram 4 is trained on structured JSON
  captions, giving users unprecedented control over composition, style,
  lighting, color palette, typography, and spatial layout, all from a single
  prompt.
- **State-of-the-art text rendering.** Ideogram 4 delivers best-in-class
  in-image text generation (signage, logos, captions, watermarks, multi-line
  text) with high fidelity directly from the prompt.
- **Spatial layout control.** Bounding-box coordinates in the prompt allow
  explicit placement of subjects, text elements, and background regions.
- **Color palette conditioning.** Specify hex colors in the prompt to steer the
  image's dominant color scheme.

For full architecture details, see
[docs/model_architecture.md](https://github.com/ideogram-oss/ideogram4/blob/main/docs/model_architecture.md). For a walkthrough of
how the pipeline components fit together, see
[docs/pipeline.md](https://github.com/ideogram-oss/ideogram4/blob/main/docs/pipeline.md).

## Prompting Guide

Ideogram 4 is trained exclusively on **structured JSON captions**. While
plain-text prompts work, you will get the best results by providing a JSON
object that follows our caption schema.


Key points:

- **Use JSON prompts** for maximum controllability — the model was trained on
  them and understands the structure natively.
- **Color palette conditioning** — specify a `colour_palette` array of hex
  colors in the style description to steer the image's color scheme.
- **Aspect ratio flexibility** — Ideogram 4 supports a wide range of aspect
  ratios (any multiple-of-16 resolution from 256 to 2048 on each side). This
  is a key advantage for practical use: portraits, landscapes, banners,
  phone wallpapers, social media formats, etc.
- **Bounding-box layout** — specify `bbox` coordinates in the prompt to
  explicitly place subjects, text elements, and background regions.
- **Compositional control** — use `compositional_deconstruction` with bounding
  boxes and per-element descriptions for precise spatial layout.


**Why JSON-only training?** We train exclusively on JSON so that training
and inference share a single, common prompt format. The training captions themselves are deliberately
**extremely descriptive**: each JSON exhaustively describes everything in
the image to maximize training efficiency. The more
text-to-image relationships each caption pins down, the more grounded
supervision the model extracts from a single training pair, rather than
having to infer those relationships across many sparsely-captioned samples.

**Why JSON at inference time?** Because the model was trained on captions
that name every object explicitly, the most reliable way to get every
requested object rendered is to mirror that pattern. Plain-text prompts still work, but
won't perform as well since the model was only trained on structured JSON captions.

**Don't want to write JSON by hand?** That's what *magic prompt* is for: it uses
an LLM to expand a plain-text prompt into a full structured caption before
generation, so you get JSON-quality results from a casual prompt. It runs by
default in `run_inference.py` (see the [CLI](#cli) section).

See [docs/prompting.md](https://github.com/ideogram-oss/ideogram4/blob/main/docs/prompting.md) for a full guide.

## Documentation

| Document | Description |
| :------- | :---------- |
| [docs/prompting.md](https://github.com/ideogram-oss/ideogram4/blob/main/docs/prompting.md) | How to write JSON prompts, color palette conditioning, aspect ratios |
| [docs/inference.md](https://github.com/ideogram-oss/ideogram4/blob/main/docs/inference.md) | Sampler presets, parameter reference, resolutions, optimization tips |
| [docs/model_architecture.md](https://github.com/ideogram-oss/ideogram4/blob/main/docs/model_architecture.md) | Architecture diagram, DiT spec, component details |
| [docs/pipeline.md](https://github.com/ideogram-oss/ideogram4/blob/main/docs/pipeline.md) | Conceptual pipeline walkthrough — how all components fit together |
| [docs/development.md](https://github.com/ideogram-oss/ideogram4/blob/main/docs/development.md) | Dev setup, pre-commit hooks, contributing |
| [docs/safety.md](https://github.com/ideogram-oss/ideogram4/blob/main/docs/safety.md) | Pre-training, post-training, and inference-time safety mitigations; how to report violations |

## Citation

If you find the provided code or models useful for your research, consider citing them as:


```bibtex
@misc{ideogram-4-2026,
    author={Ideogram AI},
    title={{Ideogram 4}},
    year={2026},
    howpublished={\url{https://ideogram.ai/blog/ideogram-4.0/}},
}
```

## We're Hiring!

We're looking for **Research Scientists** and **Research Engineers** to
work on next-generation generative models and the products built on top of
them. Interested candidates please apply https://jobs.ashbyhq.com/ideogram

---
type: Concept
title: Krea 2 Raw Text-to-Image Model
description: Krea.ai 12B diffusion-transformer text-to-image base checkpoint for fine-tuning, with a post-trained Turbo variant under the Krea 2 Community License.
tags: [krea, text-to-image, diffusion, local-inference, image-generation]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T12:00:00Z }
sources:
  - id: krea2-raw-readme
    resource: ../raw/Krea-2-Raw/README.md
    scope: ../raw/Krea-2-Raw/
    kind: documentation
    title: Krea 2 Raw model card
---

Krea 2 Raw is the **reported** base release checkpoint of the Krea 2 text-to-image family, described as a 12 billion parameter diffusion transformer suited as a fine-tuning or post-training base rather than for direct inference use, with Krea 2 Turbo as the post-trained and distilled release checkpoint.[^krea2-raw-readme]

## Identity and release

- **Reported** identity: model name Krea 2, version v1.0, release date June 22, 2026, model type text-to-image diffusion model, architecture diffusion transformer with 12 billion parameters, developer Krea.ai, Inc., release format open-weight release plus Krea-hosted product integrations.[^krea2-raw-readme]
- **Reported** family: Krea 2 Raw is the base checkpoint prior to additional post-training and fine-tuning; Krea 2 Turbo is the post-trained checkpoint with additional fine-tuning and distillation.[^krea2-raw-readme]
- **Reported** positioning: Raw is not recommended for inference use and is a good base for fine-tuning or post-training for user domains; one stated use case is training LoRAs on midtrain and using them directly on Krea 2 Turbo, with an in-house LoRA collection trained on Raw for Turbo use linked but not locally captured.[^krea2-raw-readme]
- **Reported** license: Krea 2 Community License; frontmatter names `krea-2-community-license` with a license PDF link and gated access requiring name, email, company, and agreement to the community license plus acknowledgment of the Acceptable Use Policy.[^krea2-raw-readme]

## Intended use and out-of-scope uses

- **Reported** capabilities: generates images from natural-language text descriptions for creative, commercial, developer, and research use cases, including image generation, concepting, design exploration, visual production workflows, and integration into applications and creative tools.[^krea2-raw-readme]
- **Reported** out-of-scope summary: not intended for uses violating law or regulations, infringing or misappropriating third-party rights, generating or facilitating unlawful or harmful content including CSAM, NCII, harassment or defamation, or supporting fully automated decision-making adversely affecting legal rights; use is subject to the Community License Agreement and Acceptable Use Policy, which control in case of conflict.[^krea2-raw-readme]
- **Reported** outputs position: Krea does not claim copyright or other IP over user-generated content; users are solely responsible for outputs and subsequent use, including third-party-rights risks influenced by prompts.[^krea2-raw-readme]

## Inference entry points

All procedures below are **reported**; no install, download, or generation was executed for this concept.

- **Reported** official codebase: set up the official Krea 2 codebase, download `raw.safetensors`, set `OSS_RAW=<path-to-raw.safetensors>`, then run `uv run inference.py "a fox walking in the snow" --checkpoint oss_raw --steps 52 --cfg 3.5 --width 1024 --height 1024`.[^krea2-raw-readme]
- **Reported** Diffusers: install diffusers from source with `pip install git+https://github.com/huggingface/diffusers.git`, then run `Krea2Pipeline.from_pretrained("krea/Krea-2-Raw", torch_dtype=torch.bfloat16).to("cuda")` and generate with prompt `a fox in the snow`, `num_inference_steps=52`, `guidance_scale=3.5`.[^krea2-raw-readme]
- **Reported** SGLang: install SGLang from source, then run `sglang generate --model-path krea/Krea-2-Raw --prompt "a red fox sitting in fresh snow, golden hour, photorealistic" --num-inference-steps 52 --height 1024 --width 1024 --guidance-scale 3.5 --save-output`; a full SGLang Krea 2 cookbook is linked but not locally captured.[^krea2-raw-readme]
- **Observed:** the canonical weight `raw.safetensors`, the official codebase, the Diffusers `Krea2Pipeline`, the SGLang implementation, and the LoRA collection were not captured locally and remain uninspected.

## Training, safety, and limitations

- **Reported** training data: combination of publicly available data, third-party licensed data, and proprietary synthetic data comprising images and captions or text descriptions; filtered to remove certain harmful content and reduce low-quality, duplicative, or irrelevant data, with curated and synthetic selections to improve prompt following, visual quality, and alignment.[^krea2-raw-readme]
- **Reported** safety measures: lifecycle measures including targeted fine-tuning to reduce susceptibility to direct and adversarial harmful prompts plus multiple rounds of internal and external safety evaluation; hosted Krea products add proprietary and third-party input/output classifiers, while open-weight deployers are required by the license to implement content filtering or equivalent review, with non-compliance constituting breach.[^krea2-raw-readme]
- **Reported** evaluation scope: adversarial testing covered sexually explicit content, non-consensual intimate imagery, child-safety risks, and other high-risk categories, with release checkpoints described as highly resilient across tested categories; reporting goes to `safety@krea.ai`, potential CSAM is escalated to NCMEC, and Krea reserves the right to update weights or revoke access on misuse patterns.[^krea2-raw-readme]
- **Reported** risks and limits: new technology with non-exhaustive testing and unpredictable outputs that may be inaccurate, objectionable, or undesirable; not intended to provide factual information; prompt following may fail and is influenced by prompt style, specificity, language, and phrasing; developers should perform application-specific safety testing and implement license-required safeguards.[^krea2-raw-readme]
- **Reported** examples: frontmatter widget lists around 20 prompt plus image-URL pairs illustrating styles such as halftone, pixel or low-poly, impressionist brushwork, thermal, black-and-white photography, anime, collage, flat illustration, painterly landscape, macro, digital painting, surreal, ink, retro-anime cel, and cinematic portrait; pairs were not rendered or verified here.[^krea2-raw-readme]

## Relationships

- Distilled release: [Krea 2 Turbo Text-to-Image Model](krea-2-turbo.md) is the reported post-trained and distilled checkpoint derived from Raw and optimized for few-step inference.
- Uses a LoRA workflow where adapters trained on Raw are meant for Turbo; for a community adapter pattern on a different base model, see [Qwen-Image-2.1-Fix LoRA Adapter](qwen-image-2-1-fix.md).
- For a local C/C++ engine that lists Krea2 among its supported image models, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md).
- For comparable 12B-class text-to-image diffusion-transformer coverage with different licensing and distillation, see [FLUX.1-dev Text-to-Image Model](flux-1-dev.md) and [FLUX.1-schnell Text-to-Image Model](flux-1-schnell.md).

## Coverage limits

- **Observed:** only `../raw/Krea-2-Raw/README.md` was statically inspected; no code was executed and no install, inference, LoRA-training, safety, quality, or policy claim was reproduced.
- **Observed:** uninspected material outside this scope includes `raw.safetensors` weights, the official `krea-ai/krea-2` codebase, the Krea-2 LoRA collection, header and widget sample images under `assets/hf_samples/raw/`, the license PDF, the Acceptable Use Policy, the SGLang cookbook, and the gated-access flow.
- All capability, procedure, training, safety, evaluation, permission, and contact statements above are **reported** by the model card, not independently verified.
- **Synthesis:** verify the current Community License, Acceptable Use Policy, gated terms, and model-card version upstream before commercial, derivative, or deployment reuse; this capture records card version 1.0 last updated June 22, 2026 with no immutable weight revision.

[^krea2-raw-readme]: Model-card capture in `../raw/Krea-2-Raw/README.md`; Raw-versus-Turbo positioning and LoRA use case from header; official-codebase, Diffusers `Krea2Pipeline`, and SGLang invocations from Inference sections; name, version, date, type, 12B architecture, license, format, and developer from Model Overview; family checkpoints from Model Family; capabilities, out-of-scope, training-data, safety, risks, outputs, reporting, and contact claims from their eponymous sections; gated fields, license name and link, pipeline tag, and widget prompt plus image URLs from YAML frontmatter.

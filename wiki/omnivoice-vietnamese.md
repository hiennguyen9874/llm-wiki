---
type: Concept
title: OmniVoice Vietnamese (splendor1811)
description: Vietnamese finetune of OmniVoice trained 8,000 steps on the 1,000-hour Dolly-Audio corpus, with cached voice-prompt and torch.compile serving recipes and L4 figures of RTF ~0.07 and ~210 ms TTFB, but unresolved dataset-versus-model license conflict.
tags: [tts, vietnamese, voice-cloning, zero-shot, omnivoice, finetune]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T18:00:00Z }
stale_after: 2027-10-21
sources:
  - id: omnivoice-vi-card
    resource: ../raw/omnivoice-vietnamese.md
    kind: documentation
    title: OmniVoice Vietnamese model card (splendor1811/omnivoice-vietnamese)
---

`splendor1811/omnivoice-vietnamese` is a Vietnamese fine-tune of `k2-fsa/OmniVoice` (Qwen3-0.6B backbone, non-autoregressive diffusion language model with iterative masked decoding) trained for 8,000 steps (about 6 hours on one NVIDIA H200) on the ~1,000-hour Dolly-Audio Vietnamese corpus, offering zero-shot voice cloning at 24 kHz. Its distinguishing content is a serving recipe (cached voice prompt, `torch.compile`, `num_step=8`) with self-reported L4 latency figures; it publishes no quality metric (**Reported**).[^omnivoice-vi-card]

## Identity and lineage

- Model ID `splendor1811/omnivoice-vietnamese`; `base_model: k2-fsa/OmniVoice`; `pipeline_tag: text-to-speech`; tags `voice-cloning`, `multilingual`, `zero-shot`, `voice-design`; inference library `omnivoice` (**Reported**, frontmatter **Observed**).[^omnivoice-vi-card]
- The frontmatter `language` list is inherited from the base model (hundreds of codes including `vi`), so it does not indicate multilingual quality of the finetune; the card's prose positions it for Vietnamese cloning and TTS (**Synthesis**).[^omnivoice-vi-card]
- No revision, publication date, author identity beyond the model-ID namespace, or training-recipe details (learning rate, batch size, whether full or partial finetune, checkpoint selection) are given (**Observed** absence).[^omnivoice-vi-card]

## Training data and run

| Item | Reported value |
| --- | --- |
| Training steps / time | 8,000 steps, 6 hours |
| Hardware | NVIDIA H200 SXM (141 GB VRAM) |
| Output sample rate | 24,000 Hz |
| Corpus | Dolly-Audio (`dolly-vn/dolly-audio-1000h-vietnamese`), ~1,000 h, 664,125 samples, 152 speakers across regions and accents |
| Clip length | 0.63–32.1 s per sample |
| Corpus quality / domains | cleaned, noise-free, sentence-boundary trimmed; news, entertainment, education, conversational |

(**Reported**.)[^omnivoice-vi-card] Averaged over the stated totals this is roughly 5.4 s per sample (**Synthesis**, arithmetic from the table). 8,000 steps over 664k samples implies the model sees only a fraction of the corpus unless batches are large; the batch size is not stated, so epochs seen cannot be derived (**Synthesis**).

## Usage

- Install a CUDA-matched PyTorch (`torch==2.8.0+cu128`, `torchaudio==2.8.0+cu128`), then `pip install omnivoice` (**Reported**).[^omnivoice-vi-card]
- Zero-shot cloning: `OmniVoice.from_pretrained("splendor1811/omnivoice-vietnamese", device_map="cuda:0", dtype=torch.float16)`, then `model.generate(text=..., language="vietnamese", ref_audio=..., ref_text=...)`; save with `torchaudio.save(..., audio[0], 24000)` (**Reported**).[^omnivoice-vi-card]
- Cached voice prompt (recommended for serving): `model.create_voice_clone_prompt(ref_audio, ref_text)` encodes the reference once; later `generate(..., voice_clone_prompt=voice_prompt)` calls skip re-encoding (**Reported**).[^omnivoice-vi-card]
- Production recipe: `torch.set_float32_matmul_precision("high")`, `model.llm = torch.compile(model.llm, mode="reduce-overhead", dynamic=True)`, three warmup generations to trigger compilation, and `OmniVoiceGenerationConfig(num_step=8, guidance_scale=2.0)` for speed (**Reported**).[^omnivoice-vi-card]
- The card's header mentions voice design (inherited from base), but no Vietnamese voice-design example or `instruct` usage is given; contrast [G-OmniVoice](g-omnivoice.md), which documents attribute design (**Observed** absence).[^omnivoice-vi-card]

## Performance

Self-reported on an NVIDIA L4 with `num_step=8` and `torch.compile(mode="reduce-overhead")` (**Reported**):[^omnivoice-vi-card]

| Metric | Value |
| --- | --- |
| RTF | ~0.07 (~14x real time) |
| TTFB, short sentence | ~210 ms |
| P95 TTFB at CCU=4 | ~1.26 s |

- The card does not define TTFB (time to first byte of a complete waveform versus first streamed chunk), the sentence length, the reference-prompt state (cached or not), warm/cold state, or the concurrency harness. Its usage examples return complete waveforms, so TTFB most plausibly measures whole short-utterance generation; that reading is not stated (**Synthesis**).[^omnivoice-vi-card]
- The P95 growth from ~210 ms single-stream to ~1.26 s at four concurrent users (about 6x) shows latency scaling poorly under concurrency on an L4; this is arithmetic on reported figures, not a measured trend (**Synthesis**).[^omnivoice-vi-card]
- The base card's RTF 0.025 (~40x) is not directly comparable: the hardware, step count, and protocol of that figure are not matched to this L4 setting (see [OmniVoice](omnivoice.md)) (**Synthesis**).[^omnivoice-vi-card]
- No WER, speaker-similarity, MOS, or listening evidence is provided, so cloning quality of this checkpoint is unestablished from its own card (**Observed** absence).[^omnivoice-vi-card]

## Licensing and data constraints

- Model license is stated as Apache 2.0, while the training dataset is CC-BY-NC-SA-4.0 and described as research use only (**Reported**).[^omnivoice-vi-card]
- **Unresolved tension (neither side chosen):** the card labels the finetuned model Apache 2.0, but its own cited dataset is non-commercial share-alike research-only; and the compiled base-model concept records CC-BY-NC pre-trained weights. Whether the finetune may be used commercially is therefore not established by this card (**Synthesis**).[^omnivoice-vi-card]
- No consent, speaker-rights, or responsible-use section for voice cloning is included, unlike the base card's anti-impersonation language (**Observed** absence).[^omnivoice-vi-card]

## Contradictions

- Model license claim: this card states Apache 2.0 for the model.[^omnivoice-vi-card] The [OmniVoice](omnivoice.md) concept reports Apache 2.0 code but CC-BY-NC pre-trained weights for the base. The same card's dataset terms are CC-BY-NC-SA-4.0 research-only.[^omnivoice-vi-card] No source resolves which governs the derivative.

## Relationships

- Finetuned from [OmniVoice](omnivoice.md), the 600+-language base; this concept covers a Vietnamese specialization with a serving recipe and L4 latency numbers (**Synthesis**).[^omnivoice-vi-card]
- Sibling Vietnamese OmniVoice finetunes: [G-OmniVoice](g-omnivoice.md) reports held-out Vietnamese WER 0.0259 / SIM 0.890 / MOS 7.685 with attribute voice design but no latency; [KhanhTTS-OmniVoice](khanhtts-omnivoice.md) reports ~1,500 h training with no quality or latency figures. This checkpoint is the only one of the three with latency figures and the only one with none for quality; the three were not evaluated on a common test set and none lists this model in its comparison table (**Synthesis**).[^omnivoice-vi-card]
- Deployment routes for OmniVoice checkpoints (native GGUF, audio.cpp, CrispASR, HF Speech-to-Speech) are compared in [OmniVoice Deployment Comparison](omnivoice-deployment-comparison.md); this card's recipe is the Python `omnivoice` route only, and GGUF compatibility of this finetune is not established (**Synthesis**).[^omnivoice-vi-card]
- Vietnamese deployment shortlist context: [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) treats OmniVoice finetunes as accuracy/cloning candidates pending streaming, latency, and license checks; this card adds a reported ~210 ms short-sentence TTFB on an L4 that still needs reproduction (**Synthesis**).[^omnivoice-vi-card]

## Coverage and limits

- Single model-card capture inspected statically (`raw/omnivoice-vietnamese.md`, 821 lines, of which the 660-line frontmatter is mostly the inherited `language` code list, excluded as inherited metadata). No revision or capture date is recorded (**Observed**).[^omnivoice-vi-card]
- Not performed: package installation, checkpoint or dataset download, audio synthesis, latency reproduction, and fetching the linked Hugging Face model/dataset pages or the OmniVoice arXiv paper (`2604.00688`, cited in the card's BibTeX); the Dolly-Audio dataset BibTeX (Nguyen and Nguyen, 2025) is likewise unfetched (**Synthesis**).[^omnivoice-vi-card]
- All claims are vendor assertions without independent verification; benchmark and release figures carry `stale_after: 2027-10-21` per the `tts` domain rule (**Synthesis**).[^omnivoice-vi-card]

[^omnivoice-vi-card]: [OmniVoice Vietnamese model card](../raw/omnivoice-vietnamese.md) — locators: frontmatter (`license: apache-2.0`, `datasets`, `base_model`, `pipeline_tag`, `tags`, inherited `language` list); intro paragraph and link bullets (model, base, dataset, license lines); `## Training Details` table; `## Dataset` table; `## Installation` steps 1–2; `## Usage` (Python API, cached voice prompt, torch.compile blocks); `## Performance` table; `## Base Model: OmniVoice` feature bullets; `## Citation` (zhu2026omnivoice, dolly_audio_2025 BibTeX).

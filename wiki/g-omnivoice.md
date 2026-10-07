---
type: Concept
title: G-OmniVoice
description: Vietnamese-optimized OmniVoice finetune with zero-shot voice cloning and attribute-driven voice design, reporting 2.59% Vietnamese WER at 0.890 speaker similarity on its held-out test set.
tags: [tts, vietnamese, voice-cloning, zero-shot]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T12:30:00Z }
stale_after: 2027-10-07
sources:
  - id: g-omnivoice-card
    resource: ../raw/g-omnivoice.md
    kind: documentation
    title: G-OmniVoice model card
---

G-OmniVoice is a Vietnamese-optimized text-to-speech model by G-Group AI Lab, fine-tuned from `k2-fsa/OmniVoice` (Qwen3-0.6B backbone plus Higgs Audio 2 codec) on a large-scale Vietnamese speech corpus, offering zero-shot voice cloning from a 3–10 second reference clip and reference-free voice design from an attribute description (**Reported**).[^g-omnivoice-card]

## Model identity and lineage

- Title is `G-OmniVoice`; model ID is `g-group-ai-lab/g-omnivoice` on Hugging Face; inference library is `omnivoice` (`library_name: omnivoice`, `pipeline_tag: text-to-speech`); card frontmatter declares `base_model` of `k2-fsa/OmniVoice` and `Qwen/Qwen3-0.6B`, `language: vi`, and tags `text-to-speech`, `tts`, `voice-cloning`, `voice-design`, `zero-shot`, `vietnamese`, and `omnivoice` (**Reported**, frontmatter presence **Observed**).[^g-omnivoice-card]
- Stated contribution is doing two things at once: reading Vietnamese accurately while preserving the reference speaker's voice — claimed as the lowest WER of any public OmniVoice model combined with top-tier speaker similarity (**Reported**).[^g-omnivoice-card]

## Capabilities

- Zero-shot voice cloning from a 3–10 s reference clip plus its transcript (`ref_audio` plus `ref_text`), with a tip to use 3–10 s of clean, single-speaker reference audio for the best clone (**Reported**).[^g-omnivoice-card]
- Reference-free voice design from an attribute description string, e.g. `female, young adult, medium pitch, northern Vietnamese accent` (**Reported**).[^g-omnivoice-card]
- Practical synthesis tips: apply text normalization (numbers, dates, symbols, abbreviations) before synthesis, and split long inputs into sentence-sized chunks for stable prosody (**Reported**).[^g-omnivoice-card]

## Benchmark

Vendor-reported evaluation on a held-out Vietnamese test set, where lower WER is better (intelligibility), higher SIM is better (speaker similarity), and higher MOS is better (naturalness); no evaluation protocol, dataset, judge, or uncertainty details are stated in the card (**Reported**):[^g-omnivoice-card]

| Model name | WER ↓ | SIM ↑ | MOS ↑ |
| --- | ---: | ---: | ---: |
| k2-fsa/OmniVoice | 0.0712 | 0.892 | 7.709 |
| kjanh/KhanhTTS-OmniVoice | 0.0375 | 0.888 | 7.678 |
| VietNeu/v3turbo | 0.0551 | 0.778 | 7.570 |
| g-group-ai-lab/g-omnivoice (ours) | 0.0259 | 0.890 | 7.685 |

- G-OmniVoice reports the lowest WER (0.0259, about 31% better than the next model at 0.0375) while its SIM of 0.890 essentially ties the best (0.892); MOS of 7.685 trails the base OmniVoice figure of 7.709 (**Reported**).[^g-omnivoice-card]
- The card embeds a `wer_vs_sim.png` scatter plot described as placing G-OmniVoice alone in the top-left "best of both worlds" corner; the image file is not present in `raw/` and was not inspected, so the plot itself is unavailable evidence (**Synthesis**).[^g-omnivoice-card]
- Competitor rows (KhanhTTS-OmniVoice, VietNeu v3turbo) are figures as printed by this card, not verified against their own sources; the VietNeu row is labeled `VietNeu/v3turbo`, which does not match the compiled [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) publisher/checkpoint naming, so cross-card comparability is unestablished (**Synthesis**).[^g-omnivoice-card]

## Requirements and inference usage

- NVIDIA GPU setup installs a CUDA-matched PyTorch build, e.g. `pip install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 --extra-index-url https://download.pytorch.org/whl/cu128`, then the runtime via `pip install omnivoice` (**Reported**).[^g-omnivoice-card]
- Voice cloning loads the model with `OmniVoice.from_pretrained("g-group-ai-lab/g-omnivoice", device_map="cuda:0", dtype=torch.float16)`, calls `model.generate(text=..., ref_audio="reference.wav", ref_text="...")`, and receives a list of waveforms at 24 kHz, writable with `sf.write("clone.wav", audio[0], 24000)`; voice design calls `model.generate(text=..., instruct="...")` with no reference audio (**Reported**).[^g-omnivoice-card]
- The `generate` examples return complete waveforms; the card states no time-to-first-audio, streaming, concurrency, VRAM, or CPU/edge figures (**Observed** absence).[^g-omnivoice-card]

## Languages

- Optimized for Vietnamese; the underlying OmniVoice base is stated to support 600+ languages in zero-shot mode, with performance on other languages following the base model (**Reported**).[^g-omnivoice-card]

## Licensing

- Card states Apache 2.0, following the base `k2-fsa/OmniVoice` model; the bundled audio tokenizer is derived from Higgs Audio 2 and remains subject to the Boson Higgs Audio 2 Community License (see `audio_tokenizer/LICENSE`) (**Reported**).[^g-omnivoice-card]
- License-scope caution: the compiled [OmniVoice](omnivoice.md) concept records Apache-2.0 code but CC-BY-NC model weights for the base, so the commercial usability of this finetune needs a lineage/license check beyond this card's Apache-2.0 statement; neither reading is chosen here (**Synthesis**).[^g-omnivoice-card]

## Citation and acknowledgments

- Card supplies two BibTeX entries: `gomnivoice2026` (G-Group AI Lab, 2026, Hugging Face URL) and `zhu2026omnivoice` (OmniVoice paper, arXiv `2604.00688`, 2026) (**Reported**).[^g-omnivoice-card]
- Acknowledged parties: k2-fsa / Next-gen Kaldi (base model and runtime), Boson AI (Higgs Audio 2 tokenizer), Qwen Team (Qwen3 backbone), and G-Group AI Lab (Vietnamese fine-tuning and release) (**Reported**).[^g-omnivoice-card]

## Relationships

- Finetuned from [OmniVoice](omnivoice.md), which covers the massively multilingual base (600+ languages, diffusion language-model architecture, cloning plus attribute voice design, RTF 0.025); this concept covers the Vietnamese-specialized finetune with its held-out Vietnamese WER/SIM/MOS table (**Synthesis**).[^g-omnivoice-card]
- Vietnamese TTS comparison: [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) covers the dedicated Vietnamese on-device family (48 kHz, preset voices, frame-level streaming, RTX 3060/CPU latency tables), while this concept covers an OmniVoice-lineage Vietnamese finetune with vendor-reported accuracy/similarity figures but no streaming or latency evidence; no shared codebase is asserted (**Synthesis**).[^g-omnivoice-card]
- Vietnamese artifact comparison: [Kokoro Vietnamese](kokoro-vietnamese.md) covers a fine-tuned Vietnamese Kokoro artifact set with PyTorch/ONNX CLIs and `vig2p` G2P but no published quality figures, while this concept carries a numeric Vietnamese benchmark table without independent verification (**Synthesis**).[^g-omnivoice-card]
- Tokenizer-name link: the card names a Higgs Audio 2-derived audio tokenizer under the Boson Community License; [Higgs TTS 3](higgs-tts-3-4b.md) covers a separate Boson 4B multilingual TTS model, cited here only as a name-adjacent retrieval pointer with no shared-checkpoint claim (**Synthesis**).[^g-omnivoice-card]
- Included by [TTS Model Survey](tts-model-survey.md) as a Vietnamese-finetuned catalog row and by [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) as a Vietnamese-accuracy challenger pending streaming, latency, and license checks (**Synthesis**).[^g-omnivoice-card]

## Coverage and limits

- Source inspected statically only as the single model-card capture in `raw/`; no package installed, no checkpoint downloaded, no audio synthesized, and no WER, SIM, MOS, cloning-quality, or voice-design claims reproduced (**Synthesis**).[^g-omnivoice-card]
- Unavailable or uninspected artifacts: the `wer_vs_sim.png` plot referenced by the card is not in `raw/`; Hugging Face checkpoint and dataset, `audio_tokenizer/LICENSE` text, linked base-model and tokenizer pages, and demo audio were not in `raw/` and were not fetched (**Synthesis**).[^g-omnivoice-card]
- All identity, capability, benchmark, usage, language, and licensing claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-07` per the `tts` domain rule (**Synthesis**).[^g-omnivoice-card]

[^g-omnivoice-card]: [G-OmniVoice model card](../raw/g-omnivoice.md) — locators: frontmatter (`license: apache-2.0`, `language: vi`, `base_model: k2-fsa/OmniVoice` + `Qwen/Qwen3-0.6B`, `pipeline_tag: text-to-speech`, `library_name: omnivoice`, `tags`); intro paragraph (Vietnamese optimization, k2-fsa/OmniVoice lineage, Qwen3-0.6B backbone + Higgs Audio 2 codec, large-scale Vietnamese corpus, accuracy-plus-fidelity claim); feature bullets (Vietnamese speech, WER-plus-similarity, 3–10 s cloning); `## Benchmark` section (held-out Vietnamese test-set sentence, WER/SIM/MOS 4-row table, `wer_vs_sim.png` scatter description with ~31%-better reading); `## Installation` fences (torch 2.8.0+cu128, `pip install omnivoice`); `## Usage` fences (`from_pretrained` with `device_map`/`dtype`, cloning `generate` with `ref_audio`/`ref_text`, design `generate` with `instruct`, `sf.write` at 24000); `### Tips` bullets (text normalization, sentence-sized chunks, 3–10 s clean single-speaker reference); `## Supported Languages` paragraph (Vietnamese-optimized, 600+ base languages); `## Citation` (gomnivoice2026 + zhu2026omnivoice bibtex); `## License` (Apache 2.0, Higgs Audio 2 Community License tokenizer note); `## Acknowledgments` (k2-fsa, Boson AI, Qwen Team, G-Group AI Lab).

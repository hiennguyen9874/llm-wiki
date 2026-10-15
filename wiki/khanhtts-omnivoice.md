---
type: Concept
title: KhanhTTS-OmniVoice
description: Vietnamese-English OmniVoice finetune with voice cloning, reported 1,500-hour training and 24 kHz inference, but no primary-card quality or realtime benchmarks.
tags: [tts, vietnamese, voice-cloning, bilingual]
status: stable
created: 2026-10-15
generated: { by: llm-wiki-agent/1, at: 2026-10-15T10:41:56Z }
stale_after: 2027-04-15
sources:
  - id: khanhtts-card
    resource: ../raw/KhanhTTS-OmniVoice.md
    kind: documentation
    title: KhanhTTS model card
  - id: omnivoice-card
    resource: ../raw/OmniVoice.md
    kind: documentation
    title: OmniVoice model card
  - id: g-omnivoice-card
    resource: ../raw/g-omnivoice.md
    kind: documentation
    title: G-OmniVoice model card
---

KhanhTTS is a Vietnamese-English text-to-speech finetune of `k2-fsa/OmniVoice`, published under the inference ID `kjanh/KhanhTTS-OmniVoice` and claiming voice cloning with short references (**Reported**). Its card reports approximately 1,500 hours of Vietnamese-English audio and 500,000 training steps, but supplies no quality or latency measurements; it is a research/cloning candidate, not a realtime-cleared deployment choice (**Synthesis**).[^khanhtts-card]

## Identity and training

- Frontmatter lists `vi`, `en`, `text-to-speech`, `base_model: k2-fsa/OmniVoice`, and `license: apache-2.0` (**Observed**). Training goals are natural Vietnamese-English pronunciation and stable cloning from short reference audio, not measured outcomes (**Reported**).[^khanhtts-card]
- Data provenance, consent, splits, preprocessing, training hyperparameters, compute, checkpoint selection, model parameter count and release/revision dates are not provided (**Observed** absence). No numeric minimum reference duration or code-switching evaluation is stated.[^khanhtts-card]

## Inference surface

The card installs `pip install omnivoice`, imports `OmniVoice`, `torch` and `soundfile`, and loads `OmniVoice.from_pretrained("kjanh/KhanhTTS-OmniVoice", device_map="cuda:0", dtype=torch.float16)`. It then calls `model.generate(text="Xin chào các bạn.")`; optional `ref_audio` and `ref_text` are present but commented out. The example thus does not actually enable reference-conditioned cloning (**Observed**).[^khanhtts-card]

The return is documented as a list of `np.ndarray` waveforms with shape `(T,)` at 24 kHz, written using `sf.write("out.wav", audio[0], 24000)` (**Reported**). Package versions, a complete environment, VRAM requirements, CPU/edge support, streaming APIs, TTFA, RTF and concurrency are not established by this card (**Observed** absence). Returning a complete waveform in this example does not prove that every possible runtime lacks streaming (**Synthesis**).[^khanhtts-card]

## Quality evidence

The KhanhTTS card embeds reference and generated-audio URLs under `kjanh/ViVoxCPM-1.5`, not the KhanhTTS repository path; the generated URL contains a literal space in `demo_clone .wav`. Their checkpoint provenance and audible quality are unverified: neither clip was fetched or heard (**Observed/Synthesis**).[^khanhtts-card]

Separately, the [G-OmniVoice](g-omnivoice.md) competitor table reports KhanhTTS WER **0.0375**, SIM **0.888**, MOS **7.678** on a held-out Vietnamese set (**Reported by another model's publisher**, not KhanhTTS's own benchmark). Dataset identity, evaluation/ASR judge, MOS scale, sample size, uncertainty and checkpoint revision are unspecified; these are not independently reproduced scores or a matched realtime ranking.[^g-omnivoice-card]

## Licensing and responsible use

- KhanhTTS frontmatter declares Apache-2.0; its disclaimer describes research, experimentation and development use, prohibits impersonation or cloning without lawful consent and misleading/fraudulent use, calls for AI-audio disclosure, and discourages production/commercial deployment without rigorous testing, risk evaluation and safety checks (**Reported**).[^khanhtts-card]
- **Unresolved license lineage:** base OmniVoice explicitly distinguishes Apache-2.0 code from CC-BY-NC pretrained weights. The derivative's Apache label does not itself establish that inherited weight/data restrictions have been cleared; review the full license chain before commercial deployment (**Synthesis**, not a legal determination).[^khanhtts-card][^omnivoice-card]

## Relationships

- Depends on [OmniVoice](omnivoice.md): the card explicitly names the base and uses its Python runtime; base capabilities and RTF are not automatically measurements of this finetune.[^khanhtts-card]
- Compared by [G-OmniVoice](g-omnivoice.md): its held-out table includes this exact model ID; only the competitor card supplies numeric quality evidence.[^g-omnivoice-card]
- Included in [TTS Model Survey](tts-model-survey.md) and [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) as an unranked bilingual cloning candidate (**Synthesis**).[^khanhtts-card]

## Coverage and limits

- Fully inspected the single immutable local card statically; source identity is `raw/KhanhTTS-OmniVoice.md`, with no package scope or revision supplied. Upstream model ID is inferred from its load example; author identity, canonical card URL, publication/update/capture dates are not supplied. Its citation names Zhu et al.'s 2026 OmniVoice paper, arXiv 2604.00688.[^khanhtts-card]
- Coverage ledger: card prose/frontmatter, installation and Python examples, disclaimer and BibTeX inspected; linked reference/generated audio pending listening and provenance checks; weights, runtime code, training data and original paper not inspected. Donation link, badge and support image excluded as decorative/nontechnical. No external assets fetched and no commands from the source executed.[^khanhtts-card]
- Supporting local evidence inspected: base card's License/Python API and G-OmniVoice's identity/Benchmark sections. Its external scatter plot is excluded here because the printed table already carries the relevant numeric row. No model installation, downloads, synthesis, listening or independent benchmark verification occurred; status stable means the intended card synthesis is complete, not verified.[^omnivoice-card][^g-omnivoice-card]

[^khanhtts-card]: [KhanhTTS card](../raw/KhanhTTS-OmniVoice.md) — frontmatter; KhanhTTS introduction; “Thông tin huấn luyện”; “Sample” (audio src URLs); “Cài đặt & chạy inference” §§1–2 (install, from_pretrained, commented references, return-shape comment and sf.write); “Miễn trừ trách nhiệm & Khuyến cáo sử dụng (TTS)”; “Trích dẫn (Citation)”. No revision/date recorded.
[^omnivoice-card]: [OmniVoice card](../raw/OmniVoice.md) — “License” (Apache-2.0 code versus CC-BY-NC pretrained model); “Usage” → “Python API”.
[^g-omnivoice-card]: [G-OmniVoice card](../raw/g-omnivoice.md) — introduction and “Benchmark”, row `kjanh/KhanhTTS-OmniVoice`; held-out-set statement and metric labels.

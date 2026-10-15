---
type: Concept
title: Kokoro-82M
description: Open-weight 82M-parameter text-to-speech model on the StyleTTS 2 architecture with Apache-2.0 weights, a 24 kHz Python pipeline, card-reported training and cost figures, and no in-card quality benchmarks.
tags: [tts, kokoro, styletts2, open-weights, apache-2.0]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-15T10:59:14Z }
stale_after: 2026-04-30
sources:
  - id: kokoro-82m-card
    resource: ../raw/Kokoro-82M.md
    kind: documentation
    title: Kokoro-82M model card capture
  - id: kokoro-fastapi-readme
    resource: ../raw/Kokoro-FastAPI.md
    kind: documentation
    title: Kokoro-FastAPI README capture
  - id: kokoro-library-readme
    resource: ../raw/kokoro.md
    kind: documentation
    title: kokoro library README capture
  - id: kvoicewalk-readme
    resource: ../raw/kvoicewalk.md
    kind: documentation
    title: KVoiceWalk README capture
---

Kokoro-82M is an open-weight, 82-million-parameter text-to-speech model whose card links to `hexgrad/Kokoro-82M` on Hugging Face and describes Apache-licensed weights. The card presents it as built on the StyleTTS 2 architecture and claims "comparable quality to larger models" with better speed and cost. The captured card includes no quality, latency, or memory benchmark, so those comparative claims stay unverified in this wiki (**Reported**; **Unverified**).[^kokoro-82m-card]

## Identity and provenance

- **Model and links:** the card names the Hugging Face model `hexgrad/Kokoro-82M`, a GitHub repository `hexgrad/kokoro`, and a demo Space `hexgrad/Kokoro-TTS`; its frontmatter sets `pipeline_tag: text-to-speech` (**Reported**).[^kokoro-82m-card]
- **Credits:** architecture credited to Li et al. in the StyleTTS 2 repository (`yl4579/StyleTTS2`); training credited to `@rzvzn`, the Discord handle the card names (**Reported**).[^kokoro-82m-card]
- **Declared base model:** frontmatter `base_model: yl4579/StyleTTS2-LJSpeech`. The card does not say whether this means fine-tuning or architectural reuse (**Reported**; limit).[^kokoro-82m-card]
- **Weight identity:** the v1.0 model SHA256 is `496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4`; the release table identifies it by the prefix `496dba11`. Verify downloads against the full hash (**Reported**).[^kokoro-82m-card]
- **Named dependencies:** the `kokoro` Python package (`>=0.9.2`), the `misaki` G2P library, and system `espeak-ng` (**Reported**).[^kokoro-82m-card] `misaki` is covered by [Misaki](misaki.md); `espeak-ng` is covered by [eSpeak NG](espeak-ng.md).

## Releases and training

| Release | Published | Training data | Languages & voices | SHA256 prefix |
| --- | --- | --- | --- | --- |
| v1.0 (bold row) | 2025 Jan 27 | few hundred hours | 8 & 54 | `496dba11` |
| v0.19 (legacy repo) | 2024 Dec 25 | under 100 hours | 1 & 10 | `3b0c392f` |

The release table is **Reported**; see [Contradictions](#contradictions) for the language count.[^kokoro-82m-card] The card does not mark v0.19 as deprecated, so no supersession edge is recorded.

- **Data policy:** training used "exclusively permissive/non-copyrighted audio data and IPA phoneme labels": public-domain audio, Apache- or MIT-licensed audio, and synthetic audio from closed TTS providers. The card excludes synthetic audio from open TTS models and custom voice clones (**Reported**).[^kokoro-82m-card]
- **CC BY inclusions:** the attribution table lists Koniwa `tnc` (under 1 h, CC BY 3.0) and SIWIS (under 11 h, CC BY 4.0) in v1.0, both added after v0.19 on 22 Nov 2024 (**Reported**).[^kokoro-82m-card]
- **Cost:** the card reports 500 A100 80GB GPU hours per release: $400 for v0.19 at $0.80/h and $600 for v1.0 at $1.20/h, about $1,000 in total (**Reported**).[^kokoro-82m-card] These are the card's own figures; no receipts or independent check were captured.

## Architecture and interface

- **Architecture:** the card lists StyleTTS 2 and ISTFTNet as references and states "Decoder only: no diffusion, no encoder release" (**Reported**).[^kokoro-82m-card] Module boundaries and the split of the 82M parameters are not described.
- **Usage path (read, not executed):** the example installs `kokoro>=0.9.2` and `soundfile`, plus `espeak-ng`; it builds `KPipeline(lang_code='a')` and calls `pipeline(text, voice='af_heart')`. The call yields `(gs, ps, audio)` tuples per segment; the card does not define `gs` and `ps`. The example writes each segment at 24,000 Hz (**Observed** from the code block; usage **Reported**).[^kokoro-82m-card]
- **Voices:** 54 for v1.0 per the release table. The voice list sits in a linked `VOICES.md` that was not captured (**Reported**).[^kokoro-82m-card]

## Market cost snapshot

- The card's note says that as of April 2025 the market rate was under $1 per million input characters or under $0.06 per hour of audio output, and that 1,000 input characters is about one minute of output. It cites $0.65 per million characters (ArtificialAnalysis/Replicate) and $0.80 per million (DeepInfra) (**Reported**).[^kokoro-82m-card]
- **Synthesis:** at 60,000 characters per audio hour, the cited rates imply about $0.039–0.048 per hour, which agrees with the card's bound. This is arithmetic on card figures, not a new price check.
- The card has no capture date, so April 2025 is its latest dated statement and the snapshot date is inferred (**Synthesis**). `stale_after` is set to 2026-04-30, twelve months after that snapshot, so lint flags the release, cost, and upstream-state claims for re-verification.

## Trust and provenance

- **Lookalike domains:** the card's caution block says websites with "kokoro" in their root domain that are not the model page or its author are likely scams. It names two such domains, links archived snapshots, and says they are "NOT owned by and NOT affiliated with" the model or author (**Reported**).[^kokoro-82m-card] The snapshots were not inspected.
- **Guidance (Synthesis):** take weights from the official Hugging Face repository and check the v1.0 SHA256 before use. Treat any other kokoro-named download source as unverified.
- **Deployment claims:** "deployed in numerous projects and commercial APIs" is a source assertion (**Reported**), not verified here.

## Licensing

- Weights are Apache-2.0 per frontmatter and the card text (**Reported**).[^kokoro-82m-card]
- The training set includes CC BY 3.0 and CC BY 4.0 audio. The card does not state the attribution obligations for the weights, and this wiki has not evaluated them (**Unverified**).[^kokoro-82m-card]

## Relationships

- Compared in [Kokoro Deployment Comparison](kokoro-deployment-comparison.md): separates embedded inference, dedicated APIs, native GGUF runtimes, pipeline integrations and Vietnamese artifacts; recommendations are synthesis, not a matched benchmark.

- Run by the [Kokoro Python Library](kokoro-python-library.md), the `kokoro` package whose `KPipeline` wraps this model; its README gives the basic and advanced usage cells and the `lang_code` values (**Reported**).[^kokoro-library-readme]
- Served by [Kokoro-FastAPI](kokoro-fastapi.md), a Dockerized FastAPI wrapper that exposes this model through an OpenAI-compatible `/v1/audio/speech` route. Its README names git commit `41e5892` as the tested model revision (**Reported**). That is a git identifier, distinct from the v1.0 file SHA256 above; the two do not conflict (**Synthesis**).[^kokoro-fastapi-readme]
- Uses the StyleTTS 2 and ISTFTNet architecture; the StyleTTS 2 side is described in [StyleTTS 2](styletts2.md).
- Uses the [Misaki](misaki.md) G2P library and depends on [eSpeak NG](espeak-ng.md) (`espeak-ng`) on the usage path.
- [Kokoro Vietnamese](kokoro-vietnamese.md) is a Kokoro-lineage Vietnamese artifact set; the wiki makes no shared-checkpoint claim (**Synthesis**).
- [Speaches](speaches.md) serves `hexgrad/Kokoro-82M` behind an OpenAI-compatible API, and [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) and [RealtimeVoiceChat](realtime-voice-chat.md) list Kokoro among their TTS backends (**Synthesis** from those pages).
- [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) catalogs a `Kokoro-82M-GGUF` row (BF16 and Q8, Apache-2.0). [CrispASR TTS Engines](crispasr-tts-engines.md) reports a `kokoro` backend with a ~135 MB first-use download. Packaged sizes and the card's 82M parameter count are not directly comparable (**Synthesis**).
- [Community-Reported Local ASR/TTS Selection](community-asr-tts-selection.md) relays anonymous comments calling Kokoro a local latency leader. These are unverified anecdotes, not evidence for this card (**Reported** in that page).
- [KVoiceWalk](kvoicewalk.md) uses this model as its synthesis engine to evolve new voice style tensors toward a target recording. Its README reports one example run (target similarity 0.709 for the closest stock voice, 0.917 for the walked tensor) with no independent check (**Reported**).[^kvoicewalk-readme]
- [TTS Model Survey](tts-model-survey.md) compares Kokoro-82M with the other compiled TTS models.

## Contradictions

- **Language coverage:** the frontmatter says `language: - en`, the Model Facts section says "Languages: Multiple", and the v1.0 release row says 8 languages and 54 voices.[^kokoro-82m-card] The wiki records all three and chooses none. The example's `lang_code='a'` is a code, not a language list.
- **Install version floor:** the usage cell above says `kokoro>=0.9.2`, while the library README's cells say `kokoro>=0.9.4` and its sample conda file says `kokoro>=0.3.1`. Neither floor is chosen; the conflict is also recorded in [Kokoro Python Library](kokoro-python-library.md#contradictions) (**Reported**).[^kokoro-82m-card][^kokoro-library-readme]

## Coverage and limits

- **Inspected statically:** the whole capture `raw/Kokoro-82M.md`, including frontmatter, both notes, release and cost tables, usage block, Model Facts, Training Details, attribution table, and acknowledgements (**Observed**).[^kokoro-82m-card]
- **Not executed:** the usage code was not run. No package was installed, no weights were downloaded or hash-checked, and no audio was synthesized.
- **Linked but not captured:** `EVAL.md`, `SAMPLES.md`, and `VOICES.md` (Hugging Face links); the GitHub `hexgrad/kokoro` repository beyond its README, which is compiled in [Kokoro Python Library](kokoro-python-library.md); `hexgrad/misaki` source (its README is compiled as [Misaki](misaki.md)); the demo Space; `samples/HEARME.wav`; the CC BY source datasets; the v0.19 `kLegacy` tree; and the lookalike-domain archives. The missing `EVAL.md` is the main limit: the card's "comparable quality" claim cannot be checked from this capture.
- **Excluded as decorative:** the closing image and the acknowledgement text, except the credits above. The capture contains no credentials, tokens, or private data; the Discord server link is omitted.
- **Source revision:** none recorded beyond the April 2025 pricing note and the release table.

[^kvoicewalk-readme]: [KVoiceWalk README capture](../raw/kvoicewalk.md) — locators: lines 2–4 purpose and Kokoro dependency; lines 25–33 example labels; line 95 walk and replacement; lines 86–99 example figures; line 179 Kokoro synthesis.
[^kokoro-library-readme]: [kokoro library README capture](../raw/kokoro.md) — locators: line 3 package description and PyPI link; lines 10–11 and 32–34 install commands (`kokoro>=0.9.4`); lines 16–24 basic pipeline cell (`KPipeline(lang_code='a')`, `voice='af_heart'`, 24000 Hz write); lines 36–49 advanced setup and `lang_code` comments; lines 61–67 commented sample texts; lines 75–79 voice-tensor alternative; lines 106–119 conda environment (`kokoro>=0.3.1`).
[^kokoro-fastapi-readme]: [Kokoro-FastAPI README capture](../raw/Kokoro-FastAPI.md) — locators: line 1 banner; lines 9–11 tested model-commit badge (`1.0::41e5892`, linked commit `41e5892b9d8b43e56fc560f892312a328a410973`); line 16 wrapper description.
[^kokoro-82m-card]: [Kokoro-82M model card capture](../raw/Kokoro-82M.md) — locators: frontmatter (`license: apache-2.0`, `language: - en`, `base_model: yl4579/StyleTTS2-LJSpeech`, `pipeline_tag: text-to-speech`); opening paragraph (82M, comparable-quality claim); `[!NOTE]` block (April 2025 pricing, 65 and 80 cents per M characters, 1,000 characters ≈ 1 minute); `[!CAUTION]` block (lookalike-domain warning); `### Releases` and `Training Costs` tables; `### Usage` code block (`kokoro>=0.9.2`, `espeak-ng`, `KPipeline(lang_code='a')`, `voice='af_heart'`, `rate=24000`); `### Model Facts` (architecture, architected-by, trained-by, `Languages: Multiple`, model SHA256); `### Training Details` (data policy, dataset size, training cost); `### Creative Commons Attribution` table (Koniwa CC BY 3.0, SIWIS CC BY 4.0); `### Acknowledgements` (decorative image excluded).

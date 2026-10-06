---
type: Concept
title: audio.cpp GGUF Model Packages
description: Catalog of 92 audio.cpp-native GGUF model packages with audio.cpp family names, quantization options, original-model licenses, and TTS/ASR CLI usage.
tags: [stt, tts, gguf, audio-cpp, edge-deployment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: audio-cpp-gguf-readme
    resource: ../raw/audio.cpp-gguf.md
    kind: documentation
    title: audio.cpp GGUF Model Packages
---

audio.cpp GGUF Model Packages is a catalog of 92 audio.cpp-native GGUF conversions of speech models for use with audio.cpp, listing each package directory with its audio.cpp family name, available precisions and quantizations, and original-model license, plus direct-file CLI usage for TTS and ASR tasks (**Reported**).[^audio-cpp-gguf-readme]

## Repository identity and scope

- The collection targets [audio.cpp](https://github.com/0xShug0/audio.cpp): the GGUF files are intended for use with that runtime (**Reported**).[^audio-cpp-gguf-readme]
- Frontmatter declares `pipeline_tag: text-to-speech`, `base_model_relation: quantized`, tags spanning `gguf`, `audio.cpp`, `quantized`, `text-to-speech`, `automatic-speech-recognition`, `voice-conversion`, `text-to-audio`, `audio-to-audio`, `source-separation`, and `speaker-diarization`, and a `base_model` list of upstream checkpoints (including MiniMax-H3, Ace-Step1.5, Qwen3-ASR/TTS variants, VibeVoice, Voxtral-Realtime, VoxCPM2, IndexTTS-2/2.5, and Higgs Audio v3) (**Observed** by static inspection).[^audio-cpp-gguf-readme]
- Conversion details, supported layouts, direct-file loading, sidecar embedding, and compatibility notes live in the external audio.cpp GGUF guide (`docs/gguf.md`); license names follow audio.cpp's external model-license reference, which also records commercial-use conditions and other notes — neither external document was fetched and both sit outside this source's coverage (**Reported**, with unfetched-pointer limit).[^audio-cpp-gguf-readme]

## Package catalog

- The source's `Files` table lists 92 package directories, each with an audio.cpp family key used for CLI `--family` selection, the GGUF precisions/quantizations provided (patterns: `original`, `F32`/`F16`/`BF16`, `Q8`/`Q8_0`, `Q4`/`Q4_0`/`Q4_K`, and combinations such as `BF16 + Q8` or `original + F16 + Q8`), and the governing original-model license (**Reported**).[^audio-cpp-gguf-readme]
- Voice-loop coverage by directory-name signal (**Synthesis** from directory and family names, not a source-stated grouping): `*TTS*`/`tts` directories cover synthesis; `*ASR*`/`asr`/`transcribe`/`aligner` directories cover recognition and alignment; `sortformer_diar`, `pulsevad`, and `smart_turn` cover diarization, VAD, and turn-taking; `*VC*`/`vc`/`rvc`/`seed_vc`/`tone_color_vc`/`meanvc2` cover voice conversion; `*roformer*`/`htdemucs`/`audiosr`/`universr`/`apollo` cover separation and restoration; `stable_audio` and `controlfoley` rows cover music/SFX/text-to-audio generation retained here for catalog completeness although music-only generation is outside the voice-loop core per `SCOPE.md` exclusions.[^audio-cpp-gguf-readme]

| Directory | audio.cpp family | GGUF provided | Original model license |
|---|---|---|---|
| `ACE-Step1.5-GGUF` | `ace_step` | BF16 + Q8 | MIT |
| `Apollo-GGUF` | `apollo` | original | CC-BY-SA-4.0 |
| `AudioSR-GGUF` | `audiosr` | F32 | Apache-2.0 |
| `BS-RoFormer-ep368-GGUF` | `bs_roformer` | Q8 | Apache-2.0 (checkpoint source undocumented) |
| `Breeze-TTS-2-GGUF` | `breeze_tts` | BF16 + Q8 + Q4 | BreezeBlue Research and Non-Commercial License |
| `Canary-180M-Flash-GGUF` | `canary_asr` | F32 + Q8 | CC-BY-4.0 |
| `Chatterbox-GGUF` | `chatterbox` | F16 + Q8 | MIT |
| `Chatterbox-Turbo-GGUF` | `chatterbox_turbo` | Q8 | MIT |
| `Citrinet-ASR-GGUF` | `citrinet_asr` | Q8 | CC-BY-4.0 |
| `Cohere-Transcribe-GGUF` | `cohere_asr` | BF16 + Q8 + Q4_0 | Apache-2.0 |
| `Confucius4-TTS-GGUF` | `confucius4_tts` | original | Apache-2.0 |
| `ControlFoley-GGUF` | `controlfoley` | F32 | CC-BY-NC-4.0 |
| `CosyVoice3-GGUF` | `cosyvoice3` | F32 + Q8 | Apache-2.0 |
| `CrisperWhisper2.0-GGUF` | `crisperwhisper` | BF16 + Q8 + Q4_K | nyra health Non-Commercial Research License |
| `DotTTS-Edit-GGUF` | `dots_tts` | BF16 + Q8 | Apache-2.0 |
| `DotTTS-MF-GGUF` | `dots_tts` | BF16 | Apache-2.0 |
| `DotTTS-SOAR-GGUF` | `dots_tts` | original + BF16 | Apache-2.0 |
| `DramaBox-GGUF` | `dramabox` | Q8 | LTX-2 Community License |
| `FireRedAudio-GGUF` | `firered_audio` | original + Q8 | Apache-2.0 |
| `FireRedTTS3-Base-GGUF` | `fireredtts3` | original + Q8 | Apache-2.0 |
| `FireRedTTS3-Instruct-GGUF` | `fireredtts3` | original + Q8 | Apache-2.0 |
| `Fish-Audio-S2-Pro-GGUF` | `fish_audio` | BF16 + Q8 | Fish Audio Research License |
| `Fun-ASR-Nano-2512-GGUF` | `fun_asr_nano` | F16 + Q8 | Apache-2.0 |
| `GigaAM-ASR-GGUF` | `gigaam_asr` | F16 + F32 | MIT |
| `Granite-Speech-5.0-470M-TurboCTC-GGUF` | `granite5asr` | Q8 | Apache-2.0 |
| `HeartMuLa-GGUF` | `heartmula` | F16 + Q8 | Apache-2.0 |
| `HTDemucs-GGUF` | `htdemucs` | F16 + Q8 | MIT |
| `HTDemucs-6stems-GGUF` | `htdemucs_6stems` | F16 + Q8 | MIT |
| `Higgs-Audio-v3-STT-GGUF` | `higgs_audio_stt` | F16 + Q8 | Apache-2.0 |
| `Higgs-Audio-v3-TTS-4B-GGUF` | `higgs_audio_tts` | BF16 + Q8 | Boson Higgs TTS 3 Research and Non-Commercial License |
| `Hviske-v5.3-GGUF` | `hviske_asr` | Q8 | CC-BY-NC-4.0 |
| `IndexTTS2-GGUF` | `index_tts2` | original + F16 + Q8 | bilibili Model Use License |
| `IndexTTS2.5-GGUF` | `index_tts2` | original + F16 + Q8 | bilibili Model Use License |
| `Inflect-Micro-v2-GGUF` | `inflect_v2` | original | Apache-2.0 |
| `Irodori-TTS-500M-v3-GGUF` | `irodori_tts` | F16 + Q8 | MIT |
| `Irodori-TTS-600M-v3-VoiceDesign-GGUF` | `irodori_tts` | F16 + Q8 | MIT |
| `Irodori-TTS-v4-Small-GGUF` | `irodori_tts` | F16 + Q8 | MIT |
| `KittenTTS-GGUF` | `kitten_tts` | original | Apache-2.0 |
| `Kokoro-82M-GGUF` | `kokoro_tts` | BF16 + Q8 | Apache-2.0 |
| `Kroko-ASR-GGUF` | `kroko_asr` | Q8 | CC-BY-SA |
| `KugelAudio-0-Open-GGUF` | `kugelaudio` | BF16 + Q8 + Q4_K | MIT |
| `MMS-Forced-Aligner-GGUF` | `mms_forced_aligner` | F16 | CC-BY-NC-4.0 |
| `MOSS-TTS-Local-v1.5-GGUF` | `moss_tts_local` | BF16 + Q8 | Apache-2.0 |
| `MOSS-TTS-Nano-100M-GGUF` | `moss_tts_nano` | BF16 + Q8 | Apache-2.0 |
| `MOSS-Transcribe-Diarize-GGUF` | `moss_transcribe_diarize` | BF16 + Q8 + Q4_K | Apache-2.0 |
| `MOSS-VoiceGenerator-GGUF` | `moss_voicegen` | BF16 + F16 codec decode | Apache-2.0 |
| `MagpieTTS-Multilingual-357M-GGUF` | `magpie_tts` | original | NVIDIA Open Model License |
| `Maya1-GGUF` | `maya1` | original + Q8 | Apache-2.0 (Maya1); MIT (SNAC) |
| `MeanVC2-GGUF` | `meanvc2` | F32 + Q4_K | Apache-2.0 |
| `Mel-Band-RoFormer-GGUF` | `mel_band_roformer` | F16 + Q8 | MIT |
| `MiDashengLM-Gen-GGUF` | `midashenglm_gen` | F32 + Q8 | Apache-2.0 |
| `MiniMax-H3-Q4-GGUF` | `minimax_h3` | Q4_K + INT8 DiT option | MiniMax H3 Community License |
| `MioCodec-25Hz-44.1kHz-v2-GGUF` | `miocodec` | original + F16 + Q8 | MIT |
| `MioTTS-1.7B-GGUF` | `miotts` | original + BF16 + Q8 | Apache-2.0 |
| `Moonshine-Streaming-GGUF` | `moonshine_asr` | Q8 | MIT |
| `MuScriptor-Small-GGUF` | `muscriptor` | F32 | CC-BY-NC-4.0 |
| `Nemotron-3.5-ASR-Streaming-0.6B-GGUF` | `nemotron_asr` | F16 + Q8 | OpenMDW-1.1 |
| `NeuTTS-2E-GGUF` | `neutts` | original | NeuTTS Open License v1.0 |
| `Niagara-ASR-GGUF` | `niagara_asr` | F32 | Applied Brain Research Open License v1.1 |
| `OWSM-GGUF` | `owsm` | F32 + Q8 + Q4_K (Small/Medium) | CC-BY-4.0 |
| `OWSM-CTC-GGUF` | `owsm_ctc` | F32 + Q8 | CC-BY-4.0 |
| `OmniVoice-GGUF` | `omnivoice` | BF16 + F16 + Q8 | CC-BY-NC |
| `Parakeet-TDT-0.6B-v3-GGUF` | `parakeet_tdt` | F16 + Q8 | CC-BY-4.0 |
| `PersonaPlex-GGUF` | `personaplex` | Q4_K + Q8 | NVIDIA Open Model License |
| `Piper-TTS-GGUF` | `piper_tts` | original | MIT |
| `PocketTTS-GGUF` | `pocket_tts` | BF16 + Q8 | CC-BY-4.0 |
| `PulseVAD-GGUF` | `pulsevad` | F32 | MIT |
| `Qwen3-ASR-0.6B-GGUF` | `qwen3_asr` | F16 + Q8 | Apache-2.0 |
| `Qwen3-ASR-1.7B-GGUF` | `qwen3_asr` | F16 + Q8 | Apache-2.0 |
| `Qwen3-ForcedAligner-0.6B-GGUF` | `qwen3_forced_aligner` | F16 + Q8 | Apache-2.0 |
| `Qwen3-TTS-12Hz-0.6B-Base-GGUF` | `qwen3_tts` | BF16 + Q8 | Apache-2.0 |
| `Qwen3-TTS-12Hz-1.7B-Base-GGUF` | `qwen3_tts` | original + BF16 + Q8 | Apache-2.0 |
| `Qwen3-TTS-12Hz-1.7B-CustomVoice-GGUF` | `qwen3_tts` | BF16 + Q8 | Apache-2.0 |
| `Qwen3-TTS-12Hz-1.7B-VoiceDesign-GGUF` | `qwen3_tts` | BF16 + Q8 | Apache-2.0 |
| `RVC-GGUF` | `rvc` | F16 | MIT |
| `Samsone-GGUF` | `samsone` | BF16 + Q8 | Not stated |
| `SeedVC-MLX-GGUF` | `seed_vc` | original + F16 + Q8 | GPL-3.0 |
| `Sidon-GGUF` | `sidon` | F32 | MIT |
| `Smart-Turn-v3-GGUF` | `smart_turn` | F32 | BSD-2-Clause |
| `Sortformer-Diar-4spk-v1-GGUF` | `sortformer_diar` | F16 + Q8 | CC-BY-NC-4.0 |
| `Stable-Audio-3-Medium-GGUF` | `stable_audio` | F16 + Q8 | Stability AI Community License |
| `Stable-Audio-3-Small-Music-GGUF` | `stable_audio` | F16 + Q8 | Stability AI Community License |
| `Stable-Audio-3-Small-SFX-GGUF` | `stable_audio` | F16 + Q8 | Stability AI Community License |
| `Supertonic-3-GGUF` | `supertonic` | original + F16 + Q8 | BigScience OpenRAIL-M |
| `Tone-Color-VC-GGUF` | `tone_color_vc` | F32 + F16 | MIT |
| `UniverSR-GGUF` | `universr` | original | CC-BY-4.0 |
| `Vevo2-GGUF` | `vevo2` | original + F16 + Q8 | CC-BY-NC-ND-4.0 |
| `VibeVoice-1.5B-GGUF` | `vibevoice` | BF16 + Q8 + Q4 | MIT |
| `VibeVoice-ASR-GGUF` | `vibevoice_asr` | F16 + Q8 | MIT |
| `VoxCPM1-GGUF` | `voxcpm1` | Q8 + F16 AudioVAE | Apache-2.0 |
| `VoxCPM2-GGUF` | `voxcpm2` | original + BF16 + Q8 | Apache-2.0 |
| `Voxtral-Mini-4B-Realtime-2602-GGUF` | `voxtral_realtime` | BF16 + Q8 + Q4_K | Apache-2.0 |

Table rows are source-reported values as listed in the card's `Files` table; several license cells in the source link to full license texts (BreezeBlue, LTX-2, Fish Audio, Boson Higgs TTS 3, bilibili, NVIDIA Open Model, MiniMax H3, NeuTTS, Applied Brain Research, Stability AI, BigScience OpenRAIL-M) that were not fetched (**Reported**).[^audio-cpp-gguf-readme]

## Usage

- Pass a GGUF file directly as `--model` (**Reported**).[^audio-cpp-gguf-readme]
- TTS example with the Supertonic family on CUDA:

```bash
audiocpp_cli --task tts --family supertonic --model Supertonic-3-GGUF/supertonic-3-orig.gguf --backend cuda --language en --text "Hello." --voice-id M1 --out out.wav
```

(**Reported**).[^audio-cpp-gguf-readme]

- ASR example with the Qwen3-ASR family on CUDA:

```bash
audiocpp_cli --task asr --family qwen3_asr --model Qwen3-ASR-0.6B-GGUF/qwen3-asr-0.6b-f16.gguf --backend cuda --audio speech.wav --text "" --text-out transcript.txt
```

(**Reported**).[^audio-cpp-gguf-readme]

## Quality and licensing caveats

- Converted and quantized packages are checked with automated metrics, but perceived quality can still differ for human listeners; validate the exact package, backend, and route to confirm the output is acceptable for the use case (**Reported**).[^audio-cpp-gguf-readme]
- Each GGUF file is a converted form of its original model, and use and redistribution are governed by the corresponding original model license listed above; review the original model card and license terms before using or redistributing any converted weights (**Reported**).[^audio-cpp-gguf-readme]

## Relationships

- Catalog entry for deployed ASR checkpoints: [Qwen3-ASR family](qwen3-asr-family.md) covers the upstream 0.6B/1.7B checkpoints plus forced aligner (languages, dialects, inference, serving), while this catalog covers their GGUF directory rows (`Qwen3-ASR-0.6B-GGUF`, `Qwen3-ASR-1.7B-GGUF`, `Qwen3-ForcedAligner-0.6B-GGUF`) with families and F16/Q8 options; no shared weight file is asserted (**Synthesis**).[^audio-cpp-gguf-readme]
- Catalog entry for deployed TTS checkpoints: [VoxCPM2](voxcpm2.md) covers the upstream 2B tokenizer-free diffusion-autoregressive TTS model, while this catalog covers its `VoxCPM2-GGUF` row (`voxcpm2`, original + BF16 + Q8, Apache-2.0); no shared weight file is asserted (**Synthesis**).[^audio-cpp-gguf-readme]
- Catalog entry for deployed long-form checkpoints: [VibeVoice-1.5B](vibevoice-1.5b.md) covers the upstream long-form multi-speaker TTS model and [VibeVoice-ASR](vibevoice-asr.md) covers the upstream long-form ASR model, while this catalog covers their `VibeVoice-1.5B-GGUF` (`vibevoice`, BF16 + Q8 + Q4, MIT) and `VibeVoice-ASR-GGUF` (`vibevoice_asr`, F16 + Q8, MIT) rows; no shared weight file is asserted (**Synthesis**).[^audio-cpp-gguf-readme]
- Catalog entry for deployed nano-ASR packaging: [Fun-ASR-Nano GGUF](fun-asr-nano-gguf.md) covers the Fun-ASR-Nano GGUF runtime layout, quantization tiers, and CLI usage in depth, while this catalog covers its `Fun-ASR-Nano-2512-GGUF` row (`fun_asr_nano`, F16 + Q8, Apache-2.0); no shared weight file is asserted (**Synthesis**).[^audio-cpp-gguf-readme]
- Catalog entry for deployed bilingual TTS: [Breeze TTS 2](breeze-tts-2.md) covers the upstream bilingual real-time TTS model, while this catalog covers its `Breeze-TTS-2-GGUF` row (`breeze_tts`, BF16 + Q8 + Q4, non-commercial license); no shared weight file is asserted (**Synthesis**).[^audio-cpp-gguf-readme]
- Catalog entry for deployed multilingual TTS: [OmniVoice](omnivoice.md) covers the upstream 600+-language zero-shot TTS model, while this catalog covers its `OmniVoice-GGUF` row (`omnivoice`, BF16 + F16 + Q8, CC-BY-NC); no shared weight file is asserted (**Synthesis**).[^audio-cpp-gguf-readme]
- Catalog entry alongside sibling diarization packaging: [Nemotron 3 Diarization GGUF](nemotron-3-diarization-gguf.md) covers the Nemotron 3 diarization GGUF with usage and performance figures, while this catalog covers the `Sortformer-Diar-4spk-v1-GGUF` row (`sortformer_diar`, F16 + Q8, CC-BY-NC-4.0); the `Nemotron-3.5-ASR-Streaming-0.6B-GGUF` row here is a different streaming-ASR checkpoint, not the diarization model (**Synthesis**).[^audio-cpp-gguf-readme]

## Coverage and limits

- Source inspected statically only; no GGUF downloaded, no CLI command executed, and no transcription or synthesis output reproduced (**Synthesis**).[^audio-cpp-gguf-readme]
- Linked but unfetched and not in `raw/`: the audio.cpp repository, the `docs/gguf.md` compatibility guide, the model-license reference, all 92 package directories with their GGUF weight files and sidecars, and every upstream checkpoint and license text (**Synthesis**).[^audio-cpp-gguf-readme]
- The source carries no publication date or revision; package availability, quantization options, and license terms can change, so release-sensitive rows carry `stale_after: 2027-10-06` per the domain rules (**Synthesis**).[^audio-cpp-gguf-readme]
- All catalog rows, commands, quality disclaimers, and licensing statements are source assertions without independent verification in this wiki (**Synthesis**).[^audio-cpp-gguf-readme]

[^audio-cpp-gguf-readme]: [audio.cpp GGUF Model Packages](../raw/audio.cpp-gguf.md) — locators: frontmatter (`license`, `pipeline_tag`, `tags`, `base_model_relation: quantized`, `base_model` list); H1 plus intro paragraphs (audio.cpp-native GGUF conversions for audio.cpp, `docs/gguf.md` guide pointer, automated-metrics vs perceived-quality disclaimer); `Files` section (92-row table with `Directory` / `audio.cpp family` / `GGUF provided` / `Original model license` columns; license-name cells linking to BreezeBlue, LTX-2, Fish Audio, Boson Higgs TTS 3, bilibili, NVIDIA Open Model, MiniMax H3, NeuTTS, Applied Brain Research, Stability AI, and BigScience OpenRAIL-M texts); `Usage` section (direct `--model` sentence; TTS fence `audiocpp_cli --task tts --family supertonic --model Supertonic-3-GGUF/supertonic-3-orig.gguf --backend cuda --language en --text --voice-id M1 --out`; ASR fence `audiocpp_cli --task asr --family qwen3_asr --model Qwen3-ASR-0.6B-GGUF/qwen3-asr-0.6b-f16.gguf --backend cuda --audio --text-out`); `License` section (converted-form sentence, original-license governance, review-card-and-license-terms sentence). No date or revision is stated in the source.

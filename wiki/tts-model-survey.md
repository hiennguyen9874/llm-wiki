---
type: Concept
title: TTS Model Survey
description: Survey of every TTS model compiled in the wiki — Qwen3-TTS, CosyVoice2 and Fun-CosyVoice3, Fish Audio S2 Pro, Higgs TTS 3, dots.tts, VoxCPM, Chatterbox, VibeVoice, AuK, Step-Audio-EditX, OmniVoice, Breeze TTS 2, Audio8 TTS, GLM-TTS, GPT-SoVITS, IndexTTS2/2.5, Voxtral TTS, VieNeu-TTS, LGTM-TTS, Irodori, Indic Parler-TTS, and CPU/edge models (Pocket TTS, Sopro, Soprano, Supertonic, MOSS-TTS-Nano, Inflect-Nano, sanoTTS) — compared by architecture, size, languages, streaming latency, cloning and control, license, reported benchmarks, and edge packaging.
tags: [tts, survey, comparison, voice-cloning, streaming, multilingual, benchmarks, edge-deployment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:10:00Z }
stale_after: 2027-10-06
sources:
  - id: qwen3-tts-17b-customvoice-card
    resource: ../raw/Qwen3-TTS-12Hz-1.7B-CustomVoice.md
    kind: documentation
    title: Qwen3-TTS-12Hz-1.7B-CustomVoice model card
  - id: qwen3-tts-06b-customvoice-card
    resource: ../raw/Qwen3-TTS-12Hz-0.6B-CustomVoice.md
    kind: documentation
    title: Qwen3-TTS-12Hz-0.6B-CustomVoice model card
  - id: qwen3-tts-tokenizer-card
    resource: ../raw/Qwen3-TTS-Tokenizer-12Hz.md
    kind: documentation
    title: Qwen3-TTS-Tokenizer-12Hz model card
  - id: faster-qwen3-tts-readme
    resource: ../raw/faster-qwen3-tts.md
    kind: documentation
    title: Faster Qwen3-TTS README
  - id: cosyvoice2-card
    resource: ../raw/CosyVoice2-0.5B.md
    kind: documentation
    title: CosyVoice2-0.5B README and model card
  - id: fun-cosyvoice3-card
    resource: ../raw/Fun-CosyVoice3-0.5B-2512.md
    kind: documentation
    title: Fun-CosyVoice3-0.5B-2512 README and model card
  - id: fish-s2pro-card
    resource: ../raw/s2-pro.md
    kind: documentation
    title: Fish Audio S2 Pro model card
  - id: higgs-v3-card
    resource: ../raw/higgs-audio-v3-tts-4b.md
    kind: documentation
    title: Higgs TTS 3 model card
  - id: dots-tts-soar-card
    resource: ../raw/dots.tts-soar.md
    kind: documentation
    title: dots.tts-soar model card
  - id: dots-tts-mf-card
    resource: ../raw/dots.tts-mf.md
    kind: documentation
    title: dots.tts-mf model card
  - id: voxcpm-05b-card
    resource: ../raw/VoxCPM-0.5B.md
    kind: documentation
    title: VoxCPM-0.5B model card
  - id: voxcpm2-card
    resource: ../raw/VoxCPM2.md
    kind: documentation
    title: VoxCPM2 model card
  - id: chatterbox-card
    resource: ../raw/chatterbox.md
    kind: documentation
    title: Chatterbox TTS
  - id: chatterbox-repo
    resource: ../raw/chatterbox-repo.md
    kind: documentation
    title: Chatterbox TTS GitHub repository README
  - id: vibevoice-1-5b-card
    resource: ../raw/VibeVoice-1.5B.md
    kind: documentation
    title: VibeVoice-1.5B model card
  - id: vibevoice-realtime-0-5b-card
    resource: ../raw/VibeVoice-Realtime-0.5B.md
    kind: documentation
    title: VibeVoice-Realtime-0.5B model card
  - id: vibevoice-7b-gguf-card
    resource: ../raw/VibeVoice-7B-GGUF.md
    kind: documentation
    title: VibeVoice 7B GGUF for audio.cpp
  - id: auk-card
    resource: ../raw/AuK.md
    kind: documentation
    title: AuK model card
  - id: auk-flash-card
    resource: ../raw/AuK-Flash.md
    kind: documentation
    title: AuK-Flash model card
  - id: auk-gguf-card
    resource: ../raw/AuK-Base-and-Flash-GGUF.md
    kind: documentation
    title: AuK GGUF for audio.cpp
  - id: step-audio-editx-readme
    resource: ../raw/Step-Audio-EditX.md
    kind: documentation
    title: Step-Audio-EditX README
  - id: omnivoice-card
    resource: ../raw/OmniVoice.md
    kind: documentation
    title: OmniVoice model card
  - id: breeze-tts-2-card
    resource: ../raw/Breeze-TTS-2.md
    kind: documentation
    title: Breeze TTS 2 model card
  - id: audio8-tts-preview-card
    resource: ../raw/Audio8-TTS-Preview-0.6b.md
    kind: documentation
    title: Audio8 TTS Preview 0.6B model card
  - id: glm-tts-readme
    resource: ../raw/GLM-TTS.md
    kind: documentation
    title: GLM-TTS README and model card
  - id: gpt-sovits-readme
    resource: ../raw/GPT-SoVITS.md
    kind: documentation
    title: GPT-SoVITS-WebUI README
  - id: genie-readme
    resource: ../raw/Genie-TTS.md
    kind: documentation
    title: GENIE GPT-SoVITS Lightweight Inference Engine README
  - id: indextts2-readme
    resource: ../raw/IndexTTS-2.md
    kind: documentation
    title: IndexTTS-2 README fragment
  - id: vieneu-tts-repo
    resource: ../raw/VieNeu-TTS-repo.md
    kind: documentation
    title: VieNeu-TTS GitHub repository README
  - id: vieneu-v3-turbo-card
    resource: ../raw/VieNeu-TTS-v3-Turbo.md
    kind: documentation
    title: VieNeu-TTS v3 Turbo Hugging Face model card (SDK v3.7.1)
  - id: pocket-tts-doc
    resource: ../raw/pocket-tts-without-voice-cloning.md
    kind: documentation
    title: Pocket TTS README and Hugging Face model card
  - id: pocket-tts-repo
    resource: ../raw/pocket-tts-repo.md
    kind: documentation
    title: Pocket TTS GitHub repository README
  - id: soprano-card
    resource: ../raw/Soprano-1.1-80M.md
    kind: documentation
    title: Soprano README and Hugging Face model card
  - id: soprano-80m-card
    resource: ../raw/Soprano-80M.md
    kind: documentation
    title: Soprano-80M README and Hugging Face model card with outdated notice
  - id: supertonic-readme
    resource: ../raw/supertonic.md
    kind: documentation
    title: Supertonic GitHub repository README
  - id: supertonic-2-card
    resource: ../raw/supertonic-2.md
    kind: documentation
    title: Supertonic 2 Hugging Face model card
  - id: supertonic-3-card
    resource: ../raw/supertonic-3.md
    kind: documentation
    title: Supertonic 3 Hugging Face model card
  - id: moss-tts-nano-readme
    resource: ../raw/MOSS-TTS-Nano.md
    kind: documentation
    title: MOSS-TTS-Nano README
  - id: inflect-nano-v1-card
    resource: ../raw/Inflect-Nano-v1.md
    kind: documentation
    title: Inflect-Nano-v1 model card
  - id: sanotts-thread
    resource: ../raw/i_released_sanotts_smallest_complete_tts_stack_in.md
    kind: documentation
    title: sanoTTS release thread
  - id: audio-cpp-gguf-readme
    resource: ../raw/audio.cpp-gguf.md
    kind: documentation
    title: audio.cpp GGUF Model Packages
  - id: sglang-omni-readme
    resource: ../raw/sglang-omni.md
    kind: documentation
    title: SGLang-Omni GitHub README
  - id: vllm-omni-readme
    resource: ../raw/vllm-omni.md
    kind: documentation
    title: vLLM-Omni GitHub README
  - id: speech-to-speech-readme
    resource: ../raw/speech-to-speech.md
    kind: documentation
    title: Speech To Speech README
  - id: speaches-readme
    resource: ../raw/speaches.md
    kind: documentation
    title: Speaches README
  - id: realtimevoicechat-readme
    resource: ../raw/RealtimeVoiceChat.md
    kind: documentation
    title: Real-Time AI Voice Chat README
  - id: reddit-asr-tts-thread
    resource: ../raw/good_asr_and_tts_models.md
    kind: documentation
    title: Good ASR and TTS models? thread capture
  - id: reddit-stt-llm-tts-thread
    resource: ../raw/stt_llm_tts_pipeline.md
    kind: documentation
    title: STT -> LLM -> TTS pipeline thread capture
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
  - id: irodori-v4-large-card
    resource: ../raw/Irodori-TTS-v4-Large.md
    kind: documentation
    title: Irodori-TTS-v4-Large model card
  - id: lgtm-card
    resource: ../raw/LGTM.md
    kind: documentation
    title: LGTM-TTS model card (polyskill/LGTM)
  - id: omnivoice-gguf-card
    resource: ../raw/OmniVoice-GGUF.md
    kind: documentation
    title: OmniVoice GGUF model card
  - id: indic-parler-card
    resource: ../raw/indic-parler-tts.md
    kind: documentation
    title: Indic Parler-TTS model card
  - id: sopro-v2-card
    resource: ../raw/sopro-v2-turbo.md
    kind: documentation
    title: Sopro TTS README and Hugging Face model card (sopro-v2-turbo)
  - id: voxtral-card
    resource: ../raw/Voxtral-4B-TTS-2603.md
    kind: documentation
    title: Voxtral 4B TTS 2603 model card
  - id: indextts25-card
    resource: ../raw/IndexTTS-2.5.md
    kind: documentation
    title: IndexTTS-2.5 model card
  - id: nemo-speech-readme
    resource: ../raw/NeMo-Speech.cpp.md
    kind: documentation
    title: NeMo-Speech.cpp README
  - id: seamless-m4t-v2
    resource: seamless-m4t-v2-large.md
    kind: synthesis
    title: SeamlessM4T v2 Large
---

The master catalog has 35 text-to-speech model/family rows plus six separately linked packagings, codecs, or TTS-specific runtimes (**Observed** catalog count); grouped family variants are not counted as individual checkpoints. They fall into four groups. The largest is LLM-style or codec-token autoregressive cloning models: Qwen3-TTS, CosyVoice2 and Fun-CosyVoice3, Fish Audio S2 Pro, Higgs TTS 3, Audio8 TTS Preview, Breeze TTS 2, GLM-TTS, Chatterbox, IndexTTS2/2.5, Voxtral TTS, MOSS-TTS-Nano, VieNeu-TTS, and Indic Parler-TTS (prompt-controlled Indic). The second is continuous-latent or diffusion models: dots.tts, VoxCPM and VoxCPM2, VibeVoice, OmniVoice, AuK, LGTM-TTS (encoder–duration–vector-estimator–vocoder with iterative denoising), and the Japanese-only Irodori-TTS-v4-Large. The third is the editing and voice-conversion line: Step-Audio-EditX, AuK's editing tasks, and GPT-SoVITS with its Genie-TTS CPU engine. The fourth is CPU, edge, and microcontroller models: Pocket TTS, Sopro V2 Turbo, Soprano, Supertonic, Chatterbox Nano, Inflect-Nano, and sanoTTS. The cited cards support three broad findings. First, zero-shot cloning accuracy on Seed-TTS-eval has converged: about a dozen open models report test-en WER between 1.2% and 2.3% and test-zh CER near or below 1%. Speaker similarity and hard-case CER now separate them more than plain WER does. Second, the lowest claimed streaming time-to-first-audio comes from GPU-served 0.5–4B models (Breeze TTS 2 under 40 ms, Qwen3-TTS 97 ms, Fish S2 Pro ~100 ms, Fun-CosyVoice3 150 ms). Several of those either carry non-commercial weight licenses or reach streaming only through a serving layer. Third, for a deployed voice agent, license, language list, and the CPU/edge path usually decide the choice before benchmark rank does. That matters most for Vietnamese: VieNeu-TTS is the dedicated vi/en line; VoxCPM2, LGTM-TTS, Supertonic 3, Fish S2 Pro and OmniVoice explicitly list vi, and Higgs TTS 3 puts Vietnamese in its under-5 WER/CER tier. dots.tts additionally acknowledges a low-resource Vietnamese WER gap rather than giving a per-language support table. Language listing and vendor tiers are not matched Vietnamese listening results.[^vieneu-v3-turbo-card][^voxcpm2-card][^lgtm-card][^supertonic-3-card][^fish-s2pro-card][^omnivoice-card][^higgs-v3-card][^dots-tts-mf-card] Every number below is a vendor, author, or community claim that this wiki has not reproduced (**Synthesis**).

## Scope and method

- **Included:** every concept whose primary job is turning text into speech. That covers model cards, edit-capable speech-generation foundation models that include TTS tasks, GGUF/ONNX packagings of those models, the Qwen3-TTS codec, and TTS-specific inference wrappers. Retrieval used the root index, the `tts` tag, and exact search for model names inside pipeline, serving, and community pages (**Synthesis**).
- **Adjacent, not surveyed as TTS:** full-duplex speech-to-speech models, voice-agent frameworks, and generic serving runtimes. They are listed under [Adjacent concepts](#adjacent-concepts) and used here only for serving and integration facts (**Synthesis**).
- **Evidence:** model rows are **Reported** by the cited card. Tables that reproduce a competitor's figures cite the card that printed them, not the competitor. Orderings, groupings, and the selection guide are **Synthesis**. Community and LLM-report claims are anecdotal and kept in their own sections.
- **Comparability warning:** the cards do not share one evaluation protocol. Seed-TTS-eval rows differ in text normalizer, ASR judge, reference length, and whether SIM is printed as a percentage or a 0–1 score (converted to percent here). The Audio8 card states that cross-project values are reference comparisons, not matched rankings, and it re-evaluated Fish S2 Pro because Fish uses its own normalizer.[^audio8-tts-preview-card] Latency figures come from different GPUs and harnesses, and some count time to first chunk while others count end-to-end latency. A WER gap under about 0.3 points, or a latency gap under about 2x between different cards, should not drive a decision on its own (**Synthesis**).

## Master catalog

| Model (concept) | Developer | Size | Architecture | Languages | Output | License (weights) | Headline reported result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md) | Qwen | 1.7B (family also has 1.7B Base and VoiceDesign) | discrete multi-codebook LM on [Qwen3-TTS-Tokenizer-12Hz](qwen3-tts-tokenizer-12hz.md) (12.5 Hz, 16 codebooks, causal ConvNet decoder) | 10 (zh, en, ja, ko, de, fr, ru, pt, es, it) | 24 kHz PCM via serving layer | Apache-2.0 | 1.7B-Base Seed-TTS 1.24 en / 0.77 zh; streaming down to 97 ms[^qwen3-tts-17b-customvoice-card][^qwen3-tts-tokenizer-card][^claude-pipeline-report] |
| [Qwen3-TTS-12Hz-0.6B-CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md) | Qwen | 0.6B (also 0.6B Base) | same family; 9 preset timbres, no instruction control at 0.6B | 10 | 24 kHz | Apache-2.0 | 0.6B-Base Seed-TTS 1.32 en / 0.92 zh[^qwen3-tts-06b-customvoice-card][^qwen3-tts-17b-customvoice-card] |
| [CosyVoice2-0.5B](cosyvoice2-0.5b.md) | FunAudioLLM | 0.5B | LLM text-to-token + flow matching, 25 Hz; bi-streaming | 9 (zh, en, fr, es, ja, ko, it, ru, de) | not recorded | Apache-2.0 | Seed-TTS en 2.57 / zh 1.45 / hard 6.83 (own card); vLLM and Triton TRT-LLM paths[^cosyvoice2-card] |
| [Fun-CosyVoice3-0.5B-2512](fun-cosyvoice3-0.5b-2512.md) | FunAudioLLM | 0.5B (base + RL) | LLM-based, CosyVoice 3 recipe | 9 + 18 Chinese dialects/accents | not recorded | Apache-2.0 | RL: en 1.68 / zh 0.81 / hard 5.44; 150 ms bi-streaming[^fun-cosyvoice3-card] |
| [Fish Audio S2 Pro](fish-audio-s2-pro.md) | Fish Audio | 4B slow AR + 400M fast AR | Dual-AR over 10-codebook RVQ (~21 Hz), RL-aligned | 80+ | not recorded | Fish Audio Research License (non-commercial) | RTF 0.195, ~100 ms TTFA on one H200; free-form `[tag]` control[^fish-s2pro-card] |
| [Voxtral 4B TTS 2603](voxtral-4b-tts-2603.md) | Mistral AI | 4B (Ministral-3-3B-Base lineage) | not recorded | 9 (en, fr, es, de, it, pt, nl, ar, hi) | 24 kHz (WAV, PCM, FLAC, MP3, AAC, Opus) | CC-BY-NC-4.0 (inherited from voice-reference datasets) | H200 latency 70 ms at concurrency 1 / 552 ms at 32; 20 preset voices plus reference adaptation[^voxtral-card] |
| [Higgs TTS 3](higgs-tts-3-4b.md) | Boson AI | ~4B | AR LM over Higgs Tokenizer (8×1026 codebooks, 25 fps, delay pattern) | 102 | 24 kHz | Boson research / non-commercial + Creator Use Grant | best on all four suites against 10 baselines in its own table: SeedTTS 1.11 / CV3 4.41 / MiniMax 2.74 / 111-language 3.61[^higgs-v3-card] |
| [dots.tts-soar](dots-tts-soar.md) | dots studio | 2B | continuous AR: semantic encoder + LLM + AR flow-matching head over 48 kHz AudioVAE; SCA post-training | multilingual (24-language MiniMax eval) | 48 kHz | Apache-2.0 | Seed-TTS avg 2.95 WER / 79.2 SIM, best SIM in its table[^dots-tts-soar-card] |
| [dots.tts-mf](dots-tts-mf.md) | dots studio | 2B | MeanFlow distillation of soar, NFE 2–4 | as soar | 48 kHz | Apache-2.0 | NFE=4 avg 2.94 / 78.2, matching the teacher with ~2.5x fewer evaluations[^dots-tts-mf-card] |
| [VoxCPM-0.5B](voxcpm-0.5b.md) | OpenBMB | 0.5B (MiniCPM-4 backbone) | tokenizer-free diffusion-autoregressive | en, zh | not recorded | Apache-2.0 | Seed-TTS en 1.85 / zh 0.93; RTF 0.17 streaming on RTX 4090[^voxcpm-05b-card] |
| [VoxCPM2](voxcpm2.md) | OpenBMB | 2B | tokenizer-free diffusion-AR; AudioVAE V2 (16 kHz in, 48 kHz out) | 30 incl. vi, th, id, ms, km, lo, my, tl | 48 kHz | Apache-2.0 | ~0.3 RTF on RTX 4090 (~0.13 with Nano-vLLM); voice design and cloning[^voxcpm2-card] |
| [Chatterbox TTS](chatterbox-tts.md) | Resemble AI | 0.5B (V3, English, 6 language packs); Turbo 350M; Nano 110M | 0.5B Llama backbone; Turbo/Nano one-step distilled decoder | Multilingual V3: 23; Turbo/Nano: en | not recorded | MIT | emotion exaggeration control; Nano 3x real time on 8 CPU cores; PerTh watermark[^chatterbox-card][^chatterbox-repo] |
| [VibeVoice-1.5B](vibevoice-1.5b.md) | Microsoft Research | 1.5B (Qwen2.5-1.5B) | 7.5 Hz acoustic + semantic tokenizers + diffusion head | en, zh | 24 kHz tokenizer | MIT | up to 90 min with up to 4 speakers[^vibevoice-1-5b-card] |
| [VibeVoice-Realtime-0.5B](vibevoice-realtime-0.5b.md) | Microsoft Research | 0.5B (Qwen2.5-0.5B) | acoustic-only 7.5 Hz tokenizer + diffusion head, interleaved streaming text input | en (9 more exploratory) | not recorded | MIT | ~300 ms first audio; SEED test-en 2.05 WER / 63.3 SIM[^vibevoice-realtime-0-5b-card] |
| [AuK](auk.md) / [AuK-Flash](auk-flash.md) | Tencent Hunyuan | 1.5B (+ Qwen2.5-Omni-3B encoder, VAE) | diffusion transformer with layer fusion; Flash = 4-step distillation | zh, en (Flash card) | 24 kHz (SGLang-Omni, GGUF parity) | MIT | 16 instruction-driven generation and editing tasks; benchmark image-only[^auk-card][^auk-flash-card][^auk-gguf-card] |
| [Step-Audio-EditX](step-audio-editx.md) | StepFun | 3B | dual-codebook tokenizer + audio LLM + flow-matching decoder; GRPO | zh, en, Sichuanese, Cantonese, ja, ko | not recorded | code Apache-2.0; weights unstated | iterative emotion/style/paralinguistic editing; 12–16 GB GPU[^step-audio-editx-readme] |
| [OmniVoice](omnivoice.md) | k2-fsa | Qwen3-0.6B base (total not stated) | diffusion language-model style | 600+ | 24 kHz | code Apache-2.0; weights CC-BY-NC | RTF as low as 0.025; cloning plus attribute voice design[^omnivoice-card] |
| [Breeze TTS 2](breeze-tts-2.md) | BreezeBlue | not stated | text encoder, backbone, and depth decoder stages over a Qwen3-TTS-based audio tokenizer | en, zh | 24 kHz PCM stream | BreezeBlue Research and Non-Commercial | <40 ms TTFA, RTF 0.32 on H100 fast path; #1 open-weight on Artificial Analysis[^breeze-tts-2-card] |
| [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) | Audio8 | 0.6B (excl. codec) | DualAR (24-layer slow + 4-layer fast) over 10-codebook 44.1 kHz codec | 11 recommended | 44.1 kHz | Apache-2.0 | Seed-TTS en 1.506, best in its comparison table; ONNX INT4 CPU[^audio8-tts-preview-card] |
| [GLM-TTS](glm-tts.md) | zai-org | not stated | Llama text-to-token LLM + flow matching; multi-reward GRPO | zh, en (mixed) | not recorded | MIT | GLM-TTS_RL Seed-TTS CER 0.89 / SIM 76.4, lowest CER in its table[^glm-tts-readme] |
| [GPT-SoVITS](gpt-sovits.md) | RVC-Boss | not stated | GPT (s1) + SoVITS (s2) stages; v1–v5 and v2Pro checkpoints | zh, en, ja, ko, yue | v3 24 kHz; v4 native 48 kHz | MIT | 5 s zero-shot, 1 min fine-tune; v2ProPlus RTF 0.014 on RTX 4090[^gpt-sovits-readme] |
| [IndexTTS2](indextts2.md) (draft) | IndexTeam | 1.5B (per VoxCPM table) | autoregressive zero-shot; emotion and duration control claimed | en, zh | not recorded | not in fragment; audio.cpp lists bilibili Model Use License | Seed-TTS en 2.23 / zh 1.03 (VoxCPM card)[^indextts2-readme][^voxcpm-05b-card][^audio-cpp-gguf-readme] |
| [IndexTTS-2.5](indextts-2-5.md) | IndexTeam / Bilibili | ~0.8B GPT backbone (total unstated) | autoregressive GPT + flow-matching speech-to-mel + BigVGAN | 5 (zh, en, ja, es, ar) | 22.05 kHz | bilibili Model Use License Agreement (terms not captured) | single-reference cross-lingual cloning, 8-value emotion vector, Pinyin/CMU/Kana control, speed factor 0.5–2.0; no numeric quality/latency results[^indextts25-card] |
| [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) | Pham Nguyen Ngoc Bao | not stated (Nano preview 48M) | original design trained on ~10k h English–Vietnamese; Nano = flow-matching ONNX | vi, en (code-switching) | 48 kHz (Nano 24 kHz) | Apache-2.0 per card (scope disputed) | ~115 ms TTFA, 16 streams on one RTX 3060; CPU int8 RTF ~0.36[^vieneu-tts-repo][^vieneu-v3-turbo-card] |
| [MOSS-TTS-Nano](moss-tts-nano.md) | OpenMOSS / MOSI.AI | 0.1B | pure AR audio tokenizer + LLM | 20 claimed (19 codes tabled) | 48 kHz stereo | not yet licensed for redistribution at capture | CPU streaming on 4 cores; ONNX, Android, browser, mlx-audio[^moss-tts-nano-readme] |
| [Pocket TTS](pocket-tts.md) | Kyutai | 100M | CPU-first streaming model | 7 (en, fr, de, pt, it, es, nl) | not recorded | CC-BY-4.0 (gated; per-voice licenses) | ~200 ms first chunk; ~6x real time on MacBook Air M4 with 2 cores; voice cloning[^pocket-tts-doc][^pocket-tts-repo] |
| [Sopro V2 Turbo](sopro-v2-turbo.md) | Samuel Vitorino | 120M | lightweight streaming zero-shot cloning model | 4 (en, pt, fr, de) | not recorded | Apache-2.0 | ~300 ms TTFA on laptop CPU; RTF 0.24 offline / 0.21 streaming on M3, 0.07 on H100; browser ONNX[^sopro-v2-card] |
| [Soprano-1.1-80M](soprano-1-1-80m.md) (supersedes [Soprano-80M](soprano-80m.md)) | Soprano | 80M | not recorded | en | 32 kHz | Apache-2.0 | up to 2000x real time on GPU / 20x CPU; <15 ms GPU / <250 ms CPU streaming; no cloning[^soprano-card][^soprano-80m-card] |
| [Supertonic](supertonic.md) / [Supertonic 2](supertonic-2.md) | Supertone | 66M | ONNX on-device, configurable inference steps | v1 en; v2 en, ko, es, pt, fr | not recorded | OpenRAIL-M (code MIT) | M4 Pro CPU RTF 0.012–0.015 at 2 steps; up to 167x real time[^supertonic-readme][^supertonic-2-card] |
| [Supertonic 3](supertonic-3.md) | Supertone | ~99M (public ONNX assets) | ONNX on-device | 31 (en, ko, ja, ar, bg, cs, da, de, el, es, et, fi, fr, hi, hr, hu, id, it, lt, lv, nl, pl, pt, ro, ru, sk, sl, sv, tr, uk, vi) | not recorded | OpenRAIL-M (code MIT) | competitive WER/CER range vs larger open models claimed; figures image-only[^supertonic-3-card] |
| [Inflect-Nano-v1](inflect-nano-v1.md) | owensong | 4.63M incl. vocoder | FastSpeech-style acoustic model + Snake HiFi-GAN | en, one male voice | 24 kHz | Apache-2.0 | sub-5M baseline; no measured quality in card[^inflect-nano-v1-card] |
| [sanoTTS](sanotts.md) (draft) | ampixa | 294k–2.2M | per-component teacher distillation | 6 languages, 11 voices | not recorded | not stated | ESP32 RTF 0.225; 1.51M Amy SCOREQ 4.13 / UTMOS 4.10 (author-reported)[^sanotts-thread] |
| [LGTM-TTS](lgtm-tts.md) | polyskill (card claims built by Claude Opus 5.5) | not stated | text encoder + duration predictor + iterative vector estimator over latents + vocoder; voice encoder for cloning | 11 (en, es, pt, fr, de, it, sv, vi, ja, ko, id) | 44.1 kHz | not stated | 10 built-in voices plus 5–15 s cross-lingual zero-shot cloning; PyTorch and ONNX runtimes[^lgtm-card] |
| [Irodori-TTS-v4-Large](irodori-tts-v4-large.md) | Chihiro Arata | 3.29B (24-layer 2,048-dim DiT; v4 766M → Large) | rectified-flow DiT over continuous Semantic-DACVAE latents (32-dim); shared T5Gemma 2 text/caption encoder | ja only | 48 kHz | Gemma Terms of Use (encoder-derived) + no-impersonation/no-misinformation restrictions | Joyo Parakeet 92.80% acc; Coco-Nut voice-design 4.2991; JVS 120 s cosine 0.7788; SilentCipher watermark[^irodori-v4-large-card] |
| [Indic Parler-TTS](indic-parler-tts.md) | AI4Bharat + Hugging Face audio team | not stated (Parler-TTS Mini lineage) | transcript-plus-caption prompt-controlled; dual prompt/description tokenizers with byte fallback | 21 (20 Indic + en; plus Chhattisgarhi/Kashmiri/Punjabi unofficial) | not recorded | Apache-2.0 | 69 named speakers; NSS finetuned highs Sanskrit 99.79 / Maithili 95.36 / Bodo 94.47; card recommends Indic-Speak successor[^indic-parler-card] |

Packagings and runtimes with their own concepts: [AuK Base and Flash GGUF](auk-base-and-flash-gguf.md), [VibeVoice-7B GGUF](vibevoice-7b-gguf.md), [Qwen3-TTS-Tokenizer-12Hz](qwen3-tts-tokenizer-12hz.md), [Faster Qwen3-TTS](faster-qwen3-tts.md), [Genie-TTS](genie-tts.md), and [OmniVoice GGUF](omnivoice-gguf.md) for omnivoice.cpp (**Synthesis**).

## Zero-shot cloning accuracy (Seed-TTS-eval)

Lower WER/CER is better; higher SIM (speaker similarity, %) is better. Rows are sorted by test-en WER. Each row cites the card that printed it (**Reported**; ordering is **Synthesis**):

| Model | test-en WER / SIM | test-zh CER / SIM | test-hard CER / SIM | Printed by |
| --- | ---: | ---: | ---: | --- |
| Qwen3-TTS-12Hz-1.7B-Base | 1.24 / — | 0.77 / — | — | Qwen3-TTS card[^qwen3-tts-17b-customvoice-card] |
| dots.tts-mf (NFE=4) | 1.29 / 76.2 | 0.94 / 80.0 | 6.60 / 78.5 | dots.tts-mf card[^dots-tts-mf-card] |
| dots.tts-soar | 1.30 / 77.1 | 0.94 / 81.0 | 6.60 / 79.5 | dots.tts-soar card[^dots-tts-soar-card] |
| Qwen3-TTS-12Hz-0.6B-Base | 1.32 / — | 0.92 / — | — | Qwen3-TTS card[^qwen3-tts-17b-customvoice-card] |
| Audio8 TTS Preview 0.6B | 1.506 / 63.2 | 0.950 / 73.1 | 11.510 / 68.7 | Audio8 card[^audio8-tts-preview-card] |
| Fish Audio S2 Pro (re-evaluated) | 1.607 / 64.6 | 1.038 / 73.8 | 10.149 / 70.1 | Audio8 card[^audio8-tts-preview-card] |
| Fun-CosyVoice3-0.5B-2512 RL | 1.68 / 69.5 | 0.81 / 77.4 | 5.44 / 75.0 | Fun-CosyVoice3 card[^fun-cosyvoice3-card] |
| VoxCPM2 | 1.84 / 75.3 | 0.97 / 79.5 | 8.13 / 75.3 | Audio8 and dots.tts-soar cards (VoxCPM2 card defers tables)[^audio8-tts-preview-card][^dots-tts-soar-card] |
| VoxCPM-0.5B | 1.85 / 72.9 | 0.93 / 77.2 | 8.87 / 73.0 | VoxCPM-0.5B card[^voxcpm-05b-card] |
| VibeVoice-Realtime-0.5B | 2.05 / 63.3 | — | — | VibeVoice-Realtime card[^vibevoice-realtime-0-5b-card] |
| IndexTTS2 | 2.23 / 70.6 | 1.03 / 76.5 | — | VoxCPM-0.5B card[^voxcpm-05b-card] |
| Fun-CosyVoice3-0.5B-2512 base | 2.24 / 71.8 | 1.21 / 78.0 | 6.71 / 75.8 | Fun-CosyVoice3 card[^fun-cosyvoice3-card] |
| Seed-TTS (closed reference) | 2.25 / 76.2 | 1.12 / 79.6 | 7.59 / 77.6 | dots.tts-soar card[^dots-tts-soar-card] |
| CosyVoice2-0.5B | 2.57 / 65.9 | 1.45 / 75.7 | 6.83 / 72.4 | CosyVoice2 card; other cards differ, see [Contradictions](#contradictions)[^cosyvoice2-card] |
| GLM-TTS_RL / GLM-TTS base | — | 0.89 / 76.4 and 1.03 / 76.1 | — | GLM-TTS card (CER column, split not named)[^glm-tts-readme] |

- Higgs TTS 3 publishes only a macro-averaged SeedTTS figure (1.11, ×100), so it has no per-split row. It also reports CV3 4.41, MiniMax-Multilingual 2.74, and an internal 111-language set at 3.61, ahead of OmniVoice (1.21 / 4.92 / 2.98 / 3.63), Fish S2 Pro (1.31 / 4.60 / 5.15 / 8.68), and Qwen3-TTS-1.7B (1.30 / 7.73 / 27.41 / 97.09) in its own table (**Reported**).[^higgs-v3-card]
- On multilingual suites, dots.tts-soar reports the highest average SIM (83.9) across MiniMax Multilingual's 24 languages, at 6.8 average WER versus VoxCPM2 5.7 / 82.3 and Fish S2 3.7 / 78.0 (**Reported**).[^dots-tts-soar-card] The Audio8 CV3 table gives per-language error rates for 11 languages, with Audio8 competitive against the much larger Fish S2 Pro, Higgs Audio v2, CosyVoice3-1.5B, and VoxCPM2 (**Reported**).[^audio8-tts-preview-card]
- Hard-case and similarity results diverge from the English WER order. Fun-CosyVoice3 RL has the lowest test-hard CER (5.44), while Audio8 and Fish S2 Pro sit above 10. dots.tts and VoxCPM2 lead SIM, while Audio8 and Fish S2 Pro trail it. A model that wins on WER alone may still clone voices less faithfully (**Synthesis**).
- Higgs TTS 3 leads Emergent-TTS judge win-rate overall at 53.65%. OmniVoice leads the Emotions column (61.07%) and Qwen3-TTS-1.7B leads Complex Pronunciation (30.00%) (**Reported**).[^higgs-v3-card] dots.tts-soar posts 65.7% on EmergentTTS Syntactic Complexity against `gpt-4o-mini-tts` (**Reported**).[^dots-tts-soar-card]
- Qwen3-TTS 12Hz-1.7B VoiceDesign leads the open voice-design rows on InstructTTSEval (APS/DSD/RP: ZH 85.2/81.1/65.1, EN 82.9/82.4/68.4) (**Reported**).[^qwen3-tts-17b-customvoice-card]

## Multilingual coverage

| Coverage tier | Models (language count as reported) |
| --- | --- |
| Massive (80+) | [OmniVoice](omnivoice.md) 600+; [Higgs TTS 3](higgs-tts-3-4b.md) 102; [Fish Audio S2 Pro](fish-audio-s2-pro.md) 80+ — all three with non-commercial weights[^omnivoice-card][^higgs-v3-card][^fish-s2pro-card] |
| Broad (20–31) | [Supertonic 3](supertonic-3.md) 31 (incl. Vietnamese); [VoxCPM2](voxcpm2.md) 30 (incl. Vietnamese, Thai, Indonesian, Malay, Khmer, Lao, Burmese, Tagalog); [Chatterbox](chatterbox-tts.md) Multilingual V3 23 + 6 single-language packs; [Indic Parler-TTS](indic-parler-tts.md) 21 (20 Indic + en); [MOSS-TTS-Nano](moss-tts-nano.md) 20 claimed[^supertonic-3-card][^voxcpm2-card][^chatterbox-card][^indic-parler-card][^moss-tts-nano-readme] |
| Mid (4–11) | [Audio8 TTS Preview](audio8-tts-preview-0.6b.md) 11; [LGTM-TTS](lgtm-tts.md) 11; [Qwen3-TTS](qwen3-tts-12hz-1.7b-customvoice.md) 10; [CosyVoice2](cosyvoice2-0.5b.md) 9; [Fun-CosyVoice3](fun-cosyvoice3-0.5b-2512.md) 9 + 18 Chinese dialects; [Voxtral 4B TTS 2603](voxtral-4b-tts-2603.md) 9 (en, fr, es, de, it, pt, nl, ar, hi); [Pocket TTS](pocket-tts.md) 7; [Sopro V2 Turbo](sopro-v2-turbo.md) 4 (en, pt, fr, de); [sanoTTS](sanotts.md) 6; [Step-Audio-EditX](step-audio-editx.md) 4 + 2 dialects; [GPT-SoVITS](gpt-sovits.md) 5; [Supertonic 2](supertonic-2.md) 5[^audio8-tts-preview-card][^lgtm-card][^qwen3-tts-17b-customvoice-card][^cosyvoice2-card][^fun-cosyvoice3-card][^voxtral-card][^pocket-tts-repo][^sopro-v2-card][^sanotts-thread][^step-audio-editx-readme][^gpt-sovits-readme][^supertonic-2-card] |
| Bilingual en + zh | [Breeze TTS 2](breeze-tts-2.md), [GLM-TTS](glm-tts.md), [VoxCPM-0.5B](voxcpm-0.5b.md), [VibeVoice-1.5B](vibevoice-1.5b.md), [IndexTTS2](indextts2.md), [AuK-Flash](auk-flash.md)[^breeze-tts-2-card][^glm-tts-readme][^voxcpm-05b-card][^vibevoice-1-5b-card][^indextts2-readme][^auk-flash-card] |
| Five-language IndexTeam successor | [IndexTTS-2.5](indextts-2-5.md): zh, en, ja, es, ar; adds three languages to IndexTTS2, without a Vietnamese or streaming claim[^indextts25-card] |
| Vietnamese-specific | [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) (vi + en code-switching)[^vieneu-v3-turbo-card] |
| Japanese only | [Irodori-TTS-v4-Large](irodori-tts-v4-large.md) (ja only; kanji-reading errors slightly above v4.1-Small)[^irodori-v4-large-card] |
| English only | [Soprano-1.1-80M](soprano-1-1-80m.md), [Supertonic](supertonic.md) v1, Chatterbox Turbo/Nano, [VibeVoice-Realtime-0.5B](vibevoice-realtime-0.5b.md), [Inflect-Nano-v1](inflect-nano-v1.md)[^soprano-card][^supertonic-readme][^chatterbox-repo][^vibevoice-realtime-0-5b-card][^inflect-nano-v1-card] |

- Qwen3-TTS has no Vietnamese. Community fine-tunes from 1.7B-Base exist but are unbenchmarked, with unclear data licenses (**Reported** by an LLM-generated report).[^claude-pipeline-report]
- Chinese dialect control is strongest in Fun-CosyVoice3 (18+ dialects via instruct), Step-Audio-EditX (Sichuanese and Cantonese tags), and CosyVoice2's dialect instruction (**Reported**).[^fun-cosyvoice3-card][^step-audio-editx-readme][^cosyvoice2-card]
- Pocket TTS uses larger, slower 24-layer variants for non-English languages (**Reported**).[^pocket-tts-doc]

## Streaming and latency

Claimed first-audio latency and speed. RTF below 1 means faster than real time; "Nx" speeds are multiples of real time (**Reported** per row):

| Model | First audio | Speed | Hardware / conditions |
| --- | --- | --- | --- |
| Breeze TTS 2 | <40 ms TTFA | RTF 0.32 | H100, warmed `--fast-all` path; ~7.7 GiB eager / ~14.4 GiB fast[^breeze-tts-2-card] |
| Soprano-1.1-80M | <15 ms GPU / <250 ms CPU | up to 2000x GPU (long input or large batch) / 20x CPU | unspecified[^soprano-card] |
| Qwen3-TTS 12Hz | 97 ms end-to-end | — | no protocol in the card. The official `qwen-tts` package returns audio only after full generation, so streaming comes from vLLM-Omni (TTFP 64 ms at concurrency 1 per its docs) or forks[^qwen3-tts-06b-customvoice-card][^claude-pipeline-report] |
| Faster Qwen3-TTS (0.6B / 1.7B) | 156 / 174 ms (RTX 4090); 228 / 241 ms (H100); 597 / 693 ms (Jetson AGX Orin) | 4.78x / 4.22x (RTX 4090) | CUDA graphs, `chunk_size=8`, includes tokenization[^faster-qwen3-tts-readme] |
| Fish Audio S2 Pro | ~100 ms TTFA | RTF 0.195; 3,000+ acoustic tokens/s at RTF <0.5 | one H200, SGLang engine; no protocol stated[^fish-s2pro-card] |
| [Voxtral 4B TTS 2603](voxtral-4b-tts-2603.md) | numeric TTFA not identified; table labels 70 / 552 ms as latency at concurrency 1 / 32 | RTF 0.103 at 1 / 0.302 at 32; 119–1431 char/s/GPU | one H200, vLLM-Omni `end2end.py`, 500-char text + 10 s reference[^voxtral-card] |
| VieNeu-TTS v3 Turbo | ~115 ms (1 stream), 185 ms median (16 streams); CPU int8 140–195 ms | GPU streaming RTF 0.49–0.59; CPU int8 RTF 0.35–0.37 | RTX 3060 12 GB / i5 12th gen, September 2026[^vieneu-tts-repo] |
| Fun-CosyVoice3-0.5B | as low as 150 ms | — | bi-streaming; hardware not stated[^fun-cosyvoice3-card] |
| Pocket TTS | ~200 ms first chunk | ~6x | MacBook Air M4 CPU, 2 cores[^pocket-tts-doc] |
| Sopro V2 Turbo | ~300 ms TTFA | RTF 0.24 offline / 0.21 streaming (M3 CPU); 0.07 (H100) | laptop CPU / M3 CPU / H100; no protocol stated[^sopro-v2-card] |
| VibeVoice-Realtime-0.5B | ~300 ms | — | hardware dependent; streaming text input[^vibevoice-realtime-0-5b-card] |
| Higgs TTS 3 | sub-second (SSE stream) | concurrency 1: 617 ms full response, RTF 0.147; concurrency 16: 14.74 req/s, RTF 0.262 | 1x H100, SGLang Omni, bf16, Seed-TTS EN[^higgs-v3-card] |
| Supertonic / Supertonic 2 | — | RTF 0.012–0.015 (M4 Pro CPU), 0.001–0.005 (RTX 4090) at 2 steps | ONNX CPU/WebGPU; PyTorch on RTX 4090[^supertonic-readme][^supertonic-2-card] |
| Supertonic 3 | — | ~99M on-device; CPU-fast vs A100-GPU baselines claimed | no numeric RTF/TTFA in card (figure image-only)[^supertonic-3-card] |
| OmniVoice | — | RTF as low as 0.025 | not stated[^omnivoice-card] |
| GPT-SoVITS v2ProPlus | — | RTF 0.014 (RTX 4090), 0.028 (RTX 4060 Ti), 0.526 (M4 CPU) | no protocol[^gpt-sovits-readme] |
| VoxCPM-0.5B / VoxCPM2 | — | RTF 0.17 / ~0.3 (~0.13 with Nano-vLLM) | RTX 4090 streaming[^voxcpm-05b-card][^voxcpm2-card] |
| VibeVoice-7B GGUF | — | RTF ~0.18; 13.3 GB peak VRAM | RTX 5090, Q8_0, audio.cpp server sanity check[^vibevoice-7b-gguf-card] |
| Chatterbox Nano | — | 3x | 8 CPU cores[^chatterbox-repo] |
| MagpieTTS Multilingual via [NeMo-Speech.cpp](nemo-speech-cpp.md) (runtime-only evidence) | 9 ms GPU / 203 ms CPU TTFA | 60× GPU / 2.7× CPU | Q8_0, 186 ms audio chunks, RTX 4090 / unnamed CPU; inter-chunk compute 3 / 64 ms; `BENCHMARK.md` unavailable[^nemo-speech-readme] |
| Genie-TTS (GPT-SoVITS V2) | 1.13 s first inference | — | CPU i7-13620H, 100 Japanese sentences[^genie-readme] |
| sanoTTS | — | RTF 0.225 | ESP32-class MCU (author-reported)[^sanotts-thread] |

- No numeric latency figure is recorded for CosyVoice2, GLM-TTS, dots.tts-mf (NFE=4 only), MOSS-TTS-Nano (described as CPU-friendly on 4 cores), Step-Audio-EditX, AuK-Flash (4 steps), Audio8, LGTM-TTS, Indic Parler-TTS, IndexTTS-2.5 (faster than IndexTTS2 claimed without figures), Chatterbox Turbo, or Supertonic 3 (qualitative CPU-fast claim only) (**Reported** absence).[^cosyvoice2-card][^glm-tts-readme][^dots-tts-mf-card][^moss-tts-nano-readme][^step-audio-editx-readme][^auk-flash-card][^audio8-tts-preview-card][^lgtm-card][^indic-parler-card][^indextts25-card][^chatterbox-repo][^supertonic-3-card]
- Streaming is not the same as incremental audio in every integration. The HF speech-to-speech OmniVoice handler exposes no incremental audio, so its first block waits for the full utterance. That pipeline's default Qwen3-TTS setting also uses `--qwen3_tts_non_streaming_mode True` (**Reported**).[^speech-to-speech-readme]
- Faster Qwen3-TTS reports that an RTX 4090 beats an H100 on single-stream work because of higher clocks (**Reported**). For one-user voice agents, a fast consumer GPU can therefore out-perform a datacenter card (**Synthesis**).[^faster-qwen3-tts-readme]

## Capability matrix

✅ = claimed by the cited card; — = not claimed or not recorded (**Reported**; matrix assembly is **Synthesis**):

| Model | Zero-shot cloning | Voice design (no reference) | Instruction / style control | Inline tags / paralinguistics | Speech editing | Multi-speaker long-form | Fine-tuning code |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3-TTS 12Hz | ✅ Base only (3 s) | ✅ 1.7B VoiceDesign | ✅ 1.7B CustomVoice | — | — | — | ✅ Base |
| CosyVoice2 / Fun-CosyVoice3 | ✅ incl. cross-lingual | — | ✅ `inference_instruct2` (dialect, emotion, speed, volume) | — | — | — | GRPO training (CosyVoice2) |
| Fish Audio S2 Pro | scored on clone suites by other cards | — | ✅ free-form `[tag]` | ✅ | — | — | ✅ |
| [Voxtral 4B TTS 2603](voxtral-4b-tts-2603.md) | ✅ (10 s reference; 20 presets) | — | ✅ expressive prosody and emotional range | — | — | — | — |
| Higgs TTS 3 | ✅ | — | ✅ inline emotion/style/prosody/pause | ✅ incl. sound effects | — | — | — |
| dots.tts | ✅ | — | — | — | DotTTS-Edit GGUF package listed | — | ✅ base/soar |
| VoxCPM2 | ✅ controllable + "ultimate" | ✅ | ✅ | — | — | — | ✅ |
| Chatterbox | ✅ | — | ✅ exaggeration + CFG | ✅ Turbo/Nano tags | voice-conversion script | — | — |
| VibeVoice-1.5B | — | — | — | — | — | ✅ 90 min, 4 speakers | — |
| AuK / AuK-Flash | ✅ | ✅ Instruct TTS | ✅ | ✅ nonverbal editing | ✅ 16 tasks incl. content, pitch, speed, emotion, de-accent, separation | — | delegated to repository |
| Step-Audio-EditX | ✅ | — | ✅ 14 emotion + 32 style tags | ✅ 22 paralinguistic tags | ✅ iterative | — | ✅ GRPO |
| OmniVoice | ✅ | ✅ attributes | — | ✅ `[laughter]`, pinyin/phoneme | — | — | — |
| Breeze TTS 2 | ✅ | ✅ | ✅ voice direction | ✅ vocal events | — | — | — |
| GLM-TTS | ✅ 3–10 s | — | ✅ RL emotion | — | — | — | — |
| GPT-SoVITS | ✅ 5 s | — | — | — | — | — | ✅ 1 min few-shot |
| IndexTTS-2.5 | ✅ single reference, cross-lingual | — | ✅ 8-value emotion vector; text emotion needs QwenEmotion | ✅ `<word\|reading>` Pinyin/CMU/Kana; speed factor 0.5–2.0 | — | segmented long text; no multi-speaker claim | —[^indextts25-card] |
| VieNeu-TTS v3 Turbo | ✅ 3–8 s | — | — | experimental emotion cues | — | — | ✅ LoRA |
| Pocket TTS / MOSS-TTS-Nano / Audio8 / Sopro V2 Turbo | ✅ (Sopro 5–20 s) | — | — | — | — | — | MOSS ✅; Audio8 SFT upstream |
| Soprano / Supertonic incl. [Supertonic 3](supertonic-3.md) / Inflect-Nano / sanoTTS | — (preset voices; Supertonic 3 adds `<laugh>`/`<breath>`/`<sigh>` tags plus Voice Builder custom styles) | — | Inflect: length/pitch/energy scales | — | — | — | — |
| Irodori-TTS-v4-Large | ✅ up to 120 s combined (concatenated short clips recommended) | ✅ caption-only voice design | ✅ caption-guided emotion/style | ✅ emoji-driven style + non-verbal effects | — | — | — |
| LGTM-TTS | ✅ 5–15 s, cross-lingual | — (10 presets) | — (steps/speed/silence only) | — | — | — | — |
| Indic Parler-TTS | 69 named-speaker presets (consistency by name in caption), no zero-shot reference cloning claimed | — | ✅ caption-driven emotion/pitch/rate/reverb/quality + accent style transfer | — | — | — | — |

Row sources:[^qwen3-tts-17b-customvoice-card][^claude-pipeline-report][^cosyvoice2-card][^fun-cosyvoice3-card][^fish-s2pro-card][^higgs-v3-card][^dots-tts-soar-card][^voxcpm2-card][^chatterbox-card][^chatterbox-repo][^vibevoice-1-5b-card][^auk-card][^step-audio-editx-readme][^omnivoice-card][^omnivoice-gguf-card][^breeze-tts-2-card][^glm-tts-readme][^gpt-sovits-readme][^vieneu-tts-repo][^pocket-tts-doc][^moss-tts-nano-readme][^audio8-tts-preview-card][^lgtm-card][^soprano-card][^supertonic-readme][^inflect-nano-v1-card][^sanotts-thread][^audio-cpp-gguf-readme][^irodori-v4-large-card][^indic-parler-card][^sopro-v2-card][^voxtral-card][^supertonic-3-card]

- Provenance safeguards: Chatterbox embeds a PerTh neural watermark in every file. VibeVoice embeds an audible AI disclaimer plus an imperceptible watermark. Higgs TTS 3's Creator Use Grant requires on-air or prominent credit. Irodori-TTS-v4-Large applies a SilentCipher invisible watermark to generated outputs (**Reported**).[^chatterbox-repo][^vibevoice-1-5b-card][^higgs-v3-card][^irodori-v4-large-card]

## Edge, CPU, and packaged deployment

| Target | Options |
| --- | --- |
| Microcontroller | [sanoTTS](sanotts.md): 294k-param INT8 at 337 KB, ESP32-S3 class (draft, author-reported)[^sanotts-thread] |
| Tiny CPU baseline | [Inflect-Nano-v1](inflect-nano-v1.md): 4.63M, PyTorch, `--device cpu`[^inflect-nano-v1-card] |
| CPU-first small models | [Supertonic](supertonic.md) / [Supertonic 2](supertonic-2.md) (66M ONNX, examples in 11 runtimes incl. browser WebGPU)[^supertonic-readme]; [Supertonic 3](supertonic-3.md) (~99M ONNX, 31 langs, preset plus Voice Builder custom voices, expression tags)[^supertonic-3-card]; [Pocket TTS](pocket-tts.md) (100M, community WASM/browser ports)[^pocket-tts-repo]; [Sopro V2 Turbo](sopro-v2-turbo.md) (120M, laptop-CPU streaming plus browser ONNX with quantized mobile path)[^sopro-v2-card]; [Soprano-1.1-80M](soprano-1-1-80m.md) (CUDA/CPU/MPS)[^soprano-card]; Chatterbox Nano (110M)[^chatterbox-repo]; [MOSS-TTS-Nano](moss-tts-nano.md) (ONNX CPU, Android example, browser reader, mlx-audio)[^moss-tts-nano-readme] |
| Quantized CPU builds of larger models | [Audio8 TTS Preview](audio8-tts-preview-0.6b.md) ONNX INT4[^audio8-tts-preview-card]; [LGTM-TTS](lgtm-tts.md) ONNX via ONNX Runtime with no PyTorch required (quantization unstated)[^lgtm-card]; [VieNeu-TTS](vieneu-tts-v3-turbo.md) torch-free ONNX int8 plus the 48M Nano preview (282 MB)[^vieneu-tts-repo]; [Genie-TTS](genie-tts.md) ONNX GPT-SoVITS (~200 MB runtime)[^genie-readme] |
| Jetson / Apple Silicon | [Faster Qwen3-TTS](faster-qwen3-tts.md): CUDA graphs on Jetson AGX Orin (0.6B 597 ms TTFA) and an experimental GGML backend for CUDA/Metal[^faster-qwen3-tts-readme]; HF speech-to-speech runs 6-bit Qwen3-TTS through MLX Audio[^speech-to-speech-readme] |
| audio.cpp GGUF | Concepts: [AuK Base and Flash GGUF](auk-base-and-flash-gguf.md) (16-task C++/Python waveform cosine ≥0.99999 at FP32; quantized components not parity-validated)[^auk-gguf-card] and [VibeVoice-7B GGUF](vibevoice-7b-gguf.md)[^vibevoice-7b-gguf-card]. The [catalog](audio-cpp-gguf-packages.md) adds Breeze-TTS-2, Chatterbox and Chatterbox-Turbo, CosyVoice3, DotTTS (Edit/MF/SOAR), Fish S2 Pro, Higgs v3, IndexTTS2/2.5, MOSS-TTS-Nano, OmniVoice, PocketTTS, Qwen3-TTS (0.6B/1.7B Base, CustomVoice, VoiceDesign), Supertonic-3, VibeVoice-1.5B, VoxCPM1, and VoxCPM2[^audio-cpp-gguf-readme] |
| omnivoice.cpp GGUF | [OmniVoice GGUF](omnivoice-gguf.md): paired base (Qwen3 0.6B) plus tokenizer (HuBERT + DAC + RVQ) files in F32 / BF16 / Q8_0 (recommended) / Q4_K_M, `GGML_BACKEND` selection across CUDA / Vulkan / Metal / CPU, F32-kept RVQ and Snake-alpha plus F16 non-alignable conv rows, CC-BY-NC conversion terms[^omnivoice-gguf-card] |

## Licensing

| License class | Models |
| --- | --- |
| Permissive weights (Apache-2.0 / MIT) | Apache-2.0: Qwen3-TTS, CosyVoice2, Fun-CosyVoice3, dots.tts, VoxCPM-0.5B, VoxCPM2, Audio8 TTS Preview, Sopro V2 Turbo, Soprano, Inflect-Nano, Indic Parler-TTS. MIT: Chatterbox, VibeVoice, AuK/AuK-Flash, GLM-TTS, GPT-SoVITS[^qwen3-tts-17b-customvoice-card][^cosyvoice2-card][^fun-cosyvoice3-card][^dots-tts-soar-card][^voxcpm-05b-card][^voxcpm2-card][^audio8-tts-preview-card][^sopro-v2-card][^soprano-card][^inflect-nano-v1-card][^indic-parler-card][^chatterbox-card][^vibevoice-1-5b-card][^auk-card][^glm-tts-readme][^gpt-sovits-readme] |
| Permissive with conditions | Pocket TTS CC-BY-4.0, gated, with per-voice licenses[^pocket-tts-doc]; Supertonic / Supertonic 2 / Supertonic 3 OpenRAIL-M (code MIT)[^supertonic-readme][^supertonic-2-card][^supertonic-3-card]; VieNeu v3 Turbo Apache-2.0 per card, but see [Contradictions](#contradictions)[^vieneu-v3-turbo-card] |
| Non-commercial weights | Breeze TTS 2 (BreezeBlue R&NC; code Apache-2.0)[^breeze-tts-2-card]; Fish Audio S2 Pro (Fish Audio Research License)[^fish-s2pro-card]; Higgs TTS 3 (Boson R&NC + Creator Use Grant; no API hosting or product embedding without a commercial license)[^higgs-v3-card]; OmniVoice (CC-BY-NC weights, Apache-2.0 code) with its omnivoice.cpp GGUF conversion carrying the same CC-BY-NC terms[^omnivoice-card][^omnivoice-gguf-card]; [Voxtral 4B TTS 2603](voxtral-4b-tts-2603.md) (CC-BY-NC-4.0 inherited from EARS/CML-TTS/IndicVoices-R/Arabic Natural Audio voice references)[^voxtral-card] |
| Vendor model-use license | [IndexTTS-2.5](indextts-2-5.md): bilibili Model Use License Agreement; `LICENSE` not captured, so commercial permission is not established by this card[^indextts25-card] |
| Gemma Terms of Use | [Irodori-TTS-v4-Large](irodori-tts-v4-large.md) (shared encoder derived from google/t5gemma-2-1b-1b), plus no-impersonation and no-misinformation ethical restrictions[^irodori-v4-large-card] |
| Unclear or unstated | [LGTM-TTS](lgtm-tts.md) (no license stated in source)[^lgtm-card]; MOSS-TTS-Nano (not yet licensed for redistribution at capture)[^moss-tts-nano-readme]; IndexTTS2 (fragment silent; the audio.cpp catalog lists the bilibili Model Use License)[^indextts2-readme][^audio-cpp-gguf-readme]; Step-Audio-EditX weights[^step-audio-editx-readme]; sanoTTS[^sanotts-thread] |

## Serving runtimes

| Runtime | TTS models served | Notes |
| --- | --- | --- |
| [SGLang-Omni](sglang-omni.md) | Higgs Audio v3, MOSS-TTS and MOSS-TTS Local, Fish S2-Pro, Qwen3-TTS, Voxtral TTS, Ming-Omni-TTS, dots.tts, ZONOS2, AuK/AuK-Flash | `/v1/audio/speech` with batch, streaming, and uploaded voices[^sglang-omni-readme] |
| [vLLM-Omni](vllm-omni.md) | Qwen3-TTS, AuK, Breeze-TTS-2, CosyVoice3; Higgs TTS 3 via `vllm-omni serve`; [Voxtral 4B TTS 2603](voxtral-4b-tts-2603.md) via `vllm serve ... --omni` (recommended stack per its card) | OpenAI-compatible; streaming PCM for Qwen3-TTS[^vllm-omni-readme][^higgs-v3-card][^claude-pipeline-report][^voxtral-card] |
| [Faster Qwen3-TTS](faster-qwen3-tts.md) | Qwen3-TTS 0.6B/1.7B Base, CustomVoice, VoiceDesign | CUDA graphs, OpenAI-compatible server, 4 KB precomputed speaker embeddings[^faster-qwen3-tts-readme] |
| Vendor engines | CosyVoice2 vLLM and Triton TRT-LLM; Fish SGLang engine; Breeze single-concurrency streaming API; VieNeu OpenAI-compatible `/v1/audio/speech` with a 16-stream cap; Soprano OpenAI-compatible endpoint; Pocket TTS local server; Genie FastAPI | [^cosyvoice2-card][^fish-s2pro-card][^breeze-tts-2-card][^vieneu-tts-repo][^soprano-card][^pocket-tts-doc][^genie-readme] |
| [audio.cpp Framework](audio-cpp-framework.md) | GGUF families listed above | CLI / server / WebUI[^audio-cpp-gguf-readme] |
| [NeMo-Speech.cpp](nemo-speech-cpp.md) | MagpieTTS Multilingual 357M + NeMo NanoCodec (22 kHz); no dedicated model/codec concepts yet | Native ggml CLI, local HTTP speech route/OpenAI-compatible subset, separate Riva gRPC, C SDK; runtime Apache-2.0 does not establish weight permissions[^nemo-speech-readme] |
| Voice pipelines | [HF Speech-to-Speech](speech-to-speech-pipeline.md): Qwen3-TTS default plus Kokoro-82M, Pocket TTS, ChatTTS, OmniVoice, MMS, OpenAI-compatible; [Speaches](speaches.md): Piper and Kokoro; [RealtimeVoiceChat](realtime-voice-chat.md): RealtimeTTS with Coqui, Kokoro, or Orpheus | [^speech-to-speech-readme][^speaches-readme][^realtimevoicechat-readme] |

## Selection guide

This section is agent **Synthesis** from the evidence above. Validate any choice with golden clips in the target language and voice, because no figure here has been reproduced.

- **Realtime English/Chinese voice agent with a commercial license:** serve Qwen3-TTS 0.6B or 1.7B through [Faster Qwen3-TTS](faster-qwen3-tts.md) or [vLLM-Omni](vllm-omni.md) for 150–250 ms TTFA on one consumer GPU. Choose [Fun-CosyVoice3](fun-cosyvoice3-0.5b-2512.md) for 150 ms bi-streaming plus Chinese dialects. Use [dots.tts-mf](dots-tts-mf.md) when cloning fidelity matters more than a published latency number.
- **Lowest latency regardless of license:** [Breeze TTS 2](breeze-tts-2.md) (<40 ms on H100) and [Fish Audio S2 Pro](fish-audio-s2-pro.md) (~100 ms on H200). [Voxtral 4B TTS 2603](voxtral-4b-tts-2603.md) separately reports source-labeled latency of 70 ms at concurrency 1 on H200 (552 ms at 32), not documented TTFA; do not treat it as a matched first-audio ranking. All three carry non-commercial weights.[^voxtral-card]
- **Best published cloning fidelity:** [dots.tts-soar](dots-tts-soar.md) (highest SIM on Seed-TTS and MiniMax Multilingual), then [VoxCPM2](voxcpm2.md). Qwen3-TTS-1.7B-Base reports the lowest test-en WER.
- **Broad multilingual with a commercial license:** [VoxCPM2](voxcpm2.md) (30 languages, 48 kHz), [Chatterbox Multilingual V3](chatterbox-tts.md) (23 plus language packs), [Indic Parler-TTS](indic-parler-tts.md) (21 Indic + English, Apache-2.0), then Qwen3-TTS (10). OmniVoice, Higgs TTS 3, and Fish S2 Pro cover more languages but are non-commercial.
- **Vietnamese (expanded shortlist):** see [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md). Start deployment A/B with [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md), [VoxCPM2](voxcpm2.md) for cloning/style and GPU, and [Supertonic 3](supertonic-3.md) for CPU. Fish S2 Pro and OmniVoice explicitly list `vi`; Higgs TTS 3 claims a Vietnamese WER/CER under-5 tier but lacks an exact matched Vietnamese listening result. Their non-commercial weights need deployment-specific permission. LGTM lists vi but lacks license/latency; dots-mf acknowledges higher Vietnamese WER. No matched Vietnamese MOS/TTFA comparison is compiled. VieNeu batched RTF0.011–0.02 is not streaming RTF0.49–0.59. Qwen3-TTS official has no vi; community adaptations need their own evidence. These are conditional choices, not a quality leaderboard (**Synthesis**).[^vieneu-tts-repo][^voxcpm2-card][^supertonic-3-card][^fish-s2pro-card][^omnivoice-card][^higgs-v3-card][^lgtm-card][^dots-tts-mf-card][^qwen3-tts-17b-customvoice-card]
- **Japanese-only voice design and cloning:** [Irodori-TTS-v4-Large](irodori-tts-v4-large.md) (caption-only design, up to 120 s reference cloning, emoji style control, SilentCipher watermark; reading accuracy slightly trails v4.1-Small and weights carry Gemma Terms).
- **Indic languages with prompt control:** [Indic Parler-TTS](indic-parler-tts.md) (21 languages, 69 named speakers, caption-driven emotion/pitch/rate/reverb, Apache-2.0; card recommends the uncompiled Indic-Speak successor for better quality).
- **CPU-only or laptop:** [Pocket TTS](pocket-tts.md) (cloning, ~200 ms), [Sopro V2 Turbo](sopro-v2-turbo.md) (cloning, ~300 ms TTFA, browser ONNX), [Supertonic 2](supertonic-2.md) (fastest numeric CPU RTF, preset voices), [Supertonic 3](supertonic-3.md) (31 langs, preset plus Voice Builder custom voices, expression tags; no numeric RTF in card), [Soprano-1.1-80M](soprano-1-1-80m.md) (English, no cloning), Chatterbox Nano, [MOSS-TTS-Nano](moss-tts-nano.md) (license unclear), or VieNeu int8 for Vietnamese.
- **Microcontroller or sub-5M experiments:** [sanoTTS](sanotts.md) (draft, author-reported) and [Inflect-Nano-v1](inflect-nano-v1.md).
- **Five-language cloning with explicit pronunciation/speed control:** [IndexTTS-2.5](indextts-2-5.md) for zh/en/ja/es/ar with an 8-value emotion vector, `<word|reading>` control, and 22.05 kHz output; review the uncaptured bilibili license and budget roughly 6 GB NVIDIA VRAM. The 0.8B size is GPT-only; no streaming or measured speed claim is available. Obtain reference-speaker consent, and test prosody across text-segment boundaries.[^indextts25-card]
- **Native C++ NVIDIA TTS exploration:** [NeMo-Speech.cpp](nemo-speech-cpp.md) exposes MagpieTTS 357M with reported Q8_0 TTFA of 9 ms on RTX 4090 / 203 ms on an unspecified CPU. Keep this as runtime evidence, not a quality-ranked or license-cleared model recommendation.[^nemo-speech-readme]
- **Expressive control and editing:** [Higgs TTS 3](higgs-tts-3-4b.md) or Fish S2 Pro for inline tags; [Step-Audio-EditX](step-audio-editx.md) or [AuK](auk.md) to edit existing audio; [Breeze TTS 2](breeze-tts-2.md) for voice direction; Qwen3-TTS VoiceDesign or [OmniVoice](omnivoice.md) for reference-free voices; [Chatterbox](chatterbox-tts.md) for exaggeration control.
- **Podcasts and long-form:** [VibeVoice-1.5B](vibevoice-1.5b.md) (90 min, 4 speakers) or its 7B GGUF. For a single long-form voice, use [VibeVoice-Realtime-0.5B](vibevoice-realtime-0.5b.md) (~10 min), Pocket TTS, or Soprano (unbounded via text splitting).
- **Few-shot fine-tuned character voices:** [GPT-SoVITS](gpt-sovits.md), with [Genie-TTS](genie-tts.md) for CPU serving.

## Community-reported field notes

These are unverified anecdotes from community threads and an LLM-generated report, kept apart from vendor evidence (**Reported**):

- Kokoro is called the local latency king, while Qwen3-TTS is called better-sounding but slower. Kokoro has repeated mispronunciation reports, and its model page was last updated in April 2025.[^reddit-asr-tts-thread]
- Pocket TTS is called a step up from Kokoro, with cloning near Qwen3-TTS quality. One failure report and an OmniVoice-versus-Pocket dispute are recorded in [Community-Reported Local ASR/TTS Selection](community-asr-tts-selection.md).[^reddit-asr-tts-thread]
- A voice-design-to-clone workflow keeps personas consistent: design a voice with Qwen3-TTS VoiceDesign, then clone it with Pocket TTS. Keep golden reference clips and diff new output after every model update.[^reddit-asr-tts-thread]
- Commenters favor Qwen3-TTS and OmniVoice in audio.cpp on an RTX 3060. Echo TTS is reported as VRAM-expensive at 10 GB. F5-TTS and Kokoro are named for quality per VRAM, and Piper for running almost anywhere.[^reddit-asr-tts-thread]
- Stream LLM output to TTS by complete sentence, and keep TTS as its own HTTP service with an explicit sample rate.[^reddit-stt-llm-tts-thread]
- An LLM-generated report advises putting every TTS behind one `/v1/audio/speech` interface and routing by language. It also notes that the client must know the per-backend sample rate (24 kHz for Qwen3-TTS, 48 kHz for VieNeu).[^claude-pipeline-report]

## Adjacent concepts

- Speech-to-speech without a separate TTS stage: [NVIDIA NemotronLabs VoiceChat 11B](nvidia-nemotronlabs-voicechat-11b.md), [PersonaPlex 7B v1](personaplex-7b-v1.md), and [Step-Audio-R1.1](step-audio-r1-1.md); [Ultravox](ultravox.md) on the input side.
- Pipeline integration: [Cascaded Voice-Agent Blueprint](cascaded-voice-agent-blueprint.md), [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md), [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md), [Voice Agent Frameworks](voice-agent-frameworks.md) (no framework ships an official Qwen3-TTS service), and [Community-Reported STT-LLM-TTS Pipeline Wiring](community-stt-llm-tts-pipeline.md).
- Translation plus speech generation: [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) (2.3B UnitY2, T2ST/S2ST, Vietnamese speech output, non-commercial). Its header claims 35 speech-output languages while its table yields 37 codes; no cloning, streaming latency, or numeric quality result is compiled. It remains adjacent rather than a dedicated cloning-TTS catalog row.[^seamless-m4t-v2]
- The recognition side of the loop: [ASR/STT Model Survey](asr-stt-model-survey.md).

## Contradictions

- **CosyVoice2-0.5B Seed-TTS figures.** Its own card prints test-en WER 2.57 and test-zh CER 1.45.[^cosyvoice2-card] The VibeVoice-Realtime card also prints 2.57 for test-en.[^vibevoice-realtime-0-5b-card] The VoxCPM-0.5B card prints 3.09 / 1.38,[^voxcpm-05b-card] and the GLM-TTS card prints CER 1.38.[^glm-tts-readme] Neither is chosen; normalizer or checkpoint differences are possible but unconfirmed.
- **Qwen3-TTS 1.7B test-zh.** The Qwen3-TTS card prints 0.77 CER for 12Hz-1.7B-Base.[^qwen3-tts-17b-customvoice-card] The dots.tts-soar card prints 1.22 for "Qwen3-TTS 1.7B" without naming a checkpoint.[^dots-tts-soar-card] The test-en values agree (1.24 vs 1.23).
- **Fish Audio S2 Pro multilingual WER.** The dots.tts-soar card prints a MiniMax Multilingual average WER of 3.7,[^dots-tts-soar-card] while the Higgs TTS 3 card prints 5.15 under its own macro-averaging and normalization.[^higgs-v3-card] The Audio8 card re-evaluated Fish with a different normalizer than Fish's official one.[^audio8-tts-preview-card]
- **MOSS-TTS-Nano license.** The README says the model is not yet licensed for redistribution until the root `LICENSE` is published.[^moss-tts-nano-readme] The audio.cpp catalog lists Apache-2.0 for `MOSS-TTS-Nano-100M-GGUF`.[^audio-cpp-gguf-readme] The two may reflect different capture times; neither is chosen.
- **VieNeu-TTS v3 Turbo use scope.** The model card says Apache-2.0 covers all shipped artifacts and that preset voices are commercially usable.[^vieneu-v3-turbo-card] The repository roadmap labels v3 Turbo "on-device, personal use".[^vieneu-tts-repo]
- **Qwen3-TTS streaming.** The cards claim 97 ms streaming,[^qwen3-tts-06b-customvoice-card] while the LLM report says the official package is non-streaming and that streaming comes only from the serving layer.[^claude-pipeline-report] This is recorded as a qualification and is not resolved.

## Coverage and limits

- Vietnamese selection follow-up (2026-10-07): inspected the current root catalog and relevant model/runtime/pipeline concepts plus local primary captures for VieNeu, VoxCPM2, Supertonic 3, Higgs, Fish, dots-mf, LGTM, OmniVoice and Qwen3-TTS language/family sections. Added previously omitted Vietnamese multilingual candidates to this selection guide; no live web research, model execution or listening evaluation. [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) records deployment gates and remaining coverage.
- Index-diff reconciliation: retained existing Irodori, LGTM, Indic Parler, Sopro, Voxtral, Supertonic 3, and OmniVoice GGUF coverage; added the previously absent IndexTTS-2.5 row and NeMo-Speech.cpp runtime evidence. This update inspected the IndexTTS-2.5 and NeMo raw captures plus their concepts, Supertonic 3, Voxtral TTS, and SeamlessM4T v2; it did not fetch missing attachments or run synthesis (**Observed** inspection scope).
- IndexTTS-2.5's license text, auxiliaries, training/evaluation data, and measured speed are unavailable. NeMo's TTS numbers are runtime-reported MagpieTTS results without its model card, weight-license review, or `BENCHMARK.md`; Voxtral's numeric column is labeled latency, not TTFA, so do not rank these figures as matched first-audio measurements.[^indextts25-card][^nemo-speech-readme][^voxtral-card]
- Built from compiled wiki concepts and selected raw captures. The original survey recorded a raw inspection of the [MOSS-TTS-Nano README](../raw/MOSS-TTS-Nano.md) `Supported Languages` table (20-language claim, 19 tabulated codes); this reconciliation preserves that coverage record rather than repeating the inspection.[^moss-tts-nano-readme] No model was installed, synthesized, or benchmarked.
- Missing primary-source concepts: Kokoro-82M, Piper, F5-TTS, FireRedTTS-2/3, Spark-TTS, MaskGCT, ChatTTS, KittenTTS, NeuTTS Air, Orpheus, Coqui XTTSv2, Echo TTS, MOSS-TTS (full) and MOSS-TTS Local, ZONOS2, MagpieTTS, Maya1, MioTTS, Confucius4-TTS, and Indic-Speak (recommended successor to Indic Parler-TTS). They appear here only through catalogs, competitor columns, or anecdotes.[^audio-cpp-gguf-readme][^sglang-omni-readme][^reddit-asr-tts-thread] The Qwen3-TTS Base and VoiceDesign checkpoints, dots.tts-base, and CosyVoice3-1.5B also lack their own concepts. HF speech-to-speech lists Supertonic at 32 languages, which the Supertonic 2 card's five do not cover; [Supertonic 3](supertonic-3.md) lists 31 in its own card.[^speech-to-speech-readme][^supertonic-2-card][^supertonic-3-card]
- [IndexTTS2](indextts2.md) is a draft compiled from a README fragment, and [sanoTTS](sanotts.md) is a draft built from a release thread; treat both rows as provisional. The AuK, VoxCPM2, and IndexTTS2 benchmarks are image-only or deferred, so they have no numeric rows here.[^indextts2-readme][^sanotts-thread][^auk-card][^voxcpm2-card]
- Benchmarks and releases are time-sensitive; `stale_after: 2027-10-06` follows the `tts` domain rule.

## Relationships

- Uses every TTS concept linked in the [Master catalog](#master-catalog) as its evidence base. Each model page carries the full card detail (**Synthesis**).
- Complements [ASR/STT Model Survey](asr-stt-model-survey.md), which covers the recognition half of the VAD → STT → LLM → TTS loop (**Synthesis**).

[^irodori-v4-large-card]: [Irodori-TTS-v4-Large model card](../raw/Irodori-TTS-v4-Large.md) — locators: frontmatter (`license: gemma`, `language: ja`, `pipeline_tag: text-to-speech`); `Key Features` (120 s long-reference cloning, flow matching over DACVAE latents, emoji control, SilentCipher watermark); `What's New in v4-Large` (766M → 3.29B, 24-layer 2,048-dim DiT, T5Gemma 2, frozen-parameter duration predictor); `Architecture` (5-component list, Semantic-DACVAE-Japanese-32dim 48 kHz); `Long-reference Voice Cloning` (multiple-short-clips rule, unevaluated single-recording caveat); `Benchmarks` (seeds 0–4, train-exclusion sentence, Joyo Parakeet-Edition table, JSUT table, Coco-Nut 4.2991/Gemini-judge table with +0.0652 CI, JVS 8-row CAM++ table with ~30 s saturation note); `Training Data & Annotation` (Qwen3-Omni-30B-A3B-Instruct labels, Qwen3.5-35B-A3B rephrase); `Limitations` (8 bullets); `License & Ethical Restrictions` (Gemma Terms via t5gemma-2-1b-1b, 4 ethical bullets).
[^qwen3-tts-17b-customvoice-card]: [Qwen3-TTS-12Hz-1.7B-CustomVoice model card](../raw/Qwen3-TTS-12Hz-1.7B-CustomVoice.md) — locators: frontmatter (`license: apache-2.0`); `Overview/Introduction` (10-language list, 97 ms Dual-Track streaming bullet); `Released Models` table (tokenizer row plus 5 checkpoints with instruction-control column); evaluation tables (Seed-TTS WER: 12Hz-1.7B-Base 0.77 zh / 1.24 en, 12Hz-0.6B-Base 0.92 / 1.32; multilingual WER/SIM; cross-lingual; InstructTTSEval APS/DSD/RP; long-form; tokenizer reconstruction).
[^qwen3-tts-06b-customvoice-card]: [Qwen3-TTS-12Hz-0.6B-CustomVoice model card](../raw/Qwen3-TTS-12Hz-0.6B-CustomVoice.md) — locators: frontmatter (`license`, 10-code `language`); intro paragraph (0.6B CustomVoice, 9 premium timbres); `Key Features` (97 ms streaming sentence, no protocol or hardware).
[^qwen3-tts-tokenizer-card]: [Qwen3-TTS-Tokenizer-12Hz model card](../raw/Qwen3-TTS-Tokenizer-12Hz.md) — locators: title plus lead paragraph (12.5 Hz, 16-layer multi-codebook, lightweight causal ConvNet decoder, first-packet emission); frontmatter `license`.
[^faster-qwen3-tts-readme]: [Faster Qwen3-TTS README](../raw/faster-qwen3-tts.md) — locators: lead paragraph (CUDA graphs, GGML CUDA/Metal); `Experimental GGML backend`; performance tables for 0.6B and 1.7B (baseline vs CUDA-graph RTF/TTFA at `chunk_size=8` on Jetson AGX Orin, DGX Spark, RTX 4090, RTX 4060, H100, T4) plus the RTX 4090-vs-H100 clock note; precomputed speaker-embedding section (4 KB, `x_vector_only`); server and OpenAI-compatible API sections.
[^cosyvoice2-card]: [CosyVoice2-0.5B README and model card](../raw/CosyVoice2-0.5B.md) — locators: frontmatter (`license: apache-2.0`, 9-code `language`); `Roadmap` (2024/12 25 Hz release, 2025/05 vLLM, 2025/08 Triton TRT-LLM and GRPO training); usage fences (`inference_zero_shot`, `inference_instruct2` dialect example, bi-streaming text generator); `Evaluation` table CosyVoice2 row (test-zh 1.45 / 75.7, test-en 2.57 / 65.9, test-hard 6.83 / 72.4).
[^fun-cosyvoice3-card]: [Fun-CosyVoice3-0.5B-2512 README and model card](../raw/Fun-CosyVoice3-0.5B-2512.md) — locators: frontmatter (`license`, `language`); `Highlight / Key Features` (9 languages, 18+ dialects, cross-lingual cloning, Pinyin/CMU inpainting, 150 ms bi-streaming, instruct controls); `Evaluation` table (0.5B-2512 and 0.5B-2512_RL rows).
[^fish-s2pro-card]: [Fish Audio S2 Pro model card](../raw/s2-pro.md) — locators: frontmatter (`license_name: fish-audio-research-license`, 80+-entry `language`); intro (10M+ hours, RL alignment, release of weights, fine-tuning code, and SGLang engine); `Architecture` (Dual-AR 4B slow / 400M fast, 10-codebook RVQ ~21 Hz); inline-control section (free-form `[tag]`); production streaming figures (single H200: RTF 0.195, ~100 ms TTFA, 3,000+ acoustic tokens/s); license section (non-commercial, `business@fish.audio`).
[^higgs-v3-card]: [Higgs TTS 3 model card](../raw/higgs-audio-v3-tts-4b.md) — locators: frontmatter (`license` R&NC, `language`); license `TIP` callouts (research/non-commercial, Creator Use Grant); Component Spec table (8×1026 codebooks, 25 fps, 24 kHz); `Supported Languages` (102); evaluation tables (multilingual voice-clone WER/CER across SeedTTS, CV3, MiniMax-Multilingual, Higgs-Multilingual; Emergent-TTS win-rate); SGLang Omni serving and H100 throughput table; vLLM-Omni serve command.
[^dots-tts-soar-card]: [dots.tts-soar model card](../raw/dots.tts-soar.md) — locators: frontmatter (`license: apache-2.0`); intro (2B continuous AR, semantic encoder + LLM + AR flow-matching head, 48 kHz AudioVAE, SCA); three-checkpoint table; `Fine-tuning`; benchmark tables (Seed-TTS-Eval rows for Seed-TTS, Qwen3-TTS 1.7B, VoxCPM 2, dots.tts-base, dots.tts-soar; MiniMax Multilingual averages; CV3-Eval cross-lingual SIM; EmergentTTS-Eval Syntactic Complexity).
[^dots-tts-mf-card]: [dots.tts-mf model card](../raw/dots.tts-mf.md) — locators: frontmatter (`license`, `base_model: dots-studio/dots.tts-soar`); intro (CFG-aware MeanFlow, NFE 2–4, recommended low-latency checkpoint); Seed-TTS-Eval NFE table (NFE=4 avg 2.94 / 78.2 with per-split cells); CV3-Eval hard-en row.
[^voxcpm-05b-card]: [VoxCPM-0.5B model card](../raw/VoxCPM-0.5B.md) — locators: frontmatter (`license: apache-2.0`, `language: en, zh`, `base_model` MiniCPM4-0.5B); `Overview` (1.8M-hour corpus); `Key Features` (RTF 0.17 on RTX 4090); `Performance Highlights` Seed-TTS-eval table (VoxCPM 1.85 / 0.93; CosyVoice2 3.09 / 1.38; IndexTTS2 1.5B 2.23 / 1.03) and CV3-eval table.
[^voxcpm2-card]: [VoxCPM2 model card](../raw/VoxCPM2.md) — locators: frontmatter (30-code `language`, `license: apache-2.0`); intro (2B, 30 languages, 48 kHz, 2M+ hours); `Highlights` (voice design, controllable and ultimate cloning, AudioVAE V2 16→48 kHz, RTF ~0.3 / ~0.13 Nano-vLLM, Apache-2.0); performance section deferring benchmark tables to GitHub; fine-tuning guide pointer.
[^chatterbox-card]: [Chatterbox TTS](../raw/chatterbox.md) — locators: frontmatter (`license: mit`, 23-code `language`); `Model Zoo` table; `Key Details` (0.5B Llama backbone, exaggeration control, 0.5M hours, PerTh watermark, voice conversion); `Tips` (`exaggeration`/`cfg` defaults).
[^chatterbox-repo]: [Chatterbox TTS GitHub repository README](../raw/chatterbox-repo.md) — locators: `Latest Release: Chatterbox Multilingual V3` (Turbo 350M one-step decoder, Nano 110M 3x real time on 8 CPU cores, paralinguistic tags); `Model Zoo` 5-row table; `Watermark extraction` fence; `Evaluation` (Podonos comparisons); `example_vc.py` pointer.
[^vibevoice-1-5b-card]: [VibeVoice-1.5B model card](../raw/VibeVoice-1.5B.md) — locators: frontmatter (`language: en, zh`, `license: mit`); intro (7.5 Hz acoustic and semantic tokenizers, diffusion head, 90 min / 4 speakers); `Training Details` (Qwen2.5-1.5B, tokenizer downsampling from 24 kHz); responsible-use mitigations (audible disclaimer, imperceptible watermark); limitations (English and Chinese only).
[^vibevoice-realtime-0-5b-card]: [VibeVoice-Realtime-0.5B model card](../raw/VibeVoice-Realtime-0.5B.md) — locators: frontmatter (`language: en`, `license: mit`, `base_model: Qwen/Qwen2.5-0.5B`); intro (~300 ms first audio, interleaved windowed streaming, acoustic-only 7.5 Hz tokenizer, nine exploratory languages); benchmark tables (SEED test-en 2.05 / 0.633; CosyVoice2 2.57 / 0.652).
[^vibevoice-7b-gguf-card]: [VibeVoice 7B GGUF for audio.cpp](../raw/VibeVoice-7B-GGUF.md) — locators: section `Files` (`vibevoice-7b-q8_0.gguf`); performance sanity-check paragraph (RTX 5090 server mode, RTF ~0.18, ~52 s output, ~13.3 GB peak VRAM).
[^auk-card]: [AuK model card](../raw/AuK.md) — locators: frontmatter (`license: mit`); `Introduction` (1.5B, base and Flash variants); `Supported Tasks` 16-row table; `Download the weights` (diffusion transformer plus layer-fusion checkpoint, Qwen2.5-Omni-3B encoder, separate VAE); `Performance` (image only); `Inference with SGLang-Omni`.
[^auk-flash-card]: [AuK-Flash model card](../raw/AuK-Flash.md) — locators: frontmatter (`language: zh, en`, `license: mit`, `base_model: tencent/AuK`); title block and intro (fast 4-step distilled inference); `Supported Tasks` table.
[^auk-gguf-card]: [AuK GGUF for audio.cpp](../raw/AuK-Base-and-Flash-GGUF.md) — locators: component list (generator, Qwen2.5-Omni-3B conditioner, F32 VAE); usage fences (`--family auk`, `auk.variant`); 16-task validation section (forced FP32, TF32 disabled, 24 kHz WAVs, waveform cosine ≥0.999989991); quantized-component caveat.
[^step-audio-editx-readme]: [Step-Audio-EditX README](../raw/Step-Audio-EditX.md) — locators: `Introduction` (3B LLM-based editing model, zero-shot TTS); `Features` (language and dialect tags, emotion, style, and paralinguistic editing); `Available Tags` table (14 emotion, 32 style, 22 paralinguistic); requirements table (3B, 12 GB optimal / 16 GB recommended, L40S); `Open-source Plan` (GRPO training code); license note (code Apache 2.0).
[^omnivoice-card]: [OmniVoice model card](../raw/OmniVoice.md) — locators: frontmatter (`base_model: Qwen/Qwen3-0.6B`, 600+-code `language`); `Key Features` (cloning, attribute voice design, `[laughter]` and pinyin/phoneme control, RTF 0.025, diffusion LM architecture); `Usage` (24 kHz output); license (Apache-2.0 code, CC-BY-NC weights).
[^omnivoice-gguf-card]: [OmniVoice GGUF model card](../raw/OmniVoice-GGUF.md) — locators: intro (omnivoice.cpp C++17/GGML port, 646 languages, 24 kHz mono, CPU/CUDA/ROCm/Metal/Vulkan); `## Files` variant table (paired base plus tokenizer files, F32/BF16/Q8_0-recommended/Q4_K_M sizes); `## Quick start` fence; `## Backends` table; `## Quantization policy` (F32 RVQ/Snake-alpha, F16 non-alignable conv rows, hidden-1024 K-quant note); `## License` (CC-BY-NC conversion terms, Higgs Audio v2 codec, MIT tooling).
[^breeze-tts-2-card]: [Breeze TTS 2 model card](../raw/Breeze-TTS-2.md) — locators: frontmatter (`language: en, zh`, `license: other`); `Introduction` (#1 open-weight Artificial Analysis ranking); `Highlights` (clone, design, direction, vocal events, TTFA <40 ms, RTF 0.32, 7.7 GiB); `Streaming API` (mono 24 kHz PCM); `Fast Inference Options` stage table (text encoder, backbone, depth decoder, codec); `License and Responsible Use` (Apache-2.0 code, Qwen3-TTS tokenizer attribution, non-commercial weights).
[^audio8-tts-preview-card]: [Audio8 TTS Preview 0.6B model card](../raw/Audio8-TTS-Preview-0.6b.md) — locators: frontmatter (`license: apache-2.0`, 11-code `language`); `Model Details` (601,159,424 parameters, slow/fast AR layers, 10 codebooks, 44.1 kHz codec); `Evaluation` (Seed-TTS table incl. Fish S2 Pro re-evaluation and VoxCPM2 rows; CV3 multilingual table; methodology notes on normalizers); deployment section (ONNX INT4 CPU, SGLang Omni).
[^lgtm-card]: [LGTM-TTS model card](../raw/LGTM.md) — locators: frontmatter (`language` 11 codes, `pipeline_tag: text-to-speech`); intro (Looks Good To Me expansion, Claude Opus 5.5 provenance claim, 44.1 kHz, 10 voices, cross-lingual cloning, PyTorch/ONNX); `Languages` and `Built-in voices` (11 codes; F1–F5 female, M1–M5 male); `Samples` (22 hosted WAVs); `Setup`/usage fences (PyTorch `LGTMTTS`, ONNX `LGTMOnnx` with `use_gpu`, `clone_voice` 5–15 s, `save_voice_style`, CLI); `Options` table (steps 8, speed 1.05, silence 0.3); `Files` table (safetensors, four synthesis graphs, voice encoder, voice styles, configs, `lgtm/` modules); `ONNX graph I/O` table with tensor shapes plus sampling-loop paragraph; no license, size, or benchmarks stated.
[^glm-tts-readme]: [GLM-TTS README and model card](../raw/GLM-TTS.md) — locators: frontmatter (`license: mit`, `language: zh, en`); `Key Features` (3–10 s cloning, GRPO multi-reward, phoneme-plus-text control, streaming); `System Architecture` (Llama text-to-token stage, flow-matching stage); seed-tts-eval table (GLM-TTS_RL 0.89 / 76.4, base 1.03 / 76.1, CosyVoice2 1.38 / 75.7).
[^gpt-sovits-readme]: [GPT-SoVITS-WebUI README](../raw/GPT-SoVITS.md) — locators: header (MIT badge); `Features` (5 s zero-shot, 1 min few-shot, en/ja/ko/yue/zh); RTF paragraph (v2 ProPlus 0.028 RTX 4060 Ti, 0.014 RTX 4090, 0.526 M4 CPU); version notes (v3 BigVGAN 24 kHz, v4 native 48 kHz, v2Pro).
[^genie-readme]: [GENIE GPT-SoVITS Lightweight Inference Engine README](../raw/Genie-TTS.md) — locators: header (V2/V2ProPlus, ja/en/zh/kr); `Performance Advantages` table (1.13 s first inference, ~200 MB runtime) and i7-13620H test note; FastAPI server section.
[^indextts25-card]: [IndexTTS-2.5 model card](../raw/IndexTTS-2.5.md) — locators: frontmatter `language`/`license_name`; intro (IndexTTS2 comparison); `Model Details` (0.8B GPT, flow matching, BigVGAN, 22.05 kHz); `Getting Started` (Python/NVIDIA/~6 GB); `Inference` (`emo_vector`, `<word|reading>`, `duration_factor`); `Limitations` (QwenEmotion, segment prosody, random-emotion fidelity, consent). No benchmark/streaming figures or LICENSE text supplied.
[^nemo-speech-readme]: [NeMo-Speech.cpp README](../raw/NeMo-Speech.cpp.md) — locators: `Models and applications` (MagpieTTS 357M, NanoCodec 22 kHz); `Performance` (Q8_0, 186 ms chunks, RTX 4090/CPU TTFA/inter-chunk/throughput table, unavailable `BENCHMARK.md`); `Local server and playground`; `Native SDK`; `License` (runtime code only).
[^seamless-m4t-v2]: [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) — locators: `Tasks and language coverage`; `Architecture`; `Trust, license, and limits`; `Contradictions`; `Coverage and limits`. Compiled card synthesis, not independent verification.
[^indextts2-readme]: [IndexTTS-2 README fragment](../raw/IndexTTS-2.md) — locators: frontmatter (`language: [en, zh]`); subtitle (emotionally expressive, duration-controlled autoregressive zero-shot TTS); link block; no license, size, or evaluation present.
[^vieneu-tts-repo]: [VieNeu-TTS GitHub repository README](../raw/VieNeu-TTS-repo.md) — locators: v3 Turbo `NOTE` callout (48 kHz, 25 voices, cloning, emotion cues, streaming, LoRA); v3 Nano preview bullets (48M, 24 kHz, CPU-only); OpenAI-compatible server section (`VIENEU_MAX_STREAMS` 16); benchmark section (RTX 3060 and i5 throughput and streaming tables, Nano 282 MB); `§7 Roadmap` "(on-device, personal use)" label.
[^vieneu-v3-turbo-card]: [VieNeu-TTS v3 Turbo Hugging Face model card (SDK v3.7.1)](../raw/VieNeu-TTS-v3-Turbo.md) — locators: frontmatter (`license: apache-2.0`, `language: vi, en`); `Overview` (48 kHz, preset voices, English–Vietnamese code-switching); licensing FAQ (Apache-2.0 covers shipped artifacts; preset voices commercially usable).
[^pocket-tts-doc]: [Pocket TTS README and Hugging Face model card](../raw/pocket-tts-without-voice-cloning.md) — locators: frontmatter (`license: cc-by-4.0`, gated fields); `Main takeaways` (100M, ~200 ms first chunk, ~6x on MacBook Air M4 with 2 cores, streaming, cloning); CLI `--language` 24-layer variants; local server; license and prohibited-use section.
[^pocket-tts-repo]: [Pocket TTS GitHub repository README](../raw/pocket-tts-repo.md) — locators: `Main takeaways` (7 languages incl. Dutch); `In-browser implementations` (WASM ports).
[^soprano-card]: [Soprano README and Hugging Face model card](../raw/Soprano-1.1-80M.md) — locators: frontmatter (`license: apache-2.0`); `Overview` (80M, 2000x GPU / 20x CPU, <15 ms GPU / <250 ms CPU streaming, <1 GB, 32 kHz, automatic text splitting, CUDA/CPU/MPS, WebUI/CLI/OpenAI-compatible endpoint); limitations (no voice cloning).
[^soprano-80m-card]: [Soprano-80M README and Hugging Face model card with outdated notice](../raw/Soprano-80M.md) — locators: header outdated-notice banner directing users to Soprano-1.1-80M; `News` 2026.01.14 line.
[^supertonic-readme]: [Supertonic GitHub repository README](../raw/supertonic.md) — locators: frontmatter (`license: openrail`, `language: en`); `Why Supertonic` (66M, 167x on M4 Pro); runtime matrix (examples in py, nodejs, web, java, cpp, csharp, go, swift, ios, rust, flutter); `Performance` 2-step and 5-step characters-per-second and RTF tables; `License` (MIT code, OpenRAIL-M model).
[^supertonic-2-card]: [Supertonic 2 Hugging Face model card](../raw/supertonic-2.md) — locators: frontmatter (`language: en, ko, es, pt, fr`, `license: openrail`); `Multilingual Support` table; `Performance` 2-step tables.
[^supertonic-3-card]: [Supertonic 3 Hugging Face model card](../raw/supertonic-3.md) — locators: frontmatter (`license: openrail`, 31-code `language`, `pipeline_tag`, `library_name: supertonic`); `What's New in Supertonic 3` (5-to-31 languages, stability, similarity, expression tags); `Quick Start` (`pip install supertonic`, `TTS(auto_download=True)`, `M1` voice style, `lang="en"`); `Custom Voices and Audio Samples` (preset styles, demo page, Voice Builder); `Performance Highlights` (image-only WER/CER vs VoxCPM2, v2-to-v3 deltas, CPU-vs-A100 claim, ~99M vs 0.7B–2B); 31-code `Supported Languages` table; `License` (MIT code, OpenRAIL-M model).
[^moss-tts-nano-readme]: [MOSS-TTS-Nano README](../raw/MOSS-TTS-Nano.md) — locators: intro (0.1B, realtime, CPU); `Supported Languages` (line 120 claims 20 languages; the table lists 19 codes, verified by raw read); `ONNX CPU Inference`, `Android ONNX Runtime Example`, and Reader sections; `News` (finetuning code, mlx-audio); `Finetuning`; `License` (not yet licensed for redistribution before the root `LICENSE` is published).
[^inflect-nano-v1-card]: [Inflect-Nano-v1 model card](../raw/Inflect-Nano-v1.md) — locators: frontmatter (`license: apache-2.0`, `language: en`); `Highlights` (4.63M incl. vocoder, 24 kHz, single male voice); `Generate Speech` fences (`--device cpu`, length/pitch/energy scales).
[^sanotts-thread]: [sanoTTS release thread](../raw/i_released_sanotts_smallest_complete_tts_stack_in.md) — locators: post bullets (294k–2.2M, 11 voices / 6 languages, 337 KB INT8, SCOREQ 4.13 / UTMOS 4.10 for 1.51M Amy, ESP32 RTF 0.225); author replies on per-component distillation and ESP32-S3 memory. Author-reported, not independently verified.
[^audio-cpp-gguf-readme]: [audio.cpp GGUF Model Packages](../raw/audio.cpp-gguf.md) — locators: `Files` table TTS rows (directory, audio.cpp family, precisions, original-model license; incl. `MOSS-TTS-Nano-100M-GGUF` Apache-2.0, `IndexTTS2-GGUF` bilibili Model Use License, `DotTTS-Edit-GGUF`, `Supertonic-3-GGUF`); `Usage` TTS fence.
[^sglang-omni-readme]: [SGLang-Omni GitHub README](../raw/sglang-omni.md) — locators: `News` (AuK/AuK-Flash 24 kHz, MOSS-TTS Local v1.5 48 kHz, Higgs Audio v3); supported speech-generation list (Higgs Audio v3, MOSS-TTS, MOSS-TTS Local, Fish Speech S2-Pro, Qwen3-TTS, Voxtral TTS, Ming-Omni-TTS, dots.tts, ZONOS2) on `/v1/audio/speech`.
[^vllm-omni-readme]: [vLLM-Omni GitHub README](../raw/vllm-omni.md) — locators: supported-model list (TTS: Qwen3-TTS, Tencent AuK, Breeze-TTS-2, CosyVoice3); release-note entries on TTS coverage.
[^speech-to-speech-readme]: [Speech To Speech README](../raw/speech-to-speech.md) — locators: TTS backend list (Qwen3-TTS default, Kokoro-82M, Pocket TTS, ChatTTS, OmniVoice, MMS, OpenAI-compatible); default `serve` flags (`--qwen3_tts_non_streaming_mode True`); `TTS notes: OmniVoice, Pocket, and logging` (no incremental OmniVoice audio); language-coverage paragraph (Supertonic 32 languages); Apple Silicon configuration (6-bit Qwen3-TTS via MLX Audio).
[^speaches-readme]: [Speaches README](../raw/speaches.md) — locators: overview (Piper and Kokoro `hexgrad/Kokoro-82M` TTS behind an OpenAI-compatible API).
[^realtimevoicechat-readme]: [Real-Time AI Voice Chat README](../raw/RealtimeVoiceChat.md) — locators: TTS engine configuration (`START_ENGINE` `coqui` / `kokoro` / `orpheus` in `server.py`); `RealtimeTTS` pipeline step.
[^reddit-asr-tts-thread]: [Good ASR and TTS models? thread capture](../raw/good_asr_and_tts_models.md) — locators: `Comments 51` (Kokoro latency and mispronunciation remarks; Pocket TTS versus Kokoro, Qwen3-TTS, and OmniVoice; Qwen3 VoiceDesign-to-Pocket clone workflow; golden-clip regression; audio.cpp RTX 3060 favorites; Echo 10 GB VRAM; F5-TTS, Kokoro, and Piper remarks).
[^reddit-stt-llm-tts-thread]: [STT -> LLM -> TTS pipeline thread capture](../raw/stt_llm_tts_pipeline.md) — locators: replies on three separate HTTP services, sentence-chunked LLM-to-TTS streaming, and explicit sample rates.
[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `Key Findings` 1–2 (Qwen3-TTS 10 languages without Vietnamese, unbenchmarked community fine-tunes, serving-layer streaming, vLLM-Omni 64 ms TTFP); `PHẦN 2` `Qwen3-TTS: chọn model và cách dùng` (Base-only cloning, non-streaming `qwen-tts` API); transport paragraph (24 kHz Qwen3-TTS vs 48 kHz VieNeu); TTS-router recommendation. LLM-generated report; figures are its citations, not verified here.
[^indic-parler-card]: [Indic Parler-TTS model card](../raw/indic-parler-tts.md) — locators: frontmatter (`license: apache-2.0`, 17-code `language`, `pipeline_tag: text-to-speech`, `datasets: ai4b-hf/GLOBE-annotated`); header (Parler-TTS Mini v1.1 lineage, 1,806 h fine-tune, Indic-Speak successor note, 21-language list, byte-fallback tokenizer, HF audio × AI4Bharat); `Key capabilities` (unofficial Chhattisgarhi/Kashmiri/Punjabi, 69 voices, 10-language emotion list with 12 emotions, Indian-English accents, six caption axes); usage fences (dual tokenizers, `ParlerTTSForConditionalGeneration`, Hindi prompt, `Divya's voice` pattern); 18-row speaker table; `Tips`; 10 description examples; `Evaluation` NSS table (19 rows, Kashmiri 55.30 prose mention); `Motivation`; `Training dataset` (4-row corpus table, 18-row language hours table); `Citation`; `License`.
[^sopro-v2-card]: [Sopro TTS README and Hugging Face model card (sopro-v2-turbo)](../raw/sopro-v2-turbo.md) — locators: frontmatter (`license: apache-2.0`, `language: en, pt, fr, de`, `pipeline_tag: text-to-speech`, `library_name: sopro`); `Main features` (120M, 4 languages, ~300 ms TTFA, 5–20 s cloning, 0.24/0.21 M3 and 0.07 H100 RTF, browser ONNX); `Local demo` and `Browser demo` sections (serve fences, `localhost:7860`, HF cache, mobile-quantization caveat, `web/README.md`, `demos/web`); `Examples / CLI` and `Examples / Python` sections (`--lang/--int8/--steps/--max-seconds`, `synthesize`/`stream`/`prepare_reference` fences); `Disclaimers` section (no watermark, minimal frontend, mixed-language, non-bit-exact streaming); `Training data` and `Acknowledgements` sections.
[^voxtral-card]: [Voxtral 4B TTS 2603 model card](../raw/Voxtral-4B-TTS-2603.md) — locators: frontmatter (`license: cc-by-nc-4.0`, 9-code `language`, `pipeline_tag: text-to-speech`, `base_model: mistralai/Ministral-3-3B-Base-2512`); `Key Features` (9-language list, 20 preset voices plus adaptation, 24 kHz plus 6-format list, streaming/batch); `Benchmark Results` (vllm-omni `end2end.py`, 500-char plus 10 s reference, H200, 3-row table with inverted-RTF note); `Usage` (vllm-omni install/serve fences, `/v1/audio/speech` client fence, Gradio demo fence, HF Space); `License` (EARS/CML-TTS/IndicVoices-R/Arabic Natural Audio attribution).

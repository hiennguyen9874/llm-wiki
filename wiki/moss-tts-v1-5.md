---
type: Concept
title: MOSS-TTS-v1.5
description: Flagship MOSS-TTS-v1.5 TTS checkpoint (MossTTSDelay-8B API) with 31-language zero-shot voice cloning, language-tagged synthesis, and explicit pause plus token-duration control via Hugging Face Transformers.
tags: [tts, multilingual, voice-cloning]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:47:01Z }
stale_after: 2027-10-07
sources:
  - id: moss-tts-v15-card
    resource: ../raw/MOSS-TTS-v1.5.md
    kind: documentation
    title: MOSS-TTS-v1.5 model card
---

MOSS-TTS-v1.5 is OpenMOSS/MOSI.AI's flagship continued TTS checkpoint from 1.0, served as `OpenMOSS-Team/MOSS-TTS-v1.5` through the same generation API as the 1.0 **MossTTSDelay-8B** checkpoint, preserving zero-shot voice cloning, long-form generation, token-level duration control, Pinyin/IPA pronunciation control, and multilingual plus code-switching synthesis, while adding language-tag-gated multilingual gains, more stable and consistent cloning, better long-reference short-text cloning, steadier punctuation-driven prosody, and explicit inline `[pause X.Ys]` control (**Reported**).[^moss-tts-v15-card]

## Model identity and lineage

- Title is `MOSS-TTS-v1.5`; creator is the OpenMOSS team; weights are `OpenMOSS-Team/MOSS-TTS-v1.5` on Hugging Face with a ModelScope collection; upstream code is `https://github.com/OpenMOSS/MOSS-TTS`; companion links are the project page, ModelScope models, blog, arXiv `2603.18090`, AIStudio try plus API docs, X, and Discord (**Reported**).[^moss-tts-v15-card]
- The card states v1.5 is continued from [MOSS-TTS 1.0](https://huggingface.co/OpenMOSS-Team/MOSS-TTS) and preserves its main capabilities: zero-shot voice cloning, long-form speech generation, token-level duration control, Pinyin/IPA pronunciation control, multilingual synthesis, and code-switching; the full 1.0 feature walkthrough, input schema, decoding hyperparameters, and evaluation tables are delegated to the 1.0 README, which is not in `raw/` and was not inspected here (**Reported**, with pointer limit **Synthesis**).[^moss-tts-v15-card]
- The card states v1.5 is API-compatible with 1.0: continuation with prefix audio, detailed `UserMessage` and `AssistantMessage` fields, generation hyperparameters, Pinyin/IPA preprocessing, and evaluation results are all delegated to the 1.0 README (**Reported**).[^moss-tts-v15-card]

## v1.5 improvements over v1.0

All five deltas are upstream assertions without numeric benchmarks in this card (**Reported**):[^moss-tts-v15-card]

- Stronger multilingual synthesis with language tags: with `language` omitted, v1.5 may improve some languages and regress slightly on others versus 1.0; with the language specified it is stronger than 1.0 on almost all supported languages, so the card recommends setting the tag, e.g. `processor.build_user_message(text=text_fr, language="French")` (**Reported**).[^moss-tts-v15-card]
- More stable voice cloning: improved speaker similarity with reduced cloning variance, making repeated generations more consistent (**Reported**).[^moss-tts-v15-card]
- Better long-reference, short-text cloning: handles reference audio much longer than the target text more reliably than 1.0 (**Reported**).[^moss-tts-v15-card]
- More stable punctuation-following prosody: follows punctuation-driven pauses more closely, especially in long sentences (**Reported**).[^moss-tts-v15-card]
- Explicit pause control with inline markers such as `[pause 3.2s]`; the example `我今天学习了一首中国的古诗，它的名字是[pause 3.2s]静夜思！` inserts a 3.2 s pause before `静夜思` (**Reported**).[^moss-tts-v15-card]

## Supported languages

31 languages by code: Chinese (zh), Cantonese (yue), English (en), Arabic (ar), Czech (cs), Danish (da), Dutch (nl), Finnish (fi), French (fr), German (de), Greek (el), Hebrew (he), Hindi (hi), Hungarian (hu), Italian (it), Japanese (ja), Korean (ko), Macedonian (mk), Malay (ms), Persian/Farsi (fa), Polish (pl), Portuguese (pt), Romanian (ro), Russian (ru), Spanish (es), Swahili (sw), Swedish (sv), Tagalog (tl), Thai (th), Turkish (tr), and Vietnamese (vi); the card states v1.5 keeps the 20 v1.0 languages and adds Cantonese, Dutch, Finnish, Hindi, Macedonian, Malay, Romanian, Swahili, Tagalog, Thai, and Vietnamese through continued multilingual training (**Reported**).[^moss-tts-v15-card]

## Hugging Face inference

- Environment: a clean isolated Python environment with Transformers 5.0.0; example uses `conda create -n moss-tts python=3.12`; install with `git clone https://github.com/OpenMOSS/MOSS-TTS.git` then `pip install --extra-index-url https://download.pytorch.org/whl/cu128 -e .`; `pyproject.toml` pins `torch==2.9.1+cu128` and `torchaudio==2.9.1+cu128` (**Reported**).[^moss-tts-v15-card]
- Optional FlashAttention 2 for speed and lower GPU memory where hardware supports it: `pip install --extra-index-url https://download.pytorch.org/whl/cu128 -e ".[flash-attn]"`, with `MAX_JOBS=4` to cap build parallelism on RAM-constrained many-core machines; skipped when the build fails, falling back to the default attention backend; available only on supported GPUs and typically used with `torch.float16` or `torch.bfloat16` (**Reported**).[^moss-tts-v15-card]
- Interface is the standard Hugging Face `AutoProcessor` plus `AutoModel` with `trust_remote_code=True`, using the same generation API as the 1.0 **MossTTSDelay-8B** checkpoint; the example disables the broken cuDNN SDPA backend and keeps flash, memory-efficient, and math SDPA enabled; `processor.audio_tokenizer` is moved to the inference device; attention implementation resolves to `flash_attention_2` when package plus device conditions hold (CUDA, `flash_attn` present, fp16/bf16, capability major >= 8), else `sdpa` on CUDA and `eager` on CPU (**Reported**).[^moss-tts-v15-card]
- Covered `build_user_message` patterns: direct TTS with language tags for non-Chinese/English text (French example), Pinyin or IPA input (including mixed script-plus-Pinyin `您好，请问您来自哪 zuo4 cheng2 shi4？`), explicit pause (`[pause 3.2s]`), voice cloning with a reference audio list (Chinese WAV and English M4A remote demo URLs), and duration control with `tokens=325` versus `tokens=600` on the same English text (**Reported**).[^moss-tts-v15-card]
- Generation call in the example: `model.generate(input_ids, attention_mask, max_new_tokens=4096)` over `processor(batch_conversations, mode="generation")` batches with `batch_size = 1`, decoding via `processor.decode(outputs)` and saving `message.audio_codes_list[0]` with `torchaudio.save(out_path, audio.unsqueeze(0), processor.model_config.sampling_rate)` (**Reported**).[^moss-tts-v15-card]

## License

- Capture frontmatter declares `license: apache-2.0` with `tags: text-to-speech` and a 31-code `language` list (**Observed** by static inspection of the capture frontmatter).[^moss-tts-v15-card]

## Relationships

- Sibling checkpoint line: [MOSS-TTS-Local-Transformer-v1.5](moss-tts-local-transformer-v1-5.md) covers the local-Transformer v1.5 line with native 48 kHz stereo output, a fixed 12-codebook RVQ codec, a generation-parameters table, and Hugging Face plus SGLang-Omni serving paths, while this concept covers the flagship `MOSS-TTS-v1.5` checkpoint with the MossTTSDelay-8B API; do not conflate their install extras, `generate` signatures, or stereo handling (**Synthesis**).[^moss-tts-v15-card]
- Same-family compact model: [MOSS-TTS-Nano](moss-tts-nano.md) covers the 0.1B-parameter multilingual zero-shot cloning TTS with ONNX CPU paths, while this concept covers the flagship v1.5 line; no shared checkpoint is asserted (**Synthesis**).[^moss-tts-v15-card]
- Compared by [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) as a Vietnamese-capable cloning/control research candidate; the selection does not transfer Local-Transformer streaming or stereo handling to this flagship checkpoint (**Synthesis**).[^moss-tts-v15-card]
- Survey membership: [TTS Model Survey](tts-model-survey.md) compares this checkpoint against the compiled TTS catalog on languages, cloning and control, serving, and licensing (**Synthesis**).[^moss-tts-v15-card]

## Coverage and limits

- Source inspected statically only; no environment created, no package installed, no weights or tokenizer downloaded, no audio synthesized, and no cloning-stability, multilingual-gain, prosody, pause-accuracy, or latency claim reproduced — all capability and usage claims are upstream assertions (**Synthesis**).[^moss-tts-v15-card]
- The 1.0 README (feature walkthrough, input schema, decoding hyperparameters, prefix-audio continuation, `UserMessage`/`AssistantMessage` fields, Pinyin/IPA preprocessing, evaluation tables), the `OpenMOSS/MOSS-TTS` repository and `pyproject.toml` contents, the arXiv report `2603.18090`, remote demo audio, and ModelScope/Blog/Studio/API/X/Discord targets plus badge images were linked but not fetched and are not in `raw/`; decorative images excluded, remote and linked artifacts uninspected as unavailable (**Synthesis**).[^moss-tts-v15-card]
- No numeric quality, similarity, or latency benchmark appears in this card; the v1.0-vs-v1.5 comparisons are qualitative direction statements, including the language-omitted improve-some/regress-some caveat; the card's sampling rate is only referenced as `processor.model_config.sampling_rate` with no numeric value stated, so no output sample rate is recorded here (**Synthesis**).[^moss-tts-v15-card]
- Release, compatibility, and usage claims carry `stale_after: 2027-10-07` per the `tts` domain rule (**Synthesis**).[^moss-tts-v15-card]

[^moss-tts-v15-card]: [MOSS-TTS-v1.5 model card](../raw/MOSS-TTS-v1.5.md) — locators: capture frontmatter (`license: apache-2.0`, `tags: text-to-speech`, 31-code `language`); title plus intro (continued from 1.0 with 6 preserved capabilities and 1.0 README pointer); 5-bullet v1.5 improvements (language-tag strength with omit-vs-specified caveat and `language="French"` fence; cloning stability and variance; long-reference short-text; punctuation prosody; `[pause 3.2s]` with 静夜思 example); `Supported Languages` 31-cell table (20 kept plus Cantonese, Dutch, Finnish, Hindi, Macedonian, Malay, Romanian, Swahili, Tagalog, Thai, Vietnamese); `Quick Start / Environment Setup` (Transformers 5.0.0 fence, conda python=3.12, `MOSS-TTS` clone plus `-e .` cu128 fence, `pyproject.toml` torch/torchaudio 2.9.1+cu128 pins, FlashAttention 2 `-e ".[flash-attn]"` plus `MAX_JOBS=4` with hardware/dtype caveats); `Basic Usage` (MossTTSDelay-8B API tip with `language`-when-known rule; `AutoProcessor`/`AutoModel` with `trust_remote_code=True`; cuDNN-SDPA disable plus fallback enables; `resolve_attn_implementation` logic; `audio_tokenizer.to(device)`; 11-pattern `conversations` fence with Pinyin/IPA/mixed-script/`[pause 3.2s]`/reference/`tokens=325` vs `tokens=600` examples and remote demo URLs; `generate` fence with `max_new_tokens=4096`, `batch_size = 1`, `processor.decode` plus `audio_codes_list[0]` and `model_config.sampling_rate` save line); `More Usage` 1.0 API-compatibility pointer.

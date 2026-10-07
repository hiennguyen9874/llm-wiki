---
type: Concept
title: MOSS-TTS-Local-Transformer-v1.5
description: 31-language zero-shot voice-cloning TTS checkpoint with native 48 kHz stereo output, language-tagged synthesis, explicit pause and duration control, and Hugging Face plus SGLang-Omni serving paths.
tags: [tts, multilingual, voice-cloning, streaming]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:47:01Z }
stale_after: 2027-10-07
sources:
  - id: moss-tts-local-v15-card
    resource: ../raw/MOSS-TTS-Local-Transformer-v1.5.md
    kind: documentation
    title: MOSS-TTS-Local-Transformer-v1.5 model card
---

MOSS-TTS-Local-Transformer-v1.5 is OpenMOSS/MOSI.AI's continued local-Transformer TTS checkpoint from v1.0, preserving zero-shot voice cloning, long-form generation, token-level duration control, Pinyin/IPA pronunciation control, and multilingual plus code-switching synthesis, while moving to the MOSS-Audio-Tokenizer-v2 48 kHz stereo codec with a fixed 12-codebook RVQ depth, making language tags the recommended path to stronger multilingual output, and adding explicit `[pause X.Ys]` control alongside Hugging Face Transformers and SGLang-Omni serving paths (**Reported**).[^moss-tts-local-v15-card]

## Model identity and lineage

- Title is `MOSS-TTS-Local-Transformer-v1.5`; creator is the OpenMOSS team (OpenMOSS/MOSI.AI badges); weights are `OpenMOSS-Team/MOSS-TTS-Local-Transformer-v1.5` on Hugging Face with a ModelScope collection; upstream code is `https://github.com/OpenMOSS/MOSS-TTS`; companion links are the project page, Hugging Face model, ModelScope models, blog, arXiv `2603.18090`, AIStudio try plus API docs, X, and Discord (**Reported**).[^moss-tts-local-v15-card]
- The card states v1.5 is continued from [MOSS-TTS-Local-Transformer-v1.0](https://huggingface.co/OpenMOSS-Team/MOSS-TTS-Local-Transformer) and preserves its main capabilities: zero-shot voice cloning, long-form speech generation, token-level duration control, Pinyin/IPA pronunciation control, multilingual synthesis, and code-switching; the full 1.0 feature walkthrough, input schema, and evaluation tables are delegated to the v1.0 README, which is not in `raw/` and was not inspected here (**Reported**, with pointer limit **Synthesis**).[^moss-tts-local-v15-card]
- The card is API-compatible with v1.0 for continuation with prefix audio, detailed `UserMessage` and `AssistantMessage` fields, generation hyperparameters, Pinyin/IPA preprocessing, and evaluation results, again delegated to the v1.0 README (**Reported**).[^moss-tts-local-v15-card]

## v1.5 improvements over v1.0

All six deltas are upstream assertions without numeric benchmarks in this card (**Reported**):[^moss-tts-local-v15-card]

- Higher-fidelity stereo audio modeling through [MOSS-Audio-Tokenizer-v2](https://huggingface.co/OpenMOSS-Team/MOSS-Audio-Tokenizer-v2), with native 48 kHz stereo input and output; because codec output is stereo, the `[channels, samples]` tensor from `processor.decode(...)` is saved directly (**Reported**).[^moss-tts-local-v15-card]
- Stronger multilingual synthesis with language tags: with `language` omitted, v1.5 may improve some languages and regress slightly on others versus 1.0; with the language specified it is stronger than 1.0 on almost all supported languages, so the card recommends setting the tag, e.g. `processor.build_user_message(text=text_fr, language="French")` (**Reported**).[^moss-tts-local-v15-card]
- More stable voice cloning: improved speaker similarity with reduced cloning variance across repeated generations (**Reported**).[^moss-tts-local-v15-card]
- Better long-reference, short-text cloning: handles reference audio much longer than the target text more reliably than 1.0 (**Reported**).[^moss-tts-local-v15-card]
- More stable punctuation-following prosody: follows punctuation-driven pauses more closely, especially in long sentences (**Reported**).[^moss-tts-local-v15-card]
- Explicit pause control with inline markers such as `[pause 3.2s]`; the example `我今天学习了一首中国的古诗，它的名字是[pause 3.2s]静夜思！` inserts a 3.2 s pause before `静夜思` (**Reported**).[^moss-tts-local-v15-card]

## Supported languages

31 languages by code: Chinese (zh), Cantonese (yue), English (en), Arabic (ar), Czech (cs), Danish (da), Dutch (nl), Finnish (fi), French (fr), German (de), Greek (el), Hebrew (he), Hindi (hi), Hungarian (hu), Italian (it), Japanese (ja), Korean (ko), Macedonian (mk), Malay (ms), Persian/Farsi (fa), Polish (pl), Portuguese (pt), Romanian (ro), Russian (ru), Spanish (es), Swahili (sw), Swedish (sv), Tagalog (tl), Thai (th), Turkish (tr), and Vietnamese (vi); the card states v1.5 keeps the 20 v1.0 languages and adds Cantonese, Dutch, Finnish, Hindi, Macedonian, Malay, Romanian, Swahili, Tagalog, Thai, and Vietnamese through continued multilingual training (**Reported**).[^moss-tts-local-v15-card]

## Hugging Face inference

- Environment: a clean isolated Python environment with Transformers 5.0.0 or a recent Transformers version with Qwen3 support; example uses `conda create -n moss-tts python=3.12`; install with `git clone https://github.com/OpenMOSS/MOSS-TTS.git` then `pip install --extra-index-url https://download.pytorch.org/whl/cu128 -e ".[torch-runtime]"`; `pyproject.toml` pins `torch==2.9.1+cu128` and `torchaudio==2.9.1+cu128` (**Reported**).[^moss-tts-local-v15-card]
- Optional FlashAttention 2 for speed and lower GPU memory where hardware supports it: `pip install --extra-index-url https://download.pytorch.org/whl/cu128 -e ".[flash-attn]" --no-build-isolation`, with `MAX_JOBS=4` to cap build parallelism on RAM-constrained many-core machines; skipped when the build fails, falling back to the default attention backend; available only on supported GPUs and typically used with `torch.float16` or `torch.bfloat16` (**Reported**).[^moss-tts-local-v15-card]
- Interface is the standard Hugging Face `AutoProcessor` plus `AutoModel` with `trust_remote_code=True`; the example disables the broken cuDNN SDPA backend on some CUDA/PyTorch combinations and keeps flash, memory-efficient, and math SDPA enabled; `processor.audio_tokenizer` is moved to the inference device; attention implementation resolves to `flash_attention_2` when package plus device conditions hold (CUDA, `flash_attn` present, fp16/bf16, capability major >= 8), else `sdpa` on CUDA and `eager` on CPU (**Reported**).[^moss-tts-local-v15-card]
- Fixed 12-codebook RVQ depth: do not set `n_vq_for_inference` to anything other than `config.n_vq` (**Reported**).[^moss-tts-local-v15-card]
- Covered `build_user_message` patterns: direct TTS with language tags (Chinese, English, French examples), explicit pause (`[pause 3.2s]` Chinese example), voice cloning with a reference audio list (Chinese WAV and English M4A remote demo URLs), and duration control with `tokens=125` (at 12.5 frames per second, about 10 seconds) (**Reported**).[^moss-tts-local-v15-card]
- Generation call in the example: `model.generate(input_ids, attention_mask, max_new_tokens=4096, do_sample=True, audio_temperature=1.7, audio_top_p=0.8, audio_top_k=25, audio_repetition_penalty=1.0)` with `processor(batch_conversations, mode="generation")` batching and `processor.decode(outputs)` yielding `message.audio_codes_list[0]` (**Reported**).[^moss-tts-local-v15-card]
- Model configuration sets `sampling_rate` to 48000 and `n_vq` to 12; audio encoding and decoding use `OpenMOSS-Team/MOSS-Audio-Tokenizer-v2`; decoded stereo audio shaped `[channels, samples]` is passed directly to `torchaudio.save(path, audio, sampling_rate)` (**Reported**).[^moss-tts-local-v15-card]

## Generation parameters

Recommended values from the card's table; `n_vq_for_inference` is fixed by the release and other values are rejected (**Reported**):[^moss-tts-local-v15-card]

| Parameter | Recommended | Description |
| --- | ---: | --- |
| `audio_temperature` | `1.7` | Sampling temperature for audio RVQ layers. |
| `audio_top_p` | `0.8` | Nucleus sampling cutoff for audio RVQ layers. |
| `audio_top_k` | `25` | Top-k sampling cutoff for audio RVQ layers. |
| `audio_repetition_penalty` | `1.0` | Penalty for repeated acoustic token patterns. |
| `n_vq_for_inference` | `12` | Fixed by this release. Values other than `config.n_vq` are rejected. |

## SGLang-Omni serving

- [SGLang-Omni](sglang-omni.md) (via `sglang-omni`) exposes this checkpoint behind an OpenAI-compatible `/v1/audio/speech` API for reference-less synthesis, zero-shot voice cloning, streaming, duration control, and language/style hints; install, API, deployment, benchmarking, and limitations are delegated to the [MOSS-TTS-Local cookbook](https://github.com/sgl-project/sglang-omni/blob/main/docs/cookbook/moss_tts_local.md), which is not in `raw/` and was not inspected (**Reported**, with pointer limit **Synthesis**).[^moss-tts-local-v15-card]
- Serve path: `hf download OpenMOSS-Team/MOSS-TTS-Local-Transformer-v1.5` then `sgl-omni serve --model-path OpenMOSS-Team/MOSS-TTS-Local-Transformer-v1.5 --port 8000`, with a matching config at `examples/configs/moss_tts_local.yaml` in SGLang-Omni (**Reported**).[^moss-tts-local-v15-card]
- Basic speech: `POST /v1/audio/speech` with `{"input": "..."}` returns WAV (**Reported**).[^moss-tts-local-v15-card]
- Voice cloning: `references[].audio_path` (local path, HTTP(S) URL, or base64 data URI) plus transcript for better similarity; `ref_audio` and `ref_text` are shorthand for `references[0].audio_path` and `references[0].text` (**Reported**).[^moss-tts-local-v15-card]
- Streaming: `"stream": true` with `"response_format": "pcm"` and `"stream_format": "audio"` returns raw 48 kHz PCM chunks, piped in the example through `ffmpeg -f s16le -ar 48000 -ac 1 -i pipe:0 output_stream.wav` (**Reported**).[^moss-tts-local-v15-card]
- Duration, markup, and language: duration via inline `${token:N}` prefix or `token_count`/`duration_tokens`; inline `[pause 0.5s]`, Pinyin, and IPA pass through unchanged; `language` hints the target language and `instructions` carries free-form style guidance (**Reported**).[^moss-tts-local-v15-card]

## License and citation

- Capture frontmatter declares `license: apache-2.0`, `library_name: transformers`, `pipeline_tag: text-to-speech`, and arXiv tag `arxiv:2603.18090` (**Observed** by static inspection of the capture frontmatter).[^moss-tts-local-v15-card]
- The card asks users to cite the [MOSS-TTS Technical Report](https://arxiv.org/abs/2603.18090), which is not in `raw/` and was not inspected (**Reported**).[^moss-tts-local-v15-card]

## Relationships

- Same-family compact model: [MOSS-TTS-Nano](moss-tts-nano.md) covers the 0.1B-parameter multilingual zero-shot cloning TTS with 48 kHz stereo and ONNX CPU paths, while this concept covers the larger Local-Transformer v1.5 line with 31 languages, language-tagged synthesis, and fixed 12-codebook stereo codec plus SGLang serving; no shared checkpoint is asserted (**Synthesis**).[^moss-tts-local-v15-card]
- Serving runtime: [SGLang-Omni](sglang-omni.md) lists MOSS-TTS Local among its `/v1/audio/speech` speech-generation families with Day-0 v1.5 native-streaming 48 kHz support, while this concept covers the checkpoint-side usage, generation parameters, and SGLang request shapes; consult that page for multi-model serving, scheduling, and transport (**Synthesis**).[^moss-tts-local-v15-card]
- Edge packaging: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) catalogs a `MOSS-TTS-Local-v1.5-GGUF` package (`moss_tts_local` family, BF16 + Q8, Apache-2.0) for the audio.cpp runtime, while this concept covers the upstream Hugging Face and SGLang-Omni source release; the packaging row was source-reported in that catalog and was not re-verified here (**Synthesis**).[^moss-tts-local-v15-card]
- Compared by [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) as a Vietnamese-capable GPU audio-streaming challenger, pending numeric Vietnamese quality, target-hardware TTFA, channel-framing and cancellation checks; not a replacement for the current baseline without A/B evidence (**Synthesis**).[^moss-tts-local-v15-card]
- Survey membership: [TTS Model Survey](tts-model-survey.md) compares this checkpoint against the compiled TTS catalog on languages, cloning and control, serving, and licensing (**Synthesis**).[^moss-tts-local-v15-card]

## Coverage and limits

- Source inspected statically only; no environment created, no package installed, no weights or tokenizer downloaded, no audio synthesized, and no cloning-stability, multilingual-gain, prosody, stereo-quality, latency, or throughput claim reproduced — all capability and serving claims are upstream assertions (**Synthesis**).[^moss-tts-local-v15-card]
- The v1.0 README (feature walkthrough, input schema, decoding hyperparameters, prefix-audio continuation, `UserMessage`/`AssistantMessage` fields, Pinyin/IPA preprocessing, evaluation tables), the `OpenMOSS/MOSS-TTS` repository and `pyproject.toml` contents, `MOSS-Audio-Tokenizer-v2` weights, the arXiv technical report, remote demo audio, the SGLang-Omni cookbook plus `moss_tts_local.yaml` config, ModelScope/Blog/Studio/API/X/Discord targets, and badge images were linked but not fetched and are not in `raw/` (**Synthesis**).[^moss-tts-local-v15-card]
- No numeric quality, similarity, or latency benchmark appears in this card; the v1.0-vs-v1.5 comparisons are qualitative direction statements, including the language-omitted improve-some/regress-some caveat (**Synthesis**).[^moss-tts-local-v15-card]
- `raw/MOSS-TTS-v1.5.md` (flagship MossTTSDelay-8B-API v1.5 capture) is now ingested as [MOSS-TTS-v1.5](moss-tts-v1-5.md); do not conflate its MossTTSDelay-8B API and install/`generate` handling with this Local-Transformer card (**Synthesis**).[^moss-tts-local-v15-card]
- Release, compatibility, and serving claims carry `stale_after: 2027-10-07` per the `tts` domain rule (**Synthesis**).[^moss-tts-local-v15-card]

[^moss-tts-local-v15-card]: [MOSS-TTS-Local-Transformer-v1.5 model card](../raw/MOSS-TTS-Local-Transformer-v1.5.md) — locators: capture frontmatter (`license: apache-2.0`, `library_name: transformers`, `pipeline_tag: text-to-speech`, 31-code `language`, `arxiv:2603.18090` tag); title plus intro (continued from v1.0 with 6 preserved capabilities and v1.0 README pointer); 6-bullet v1.5 improvements (stereo via MOSS-Audio-Tokenizer-v2 with `[channels, samples]` save rule; language-tag strength with omit-vs-specified caveat and `language="French"` fence; cloning stability and variance; long-reference short-text; punctuation prosody; `[pause 3.2s]` with 静夜思 example); `Supported Languages` 31-cell table (20 kept plus Cantonese, Dutch, Finnish, Hindi, Macedonian, Malay, Romanian, Swahili, Tagalog, Thai, Vietnamese); `Environment Setup` (Transformers 5.0.0/Qwen3 fence, conda python=3.12, `MOSS-TTS` clone plus `.[torch-runtime]` cu128 fence, `pyproject.toml` torch/torchaudio 2.9.1+cu128 pins, FlashAttention 2 `.[flash-attn]` plus `--no-build-isolation` and `MAX_JOBS=4` fences with hardware/dtype caveats); `Basic Usage` (fixed 12-codebook tip; `AutoProcessor`/`AutoModel` with `trust_remote_code=True`; cuDNN-SDPA disable plus fallback enables; `resolve_attn_implementation` logic; `audio_tokenizer.to(device)`; 7-pattern `build_user_message` fences with remote demo URLs and `tokens=125` at 12.5 fps note; `generate` fence with `max_new_tokens=4096`, `do_sample`, `audio_temperature=1.7`, `audio_top_p=0.8`, `audio_top_k=25`, `audio_repetition_penalty=1.0`; stereo `torchaudio.save` line); `Generation Parameters` 5-row table; `Notes` (remote code, stereo shape, tokenizer v2, `sampling_rate` 48000 plus `n_vq` 12, attention fallbacks); `SGLang Usage` (OpenAI-compatible `/v1/audio/speech` scope sentence plus cookbook pointer; `hf download` plus `sgl-omni serve` fences with `moss_tts_local.yaml`; basic-speech, cloning with `references[].audio_path` plus `ref_audio`/`ref_text` shorthand, streaming `stream`/`pcm`/`audio` plus 48 kHz `ffmpeg` pipe, and `${token:N}`/`token_count`/`duration_tokens` plus `[pause 0.5s]`/Pinyin/IPA/`language`/`instructions` curl fences); `More Usage` v1.0 API-compatibility pointer; `Citation` (Technical Report arXiv:2603.18090).

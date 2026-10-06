---
type: Concept
title: MOSS-Transcribe-Diarize 0.9B
description: Upstream 0.9B joint long-form transcription, diarization, timestamp, and acoustic-event model for up to 90 minutes and 50+ languages with hotword prompting and SGLang/vLLM serving.
tags: [stt, diarization, long-form, multilingual, hotwords, timestamps]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: moss-transcribe-diarize-card
    resource: ../raw/MOSS-Transcribe-Diarize.md
    kind: documentation
    title: MOSS-Transcribe-Diarize 0.9B HF model card
---

MOSS-Transcribe-Diarize 0.9B is OpenMOSS / MOSI.AI's end-to-end 0.9B audio-understanding checkpoint that jointly transcribes, diarizes, timestamps, and annotates acoustic events in one pass over up to 90 minutes of audio or video across 50+ languages, emitting compact `[start][Sxx]text[end]` segments with anonymous speaker labels and supporting custom instructions plus hotword hints, served through Transformers, SGLang Omni, vLLM, and a local subtitle WebUI (**Reported**).[^moss-transcribe-diarize-card]

## Model identity and release

- Card title is `MOSS-Transcribe-Diarize 0.9B`; model ID is `OpenMOSS-Team/MOSS-Transcribe-Diarize`; code is `github.com/OpenMOSS/MOSS-Transcribe-Diarize`; technical report is `arXiv:2601.01554` (**Reported**).[^moss-transcribe-diarize-card]
- Frontmatter declares `license: apache-2.0`, `library_name: transformers`, `language: [en, zh]`, `pipeline_tag: audio-text-to-text`, `custom_code: true`, and tags including `moss`, `audio`, `speech`, `asr`, `diarization`, `timestamp-asr`, `long-form-audio`, `multimodal`, and `multilingual`; the 50+ language claim lives in prose, not the two-code frontmatter list (**Observed** by static inspection).[^moss-transcribe-diarize-card]
- Release history in `News`: 2026-07-09 0.9B release; 2026-07-14 first place in the 2nd MLC-SLM Challenge at INTERSPEECH 2026 across 14 languages (English, French, German, Italian, Portuguese, Spanish, Japanese, Korean, Russian, Thai, Vietnamese, Tagalog, Urdu, Turkish); 2026-07-22 subtitle Web UI in Simplified Chinese and English (**Reported**).[^moss-transcribe-diarize-card]
- Loading requires custom remote code with `trust_remote_code=True` for both model and processor; the `Model Architecture` figure (`Model_Architecture.png`) is referenced but absent from `raw/` and was not inspected (**Reported**, with image limit **Synthesis**).[^moss-transcribe-diarize-card]
- License is Apache License 2.0; citation key is `moss_transcribe_diarize_2026` (MOSI.AI, 2026, `eprint 2601.01554`, `cs.SD`) (**Reported**).[^moss-transcribe-diarize-card]

## Capabilities

- Long-form single pass: one-pass inference on recordings up to 90 minutes, aimed at meetings, calls, podcasts, interviews, lectures, and videos, instead of stitching separate ASR plus diarization systems (**Reported**).[^moss-transcribe-diarize-card]
- Joint transcription plus diarization plus timestamps: time-aligned text with consistent anonymous labels `[S01]`, `[S02]`, and beyond; labels are relative within one input and are not real speaker identities (**Reported**).[^moss-transcribe-diarize-card]
- Acoustic-event awareness: can emit acoustic-event annotations alongside speech for a richer who-spoke-when view (**Reported**).[^moss-transcribe-diarize-card]
- Promptable generation: supports custom transcription instructions, hotword lists for domain terms, and acoustic-event annotation toggles; extra prompt recipes live in `examples/prompts.md`, which was not in `raw/` and was not inspected (**Reported**, with unfetched-pointer limit).[^moss-transcribe-diarize-card]

## Output format

- Canonical segment is `[start_time][Sxx]transcribed speech[end_time]` with times in seconds, e.g. `[0.48][S01]Welcome everyone[1.66][12.26][S02]The new transcription pipeline is ready for evaluation[13.81][14.36][S01]Great, include the diarization results in the report[18.76]` (**Reported**).[^moss-transcribe-diarize-card]
- Python helper `parse_transcript(result["text"])` yields segments with `start`, `end`, `speaker`, and `text` fields (**Reported**).[^moss-transcribe-diarize-card]

## Evaluation

All figures below are vendor-reported card tables; nothing was executed or reproduced (**Synthesis**).[^moss-transcribe-diarize-card]

- Protocol: CER, concatenated minimum-permutation CER (cpCER), and Delta-cp on AISHELL-4, Alimeeting, Podcast, and Movies; lower is better; `-` means unavailable (**Reported**).[^moss-transcribe-diarize-card]
- AISHELL-4: MOSS 0.9B 14.84 / 15.83 / 0.99 is the best open row in the card, behind only MOSS Pro (13.78 / 14.02 / 0.24); next rivals are Doubao 18.18 / 27.86 / 9.68 and ElevenLabs 19.58 / 37.95 / 18.36 (**Reported**).[^moss-transcribe-diarize-card]
- Alimeeting: MOSS 0.9B 24.86 / 22.17 / −2.69 is the best non-Pro row, behind MOSS Pro (18.22 / 13.94 / −4.27); rivals span 25.25–27.43 CER and 29.33–41.64 cpCER (**Reported**).[^moss-transcribe-diarize-card]
- Podcast: MOSS 0.9B 5.97 / 7.37 with Delta-cp 1.40 (best Delta-cp in the card); MOSS Pro leads CER/cpCER at 4.46 / 6.97 with Delta-cp 2.51; Gemini 2.5 Pro and Doubao follow at 7.38 / 10.23 and 7.93 / 10.54 (**Reported**).[^moss-transcribe-diarize-card]
- Movies: MOSS 0.9B 6.36 / 12.76 / 6.40 trails MOSS Pro (5.86 / 11.78 / 5.92) and Gemini 3 Pro on Delta-cp (6.11); GPT-4o, Gemini 2.5 Pro, VIBEVOICE ASR, Doubao, and ElevenLabs are worse on CER/cpCER in the same table (**Reported**).[^moss-transcribe-diarize-card]
- Baselines in the table are Doubao, ElevenLabs, GPT-4o (Movies only), Gemini 2.5 Pro, Gemini 3 Pro (no Podcast row), and VIBEVOICE ASR; GPT-4o and some Gemini cells are `-` (**Reported**).[^moss-transcribe-diarize-card]

## Python usage

- Setup: clean Python 3.12 env (`conda create -n moss-transcribe-diarize python=3.12`), clone `OpenMOSS/MOSS-Transcribe-Diarize`, install `torch`/`torchaudio` from the cu128 index, then `pip install -e .`; the repo helpers cover audio/video loading, message construction, transcript parsing, CLI inference, and the subtitle app, while weights plus remote-code files load from Hugging Face (**Reported**).[^moss-transcribe-diarize-card]
- Inference defaults from the card fence: `resolve_device("auto")`, `bfloat16` on CUDA else `float32`, `attn_implementation="sdpa"` (or `flash_attention_2` with flash-attn installed), `build_transcription_messages(audio_path)`, `generate_transcription(..., max_new_tokens=2048, do_sample=False)`, then `parse_transcript` (**Reported**).[^moss-transcribe-diarize-card]
- Message flow follows the Qwen multimodal pattern: `processor.apply_chat_template(messages, tokenize=False)` renders text with audio placeholders; helpers load waveforms from the same messages; `processor(text=text, audio=audios)` computes Whisper input features and expands placeholders; `model.generate(...)` emits the timestamped diarized text (**Reported**).[^moss-transcribe-diarize-card]

## Prompting and hotwords

- Default prompt is optimized for timestamped diarized output (Chinese): `请将音频转写为文本，每一段需以起始时间戳和说话人编号（[S01]、[S02]、[S03]…）开头，正文为对应的语音内容，并在段末标注结束时间戳，以清晰标明该段语音范围。` (**Reported**).[^moss-transcribe-diarize-card]
- Hotwords append a hint to that prompt: `...以清晰标明该段语音范围。热词提示：热词1, 热词2, 热词3` (**Reported**).[^moss-transcribe-diarize-card]

## Serving

- Recommended serving is SGLang Omni over OpenAI-compatible `POST /v1/audio/transcriptions`; on CUDA 12 SGLang is stated as unsupported and vLLM should be used instead (**Reported**).[^moss-transcribe-diarize-card]
- SGLang path: follow the `sglang-omni` installation guide (not in `raw/`), `hf download OpenMOSS-Team/MOSS-Transcribe-Diarize`, then `sgl-omni serve --model-path OpenMOSS-Team/MOSS-Transcribe-Diarize --port 8000 --max-running-requests 16 --cuda-graph-max-bs 16 --mem-fraction-static 0.80`; use `response_format=verbose_json` for parsed speaker segments (`json` returns raw text only) and raise `max_new_tokens=65536` for longer multi-speaker audio (**Reported**).[^moss-transcribe-diarize-card]
- vLLM path: install a pinned vLLM nightly including the MOSS registration (`cu129` wheel for CUDA 12, `cu130` for CUDA 13 via the card's `wheels.vllm.ai` index), then `vllm serve OpenMOSS-Team/MOSS-Transcribe-Diarize --trust-remote-code`; the card curl uses `response_format="json"` with `temperature="0"` (**Reported**).[^moss-transcribe-diarize-card]

## Subtitle workflow

- Interactive: `mtd-subtitle-web --model OpenMOSS-Team/MOSS-Transcribe-Diarize --host 127.0.0.1 --port 7860`, open `http://127.0.0.1:7860`, upload audio/video, review parsed segments, download JSON/SRT/ASS, or burn MP4 when `ffmpeg` and `ffprobe` are on `PATH` (**Reported**).[^moss-transcribe-diarize-card]
- Batch: `mtd-subtitle /path/to/input.mp4 --model OpenMOSS-Team/MOSS-Transcribe-Diarize --out-dir runs/example --render` (**Reported**).[^moss-transcribe-diarize-card]

## Relationships

- GGUF CPU port: [MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp)](moss-transcribe-cpp-gguf.md) packages these upstream weights as self-contained GGUF files (f16 through q4_0) for the zero-Python moss-transcribe.cpp CPU runtime with a published quantization ladder, while this concept covers the upstream 0.9B Transformers card, benchmarks, prompting, SGLang/vLLM serving, and subtitle workflow (**Synthesis**).[^moss-transcribe-diarize-card]
- Joint transcription-plus-diarization comparison: [VibeVoice-ASR](vibevoice-asr.md) covers a unified 60-minute 50+ language ASR model with speaker, timestamp, and hotword output but no numeric table in its card, while this concept covers a 90-minute 50+ language joint model with a four-suite CER/cpCER/Delta-cp table and hotword prompting (**Synthesis**).[^moss-transcribe-diarize-card]
- Diarization-only comparison: [Nemotron 3 Diarization](nemotron-3-diarization.md) covers a streaming/offline diarization-only model with DER/RTFx benchmarks, while this concept covers joint one-pass transcription plus diarization with transcript-accuracy (not DER) figures; no shared method is asserted (**Synthesis**).[^moss-transcribe-diarize-card]
- Serving runtime: [SGLang-Omni](sglang-omni.md) is the multi-stage GPU serving runtime this card recommends for `/v1/audio/transcriptions` with `verbose_json` speaker segments; check both before serving (**Synthesis**).[^moss-transcribe-diarize-card]

## Coverage and limits

- Source inspected statically only; no environment created, no package installed, no weight downloaded, no audio transcribed, no SGLang/vLLM server launched, and no CER, cpCER, Delta-cp, speed, or subtitle figure reproduced (**Synthesis**).[^moss-transcribe-diarize-card]
- Linked but unfetched and absent from `raw/`: `Model_Architecture.png`, the `OpenMOSS/MOSS-Transcribe-Diarize` repository (helpers, CLI, subtitle app, `examples/prompts.md`), Hugging Face weights plus remote code, arXiv:2601.01554, the `sglang-omni` installation guide, pinned vLLM nightly wheels, MOSI.AI / OpenMOSS sites, the MLC-SLM challenge page, and the MOSI playground hosting the Pro variant (**Synthesis**).[^moss-transcribe-diarize-card]
- Material gaps: architecture internals beyond the uninspected figure, training data and compute, 90-minute memory/VRAM behavior, streaming support (card describes offline long-form plus server endpoints, no streaming chunk protocol), per-language coverage beyond the 14 challenge languages, acoustic-event taxonomy, and Pro-variant weights/procedure are unstated; all identity, capability, benchmark, usage, and serving claims are source assertions, and release plus benchmark details carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^moss-transcribe-diarize-card]

[^moss-transcribe-diarize-card]: [MOSS-Transcribe-Diarize 0.9B HF model card](../raw/MOSS-Transcribe-Diarize.md) — locators: frontmatter (`license`, `library_name`, `language`, `pipeline_tag`, `tags`); header (0.9B joint transcription plus diarization plus timestamps plus acoustic events, 50+ languages, 90-minute single pass, hotword prompting, `[S01]`/`[S02]` labels); `News` (2026-07-09 release, 2026-07-14 MLC-SLM 14-language win, 2026-07-22 subtitle Web UI zh/en); `Introduction` (one-pass vs stitched ASR plus diarization, meetings/calls/podcasts/interviews/lectures/videos, three capability bullets); `Model Architecture` (`Model_Architecture.png`, `trust_remote_code=True`); `Evaluation` (CER/cpCER/Delta-cp definitions, dash rule, 8-row × 12-cell table across AISHELL-4, Alimeeting, Podcast, Movies); `Quickstart > Environment Setup` (`conda create -n moss-transcribe-diarize python=3.12`, `git clone`, cu128 `torch`/`torchaudio`, `pip install -e .`); `Quickstart > Python Usage` (fence: `AutoModelForCausalLM`/`AutoProcessor`, `resolve_device`, bfloat16/float32 rule, `sdpa` vs `flash_attention_2`, `build_transcription_messages`, `generate_transcription` with `max_new_tokens=2048`/`do_sample=False`, `parse_transcript` with `start`/`end`/`speaker`/`text`; four-step Qwen multimodal flow); `Custom Prompt and Hotwords` (default Chinese prompt fence, `热词提示：热词1, 热词2, 热词3` suffix, `examples/prompts.md` link); `Serve with SGLang and VLLM` (`sgl-omni serve` with `--port 8000 --max-running-requests 16 --cuda-graph-max-bs 16 --mem-fraction-static 0.80`, `hf download`, `/v1/audio/transcriptions` curls with `response_format=verbose_json` vs `json` and `max_new_tokens=65536`, CUDA-12 vLLM note, cu129/cu130 `wheels.vllm.ai` fences, `vllm serve ... --trust-remote-code`, `temperature="0"` curl); `Subtitle Web App` (`mtd-subtitle-web --model/--host/--port`, `http://127.0.0.1:7860`, JSON/SRT/ASS plus `ffmpeg`/`ffprobe` MP4 burn-in, `mtd-subtitle ... --out-dir/--render`); `Output Format` (`[start][Sxx]text[end]` spec, three-segment example, relative-label warning); `More Information` (GitHub/MOSI/OpenMOSS links); `License` (Apache-2.0); `Citation` (`moss_transcribe_diarize_2026` bibtex).

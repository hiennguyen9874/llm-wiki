---
type: Concept
title: Qwen3-ASR family
description: Open-weight multilingual ASR family with 1.7B and 0.6B checkpoints plus a 0.6B forced aligner, covering 30 languages and 22 Chinese dialects with unified offline/streaming inference, vLLM serving, and timestamp prediction.
tags: [stt, asr, multilingual, streaming, forced-alignment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T20:00:00Z }
stale_after: 2027-10-06
sources:
  - id: qwen3-asr-readme
    resource: ../raw/Qwen3-ASR-0.6B.md
    kind: documentation
    title: Qwen3-ASR README and model card (family)
  - id: qwen3-asr-hf-card
    resource: ../raw/Qwen3-ASR-0.6B-hf.md
    kind: documentation
    title: Qwen3-ASR-0.6B-hf Transformers-native model card
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
---

Qwen3-ASR is an open-weight automatic speech recognition family from Qwen built on the Qwen3-Omni foundation model, with a 1.7B accuracy flagship and a 0.6B efficiency point for joint language identification plus transcription across 30 languages and 22 Chinese dialects, a separate Qwen3-ForcedAligner-0.6B for word/character timestamps, unified streaming/offline inference with long-audio support including singing and songs with background music, and a full toolkit (`qwen-asr` Transformers and vLLM backends, async serving, Gradio and streaming demos, DashScope APIs, Docker, day-0 vLLM support), reported as state-of-the-art among open-source ASR with the 1.7B competitive against proprietary APIs and the aligner surpassing end-to-end forced-alignment baselines (**Reported**).[^qwen3-asr-readme]

## Model identity and lineage

- Family members are `Qwen/Qwen3-ASR-1.7B`, `Qwen/Qwen3-ASR-0.6B`, and `Qwen/Qwen3-ForcedAligner-0.6B`, all downloadable from ModelScope or Hugging Face and auto-downloaded on model load by the `qwen-asr` package or vLLM unless pre-staged locally (**Reported**).[^qwen3-asr-readme]
- Foundation is Qwen3-Omni, credited for the family's audio understanding capability after large-scale speech training (**Reported**).[^qwen3-asr-readme]
- Frontmatter of the ingested card declares `license: apache-2.0` and `pipeline_tag: automatic-speech-recognition` (**Observed** by static inspection).[^qwen3-asr-readme]
- Technical report citation is Shi et al., "Qwen3-ASR Technical Report", arXiv 2601.21337, 2026 (**Reported**).[^qwen3-asr-readme]

## Language and audio coverage

| Model | Languages | Dialects / accents | Inference mode | Audio types |
| --- | --- | --- | --- | --- |
| Qwen3-ASR-1.7B and Qwen3-ASR-0.6B | 30: zh, en, yue, ar, de, fr, es, pt, id, it, ko, ru, th, vi, ja, tr, hi, ms, nl, sv, da, fi, pl, cs, fil, fa, el, hu, mk, ro | 22 Chinese varieties: Anhui, Dongbei, Fujian, Gansu, Guizhou, Hebei, Henan, Hubei, Hunan, Jiangxi, Ningxia, Shandong, Shaanxi, Shanxi, Sichuan, Tianjin, Yunnan, Zhejiang, Cantonese Hong Kong accent, Cantonese Guangdong accent, Wu, Minnan; plus multi-country English accents | Offline / Streaming | Speech, singing voice, songs with BGM |
| Qwen3-ForcedAligner-0.6B | 11: Chinese, English, Cantonese, French, German, Italian, Japanese, Korean, Portuguese, Russian, Spanish | — | NAR | Speech |

- Coverage headline is 52 languages and dialects (30 languages plus 22 Chinese dialects) for language identification and ASR, with multi-region English accents called out (**Reported**).[^qwen3-asr-readme]
- The forced aligner predicts timestamps for arbitrary units within up to 5 minutes of speech in its 11 languages (**Reported**).[^qwen3-asr-readme]

## Key capabilities

- All-in-one language identification plus recognition in a single model; language can be auto-detected (`language=None`) or forced (for example `"English"`, `"Chinese"`) (**Reported**).[^qwen3-asr-readme]
- Accuracy/efficiency tradeoff: the 1.7B is the quality flagship while the 0.6B is stated to reach "2000 times throughput at a concurrency of 128" — the card gives no denominator, hardware, or unit for that multiplier, so treat it as an uninterpretable throughput claim rather than a usable figure (**Reported**, with ambiguity flagged as **Synthesis**).[^qwen3-asr-readme]
- Single-model streaming/offline unified inference with long-audio transcription; robustness is claimed under complex acoustics and challenging text patterns (**Reported**).[^qwen3-asr-readme]
- Toolkit breadth: vLLM batch inference, asynchronous serving, streaming inference, and timestamp prediction in one framework (**Reported**).[^qwen3-asr-readme]

## Inference and serving

- Environment: fresh isolated Python 3.12 environment recommended (`conda create -n qwen3-asr python=3.12`); minimal install `pip install -U qwen-asr`, vLLM backend `pip install -U qwen-asr[vllm]`, editable source install `git clone https://github.com/QwenLM/Qwen3-ASR.git` plus `pip install -e .` (optionally `.[vllm]`); FlashAttention 2 recommended for memory and long-input speed via `pip install -U flash-attn --no-build-isolation`, with `MAX_JOBS=4` on machines under 96 GB RAM with many CPU cores, compatible hardware required, and use restricted to `float16`/`bfloat16` (**Reported**).[^qwen3-asr-readme]
- Transformers backend: `Qwen3ASRModel.from_pretrained("Qwen/Qwen3-ASR-1.7B", dtype=torch.bfloat16, device_map="cuda:0", max_inference_batch_size=32, max_new_tokens=256)` then `model.transcribe(audio=...)`; audio inputs may be a local path, URL, base64 data, or `(np.ndarray, sr)` tuple, batched as a list; timestamps need `forced_aligner="Qwen/Qwen3-ForcedAligner-0.6B"` plus `forced_aligner_kwargs` and `return_time_stamps=True`, yielding per-result `language`, `text`, and `time_stamps` (**Reported**).[^qwen3-asr-readme]
- vLLM backend (fastest per the card): `Qwen3ASRModel.LLM(model=..., gpu_memory_utilization=0.7, max_inference_batch_size=128, max_new_tokens=4096, forced_aligner=..., forced_aligner_kwargs=...)` with the same `transcribe` call; FlashAttention install advised when timestamps are used; code must sit under `if __name__ == '__main__':` to avoid the documented vLLM `spawn` multiprocessing error (**Reported**).[^qwen3-asr-readme]
- Server: `qwen-asr-serve Qwen/Qwen3-ASR-1.7B --gpu-memory-utilization 0.8 --host 0.0.0.0 --port 8000` wraps `vllm serve` and forwards its arguments; requests use the OpenAI chat-completions shape (`messages` with `audio_url`) and `parse_asr_output(content)` splits the reply into `(language, text)`; plain vLLM serving is `vllm serve Qwen/Qwen3-ASR-1.7B`, with OpenAI SDK (`chat.completions.create`, `audio.transcriptions.create`), cURL, and offline `LLM(...).chat(conversation, SamplingParams(temperature=0.01, max_tokens=256))` forms all documented, and day-0 vLLM support claimed (**Reported**).[^qwen3-asr-readme]
- Streaming: fully supported but only on the vLLM backend, with no batch inference and no timestamps; a Flask streaming demo captures browser microphone audio, resamples to 16,000 Hz, and pushes PCM chunks (`qwen-asr-demo-streaming --asr-model-path ... --host 0.0.0.0 --port 8000 --gpu-memory-utilization 0.9`) (**Reported**).[^qwen3-asr-readme]
- Direct aligner use: `Qwen3ForcedAligner.from_pretrained("Qwen/Qwen3-ForcedAligner-0.6B", ...)` then `model.align(audio=..., text=..., language="Chinese")`, returning word/character segments with `text`, `start_time`, `end_time`; same local/URL/base64/array inputs plus batch inference (**Reported**).[^qwen3-asr-readme]
- Gradio demo `qwen-asr-demo` supports transformers and vLLM backends with `--asr-checkpoint`, `--backend`, `--cuda-visible-devices` (sets `CUDA_VISIBLE_DEVICES` since vLLM ignores `cuda:0` style selection), JSON `--backend-kwargs` / `--aligner-kwargs`, optional `--aligner-checkpoint` (timestamps UI hidden without it), and `--ssl-certfile`/`--ssl-keyfile`/`--no-ssl-verify` HTTPS for remote microphone permission, with a self-signed `openssl req -x509` example for testing (**Reported**).[^qwen3-asr-readme]
- Hosted option: DashScope Real-time API and FileTrans API for Qwen3-ASR, with mainland-China and international documentation links (**Reported**).[^qwen3-asr-readme]
- Docker: prebuilt `qwenllm/qwen3-asr` image needs only the GPU driver plus model files; documented `docker run --gpus all` mounts the workspace at `/data/shared/Qwen3-ASR`, maps host port to container port 80, requires services to bind `0.0.0.0`, and uses `--shm-size=4gb` (**Reported**).[^qwen3-asr-readme]

## Transformers-native (`-hf`) usage

- Native checkpoints are `Qwen/Qwen3-ASR-1.7B-hf` and `Qwen/Qwen3-ASR-0.6B-hf` plus `Qwen/Qwen3-ForcedAligner-0.6B-hf`, supported in Transformers from v5.13.0 via `pip install "transformers>=5.13.0"`; the card's checkpoint table repeats the 30-language, 22-dialect, offline/streaming, and speech/singing/songs-with-BGM coverage of the family card (**Reported**).[^qwen3-asr-hf-card]
- Recommended entry point is `processor.apply_transcription_request(audio=...)` (a convenience wrapper over `apply_chat_template`) with `AutoProcessor` plus `AutoModelForMultimodalLM` (or `Qwen3ASRForConditionalGeneration`), `model.generate(..., max_new_tokens=256)`, and three decode modes: raw (includes the language tag and `<asr_text>` marker), `return_format="parsed"` (dict with `language` and `transcription`), and `return_format="transcription_only"` (**Reported**).[^qwen3-asr-hf-card]
- Language forcing passes `language="Chinese"` (or code `"zh"`) to `apply_transcription_request`, which prefills the assistant turn with `language <NAME><asr_text>` and `continue_final_message=True`; when forcing in a batch, every sample sets the prefill, using an empty prefill for the auto-detect samples (**Reported**).[^qwen3-asr-hf-card]
- Domain context and hotwords pass as free-form `prompt` (for example `"Vocabulary: Quilter, apostle, gospel."`) or, in the chat-template form, as a system message; batch inference passes a list of audio paths with a per-sample language list where `None` means auto-detect (**Reported**).[^qwen3-asr-hf-card]
- Fine-tuning puts the target transcript in the assistant turn in the pretrained output format `language <NAME><asr_text>...` and passes `processor_kwargs={"output_labels": True}`; audio and padding positions are masked automatically and training uses `model(**inputs).loss` (**Reported**).[^qwen3-asr-hf-card]
- Word timestamps use the aligner as `AutoModelForTokenClassification` (card example loads it in `torch.bfloat16`): transcribe first, then `aligner_processor.prepare_forced_aligner_inputs(audio=..., transcript=..., language=...)`, a single forward pass, and `decode_forced_alignment(logits, input_ids, word_lists, timestamp_token_id)` yielding per-word `text`, `start_time`, `end_time`; Japanese needs `nagisa` and Korean needs `soynlp` (**Reported**).[^qwen3-asr-hf-card]
- Two shortcuts exist: `pipeline("any-to-any", model=..., device_map="auto")` with `pipe.processor.extract_transcription(raw_text)`, and `torch.compile` on `model.forward`, observed on an A100 at about 2.5x for the forced aligner and 2.4x for ASR `generate` at batch size 4; the card notes the aligner fits bulk timestamping because it runs one forward pass with no autoregressive decoding (**Reported**).[^qwen3-asr-hf-card]

## Evaluation protocol

- All reported runs use `dtype=torch.bfloat16` with `max_new_tokens=1024` under vLLM, greedy decoding, and no language parameter specified (**Reported**).[^qwen3-asr-readme]
- All benchmark numbers below are source assertions from the card's tables; nothing was executed or reproduced for this wiki (**Synthesis**).[^qwen3-asr-readme]

## Benchmark highlights

Public-set WER in percent, lower is better; 1.7B leads most columns with noted exceptions (**Reported**):[^qwen3-asr-readme]

| Suite | 1.7B | 0.6B | Closest rival in card |
| --- | ---: | ---: | --- |
| Librispeech clean / other | 1.63 / 3.38 | 2.11 / 4.55 | GPT-4o-Transcribe 1.39 clean; 1.7B best on other |
| GigaSpeech | 8.45 | 8.88 | Gemini-2.5-Pro 9.37 |
| CommonVoice-en | 7.39 | 9.92 | GPT-4o-Transcribe 9.08 |
| WenetSpeech net / meeting | 4.97 / 5.88 | 5.97 / 6.88 | Fun-ASR-MLT-Nano 6.35 net-only |
| AISHELL-2 test | 2.71 | 3.15 | Doubao-ASR 2.85 |
| SpeechIO | 2.88 | 3.44 | Doubao-ASR 2.93 |
| KeSpeech (dialect) | 5.10 | 7.08 | Doubao-ASR 5.27 |
| Fleurs-yue | 3.98 | 5.79 | Doubao-ASR / GPT-4o 4.98 |
| WenetSpeech-Sichuan easy / hard | 11.99 / 21.63 | 13.92 / 24.45 | Doubao-ASR 11.40 / 20.20 (1.7B not best here) |

- Internal sets (WER down): Dialog accented English 16.07, Elders and Kids 3.81, ExtremeNoise 16.17, TongueTwister 2.44, Dialog Mandarin 6.54, Dialog Cantonese 4.12, Dialog Chinese dialects 15.94 — 1.7B best in every internal row, 0.6B second on accented English (16.62), Cantonese (4.80), and dialects (18.24); accent coverage is 16 accents averaged and dialect coverage 22 dialects averaged (**Reported**).[^qwen3-asr-readme]
- Multilingual WER down (1.7B best except the low-resource tail): MLS 8.55, CommonVoice 9.18, MLC-SLM 12.74, Fleurs 4.90, Fleurs-8-extra-languages 6.62, News-Multilingual 12.80; on the 10-further-language Fleurs tail Whisper-large-v3 leads at 8.16 versus 12.60 for 1.7B and 21.80 for 0.6B (**Reported**).[^qwen3-asr-readme]
- Language identification accuracy up: 1.7B averages 97.9 and 0.6B 96.8 against Whisper-large-v3 at 94.1 across MLS, CommonVoice, MLC-SLM, and 30-language Fleurs (**Reported**).[^qwen3-asr-readme]
- Singing and songs with BGM (WER down): M4Singer 5.98, MIR-1k-vocal 6.25, Popcs 8.52 best for 1.7B; Opencpop 3.08 just behind Fun-ASR-MLT-Nano at 2.98; EntireSongs-zh 13.91 best; EntireSongs-en 14.60 behind Gemini-2.5-Pro at 12.18 (**Reported**).[^qwen3-asr-readme]
- Streaming versus offline gap (WER down, Librispeech clean/other plus Fleurs-en/zh average): 1.7B offline 2.69 versus streaming 3.33; 0.6B offline 3.48 versus streaming 4.40 (**Reported**).[^qwen3-asr-readme]
- Forced alignment (average absolute shift, ms, down): on MFA-labeled raw audio 1.7B-aligner averages 42.9 against NFA 129.8, WhisperX 133.2, and Monotonic-Aligner 161.1; on 300-second concatenations 52.9 against NFA 246.7, WhisperX 2708.4, and Monotonic 1742.4, showing long-form robustness; on human-labeled audio 32.4 against 141.3 / 101.2, including cross-lingual 34.2–42.5 ms rows (**Reported**).[^qwen3-asr-readme]
- Hugging Face Open ASR Leaderboard snapshot dated 26 June 2026 (WER percent, lower is better) gives the `-hf` checkpoints a directly comparable English average: 1.7B-hf mean 5.59 and 0.6B-hf mean 6.31 (**Reported**):[^qwen3-asr-hf-card]

| Model | Mean WER | AMI | Earnings22 | GigaSpeech | LS Clean | LS Other | SPGISpeech | VoxPopuli |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen3-ASR-1.7B-hf | 5.59 | 9.26 | 9.88 | 7.25 | 1.24 | 2.92 | 2.58 | 5.99 |
| Qwen3-ASR-0.6B-hf | 6.31 | 10.57 | 10.72 | 7.65 | 1.69 | 3.97 | 2.74 | 6.80 |

- Do not merge these cells with the family card's own tables: this card's LibriSpeech-clean/other figures (1.7B: 1.24 / 2.92) differ from the family README's (1.63 / 3.38) without a stated protocol change, so treat the two snapshots as separate protocols (**Synthesis**).[^qwen3-asr-readme][^qwen3-asr-hf-card]

## Relationships

- Used by [Audio8-ASR-0.1B](audio8-asr-0.1b.md): that compact model pairs a Qwen3-ASR audio encoder (its card names `Qwen/Qwen3-ASR-0.6B` as the backbone) with a small Qwen-style LM, so read this family concept for the encoder lineage's language coverage, streaming/offline behavior, and serving toolkit (**Synthesis**).[^qwen3-asr-readme]
- Benchmarked against [Fun-ASR-MLT-Nano-2512](fun-asr-mlt-nano-2512.md), [Fun-ASR-Nano-2512](fun-asr-nano-2512.md), and [GLM-ASR-Nano-2512](glm-asr-nano-2512.md): the card's public, multilingual, singing, and alignment tables carry `Fun-ASR-MLT-Nano`, `Fun-ASR-Nano`, and `GLM-ASR-Nano-2512` columns as baselines, so cross-read those concepts when comparing compact Chinese-oriented ASR checkpoints; the WER numbers above are Qwen3-ASR-side values as reported in this card, not a merged ranking (**Synthesis**).[^qwen3-asr-readme]
- Vietnamese figures from an AI-compiled report citing the tech report (arXiv 2601.21337): Fleurs-vi 5.55 (1.7B) / 8.52 (0.6B) and MLC-SLM-vi 14.92 / 17.67, with the 0.6B via vLLM reaching 92 ms average TTFT and 2000 s of speech per second at concurrency 128; the report names this family the main Whisper replacement for Vietnamese in [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) and [Whisper Hallucination Mitigation for Vietnamese](whisper-hallucination-mitigation.md) (**Reported**).[^claude-pipeline-report]

## Coverage and limits

- Source inspected statically only; no package installed, no model downloaded, no audio transcribed, and no WER, accuracy, AAS, or throughput figure reproduced (**Synthesis**).[^qwen3-asr-readme]
- Linked but unfetched and absent from `raw/`: Hugging Face and ModelScope model pages, `qwen-asr` PyPI package and GitHub repository with its `examples/` scripts, Hugging Face sample-audio URLs, `vllm serve` and OpenAI endpoints, DashScope API docs, Docker Hub image `qwenllm/qwen3-asr`, the two header figures (introduction PNG, architecture overview JPG — architecture detail therefore comes only from prose, not the diagram), and every benchmark dataset; example commands are transcribed, not executed (**Synthesis**).[^qwen3-asr-readme]
- `raw/Qwen3-ASR-1.7B.md` was found byte-identical to the ingested family file (verified by file comparison in an earlier session), so it is a duplicate of the same family card rather than a second source; ingesting it again should be a no-op (future idempotency note, **Synthesis**).[^qwen3-asr-readme]
- `raw/Qwen3-ASR-0.6B-hf.md` inspected statically only: none of its example commands executed, no model downloaded, no audio transcribed; linked-but-unfetched artifacts are the three `-hf` checkpoint pages, the two header figures, and the `qianwen-res` plus `bezzam/audio_samples` sample-audio URLs (**Synthesis**).[^qwen3-asr-hf-card]
- Material gaps: the "2000 times throughput" claim has no usable denominator or hardware; architecture section carries figures without transcribed text; per-language results beyond the averaged tables, training data and compute, and DashScope pricing or latency are not in the card; all identity, coverage, and accuracy claims are source assertions, and model-release plus benchmark details carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^qwen3-asr-readme]

[^qwen3-asr-readme]: [Qwen3-ASR README and model card](../raw/Qwen3-ASR-0.6B.md) — locators: frontmatter (`license`, `pipeline_tag`); section `Introduction` (family members, 52-language claim, Qwen3-Omni lineage, SOTA/competitive claim, four feature bullets incl. 30 languages plus 22 dialects, 2000x-throughput sentence, 5-minute/11-language aligner, toolkit sentence); section `Model Architecture` (figures only); section `Released Models Description and Download` (30-language plus 22-dialect table, offline/streaming and speech/singing/songs cells, 11-language NAR aligner row, ModelScope and Hugging Face download commands); section `Environment Setup` (conda 3.12, `pip install qwen-asr` / `qwen-asr[vllm]`, editable install, FlashAttention 2 commands, `MAX_JOBS=4`, float16/bfloat16 note); `Quick Inference` fence (`from_pretrained`, `max_inference_batch_size`, `max_new_tokens`, audio-input forms, `language`, timestamps via `forced_aligner`); `vLLM Backend` fence (`LLM(...)`, `gpu_memory_utilization`, `qwen-asr-serve`, OpenAI chat/transcription, `__main__` spawn note); `Streaming Inference` (vLLM-only, no batch/timestamps); `ForcedAligner Usage` fence (`Qwen3ForcedAligner.from_pretrained`, `align`, `start_time`/`end_time`); `DashScope API Usage` (Real-time and FileTrans rows); `Gradio Demo` and `Streaming Demo` (`qwen-asr-demo` backend/CUDA/timestamps/HTTPS variants, 16,000 Hz Flask demo); `Deployment with vLLM` (nightly install, `vllm serve`, SDK/cURL/offline forms); `Docker` (`qwenllm/qwen3-asr`, `--gpus all`, mount/port/`--shm-size`); `Evaluation` protocol paragraph (bfloat16, `max_new_tokens=1024`, greedy, no language) and benchmark tables (public WER, internal WER, multilingual WER, LID accuracy, singing/song WER, streaming/offline WER, forced-alignment AAS); section `Citation` (arXiv 2601.21337 BibTeX).

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `TL;DR` verified-facts bullet; `Key Findings` 3; `PHẦN 1` §4 Qwen3-ASR row; `Triển khai` scaling bullet; `Recommendations` tier table and replacement triggers.

[^qwen3-asr-hf-card]: [Qwen3-ASR-0.6B-hf Transformers-native model card](../raw/Qwen3-ASR-0.6B-hf.md) — locators: frontmatter (`license`, `pipeline_tag`, `library_name`, 30-language list); `Overview` (1.7B/0.6B family, 52-language claim, Qwen3-Omni lineage, 2000x-throughput sentence, 5-minute/11-language aligner); `Available Checkpoints` table (30 languages, 22 dialects, offline/streaming, speech/singing/songs, 11-language NAR aligner row); `Usage` (`apply_transcription_request` fence with three decode formats; `language` forcing fence; `prompt` hotwords fence; batch fence; chat-template prefill fence with `continue_final_message`; training fence with `output_labels`; forced-alignment fence with `prepare_forced_aligner_inputs` / `decode_forced_alignment` and `nagisa`/`soynlp` note; `pipeline("any-to-any")` fence with `extract_transcription`); `Speed & Memory Improvements` (`torch.compile` fence, A100 2.5x aligner / 2.4x ASR at batch size 4); `Evaluation` (HF Open ASR Leaderboard table dated 26 June 2026, both `-hf` rows); `Citation` (arXiv 2601.21337 BibTeX).

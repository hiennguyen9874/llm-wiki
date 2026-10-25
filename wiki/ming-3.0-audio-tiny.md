---
type: Concept
title: Ming-3.0-audio-tiny
description: inclusionAI 9.3B-total, 2.7B-active native audio-language Mixture-of-Experts model that takes audio plus text instructions and returns text or, through an optional Talker, synthesized speech, covering Chinese-English ASR, audio understanding and audio reasoning without a numeric benchmark in the captured text.
tags: [stt, tts, audio-llm, mixture-of-experts, chinese, english]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T13:10:00Z }
stale_after: 2027-04-21
sources:
  - id: ming-audio-tiny-card
    resource: ../raw/inclusionAI-Ming-3.0-audio-tiny.md
    kind: documentation
    title: Ming-3.0-audio-tiny model card capture
---

Ming-3.0-audio-tiny from inclusionAI is a compact native audio-language Mixture-of-Experts model that consumes audio together with a text instruction and answers in text, optionally with synthesized speech from an attached Talker, positioned for Chinese-English speech recognition, spoken question answering, audio understanding and audio reasoning at 9.3B total and 2.7B activated parameters per step (**Reported**).[^ming-audio-tiny-card] It is a different model from [Ming-3.0-asr-tiny](ming-3.0-asr-tiny.md) despite the shared `tiny` suffix: this card describes one audio-in, text-or-speech-out model, while that page describes a single-turn ASR checkpoint with a Ling-tiny-v3 backbone (**Observed/Synthesis**).[^ming-audio-tiny-card] No WER, CER or MOS number is recoverable from the captured text — every evaluation section is an image reference — so the model cannot be ranked against other ASR or TTS entries here (**Observed** coverage limit).[^ming-audio-tiny-card]

## Identity and family

- Developer is inclusionAI; the model type is a native audio-language MoE with audio and text instructions as input and text, or text plus optional synthesized speech, as output; primary languages are Chinese and English including varied accents and dialects; license MIT (**Reported**).[^ming-audio-tiny-card]
- Frontmatter declares `library_name: transformers`, languages `en` and `zh`, license `mit`, and tags including `automatic-speech-recognition`, `audio-understanding`, `audio-reasoning`, `speech-to-text`, `text-to-speech`, `conversational`, `mixture-of-experts` and `custom_code` (**Observed**).[^ming-audio-tiny-card]
- The capture prints no revision, release date or capture date, and no parameter count beyond the 9.3B/2.7B pair; whether 2.7B counts only MoE experts plus shared layers is not stated (**Observed** coverage limit).[^ming-audio-tiny-card]
- The card links a shared repository and two HF checkpoints — a larger `Ming-3.0-audio-flash` sibling and this `Ming-3.0-audio-tiny` — and says the benchmark figures cover both variants. Per-variant numbers are not separated in the text (**Reported**).[^ming-audio-tiny-card]
- Naming caution: the GitHub project is `inclusionAI/Ming-3.0-audio-flash` even for the Tiny example commands, and [Ming-3.0-asr-tiny](ming-3.0-asr-tiny.md) is a separate ASR-only checkpoint family. Do not transfer parameter counts, architecture or benchmark claims across these three names (**Observed/Synthesis**).[^ming-audio-tiny-card]

## Architecture and claimed capabilities

- Architecture is an audio encoder plus projector feeding a compact MoE language backbone, with an optional Talker that generates speech responses from the model's output (**Reported**).[^ming-audio-tiny-card]
- Claimed capabilities: complex Chinese and English speech recognition across dialects, accents, noisy environments and multi-speaker recordings; long-form audio understanding; multidimensional perception of speech, non-speech sounds, acoustic scenes and music; audio reasoning and question answering; and audio interaction returning text or optional speech with built-in voices or a reference voice (**Reported**).[^ming-audio-tiny-card]
- Not stated anywhere in the capture: encoder family or size, projector design, MoE layer count and expert count, context window or maximum audio duration, input sample rate and feature configuration, tokenizer, Talker size and its codec/sample rate, and weight footprint or VRAM (**Observed** coverage limit).[^ming-audio-tiny-card]
- The "long-audio understanding" highlight carries no duration, chunking recipe or context limit, so it is a capability claim rather than a measured envelope (**Reported/Synthesis**).[^ming-audio-tiny-card]
- Non-speech and music perception is recorded as catalog context only: `SCOPE.md` excludes music-only generation and non-speech modalities unless they feed the voice loop, and this model accepts speech for recognition and response in the same request (**Synthesis**).[^ming-audio-tiny-card]

## Speech recognition

- The validated ASR path asks the model to identify the spoken language and place a tab between the language label and the transcription; the card labels this prompt the validated one without printing it verbatim (**Reported**).[^ming-audio-tiny-card]
- The bundled CLI route is `examples/transformers_audio.py <audio> --model inclusionAI/Ming-3.0-audio-tiny --task asr --max-new-tokens 256 --no-repeat-ngram-size 10` (**Reported** example, not executed).[^ming-audio-tiny-card]
- The same script without `--task asr` performs audio understanding with a free-form prompt, for example "Please answer the question in the audio", at 512 new tokens in the Python path (**Reported**).[^ming-audio-tiny-card]
- No language list beyond Chinese and English, no timestamps, no diarization output format, no hotword or context-biasing control, and no streaming audio-input mode are documented; speech output is the only non-text output surface (**Observed** coverage limit).[^ming-audio-tiny-card]

## Transformers usage (reported, not executed)

The card supplies a Python path with `AutoProcessor` and `AutoModelForCausalLM` loaded from the checkpoint using `trust_remote_code=True` and `use_fast=False`, BF16 with `device_map="auto"`, a chat-style message list holding one audio part plus one text part, `audio_feats` cast to the model dtype, and greedy generation (`do_sample=False`) with special tokens skipped on decode (**Reported/Observed** example).[^ming-audio-tiny-card]

- Setup is a clone of the shared repository, a virtual environment and `pip install -r requirements-transformers.txt`; no version pins, Python or CUDA requirement is printed (**Reported**).[^ming-audio-tiny-card]
- `trust_remote_code=True` means checkpoint-shipped Python runs in-process. The card asks readers to review that code before enabling it; the code was not captured or audited here, so treat this as an unreviewed execution boundary rather than a verified one (**Synthesis**).[^ming-audio-tiny-card]
- Speech output and multi-GPU serving routes are compiled separately in [Ming-3.0-audio-tiny Serving](ming-3.0-audio-tiny-serving.md) (**Synthesis**).[^ming-audio-tiny-card]

## Evaluation

- Three image-only sections cover speech recognition (`assets/benchmark-asr.png`), audio intelligence (`assets/benchmark-audio-intelligence.png`) and text benchmarks (`assets/benchmark-text.png`). Values are percentages, higher is better unless marked with a downward arrow, and asterisked results are self-evaluated (**Observed** from surrounding text).[^ming-audio-tiny-card]
- All three files are absent from `raw/`, so no ASR accuracy, audio-understanding score or retained text-ability figure is compiled. The card defers latest notes and evaluation details to the GitHub README, which was not fetched (**Observed** coverage limit).[^ming-audio-tiny-card]
- Because the figures are shared between Tiny and Flash, even the missing plots would not by themselves establish a per-variant ranking without the evaluation notes (**Synthesis**).[^ming-audio-tiny-card]

## License

- MIT is declared in frontmatter and the `License` section, with a separate `LEGAL.md` disclaimer linked; the license and disclaimer files were not captured, so their terms are unverified beyond the card statement (**Reported**, plus unverified-file limit).[^ming-audio-tiny-card]

## Relationships

- Distinct from: [Ming-3.0-asr-tiny](ming-3.0-asr-tiny.md) — a separate inclusionAI ASR checkpoint with a Ling-tiny-v3 backbone, prompt-based hotwords and its own SGLang-Omni transcription route; only the marketing suffix is shared (**Synthesis**).[^ming-audio-tiny-card]
- Served by: [vLLM-Omni](vllm-omni.md), [SGLang-Omni](sglang-omni.md) and SGLang per the card's deployment section; see [Ming-3.0-audio-tiny Serving](ming-3.0-audio-tiny-serving.md) for GPU placement and voice selection (**Reported**).[^ming-audio-tiny-card]
- Compares with: [MOSS-Audio family](moss-audio.md) as another audio-understanding LLM that also does timestamped ASR, and [Qwen3-ASR family](qwen3-asr-family.md) as a recognizer built on an omni audio LLM — but neither comparison can be scored from this card because its benchmark attachments are missing (**Synthesis**).[^ming-audio-tiny-card]
- Cataloged in: [ASR/STT Model Survey](asr-stt-model-survey.md) as an audio-language recognizer whose accuracy is unreported, and noted in [TTS Model Survey](tts-model-survey.md) as an adjacent optional-speech-output model rather than a catalog row (**Synthesis**).[^ming-audio-tiny-card]

## Coverage ledger and limits

**Observed coverage:** the entire 242-line Markdown capture was read statically. Source identity is this file alone; no package scope, revision or capture date is supplied. No credentials, tokens or disclosure restrictions were found, and no example code was executed.[^ming-audio-tiny-card]

| Artifact | Coverage / consequence |
| --- | --- |
| `raw/inclusionAI-Ming-3.0-audio-tiny.md` | Fully inspected: frontmatter, summary table, highlights, architecture, Transformers quick start, ASR and understanding examples, Python usage, speech output, vLLM-Omni / SGLang / SGLang-Omni serving, evaluation headings, license. |
| `assets/benchmark-asr.png`, `assets/benchmark-audio-intelligence.png`, `assets/benchmark-text.png` | Absent at capture-relative paths. No WER/CER, per-language, dialect, reasoning or text-retention number, baseline set or protocol can be recovered; this is why status stays `draft`. |
| `assets/ming-3.0-audio-logo.png`, `assets/github-invertocat-black-17.svg` | Absent; excluded as decorative. |
| `examples/transformers_audio.py`, `examples/transformers_thinker_talker.py`, `examples/vllm_omni_audio_chat.py`, `examples/sglang_audio_chat.py`, `requirements-transformers.txt`, `scripts/serve_vllm_omni.sh`, `scripts/serve_sglang.sh`, deployment YAMLs | Absent locally; only README commands and the inline Python fence were inspected. Prompt construction, audio preprocessing, chunking, decoding and profile contents are unchecked. |
| `voice_presets/voice_audio/`, `voice_presets/voice_prompts.json`, `docs/voices.md` | Absent; preset voice assets, their transcripts and the full voice roster are not verified. |
| Weights, tokenizer, processor, custom `trust_remote_code` implementation, `LICENSE`, `LEGAL.md` | Mentioned or linked, not supplied or inspected; no download and no code audit. |
| GitHub repository, ModelScope page, HF Flash and Tiny pages, SGLang-Omni cookbook `ming3_audio.html`, voice guide, external benchmark notes | External targets not fetched; release timeline, full voice list, implementation and evaluation protocol remain unassessed. |

Only static reading was performed: no install, download, inference, audio listening, server launch or benchmark reproduction. All capability, size and compatibility statements are **Reported**; absence claims and file-presence checks are **Observed**; cross-model comparisons are **Synthesis**. No contradiction or supersession with another compiled source is established.[^ming-audio-tiny-card]

[^ming-audio-tiny-card]: [Ming-3.0-audio-tiny model card](../raw/inclusionAI-Ming-3.0-audio-tiny.md) — locators: frontmatter (`language`, `license`, `library_name`, `tags`, `model_name`); header link row (GitHub `inclusionAI/Ming-3.0-audio-flash`, ModelScope, HF Flash, HF Tiny, Examples, voice-guide and deployment-guide links); `Model Summary` table (developer, MoE type, 9.3B/2.7B parameters, inputs, outputs, languages, MIT); `Highlights` (six capability bullets); `Architecture` (encoder, projector, MoE backbone, optional Talker); `Quick Start with Transformers` and its `Audio Understanding` / `Speech Recognition` / `Direct Python Usage` subsections; `Speech Output` (`US_Stella`, reference-audio prompting); `Serving` → `vLLM-Omni`, `SGLang`, `SGLang-Omni`; `Evaluation` with its three image references and percentage/asterisk notes; `License` (`LEGAL.md`). Attachment inspection is unavailable as recorded in the ledger.

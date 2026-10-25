---
type: Concept
title: Granite Speech 5.0 2B Prompting and Serving
description: Task prompt strings, ~2-minute segmentation guidance, and the Transformers, vLLM, Hugging Face Inference Endpoint, llama.cpp GGUF, and mlx-audio routes documented for Granite Speech 5.0 2B, including the Q8_0 quantization recommendation.
tags: [stt, asr, serving, prompts, vllm, llama-cpp, mlx]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T02:38:02Z }
stale_after: 2027-10-25
sources:
  - id: granite-2b-card
    resource: ../raw/ibm-granite-granite-speech-5.0-2b.md
    kind: documentation
    title: granite-speech-5.0-2b model card
---

Granite Speech 5.0 2B exposes no task flags: transcription, punctuation, keyword biasing, language-ID prompting, and translation are all selected by the natural-language prompt sent with the audio, and the card documents five serving routes — Transformers, vLLM (offline and OpenAI-compatible server), a hosted Hugging Face Inference Endpoint, llama.cpp GGUF, and `mlx-audio` — each with its own decode parameters and token budget (**Reported**).[^granite-2b-card]

## Segmentation and input format

- The card's guidance is to transcribe audio in segments of up to about 2 minutes and to split longer recordings, for example with VAD, before decoding (**Reported**).[^granite-2b-card]
- Sample code asserts mono, 16 kHz input (`wav.shape[0] == 1 and sr == 16000`); the card does not document resampling behavior or a hard input-length limit, so the 2-minute figure is guidance rather than a validated ceiling (**Observed** for the assertion; **Synthesis** for the guidance-versus-limit distinction).[^granite-2b-card]
- The hosted-endpoint example repeats the same constraint as a comment: 16 kHz mono audio, up to about 2 minutes (**Reported**).[^granite-2b-card]
- Because every request carries the audio plus a prompt prefix and the decoder is autoregressive, a fixed `max_new_tokens` caps transcript length; the card's own examples use 64, 200, and 512 tokens without stating a mapping to audio duration (**Reported**; the consequence is **Synthesis**).[^granite-2b-card]

## Task prompts

Prompts are given in the card as natural-language instructions; several have documented multilingual variants (**Reported**).[^granite-2b-card]

| Task | Prompt | Notes |
| --- | --- | --- |
| ASR, raw transcripts | `can you transcribe the speech into a written format?` | Multilingual variants supported, e.g. `Pouvez-vous reconnaître le contenu de la parole ?` |
| ASR with punctuation | `transcribe the speech with proper punctuation and capitalization.` | Multilingual variants, e.g. `Transcrivez la parole avec une ponctuation et des majuscules appropriées.` |
| ASR with keyword biasing | `transcribe the speech to text. Keywords: <kw1>, <kw2>, ...` | Multilingual variants, e.g. Spanish with `Palabras clave:` |
| ASR with language ID | `The speech is in <language>. Transcribe it exactly; do not translate. can you transcribe the speech into a written format?` | `<language>` in English, French, German, Spanish, Portuguese, or Japanese; also works with the whole prompt in another language naming that language |
| AST, raw transcripts | `translate the speech to <language>.` | Target English, French, German, Spanish, Japanese, Italian, or Mandarin; multilingual variants supported |
| AST with punctuation | `translate the speech to <language> with proper punctuation and capitalization.` | English prompt only |
| AST with keyword biasing | `translate the speech to <language>. Keywords: <kw1>, <kw2>, ...` | Multilingual variants supported |

- The language-ID prompt is the documented way to constrain multilingual ASR; the card lists English, French, German, Spanish, Portuguese, and Japanese as valid `<language>` values, matching the ASR language list (**Reported**).[^granite-2b-card]
- Keyword biasing is prompt-side only: the card reports a keyword list raised to 2,000 entries but documents no scoring, weight, or insertion mechanism, so biasing strength is not tunable from the card (**Reported**; **Synthesis** for the missing knob).[^granite-2b-card]
- The card states that an unfamiliar or malformed prompt is ignored and the model falls back to plain transcription, so a wrong task or language string produces a plausible-looking but unintended output rather than an error (**Reported**; the failure-mode reading is **Synthesis**).[^granite-2b-card]

## Transformers

- Requires `transformers>=4.52.1` plus `torchaudio` and `soundfile`; load `AutoProcessor.from_pretrained` and `AutoModelForSpeechSeq2Seq.from_pretrained(..., torch_dtype=torch.bfloat16)` (**Reported**).[^granite-2b-card]
- Prompt construction uses the tokenizer chat template with `add_generation_prompt=True` and the audio placeholder `<|audio|>` prepended to the user text; inputs go through `processor(prompt, wav, device=device, return_tensors="pt")`, and passing `device` computes the feature front-end on the model's accelerator (**Reported**).[^granite-2b-card]
- Generation uses `max_new_tokens=200, do_sample=False, num_beams=1`; decoding must slice off the input tokens (`model_outputs[0, num_input_tokens:]`) because Transformers returns prompt plus generated ids, then `tokenizer.batch_decode(..., skip_special_tokens=True)` (**Reported**).[^granite-2b-card]

## vLLM

- Offline: `LLM(model=..., max_model_len=2048, limit_mm_per_prompt={"audio": 1})`, with the prompt built via `apply_chat_template(chat, tokenize=False)` and audio supplied as `multi_modal_data={"audio": audio_and_sample_rate}`; sampling is `temperature=0.0, max_tokens=64` in the card's example (**Reported**).[^granite-2b-card]
- The offline snippet builds its chat prompt without `add_generation_prompt=True`, unlike the Transformers snippet, and caps generation at 64 tokens, so it is a smoke test rather than a transcription recipe (**Synthesis**).[^granite-2b-card]
- Online: `vllm serve ibm-granite/granite-speech-5.0-2b --api-key <placeholder> --max-model-len 2048`, then the OpenAI-compatible `client.chat.completions.create` with a message containing a text part and an `audio_url` part whose URL is a base64 `data:audio/ogg;base64,...` URI; any format librosa supports is accepted (**Reported**).[^granite-2b-card]
- The `--max-model-len 2048` value is presented as possibly needed for lower-resource devices; the card does not relate it to audio duration (**Reported**; **Synthesis** for the missing mapping).[^granite-2b-card]

## Hosted Inference Endpoint

- A Hugging Face Inference Endpoint serving this model with vLLM exposes the same OpenAI-compatible request shape as the vLLM online route, authenticated with an `HF_TOKEN`, using a `data:audio/wav;base64,` audio part and `max_tokens=512` (**Reported**).[^granite-2b-card]
- The endpoint scales to zero when idle, so the first request may take a few minutes while it starts — unusable as a low-latency voice-pipeline backend without a keep-alive (**Reported**; the pipeline consequence is **Synthesis**).[^granite-2b-card]

## llama.cpp GGUF

- Install via `brew install llama.cpp` on macOS; offline transcription is `llama-cli -st -hf ibm-granite/granite-speech-5.0-2b-GGUF:Q8_0 --audio "audio.wav" -p "transcribe the speech with proper punctuation and capitalization."` (**Reported**).[^granite-2b-card]
- Server mode is `llama-server -hf ibm-granite/granite-speech-5.0-2b-GGUF:Q8_0 --port 9797`, queried through the OpenAI-compatible `POST /v1/audio/transcriptions` multipart endpoint with `model`, `file`, and `prompt` fields, reading `.text` from the JSON reply (**Reported**).[^granite-2b-card]
- `Q8_0` is the recommended quantization because IBM's tests found it matches the unquantized model; lower-bit quantizations lose accuracy on audio longer than about a minute (**Reported**).[^granite-2b-card]
- The card names no other runtime or GGUF producer for this model, so support in transcribe.cpp, audio.cpp, or CrispASR cannot be inferred from it (**Synthesis**).[^granite-2b-card]

## Apple Silicon (mlx-audio)

- Requires `mlx-audio` 0.5.9 or later plus `jinja2`, which `mlx-audio` needs for the chat template but does not install itself (**Reported**).[^granite-2b-card]
- Transcription runs as `python -m mlx_audio.stt.generate --model ibm-granite/granite-speech-5.0-2b --verbose --audio "audio.wav" --output-path "transcript"` (**Reported**).[^granite-2b-card]
- No Apple-silicon speed, memory, or quantization figure is given for this route (**Observed** by static inspection).[^granite-2b-card]

## Voice-pipeline implications

- The documented routes all assume a complete segment, not a live audio stream: there is no partial-hypothesis, chunk-commit, or endpointing API in the card, so a realtime voice loop would need external VAD segmentation and would treat this model as a turn-final recognizer (**Synthesis**).[^granite-2b-card]
- Prompt-side control means each turn re-sends the task/language/keyword prefix; keyword lists up to 2,000 entries would occupy prompt tokens on every request, and the card gives no cost or accuracy tradeoff for large lists (**Reported** for the list size; **Synthesis** for the cost reading).[^granite-2b-card]
- No RTFx, TTFT, or memory figure exists for any route, so latency budgeting must be measured locally before choosing between Transformers, vLLM, llama.cpp Q8_0, and the hosted endpoint (**Synthesis**).[^granite-2b-card]

## Relationships

- Model identity, architecture, training data, and the PER/Cap-F1 results live on [Granite Speech 5.0 2B](granite-speech-5.0-2b.md); this page holds only the prompting and serving contract (**Synthesis**).[^granite-2b-card]
- Runtime peers: [transcribe.cpp](transcribe-cpp.md) and [audio.cpp Framework](audio-cpp-framework.md) are ggml/GGUF STT runtimes documented elsewhere in this wiki, but this card only claims llama.cpp support for 5.0-2B, so neither can be assumed to load it (**Synthesis**).[^granite-2b-card]
- Serving comparison: [Speech-to-Speech OpenAI-Compatible STT/TTS Backends](speech-to-speech-openai-compatible-backends.md) documents the OpenAI-compatible STT contract that the vLLM online and hosted-endpoint routes here would satisfy, if a pipeline backend were pointed at this model (**Synthesis**).[^granite-2b-card]

## Coverage and limits

- Source inspected statically; no runtime was installed, no weight downloaded, and no request was executed against Transformers, vLLM, llama.cpp, mlx-audio, or the hosted endpoint, so every command and parameter is **Reported** only (**Synthesis**).[^granite-2b-card]
- The card's vLLM snippets print a literal example API-key value; it is treated here as a placeholder, not a credential, and is not reproduced (**Observed**; no sensitive value compiled).[^granite-2b-card]
- Not inspected: the GGUF repository card (a stub that defers to the base card, excluded as duplicative on [Granite Speech 5.0 2B](granite-speech-5.0-2b.md)), the linked notebooks, and the IBM Granite docs pages that the card points to for prompt engineering (**Synthesis**).[^granite-2b-card]

[^granite-2b-card]: [Granite-Speech-5.0-2B model card](../raw/ibm-granite-granite-speech-5.0-2b.md) — locators: Usage preamble (`transformers>=4.52.1`, segments up to ~2 minutes, split longer recordings with VAD); Usage with `transformers` (install fence, `<|audio|>` prompt, `apply_chat_template(..., add_generation_prompt=True)`, `processor(prompt, wav, device=device)`, `max_new_tokens=200`, input-token slicing, `batch_decode`); Usage with `vLLM` (offline `LLM(max_model_len=2048, limit_mm_per_prompt={"audio": 1})`, `SamplingParams(temperature=0.0, max_tokens=64)`; online `vllm serve` command and base64 `audio_url` chat-completions snippet); Usage with the hosted Inference Endpoint (HF_TOKEN, `max_tokens=512`, scale-to-zero note); Usage with `llama.cpp` (`llama-cli -st -hf ...:Q8_0 --audio`, `llama-server --port 9797`, curl `/v1/audio/transcriptions`, Q8_0 recommendation and lower-bit long-audio accuracy loss); Usage with `mlx-audio` (0.5.9+, jinja2 note, `mlx_audio.stt.generate` command); Preferred prompt by task table (7 rows with multilingual variants and the English-only AST punctuation caveat); Ethical Considerations and Limitations (malformed-prompt fallback to transcription).

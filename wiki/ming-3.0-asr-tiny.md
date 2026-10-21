---
type: Concept
title: Ming-3.0-asr-tiny
description: inclusionAI Chinese-English contextual ASR model with Ling-tiny-v3 backbone, prompt-based hotwords and dialogue context, CUDA Transformers inference and SGLang-Omni serving, but no streaming input in the bundled example.
tags: [stt, asr, contextual-asr, hotwords, chinese, serving]
status: draft
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T15:07:23Z }
stale_after: 2027-04-21
sources:
  - id: ming-asr-tiny-card
    resource: ../raw/Ming-3.0-asr-tiny.md
    kind: documentation
    title: Ming-3.0-asr-tiny model card capture
---

Ming-3.0-asr-tiny from inclusionAI combines a Ling-tiny-v3 language backbone with an audio encoder for single-turn Chinese and English transcription, with regional dialect coverage and hotword or preceding-dialogue conditioning through the prompt (**Reported**). Its bundled Transformers example does not accept streaming input; the separate [SGLang-Omni](sglang-omni.md) route reports streamed transcript output through SSE. These are different streaming boundaries, not evidence of native realtime audio-input streaming (**Synthesis**).[^ming-asr-tiny-card]

## Identity and capabilities

- Upstream checkpoint is `inclusionAI/Ming-3.0-asr-tiny`; code/cookbook repository is [inclusionAI/Ming-3.0-asr](https://github.com/inclusionAI/Ming-3.0-asr). Frontmatter names Transformers, ASR and languages `zh`/`en`; the citation names inclusionAI and year 2026. No immutable revision, exact release date or capture date is supplied (**Observed**).[^ming-asr-tiny-card]
- The card reports evaluation on 15 regional dialect test sets, including Cantonese, Minnan and Shanghainese, plus noisy speech and five application domains. It does not enumerate all dialects/domains in text (**Reported/Observed**).[^ming-asr-tiny-card]
- Output is transcription text without word-level timestamps or speaker diarization. Image/video inputs are unsupported. Hotwords are hints, not guaranteed output (**Reported**).[^ming-asr-tiny-card]
- Parameter count, encoder/adapter details, training data and recipe, input sample-rate requirements, context-window size, memory footprint and numerical accuracy/latency/throughput are not established by the captured text. Do not infer a parameter count or edge suitability from “tiny” (**Observed/Synthesis**).[^ming-asr-tiny-card]

## Transformers deployment

**Reported procedure, not executed:** use Python 3.12 on Linux with a compatible CUDA GPU, download the complete checkpoint, and install its requirements.[^ming-asr-tiny-card]

```bash
python -m pip install "huggingface_hub[cli]"
hf download inclusionAI/Ming-3.0-asr-tiny --local-dir Ming-3.0-asr-tiny
cd Ming-3.0-asr-tiny
python -m pip install -r requirements.txt
python examples/transcribe.py --model . --audio /path/to/speech.wav
```

- Add `--language-hint zh` or `--language-hint en` when known. The example uses CUDA, BF16, SDPA, greedy decoding and at most 256 new tokens; bundled code is loaded with `trust_remote_code=True` (**Reported**). Review that code before running it; it was not captured or audited here (**Synthesis**).[^ming-asr-tiny-card]
- The card names Transformers 5.12.1, fla-core 0.5.2 and PyTorch 2.11.0. For another CUDA version, it directs users to install matching PyTorch and torchaudio 2.11.0 wheels before installing requirements. Compatibility is unverified (**Reported**).[^ming-asr-tiny-card]
- The Python fence loads `AutoProcessor` and `AutoModelForCausalLM` from `"."`, uses `soundfile.read(..., dtype="float32", always_2d=True)`, transposes to `(waveform.T, rate)`, and passes this to `asr_request.prepare_asr_request(..., return_tensors="pt")` before moving inputs to the model device (**Observed** example).[^ming-asr-tiny-card]
- Generation runs in inference mode with `do_sample=False`, `max_new_tokens=256`, `no_repeat_ngram_size=10`, and EOS/padding IDs from `model.config.text_config.eos_token_id`; only tokens after the input length are sent to `decode_transcript` (**Observed** example).[^ming-asr-tiny-card]
- Long audio can be encoded using `--audio-chunk-frames`, subject to an unspecified model context limit. Chunked encoding alone does not establish live input streaming (**Reported/Synthesis**).[^ming-asr-tiny-card]

## Context ASR: topic, hotwords and dialogue

- Ordinary and contextual transcription share the same input format. Append topic and hotword text directly to the base instruction **without a newline**; preceding dialogue may also be included. Python calls pass the full text via `prepare_asr_request(..., prompt=...)` (**Reported**).[^ming-asr-tiny-card]
- The illustrated base instruction requests language identification followed by a tab and transcription. Its suffix pattern is `This is an audio about <topic>.This audio may contains the following words or phrases:<terms>.`; the wording is preserved as a source example, not an independently validated prompt requirement (**Observed**).[^ming-asr-tiny-card]
- For known-language clips up to 60 seconds, the card says `--context-chunks` selects 3000 mel frames for clips up to 30 seconds and 6000 beyond 30 seconds; combine it with `--language-hint zh` or `en`. These are context-processing settings, not measured latency or a general 60-second maximum for every inference path (**Reported/Synthesis**).[^ming-asr-tiny-card]

## SGLang-Omni serving

**Reported single-GPU launch and request, not executed:**[^ming-asr-tiny-card]

```bash
sgl-omni serve --model-path inclusionAI/Ming-3.0-asr-tiny
curl -X POST http://127.0.0.1:8000/v1/audio/transcriptions \
  -F model=inclusionAI/Ming-3.0-asr-tiny \
  -F file=@/path/to/speech.wav \
  -F response_format=json
```

- JSON includes a `text` field. `language` accepts `en` or `zh`; `prompt` appends one line of topic/hotword context; `stream=true` returns transcript text as server-sent events (**Reported**).[^ming-asr-tiny-card]
- The linked [Ming ASR cookbook](https://sgl-project.github.io/sglang-omni/cookbook/ming3_asr.html) is the pointer for response formats, streaming and long-audio handling. No SGLang-Omni version floor, SSE event schema, audio-input streaming protocol, concurrency or latency measurement is established here (**Observed** coverage limit).[^ming-asr-tiny-card]

## License

The card and frontmatter declare MIT for model weights and original project code. Bundled Apache-2.0 files retain their headers/license text, and `modeling_whisper_encoder.py` retains the MIT notice for code adapted from OpenAI Whisper (**Reported**). The actual license files and encoder code are absent locally, so their contents and compliance details were not verified.[^ming-asr-tiny-card]

## Relationships

- Uses: [SGLang-Omni](sglang-omni.md) as the card's single-GPU OpenAI-compatible transcription serving route; SSE output does not demonstrate live audio-input streaming (**Reported/Synthesis**).[^ming-asr-tiny-card]
- Cataloged in: [ASR/STT Model Survey](asr-stt-model-survey.md) as a Chinese-English contextual recognizer without a compiled numerical benchmark; no cross-model quality ranking is justified (**Synthesis**).[^ming-asr-tiny-card]

## Coverage ledger and limits

**Observed coverage:** the entire single Markdown capture was read statically. Source identity is this file alone, with no package scope or revision supplied; filenames below describe missing upstream dependencies, not additional local sources. No credentials or disclosure restrictions were identified; the example code was not executed.[^ming-asr-tiny-card]

| Artifact | Coverage / consequence |
| --- | --- |
| `raw/Ming-3.0-asr-tiny.md` | Fully inspected: frontmatter, introduction, capabilities, Quick Start/API/context/serving, evaluation headings, usage notes, license and citation. |
| `figures/model.jpg` | Absent at the capture-relative path; architecture image not inspected. Only the prose backbone-plus-encoder claim is compiled. |
| `figures/asr.png`, `figures/开源asr.png`, `figures/自建asr.png`, `figures/contextasr.png` | All absent at capture-relative paths; overview, Chinese/English, dialect/domain and Context ASR plots not inspected. No WER/CER, baseline comparison, context gain or benchmark protocol can be recovered from the text. |
| `figures/bailing-logo.png` | Absent; excluded as decorative. |
| `examples/transcribe.py`, `asr_request.py`, `requirements.txt` | Absent locally; README commands and inline Python inspected, but implementation, request validation and actual dependency pins not checked. |
| `LICENSE`, `LICENSE-APACHE-2.0`, `modeling_whisper_encoder.py`, `CITATION.cff` | Absent locally; only the card's license/citation statements inspected. |
| Weights, tokenizer, processor and other custom Transformers files | Mentioned, not supplied in this capture or inspected; no model download. |
| Chinese README, GitHub code/cookbook, SGLang-Omni site and Ming cookbook, PyTorch install page, Ming project link, release-film MP4 | External targets not fetched or inspected; alternate-language duplication, implementation and supplemental evaluation remain unassessed. Film URL contains `media-2026-10-19`, which is not treated as an attested release date. |

Only static reading was performed; no package install, server, model inference, audio listening or benchmark reproduction occurred. Capabilities and compatibility remain **Reported**, not verified. Status stays **draft** because the architecture and evaluation attachments are materially missing; no contradiction or supersession is established from the available text.[^ming-asr-tiny-card]

[^ming-asr-tiny-card]: [Ming-3.0-asr-tiny model card](../raw/Ming-3.0-asr-tiny.md) — locators: frontmatter (`library_name`, `license`, `pipeline_tag`, `language`, `tags`); title/link block and introduction (Ling-tiny-v3, encoder, single-turn, bundled artifacts); `Capabilities` (15 dialect sets, noisy speech, five domains); `Architecture` (`figures/model.jpg`); `Quick Start` → `Download and install`, `Run the PyTorch / Transformers example` (versions, CUDA/BF16/SDPA, trust boundary), `PyTorch / Transformers Python API` (request/decode helpers and generation keys), `Context ASR` (prompt concatenation and mel-frame settings), `SGLang-Omni serving` (launch, endpoint, fields, SSE, cookbook); `Evaluation` and its four image subsections plus release-film link; `Usage Notes` (timestamps, diarization, streaming input, chunking, hotword caveat); `License`; `Citation` (inclusionAI, year 2026, repository, CFF pointer). Attachment inspection is unavailable as recorded above.

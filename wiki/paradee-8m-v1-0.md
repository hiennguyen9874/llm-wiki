---
type: Concept
title: Paradee-8M v1.0
description: 8.07M-parameter English single-voice Kokoro distillation with INT8 ONNX deployment, misaki-compatible phoneme input, and reported CPU speed plus quality benchmarks.
tags: [tts, kokoro, distillation, onnx, cpu, edge-deployment, english]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T15:12:59Z }
stale_after: 2027-04-21
sources:
  - id: paradee-card
    resource: ../raw/Paradee-8M-v1.0.md
    kind: documentation
    title: Paradee-8M v1.0 model card capture
---

Paradee-8M v1.0 is an English TTS model distilled from [Kokoro-82M](kokoro-82m.md), retaining only its American-English `af_heart` voice. The card reports 8.07M parameters, a roughly 9 MB INT8 ONNX graph, 24 kHz audio, and about 18× realtime generation on one CPU thread. It is a different checkpoint, not a runtime for the full multilingual/multivoice teacher. Quality, speed, and leaderboard positions remain **Reported**, not independently verified; deployment recommendations below are **Synthesis**.[^paradee-card]

## Identity and licensing

- **Author and upstream:** Sahil Mahendrakar per the citation; model URL `https://huggingface.co/sahilmahendrakar/Paradee-8M-v1.0`, code/training/Python package at `https://github.com/sahilmahendrakar/paradee`. The citation gives 2026; the latest dated benchmark statement is October 9, 2026. No capture date, immutable commit, weight hash, or exact release date is supplied (**Reported**; limits).[^paradee-card]
- **License:** Apache-2.0 in frontmatter and License, described as the same as Kokoro-82M. License text and dependencies were not inspected; this is not a dependency-license audit (**Reported**).[^paradee-card]

## Architecture and distillation

The card describes Kokoro's code at smaller widths: a 4.23M text side and a 3.85M decoder (reported component counts; 8.07M overall per the card). The halves were trained separately against a frozen teacher on 12,000 WikiText-103 sentences synthesized by Kokoro, totaling 23.9 hours (**Reported**).[^paradee-card]

1. The text side predicts teacher phoneme durations, pitch, loudness, and phoneme features.
2. The decoder maps saved teacher values to teacher audio, using spectrogram losses followed by adversarial training.
3. The halves are joined without further training.
4. A parameter-free phase-locking filter corrects voiced-sound phase between 2 and 8 kHz to reduce a small-decoder buzz; it is included in the ONNX graph.

All training is reported to have run on one MacBook Pro. Training duration, optimizer/hyperparameters, ablations, and data-rights review are not provided in the capture (**Reported**; limits).[^paradee-card]

## Deployment and phoneme contract

The card recommends `onnx/paradee_int8.onnx` (9.0 MB); `onnx/paradee.onnx` is FP32 (37 MB), claimed to sound the same. PyTorch training weights are split into `pytorch/text_side.pt` and `pytorch/decoder.pt`. `config.json` contains Kokoro's phoneme vocabulary and sample rate; `tokenizer.json` presents the vocabulary in the format used by transformers.js and kokoro-js (**Reported**). The file-size discrepancy is retained below.[^paradee-card]

| ONNX tensor | Type and shape | Meaning |
| --- | --- | --- |
| `input_ids` | int64 `[1, T]` | Phoneme IDs from `config.json`, with a `0` pad token at each end; at most 512 IDs total |
| `speed` | float32 `[1]` | `1.0` is normal speed; accepted range not stated |
| `waveform` | float32 `[1, samples]` | Audio at 24 kHz |

The graph consumes phonemes, not raw text (**Reported**). The Python wrapper examples instead accept text:[^paradee-card]

```bash
pip install git+https://github.com/sahilmahendrakar/paradee
python -m paradee "Paradee is a small voice that runs anywhere." -o hello.wav
```

```python
from paradee import Paradee, SAMPLE_RATE
import soundfile as sf

tts = Paradee()
sf.write("hello.wav", tts("A small English voice."), SAMPLE_RATE)
```

These commands were read, not run; the Git install is unpinned and the card supplies no Python, ONNX Runtime, or dependency versions (**Observed** documentation; **Unverified** execution).[^paradee-card]

**Frontend compatibility matters:** phoneme spelling must match [Misaki](misaki.md), which produced the training inputs. The browser's kokoro-js uses [eSpeak NG](espeak-ng.md); the linked `web/misaki.js` converts that spelling to misaki's. The card reports Whisper mishearing about 31% of words without the conversion and about 2% with it, but gives no sample count, judge version, or matching evaluation protocol for this comparison (**Reported**). These are not the 200-sentence WER or leaderboard result below.[^paradee-card]

**Integration guidance (Synthesis):** shortlist it for a small, fixed-voice English CPU TTS stage; preserve the phoneme frontend and segment text to respect the 512-ID ceiling. Do not assume compatibility with Kokoro voicepacks, upstream servers, Vietnamese, or cloning. Neither the Python example nor the graph contract establishes incremental text input, chunked audio output, cancellation, or an HTTP API; a leaderboard streaming entry alone does not establish those interfaces.[^paradee-card]

## Reported evaluation

### Card's 200-held-out-sentence comparison

The card says all figures here use 200 held-out sentences, with speed measured on one Apple M4 Pro CPU thread. It explicitly identifies the table as **PyTorch results from the paper**, not released ONNX timings (**Reported**). Competitor figures below are attributed to the Paradee card, not independently to those projects.[^paradee-card]

| Model and voice | Parameters | File size | Realtime speed | UTMOS | WER |
| --- | ---: | ---: | ---: | ---: | ---: |
| Kokoro-82M (`af_heart`, teacher) | 81.8M | 325 MB | 7.6× | 4.52 | 5.7% |
| Paradee (`af_heart`) | 8.07M | 8.45 MB | 25.0× | 4.41 | 5.7% |
| Kokoro-7M-Distill (`af_msa`) | 7.48M | 30.1 MB | 35.5× | 4.18 | 7.4% |
| Piper (`en_US-lessac-medium`) | 15.7M | 63.2 MB | 15.4× | 4.36 | 8.8% |
| KittenTTS nano 0.8 (`Bella`) | 14.0M | 56.8 MB | 10.7× | 4.01 | 5.5% |

UTMOS is a learned naturalness predictor on a 1–5 scale, not a new human-listening MOS test; WER is judged by Whisper base. The released INT8 ONNX graph is separately reported at UTMOS 4.41 on the same sentences and about 18× realtime in ONNX Runtime on one thread. An ONNX-specific WER is not supplied (**Reported**; limit).[^paradee-card]

### October 9, 2026 leaderboard snapshot

The card attributes the following to Hugging Face's Open TTS Leaderboard, described as evaluating on Seed TTS Eval and CV3 Eval (**Reported**, not a live lookup):[^paradee-card]

- English WER 1.47%, ranked second behind Kokoro-82M at 1.46%.
- On the model-size versus WER Pareto front, with no comparable-size model claimed to have lower WER.
- CPU streaming, batch 1, single thread: RTFx 11.48 (about 11.5× realtime), ranked first; median time-to-first-audio 390 ms, ranked fourth.

Hardware, runtime revision, exact English-split aggregation, normalization, sample counts, and the streaming adapter are not supplied for this snapshot. Do not substitute 1.47% for the 200-sentence 5.7%, combine 11.48× with the M4 Pro PyTorch 25×, or rank these against another card's TTFA as if protocols matched (**Synthesis**).[^paradee-card]

## Limitations

- English only, American pronunciation, one voice; no multilingual synthesis or reference-voice cloning is offered (**Reported**).[^paradee-card]
- Numbers, abbreviations, and unusual-word pronunciation depend on misaki's handling (**Reported**).[^paradee-card]
- A faint buzz can remain on some voiced sounds even after filtering (**Reported**). No audio was listened to here.[^paradee-card]
- Weight-file size is not measured total RAM; sustained concurrent use, cold start, target-device speed, and end-to-end voice-turn latency are unverified (**Synthesis** limits).

## Contradictions

- **File size:** the opening says 9 MB and Files specifies 9.0 MB for `onnx/paradee_int8.onnx`; the Results table lists Paradee at 8.45 MB while describing that table as PyTorch. The card does not explain the artifact or unit difference. Neither exact value is chosen as a verified download size; FP32 is separately listed at 37 MB (**Reported**).[^paradee-card]

## Relationships

- **Depends on:** [Kokoro-82M](kokoro-82m.md) as distillation teacher, retaining `af_heart` rather than its full voice/language inventory (**Reported**).[^paradee-card]
- **Uses:** [Misaki](misaki.md)-compatible phoneme spelling; browser [eSpeak NG](espeak-ng.md) output requires the card's linked conversion (**Reported**).[^paradee-card]
- Compared in [TTS Model Survey](tts-model-survey.md) and [Kokoro Deployment Comparison](kokoro-deployment-comparison.md); the latter distinguishes distilled alternatives from deploying the teacher (**Synthesis** navigation).
- Distinct from [Kitten TTS 2](kitten-tts-2.md): the comparison table's `KittenTTS nano 0.8 (Bella)` row (14.0M, 56.8 MB) is the earlier nano generation, not the 1.7B ternary-packed Kitten TTS 2, which carries the `Bella` speaker name only and states no benchmark (**Synthesis**).[^paradee-card]

## Coverage and trust limits

- **Inspected statically:** the entire single-file capture `raw/Paradee-8M-v1.0.md`, including metadata, all prose/tables, usage cells, five sample pairs, image URLs, and BibTeX (**Observed**). Source identity is this resource; no composite package scope or immutable revision is available.
- **Absent at capture-relative paths:** both ONNX graphs; `config.json`; `tokenizer.json`; both PyTorch weights; `samples/sentences.txt`; and ten WAVs (`samples/1_paradee.wav` through `5_paradee.wav` and the five matching `*_kokoro.wav`). These are material unavailable attachments, not inspected evidence. Neither binary structure nor audio quality was checked.
- **External, uninspected:** paper `2610.06817`; the paradee repository/package/training code and `web/misaki.js`; upstream Kokoro/misaki implementation; WikiText-103 training material; Open TTS Leaderboard; Seed TTS Eval and CV3 Eval code/data. Implementation, training, benchmark protocols, licensing text, and reproduced metrics remain unestablished.
- **Figures uninspected:** four remote leaderboard screenshots under `bezzam/tts_leaderboard_screenshots/.../paradee/`: `top_models_wer_en.png`, `pareto_size_wer.png`, `top_models_rtfx_cpu.png`, `top_models_ttfa_cpu.png`. Surrounding prose supplies the transcribed headline claims, but other plotted values, axes, and visual ranking evidence were not checked.
- **Excluded:** repetitive sample-link markup and HTML presentation; retained sample inventory and benchmark claims. No downloads, installation, code/model execution, browser session, audio listening, or benchmark verification. Static input screening found no sensitive values or disclosure restriction requiring a pause.
- **Status:** stable as a complete model-card synthesis, not a verified implementation or benchmark. Six-month `stale_after` covers release/API and dated benchmark claims; no `verified` metadata is set.

[^paradee-card]: [Paradee-8M v1.0 model card capture](../raw/Paradee-8M-v1.0.md) — locators: frontmatter (`base_model`, `language`, `library_name`, `license`); opening description and Small/Fast/Close bullets; Paper/Code links; Samples table and `samples/sentences.txt`; Usage shell/Python cells; Files table and following ONNX Inputs/Output plus misaki/browser-conversion paragraphs; Results table and UTMOS/Whisper-base/PyTorch/INT8-ONNX qualifications; Hugging Face Open TTS Leaderboard (October 9, 2026 bullets and four image URLs); How it was made (four steps, training data, component counts, MacBook claim); Limitations; License; Citation (author/year/model URL).

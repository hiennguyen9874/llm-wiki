---
type: Concept
title: Kokoro-FastAPI Performance and Evaluation
description: Vendor-reported Kokoro-FastAPI first-token latency, realtime throughput, VRAM unload and reload, chunking defaults, and Whisper-roundtrip WER on the author's named hardware, with the conditions under which each figure holds.
tags: [tts, kokoro, fastapi, latency, benchmark, wer, vram]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:17:58Z }
stale_after: 2027-10-13
sources:
  - id: kokoro-fastapi-readme
    resource: ../raw/Kokoro-FastAPI.md
    kind: documentation
    title: Kokoro-FastAPI README capture
---

The Kokoro-FastAPI README reports four kinds of figures: streaming first-token latency on GPU and CPU, long-form throughput on one book, VRAM reclaimed by model unload, and Whisper-roundtrip WER for English and eight other languages. Each figure is tied to the author's hardware or test set, and none was reproduced in this wiki. Treat them as vendor claims for those setups, not as comparable benchmark values (**Reported**; **Unverified**).[^kokoro-fastapi-readme]

## Streaming first-token latency

| Setup (as labelled) | Chunk size | First token |
| --- | --- | --- |
| NVIDIA GPU | 400 | about 300 ms |
| CPU, older i7 | 200 | about 3,500 ms |
| CPU, Apple M3 Pro | 200 | under 1 s |

Source: lines 292–296 (**Reported**).[^kokoro-fastapi-readme]

- The README does not define what "first token" measures, does not name the chunk setting behind "chunksize", and does not name the GPU in the first row (**Observed** absence).
- The README warns that smaller chunks can add intonation artifacts (line 299).

## Throughput

- Setup as stated (lines 708–722): Windows 11 Home with WSL2; NVIDIA RTX 4060 Ti 16 GB at CUDA 12.1; Intel i7-11700 at 2.5 GHz; 64 GB RAM; WAV output; full text of H. G. Wells, *The Time Machine*; run through the local API.
- Stated figures: "Realtime Speed" 35x–100x, with the parenthetical "generation time to output audio length" (line 724); average processing rate 137.67 tokens/s, counted with `cl100k_base` (line 725).
- **Synthesis, reading the speed unit:** the parenthetical reads as generation time divided by audio length. That would make 35–100x slower than realtime, which contradicts the README's headline "hours of high quality speech in minutes" (line 16). The long-book row, 507 min 52 s of audio at "45.7x" synth speedup, implies about 11 minutes of wall time, which fits audio duration divided by wall time. The parenthetical looks inverted or loose.
- The README does not say whether the 137.67 tokens/s figure counts input text tokens or generated audio tokens.

## VRAM unload and reload

| Workload | Loaded | Floor | Reclaimed | Reload |
| --- | --- | --- | --- | --- |
| Short (6 s audio) | 3.11 GB | 2.37 GB | 758 MiB | +4.9 s |
| Long-form (7.5 min) | 3.98 GB | 2.37 GB | 1,656 MiB | +5.1 s |

Source: lines 727–743 (**Reported**); same setup as the throughput run.[^kokoro-fastapi-readme]

- The floor is host memory plus the CUDA context. Reclaim grows with workload but plateaus, because chunks cap at 450 tokens (**Reported**).
- Synthesis: unload never frees the 2.37 GB floor, so it reclaims only part of the process footprint.
- Controls: `POST /dev/unload` and `POST /dev/reload` need `ALLOW_DEV_UNLOAD=true`. `MODEL_AUTO_UNLOAD_TIMEOUT_SECONDS` (default `0`, disabled) unloads after idle time (lines 743, 792–794). See [Kokoro-FastAPI](kokoro-fastapi.md) for flags.

## Chunking and dialogue cost

- The model accepts up to 510 phonemized tokens per chunk. The README says running near that limit produces "rushed" speech and artifacts. The wrapper's chunker sizes chunks with `TARGET_MIN_TOKENS` 175, `TARGET_MAX_TOKENS` 250, and `ABSOLUTE_MAX_TOKENS` 450, and splits and stitches at sentence boundaries (lines 551–558; **Reported**).[^kokoro-fastapi-readme]
- Dialogue: voice count has minimal effect on speed. If each speaker gets fewer than about two sentences, chunking slows generation. The cost stays flat as text grows rather than compounding (line 488; **Reported**).[^kokoro-fastapi-readme]

## Transcription roundtrip (WER/CER)

Method: synthesize with Kokoro-FastAPI, transcribe with faster-whisper, and compare to the source text. Scripts sit under `examples/assorted_checks/test_transcription/`, not captured (lines 745–747; **Reported**).[^kokoro-fastapi-readme]

Long-form English: *A Journey to the Centre of the Earth* (Project Gutenberg), voice `af_heart`, `base.en` Whisper on CUDA float16, cu126 GPU build (lines 749–754):

| Run | Input chars | Audio | Synth speedup | Transcribe speedup | WER |
| --- | --- | --- | --- | --- | --- |
| Short (about ch. 7) | 64,996 | 66 min 06 s | 36.4x | 62.4x | 0.047 |
| Full book | 502,766 | 507 min 52 s | 45.7x | 65.1x | 0.033 |

Per-language check: one short sentence per voice, multilingual Whisper `small`, WER for Latin scripts and CER for ja/zh/hi (lines 758–770):

| Language | Voice | Metric | Score |
| --- | --- | --- | --- |
| English | `af_heart` | WER | 0.000 |
| English (UK) | `bf_emma` | WER | 0.111 |
| Spanish | `ef_dora` | WER | 0.000 |
| French | `ff_siwis` | WER | 0.000 |
| Italian | `if_sara` | WER | 0.000 |
| Portuguese | `pf_dora` | WER | 0.000 |
| Hindi | `hf_alpha` | CER | 0.059 |
| Japanese | `jf_alpha` | CER | 0.000 |
| Chinese | `zf_xiaobei` | CER | 0.143 |

- The README's caveat: single short sentences confirm that each voice yields transcribable audio. They are not a comprehensive per-language quality benchmark, and deeper evaluation is open work (line 772; **Reported**).[^kokoro-fastapi-readme]
- Interpretation (**Synthesis**): WER here measures how well a Whisper model recognizes the synthesized speech. It is an intelligibility proxy bounded by that ASR's own errors, and it says nothing about naturalness or speaker similarity. The full-book figure covers one voice, `af_heart`.
- The README does not say whether text normalization was on during these runs. The normalization issue (lines 808–835) can drop phrases, which WER would count as errors.
- Regression bands live in `examples/assorted_checks/test_transcription/BASELINE.md`, not captured (line 756).

## Reading the figures

- Among the concepts that describe Kokoro directly ([Kokoro-82M](kokoro-82m.md), [Kokoro Vietnamese](kokoro-vietnamese.md), [Speaches](speaches.md)), this README is the only source of timing or WER figures. The Kokoro-82M card reports no benchmarks. Anonymous latency anecdotes in [Community-Reported Local ASR/TTS Selection](community-asr-tts-selection.md) are not evidence (**Synthesis**).
- Metric conventions: [Speech deployment tools comparison](speech-deployment-tools-comparison.md) defines RTF as wall time over audio time, RTFx as audio time over wall time, and reports TTFA separately. Read the README's "realtime speed" under the same convention (**Synthesis**).
- WER is measured with [Faster-Whisper](faster-whisper.md) as the judge. The README names `base.en` and multilingual `small`, and the score depends on that model.

## Relationships

- Parent server: [Kokoro-FastAPI](kokoro-fastapi.md).
- Voice, dialogue, and caption features whose timing these figures touch: [Kokoro-FastAPI Voice and Markup Controls](kokoro-fastapi-voice-and-markup.md).
- Upstream model: [Kokoro-82M](kokoro-82m.md). Its card has no benchmark, so its "comparable quality" claim stays unverified there.

## Coverage and limits

- Inspected statically: README lines 292–299, 488, 551–558, 706–774 (**Observed**).[^kokoro-fastapi-readme]
- Not executed: no benchmark, WER run, transcription, GPU or CPU timing, or VRAM measurement was reproduced.
- Charts not captured: the first-token timelines, processing-time and realtime-factor plots, unload plots, and dialogue plots under `assets/`. Only the text figures are compiled.
- Not captured: `examples/assorted_checks/test_transcription/` (README, BASELINE.md), `examples/assorted_checks/benchmarks/benchmark_model_unload.py`, and `examples/assorted_checks/test_dialogue/`.
- The software versions behind the throughput and VRAM runs are not stated. The badge pins (`kokoro` 0.9.4, `misaki` 0.9.4, model commit `41e5892`; lines 9–11) may or may not apply to these runs.
- No wrapper revision is recorded, so these figures are dated by the capture only (`stale_after` 2027-10-13).

[^kokoro-fastapi-readme]: [Kokoro-FastAPI README capture](../raw/Kokoro-FastAPI.md) — locators: lines 9–11 test pins; lines 292–299 Key Streaming Metrics (first-token rows, line 299 artifact note); lines 708–722 Throughput setup list; lines 724–725 Key Performance Metrics (realtime speed and tokens/s); lines 727–743 Model Unload / VRAM Reclaim (table, floor note, env controls); lines 551–558 Natural Boundary Detection (token limits); line 488 dialogue voice-count note; lines 745–774 Transcription roundtrip (method, long-form and per-language tables, caveat, BASELINE link); lines 808–835 normalization known issue.

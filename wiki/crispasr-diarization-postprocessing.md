---
type: Concept
title: CrispASR Diarization and Post-Processing
description: "CrispASR's speaker diarization methods (energy, xcorr, foxnose, Sortformer, pyannote, sherpa, vad-turns) and its post-ASR steps: punctuation restoration, German truecasing, CTC forced alignment, and hotword biasing."
tags: [vad, diarization, stt, punctuation, truecasing, alignment, hotwords]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:57:00Z }
stale_after: 2027-10-13
sources:
  - id: crispasr-readme
    resource: ../raw/CrispASR.md
    kind: documentation
    title: CrispASR README
---

CrispASR runs speaker diarization as a post-processing step (`--diarize`), with six methods that differ in dependencies and in whether they estimate the speaker count. Backends that lack punctuation, casing, or word timing get them from separate models and aligners (`--punc-model`, `--truecase-model`, `-am`). The README's diarization accuracy figures are vendor-style claims with conflicting metric labels (**Reported**).[^crispasr-readme]

## Speaker diarization (`--diarize`)

| Method | Dependencies and behavior (README) |
| --- | --- |
| `energy` / `xcorr` | Stereo input only; no extra dependencies |
| `foxnose` | No external dependencies. WeSpeaker ResNet34-LM 256-d embeddings, GMM/BIC speaker counting, spectral clustering, and Viterbi smoothing. It estimates the speaker count. `--diarize-embedder auto` fetches a 24 MB CC-BY-4.0 GGUF. Called "best accuracy" |
| `sortformer` | NVIDIA's streaming Sortformer v3 (Nemotron-3-Diarization). One network, up to 8 speakers in order of appearance, overlap-aware, with no embedder or clustering. `--diarize-model auto` fetches a 107 MB q8_0 GGUF under OpenMDW-1.1 |
| `pyannote` | Native GGUF with no Python or sherpa-onnx. Add `--diarize-embedder auto` (TitaNet) or `--diarize-embedder indextts` (ECAPA-TDNN) for speaker IDs stable across long files |
| `sherpa` / `ecapa` | External sherpa-onnx subprocess, run once on the full audio so IDs stay consistent |
| `vad-turns` | Mono-friendly, gap-based proxy |

(**Reported**).[^crispasr-readme]

- The `sortformer` checkpoint is the family covered in [Nemotron 3 Diarization](nemotron-3-diarization.md) and its [GGUF packaging](nemotron-3-diarization-gguf.md). The README says CrispASR's output "matches transformers exactly on every p > 0.5 decision" (**Reported**; link **Synthesis**).[^crispasr-readme]
- The README's foxnose claim is 7.3% DER on VoxConverse dev, against 7.8% for pyannote with TitaNet. See [Contradictions](#contradictions) for its second figure (**Reported**).[^crispasr-readme]
- The ECAPA-TDNN embedder is selected by the name `indextts`, which the README does not explain (**Synthesis**).[^crispasr-readme]
- Server mode can return `response_format=diarized_json`, which uses normalised speaker letters A, B, C, and so on. Tuning knobs (cluster threshold, maximum speakers, embedder adapters) are in `docs/cli.md#diarization`, which was not captured (**Reported**).[^crispasr-readme]

## Punctuation restoration (`--punc-model`)

- CTC backends emit lowercase text without punctuation. The README's table marks fc-ctc, wav2vec2, firered-asr, omniasr (CTC), and paraformer as having no native punctuation (**Reported**).[^crispasr-readme]
- Shortcuts: `auto` or `firered` (FireRedPunc, Chinese and English), `fullstop` (XLM-R-large, 6 classes, EN/DE/FR/IT, MIT), `punctuate-all` (XLM-R-base, 12 languages, MIT), and `pcs` (XLM-R-base, 47 languages, with punctuation, truecasing, and sentence-boundary detection in one model, Apache-2.0). A GGUF path also works, and the Python, Rust, and Dart wrappers expose `crispasr.PuncModel` (**Reported**).[^crispasr-readme]
- The auto-enabled FireRedPunc is suppressed for gigaam's charwise `ctc` and `rnnt` revisions because, the README says, it injects full-width CJK punctuation into Russian. The `e2e_*` revisions carry punctuation in their vocabulary (**Reported**).[^crispasr-readme]
- For a standalone multilingual punctuation model that these shortcuts do not name, see [Punctuation Restoration (base, 307M)](punctuation-restoration-base.md) (**Synthesis**).

## Truecasing (`--truecase-model`)

Restores German noun and name capitalization on lowercase output. Three options, in ascending quality (**Reported**).[^crispasr-readme]

- `auto`: statistical, 1.7 MB (**Reported**).[^crispasr-readme]
- `crf`: CRF with context features, 8.5 MB (**Reported**).[^crispasr-readme]
- `lstm`: BiLSTM at character level, 3.2 MB, 97.9% F1, recommended (**Reported**).[^crispasr-readme]

All three auto-download from `cstr/truecaser-de`. The `pcs` punctuation model is the multilingual alternative.

## Word-level alignment (`-am`, `--align-only`)

- `-am FNAME` loads a CTC aligner GGUF for word-level timestamps on LLM backends. The README names `canary-ctc-aligner.gguf` and `qwen3-forced-aligner.gguf`, and says the CTC branches of the FastConformer hybrid fleet double as compact aligners of about 82 MB (**Reported**).[^crispasr-readme]
- `--align-only` runs forced alignment on its own: text (or a `.srt`) plus audio gives timestamped SRT or JSON. A `.srt` input keeps its cues and is re-timed, with `--align-granularity auto|word|segment` (**Reported**).[^crispasr-readme]
- Native word timing (✔ in the matrix) covers whisper, parakeet, canary, cohere, and kyutai-stt, plus granite-4.1 in its PLUS variant (`-owts`). Most other columns use `-am` (**Reported**).[^crispasr-readme]

## Hotwords (`--hotwords`)

`--hotwords "A,B,C"` boosts named terms during CTC or TDT decoding, or adds them to an LLM prompt. The README does not list which backends honour it beyond the flag description (**Reported**; coverage gap **Synthesis**).[^crispasr-readme]

## Contradictions

- Foxnose figure: the ASR backend table reads "3.18 % DER on VoxConverse dev vs the upstream reference implementation's 3.07 %". The diarization bullet gives the same pair "when scored on turns". The metric label therefore conflicts, and neither reading is chosen (**Reported**).[^crispasr-readme]

## Coverage and limits

- Benchmark figures (DER, WER, and the pyannote and TitaNet comparison) are README assertions with no named test protocol beyond the VoxConverse dev label. They were not reproduced (**Synthesis**).[^crispasr-readme]
- The feature matrix marks diarization ✔ for every ASR column, which reads as tool-level availability, not per-backend capability (**Synthesis**).[^crispasr-readme]
- The `docs/cli.md` diarization and alignment sections, and the `docs/architecture.md` tour, were not captured (**Synthesis**).
- No diarizer, punctuation model, or aligner was loaded or run (**Synthesis**).

## Relationships

- Uses: [Nemotron 3 Diarization](nemotron-3-diarization.md) for the Sortformer method (**Synthesis**).[^crispasr-readme]
- Follows: [CrispASR VAD and Language Identification](crispasr-vad-language-id.md), since diarization and punctuation act on VAD-segmented output (**Synthesis**).
- Part of: [CrispASR](crispasr.md) (**Synthesis**).

[^crispasr-readme]: [CrispASR README](../raw/CrispASR.md) — locators: `Feature matrix` section (the "Speaker diarization as a post-processing step via `--diarize`" bullet list with foxnose, sortformer, pyannote, sherpa/ecapa, vad-turns entries; the "Punctuation restoration" and "Truecasing" paragraphs; the "Which backends produce punctuation natively?" `<details>` table with the gigaam row); `ASR backends` table foxnose and sortformer rows (the 3.18%/3.07% DER pair); `CLI reference` table (`-am`, `--align-only`, `--hotwords`); `Server mode (HTTP API)` (diarized_json note in the diarization bullet); `Credits` (Nemotron, sherpa-onnx, pyannote).

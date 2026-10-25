---
type: Concept
title: Underdog Bark 3.0 Clean
description: Conway Research's 180 MB English Parakeet TDT 0.6B V3 finetune that drops fillers, false starts, and repeated words for dictation, reporting 4.08% WER against cleaned DisfluencySpeech transcripts and 5.83% on the seven Open ASR sets.
tags: [stt, asr, english, dictation, disfluency-removal, on-device, mlx, apple-silicon, parakeet]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T02:49:29Z }
stale_after: 2027-10-25
sources:
  - id: bark-clean-card
    resource: ../raw/ConwayResearch-Underdog-Bark-3.0-Clean.md
    kind: documentation
    title: Underdog Bark 3.0 Clean model card
  - id: bark-3.0-card
    resource: ../raw/ConwayResearch-Underdog-Bark-3.0.md
    kind: documentation
    title: Underdog Bark 3.0 (verbatim) model card
---

Underdog Bark 3.0 Clean is Conway Research's 0.6B English ASR checkpoint that transcribes *and* cleans up speech in one pass — dropping "um", "uh", filler phrases such as "you know" and "I mean", false starts, and repeated words — from a 180 MB download, reporting 4.08% WER against cleaned DisfluencySpeech references and 5.83% on the seven Open ASR Leaderboard English sets where its deliberate deletions count as errors (**Reported**).[^bark-clean-card] It is a finetune of [Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus), itself a derivative of `nvidia/parakeet-tdt-0.6b-v3`, and it is the dictation model shipped inside the Underdog Mac/iPhone app (**Reported**).[^bark-clean-card]

## Identity and lineage

- Model name Underdog Bark 3.0 Clean; the card frontmatter declares `base_model: nvidia/parakeet-tdt-0.6b-v3` with `base_model_relation: finetune`, `language: en`, `library_name: transformers`, `pipeline_tag: automatic-speech-recognition`, `license: cc-by-4.0`, and tags `dictation`, `disfluency-removal`, `low-bit`, `on-device`, `mlx`, `apple-silicon`, `parakeet`, `underdog` (**Observed** by static inspection).[^bark-clean-card]
- Lineage stated in the card: NVIDIA `parakeet-tdt-0.6b-v3` → `moondream/parakeet-ultra` → Bark 3.0 Plus → this Clean release; the tokenizer and output conventions (punctuation, casing, numerals) are the original's (**Reported**).[^bark-clean-card]
- Licence CC-BY-4.0, the same as the original, with a `NOTICE` file listing the attribution; English only (**Reported**).[^bark-clean-card]
- Family siblings named in the card but not compiled in this wiki: Bark 3.0 (verbatim, 163 MB), [Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus) (verbatim, 180 MB), Bark 3.0 Pro (1,254 MB), and [Bark 2.0](https://huggingface.co/ConwayResearch/bark-0.6B-4bit-v2.0) (472 MB) (**Reported**).[^bark-clean-card]
- Sizes: 180 MB to download, 1.25 GB in memory once unpacked (**Reported**); the two figures are download and runtime footprint, not interchangeable (**Synthesis**).[^bark-clean-card]

## Built-in disfluency removal

- The value proposition is one model instead of two: "no 'um', no false starts, no second model to clean up after it", so spoken thoughts become ready-to-use text without a separate cleanup stage (**Reported**).[^bark-clean-card]
- The card's intended use is dictation and readable transcripts rather than preserving every hesitation; it explicitly points verbatim work at Bark 3.0 (4.94) or Bark 3.0 Plus (4.76) instead (**Reported**).[^bark-clean-card]
- Consequence for measurement: on Open ASR sets whose references are verbatim, every filler or repeat that Clean removes on purpose is scored as an error on AMI, GigaSpeech, and Earnings-22 (**Reported**); a cleanup model's leaderboard WER is therefore not a transcription-quality ranking against verbatim models (**Synthesis**).[^bark-clean-card]

## Benchmarks

### Cleanup (DisfluencySpeech, 250 unscripted-conversation clips)

WER percent, lower is better; fillers count as errors (**Reported**).[^bark-clean-card] The two reference columns are the point of the table: a cleanup model should score low in the first column, a verbatim model in the second.

| Model | Download | Against cleaned transcripts | Against verbatim transcripts |
| --- | --: | --: | --: |
| **Bark 3.0 Clean** | **180 MB** | 4.08 | 13.85 |
| [Bark 2.0](https://huggingface.co/ConwayResearch/bark-0.6B-4bit-v2.0) | 472 MB | **3.83** | 13.01 |
| Bark 3.0 (verbatim) | 163 MB | 16.53 | **3.15** |

- Reading the table: the gap between columns is the cleanup effect, about 9.8 WER points for Clean and 13.4 for verbatim Bark 3.0 (**Synthesis** from the printed cells).[^bark-clean-card]
- Bark 2.0, a 472 MB older checkpoint, scores 0.25 points *better* than Clean on the cleanup column and 0.84 points better on the verbatim column in this 250-clip test, so this table does not establish Clean as the family's best cleanup model (**Observed** cells; interpretation is **Synthesis**).[^bark-clean-card]

### Ordinary speech (Open ASR Leaderboard, seven English sets)

WER percent on the full test sets, scored with the Open ASR Leaderboard's code; lower is better (**Reported**).[^bark-clean-card]

| Model | Download | LS clean | LS other | AMI | Earnings-22 | GigaSpeech | SPGISpeech | VoxPopuli | Average |
| --- | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| **Bark 3.0 Clean** | **180 MB** | **1.71** | **3.78** | **12.12** | **8.55** | **9.76** | **2.66** | **2.23** | **5.83** |
| [Bark 2.0](https://huggingface.co/ConwayResearch/bark-0.6B-4bit-v2.0) | 472 MB | 2.94 | 5.21 | 16.16 | 11.08 | 10.56 | 3.47 | 2.90 | 7.48 |

- Clean beats Bark 2.0 on all seven sets (5.83 against 7.48 average) from a download less than half the size (**Reported**).[^bark-clean-card]
- Clean matches Plus's 1.71% on LibriSpeech clean and reports 3.78% on LibriSpeech other; its 5.83% seven-set average is worse than Plus's 4.76% and verbatim Bark 3.0's 4.94% because cleanup output is penalized against verbatim references (**Reported**; the causal reading is **Synthesis**).[^bark-clean-card]

### The Plus foundation and selected baselines (verbatim recognition)

The card reproduces the family's verbatim table to show the accuracy and size behind Clean; the Bark rows use the leaderboard's scoring code and were reported separately rather than submitted as leaderboard entries, while dagger rows are published leaderboard results as of 9 October 2026 (**Reported**).[^bark-clean-card]

| Model | Download | LS clean | LS other | AMI | Earnings-22 | GigaSpeech | SPGISpeech | VoxPopuli | Average |
| --- | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| Bark 3.0 Pro | 1,254 MB | 1.38 | 3.11 | 7.16 | 5.65 | 7.46 | 3.54 | 1.70 | 4.29 |
| **Bark 3.0 Plus** | **180 MB** | 1.71 | 3.82 | 7.76 | 6.70 | 7.77 | 3.64 | 1.92 | **4.76** |
| Bark 3.0 | 163 MB | 1.89 | 4.08 | 7.82 | 7.05 | 7.95 | 3.72 | 2.05 | 4.94 |
| Phonon-2† | 164 MB | 1.73 | 3.92 | 9.32 | 6.96 | 8.35 | 3.70 | 2.46 | 5.21 |
| Parakeet TDT 0.6B v3† | 2,508 MB | 1.52 | 3.13 | 9.42 | 5.85 | 7.99 | 3.63 | 3.05 | 4.94 |
| Qwen3-ASR-0.6B† | 1,876 MB | 1.70 | 4.01 | 9.33 | 7.83 | 7.62 | 2.74 | 2.90 | 5.16 |
| Whisper large-v3† | 9,261 MB | 1.56 | 3.52 | 13.63 | 7.99 | 8.35 | 2.71 | 4.53 | 6.04 |
| Whisper large-v3-turbo† | 1,618 MB | 2.13 | 3.71 | 13.88 | 8.09 | 8.47 | 2.79 | 7.02 | 6.58 |

- Download sizes are weight-file sizes, not runtime memory, and these figures reproduce the Plus model card's comparison rather than a new evaluation of Clean (**Reported**).[^bark-clean-card]
- Within this card's own table the 180 MB Plus row (4.76) sits between Pro (4.29) and the 163 MB verbatim model (4.94), and ahead of a 2,508 MB Parakeet teacher and a 9,261 MB Whisper large-v3 (**Observed** cells; ranking is **Synthesis**).[^bark-clean-card]
- Cross-card caution: this 7-set, vendor-scored table is not the 8-set protocol used by several rows in the [ASR/STT Model Survey](asr-stt-model-survey.md), so sub-0.5-point gaps against those pages should not drive a decision (**Synthesis**).[^bark-clean-card]

## In Underdog (native runtime)

- Underdog runs the file as-is with no Python: a native Swift runtime reads `model.bark`, unpacks it in memory in about 2 seconds on Apple silicon, and runs the model on MLX; the unpacked weights are bit-identical to what `bark_loader.py` produces (**Reported**).[^bark-clean-card]
- The app downloads two files, `model.bark` and `mlx/config.json`, and checks each against a pinned size and SHA-256 before use; audio stays on the device (**Reported**).[^bark-clean-card]
- Throughput: on an M5 Max a 136-second recording transcribes in about 4 seconds including model load (**Reported**); that is roughly 34× realtime for a whole-recording, batch-style call, not per-chunk streaming latency (**Synthesis**).[^bark-clean-card]

## Running it yourself

- Transformers route: `pip install "transformers>=5.19" torch constriction numpy soundfile soxr`, then `python bark_loader.py model.bark recording.wav` (**Reported**).[^bark-clean-card]
- Python API: `load_model("model.bark", device="cuda" | "cpu" | "mps")` then `transcribe(model, wave.mean(1), sr)` on float32 audio read with `soundfile` (**Reported**).[^bark-clean-card]
- Apple silicon MLX route: `pip install mlx mlx-audio constriction numpy soundfile soxr`, then `python bark_mlx.py recording.wav`; the first run unpacks the weights into an MLX folder and caches it (**Reported**).[^bark-clean-card]
- Measurement protocol note: Clean was measured with no silence added before the audio, which is what `transcribe` does, and the card claims unpacking is exact so the weights loaded are the weights measured (**Reported**).[^bark-clean-card]
- The sibling verbatim card states the reverse for the same helper — that `transcribe` adds 0.25 s of silence before the audio and that its benchmark numbers use that setting — so the padding convention of the two captures is unresolved; see the contradiction recorded on [Underdog Bark 3.0](underdog-bark-3.0.md#contradictions) (**Reported**; tension is **Synthesis**).[^bark-3.0-card]

## Files in the release

| File | What it is |
|---|---|
| `model.bark` | Entropy-coded weights, format `bark-levels-v3` |
| `mlx/config.json` | Model configuration and vocabulary |
| `mlx/tokenizer.*`, `mlx/vocab.txt` | Tokenizer files for mlx-audio |
| `bark_loader.py` | Unpacks `model.bark` into a transformers `ParakeetForTDT` |
| `bark_mlx.py` | Unpacks `model.bark` into an mlx-audio Parakeet folder |

## Relationships

- Finetune of [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) through `moondream/parakeet-ultra` and Bark 3.0 Plus; it keeps the teacher's tokenizer and punctuation/casing/numeral conventions but narrows coverage from 25 European languages to English only (**Reported**).[^bark-clean-card]
- Cleanup counterpart of the English V3 derivatives already in the wiki: [Parakeet Ultra](parakeet-ultra.md) (full-precision accuracy push, 5.80 seven-set), [Parakeet Redux](parakeet-redux.md) (ternary 178 MB CPU/edge), and [Phonon-2](phonon-2.md) (164 MB ~2.1-bit encoder, 5.21 in its own vendor table). Only Clean changes *what is transcribed* rather than how cheaply or accurately verbatim speech is decoded, so its numbers are not a like-for-like ranking against them (**Synthesis**).[^bark-clean-card]
- Same-card baselines with wiki concepts: [Phonon-2](phonon-2.md) (164 MB, 5.21 verbatim) and the Parakeet teacher; the card also lists Qwen3-ASR-0.6B at 5.16, matching the [Qwen3-ASR family](qwen3-asr-family.md) page's scope rather than adding a new one (**Reported**).[^bark-clean-card]
- Contrast with offline giants in the same table: [Whisper Large v3](whisper-large-v3.md) (9,261 MB, 6.04) and [Whisper Large v3 Turbo](whisper-large-v3-turbo.md) (1,618 MB, 6.58) trail the 180 MB Plus row in this vendor table, a 51× and 9× size difference respectively (**Observed** cells; ratios are **Synthesis**).[^bark-clean-card]
- Pipeline fit: for dictation-style voice input, built-in cleanup removes a post-processing stage and its added latency, but it also means the transcript the dialogue LLM receives has already lost hesitations and repeats, which changes both the WER you should measure against and any downstream disfluency feature (**Synthesis**).[^bark-clean-card]
- Family navigation: the verbatim members are compiled as [Underdog Bark 3.0](underdog-bark-3.0.md) (base, 163 MB, 4.94) and its `Plus`/`Pro` siblings are documented there, while the platform execution matrix is on [Underdog Bark 3.0 Platform Runtimes](underdog-bark-3.0-runtimes.md); Clean is the only member that changes the transcript's content rather than its size or runtime (**Synthesis**).
- Name collision, not a relationship: the `bark` engine listed in [CrispASR TTS Engines](crispasr-tts-engines.md) is Suno's Bark text-to-speech model, a different system that shares the name with this ASR family (**Synthesis**).

## Contradictions

- The card highlights "more accurate than Bark 2.0 on all seven Open ASR Leaderboard English sets (5.83 % against 7.48 %)" while its own cleanup table shows Bark 2.0 at 3.83 against Clean's 4.08 on cleaned DisfluencySpeech transcripts, i.e. the older, larger model scores better on the metric the model is built for. Both are the same source's printed cells, the sets and protocols differ (Open ASR vs 250-clip DisfluencySpeech), and neither reading is chosen here (**Reported**; tension is **Synthesis**).[^bark-clean-card]

## Coverage and limits

- One capture, `raw/ConwayResearch-Underdog-Bark-3.0-Clean.md`, read in full and inspected statically only; no weights downloaded, no audio transcribed, no install, and no WER or throughput figure reproduced (**Synthesis**).[^bark-clean-card]
- The referenced figure `bark_frontier.png` (accuracy vs download size) is not present in `raw/` and was not inspected; its caption states it plots Plus, Pro, and the standard model, not Clean's cleanup scores, so no material claim depends on it (**Synthesis**).[^bark-clean-card]
- Excluded as not captured or not compiled: `bark_loader.py`, `bark_mlx.py`, `mlx/config.json`, the tokenizer files and `model.bark` weights themselves; the [DisfluencySpeech paper](https://arxiv.org/abs/2406.08820) and its 250-clip test set; the Open ASR Leaderboard space and scoring code; the Plus, Pro, and Bark 2.0 cards; and `underdog.ai` (**Synthesis**).[^bark-clean-card]
- The sibling verbatim capture `raw/ConwayResearch-Underdog-Bark-3.0.md` is now compiled as [Underdog Bark 3.0](underdog-bark-3.0.md), and its own table reproduces every Plus/Pro/base cell quoted here, so the previously second-hand figures are corroborated by the verbatim card; its evaluated comparisons and the iOS/Windows/Core ML routes are compiled on [Underdog Bark 3.0 Platform Runtimes](underdog-bark-3.0-runtimes.md) rather than duplicated here (**Observed** cells; reconciliation is **Synthesis**).[^bark-3.0-card]
- No card statement covers streaming or partial hypotheses, per-word timestamps, diarization, language coverage beyond English, or behaviour on non-dictation audio such as meetings with crosstalk; the M5 Max figure is whole-recording throughput (**Synthesis**).[^bark-clean-card]
- Every accuracy, size, and speed claim is the vendor's own report; release and benchmark figures carry `stale_after: 2027-10-25` per the `stt` domain rule (**Synthesis**).[^bark-clean-card]

[^bark-clean-card]: [Underdog Bark 3.0 Clean model card](../raw/ConwayResearch-Underdog-Bark-3.0-Clean.md) — locators: frontmatter (`base_model: nvidia/parakeet-tdt-0.6b-v3`, `base_model_relation: finetune`, `language: en`, `library_name: transformers`, `license: cc-by-4.0`, tags `dictation`/`disfluency-removal`/`low-bit`/`on-device`/`mlx`/`apple-silicon`/`parakeet`/`underdog`); `# Underdog Bark 3.0 Clean` intro (clean version of Bark 3.0 Plus, 180 MB, built-in removal of "um"/"uh"/"you know"/"I mean"/false starts/repeats, Plus's 4.76 seven-set average versus Parakeet TDT 0.6B v3 4.94, Qwen3-ASR-0.6B 5.16 and Whisper large-v3 6.04, Plus AMI 7.76 and VoxPopuli 1.92, Clean 4.08 against cleaned DisfluencySpeech and 1.71 LibriSpeech clean / 3.78 other, Underdog app on Mac and iPhone); `## Highlights` (no second cleanup model, 5.83 versus Bark 2.0 7.48 on seven sets, 1.71 parity with Plus on LS clean, 180 MB download / 1.25 GB memory); `### Cleanup` table (Clean 180 MB 4.08 / 13.85, Bark 2.0 472 MB 3.83 / 13.01, Bark 3.0 verbatim 163 MB 16.53 / 3.15; 250 clips, fillers count as errors); `### Ordinary speech` table (Clean 1.71 / 3.78 / 12.12 / 8.55 / 9.76 / 2.66 / 2.23 / 5.83 versus Bark 2.0 2.94 / 5.21 / 16.16 / 11.08 / 10.56 / 3.47 / 2.90 / 7.48; verbatim references penalize deliberate deletions on AMI, GigaSpeech, Earnings-22); `### The Plus foundation` table (Pro 1,254 MB 4.29; Plus 180 MB 4.76; Bark 3.0 163 MB 4.94; Phonon-2† 164 MB 5.21; Parakeet TDT 0.6B v3† 2,508 MB 4.94; Qwen3-ASR-0.6B† 1,876 MB 5.16; Whisper large-v3† 9,261 MB 6.04; Whisper large-v3-turbo† 1,618 MB 6.58; † published leaderboard as of 9 October 2026, Bark rows separately reported; weight-file sizes, not runtime memory); `## In Underdog` (native Swift runtime, ~2 s in-memory unpack on Apple silicon, MLX, bit-identical to `bark_loader.py`, pinned size and SHA-256 on `model.bark` and `mlx/config.json`, audio never leaves the device, M5 Max 136 s in ~4 s including load); `## Run it yourself` (pip `transformers>=5.19` fence, `bark_loader.py` CLI, `load_model`/`transcribe` API with `cuda`/`cpu`/`mps`, `mlx mlx-audio` fence with `bark_mlx.py`, first-run unpack and cache, no silence added before audio); `## Files` table (`model.bark` `bark-levels-v3`, `mlx/config.json`, `mlx/tokenizer.*`/`mlx/vocab.txt`, `bark_loader.py`, `bark_mlx.py`); `## Notes` (parakeet-tdt-0.6b-v3 via moondream/parakeet-ultra and Bark 3.0 Plus, original tokenizer and punctuation/casing/numeral conventions, CC-BY-4.0 plus `NOTICE`, English only).

[^bark-3.0-card]: [Underdog Bark 3.0 model card](../raw/ConwayResearch-Underdog-Bark-3.0.md) — locators: `## Benchmarks` table (identical Bark 3.0 Pro 1,254 MB / 4.29, Plus 180 MB / 4.76 and Bark 3.0 163 MB / 4.94 rows over the same seven English sets, with the three-decimal Pro 4.286 average); `### Disfluent speech` (Bark 3.0 3.15 against verbatim DisfluencySpeech transcripts, matching the Clean card's verbatim column); `## Run it` ("`transcribe` adds 0.25 s of silence before the audio, the setting the numbers above use"); `## Additional platform runtimes` (Core ML GPU/ANE macOS packages, iOS embedding contract, Windows CUDA/CPU runtime).

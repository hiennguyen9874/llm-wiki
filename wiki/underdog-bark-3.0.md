---
type: Concept
title: Underdog Bark 3.0
description: Conway Research's 163 MB English Parakeet TDT 0.6B V3 finetune that averages 4.94% WER over the seven Open ASR Leaderboard English sets and anchors a 163 MB–1,254 MB family with Plus at 4.76% and Pro at 4.29%.
tags: [stt, asr, english, on-device, mlx, apple-silicon, parakeet, low-bit, benchmarks]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T02:49:29Z }
stale_after: 2027-10-25
sources:
  - id: bark-3.0-card
    resource: ../raw/ConwayResearch-Underdog-Bark-3.0.md
    kind: documentation
    title: Underdog Bark 3.0 (verbatim) model card
---

Underdog Bark 3.0 is Conway Research's 0.6B English ASR checkpoint — a finetune of `nvidia/parakeet-tdt-0.6b-v3` through `moondream/parakeet-ultra` and Bark 3.0 Plus — that ships as a 163 MB `model.bark` file and reports a 4.94% mean WER over the seven Open ASR Leaderboard English sets, matching the 2,508 MB Parakeet teacher it derives from at two decimals while differing in the third (4.937 against 4.941) (**Reported**).[^bark-3.0-card] It is the verbatim member of a three-size family: [Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus) at 180 MB / 4.76% and Bark 3.0 Pro at 1,254 MB / 4.29% trade download size for accuracy along the same lineage, while the dictation variant [Underdog Bark 3.0 Clean](underdog-bark-3.0-clean.md) reuses the Plus weights to delete fillers instead of transcribing them (**Reported**).[^bark-3.0-card]

## Identity, lineage, and family

- Frontmatter declares `base_model: nvidia/parakeet-tdt-0.6b-v3` with `base_model_relation: finetune`, `language: en`, `library_name: transformers`, `pipeline_tag: automatic-speech-recognition`, `license: cc-by-4.0`, and tags `underdog`/`speech-to-text`/`asr`/`stt`/`low-bit`/`on-device`/`mlx`/`apple-silicon`/`parakeet` (**Observed** by static inspection).[^bark-3.0-card]
- Lineage stated in the card: NVIDIA `parakeet-tdt-0.6b-v3` → `moondream/parakeet-ultra` → the Bark 3.0 family; the tokenizer and output conventions (punctuation, casing, numerals) are the original's, and `NOTICE` carries the attribution (**Reported**).[^bark-3.0-card]
- Family members with download sizes as printed in the benchmark table: Bark 3.0 (163 MB), Bark 3.0 Plus (180 MB), Bark 3.0 Pro (1,254 MB); the card calls Pro "full precision" and Plus and the base model "the larger members of the family" relative to nothing smaller, and prints no bit-width for either compressed member — only the frontmatter's `low-bit` tag and the sibling Bark 2.0 repository name (`bark-0.6B-4bit-v2.0`) indicate a low-bit encode (**Reported**; the missing bit-width is a limit).[^bark-3.0-card]
- English only, CC-BY-4.0 like the original (**Reported**).[^bark-3.0-card]
- Download size is the weight-file size, not runtime memory: on the sibling Clean release the same 180 MB download unpacks to 1.25 GB in memory, and the Windows loader likewise expands the packed weights to FP32 before inference (**Reported**; the transfer to the 163 MB member is **Synthesis**).[^bark-3.0-card]

## Benchmarks: seven English Open ASR sets

WER percent, lower is better, on the full test sets of the Open ASR Leaderboard's seven English sets, including its cleaned versions of AMI, Earnings-22, GigaSpeech and VoxPopuli (**Reported**).[^bark-3.0-card] † marks the leaderboard's own published row as of 9 October 2026; the Bark rows use the leaderboard's scoring code but are not leaderboard entries. Bold marks the best cell in each column as the card sets it.

| Model | Download | LS clean | LS other | AMI | Earnings-22 | GigaSpeech | SPGISpeech | VoxPopuli | Average |
| --- | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| Bark 3.0 Pro | 1,254 MB | 1.38 | 3.11 | 7.16 | **5.65** | 7.46 | 3.54 | **1.70** | **4.29** |
| Bark 3.0 Plus | 180 MB | 1.71 | 3.82 | 7.76 | 6.70 | 7.77 | 3.64 | 1.92 | 4.76 |
| **Bark 3.0** | **163 MB** | 1.89 | 4.08 | 7.82 | 7.05 | 7.95 | 3.72 | 2.05 | 4.94 |
| Phonon-2† | 164 MB | 1.73 | 3.92 | 9.32 | 6.96 | 8.35 | 3.70 | 2.46 | 5.21 |
| Hojo-ASR-V1† | 11,957 MB | 1.30 | 3.24 | 7.54 | 6.97 | **6.14** | 1.74 | 3.11 | 4.29 |
| Qwen3-ASR-1.7B† | 4,699 MB | 1.26 | 2.94 | 8.31 | 5.84 | 7.22 | 2.57 | 2.85 | 4.43 |
| higgs-audio-v3-stt† | 5,351 MB | 1.08 | 2.61 | 7.19 | 7.04 | 7.45 | 2.07 | 3.73 | 4.45 |
| Canary-Qwen 2.5B† | 5,119 MB | 1.23 | 2.63 | 7.91 | 6.41 | 7.80 | **1.70** | 4.14 | 4.55 |
| Granite Speech 4.1 2B† | 4,832 MB | 1.03 | 2.19 | 7.06 | 6.69 | 8.18 | 3.47 | 4.18 | 4.69 |
| Cohere Transcribe† | 4,132 MB | **0.97** | **2.05** | **7.02** | 7.88 | 7.88 | 2.74 | 5.38 | 4.85 |
| Granite Speech 5.0 470M (NC)† | 946 MB | 1.45 | 2.67 | 7.31 | 8.23 | 8.37 | 1.75 | 4.67 | 4.92 |
| Parakeet TDT 0.6B v3† | 2,508 MB | 1.52 | 3.13 | 9.42 | 5.85 | 7.99 | 3.63 | 3.05 | 4.94 |
| Granite Speech 5.0 470M† | 946 MB | 1.48 | 2.71 | 7.71 | 6.75 | 8.74 | 3.22 | 4.90 | 5.07 |
| Qwen3-ASR-0.6B† | 1,876 MB | 1.70 | 4.01 | 9.33 | 7.83 | 7.62 | 2.74 | 2.90 | 5.16 |
| Whisper large-v3† | 9,261 MB | 1.56 | 3.52 | 13.63 | 7.99 | 8.35 | 2.71 | 4.53 | 6.04 |
| Whisper large-v3-turbo† | 1,618 MB | 2.13 | 3.71 | 13.88 | 8.09 | 8.47 | 2.79 | 7.02 | 6.58 |

### Reading the table

- The three-decimal claims reproduce from the printed cells: Bark 3.0 averages 4.937 and the Parakeet teacher 4.941, Pro 4.286 and Hojo-ASR-V1 4.291 (**Observed** arithmetic over the seven cells; each pair differs by about 0.004–0.005 points).[^bark-3.0-card]
- Both "edges out" framings therefore rest on a sub-0.01-point mean difference produced by opposite per-set trades, not on consistently lower error: against the teacher, Bark 3.0 wins AMI (7.82 vs 9.42), GigaSpeech (7.95 vs 7.99) and VoxPopuli (2.05 vs 3.05) while losing LibriSpeech clean, LibriSpeech other, Earnings-22 and SPGISpeech (**Observed** cells; the reading is **Synthesis**).[^bark-3.0-card]
- Size ratios from the same column: 163 MB is about 15× smaller than the 2,508 MB teacher, about 57× smaller than Whisper large-v3 (9,261 MB) and about 25× smaller than Cohere Transcribe (4,132 MB) (**Synthesis** from printed sizes).[^bark-3.0-card]
- The card's "no open model under 900 MB is more accurate except its larger sibling" holds inside this table — the nearest sub-900 MB competitor is Phonon-2 at 164 MB / 5.21, and the 946 MB Granite Speech 5.0 470M rows sit just above the threshold at 4.92 and 5.07 — but it is a vendor's curated comparison, not a sweep of every sub-900 MB checkpoint (**Reported**; scoping is **Synthesis**).[^bark-3.0-card]
- Per-column frontier: the 163 MB model leads no column outright, Pro leads Earnings-22 and VoxPopuli, and much larger models own the LibriSpeech, AMI and SPGISpeech best cells — so the family's pitch is average WER per download byte rather than best-in-class on any single set (**Observed** cells; interpretation is **Synthesis**).[^bark-3.0-card]
- Two rows carry the same model name with different figures (Granite Speech 5.0 470M at 4.92 non-commercial and 5.07 licensed); the card does not explain whether these are different checkpoints, decoding settings, or licence terms on the same weights, so the 0.15-point gap is unexplained (**Reported**; ambiguity recorded as a limit).[^bark-3.0-card]

## Disfluent speech (verbatim scoring)

WER percent on the DisfluencySpeech test set — 250 clips of unscripted conversation full of "um", "uh", restarts and repeats — scored against its **verbatim** transcripts with fillers counted as errors (**Reported**).[^bark-3.0-card]

| Model | Word error rate (%) |
| --- | --: |
| Bark 3.0 Pro | **2.95** |
| Bark 3.0 | 3.15 |
| Bark 3.0 Plus | 3.21 |
| Phonon-2 | 3.39 |

- All three Bark sizes beat Phonon-2 on filler-laden speech, with Pro the most robust (2.95 against 3.39), and the family spread on this set is only 0.26 points (**Reported**; spread is **Synthesis**).[^bark-3.0-card]
- This is the mirror image of the sibling Clean release's cleanup table: there, the verbatim model scores 3.15 against verbatim references and 16.53 against cleaned references, because it writes the fillers out (**Reported**; cross-card reading is **Synthesis**).[^bark-3.0-card]
- Consequence for voice agents: Bark 3.0 writes what was said, so a pipeline that wants clean copy must delete fillers downstream or use [Underdog Bark 3.0 Clean](underdog-bark-3.0-clean.md) (**Reported** for the behaviour; the routing advice is **Synthesis**).[^bark-3.0-card]

## Throughput and memory behaviour

- On an Apple M2 laptop the card reports a minute of audio in about 1.5 seconds, stated as 41× realtime, using stock mlx-audio (**Reported**).[^bark-3.0-card]
- Stock mlx-audio transcribes a file in one pass, so memory grows with length: on a 16 GB M2 a 10-minute file peaked at about 15 GB, and the card advises splitting long recordings into pieces of a few minutes on 8 or 16 GB Macs (**Reported**).[^bark-3.0-card]
- The measured throughput is a whole-file batch figure, not per-chunk streaming latency: 41× realtime means a 60 s clip returns in ~1.5 s, which is far above any realtime turn budget once VAD, network, and LLM/TTS time are added (**Synthesis**).[^bark-3.0-card]
- The card's runtime measurements use `transcribe`, which it says adds 0.25 s of silence before the audio (**Reported**); see [Contradictions](#contradictions) for the sibling card's opposite statement.[^bark-3.0-card]

## Runtimes

- Underdog runs `model.bark` as-is with no Python: a native Swift runtime unpacks it in memory in about 2 seconds on Apple silicon, runs it on MLX, and verifies `model.bark` and `mlx/config.json` against a pinned size and SHA-256; the unpacked weights are bit-identical to what `bark_loader.py` produces (**Reported**).[^bark-3.0-card]
- The release also documents Transformers (`bark_loader.py` with `transformers==5.19.0`/`torch==2.8.0`), mlx-audio (`bark_mlx.py`, `mlx==0.32.2`/`mlx-audio==0.5.3`), Core ML GPU and ANE packages for macOS, an iOS Core ML embedding contract, and a Windows CUDA/CPU runtime; the full matrix, pins, and file manifests are compiled on [Underdog Bark 3.0 Platform Runtimes](underdog-bark-3.0-runtimes.md) (**Reported**).[^bark-3.0-card]

## Relationships

- Finetune of [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) through `moondream/parakeet-ultra`, keeping the teacher's tokenizer and punctuation/casing/numeral conventions while narrowing 25-language coverage to English and shrinking the download about 15× for the same seven-set mean (**Reported**; ratio is **Synthesis**).[^bark-3.0-card]
- Same-lineage siblings already in the wiki: [Parakeet Ultra](parakeet-ultra.md) is the full-precision post-training path that scores 5.80 on the same seven sets, [Parakeet Redux](parakeet-redux.md) is the ternary 178 MB derivative at 6.55, and [Phonon-2](phonon-2.md) is a separate 164 MB quantization of the same teacher at 5.21; Bark 3.0 is the branch that spends the family budget on English-only accuracy at 4.94 (**Reported**; the comparison is **Synthesis**).[^bark-3.0-card]
- Verbatim parent of [Underdog Bark 3.0 Clean](underdog-bark-3.0-clean.md), which is built on Plus rather than the 163 MB base and changes *what* is transcribed; the two pages must not be ranked against each other, because Clean's 5.83 is scored against verbatim references (**Reported**; non-comparability is **Synthesis**).[^bark-3.0-card]
- Baselines with wiki concepts in the same vendor table: [Hojo-ASR-V1](hojo-asr-v1.md) (11,957 MB, 4.29), [Qwen3-ASR-1.7B](qwen3-asr-family.md) (4,699 MB, 4.43), [Higgs Audio v3 STT](higgs-audio-v3-stt.md) (5,351 MB, 4.45), [Canary-Qwen 2.5B](canary-qwen-2.5b.md) (5,119 MB, 4.55), [Cohere Transcribe 03-2026](cohere-transcribe-03-2026.md) (4,132 MB, 4.85), [Whisper Large v3](whisper-large-v3.md) (9,261 MB, 6.04) and [Large v3 Turbo](whisper-large-v3-turbo.md) (1,618 MB, 6.58) (**Reported**).[^bark-3.0-card]
- Cross-card caution: this seven-set, vendor-scored table is not the eight-set protocol used by several rows of the [ASR/STT Model Survey](asr-stt-model-survey.md), so sub-0.5-point gaps against those pages should not drive a decision (**Synthesis**).[^bark-3.0-card]
- Name collision, not a relationship: the `bark` engine listed in [CrispASR TTS Engines](crispasr-tts-engines.md) is Suno's Bark text-to-speech model, a different system sharing the name (**Synthesis**).

## Contradictions

- Measurement padding: this card states that `transcribe` "adds 0.25 s of silence before the audio, the setting the numbers above use", while the sibling Clean card states that Bark 3.0 Clean "was measured with no silence added before the audio, which is what `transcribe` does". Both describe the same helper by name; the statements cannot both be true unless the two releases use different loaders or the two cards describe different code versions, and neither card settles which. The benchmark numbers on both pages may therefore have been produced under different padding conventions; neither reading is chosen here (**Reported**; tension is **Synthesis**).[^bark-3.0-card]
- Frontier wording as a second, weaker tension: the card says the family "holds the accuracy frontier ... at every size from 163 MB to 1.25 GB" while its own table shows several much larger models with better per-column bests and a Hojo-ASR-V1 mean of 4.29 that ties Pro; the claim is about the 163 MB–1.25 GB band only, which the table supports and the wording does not state (**Reported**; scoping is **Synthesis**).[^bark-3.0-card]

## Coverage and limits

- One capture, `raw/ConwayResearch-Underdog-Bark-3.0.md` (181 lines), read in full and inspected statically only; no weights downloaded, no audio transcribed, no install, and no WER or throughput figure reproduced (**Synthesis**).[^bark-3.0-card]
- The referenced figure `bark_frontier.png` is not present in `raw/` and was not inspected; no material claim depends on it, and the plotted values would in any case be unverifiable at pixel precision (**Synthesis**).[^bark-3.0-card]
- Excluded as absent or uninspected: `model.bark`, `mlx/*`, `bark_loader.py`, `bark_mlx.py`, `coreml/*`, `runtime/*`, `NOTICE`; the DisfluencySpeech paper (arXiv 2406.08820) and its 250-clip test set; the Open ASR Leaderboard space and scoring code; the Plus, Pro, Bark 2.0 and Clean cards except for the cross-check above; and `underdog.ai` (**Synthesis**).[^bark-3.0-card]
- No card statement covers streaming or partial hypotheses, word or segment timestamps, diarization, language coverage beyond English, VRAM/RAM on non-Apple hardware, or behaviour on non-dictation audio with crosstalk; the 41× M2 figure is whole-file throughput and the 15 GB peak is a single 10-minute observation on one machine (**Synthesis**).[^bark-3.0-card]
- Every accuracy, size, and speed figure is the vendor's own report; per the `stt` domain rule the page carries `stale_after: 2027-10-25` (**Synthesis**).[^bark-3.0-card]

[^bark-3.0-card]: [Underdog Bark 3.0 model card](../raw/ConwayResearch-Underdog-Bark-3.0.md) — locators: frontmatter (`base_model: nvidia/parakeet-tdt-0.6b-v3`, `base_model_relation: finetune`, `language: en`, `library_name: transformers`, `pipeline_tag: automatic-speech-recognition`, `license: cc-by-4.0`, tags `underdog`/`speech-to-text`/`asr`/`stt`/`low-bit`/`on-device`/`mlx`/`apple-silicon`/`parakeet`, metric `wer`); `# Underdog Bark 3.0` intro (163 MB, 4.94 seven-set average, "no open model under 900 MB ... except Bark 3.0 Plus", Phonon-2 same size, three-decimal 4.937 vs 4.941 against Parakeet TDT 0.6B v3, Whisper large-v3 57× bigger, AMI 7.82 and VoxPopuli 2.05, M2 one minute in ~1.5 s = 41× realtime on stock mlx-audio, `bark_frontier.png` image reference); `## In Underdog` (native Swift runtime, ~2 s unpack on Apple silicon, MLX, bit-identical to `bark_loader.py`, pinned size and SHA-256 on `model.bark` and `mlx/config.json`, audio never leaves the device, Clean named as the dictation variant); `## Highlights` (frontier claim for 163 MB–1.25 GB, Phonon-2 163.4 MB/5.21, Whisper large-v3 6.04/9.3 GB and Voxtral Small 24B 5.21/97 GB at 57× and ~600× smaller downloads, Qwen3-ASR-0.6B 5.16, Canary 1B v2 5.81, Phi-4-multimodal 5.10, Parakeet teacher at a fifteenth of its size); `## Benchmarks` table (16 rows as reproduced above; seven English Open ASR sets with cleaned AMI/Earnings-22/GigaSpeech/VoxPopuli, † leaderboard rows as of 9 October 2026, Bark rows scored with the leaderboard code but not submitted, three-decimal averages Pro 4.286 and Hojo-ASR-V1 4.291, NC = non-commercial licence, download = weight-file size); `### Disfluent speech` (250 unscripted clips, verbatim transcripts with fillers counted: Pro 2.95, Bark 3.0 3.15, Plus 3.21, Phonon-2 3.39; "writes what was said" and does not clean speech up); `## Run it` (pip `huggingface_hub==2.2.0`, `hf download ... --include "model.bark" --include "bark_loader.py" --include "bark_mlx.py" --include "mlx/*" --include "NOTICE"`, `transformers==5.19.0 torch==2.8.0 constriction==0.5.0 numpy==2.4.6 soundfile==0.14.0 soxr==1.1.0 librosa==0.11.0`, `python bark_loader.py model.bark recording.wav`, `load_model(device="cuda"|"cpu"|"mps")` plus `transcribe`, MLX fence `mlx==0.32.2 mlx-audio==0.5.3` and `python bark_mlx.py`, first-run unpack and cache, exact unpacking, 0.25 s leading silence, 10-minute file peaking at ~15 GB on a 16 GB M2, split guidance for 8/16 GB Macs); `## Notes` (V3 via moondream/parakeet-ultra, original tokenizer and punctuation/casing/numeral conventions, CC-BY-4.0 plus `NOTICE`, English only, Plus 180 MB and Pro full precision as the larger family members); `## Additional platform runtimes` (Core ML GPU/ANE macOS packages, iOS multifunction model and Swift porting contract, Windows CUDA/CPU `runtime/transcribe_bark.py`, Pro's 1.23 GB whole-pipeline Core ML alternative via FluidAudio, "Not yet tested on an iPhone or iPad").

---
type: Concept
title: VieGem-ASR
description: Vietnamese and Vietnamese–English 359M CTC ASR with 0.48-second chunked attention, reported Vietnamese and code-switching WER, and non-commercial licensing.
tags: [stt, asr, vietnamese, code-switching, ctc, streaming]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T14:32:06Z }
stale_after: 2027-11-02
sources:
  - id: viegem-card
    resource: ../raw/VieGem-ASR.md
    kind: documentation
    title: VieGem-ASR model card capture
---

VieGem-ASR is a **reported** 359M-parameter Vietnamese and Vietnamese–English CTC recognizer built on the EmbeddingGemma 2 audio encoder. One model supports full-context and 0.48 s chunked attention without look-ahead; the card reports 6.34% mean greedy WER on eight Vietnamese sets and 14.30% on ViMedCSS. Its CC-BY-NC-SA-4.0 and Gemma terms constrain use, and none of these claims has been independently reproduced.[^viegem-card]

## Architecture and operation

**Reported:** the encoder has 12 Conformer layers at 25 frames/s, with the top four fine-tuned. A layer mix feeds six 768-dimensional Transformer reader blocks and a 21,031-Gemma-token CTC head initialized from text embeddings. The listed fp16 checkpoint is 311 MB; the card does not explain how its size relates to the 359M parameter count or which encoder components it includes.[^viegem-card]

The example requires PyTorch, CUDA, `soundfile`, the repository's `asr/` code, checkpoint and Gemma tokenizer; Gemma terms must be accepted. It supplies 16 kHz mono audio of at most 30 seconds and uses BF16 autocast; `streaming=True` selects chunked mode. Optional KenLM 4-gram beam decoding uses `alpha=0.35`, `beta=1.5`, beam width 32 and a unigrams file. This is an example on an audio tensor, not a documented live session or cache policy (**Reported**; deployment distinction **Synthesis**). Do not load untrusted PyTorch checkpoints or run uninspected code without a separate safety review.[^viegem-card]

## Evaluation

**Reported**, WER in percent; all results below are from the card, not reproduced. Its Vietnamese table says VieGem, QUAN and Qwen3-ASR-0.6B were run using one normalizer (lowercase, no punctuation, numbers as words); other systems marked † come from the QUAN card. Training sentences were reportedly filtered against test and dev sentences; this does not independently establish split integrity.[^viegem-card]

| Set | Greedy | + LM | Streaming greedy (0.48 s) |
|---|---:|---:|---:|
| VIVOS | 6.63 | 4.78 | 8.73 |
| FLEURS vi | 7.33 | 5.85 | 9.02 |
| Common Voice 17 | 8.61 | 6.21 | 10.84 |
| PhoAudiobook | 1.39 | 1.04 | — |
| LSVSC | 5.16 | 4.71 | 5.84 |
| Bud500 | 3.08 | 2.75 | — |
| GigaSpeech2 vi | 9.50 | 8.52 | — |
| ViMD | 9.05 | 8.46 | 10.00 |
| Mean of eight | 6.34 | 5.29 | — |

On ViMedCSS, test/hard WER is 14.30/21.08 greedy, 13.00/19.84 with LM, and test WER 15.99 in streaming mode. The card reports 66% of English terms written exactly but gives no measurement protocol. Paper-sourced baselines have their own normalization, so comparisons are approximate.[^viegem-card]

The headline ~3,500× real time uses batched greedy inference on one H100; separately, a 10-minute video takes 0.49 s, median of 20 runs (~1,220×). Neither is a live mic-to-stable-text latency measurement, and their workload details are insufficient to reconcile the two throughput rates (**Reported**; distinction **Synthesis**). The 0.48 s chunk is not an end-to-end latency guarantee.[^viegem-card]

## Training, limitations and license

**Reported:** about 5,800 hours include ~1,900 h audiobooks, ~2,820 h social media/YouTube, ~780 h mixed Vietnamese, ~100 h LibriSpeech-100, and ~23 h medical ViMedCSS. Itemized values are approximate and do not sum exactly to the headline. Output is lowercase, without punctuation, with numbers as words; clips cut mid-word more often lose the last word. Plain English is weak: LibriSpeech test-clean WER 10.7. The card declares CC-BY-NC-SA-4.0 for non-commercial research and additionally requires Gemma Terms of Use and Prohibited Use Policy; the actual terms and training-data rights were not inspected.[^viegem-card]

## Relationships

- Inspired by [QUAN-Transcribe-1.0](quan-transcribe-1.0.md), another EmbeddingGemma 2 CTC system; the VieGem card reports QUAN's eight-set mean at 6.89 versus VieGem's 6.34 under its own evaluation. Do not substitute QUAN's separate card benchmark or infer identical live-streaming implementation.[^viegem-card]
- Compared in [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) and [ASR/STT Model Survey](asr-stt-model-survey.md); test the actual license, endpointing, stable partials and target hardware before selection (**Synthesis**).[^viegem-card]

## Coverage and limits

**Observed:** the entire local model-card capture was read statically. Its decorative `assets/cover.jpg`, `asr/`, `lm/`, checkpoint and `demo/` paths are absent relative to `raw/`; the remote demo video, model implementation, weights, tokenizer, LM, datasets, benchmark code, cited baselines and license texts were not inspected. No installation, download, inference or benchmark was run. The source does not identify a revision, release date or capture date; the video URL indicates `5CD-AI/VieGem-ASR` but provenance is otherwise not independently established. Cache reuse, live API, endpointing, GPU memory, CPU performance and per-turn latency are not documented. `draft` reflects these material evidence gaps.[^viegem-card]

[^viegem-card]: [VieGem-ASR model card](../raw/VieGem-ASR.md) — frontmatter and opening; `Results` (Vietnamese, code-switching, streaming and speed); `Usage`; `Model`; `Training data`; `Limitations`; `License`; `Demo`.

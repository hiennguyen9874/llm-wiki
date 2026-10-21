---
type: Concept
title: Parakeet CTC 0.6B Vietnamese
description: NVIDIA 600M-parameter offline FastConformer-CTC Vietnamese ASR model (card title "Unified Vietnamese–English CS") trained on ~2,000 hours with Qwen3-generated punctuation and capitalization, NeMo timestamps, an optional KenLM 4-gram flashlight decode, reported 9.30 blind and 9.73 in-domain average WER, and a gated NVIDIA Open Model License.
tags: [stt, asr, vietnamese, fastconformer, ctc, nemo, punctuation, kenlm]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T21:00:00Z }
stale_after: 2027-10-21
sources:
  - id: parakeet-ctc-vi-card
    resource: ../raw/parakeet-ctc-0.6b-Vietnamese.md
    kind: documentation
    title: Parakeet-CTC-0.6B Unified Vietnamese–English CS model card capture
---

Parakeet CTC 0.6B Vietnamese (Hugging Face `nvidia/parakeet-ctc-0.6b-Vietnamese`; the card's code uses `nvidia/parakeet-ctc-0.6b-vi`) is an NVIDIA NeMo FastConformer-CTC model of about 600M parameters that transcribes Vietnamese speech offline. It was trained on roughly 2,000 hours from 10 public datasets, with punctuation and capitalization (PnC) added to most training transcripts by Qwen3, and it ships with an optional Wikipedia-based 4-gram KenLM plus lexicon for flashlight beam search (**Reported**).[^parakeet-ctc-vi-card] The card reports 9.30 average WER on four "blind" sets and 9.73 on six "in-domain" sets, but it describes no streaming mode, latency, or throughput figure, so it is a final-pass (turn-final) candidate for a Vietnamese voice loop, not an established partial-transcript engine (**Synthesis**).[^parakeet-ctc-vi-card]

## Identity and lineage

- Card title "Parakeet-CTC-0.6B Unified Vietnamese–English CS"; version string `Parakeet-CTC-0.6B-unified ASR Vietnamese_1.1`; frontmatter `language: [vi]`, `library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, `metrics: [wer]`, tags `FastConformer`, `Parakeet`, `CTC` (**Observed** by static inspection).[^parakeet-ctc-vi-card]
- The description names only Vietnamese data. The words "Unified" and "CS" (read here as code-switching) and the Figure 1 caption reference to "CSPs" are never expanded in text, and the README states no English or code-switch training data, evaluation set, or score (**Observed**; the meaning of "CS" is a **Synthesis** reading).[^parakeet-ctc-vi-card]
- Architecture: Parakeet-CTC, also called FastConformer-CTC, an optimized Conformer with 8x depthwise-separable convolutional downsampling and CTC loss; 600M parameters (**Reported**).[^parakeet-ctc-vi-card]
- Runtime: NeMo 2.6; supported microarchitectures Ampere, Blackwell, Hopper, Volta; preferred OS Linux (**Reported**).[^parakeet-ctc-vi-card]
- License: `license: other`, NVIDIA Open Model License; the repository is gated, with a request form (company, date, intended use) and a stated 2–3 day processing time. The card says the model is ready for commercial and non-commercial use (**Reported**).[^parakeet-ctc-vi-card]

## Training and evaluation data

- Training size ~2,000 hours across 10 datasets: Common Voice Corpus 20.0, VietMed-L (16 h), LSVSC, FLEURS, InfoRe 2, FOSD (FPT), VAIS, VLSP 2020, VSV-1100, and MS-SNSD (**Reported**).[^parakeet-ctc-vi-card]
- FLEURS transcripts keep their original punctuation and capitalization; the remaining transcripts received PnC from Qwen3 (the card links the Qwen3-Next-80B-A3B-Instruct model card). So most punctuated and capitalized targets are machine-generated, and the card gives no PnC accuracy check (**Reported**; the missing check is **Observed**).[^parakeet-ctc-vi-card]
- The tokenizer was built from the training transcripts with NeMo's `process_asr_text_tokenizer.py`; training used `speech_to_text_ctc_bpe.py` with `fast-conformer_ctc_bpe.yaml`. Vocabulary size, epochs, batch size, and hardware are not stated (**Reported**; gaps **Observed**).[^parakeet-ctc-vi-card]
- Collection is labeled hybrid automated/human and labeling hybrid synthetic/human. Per-dataset licenses and consent terms are not discussed (**Observed**).[^parakeet-ctc-vi-card]

## Reported accuracy

WER is scored without punctuation and capitalization errors, per the Figure 1 caption. The decoding setup, with or without the n-gram LM, is not stated for either table (**Reported**).[^parakeet-ctc-vi-card]

| Blind set | AVG | Gigaspeech2 | VLSP 2021 Task 2 | ViMD | VIVOS |
| --- | --- | --- | --- | --- | --- |
| WER % | 9.30 | 11.23 | 8.99 | 11.02 | 5.96 |

| In-domain set | AVG | MCV-Vi-20 | FOSD | LSVSC | FLEURS | VLSP 2021 Task 1 | VietMed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WER % | 9.73 | 8.58 | 9.67 | 5.15 | 6.86 | 13.60 | 14.52 |

- Both averages equal the plain mean of their printed cells (9.30 over four, 9.73 over six), a recomputation by the wiki (**Reproduced** arithmetic only; no model run).
- "In domain" sets share names with training datasets (Common Voice, FOSD, LSVSC, FLEURS, VietMed), so those six scores measure matched-domain performance. Whether train and test splits overlap is not stated (**Observed**). Only the blind sets are described as held out (**Reported**).[^parakeet-ctc-vi-card]
- The card says the VietMed test set was fixed for transcript-audio misalignment, without saying how or against which reference (**Reported**).[^parakeet-ctc-vi-card]
- Figure 1 (a bar chart of WER against other models and "CSPs", not captured as text) and all compared-model numbers are uninspected, so no head-to-head ranking is recorded here (limit).[^parakeet-ctc-vi-card]

## Inference and usage

- Install `nemo_toolkit['asr']` after the latest PyTorch; load with `nemo_asr.models.ASRModel.from_pretrained(...)`; `asr_model.transcribe([...])` returns objects whose `.text` holds the transcript (**Reported**).[^parakeet-ctc-vi-card]
- `transcribe(..., timestamps=True)` returns char, word, and segment timestamps in `output[0].timestamp['char' | 'word' | 'segment']` with `start`/`end` seconds (**Reported**).[^parakeet-ctc-vi-card]
- N-gram LM: the repository provides a 4-gram KenLM binary and a filtered lexicon (`lm_4gram_wiki_traintext_4x_vi_en_dict_newStyleTone_PnC_vi_en_2.0*`), trained on Vietnamese Wikipedia and extended with a Vietnamese dictionary and proper-name/place-name lists. The documented recipe sets `CTCDecodingConfig` strategy and beam search type to `flashlight`, `beam_size` 64, `beam_alpha` 0.3, `beam_beta` 0.5, `beam_size_token` 32, `beam_threshold` 20.0, then calls `change_decoding_strategy`. No WER with the LM, no cost in latency or memory, and no tuning guidance are given (**Reported**; gaps **Observed**).[^parakeet-ctc-vi-card]
- Input: `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`; mono channel required; maximum length is bounded by GPU memory; no pre-processing needed. Output: a string with no maximum length, and the card says it does not handle special characters (**Reported**).[^parakeet-ctc-vi-card]
- Test hardware list: A10, A100, A30, H100, Jetson Orin, L4, L40, T4, V100, and a Blackwell GPU. It is a compatibility list, not a performance table (**Reported**).[^parakeet-ctc-vi-card]

## Voice-pipeline implications (Synthesis)

- **Role:** offline CTC with no documented chunking or cache, so treat it as a turn-final model after VAD/endpointing. Native partials would need a separate buffering design, or a cache-aware model such as [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md).
- **Output form:** built-in punctuation and capitalization (unlike the English lowercase [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md)) can save a separate punctuation step for display, but the PnC labels are LLM-generated and unaudited, so test numerals, names, and sentence boundaries before relying on them.
- **Comparison caution:** the test sets (VIVOS, VLSP 2021 Task 1/2, FLEURS, Common Voice 20.0, VietMed) are not the same releases, normalizers, or splits as the cards behind [ZipFormer 150M Vietnamese](zipformer-150m-vietnamese.md), [ChunkFormer Vietnamese](chunkformer-vietnamese.md), [PhoWhisper](phowhisper.md), or [Gipformer 1.5 68M RNNT](gipformer1.5-68m-rnnt.md). Do not rank them from published cells; run one holdout with one normalizer.
- **License gate:** the gated NVIDIA Open Model License needs reading and acceptance before a production decision. It differs from the CC-BY-4.0 of the English Parakeet CTC pages.

## Relationships

- Vietnamese counterpart of [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md): same FastConformer-CTC ~600M family and NeMo `speech_to_text_ctc_bpe.py` recipe, but a different checkpoint, language, data, PnC behavior, and license (**Synthesis**).[^parakeet-ctc-vi-card]
- Compared in the card tables of [Gipformer 68M RNNT](gipformer-68m-rnnt.md) and [Gipformer 1.5 68M RNNT](gipformer1.5-68m-rnnt.md) as `nvidia/parakeet-ctc-0.6b-Vietnamese`; those pages give a third-party comparison on private call-center sets, not this card's evidence (**Reported** by those pages).
- Candidate listed in [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) as an offline NVIDIA-stack final-pass option, and cataloged in the [ASR/STT Model Survey](asr-stt-model-survey.md) (**Synthesis**).
- Same toolchain family as [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) (multilingual TDT, no Vietnamese among its 25 European languages in this wiki's page) and the NeMo-based [NeMo Speech ASR Models](nemo-speech-asr-models.md) packaging; whether the Vietnamese checkpoint is supported by a GGUF or C++ runtime is **Unverified** (no source states it).

## Coverage and limits

- One model-card capture, inspected statically in full (frontmatter, description, architecture, I/O, usage code, software integration, datasets, performance, inference, ethics, license, references); no NeMo install, checkpoint download, audio, or WER execution (**Synthesis**).[^parakeet-ctc-vi-card]
- Not inspected or unavailable: Figure 1 image and its comparison models, the 4-gram `.bin` and lexicon files, weights and tokenizer, the Qwen3 model card, NeMo example script and configuration, NVIDIA license PDF, the linked KenLM tutorial, dataset releases, and the cited references (FastConformer arXiv 2305.05084, NeMo docs, Conformer arXiv 2005.08100). Revision hash and publication date are not in the capture.
- Absent evidence: streaming or chunked behavior, latency, RTFx, memory, code-switch or English performance, noise and telephony robustness, per-dialect results, PnC accuracy, and WER with the n-gram LM.
- Card inconsistencies noted without resolving: repository id `...-Vietnamese` versus `...-vi` in code; the title's "Unified ... CS" versus a Vietnamese-only description; Reference [3] is cited as "NeMo toolkit" but links the Conformer paper (**Observed**).[^parakeet-ctc-vi-card]
- All capability, data, and accuracy claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-21` per the `stt` domain rule (**Synthesis**).

[^parakeet-ctc-vi-card]: [Parakeet-CTC-0.6B Unified Vietnamese–English CS card](../raw/parakeet-ctc-0.6b-Vietnamese.md) — locators: frontmatter (`license`, `license_name`, `extra_gated_*`, `language`, `metrics`, `library_name`, `tags`); `Description`; `Model Architecture`; `Input(s)`; `Output(s)`; `How to use this model` (install, `from_pretrained`, `transcribe`, timestamps, `Inference with n-gram language model`); `Software Integration`; `Model Version(s)`; `Training and Evaluation Datasets` (`Training Dataset`, `Evaluation Dataset`); `Performance` (`Blind testset`, `In domain testset`); `Inference` (test hardware); `License/Terms of Use`; `References(s)`; Figure 1 caption.

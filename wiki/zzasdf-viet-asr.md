---
type: Concept
title: VietASR (zzasdf, arXiv 2505.21527)
description: Official VietASR code and paper pointer (arXiv 2505.21527) for a low-resource Vietnamese ASR pipeline with ASR-biased SSL and iterative k-means pseudo-labeling on icefall and lhotse, a 70,000-hour Iteration 3 checkpoint, and no WER in the captured README.
tags: [stt, asr, vietnamese, self-supervised, pseudo-labeling, icefall, open-source, research]
status: draft
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T05:20:00Z }
stale_after: 2027-10-13
sources:
  - id: zzasdf-viet-asr-readme
    resource: ../raw/zzasdf-VietASR.md
    kind: documentation
    title: VietASR (zzasdf/VietASR) README capture
---

VietASR is the official code release for the arXiv 2505.21527 paper of the same name, a training pipeline "designed for low resource ASR" (**Reported**).[^zzasdf-viet-asr-readme] It uses ASR-biased self-supervised learning (SSL) to pretrain a speech encoder from limited labeled data and large unlabeled data, runs in four stages (initial ASR training, label extraction, pretraining, finetuning), and publishes a checkpoint trained on 70,000 hours of pseudo-labeled Vietnamese speech from Iteration 3 (**Reported**).[^zzasdf-viet-asr-readme] The captured README reports no word or character error rate, so the title's "industry-level" accuracy claim is **Unverified** here. This project is **not** the [VietASR (dangvansam, QuartzNet)](dangvansam-viet-asr.md) model that shares its name; see [Disambiguation](#disambiguation). Run commands are in [VietASR Training and Checkpoint Procedure](zzasdf-viet-asr-procedure.md).

## Method

- **Stages:** the README lists four stages: initial ASR training on a small labeled set, label extraction, pretraining, and finetuning.[^zzasdf-viet-asr-readme]
- **Pseudo-label targets:** k-means is applied to the supervised ASR model for the first pretraining iteration and to the finetuned model for later iterations, selected by a `--checkpoint-type` flag (**Reported**).[^zzasdf-viet-asr-readme] The README does not define "ASR-biased" beyond this; the paper, not captured, would.
- **Unlabeled audio:** FunASR `fsmn-vad` segments the audio into `.wav` files before fbank extraction (**Reported**).[^zzasdf-viet-asr-readme]
- **Title framing:** "50-hour labeled data" and "industry-level" appear only in the paper title. The README body does not quantify either.[^zzasdf-viet-asr-readme]

## Artifacts and dependencies

- **Code:** the GitHub repository `zzasdf/VietASR`. It uses [icefall](https://github.com/k2-fsa/icefall) as its training framework and [lhotse](https://github.com/lhotse-speech/lhotse) for data preparation; `PYTHONPATH` must include icefall before any script runs.[^zzasdf-viet-asr-readme] A Python 3.10 badge appears, but the text gives no version requirement.
- **Checkpoint:** the Hugging Face repository `zzasdf/viet_iter3_pseudo_label`, described as 70,000 hours of Vietnamese pseudo-labeled data from VietASR Iteration 3. The usage example loads `exp/epoch-12.pt` with a BPE tokens file under `data/Vietnam_bpe_2000_new/` (**Reported**).[^zzasdf-viet-asr-readme] The path name suggests a 2,000-piece BPE vocabulary, which the README does not state (**Synthesis**).
- **Decoder:** the example uses `modified_beam_search` in `ASR/zipformer/pretrained.py`. The Zipformer architecture is inferred from that path (**Synthesis**).[^zzasdf-viet-asr-readme]
- **License:** Apache License 2.0, stated as derived from icefall. The LICENSE file is not captured, and the checkpoint's license is not stated.[^zzasdf-viet-asr-readme]
- **Downstream package:** [Zipformer 30M Vietnamese](zipformer-30m-vietnamese.md) records a sherpa-onnx package whose upstream pointer resolves to this checkpoint (**Observed** docs, per that page's research capture; not re-checked here).

## Relationships

- **Uses:** icefall and lhotse, and FunASR `fsmn-vad` for unlabeled-audio segmentation. The wiki has no concept pages for these.[^zzasdf-viet-asr-readme]
- **Companion:** [VietASR Training and Checkpoint Procedure](zzasdf-viet-asr-procedure.md) holds the run order, data layout, and checkpoint commands.

## Disambiguation

- **Same name, different project:** [VietASR (dangvansam, QuartzNet)](dangvansam-viet-asr.md) is a community NeMo QuartzNet model with 13M parameters. Figures for one do not apply to the other.
- **Unverified WER attribution:** other pages credit this paper with a 16.44% mean WER for Whisper large-v3 on three Vietnamese test sets, for example [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) and [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md). The README contains no such table, test set, or Whisper number,[^zzasdf-viet-asr-readme] so that attribution stays **Unverified** until checked against the paper's tables.
- **Unchecked name:** the "VietASR-zipformer (68M)" column in [Gipformer 68M RNNT](gipformer-68m-rnnt.md) was not compared with this project and should not be assumed to refer to it.

## Coverage and limits

- **Inspected:** the README capture `raw/zzasdf-VietASR.md` (154 lines), read statically. No commit or release is recorded, so no revision is pinned.[^zzasdf-viet-asr-readme]
- **Not captured:** the paper and its results tables; `images/pipeline.png`, the pipeline diagram (unavailable; the text names the same four stages); `LICENSE`; the scripts and code the README links; the Hugging Face checkpoint and its model card; the icefall and lhotse sources; and the k2SSL paper, which appears only in the BibTeX citation.
- **Consequential limits:** the capture has no WER, CER, latency, or hardware evidence. The unlabeled corpus and the 70,000-hour pseudo-labeled set are described only generally, so their provenance, consent, and redistribution terms are unknown.
- **Status:** `draft`. Promotion past draft needs the paper's results, the LICENSE, and the checkpoint's model card.
- No install, script execution, download, or inference was run. The capture contains public URLs only, and no sensitive values were found.

[^zzasdf-viet-asr-readme]: [VietASR (zzasdf/VietASR) README capture](../raw/zzasdf-VietASR.md) — locators: title and arXiv badge (lines 1–2); repository link and Python 3.10 badge (line 3); opening paragraph (line 5); checkpoint paragraph (line 7); `Overview` (lines 8–9; pipeline image at line 11, not captured); `Environment` (lines 13–17); `Unsupervised data preparation` (lines 20–29, VAD at line 21); `Initial ASR model` (lines 56–61); `Train k-means model` (lines 63–70, checkpoint-type rule at line 64); `Pre-train` and `Fine-tune` (lines 89–100); `Checkpoint usage` (lines 109–128); `Citation` (lines 131–149); `License` (lines 151–154).

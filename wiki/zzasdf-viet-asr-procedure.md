---
type: Concept
title: VietASR Training and Checkpoint Procedure
description: Run order for the zzasdf VietASR code, covering data layout, initial ASR training, k-means label extraction, pretraining, finetuning, decoding, and inference with the released checkpoint, with an unreconciled supervised-data layout and a decode-flag caveat.
tags: [stt, asr, vietnamese, self-supervised, procedure, icefall]
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

The [VietASR (zzasdf, arXiv 2505.21527)](zzasdf-viet-asr.md) README gives an ordered run sequence: prepare data, train an initial ASR model, learn and extract k-means labels, pretrain, finetune, and decode. It also gives a separate path for inference with the released checkpoint and for finetuning it (**Reported**).[^zzasdf-viet-asr-readme] The commands below are transcribed from the README and were not executed. Script internals, argument defaults, and hardware needs are outside this capture (see [Coverage and limits](#coverage-and-limits)).

## Prerequisites

- Install icefall and lhotse by their own tutorials; the README links them and gives no versions.[^zzasdf-viet-asr-readme]
- Before running any script, run `export PYTHONPATH=icefall_path:$PYTHONPATH`, with `icefall_path` set to the local icefall checkout (lines 14–17).[^zzasdf-viet-asr-readme]
- A Python 3.10 badge appears at the top of the README; no Python requirement appears in the text.[^zzasdf-viet-asr-readme]

## Data preparation

- **Unlabeled audio:** run VAD with FunASR `fsmn-vad`, using `SSL/local/vad.py` as the example. Store `.wav` segments under `SSL/download/ssl_${subset_name}`, set `subset_name` in `SSL/prepare_ssl.sh` to match, then run `cd SSL && ./prepare_ssl.sh`. The manifest lands in `SSL/data/ssl_${subset_name}/{subset_name}_split`. Training subset names must start with `train`, and a `dev` subset must exist.[^zzasdf-viet-asr-readme]
- **Supervised audio:** store `.wav` files in per-utterance folders, each with a `filename.trans.txt` whose lines pair a filename stem with its transcript. Organize the train, test, and dev folders, then run `cd ASR && ./prepare.sh`.[^zzasdf-viet-asr-readme]
- **Contradiction:** line 32 says to put supervised data under `download/supervised`, but the directory tree at lines 33–43 places `train`, `test`, and `dev` directly under `download`. Neither reading is chosen here; check `ASR/prepare.sh` before relying on either.[^zzasdf-viet-asr-readme]

## Training stages

1. **Initial ASR model:** run `cd ASR && ./scripts/train.sh` on the small labeled set.[^zzasdf-viet-asr-readme]
2. **K-means model:** build a train cut of about 100 hours from the unlabeled manifest (the README suggests Python's gzip library). Point `--files` in `SSL/scripts/learn_fbank_kmeans.sh` at that cut. Set `--checkpoint-type` to `ASR` for the first pretraining iteration and to `finetune` for later iterations. Then run `cd SSL && ./scripts/learn_vietASR_kmeans.sh`.[^zzasdf-viet-asr-readme]
3. **Label extraction:** write one `src_cut target_cut` pair per line into the file named by `--task-list`. Give each iteration its own label in the target name, for example `..._iter1.00000001.jsonl.gz`. Edit `SSL/scripts/extract_vietASR_kmeans.sh`, then run it.[^zzasdf-viet-asr-readme]
4. **Pretraining:** edit the parameters in `SSL/scripts/run_ssl.sh` and run it.[^zzasdf-viet-asr-readme]
5. **Finetuning:** edit the parameters in `SSL/scripts/finetune.sh` and run it.[^zzasdf-viet-asr-readme]
6. **Decoding:** run `cd SSL && ./scripts/decode.sh $epoch $avg $gpu_id`. This evaluates the checkpoint at `$epoch`, averaged over `$avg` epochs, on GPU `$gpu_id`.[^zzasdf-viet-asr-readme]

Steps 2–5 are described per iteration. The k-means flag rule implies that later iterations start from the finetuned model (**Reported**); that the loop repeats is **Synthesis** from the `iter` label naming and the "Iteration 3" checkpoint.

## Checkpoint inference and finetuning

- **Inference:** after downloading the Hugging Face checkpoint `zzasdf/viet_iter3_pseudo_label`, run `./ASR/zipformer/pretrained.py --checkpoint viet_iter3_pseudo_label/exp/epoch-12.pt --tokens ./viet_iter3_pseudo_label/data/Vietnam_bpe_2000_new/tokens.txt --method modified_beam_search /path/to/foo.wav`. The README does not show the download step, the expected audio format, or sample-rate requirements.[^zzasdf-viet-asr-readme]
- **Finetuning the checkpoint:** run `cd SSL && ./scripts/finetune_ASR_checkpoint.sh`.[^zzasdf-viet-asr-readme]
- **Decoding a finetuned checkpoint:** run `cd SSL && ./scripts/decode.sh $epoch $avg $gpu_id`, after adding `--use-layer-norm 0` in `decode.sh`. The README does not say whether this flag applies only to finetuned checkpoints or why it is needed.[^zzasdf-viet-asr-readme]

## Relationships

- **Uses:** icefall, lhotse, and FunASR `fsmn-vad`. The wiki has no concept pages for them.[^zzasdf-viet-asr-readme]
- **Companion:** this page is the operational half of [VietASR (zzasdf, arXiv 2505.21527)](zzasdf-viet-asr.md), which holds the method, artifacts, and disambiguation.

## Contradictions

- **Supervised data location:** `download/supervised` (line 32) versus `download/{train,test,dev}` (lines 33–43). Unresolved; neither reading is chosen.[^zzasdf-viet-asr-readme]

## Coverage and limits

- **Inspected:** the README prose and commands in `raw/zzasdf-VietASR.md` (lines 13–128), read statically. No script, config, or launcher was captured or read.[^zzasdf-viet-asr-readme]
- **Not captured:** `SSL/local/vad.py`, `SSL/prepare_ssl.sh`, `ASR/prepare.sh`, `ASR/scripts/train.sh`, the `SSL/scripts/*.sh` files, and `ASR/zipformer/pretrained.py`. Their argument defaults, paths, and the effect of `--use-layer-norm 0` are **Unverified**.
- **Not stated in the README:** GPU count and memory, training duration, the checkpoint download step, the audio format for inference, and the expected output quality of each stage.
- **Execution:** none. The commands were transcribed, not run, so they support no reproduced finding.
- **Status:** `draft`. Promotion past draft needs the captured scripts and a reproduced run in a stated environment.

[^zzasdf-viet-asr-readme]: [VietASR (zzasdf/VietASR) README capture](../raw/zzasdf-VietASR.md) — locators: `Environment` (lines 13–17); `Unsupervised data preparation` (lines 20–29, VAD at line 21); `Supervised data preparation` (lines 31–54, directory tree at lines 33–43); `Initial ASR model` (lines 56–61); `Train k-means model` (lines 63–70, checkpoint-type rule at line 64); `Extract labels` (lines 73–87); `Pre-train` (lines 89–94); `Fine-tune` (lines 95–100); `Decode` (lines 101–107); `Checkpoint usage` (lines 109–128, `--use-layer-norm 0` at line 128).

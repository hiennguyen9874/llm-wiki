---
type: Software
title: HunyuanOCR-1.5 training and inference stack
description: HunyuanOCR-1.5's GitHub repository documents packed-sequence SFT, DFlash draft-model training, a unified CUDA-13 inference environment, and GGUF deployment through upstream llama.cpp.
tags: [ocr, document-parsing, training-pipeline, speculative-decoding, llama-cpp, deployment]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:24:26Z }
sources:
  - id: hunyuanocr-repo-readme
    resource: ../raw/HunyuanOCR-github.md
    kind: code
    title: "HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better (GitHub repository README)"
---

# HunyuanOCR-1.5 training and inference stack

The HunyuanOCR-1.5 repository publishes the full supervised fine-tuning pipeline, a separate procedure for training or continue-finetuning the DFlash speculative-decoding draft model, one unified inference environment covering vLLM, DFlash, and native Transformers, and a GGUF path for `llama.cpp`. All of it is documentation of intended use: the README supplies commands, default hyperparameters, and entry-point paths, while the pages those commands depend on (`docs/`, `train/`, `scripts/`, `inference/`) are absent from the local bundle, so nothing here is observed or reproduced.[^hunyuanocr-repo-readme]

## Training environment

The README's `Environment → Training` section lists Python 3.10+ (3.12 tested), PyTorch 2.1+ with CUDA 12.1+ (a `cu130` build is said to be tested end-to-end), `transformers` 4.57+, and DeepSpeed 0.14+; `flash-attn` must be built manually with `--no-build-isolation`. Training scripts live under `scripts/` and share `scripts/env_common.sh` for distributed variables, with multi-node runs driven by the standard `NNODES` / `NODE_RANK` / `MASTER_ADDR` / `MASTER_PORT` variables.[^hunyuanocr-repo-readme]

## Data packing and SFT

The `Training` section documents a two-stage data preparation: tokenize each raw OCR JSONL, then pack multiple samples into single sequences up to `packed_max_length=20480` tokens. `configs/data_list.txt` holds one absolute path per raw JSONL, and `scripts/pack_data.sh` runs a multi-process count-and-pack pipeline (`PACK_LEN=20480`, `NUM_PROCESSES=32`, `THREADS_PER_PROCESS=8`) implemented by `tools/pipeline_count_and_pack.py` and `tools/pack_from_counted.py`, emitting `./data/parsing_packed_20480.jsonl`.[^hunyuanocr-repo-readme]

Full end-to-end SFT covers the vision encoder, MLP projector, and language model on those packed sequences. The stated default profile is `lr=2e-5`, 5 epochs, per-GPU batch size 1, and `packed_max_length=20480`, launched through `scripts/sft_base.sh` with `train/train_hunyuan.py` as entry point in an 8-GPU example. The README defers the complete argument list to `docs/training.md`, which is not in the bundle.[^hunyuanocr-repo-readme]

## DFlash draft training

Two documented paths train the speculative draft. Training **from scratch** (`scripts/sft_dflash.sh`, `train/train_draft.py`) uses `lr=1e-4`, 2 epochs, `num_mask_tokens=16`, and `sample_block_num=8`. Continue-finetuning a released draft (`scripts/sft_dflash_finetune.sh`, `train/train_draft_from_dflash.py`, requiring `DFLASH_INIT`) is recommended by the README for adapting to a smaller or domain-specific dataset, with `lr=2e-5`, 10 epochs, `warmup_ratio=0.05`, and `save_steps=500`. Both paths consume the same packed OCR JSONL as the base SFT stage.[^hunyuanocr-repo-readme]

Separately, the News entry dated 2026/07/24 announces open-sourcing a verl-based reinforcement-learning stack (`train_verl/`). The README gives no reward definitions, data requirements, or training scales for it, and that directory is not in the bundle.[^hunyuanocr-repo-readme]

## Unified inference environment

The README replaces per-stack installs with one `uv` environment requiring CUDA 13 (`uv venv --python 3.12`, `vllm>=0.25.1`, `flash-attn==2.8.3` built without isolation) that serves all three configurations from one install: vLLM autoregressive, DFlash speculative decoding, and native multi-GPU Transformers. The README states that accuracy alignment across the three has been verified, but publishes neither the comparison protocol nor its results; it points to lighter per-configuration recipes in `docs/inference/inference.md` for machines without CUDA 13.[^hunyuanocr-repo-readme]

Weights come from the single Hugging Face repository `tencent/HunyuanOCR`, which holds the 1.5 base checkpoint at the root and the DFlash draft under `dflash/`, downloaded with `--exclude "v1.0/*"` to skip the archived 1.0 checkpoint. The vLLM serving example uses `-tp 1` and `--max-model-len 131072`, and its readiness check is a `/v1/models` request.[^hunyuanocr-repo-readme]

## Task types and sampling defaults

Prompts are locked to official task types through `--task-type`, and `--list-tasks` enumerates 12 of them. The README fixes the sampling configuration around those prompts — `temperature=0.0`, `top_p=1.0`, `top_k=-1`, `repetition_penalty=1.08` — and builds in tail-repetition early stopping and cleanup, so the documented client is not a free-form generation interface. Client examples use `--max-tokens 32768`, and `inference/vLLM/batch_infer.py` adds multi-endpoint concurrency (example `--concurrency 16`) with resumable runs over an image directory. The README says all configurations share the same weights, task prompts, sampling, and post-processing so their outputs are directly comparable.[^hunyuanocr-repo-readme]

## llama.cpp and GGUF deployment

For CPU, consumer-GPU, or laptop use, the README converts the checkpoint with `convert_hf_to_gguf.py` into an `f16` base GGUF plus a separate `mmproj` vision projector, then serves both through `llama-server` with `--ctx-size 10240`, `--n-predict 4096`, `-fa on`, and `--jinja` in the example. Enabling speculation additionally converts the shipped draft to `bf16` with `--target-model-dir` and starts the server with `--spec-draft-model`, `--spec-type draft-dflash`, `--spec-draft-n-max 15`, and `--parallel 1`.[^hunyuanocr-repo-readme]

Critically, the README states that DFlash speculative decoding is now merged into upstream `llama.cpp` (PR #28890, build `b11103` and later), so "no fork is needed: upstream `master` serves both the base model and DFlash." Draft conversion, DFlash tuning, measured speedup, and a smoke-test client (`llama_cpp/chat.py` with 26 sample OCR images) are deferred to `docs/llama_cpp.md`, which is not in the bundle.[^hunyuanocr-repo-readme]

## Coverage and trust limits

The local source is one README file, so its coverage ledger is short: the entry point was read in full, and every artifact it links — `docs/training.md`, `docs/data_format.md`, `docs/inference/inference.md`, `docs/llama_cpp.md`, `docs/benchmark.md`, `inference/`, `train/`, `scripts/`, `tools/`, `configs/`, `benchmarks/`, `llama_cpp/`, `train_verl/`, `LICENSE`, `README_zh.md`, and `assets/HyOCR_1_5_teaser.png` — is absent. Nothing was executed: no environment was built, no training run started, and no server launched.[^hunyuanocr-repo-readme]

Consequently every value above is **reported** documentation, not a verified effective default. The bundle provides no measured speedup, acceptance rate, VRAM footprint, throughput, dataset composition, or model size, and it does not reconcile these defaults with the code that consumes them. The News timeline is promotional in tone, so dated claims (especially the upstream `llama.cpp` merge and the 12 task types) should be re-checked against the repository or build notes before being relied on.[^hunyuanocr-repo-readme]

## Relationships

- **Trains:** [HunyuanOCR-1.5](hunyuanocr-1.5.md) base weights, then the DFlash draft that provides its speculative decoding.[^hunyuanocr-repo-readme]
- **Related to:** [Document-parser data flywheel](document-parser-data-flywheel.md) — the README's Agentic Data Flow is described as producing the capability data that the upgraded recipe consumes, but the pipeline pages never trace provenance for the packed JSONL input (synthesis).[^hunyuanocr-repo-readme]

[^hunyuanocr-repo-readme]: Tencent Hunyuan, *HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better* (GitHub repository README), local capture at [HunyuanOCR-github.md](../raw/HunyuanOCR-github.md); locators are the README sections `News`, `Environment → Training`, `Training` steps 1–4, `Inference` and its subsections, `Documentation`, and `License` (accessed 2026-10-25).

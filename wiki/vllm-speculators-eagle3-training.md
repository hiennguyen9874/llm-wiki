---
type: Concept
title: vLLM Speculators Eagle3 Training (v0.3.0)
description: End-to-end Eagle3 draft-model training in Speculators v0.3.0 with offline vLLM hidden-state data generation, FlexAttention train-time testing, and self-contained vLLM deployment.
tags: [vllm, speculative-decoding, speculators, eagle]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T23:00:00Z }
sources:
  - id: spec050
    resource: ../raw/speculators-v050-dflash-support-and-online-training/index.md
    title: 'Speculators v0.5.0: DFlash support and online training'
  - id: spec030
    resource: ../raw/2025-12-13-speculators-v030/index.md
    title: Diving into speculative decoding training support for vLLM with Speculators v0.3.0
---

Speculators v0.3.0 provides end-to-end training support for Eagle3 draft models that run in vLLM, covering offline hidden-state data generation with vLLM, training for single- and multi-layer drafts on MoE and non-MoE verifiers, and a self-contained model artifact with `speculators_config` for one-command serving[^spec030].

## Eagle3 draft inputs

Eagle3 is presented as the current SOTA speculative-decoding algorithm: the draft takes hidden states from verifier layers plus token IDs and autoregressively proposes draft tokens for parallel verifier checking[^spec030].

Training needs per-sample[^spec030]:

- Verifier hidden states from intermediate layers.
- Token IDs.
- Loss mask restricting training to model responses, ignoring user prompts.
- Verifier output signal as the training target; the data-generation diagram stores the last-layer output before `lm_head` instead of the full distribution because `hidden_dim` is typically orders of magnitude smaller than verifier vocab size, recomputing the target distribution later with the verifier `lm_head`.

The appendix reproduces Eagle3 generation as verifier-plus-draft pseudocode: autoregressively sample K drafts from `D(tokens, hidden)`, validate them in parallel with `V`, keep each draft with probability `min(1, q/p)` against verifier probabilities, and on rejection discard the suffix and resample from `q − p`[^spec030].

## Offline data generation

Three stages: preprocessing, hidden-states generation, and saving[^spec030].

Preprocessing of a standard text dataset[^spec030]:

1. Reformat and normalize conversation turns.
2. Apply the model chat template.
3. Tokenize.
4. Compute loss masks from assistant-response spans.
5. Save token IDs plus preprocessing output and collect token-frequency statistics.

Loss masks focus training on machine-generated tokens. For reasoning models that typically put thinking tokens only in the last response, an extra flag randomly drops conversation turns to widen the mix of trained conversation lengths[^spec030].

Hidden-state capture uses a vLLM plugin through a custom worker extension: it patches the model forward pass to intercept selected intermediate hidden states during prefill, runs batched inference with the vLLM multiprocess executor, and supports tensor parallelism for larger models[^spec030]. The diagram shows the generator driving an executor plus scheduler, RPC setup of capture on `custom worker × n`, forward-pass patching on the LLM, interception of selected-layer outputs, and return of a capture buffer via RPC[^spec030].

Saving writes each sample as one `.pt` file with `input_ids`, per-layer `hidden_states` list, and `loss_mask`, using `ThreadPoolExecutor` async I/O so disk writes overlap generation[^spec030]. It also writes `data_config.json` metadata and `token_freq.pt` frequencies[^spec030].

`token_freq.pt` feeds `build_vocab_mapping.py` to create target-to-draft (`t2d`) and draft-to-target (`d2t`) mappings between the verifier full vocabulary and a smaller draft vocabulary; the reduced draft vocabulary, typically 10k–32k tokens, improves draft efficiency by keeping only frequent tokens[^spec030].

Scripts[^spec030]:

- `scripts/data_generation_offline.py`: preprocess, save token frequencies, generate hidden states.
- `scripts/build_vocab_mapping.py`: build `t2d`/`d2t` tensors.
- `scripts/train.py`: run Eagle3 training.

## Training

Training consumes the generated samples, vocabulary mappings, and model configuration to initialize an `Eagle3DraftModel`, using the Eagle3 authors' train-time testing: simulate multi-step draft sampling during training so the model learns second and later tokens, not only the first token after a prefix[^spec030].

The reproduced train-time-testing figure shows per-prefix first-generation, then second-generation conditioned on prefix plus first draft, and so on, with the corresponding sparse attention masks[^spec030].

Sparsity is handled with FlexAttention plus `torch.compile`: FlexAttention splits the mask into blocks and computes only non-empty regions, speeding computation while cutting activation VRAM for the backward pass[^spec030].

Batching concatenates variable-length sequences along the sequence dimension and configures attention masks to treat them as separate sequences, avoiding padding/truncation waste; this composes with FlexAttention and an intelligent batch sampler that packs batches near the maximum sequence length[^spec030].

## Deployment in vLLM

Training emits a complete artifact whose extended `config.json` carries `speculators_config`, making the speculator self-describing: architecture and `auto_map`, `Speculators_model_type`/`Speculators_version`, `draft_vocab_size`, `transformer_layer_config`, plus algorithm, `proposal_methods` with `speculative_tokens`, acceptance controls such as `verifier_accept_k`/`accept_tolerance`, and the verifier `name_or_path` plus architectures[^spec030].

One-command serving reads that config to load draft plus verifier together[^spec030]:

```bash
vllm serve RedHatAI/Llama-3.1-8B-Instruct-speculator.eagle3
```

Long-form serving overrides the bundled verifier or tunes speculation, for example pairing an FP8 Qwen3-8B verifier with an Eagle3 speculator at five speculative tokens[^spec030]:

```bash
vllm serve RedHatAI/Qwen3-8B-FP8-dynamic \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.9 \
  --speculative-config '{"model": "RedHatAI/Qwen3-8B-speculator.eagle3", "num_speculative_tokens": 5, "method": "eagle3"}'
```

Speculative decoding is framed as best in low-throughput settings where unsaturated GPUs can exploit parallel verifier generation, with verifier-specific draft training needed for close alignment; reported latency reduction is 1.5–3x with no distribution shift versus verifier-only generation[^spec030].

## Model coverage and roadmap

At release, Speculators training plus vLLM serving covered Llama 3.1/3.2/3.3 from 8B to 70B, Qwen3 8B/14B/32B, Qwen3 MoE 235B-A22B, and GPT-OSS 20B/120B, with serving-only support for multimodal Llama 4 vision-language models[^spec030].

Planned next work: online data generation without intermediate disk caching, data-generation support for vision-language models, and regenerating verifier responses to replace dataset assistant responses for better-aligned training data[^spec030].

Online generation on the native hidden-states path shipped in v0.5.0 with shared online/offline format and hybrid file reuse[^spec050] — see [vLLM Speculators DFlash Training (v0.5.0)](vllm-speculators-dflash-training.md)[^spec050].

## Relationships

- Related to [vLLM Speculators Library](vllm-speculators.md) — v0.3.0 is the end-to-end Eagle3 training release within that library.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — Eagle3 `method: eagle3` serving is the deployment target for drafts trained here.
- Related to [vLLM Hidden State Extraction](vllm-hidden-state-extraction.md) — native `extract_hidden_states` plus KV-connector sinking is the later in-vLLM mechanism corresponding to this release's patched-worker offline hidden-state generator.
- Uses [FlexAttention Programmable Attention Kernels](flex-attention.md) — block-sparse FlexAttention plus `torch.compile` handles train-time-testing masks and backward-pass memory.
- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — low-concurrency fit, alignment requirement, and acceptance/K tuning for serving the resulting drafts.
- Related to [vLLM Speculators DFlash Training (v0.5.0)](vllm-speculators-dflash-training.md) — v0.5.0 unified native online/offline successor to this patched-worker offline path.

[^spec030]: Fynn Schmitt-Ulms, Helen Zhao, Rahul Tuli, Dipika Sikka (Red Hat AI Model Optimization Team), Diving into speculative decoding training support for vLLM with Speculators v0.3.0 — `../raw/2025-12-13-speculators-v030/index.md` (vLLM blog, 2025-12-13), covering Eagle3 inputs and dataset fields, three-stage offline generation with preprocessing/loss masks/reasoning-turn dropout, patched-worker prefill capture with multiprocess executor plus tensor parallelism and async writes, per-sample `.pt` plus `data_config.json`/`token_freq.pt` and `t2d`/`d2t` reduced-vocabulary mapping, `Eagle3DraftModel` train-time testing with FlexAttention plus `torch.compile` and concatenated sequence packing, `speculators_config` artifact with one-command and long-form `vllm serve`, 1.5–3x lossless latency claim with low-throughput fit, Llama/Qwen/GPT-OSS training-plus-serving coverage with Llama 4 serving-only, and online-generation/VLM/verifier-response roadmap; `assets/data_generation.png`, `assets/hidden_state_generator.png`, `assets/flex_attention.png`, and `assets/EAGLE3.png` inspected for last-layer storage note, executor/scheduler/worker capture path, multi-step mask structure, and Eagle3 accept/reject pseudocode.

[^spec050]: Helen Zhao, Speculators v0.5.0: DFlash support and online training — `../raw/speculators-v050-dflash-support-and-online-training/index.md` (Red Hat Developer, 2026-06-04), native-path online generation with shared format and hybrid reuse landing the v0.3.0 online roadmap item.

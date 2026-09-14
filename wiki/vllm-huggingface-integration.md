---
type: Concept
title: vLLM Hugging Face Integration
description: Resolving model IDs to config, tokenizer, and weights via Hugging Face Hub or local path, with config-class and architecture-registry mapping.
tags: [vllm, huggingface, model-loading, tokenizer]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: hf-integration
    resource: ../raw/vllm/design/huggingface_integration.md
    title: Integration with Hugging Face
---

vLLM loads `config.json`, the tokenizer, and the weights from a local path or the Hugging Face Hub, then selects a config class from vLLM, transformers, or the model repo and maps `architectures` to a vLLM model implementation[^hf-integration].

## Model-ID resolution

- Example flow is `vllm serve Qwen/Qwen2-7B`, where the `model` argument is resolved to a `config.json`[^hf-integration].
- If `model` is an existing local path, the config is loaded directly from that path[^hf-integration].
- If `model` is a Hub ID (`username/model-name`), vLLM first tries the local Hugging Face cache using `model` as name and `--revision` as revision (cache layout follows `HF_HOME`) [^hf-integration].
- On cache miss, vLLM downloads `config.json` from the Hub with `model`, `--revision`, and `HF_TOKEN` as the access token (e.g. `Qwen/Qwen2-7B` `config.json` on `main`) [^hf-integration].
- Implementation: `vllm/transformers_utils/config.py` config-existence check and download helper[^hf-integration].
- After existence is confirmed, the config file is loaded and converted to a dictionary[^hf-integration].

## Config-class selection

- vLLM inspects the `model_type` field in the config dict to generate the config object to use[^hf-integration].
- A subset of `model_type` values is directly supported by vLLM; the supported list lives in `vllm/transformers_utils/config.py`[^hf-integration].
- Otherwise vLLM falls back to `AutoConfig.from_pretrained` with `model`, `--revision`, and `--trust_remote_code` as arguments[^hf-integration].
- Hugging Face's own resolution first searches `model_type` in the transformers `models/` directory; if absent, it uses the `AutoConfig` entry under the config's `auto_map` field (e.g. `deepseek-ai/DeepSeek-V2.5`) [^hf-integration].
- That `auto_map` value points to a module path inside the model repo; Hugging Face imports it and calls `from_pretrained`, which can execute arbitrary code and therefore only runs when `--trust_remote_code` is enabled[^hf-integration].

## Config patches and architecture mapping

- vLLM then applies historical patches to the config object, mostly RoPE-related[^hf-integration].
- The `architectures` field in the config selects the model class via vLLM's architecture-to-class registry in `vllm/model_executor/models/registry.py`; an unregistered name means the architecture is unsupported[^hf-integration].
- Example: `Qwen/Qwen2-7B` has `architectures: ["Qwen2ForCausalLM"]`, mapped to the `Qwen2ForCausalLM` implementation in `vllm/model_executor/models/qwen2.py`, which initializes from the various configs[^hf-integration].

## Tokenizer

- vLLM tokenizes with the Hugging Face tokenizer loaded via `AutoTokenizer.from_pretrained` using `model` and `--revision`, implemented in `get_tokenizer` in `vllm/transformers_utils/tokenizer.py`[^hf-integration].
- A different tokenizer model can be forced with `--tokenizer`, plus `--tokenizer-revision` and `--tokenizer-mode`; see Hugging Face docs for their meanings[^hf-integration].
- Setting `VLLM_USE_FASTOKENS=1` swaps in a drop-in Rust BPE backend for any loaded HF fast tokenizer; full backend detail is in [vLLM Input Processing Performance](vllm-input-processing-tuning.md)[^hf-integration].
- vLLM caches expensive tokenizer attributes in `vllm.tokenizers.hf.get_cached_tokenizer` after loading[^hf-integration].

## Model weights

- Weights are downloaded from the Hub using `model` and `--revision`; `--load-format` controls which files are fetched[^hf-integration].
- Default behavior tries safetensors first and falls back to PyTorch bin format; `--load-format dummy` skips weight download[^hf-integration].
- Safetensors is recommended because it loads efficiently in distributed inference and avoids arbitrary code execution; weight-loading logic lives in `vllm/model_executor/model_loader/loader.py`[^hf-integration].

## Coverage limits

- Pinned code links in the source (vLLM `10b67d8` / `127c074`) were not re-verified against a live checkout; line numbers may have drifted[^hf-integration].
- The `fastokens Backend` detail from `../configuration/optimization.md` is now compiled in [vLLM Input Processing Performance](vllm-input-processing-tuning.md)[^hf-integration].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — `vllm serve <model>` is the entry flow that triggers Hub resolution.
- Uses [vLLM Input Processing Performance](vllm-input-processing-tuning.md) — `VLLM_USE_FASTOKENS` Rust BPE backend replacing the HF fast tokenizer path above.
- Uses [vLLM LoRA Resolver Plugins](vllm-lora-resolver-plugins.md) — LoRA adapters can also be discovered from filesystem or Hub backends at request time.

[^hf-integration]: Integration with Hugging Face — `../raw/vllm/design/huggingface_integration.md`.

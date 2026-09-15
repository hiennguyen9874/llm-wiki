---
type: Concept
title: Qwen3.8-2.4T-A95B Architecture and Evaluation
description: Official HF model card, config, and Transformers code for Qwen3.8-2.4T-A95B hybrid GDN-MoE with thinking controls and Max benchmark evidence.
tags: [qwen3.8, moe, gated-deltanet, hybrid-attention, mtp, reasoning, transformers, context-extension]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T18:00:00Z }
sources:
  - id: qwen38-readme
    resource: ../raw/Qwen3.8-2.4T-A95B/README.md
    title: Qwen3.8-2.4T-A95B
  - id: qwen38-config
    resource: ../raw/Qwen3.8-2.4T-A95B/config.json
    title: Qwen3.8-2.4T-A95B config.json
  - id: qwen38-py-config
    resource: ../raw/Qwen3.8-2.4T-A95B/configuration_qwen3_5_moe.py
    title: configuration_qwen3_5_moe.py
  - id: qwen38-py-model
    resource: ../raw/Qwen3.8-2.4T-A95B/modeling_qwen3_5_moe.py
    title: modeling_qwen3_5_moe.py
  - id: qwen38-py-modular
    resource: ../raw/Qwen3.8-2.4T-A95B/modular_qwen3_5_moe.py
    title: modular_qwen3_5_moe.py
---

Qwen3.8-2.4T-A95B is the open post-trained text-only causal LM behind Qwen3.8-Max, built on the Qwen3.5 architectural foundation with 2.4T total / 95B active parameters, 92-layer 3:1 Gated DeltaNet plus gated-attention MoE, mandatory thinking mode with `reasoning_effort` control, and official Max benchmark evidence against Opus 4.8, Fable 5, GPT-5.6 Sol, and Qwen3.7-Max[^qwen38-readme][^qwen38-config].

## Model identity

- Type: causal language model, pre-training plus post-training stage[^qwen38-readme].
- First Qwen-Max-class model in open release; follows Qwen3.5/Qwen3.6 adoption with claimed gains on coding, professional work, research, and long-horizon agentic tasks[^qwen38-readme].
- `Qwen3.8-2.4T-A95B` is text-only and thinking-required; `Qwen3.8-Max` is the official API version adding vision input, non-thinking support, 1M context by default, and built-in tools[^qwen38-readme].
- Highlights: stronger autonomous planning and environment-feedback handling, broader harness/tool compatibility, tunable reasoning depth via `reasoning_effort`, and retained historical reasoning context via `preserve_thinking`[^qwen38-readme].
- License: `qwen3.8-max`; citation is the Qwen3.8-Max blog entry, August 2026[^qwen38-readme].
- HF architecture: `Qwen3_5MoeForCausalLM`, model type `qwen3_5_moe_text`, Transformers `4.57.3`[^qwen38-config][^qwen38-py-config].

## Architecture

Authoritative dims from README plus `config.json`[^qwen38-readme][^qwen38-config]:

- Total 2.4T, 95B activated; hidden `8192`; vocab/LM output `248320` padded; `92` layers; `bfloat16`; `tie_word_embeddings: false`; `bos_token_id`/`eos_token_id` `248044`[^qwen38-readme][^qwen38-config].
- Hidden layout: `23 × (3 × (Gated DeltaNet → MoE) → 1 × (Gated Attention → MoE))`, i.e. 69 linear-attention plus 23 full-attention layers[^qwen38-readme].
- `full_attention_interval: 4` with explicit 92-entry `layer_types` list (`linear_attention` except every 4th `full_attention`)[^qwen38-config].
- Gated DeltaNet: 128 V heads plus 16 QK heads; QK head dim 128, V head dim 128; conv kernel dim 4; SSM dtype `float32`[^qwen38-readme][^qwen38-config].
- Gated attention: 64 Q heads, 4 KV heads, head dim 256, partial rotary factor `0.25` (64 rotary dims), RoPE theta `10000000`[^qwen38-readme][^qwen38-config].
- MoE: 512 experts, 10 routed plus 1 shared per token; expert and shared-expert intermediate `2048`; `router_aux_loss_coef 0.001`; `output_router_logits false`[^qwen38-readme][^qwen38-config].
- Attention options: `attention_bias false`, `attention_dropout 0.0`, `attn_output_gate true`, `output_gate_type swish`, `hidden_act silu`, `rms_norm_eps 1e-06`[^qwen38-config].
- MTP: trained with multiple steps; `mtp_num_hidden_layers 1`, `mtp_use_dedicated_embeddings false`[^qwen38-readme][^qwen38-config].
- Context: `max_position_embeddings 262144` natively, extensible to `1,010,000` tokens[^qwen38-readme][^qwen38-config].

## Transformers implementation

- Config classes: `Qwen3_5MoeTextConfig`, `Qwen3_5MoeVisionConfig`, `Qwen3_5MoeConfig`; text `model_type qwen3_5_moe_text` with `base_config_key text_config`[^qwen38-py-config].
- Modular file re-exports Qwen3.5 / Qwen3-Next / Qwen3-VL-MoE bases: `Qwen3_5MoeGatedDeltaNet` from `Qwen3_5GatedDeltaNet`, attention/experts/decoder from `Qwen3Next*`, router/outputs from `Qwen3VLMoe*`, vision from `Qwen3_5Vision*`[^qwen38-py-modular].
- Modeling file defines `Qwen3_5MoeGatedDeltaNet`, `Qwen3_5MoeAttention`, `Qwen3_5MoeMLP`, `Qwen3_5MoeExperts`, `Qwen3_5MoeTopKRouter`, `Qwen3_5MoeSparseMoeBlock`, `Qwen3_5MoeDecoderLayer`, plus `Qwen3_5MoeTextModel`, `Qwen3_5MoeModel`, `Qwen3_5MoeForCausalLM`, and `Qwen3_5MoeForConditionalGeneration`[^qwen38-py-model].
- Parallel plans in config: TP plan for q/k/v/o plus q/k norms, expert gate/up/down and linear-attn in/out projections; PP plan for embeddings/layers/norm; EP plan for router plus grouped-GEMM experts[^qwen38-py-config].
- Optional kernels: `causal_conv1d` and `fla` gated-delta-rule with Torch fallback paths (`torch_chunk_gated_delta_rule`, `torch_recurrent_gated_delta_rule`, `torch_causal_conv1d_update`) when hub kernels are absent[^qwen38-py-model].
- Config-file defaults (`hidden 2048`, 40 layers, 256 experts, 8 per token) are base-class placeholders; the 2.4T-A95B `config.json` values above override them — do not read the `.py` defaults as this checkpoint's specs[^qwen38-py-config][^qwen38-config].

## Thinking controls and API usage

- Thinking cannot be disabled; every response begins with reasoning in `<think>\n...\n</think>\n\n` before the final output[^qwen38-readme].
- `reasoning_effort`: `xhigh` default for thorough analysis, `medium` for balance, `low` for speed/cost; `preserve_thinking` on by default[^qwen38-readme].
- Recommended sampling: `temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, presence_penalty 0.0, repetition_penalty 1.0`; `presence_penalty` 0–2 may curb repetition at some language-mixing risk[^qwen38-readme].
- Agentic output budget within 1M context: 262,144 reasoning plus 131,072 final response tokens[^qwen38-readme].
- Chat Completions pattern passes `extra_body.chat_template_kwargs {enable_thinking: True, preserve_thinking: True}` with `reasoning_effort` and streaming `include_usage`; Qwen Cloud instead passes `extra_body {enable_thinking: True, preserve_thinking: True}` with a changed `model` value — full Python snippet lives in the source[^qwen38-readme].

## Serving compatibility

- HF-Transformers-format weights are stated compatible with vLLM, SGLang, and TokenSpeed; source urges latest framework versions and serving engines for production/high-throughput use[^qwen38-readme].
- Pointers only (not inspected): SGLang Qwen3.8 cookbook, vLLM Qwen3.8-2.4T-A95B recipe, TokenSpeed Qwen3.8 recipe, Qwen Cloud managed API, and Qwen3.8-Max blog overview[^qwen38-readme].

## Benchmark evidence

Source-reported Qwen3.8-Max table vs Opus 4.8, Fable 5, GPT-5.6 Sol (max), and Qwen3.7-Max; `--` means unavailable; methodology footnotes are condensed below[^qwen38-readme].

Coding agent:

| Benchmark | Opus 4.8 | Fable 5 | GPT-5.6 Sol | Qwen3.7-Max | Qwen3.8-Max |
| --- | --- | --- | --- | --- | --- |
| Terminal Bench 2.1 | 84.6 | 84.6 | 88.8 | 74.5 | 86.6 |
| SWE-bench Pro | 69.2 | 80.0 | 64.6 | 60.6 | 67.7 |
| DeepSWE 1.1 | 59.0 | 70.0 | 73.0 | 21.6 | 56.6 |
| NL2Repo-Bench | 69.4 | -- | -- | 47.2 | 55.9 |
| FrontierSWE | 70.0 | 88.8 | -- | 40.7 | 73.5 |
| MLS-Bench-Lite | 42.8 | 49.9 | 46.2 | 31.7 | 41.0 |
| PaperBench | 80.3 | 88.8 | 90.5 | 64.8 | 93.0 |
| AndroidBench | 69.8 | 84.5 | 74.0 | 56.5 | 75.1 |
| QwenSWEBench | 84.0 | 86.3 | 73.5 | 63.4 | 80.7 |
| QwenQoderBench | 62.7 | 63.1 | 53.8 | 36.8 | 58.4 |
| QwenReactBench | 1694 | 1770 | 1564 | 1538 | 1724 |
| QwenSVGBench | 1648 | 1690 | 1758 | 1499 | 1713 |

General agent:

| Benchmark | Opus 4.8 | Fable 5 | GPT-5.6 Sol | Qwen3.7-Max | Qwen3.8-Max |
| --- | --- | --- | --- | --- | --- |
| CoWorkBench | 72.3 | 75.9 | 71.5 | 64.6 | 74.8 |
| WorkSpaceBench | 66.8 | 68.7 | 65.6 | 61.4 | 67.7 |
| JobBench | 48.4 | 57.4 | 45.4 | 31.3 | 53.4 |
| SkillsBench | 65.1 | 70.9 | 73.5 | 61.2 | 70.2 |
| Agents Last Exam pass/score | 27.0 / 45.1 | -- / -- | 30.6 / 53.6 | 11.8 / 31.1 | 27.0 / 52.4 |
| Automation-Bench | 27.2 | 29.1 | 29.7 | 14.2 | 27.3 |
| Toolathlon Verified | 76.2 | 77.9 | 74.9 | 49.7 | 72.5 |
| WideSearch | 72.9 | 81.2 | -- | 75.2 | 81.9 |
| HLE w/ tools | 57.9 | 64.5 | 58.0 | 53.5 | 56.2 |

General capabilities:

| Benchmark | Opus 4.8 | Fable 5 | GPT-5.6 Sol | Qwen3.7-Max | Qwen3.8-Max |
| --- | --- | --- | --- | --- | --- |
| GPQA Diamond | 92.0 | 92.6 | 94.1 | 92.4 | 92.6 |
| HLE | 45.7 | 53.3 | 47.2 | 41.4 | 43.6 |
| IFBench | 62.2 | 63.5 | 72.7 | 79.1 | 82.8 |
| $OneMillion-Bench | 41.8 | 55.9 | 53.8 | 44.4 | 52.5 |
| HealthBench | 52.4 | -- | 55.3 | 54.5 | 60.2 |
| PLawBench | 69.6 | 70.2 | 72.3 | 58.9 | 73.2 |
| PRBench-Legal | 52.7 | 57.6 | 57.6 | 48.5 | 57.6 |
| PRBench-Finance | 51.9 | 55.8 | 55.5 | 46.8 | 58.3 |
| MRCR v2 256K 8-needle | 83.2 | -- | 93.8 | 86.7 | 92.9 |
| LongBench v2 | 69.1 | -- | 67.1 | 65.3 | 66.3 |

Methodology notes (condensed): Terminal Bench 2.1 Claude Code avg@10, 5h timeout, 131K max tokens vs published best (Terminus 2 / Codex); SWE-bench Pro Claude Code temp 1.0 top_p 0.95 256K on refined tasks; DeepSWE best of Claude Code / mini-SWE-agent; NL2Repo Claude Code with pip/git-clone bans; FrontierSWE Claude Code MEAN@5 vs Aug-2026 leaderboard; MLS-Bench-Lite Claude Code 5h 131K; PaperBench BasicAgent Code-Dev judged by Claude Opus 4.6 avg 3 runs; AndroidBench 95-task public avg@3; QwenSWEBench inhouse avg@3 8h 32K 256K; QwenQoderBench avg@5 6h; QwenReact/QwenSVG bilingual auto-render plus multimodal BT/Elo; CoWorkBench inhouse; SkillsBench v1.1 87 tasks avg 3 (Opus/Fable on Claude Code, GPT on Codex, Qwen on OpenCode); Automation 600-task public; WideSearch Claude Code vs Qwen-Agent item-F1 avg 4; $OneMillion/PLaw judged by gemini-3.1-pro-preview[^qwen38-readme].

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 2.4T-A95B identity run here via Unsloth GGUF/NVFP4 and llama.cpp rather than the official HF checkpoint and sampling/thinking controls above.
- Related to [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md) — datacenter Day-0 serving for the same 92-layer 69-GDN/23-GQA plus 512-expert top-10 architecture with three-state caching, ReplaySSM, chunked PP prefill, and PD disaggregation.
- Related to [SGLang Qwen3.8-Flash-Next Inference](sglang-qwen3.8-flash-next-inference.md) — Flash-Next sibling replacing this 69/23 GDN/GQA stack with 36-GDN/12-QSA sparse attention plus gated residual and PLE offload.
- Uses [SGLang and vLLM Comparison](sglang-vs-vllm.md) — vLLM/SGLang/TokenSpeed compatibility claim above is the framework context that comparison evaluates.

## Contradictions

- None across the ingested files. Distinguish variants rather than treating them as conflicting: text-only thinking-required `2.4T-A95B` vs multimodal hybrid-thinking `Qwen3.8-Max` with vision, non-thinking, 1M default, and built-in tools[^qwen38-readme].

## Coverage limits

- `modeling_qwen3_5_moe.py` (2280 lines) inspected via headers, class/function list, and kernel-import fallbacks — not full forward-pass logic; `configuration` (213 lines) and `modular` (336 lines) inspected for class names, defaults, TP/PP/EP plans, and inheritance, not every docstring line[^qwen38-py-model][^qwen38-py-config][^qwen38-py-modular].
- Benchmark table transcribed from README HTML; figures are source-reported Qwen-team claims under mixed harnesses, not independently verified[^qwen38-readme].
- Blog post, SGLang/vLLM/TokenSpeed cookbooks, Qwen Cloud API, and HF/ModelScope weight files were referenced but not inspected[^qwen38-readme].
- No credentials, PII, or disclosure markings found in the five ingested files.

[^qwen38-readme]: Qwen3.8-2.4T-A95B model card — `../raw/Qwen3.8-2.4T-A95B/README.md`, covering Max-class open-release identity, text-only thinking-required vs Max API variant, 2.4T/95B 92-layer 23×(3×GDN→MoE→GQA→MoE) dims, 262K native / 1.01M extensible context, multi-step MTP, reasoning_effort plus preserve_thinking controls with sampling and output-budget guidance, Chat Completions snippet with Qwen Cloud variant, vLLM/SGLang/TokenSpeed compatibility, full Max benchmark table with 20 methodology notes, license, and citation.
[^qwen38-config]: Qwen3.8-2.4T-A95B config — `../raw/Qwen3.8-2.4T-A95B/config.json`, covering Qwen3_5MoeForCausalLM / qwen3_5_moe_text identity with 8192 hidden, 248320 vocab, 92 layers, full_attention_interval 4 plus explicit layer_types, GDN 16-QK/128-V and gated-attention 64-Q/4-KV dims with partial-rotary 0.25 and RoPE theta 10M, 512-expert 10+1 MoE with 2048 intermediates, MTP 1-layer no-dedicated-embeddings, and 262144 max positions.
[^qwen38-py-config]: Transformers config code — `../raw/Qwen3.8-2.4T-A95B/configuration_qwen3_5_moe.py`, covering Qwen3_5MoeText/Vision/Config classes, qwen3_5_moe_text type, base-class defaults vs checkpoint overrides, layer_types derivation from full_attention_interval, and TP/PP/EP plans.
[^qwen38-py-model]: Transformers modeling code — `../raw/Qwen3.8-2.4T-A95B/modeling_qwen3_5_moe.py`, covering GatedDeltaNet/attention/MoE/router/decoder/text/model/CausalLM class list with causal_conv1d and fla optional kernels plus Torch fallbacks.
[^qwen38-py-modular]: Transformers modular code — `../raw/Qwen3.8-2.4T-A95B/modular_qwen3_5_moe.py`, covering thin-wrapper inheritance from Qwen3.5, Qwen3-Next, and Qwen3-VL-MoE bases for config, attention, MoE, norm, decoder, vision, and CausalLM classes.

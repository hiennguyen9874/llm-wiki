---
type: Concept
title: Qwen3.8-Flash-Next HF Release and Serving
description: Official HF Qwen3.8-Flash-Next release with Qwen4Exp config and code, thinking controls, YaRN 1M extension, QwenCloud Flash pricing and integrations, and post-trained agentic evaluation.
tags: [qwen3.8-flash-next, qwen4, transformers, thinking, reasoning-effort, yarn, serving, evaluation, multimodal]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: qwen38-next-readme
    resource: ../raw/Qwen3.8-Flash-Next/README.md
    title: Qwen3.8-Flash-Next HF model card
  - id: qwen38-next-blog
    resource: ../raw/Qwen3.8-Flash-Next/blog.md
    title: Qwen3.8-Flash-Next blog
  - id: qwen38-next-config
    resource: ../raw/Qwen3.8-Flash-Next/config.json
    title: Qwen3.8-Flash-Next config.json
  - id: qwen38-next-py-config
    resource: ../raw/Qwen3.8-Flash-Next/configuration_qwen4_exp.py
    title: configuration_qwen4_exp.py
  - id: qwen38-next-py-model
    resource: ../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py
    title: modeling_qwen4_exp.py
  - id: qwen38-next-py-modular
    resource: ../raw/Qwen3.8-Flash-Next/modular_qwen4_exp.py
    title: modular_qwen4_exp.py
---

Qwen3.8-Flash-Next is the open post-trained multimodal MoE preview of the Qwen4 architecture, released as 125B total with 6B active plus 51B host-resident n-gram tables and 4B MTP, with mandatory thinking mode, `reasoning_effort` control, 262K native context extendable to 1M via YaRN, and a managed `qwen3.8-flash` production counterpart[^qwen38-next-readme][^qwen38-next-blog][^qwen38-next-config].

## Release identity

- Type: causal language model with vision encoder; pre-training plus post-training stage[^qwen38-next-readme].
- Role: early Qwen4 architecture preview, playing the same role Qwen3-Next played for Qwen3.5; GDN plus gated-attention pairing reworked into GDN plus QSA[^qwen38-next-readme][^qwen38-next-blog].
- Weights: HF `Qwen/Qwen3.8-Flash-Next` and ModelScope mirror; HF Transformers-format artifacts stated compatible with Transformers, vLLM, SGLang, and TokenSpeed; source urges latest framework versions and dedicated engines for production or high throughput[^qwen38-next-readme][^qwen38-next-blog].
- License: `other`, `qwen-community-1.0`[^qwen38-next-readme].
- Production counterpart: `qwen3.8-flash` on QwenCloud adds 1M context by default and official built-in tools; listed at 0.16 USD per M input tokens and 0.47 USD per M output tokens with API noted as coming soon[^qwen38-next-readme][^qwen38-next-blog].
- HF architecture: `Qwen4ExpForConditionalGeneration`, model type `qwen4_exp`, Transformers `5.8.0.dev0`[^qwen38-next-config].

## Authoritative dimensions

README plus `config.json`[^qwen38-next-readme][^qwen38-next-config]:

- LM: 125B with 6B activated, plus 51B n-gram embedding and 4B MTP; hidden `2560`; vocab and LM output `248320` padded; `48` layers; `bfloat16`; `tie_word_embeddings false`; `bos/eos 248044`[^qwen38-next-readme][^qwen38-next-config].
- Layout: `12 × (3 × (Gated DeltaNet → MoE) → 1 × (QSA → MoE))`, i.e. 36 linear-attention plus 12 sparse-attention layers; `full_attention_interval 4` with explicit 48-entry `layer_types` list[^qwen38-next-readme][^qwen38-next-config].
- GDN: 48 V heads plus 16 QK heads; QK and V head dim `128`; conv kernel dim `4`; SSM dtype `float32`[^qwen38-next-readme][^qwen38-next-config].
- QSA: 24 Q heads, 2 KV heads, head dim `256`, partial rotary factor `0.25` (64 rotary dims), RoPE theta `10000000`; indexer MQA with 4 query heads plus 1 shared key head, head dim `128`, budget `2048` tokens or 512 complete blocks plus tail, compress ratio `4`[^qwen38-next-readme][^qwen38-next-config].
- MoE: 512 experts, 10 routed plus 1 shared per token; expert and shared-expert intermediate `640`; `router_aux_loss_coef 0.001`; `output_router_logits false`[^qwen38-next-readme][^qwen38-next-config].
- Gated Residual: `hc_count 4` branches, bottleneck rank `320` (`d/8`); read is elementwise gated, write is per-branch scalar, no branch-mixing matrix[^qwen38-next-readme][^qwen38-next-config][^qwen38-next-blog].
- N-gram/PLE: `ngram_size 3` (bigrams and trigrams at layer 2), `ngram_vocab_size_base 20000000`, `heads_per_ngram 8`, `split_ngram_parts 128`, `ple_layer_ids [2]`, `ple_embed_dim 2560`, `ple_conv_kernel_size 4`[^qwen38-next-readme][^qwen38-next-config].
- MTP: `mtp_num_hidden_layers 1`, trained with multiple steps; `mtp.hybrid true`, `layer_types [full_attention]`, `rope_theta 10000000`, `mtp_use_dedicated_embeddings false`[^qwen38-next-readme][^qwen38-next-config].
- Context: `max_position_embeddings 262144` natively, extensible to `1000000`; M-RoPE `mrope_interleaved true`, `mrope_section [11,11,10]`, `partial_rotary_factor 0.25`, `rope_theta 10000000`[^qwen38-next-readme][^qwen38-next-config].
- Vision: depth `27`, hidden `1152`, intermediate `4304`, 16 heads, patch `16`, spatial merge `2`, temporal patch `2`, out hidden `2560`, positions `2304`; special ids image `248056`, video `248057`, vision-start `248053`, vision-end `248054`[^qwen38-next-config].
- Attention options: `attention_bias false`, `attention_dropout 0.0`, `output_gate_type sigmoid`, `hidden_act silu`, `rms_norm_eps 1e-06`[^qwen38-next-config].

## Transformers implementation

- Config classes: `Qwen4ExpTextConfig`, `Qwen4ExpVisionConfig`, `Qwen4ExpConfig`; text `model_type qwen4_exp_text` with `base_config_key text_config`; vision `model_type qwen4_exp_vision`[^qwen38-next-py-config][^qwen38-next-py-modular].
- `Qwen4ExpTextConfig` subclasses `Qwen3_5MoeTextConfig`; vision and top-level configs subclass the corresponding `Qwen3_5Moe` bases; modeling reuses Qwen3.5, Qwen3.5-MoE, and Qwen3-Next bases for rotary, norms, GDN, attention, experts, router, decoder, and vision blocks[^qwen38-next-py-modular].
- Modeling defines `Qwen4ExpTextGatedDeltaNet`, `Qwen4ExpTextQSAIndexer`, `Qwen4ExpTextAttention`, `Qwen4ExpTextExperts`, `Qwen4ExpTextTopKRouter`, `Qwen4ExpTextSparseMoeBlock`, `Qwen4ExpTextGatedResidual`, `Qwen4ExpTextNGramEmbedding`, `Qwen4ExpTextPLELayer`, `Qwen4ExpTextDecoderLayer`, plus `Qwen4ExpTextModel`, `Qwen4ExpForCausalLM`, vision `Qwen4ExpVisionModel`, and `Qwen4ExpForConditionalGeneration`[^qwen38-next-py-model][^qwen38-next-py-modular].
- Config-file defaults (`hidden 2048`, 40 layers, 16 heads, 256 experts) are base-class placeholders; the 125B checkpoint `config.json` values above override them — do not read the `.py` defaults as this checkpoint's specs[^qwen38-next-py-config][^qwen38-next-config].
- `__post_init__` maps checkpoint `full_attention` entries to `qwen_sparse_attention`; without explicit `layer_types` it derives them from `full_attention_interval`; `number_of_conv_states` is 3 with PLE else 1[^qwen38-next-py-config].
- Validation invariants: only `linear_attention` and `qwen_sparse_attention` allowed; output gate must be `sigmoid` or `silu`; `hc_count > 1`; MoE counts and intermediate sizes positive; QSA fields all-or-none, positive, `indexer_kv_heads == 1`, budget divisible by compress ratio, and attention RoPE dims must fit the index head; PLE ids must be one-indexed, on `linear_attention` layers only, with divisible `ple_embed_dim` and set `eos_token_id`[^qwen38-next-py-config].
- Parallel plans: TP plan covers expert gate/up/down, shared-expert projections, linear-attn in/out projections, QSA indexer projection, hyper-connection down projections, and PLE n-gram embedding; EP plan covers router plus grouped-GEMM experts; FSDP plan frees embeddings and layers while keeping the hyper-connection mixer[^qwen38-next-py-config][^qwen38-next-py-modular].
- PLE sharding note in code: embedding is about 45B or 90 GiB and must shard on dim 1 because checkpoints shard on dim 0; `split_ngram_parts` defaults to 512 with 128 in this checkpoint; loading concatenates shards and `save_pretrained` restores the sharded layout; `_no_placement_params` keeps the n-gram weight off automatic placement to avoid full-model offload OOM[^qwen38-next-py-config][^qwen38-next-py-model].
- QSA indexer: `token_budget 2048`, `compress_ratio 4`, `block_topk = budget // ratio`; complete blocks are mean-pooled and selected by top-k, then expanded back to token indices plus the incomplete tail; mask is overlaid on the full-attention causal mask for both prefill and decode paths[^qwen38-next-py-model][^qwen38-next-py-modular].
- N-gram hashing: deterministic per-layer multipliers from seed `1234` with prime vocab sizes per hashed head; shifted histories ignore EOS so padding does not create spurious n-grams; PLE projects concatenated n-gram embeddings to a shared value plus one key per residual stream[^qwen38-next-py-model][^qwen38-next-py-modular].

## Figures inspected

- `architecture.png` (2885×2930) shows the left spine from vocabulary embedding plus layer-2-only N-gram layer through repeated 3× GDN plus 1× QSA hybrid blocks to GR read, prediction head, and MTP modules; each GDN and QSA layer detail shows expanded residual branches with GR read for the sublayer input, GR write back to residual, and MoE after both token mixers[^qwen38-next-readme][^qwen38-next-blog].
- `Attention.png` (2246×1171) shows QSA as a compressed lightweight indexer feeding a sparse core attention: q path Linear plus zero-centered RMSNorm plus partial RoPE, k path Linear plus AvgPool plus zero-centered RMSNorm plus partial RoPE, Top-k Selector emitting top-k indices, then sparse q/k/v attention with sigmoid output gate; lower panels contrast a dense compressed mask with a micro-block sparse mask[^qwen38-next-readme][^qwen38-next-blog].

## Thinking controls and sampling

- Thinking is on by default with `<think>\n...\n</think>\n\n` before the final response; disable via `chat_template_kwargs {enable_thinking: False}` on generic OpenAI-compatible servers or via top-level `enable_thinking: False` on QwenCloud[^qwen38-next-readme].
- `reasoning_effort`: `xhigh` default, plus `medium` and `low`; source warns lower effort can increase total task latency and tokens via failures and retries in multi-turn agent work[^qwen38-next-readme][^qwen38-next-blog].
- `preserve_thinking` is on by default, retaining thinking blocks from all history for context continuity, decision consistency, less redundant reasoning, and better KV-cache use; set false to keep only the latest turn's thinking; QwenCloud takes the top-level key rather than the `chat_template_kwargs` wrapper[^qwen38-next-readme].
- Recommended sampling: thinking `temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, presence_penalty 0.0, repetition_penalty 1.0`; instruct `temperature 0.7, top_p 0.80, top_k 20, min_p 0.0, presence_penalty 1.5, repetition_penalty 1.0`; `presence_penalty` 0–2 may curb repetition with some language-mixing risk; framework support varies[^qwen38-next-readme].
- Agentic output budget within 1M: 262144 reasoning plus 131072 final-response tokens where the framework supports split limits[^qwen38-next-readme].

## Serving, YaRN, and long video

- Pointers only, not inspected: SGLang cookbook, vLLM recipe, and TokenSpeed recipe links in the card; plus KTransformers named as a serving-engine option alongside SGLang and vLLM[^qwen38-next-readme].
- Native 262144 context; beyond that use static YaRN with `rope_type yarn`, `factor 4.0`, `original_max_position_embeddings 262144`, retaining M-RoPE sections and theta; lower factor 2.0 is suggested when typical use is around 524288; static YaRN may hurt short-text quality so enable only when long context is needed[^qwen38-next-readme].
- Engine flags: `VLLM_ALLOW_LONG_MAX_MODEL_LEN=1` with `--hf-overrides` plus `--max-model-len 1000000` for vLLM; `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1` with `--json-model-override-args` plus `--context-length 1000000` for SGLang; `TOKENSPEED_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1` with `--hf-overrides` plus `--max-model-len 1000000` for TokenSpeed[^qwen38-next-readme].
- Video: released `video_preprocessor_config.json` `size` is conservative for text and image efficiency; for hour-scale video raise `longest_edge` to 469762048 (about 224K video tokens), e.g. `{"longest_edge": 469762048, "shortest_edge": 4096}`, or override at engine startup; vLLM-only per-request `fps` and frame-sampling notes live in the card[^qwen38-next-readme].

## Production API and agent integrations

- QwenCloud serves the production tuning as `qwen3.8-flash` over OpenAI-compatible Chat Completions and Responses plus an Anthropic-compatible interface; generic card examples use `model Qwen/Qwen3.8-Flash-Next` while cloud examples use `model qwen3.8-flash`[^qwen38-next-readme][^qwen38-next-blog].
- Integrations documented with configs: Claude Code via Anthropic protocol, Codex via Responses protocol with a local model-catalog entry (1M context, 95% effective, parallel tools, image input, 65536 max tokens), Qoder CLI, Qwen Code, OpenClaw with a `qwencloud/qwen3.8-flash` primary model entry, and QwenWork Standard mode as coming soon[^qwen38-next-blog].
- API coming-soon note applies to the cloud examples in the blog; treat endpoint availability as time-sensitive and verify before use[^qwen38-next-blog].

## Post-trained benchmark evidence

Source-reported post-trained tables vs Qwen3.8-27B, Qwen3.7-Plus (397B), DeepSeek-V4-Flash-0731, and Claude-Opus-4.6 Max; `--` means unavailable; bold was best-in-row in the source[^qwen38-next-readme][^qwen38-next-blog].

Language, Flash-Next first:

| Benchmark | Flash-Next | 27B | 3.7-Plus | DS-V4-Flash | Opus-4.6 Max |
| --- | --- | --- | --- | --- | --- |
| DeepSWE 1.1 | 58.7 | 42.2 | 16.5 | 54.4 | -- |
| SWE-bench Pro | 62.5 | 61.7 | 55.8 | 56.0 | 53.4 |
| SWE-bench Multilingual | 81.0 | 73.8 | 75.8 | -- | 77.5 |
| NL2Repo-Bench | 48.1 | 42.3 | 41.1 | 54.2 | 47.6 |
| CoWorkBench | 73.9 | 70.7 | 65.1 | 45.1 | 68.2 |
| JobBench | 55.7 | 33.4 | 27.6 | 41.3 | 36.6 |
| Agents Last Exam Pass@1 / Score | 24.3 / 51.2 | 20.4 / 42.9 | 13.2 / 33.6 | 25.2 / -- | -- |
| Toolathlon Verified Pass@1 | 73.5 | 67.1 | 50.6 | 70.3 | -- |
| IFBench | 81.3 | 79.5 | 79.1 | 79.2 | 62.5 |
| GPQA Diamond | 91.7 | 89.2 | 90.3 | 90.8 | 91.3 |
| HLE | 35.9 | 30.8 | 34.7 | 33.8 | 40.0 |
| LiveCodeBench v6 | 91.9 | 90.3 | 89.6 | 90.6 | 88.8 |

Vision-language, Flash-Next first:

| Benchmark | Flash-Next | 27B | 3.7-Plus | Opus-4.6 Max |
| --- | --- | --- | --- | --- |
| ClawEval-MM Pass@3 / Avg | 64.4 / 60.4 | 57.4 / 56.9 | 57.4 / 60.1 | 52.5 / 54.7 |
| RecreationBench | 49.9 | 47.1 | 30.2 | -- |
| AndroidWorld | 84.5 | 81.9 | 81.0 | 62.0 |
| OSWorld 2.0 Binary / Partial | 19.4 / 52.3 | 19.4 / 48.0 | 2.8 / 21.5 | -- |
| Vision2Web | 64.0 | 62.9 | 42.1 | -- |
| ERQA | 72.3 | 65.5 | 69.8 | 40.8 |
| LVBench | 76.6 | 72.4 | 76.2 | 63.0 |
| RealWorldQA | 88.5 | 85.9 | 86.9 | 73.9 |
| MathVision w/o CI / with CI | 90.6 / 95.7 | 90.0 / 94.6 | 90.3 / 88.7 | 65.5 / -- |
| CharXiv RQ w/o CI / with CI | 84.6 / 90.6 | 83.7 / 90.2 | 85.8 / 85.9 | 66.0 / -- |

Methodology notes: DeepSWE reports the better of Claude Code and mini-SWE-agent harnesses at temp 1.0, top_p 0.95, 256K; SWE-bench Pro uses Claude Code except published Opus score on a corrected task set with baselines re-evaluated; SWE-bench Multilingual uses mini-SWE-agent; NL2Repo disables repo-fetching bash to block reward hacking; CoWorkBench is an in-house long-horizon office suite; HLE is judged by GPT-4o; Vision2Web is Claude Code plus GPT-5.4 judging; MathVision had manual ground-truth fixes and a fixed boxed-answer prompt[^qwen38-next-readme][^qwen38-next-blog].

Efficiency claims from the blog: QSA attention kernel up to 7.6× prefill and 4.9× decode at 1M tokens; 8.6× prefill throughput vs Qwen3.7-Plus at 1M with 90% prefix-cache hit in an online-serving-like setup[^qwen38-next-blog].

Base-model 14-suite comparison (Flash-Next-Base vs 27B-Base vs 3.7-Plus-Base) is covered in [Qwen3.8-Flash-Next Architecture and Evaluation](qwen3.8-flash-next-architecture.md) and not duplicated here beyond noting the source claim of 8 of 14 wins at about 1/9 training cost vs Qwen3.7-Plus[^qwen38-next-blog].

## Relationships

- Related to [Qwen3.8-Flash-Next Architecture and Evaluation](qwen3.8-flash-next-architecture.md) — tech-report design, ablations, and base-model evaluation behind this HF checkpoint.
- Related to [Qwen3.8-Flash-Next Training and Stability](qwen3.8-flash-next-training.md) — Muon scope, scaling, warmup rejection, and stability evidence behind this checkpoint.
- Related to [SGLang Qwen3.8-Flash-Next Inference](sglang-qwen3.8-flash-next-inference.md) — day-0 SGLang realization with GDN/QSA kernels, Radix-Cache-compatible sparse KV, and IndexShare MTP.
- Related to [Qwen3.8-Flash-Next Local Deployment](qwen3.8-next.md) — Unsloth GGUF and llama.cpp local route for the same 125B-plus-51B identity.
- Related to [Qwen3.8-2.4T-A95B Architecture and Evaluation](qwen3.8-2.4t-a95b-architecture.md) — sibling Qwen3.8 flagship family with shared thinking-control and HF-release conventions.

## Coverage limits

- Images `architecture.png` and `Attention.png` were visually inspected for block and QSA structure; throughput and kernel-speedup plots referenced by URL in the blog were not inspected as local files.
- Serving cookbook, recipe, and managed-API links are recorded as pointers; launch commands and live endpoint status were not verified.
- Post-trained scores are source-reported snapshots with harness, temperature, context, and judging caveats above; do not treat narrow gaps as independently verified.
- No live credentials, private keys, tokens, PII, or disclosure markings found; code examples contain only placeholder keys and env-var names.

[^qwen38-next-readme]: Qwen3.8-Flash-Next HF model card — `../raw/Qwen3.8-Flash-Next/README.md`, highlights, model-overview dims, post-trained language and vision tables with methodology, serving pointers, thinking and sampling controls, output-length, YaRN, and video-preprocessor guidance.
[^qwen38-next-blog]: Qwen3.8-Flash-Next blog — `../raw/Qwen3.8-Flash-Next/blog.md`, Qwen4-preview framing, GDN/QSA plus gated-residual plus n-gram plus Muon narrative, 7.6×/4.9× and 8.6× efficiency claims, base-eval summary, QwenCloud pricing and Claude Code/Codex/Qoder/Qwen Code/OpenClaw/QwenWork integrations, and citations.
[^qwen38-next-config]: Qwen3.8-Flash-Next `config.json` — `../raw/Qwen3.8-Flash-Next/config.json`, `Qwen4ExpForConditionalGeneration` / `qwen4_exp` identity plus authoritative text, indexer, PLE, MTP, RoPE/M-RoPE, and vision dims.
[^qwen38-next-py-config]: `configuration_qwen4_exp.py` — `../raw/Qwen3.8-Flash-Next/configuration_qwen4_exp.py`, `Qwen4Exp` config classes, TP/EP/FSDP plans with PLE-sharding note, `full_attention`-to-QSA mapping, and architecture validation invariants.
[^qwen38-next-py-model]: `modeling_qwen4_exp.py` — `../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py`, QSA indexer and mask overlay, PLE hash and shift logic, GDN/attention/MoE/gated-residual/decoder/vision classes, and no-placement guard for the n-gram table.
[^qwen38-next-py-modular]: `modular_qwen4_exp.py` — `../raw/Qwen3.8-Flash-Next/modular_qwen4_exp.py`, Qwen3.5/MoE/Next base reuse, mirrored QSA/PLE/parallel-plan definitions, and checkpoint shard handling.

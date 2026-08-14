---
type: Concept
title: GLM-5 architecture, pre-training, and systems
description: GLM-5 is a 744B-total/40B-active MoE model combining MLA, DSA, shared-parameter multi-token prediction, Muon Split, 28.5T-token base training, and long-context systems co-design.
tags: [glm-5, mixture-of-experts, deepseek-sparse-attention, multi-head-latent-attention, pre-training, long-context]
status: stable
created: 2026-08-14
generated: { by: llm-wiki-agent/1, at: 2026-08-14T08:30:00Z }
sources:
  - id: glm5-report-2026
    resource: ../raw/arXiv-2602.15763v2/0_main.tex
    title: "GLM-5: from Vibe Coding to Agentic Engineering"
  - id: glm5-code-2026
    resource: ../raw/glm-moe/modular_glm_moe_dsa.py
    title: Hugging Face GLM-MoE-DSA modular implementation
---

# GLM-5 architecture, pre-training, and systems

GLM-5 is reported as a 744B-total/40B-active sparse MoE model trained for 28.5T base-model tokens. It combines 256 routed experts, MLA followed by DSA adaptation, Muon with per-head projection splitting, and shared-parameter sequential MTP; its training system targets memory pressure, expert communication, and 200K-scale sequences together rather than treating architecture independently of execution.[^glm5-report-2026]

## Backbone and sparse capacity

The appendix specifies hidden width 6,144, 78 backbone layers comprising 3 dense and 75 MoE layers, 256 routed experts plus one shared expert, top-8 routed selection, and 2,048 expert intermediate width. The released configuration independently exposes 78 layers, the same dense/MoE split, 256 routed experts, top-8 routing, one shared expert, a maximum position length of 202,752, a 154,880-token vocabulary, and a 12,288 dense-MLP intermediate width for the 3 leading dense layers; `norm_topk_prob` is enabled. With `n_group=1` and `topk_group=1`, the router's inherited expert-grouping machinery is present in code but a no-op at this configuration.[^glm5-report-2026][^glm5-code-2026]

The released router computes sigmoid expert affinities in float32, adds a learned correction bias only for top-k selection, normalizes the original selected affinities, scales the mixture weights by 2.5, and adds the always-on shared-expert output. This is implementation evidence for auxiliary-loss-free assignment control, not evidence that the released eager Python expert loop is the production distributed kernel. Expert weights are stored as 3D tensors (`gate_up_proj [E, 2*I, H]`, `down_proj [E, H, I]`) rather than per-expert module lists, and the configuration declares a `grouped_gemm` expert-parallel plan over them; the router bias buffer is kept strictly in float32.[^glm5-code-2026]

## MLA, DSA, and MTP changes

GLM-5 uses MLA with a 512-dimensional KV latent, 2,048-dimensional query latent, 64 attention heads, 192 non-positional Q/K dimensions, 64 rotary dimensions, and 256 value dimensions. The report’s Muon Split applies orthogonalization independently to per-head Q/K/V up-projection blocks; its listed ablation closes an observed gap between ordinary MLA and GQA-8. Reducing head count while increasing effective Q/K width is intended to lower decode dot-product work at constant reported parameter and prefill compute.[^glm5-report-2026][^glm5-code-2026]

DSA adaptation starts from the mid-training MLA checkpoint: a 1,000-step indexer warm-up is followed by 20B sparse-adaptation tokens. The released indexer forms weighted sums of ReLU query-key scores and selects up to 2,048 causal token positions; it projects queries from the shared MLA query latent (`q_lora_rank` → 32 heads × 128 head-dim), scores single-head keys, applies learned per-head weights through `weights_proj` (kept in float32), and maintains its own key cache alongside the attention KV cache. It uses interleaved RoPE and can reuse a prior full indexer layer's top-k indices on configured `shared` layers; the default schedule (`index_topk_freq=1`, `index_skip_topk_offset=2`) marks all 78 layers `"full"`, so sharing activates only when the released checkpoint overrides the pattern. Eager/SDPA converts the indices into a sparse additive mask, while compatible kernels consume indices directly; the modular file cites arXiv:2603.12201 for cross-layer top-k sharing.[^glm5-report-2026][^glm5-code-2026]

The modular file makes the architecture's lineage explicit: attention, RMSNorm, and interleaved-RoPE helpers are imported from the DeepSeek-V3 implementation, while the indexer, decoder layer, and model classes derive from DeepSeek-V3.2. The cross-layer `prev_topk_indices` propagation through the decoder loop is the file's marked "MAIN DIFF with DSV3.2". The implementation ignores unexpected `model.layers.78.*` checkpoint keys at load time, which is consistent with the report's shared-parameter MTP module sitting at index 78 in the checkpoint while the executable backbone stays at 78 layers (0–77).[^glm5-code-2026]

For speculative drafting, three sequential MTP depths share parameters during training, keeping draft parameter memory comparable to a single MTP layer. On a private prompt set with four speculative steps, the report gives mean accepted length 2.76 versus 2.55 for DeepSeek-V3.2; workload and latency are undisclosed.[^glm5-report-2026]

## Data and context schedule

General pre-training emphasizes web, code, and math/science filtering. Mid-training then extends context through 32K over 1T tokens, 128K over 500B, and 200K over 50B. Its software-engineering mixture includes repository files, issues, PRs, diffs, and relevant-file retrieval; the report claims about 10M issue-PR pairs and 160B unique issue-PR tokens after filtering.[^glm5-report-2026]

## Training-system co-design

Reported controls include pipeline-aware MTP placement, ZeRO-2-style gradient sharding with two rolling full buffers, shard-local overlapped Muon all-gathers, layer-granular activation offload, sequence-chunked output projection/loss, deferred weight-gradient work, variable context-parallel groups, and hierarchical all-to-all for long sequences. INT4 quantization-aware training is applied during SFT with a kernel intended to make training and offline quantization bitwise identical.[^glm5-report-2026]

## Contradictions

- The architecture prose says GLM-5 reduces its layer count to **80**, while the appendix gives 3 dense + 75 MoE = **78 backbone layers**, and the released configuration sets `num_hidden_layers=78`. This page uses 78 for the executable backbone and leaves “80” as an unresolved report inconsistency rather than inferring whether auxiliary modules were counted.[^glm5-report-2026][^glm5-code-2026]
- The report presents a 192-to-256 attention head-dimension change, while its appendix labels “QK Head Dim” as 192. The code resolves its own implementation as 192 non-RoPE + 64 RoPE = 256 Q/K dimensions, but this does not prove the appendix’s intended labeling.[^glm5-report-2026][^glm5-code-2026]

## Relationships

- **Uses:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md) over [Multi-head Latent Attention](multi-head-latent-attention.md).[^glm5-report-2026][^glm5-code-2026]
- **Uses:** [Auxiliary-loss-free MoE load balancing](auxiliary-loss-free-moe-load-balancing.md) and [Sequential multi-token prediction](sequential-multi-token-prediction.md).[^glm5-code-2026][^glm5-report-2026]
- **Uses:** [Muon orthogonalized-momentum optimizer](muon-orthogonalized-momentum-optimizer.md) with per-head projection splitting.[^glm5-report-2026]
- **Followed by:** [GLM-5 post-training and asynchronous agentic RL](glm-5-post-training-and-asynchronous-agentic-rl.md).

## Evidence limits

The training scales, performance parity, memory savings, and systems benefits are author-reported and lack end-to-end controlled ablations. The bundled code is a Hugging Face implementation, not the training stack or optimized production kernels; it omits MTP and the paper's distributed infrastructure. Cross-layer DSA top-k sharing appears in code but is not described in this report, so it should not be attributed to the reported training run without additional evidence; the code cites arXiv:2603.12201 for it, but that report is not in `raw/`. The code does not demonstrate that the released checkpoint actually enables `"shared"` indexer layers, since the derived default marks every layer `"full"`. The generated configuration file also contains an unreachable second `mlp_layer_types` default in `__post_init__` ("dense + rest sparse" written after a 3-dense default has always been assigned), a generation artifact rather than a modeling decision.[^glm5-report-2026][^glm5-code-2026]

[^glm5-report-2026]: GLM-5 Team, “GLM-5: from Vibe Coding to Agentic Engineering,” arXiv:2602.15763v2, [main source](../raw/arXiv-2602.15763v2/0_main.tex), [pre-training and systems](../raw/arXiv-2602.15763v2/2_pretrain.tex), and [architecture appendix](../raw/arXiv-2602.15763v2/9_appendix.tex).

[^glm5-code-2026]: Hugging Face, “GLM-MoE-DSA modular implementation,” [source](../raw/glm-moe/modular_glm_moe_dsa.py), configuration, indexer, attention, router, MoE, decoder, and model classes; cross-checked against the generated [configuration](../raw/glm-moe/configuration_glm_moe_dsa.py) and [modeling module](../raw/glm-moe/modeling_glm_moe_dsa.py).

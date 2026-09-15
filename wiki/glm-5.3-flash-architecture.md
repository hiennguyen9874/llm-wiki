---
type: Concept
title: GLM-5.3-Flash Architecture and Evaluation
description: Z.ai 320B (18B active) natively multimodal hybrid linear-sparse MoE model with mHC, IndexPool, 1M context, and Flash-cost evaluation and serving evidence.
tags: [glm, z-ai, multimodal, moe, sparse-attention, linear-attention, hyper-connections, efficiency, evaluation, serving]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: flash-readme
    resource: ../raw/GLM-5.3-Flash/README.md
    title: GLM-5.3-Flash model card
  - id: flash-blog
    resource: ../raw/GLM-5.3-Flash/blog.md
    title: GLM-5.3-Flash blog (2026-08-26)
  - id: flash-config
    resource: ../raw/GLM-5.3-Flash/config.json
    title: GLM-5.3-Flash config.json
  - id: flash-arch
    resource: ../raw/GLM-5.3-Flash/architecture.webp
    title: GLM-5.3-Flash architecture diagram
  - id: flash-bench
    resource: ../raw/GLM-5.3-Flash/benchmark.png
    title: GLM-5.3-Flash LLM Performance Evaluation chart
---

GLM-5.3-Flash is Z.ai's 320B-parameter (18B active) natively multimodal open model, the first multimodal model in the GLM-5 series, built on a newly trained base with hybrid linear plus sparse attention and Manifold-Constrained Hyper-Connections (mHC) for Flash-cost long-context inference[^flash-readme][^flash-blog].

## Model identity and release

- First natively multimodal model in the GLM-5 series; 320B total / 18B active; newly trained base with architecture and training recipe redesigned around capability and efficiency[^flash-readme][^flash-blog].
- Positioned as outperforming GLM-5.2 across benchmarks and real-world workloads at one-tenth the price, while approaching Claude Opus 4.8 on coding and agentic benchmarks[^flash-readme].
- Released 2026-08-26; tested anonymously before release as `ox-alpha` on OpenCode and OpenRouter, where it became the most popular model of the week with traffic served on Chinese AI chips[^flash-blog].
- Weights: `zai-org/GLM-5.3-Flash` on Hugging Face; `transformers` library, `text-generation` pipeline, MIT license[^flash-readme][^flash-blog].
- Technical report: `GLM-5: from Vibe Coding to Agentic Engineering`, arXiv `2602.15763`[^flash-readme].
- For community GGUF/llama.cpp run paths, see [GLM-5.3-Flash Local Deployment](glm-5.3-flash.md).

## Text backbone and MoE

- 45 hidden layers, hidden size 4096, intermediate size 12288, 64 attention heads, vocab 154880, `max_position_embeddings` 1048576 (1M context)[^flash-config].
- MoE: 288 routed experts plus 1 shared expert, 8 experts per token, `moe_intermediate_size` 2048, `scoring_func` sigmoid, `topk_method` noaux_tc, `norm_topk_prob` true, `routed_scaling_factor` 2.5, `router_aux_loss_coef` 0.001[^flash-config].
- MLA-style projections: `kv_lora_rank` 512, `q_lora_rank` 1536, `qk_head_dim` 256 with `qk_rope_head_dim` 0 and `qk_nope_head_dim` 256, `v_head_dim` 256, `mla_use_nope` true[^flash-config].
- One MTP layer (`num_nextn_predict_layers` 1); diagram shows an MTP Layer alongside the LM Head above the mHC-wrapped stack[^flash-config][^flash-arch].
- Compared with the GLM-4.5 series: similar total parameters (320B vs. 355B) with nearly halved active parameters (18B vs. 32B) and layers (45 vs. 92)[^flash-blog].

## Hybrid linear plus sparse attention with IndexPool

- Per-layer schedule: 34 `linear_attention` layers plus 11 `deepseek_sparse_attention` layers in a repeating 3-linear plus 1-sparse pattern at layers 3, 7, 11, 15, 19, 23, 27, 31, 35, 39, and 43, with `first_k_dense_replace` 3[^flash-config].
- Linear attention captures local dependencies through state modeling (64 heads, head dim 128, short-conv kernel 4, gate lower bound -5.0); sparse attention retrieves relevant global context through a lightweight indexer[^flash-blog][^flash-config].
- DSA indexer: `index_topk` 2048, `index_head_dim` 128, `index_n_heads` 32; checkpoint sets all 45 `indexer_types` to `full`[^flash-config].
- IndexPool compresses four indexer key vectors into one through weighted pooling to reduce indexer latency and memory at 1M context; diagram shows Indexer Keys through 4x Pooling into an Indexer Cache, then Indexer, TopK, and KV Block Selection feeding Sparse Attention[^flash-blog][^flash-arch].

## Hyper-connections and multimodal input

- `mhc` true with `hc_mult` 4, `hc_eps` 1e-06, and `hc_sinkhorn_iters` 20; mHC is described as improving scaling efficiency[^flash-config][^flash-readme].
- Diagram shows mHC blocks wrapping both the linear-attention and sparse-attention plus MoE stages, with ViT image and text embedding inputs entering the bottom mHC stage[^flash-arch].
- Native vision encoder: depth 24, hidden size 1024, output hidden size 4096, image size 448, patch size 14, `spatial_merge_size` 2, `temporal_patch_size` 2, projection intermediate size 10240[^flash-config].
- Special tokens: image token 154854, video token 154855, image start/end 154830/154831, video start/end 154832/154833[^flash-config].

## Efficiency and cost-performance

- Per-head per-layer attention compute and average per-layer KV cache (BF16) are reduced by about 3.0x and 4.4x versus GLM-5.3; the architecture diagram labels 3.01x compute and 4.44x KV-cache gaps at 1M tokens[^flash-blog][^flash-arch].
- Lowest attention compute among the compared models (GLM-5.3, DeepSeek-V4-Flash, Kimi-K3); KV cache is still slightly larger than Kimi-K3 and DeepSeek-V4-Flash[^flash-blog].
- Artificial Analysis Intelligence Index v4.1.1: score 57 at $0.045 per task discounted, described as intelligence previously available at roughly 10x the cost[^flash-blog].

## Pre-training and base evaluation

- Latest 30T-token multimodal pre-training corpus combined with the efficiency architecture to deliver more intelligence with less compute[^flash-readme][^flash-blog].
- Base-model comparison (Flash-Base vs. GLM-4.5-Base, GLM-5-Base, DeepSeek-V4-Flash-Base; DeepSeek numbers re-evaluated internally)[^flash-blog]:

| Benchmark | GLM-4.5-Base | GLM-5-Base | DeepSeek-V4-Flash-Base | GLM-5.3-Flash-Base |
| --- | --- | --- | --- | --- |
| Activated / Total | 32B / 355B | 40B / 744B | 13B / 284B | 18B / 320B |
| MMLU | 86.1 | 88.3 | 88.5 | 88.1 |
| BBH | 86.2 | 87.4 | 84.9 | 86.6 |
| HellaSwag | 87.1 | 88.1 | 85.3 | 87.1 |
| LiveCodeBench-Base | 28.1 | 34.4 | 29.9 | 37.6 |
| SimpleQA | 30.0 | 36.0 | 31.2 | 33.5 |

- Vendor summary: Flash-Base outperforms GLM-4.5-Base overall and stays competitive with GLM-5-Base on most benchmarks[^flash-blog].

## Official evaluation and methodology

Selected Flash scores; full table also compares GLM-5.2, DeepSeek-V4-Vision-Exp, Opus 4.8, GPT-5.6 Terra, and Gemini 3.7 Flash[^flash-blog][^flash-bench]:

- Coding: Terminal-Bench 2.1 84.3; DeepSWE v1.1 63.4; NL2Repo 56.3.
- Agentic: Toolathlon Verified 78.4; AutomationBench v1.0.6 48.8; Agents' Last Exam 26.3; HLE w/ Tools 55.3; GDPval-AA v2 1773.
- Vision: OfficeQA Pro 62.4; CharXiv Reasoning w/ Tools 89.4; Chartography w/ Tools 78.0; BabyVision 53.4; MVBench 77.8; MMVU 80.5.
- Z.ai Code Bench v1.0 on Claude Code 2.1.207: outperforms GLM-5.2 at every effort level and nearly matches Claude Opus 4.8 at max effort (29.0 vs. 29.5)[^flash-blog].

Reported evaluation settings include: HLE w/ Tools at temperature 1.0 / top_p 0.95, 163840 max generation tokens, 300000 context with context management, GPT-5.6-luna (medium) judge; NL2Repo at temperature 1.0 / top_p 1.0 / 64K new tokens under 1M context with rule plus LLM anti-hacking checks; DeepSWE via mini-swe-agent at temperature 0.95 / top_p 1.0, 6h timeout, 400K context; Terminal-Bench 2.1 in Claude Code 2.1.207 at temperature 1.0 / top_p 1 / 65536 new tokens, 6h timeout; ALE via Claude Code harness at max reasoning effort, 1M context, 64K output, Tool Search disabled; Toolathlon Verified as pass@1 over 3 runs; AutomationBench v1.0.6 with the `null`-type fix; GDPval-AA v2 by Artificial Analysis; and vision suites at temperature 1.0 / top_p 0.95 with suite-specific context lengths and image/video handling[^flash-readme][^flash-blog].

## Visual intelligence

- Vision is natively integrated so the model can decide when to observe and use visual feedback to guide actions; code builds and changes the world while vision lets the model enter the world people see and use[^flash-blog].
- Visual-coding data synthesis targets self-visual judgment and test-time improvement: trajectories require interacting with environments, inspecting outputs, and refining iteratively; frontend work adds RL with environment feedback plus agent-based GUI verification grounded in real user flows[^flash-blog].
- Professional-work claim: joint reasoning over textual, visual, and structural context (documents, spreadsheets, presentations, dashboards, interfaces, meeting artifacts) with self-verification against visual context, including presentation quality and aesthetics[^flash-blog].

## Serving at scale and access

- Local/server frameworks listed: SGLang (cookbook), vLLM (recipes), TokenSpeed, and KTransformers (tutorial)[^flash-readme].
- Large-scale Chinese-AI-chip cluster with high-bandwidth interconnect and a dedicated SGLang-based inference engine; a GLM-5.3-powered infrastructure agent assisted kernel development, bottleneck diagnosis, and serving-stack improvements[^flash-blog].
- Memory stack for 1M context on bandwidth- and capacity-constrained chips: intra-node tensor parallelism for Linear Attention and LM head, ReplaySSM, W8A8 quantization, hybrid INT8/FP8/BF16 cache quantization, and Layer Split[^flash-blog].
- Production Encode-Prefill-Decode (EPD) disaggregation separates multimodal encoding, prefill, and decoding into independently scheduled worker pools across tens of thousands of domestic accelerators; reported 3x end-to-end gain over the same-hardware baseline, reaching hardware efficiency and per-token cost comparable to mainstream NVIDIA GPUs[^flash-blog].
- Product access: Z.ai API Platform, GLM Coding Plan with 3x usable quota versus GLM-5.3, and ZCode with Browser Use and Computer Use for click-through visual verification and desktop-app operation[^flash-readme][^flash-blog].

## Relationships

- Uses [SGLang EPD Disaggregation](sglang-epd-disaggregation.md) — production Encode-Prefill-Decode worker separation for multimodal encoding, prefill, and decode scaling.
- Related to [GLM-5.3-Flash Local Deployment](glm-5.3-flash.md) — community Unsloth GGUF plus llama.cpp/Unsloth Desktop run paths for this checkpoint.
- Related to [GLM-5.3 Local Deployment](glm-5.3.md) — larger 744B (40B active) GLM-5.3 sibling; Flash is the smaller newly trained 320B (18B active) counterpart.
- Related to [vLLM HiSparse Local KV Offload](vllm-hisparse.md) — hybrid sparse-attention KV residency and shared-pool context relevant to Flash-class DSA serving.

## Coverage limits

- Remote blog/CDN images, benchmark plots, linked cookbooks/recipes/tutorials, API docs, community links, and the arXiv technical report were not independently inspected; all benchmark, cost, and serving-performance numbers are vendor-reported, not independently verified.
- Transformers implementation files (`modeling_glm5_next.py`, `modular_glm5_next.py`, `processing_glm5_next.py`, image/video processing) were enumerated but not fully compiled; architectural detail here comes from the model card, blog, config, and the two inspected local images.
- No credentials, private keys, tokens, or PII were found in the inspected model card, blog, config, and image files.

[^flash-readme]: GLM-5.3-Flash model card — `../raw/GLM-5.3-Flash/README.md`, first natively multimodal GLM-5 model, 320B/18B identity, newly trained base with sparse plus linear attention and mHC, 30T-token corpus, 1/10th price and near-Opus coding/agentic positioning, SGLang/vLLM/TokenSpeed/KTransformers serving list, evaluation footnotes, and `2602.15763` citation.
[^flash-blog]: GLM-5.3-Flash blog (2026-08-26) — `../raw/GLM-5.3-Flash/blog.md`, `ox-alpha` anonymous test, 45-vs-92-layer and 18B-vs-32B comparison, linear-local plus indexer-global attention with 4x IndexPool, 3.0x/4.4x efficiency, AA Index 57 at $0.045/task, base and full benchmark tables, Z.ai Code Bench 29.0 vs. 29.5, visual-coding and professional-workflows narrative, Chinese-chip EPD/ReplaySSM/W8A8 serving stack with 3x gain, and Coding Plan/ZCode/Hugging Face access.
[^flash-config]: GLM-5.3-Flash config — `../raw/GLM-5.3-Flash/config.json`, 45 layers, hidden 4096, vocab 154880, 1M max positions, 288+1 MoE with 8 active, MLA LoRA ranks and head dims, 34 linear plus 11 DSA layers at every fourth layer, indexer top-k/head/pool settings, mHC and single-MTP-layer flags, and 24-layer 1024-hidden vision encoder with image/video token IDs.
[^flash-arch]: GLM-5.3-Flash architecture diagram — `../raw/GLM-5.3-Flash/architecture.webp`, mHC-wrapped linear/sparse plus MoE stack with MTP head, ViT plus embedding inputs, Indexer/TopK/KV-block-selection flow with 4x pooling, and 4.44x KV-cache plus 3.01x compute annotations at 1M.
[^flash-bench]: LLM Performance Evaluation chart — `../raw/GLM-5.3-Flash/benchmark.png`, six-benchmark bar comparison (Terminal Bench 2.1, DeepSWE v1.1, Agents' Last Exam, AutomationBench, HLE w/ Tools, GDPVal-AA v2) corroborating the blog table values.

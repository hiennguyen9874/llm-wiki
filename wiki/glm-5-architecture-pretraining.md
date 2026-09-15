---
type: Concept
title: GLM-5 Architecture and Pre-training
description: 744B/40B MoE with MLA-256 plus Muon Split, shared MTP, DSA continued pre-training, 28.5T-token data, and memory-parallel training systems.
tags: [glm-5, z-ai, moe, mla, muon, mtp, dsa, sparse-attention, pretraining, mid-training, qat]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: glm5-intro
    resource: ../raw/arXiv-2602.15763v2/1_intro.tex
    title: GLM-5 Introduction — pipeline, scale, and DSA/async-RL claims
  - id: glm5-pretrain
    resource: ../raw/arXiv-2602.15763v2/2_pretrain.tex
    title: GLM-5 Pre-Training — architecture, data, mid-training, infrastructure
  - id: glm5-appendix
    resource: ../raw/arXiv-2602.15763v2/9_appendix.tex
    title: GLM-5 Appendix — architecture table, base benchmarks, hyperparameters
---

GLM-5 is Z.ai's 744B-parameter (40B active) MoE flagship for agentic engineering, trained on ~28.5T base tokens with MLA-256 plus Muon Split, shared multi-token prediction, and DeepSeek Sparse Attention continued pre-training to cut long-context cost without losing quality[^glm5-intro][^glm5-pretrain].

## Model scale

- 256 experts, 80-layer-class depth tradeoff to cut expert-parallel communication: 744B total / 40B active vs GLM-4.5 355B / 32B[^glm5-pretrain].
- Appendix architecture (parameters count MTP but exclude embeddings/output): 3 dense + 75 MoE + 1 MTP layers vs GLM-4.5 3 + 89 + 1; hidden 6144 vs 5120; dense intermediate 12288; MoE intermediate 2048 vs 1536; vocab 154880 vs 151552; 256 total / 8 routed / 1 shared experts vs 160 / 8 / 1[^glm5-appendix].
- Attention config shift: QK head dim 192 vs 128; V head dim 256 vs 128; Q LoRA 2048 and KV LoRA 512 (absent in GLM-4.5); 64 heads vs 96; 8 KV heads removed for MLA; 32 indexer heads with head dim 128 for DSA[^glm5-appendix].
- Training budget: ~27T-token initial corpus plus extended mid-training totals ~28.5T base tokens; context 4K to 200K in mid-training and 202,752 in SFT[^glm5-intro][^glm5-pretrain].

## MLA plus Muon Split and MLA-256

- MLA uses reduced KV vectors to match GQA quality with lower memory and faster long-context processing, but 576-dim latent KV under standard Muon trailed GQA-8 (2048-dim KV)[^glm5-pretrain].
- Muon Split splits up-projections `W^UQ/W^UK/W^UV` per head before orthogonalization so heads update at different scales; reported table restores MLA to GQA-8 level (e.g. MMLU 62.5 vs 61.2, C-Eval 62.1 vs 60.0, RACE 79.9 vs 79.6) and keeps attention logits stable without clipping[^glm5-pretrain].
- MLA-256 raises head dim 192 to 256 while cutting head count by one-third: constant training compute/parameters but lower decode dot-product cost than 576-dim MLA (vs 128-dim GQA decode), with matched quality under Muon Split[^glm5-pretrain].

## Shared multi-token prediction

- Standard MTP needs `n` layers for `n` future tokens, scaling parameter and KV memory linearly; DeepSeek-V3 trains one MTP layer yet predicts two tokens at inference, hurting second-token acceptance[^glm5-pretrain].
- GLM-5 shares parameters across 3 MTP layers in training, holding draft memory near DeepSeek-V3 while improving acceptance; reported accept length 2.76 vs DeepSeek-V3.2 2.55 at 4 speculative steps on a private prompt set[^glm5-pretrain].

## DSA continued pre-training

- DSA replaces dense `O(L^2)` attention with content-based Top-K selection; two-stage dense warm-up plus sparse adaptation avoids from-scratch cost on the claim that ~90% of long-context attention entries are redundant[^glm5-pretrain].
- GLM-5 recipe: warm-up 1,000 steps of 14 sequences × 202,752 tokens at max LR 5e-3, then 20B-token sparse adaptation with mid-training data/hyperparameters — far smaller than DeepSeek-V3.2's 943.7B yet reported sufficient to tie MLA[^glm5-pretrain].
- Reported long-context tie: MQ-NIAH-128K 100.0/100.0; MV-NIAH 95.5 MLA vs 97.0 DSA; SQuAD-128K 79.7 vs 86.0; HotpotQA-128K 66.3 vs 63.0; same-SFT loss/eval tie and ~1.5–2× attention saving, framed as 128K reasoning agents at half GPU cost[^glm5-pretrain].

## Efficient-attention ablations

- GLM-9B (40-layer, 128K) baselines: fixed SWA interleave and Gated DeltaNet linear attention; proposals are search-based SWA layer selection and minimalist SimpleGDN reusing QKV without Conv1d/gating[^glm5-pretrain].
- Search uses beam 8, two layers per step (~10 steps for 40 layers), RULER-16K objective; discovered pattern `SFSSFFSSSFFFFSSFSFFFFFFSFSFSSFSSFSFSSFSSS` generalizes from 16K to 128K and beats interleave (e.g. RULER-16K 88.92 vs 25.89 without extra training)[^glm5-pretrain].
- After 190B-token 64K continual training at 1:1 efficient/full ratio: interleave collapses (RULER-128K −30.35, RepoQA-128K −26.50); search narrows gap (−5.69/−14.66); GDN −11.28/−9.66; SimpleGDN best balance (−8.25/−7.33) and sole HELMET-ICL gain (+2.12 at 64K, +4.48 at 128K)[^glm5-pretrain].
- DSA contrast: described as lossless by construction via lightning indexer token sparsity applicable to all layers; GLM-4.7-Flash + DSA warm-up-only (indexer-only, 1K steps, batch 16, frozen base) drops 128K RULER 79.21 to 71.35, while full 150B joint training beats baseline at 16K/32K/64K (+0.86/+0.49/+1.72) with only −0.35 at 128K[^glm5-pretrain].

## Pre-training data

- Web: GLM-4.5 pipeline plus sentence-embedding DCLM classifier for extra high-quality data and Wikipedia/LLM-optimized World Knowledge classifier to mine long-tail medium-low-quality data[^glm5-pretrain].
- Code: refreshed host snapshots plus code-bearing web pages (+28% fuzzy-deduped unique tokens); fixed Software Heritage metadata alignment and language classification; quality-aware sampling retained; added low-resource classifiers (e.g. Scala, Swift, Lua)[^glm5-pretrain].
- Math/science: refined webpage extraction and book/paper PDF parsing; LLM educational-value scoring with chunk-and-aggregate for long docs; strict exclusion of synthetic/AI-generated/template data[^glm5-pretrain].

## Mid-training

- Three stages: 32K (1T tokens), 128K (500B), 200K (50B); 200K stage added over GLM-4.5's 128K max for ultra-long documents and multi-file codebases, with long-document and synthetic agent-trajectory upsampling late[^glm5-pretrain].
- Software engineering: concatenated repo files, diffs, issues, PRs, retrieved context; relaxed repo filter plus stricter issue filter yields ~10M issue-PR pairs and ~160B unique issue-PR tokens with richer per-issue file sets[^glm5-pretrain].
- Long-context mixture: filtered natural books/papers plus NextLong/EntropyLong-inspired synthetic interleaved packing against lost-in-the-middle; 200K-stage MRCR-like multi-turn recall variants; reported diversity and 200K-stage gains transfer even back to 128K performance[^glm5-pretrain].

## Training infrastructure

- Memory: flexible MTP placement (shared output on final pipeline stage, embedding/transformer on prior stage); pipeline ZeRO-2 gradient sharding to `1/dp` plus two-buffer rolling accumulation; shard-only Muon all-gather overlapped with compute; layer-granular pipeline activation offload to host plus recomputation avoiding P2P/MoE contention; sequence-chunked output projection plus loss[^glm5-pretrain].
- Parallelism: deferred critical-path weight-gradient compute with bounded storage/overlap; workload-aware reordering, dynamic attention redistribution, flexible context-parallel group sizing; hierarchical all-to-all overlapping intra/inter-node QKV traffic[^glm5-pretrain].
- Low precision: INT4 quantization-aware training in SFT with a unified train/offline kernel claimed bitwise-identical between training and inference; LR schedule warms 0 to 2e-4 then cosine to 4e-5 pre-training, linear 4e-5 to 1e-5 mid-training, DSA warm-up 5e-3 to 2e-4 and sparse adaptation constant 1e-5[^glm5-pretrain][^glm5-appendix].

## Relationships

- Uses [LongCat Sparse Attention](longcat-sparse-attention.md) — DSA-derived indexing/offload context for interpreting GLM-5's lossless-sparsity and indexer-stability claims.
- Uses [vLLM IndexCache for DeepSeek Sparse Attention](vllm-index-cache.md) — cross-layer Top-K reuse contrast for GLM-5's large-`k=2048` storage concern.
- Related to [GLM-5.3 Local Deployment](glm-5.3.md) — same 744B/40B size class; GLM-5 report is the architectural predecessor, not the GLM-5.3 deployment artifact.
- Related to [GLM-5.3-Flash Architecture and Evaluation](glm-5.3-flash-architecture.md) — Flash-Base vs GLM-5-Base table reuses GLM-5 base numbers summarized here.

## Coverage limits

- Figures (`loss_v2.pdf`, pipeline, arena/AA/Vending plots) and `ref.bib` were enumerated but not used as quantitative evidence beyond tex-stated numbers.
- Accept-length and DSA SFT-tie claims rest on private prompt sets and internal SFT data not inspectable here.

[^glm5-intro]: Introduction — `../raw/arXiv-2602.15763v2/1_intro.tex`, ARC-from-GLM-4.5 framing, 27T-to-28.5T plus 744B/DSA/async-RL/domestic-chip summary, 4K-to-200K pipeline figure reference, and AA/LMArena/Vending/CC-Bench headline results.
[^glm5-pretrain]: Pre-training — `../raw/arXiv-2602.15763v2/2_pretrain.tex`, 256-expert/80-layer and 744B/40B scaling, GQA-8 vs MLA/Muon-Split/MLA-256 table, 3-layer shared MTP accept-length table, DSA warm-up/adaptation plus long-context table, GLM-9B SWA/GDN/SimpleGDN and GLM-4.7-Flash DSA RULER tables, web/code/math data, 32K/128K/200K plus 10M-pair/160B-token mid-training, and memory/parallelism/INT4-QAT systems.
[^glm5-appendix]: Appendix — `../raw/arXiv-2602.15763v2/9_appendix.tex`, GLM-4.5 vs GLM-5 architecture table with MTP-inclusive/embedding-exclusive counting, base-benchmark table, and pre/mid/DSA learning-rate schedules.

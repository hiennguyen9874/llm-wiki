---
type: Concept
title: MoE-ViE mixture-of-experts vision encoder
description: A CLIP-style vision encoder that uses fine-grained routed and shared experts, custom MoE kernels, and video fine-tuning designed to retain image transfer.
tags: [vision-language-models, vision-encoders, mixture-of-experts, contrastive-learning, video-understanding, efficient-inference]
status: draft
created: 2026-08-20
generated: { by: llm-wiki-agent/1, at: 2026-08-20T10:14:19Z }
sources:
  - id: zhang-2026-moe-vie
    resource: ../raw/2608.17402_MoE-ViE/main.tex
    title: "MoE-ViE: Mixture of Experts Vision Encoder for Efficient Image and Video Understanding"
---

# MoE-ViE mixture-of-experts vision encoder

MoE-ViE is a CLIP-style image and video encoder family that sparsely scales the vision tower rather than the text tower. It replaces most vision-transformer FFNs with fine-grained MoE blocks, pairs them with an optimized Triton implementation, and uses frame-level distillation plus selective freezing during video fine-tuning. The supplied manuscript reports strong zero-shot image, video, and vision-to-LLM results at a lower activated-parameter count than selected dense encoders; all performance and latency claims remain author-reported and setup-specific.[^zhang-2026-moe-vie]

## Architecture and training

- **Fine-grained sparse vision tower:** Every vision MLP except the first transformer block is replaced by an MoE layer; the text tower stays dense during image-text pretraining. Each reported model uses 32 experts, each with one quarter of the corresponding dense-MLP hidden width. One shared expert is always active, while a top-4 (B/L) or top-8 (H) subset of routed experts is activated per token. Selected sigmoid router scores are renormalized before mixture; the shared path supplies a persistent global transformation.[^zhang-2026-moe-vie]
- **Loss-free routing control:** The router selects experts from sigmoid scores plus per-expert bias. Instead of an auxiliary balancing loss, the source updates each bias from the z-scored deviation of its observed token load, which the authors report outperformed the compared importance/load, entropy, and sign-update loss-free variants in their B/32 ablation.[^zhang-2026-moe-vie]
- **Encoder details:** The implementation is based on OpenCLIP, removes the class token in favor of attention pooling, uses 2D RoPE in the vision tower, and uses SwiGLU FFNs. The reported H/14 encoder has 3.5B total and 1.1B activated parameters; its B/16 and L/16 variants have 0.5B/0.1B and 1.7B/0.3B total/activated parameters, respectively.[^zhang-2026-moe-vie]
- **Image then video training:** Image-text contrastive pretraining uses 2B MetaCLIP pairs and 1.5B proprietary pairs, progressively increasing resolution. During video fine-tuning, a frozen image-pretrained teacher supplies a cosine frame-logit distillation loss; the student freezes vision MoE experts and text-tower MLPs. The authors’ ablations report that this combination retained ImageNet-1K accuracy better than naive video fine-tuning or image/video mixing while improving K400.[^zhang-2026-moe-vie]

## Kernel co-design

The source attributes naive MoE latency to small per-expert GEMMs, routing-related synchronization, and intermediate-memory traffic. Its Triton implementation uses GPU-side routing preparation and jagged grouped GEMM, then fuses gate/up projection with SwiGLU and down projection with routing-weighted scatter-add. The authors report that this moves inference from a Python expert loop to two custom kernel launches; the training kernel keeps the activation separate for flexibility.[^zhang-2026-moe-vie]

For MoE-ViE-H/14 at 576 input tokens, the reported optimized-versus-vanilla latencies are 82.59 vs. 318.76 ms (batch 16), 145.82 vs. 448.93 (32), 276.87 vs. 740.84 (64), and 544.96 vs. 1306.81 (128). The same table places the optimized encoder near the 1.1B-active-parameter SigLIP2-g-opt and at roughly 76% of the latency of the 1.9B-active-parameter PEcoreG/14; differences in patch size are controlled only by matching token count.[^zhang-2026-moe-vie]

## Reported evidence

- On the reported zero-shot image table, B/16 and L/16 lead their selected comparable-scale entries on the stated classification and retrieval averages. H/14 reports stronger fine-grained-classification and OCR averages than PEcoreG/14 (83.9 vs. 83.8 and 80.4 vs. 79.1), but lower general image-classification and retrieval averages (88.3 vs. 88.6 and 78.2 vs. 78.9).[^zhang-2026-moe-vie]
- On the reported zero-shot video table, H/14 has a 76.5 classification average and 50.6 retrieval average, compared with PEcoreG/14's 76.0 and 50.6. The comparison varies in resolution and patch size, despite both having 448-pixel inputs.[^zhang-2026-moe-vie]
- When the H/14 encoder is aligned with either Llama 3.1 Instruct 8B or Qwen 2.5 VL 7B through the manuscript's three-stage pipeline, it has the highest reported selected image and video averages among the table entries, but not the highest captioning average. The expanded Llama alignment run reports 81.3 image, 63.1 video, and 132.6 captioning averages after 42M samples.[^zhang-2026-moe-vie]
- The source's routing analysis reports lower entropy in late MoE layers and on narrower-domain tasks such as Flowers and Aircraft. Its supplied visualizations illustrate token-level expert distinctions, but they are qualitative examples rather than evidence that each expert has a stable human-interpretable semantic role.[^zhang-2026-moe-vie]

## Limits and evidence boundaries

- This is a supplied August 2026 manuscript source. Its full LaTeX manuscript, appendices, tables, and supplied architecture, scaling, ablation, and expert-activation figures were reviewed. No code, weights, proprietary data, kernel, or benchmark reproduction was inspected or executed here; reported claims are unverified.[^zhang-2026-moe-vie]
- Training includes 1.5B proprietary image-text pairs, and reported evaluation additionally selects the maximum result from center-cropped or uncropped preprocessing and applies retrieval reweighting. Results therefore do not isolate MoE architecture, nor support direct ranking against entries trained or evaluated under other data and protocols.[^zhang-2026-moe-vie]
- The text says the optimized kernel provides “>2.5x” speedup across batch sizes, but its batch-128 values imply about 2.40x (1306.81 / 544.96). The table supports speedups at the other listed batch sizes but conflicts with the universal wording.[^zhang-2026-moe-vie]
- The source links to a code repository, but its availability, contents, and licensing were not verified here.[^zhang-2026-moe-vie]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) by retaining contrastive image-text training while sparsely scaling the vision-tower FFNs; it does not sparsify the text tower during pretraining.[^zhang-2026-moe-vie]
- Related: [SigLIP 2 multilingual vision–language encoders](siglip2-multilingual-vision-language-encoders.md) is a dense vision-encoder baseline in the manuscript's reported comparisons; its auxiliary pretraining and multilingual design are different approaches to representation quality.[^zhang-2026-moe-vie]
- Synthesized by: [Recent vision-language research directions](recent-vision-language-research-directions.md), [From unified pretraining to modern vision-language models](from-unified-pretraining-to-modern-vision-language-models.md), and [Vision-language task-to-model map](vision-language-task-to-model-map.md) as evidence for sparsely scaled CLIP-style encoders.

[^zhang-2026-moe-vie]: Zhang et al., “MoE-ViE: Mixture of Experts Vision Encoder for Efficient Image and Video Understanding” (supplied manuscript, August 2026), [complete supplied manuscript source](../raw/2608.17402_MoE-ViE/main.tex).

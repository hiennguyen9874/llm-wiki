---
type: Synthesis
title: Video backbones and encoders comparison
description: A task-aware comparison of video backbones and pretrained encoders, including architecture, pretraining scale, reported evidence, and selection trade-offs.
tags: [video, backbones, encoders, pretraining, representation-learning, comparison]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T12:03:39+07:00 }
sources:
  - id: i3d-paper
    resource: ../raw/I3D/full_kinetics_update_v0.tex
    title: Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset
  - id: r2plus1d-paper
    resource: ../raw/R(2+1)D/res2_plus_1d.pdf
    title: A Closer Look at Spatiotemporal Convolutions for Action Recognition
  - id: slowfast-paper
    resource: ../raw/SlowFast/slowfast_iccv19_arxiv_final.tex
    title: SlowFast Networks for Video Recognition
  - id: mvit-paper
    resource: ../raw/MViT/mvit_arxiv.tex
    title: Multiscale Vision Transformers
  - id: timesformer-paper
    resource: ../raw/TimeSformer/TimeSformer_arxiv_v17.tex
    title: Is Space-Time Attention All You Need for Video Understanding?
  - id: vivit-paper
    resource: ../raw/ViViT/main_arxiv.tex
    title: "ViViT: A Video Vision Transformer"
  - id: video-swin-paper
    resource: ../raw/VideoSwin/main.tex
    title: Video Swin Transformer
  - id: videomae-paper
    resource: ../raw/VideoMAE/main.tex
    title: "VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training"
  - id: internvideo-paper
    resource: ../raw/InternVideo/main.tex
    title: "InternVideo: General Video Foundation Models via Generative and Discriminative Learning"
  - id: internvideo2-paper
    resource: ../raw/InternVideo2/main.tex
    title: "InternVideo2: Scaling Foundation Models for Multimodal Video Understanding"
  - id: lv-mae-paper
    resource: ../raw/LV-MAE/main.tex
    title: "LV-MAE: Learning Long Video Representations through Masked-Embedding Autoencoders"
  - id: xclip-recognition-paper
    resource: ../raw/2208.02816_X-CLIP/main.tex
    title: Expanding Language-Image Pretrained Models for General Video Recognition
  - id: xclip-retrieval-paper
    resource: ../raw/2207.07285_X-CLIP/sample-base.tex
    title: "X-CLIP: End-to-End Multi-grained Contrastive Learning for Video-Text Retrieval"
  - id: videoprism-paper
    resource: ../raw/2402.13217_VideoPrism/main.tex
    title: "VideoPrism: A Foundational Visual Encoder for Video Understanding"
  - id: vjepa2-paper
    resource: ../raw/2506.09985_V-JEPA 2/main.tex
    title: "V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning"
---

# Video backbones and encoders comparison

A **video backbone** is the visual network that converts RGB/flow clips into features; an **encoder** often means that same network after pretraining, while a foundation encoder adds a reusable pretraining recipe and broader transfer objective. This distinction matters: I3D, SlowFast, MViT, and Video Swin are primarily architectures; VideoMAE is primarily a self-supervised recipe over a ViT encoder; InternVideo, InternVideo2, VideoPrism, and V-JEPA 2 are pretrained model systems. Their reported scores are not a common leaderboard because model scale, pretraining data, heads, fine-tuning, input views, and tasks differ.

## Architecture map

| Family | Concept | Temporal mechanism | Native role | Main trade-off |
| --- | --- | --- | --- | --- |
| Optical-flow CNN | [Two-stream ConvNets](two-stream-convnets-action-recognition.md), [TSN](temporal-segment-networks.md) | RGB appearance plus stacked flow; TSN samples global snippets | Video classification framework | Historically effective but flow extraction is expensive; sparse TSN sampling can miss brief events |
| 3D/factorized CNN | [I3D](inflated-3d-convnets-i3d.md) | Inflated 3D convolutions, optionally RGB+flow | Clip backbone | Strong transfer baseline; local temporal receptive fields and optional flow cost |
| 3D/factorized CNN | [R(2+1)D](r-2-plus-1-d.md) | Spatial 2D then temporal 1D convolution with an extra nonlinearity | Clip backbone | Easier optimization than matched full 3D ConvNet in its study; still bounded by clip sampling |
| Dual-rate CNN | [SlowFast](slowfast-networks.md) | Sparse high-capacity semantics plus dense lightweight motion | Recognition/detection backbone | Good explicit motion bias without flow; dual pathway adds implementation and compute cost |
| Global augmentation | [Non-local blocks](non-local-neural-networks.md) | Pairwise aggregation over all positions | Add-on to CNN backbone | Improves long-range interaction on high-level maps; not a standalone encoder and scales poorly at raw-token resolution |
| Hierarchical Transformer | [MViT](multiscale-vision-transformers-mvit.md) | Pools token resolution while widening channels | Recognition/detection backbone | Efficient multiscale pyramid; fixed-clip evidence only |
| Factorized Transformer | [TimeSformer](timesformer.md) | Temporal then spatial attention per patch | Clip backbone | Supports longer clips than joint attention; depends strongly on image pretraining in the reported study |
| Factorized Transformer | [ViViT](vivit.md) | Four joint/factorized space-time variants | Clip backbone | Flexible accuracy–cost choices; full joint attention is expensive |
| Local hierarchical Transformer | [Video Swin](video-swin-transformer.md) | Joint attention in alternating shifted 3D windows | Recognition backbone | Strong accuracy/efficiency compromise; local windows do not provide persistent long-video memory |
| CLIP adaptation | [X-CLIP recognition](x-clip-video-recognition.md) | Cross-frame message tokens, shallow temporal integration, video-conditioned prompts | Recognition encoder | Strong supervised/few-shot transfer from CLIP; not temporal localization and “zero-shot” follows K400 adaptation |
| CLIP adaptation | [X-CLIP retrieval](x-clip-video-text-retrieval.md) | Temporal frame encoder plus multi-grained frame/word similarities | Video-text retrieval encoder | Better alignment granularity; whole-video retrieval, not event boundaries or reasoning |
| Masked autoencoder | [VideoMAE](videomae.md) | Reconstructs pixels of 90%-masked video tubes | Self-supervised short-clip encoder | Very data-efficient and simple; pixel reconstruction and fixed clips do not solve long context |
| Foundation encoder | [InternVideo](internvideo.md) | Coordinates masked-video and video-text branches | General short-clip feature backbone | Broad action/language transfer; complex two-branch system and incomplete data governance |
| Foundation encoder | [InternVideo2](internvideo2.md) | Teacher distillation, multimodal alignment, then LLM connection | General visual/multimodal backbone | Strong localization and grounding transfer; fixed resolution/rate and compressed tokens limit detail |
| Frozen foundation encoder | [VideoPrism](videoprism.md) | Video-text contrast followed by masked global/local feature distillation | Frozen short-clip encoder | Broadest frozen-backbone evaluation in the wiki; direct input is only 8–16 sampled frames |
| Predictive encoder | [V-JEPA 2](v-jepa-2.md) | Predicts masked EMA-teacher features; optional action-conditioned latent predictor | Motion/anticipation encoder | Strong motion and anticipation evidence at scale; direct context remains at most 64 pretrained frames |
| Long-video aggregator | [LV-MAE](lv-mae.md) | Reconstructs masked sequences of frozen five-second clip embeddings | Encoder over clip tokens | Reaches about 21 minutes at 256 tokens; inherits information loss from the frozen short-clip encoder |

## Pretraining scale

Counts below are the paper-reported samples used by the relevant stage, not necessarily unique source videos. A model initialized from CLIP or another teacher also inherits knowledge from that teacher's data; those upstream examples must not be added mechanically to downstream corpus counts.

| Model | Reported pretraining or initialization data | Interpretation |
| --- | --- | --- |
| Two-stream / TSN | ImageNet initialization plus target datasets such as UCF101/HMDB51 | Limited-data supervised baseline; no web-scale video pretraining in the cited work |
| I3D | ImageNet initialization optionally followed by Kinetics-400, about **240k** train clips | Supervised action pretraining; two-stream version also requires optical flow[^i3d-paper] |
| R(2+1)D | Kinetics-400 (about **240k**) or Sports-1M supervised training, depending on experiment | Architecture comparisons include from-scratch Kinetics training[^r2plus1d-paper] |
| SlowFast | Usually from scratch on K400 (**~240k**) or K600 (**~392k** in this source); ImageNet changed results by only about ±0.3 in its experiment | Strong evidence that its reported performance was not dependent on image initialization[^slowfast-paper] |
| MViT | From scratch on K400 (**~240k**) for the main video models | Architecture and video learning are less confounded by external image pretraining[^mvit-paper] |
| TimeSformer | ViT initialized on ImageNet-1K or ImageNet-21K, then trained on video datasets such as K400 | Exact image-example count is not recorded in the concept; K400 from-scratch 64.8 versus 78.0 with ImageNet-21K shows strong initialization dependence[^timesformer-paper] |
| ViViT | ImageNet-21K or JFT image initialization, then datasets such as K400 | Exact upstream image count varies by configuration; progressive K400 initialization helps smaller video datasets[^vivit-paper] |
| Video Swin | ImageNet-21K initialization, then K400 (**~240k**) or K600 (**~370k** in this source) | Hierarchical image-to-video transfer[^video-swin-paper] |
| VideoMAE | Self-supervised on each target train set: K400 **~240k**, SSv2 **~169k**, UCF101 **~9.5k**, or HMDB51 **~3.5k** | Clearest data-efficiency result: useful pretraining even at only 3k–4k videos[^videomae-paper] |
| X-CLIP recognition | CLIP initialization trained on **400M image-text pairs**, then supervised video adaptation such as K400 | No new web-scale video-text pretraining; strong results partly reflect CLIP's upstream scale[^xclip-recognition-paper] |
| X-CLIP retrieval | CLIP **400M image-text** initialization plus downstream video-text data; the main MSR-VTT protocol uses **9k** training videos | Efficient adaptation, not a video foundation pretraining corpus[^xclip-retrieval-paper] |
| InternVideo | Manuscript summarizes roughly **12M video clips** across public and collected sources; multimodal branch uses WebVid2M/10M and HowTo100M plus **100M LAION image-text pairs**, with CLIP initialization | Branch-specific datasets overlap and the table's rounded totals should not be treated as a deduplicated unique count[^internvideo-paper] |
| InternVideo2 | Stage 1: **2M** unlabeled videos; later stages list **300M image-text**, **50M** video-audio-speech-text clips, and **2.1M** instruction examples | Largest explicitly staged multimodal pipeline in the wiki; teacher provenance and corpus licensing remain incompletely auditable[^internvideo2-paper] |
| VideoPrism | **36.1M** manually captioned stock clips; about **582M** additional/noisier clips from **275M videos**; Stage 1 also uses about **1B WebLI image-text pairs** | Largest reported mixed visual-language corpus here; three major corpora are anonymized and governance is only partially documented[^videoprism-paper] |
| V-JEPA 2 | VideoMix22M: **22M video/image samples**, including **>1M video hours**; action-conditioned post-training uses **<62 robot hours** | Very large action-free motion corpus, but robot control evidence comes from a tiny and specialized post-training subset[^vjepa2-paper] |
| LV-MAE | More than **1,000 movies/TV series**, **>40k FineVideo videos**, **~7k MovieClips train clips**, plus ActivityNet; short-clip encoders remain frozen | Long-video pretraining is cheap (reported 20 hours on 8×A10), but upstream LanguageBind/InternVideo2 data are inherited rather than retrained[^lv-mae-paper] |

## Evaluation signals that are reasonably informative

These numbers illustrate each model's documented strength; they are **not directly rankable across rows**.

| Model | Representative paper-specific evidence | What it supports |
| --- | --- | --- |
| I3D two-stream | UCF101 **97.8%**, HMDB51 **80.9%** after K400 pretraining | Historical supervised transfer[^i3d-paper] |
| R(2+1)D-34 RGB | K400 **72.0%** top-1 from scratch | Benefit of factorized 3D convolution in its training regime[^r2plus1d-paper] |
| SlowFast R50 | K400 **75.6%** at 36.1 GFLOPs/view; AVA v2.1 **24.2 mAP** | Motion-sensitive recognition and person-centric detection[^slowfast-paper] |
| MViT-B 16×4 | K400 **78.4%**, 70.5 GFLOPs/clip, 36.6M parameters | Efficient hierarchical Transformer baseline[^mvit-paper] |
| TimeSformer long | K400 **80.7%**; paper-defined HowTo100M task **62.6%** over 102.4-second clips | Longer clip-level context, not arbitrary long-video memory[^timesformer-paper] |
| ViViT-L factorized encoder | K400 **81.7%**, SSv2 **65.9%** | Strong pure-Transformer classification with factorization[^vivit-paper] |
| Video Swin-L | K400 **84.9%** with ImageNet-21K initialization | Strong historical fixed-clip classification[^video-swin-paper] |
| VideoMAE-B | K400 **80.0%**, SSv2 **69.6%** after self-supervised target-set pretraining | Data-efficient masked video learning[^videomae-paper] |
| X-CLIP-L/14 | K400 **87.1%**; X-CLIP-B/16 UCF101 zero-shot **72.0%** under its protocol | CLIP-based recognition and few/zero-shot transfer[^xclip-recognition-paper] |
| InternVideo | K400 **91.1%** for a three-model configuration; ActionFormer+ViT-H THUMOS14 **71.58 mAP** | Broad transfer, but K400 number is an ensemble/configuration result[^internvideo-paper] |
| InternVideo2 | ActionFormer THUMOS14 **72.0 mAP**; CG-DETR QVHighlight R1@0.5 **71.42** | Strong pretrained features for localization and language grounding[^internvideo2-paper] |
| VideoPrism-g frozen | K400 **87.2%**, SSv2 **68.5%**, ActivityNet localization **37.8 mAP** with trained heads | Broad frozen-encoder transfer; heads still matter[^videoprism-paper] |
| V-JEPA 2 1B frozen | SSv2 **77.3%**; Epic-Kitchens anticipation recall@5 **39.7** | Strong motion representation and short-horizon anticipation[^vjepa2-paper] |
| LV-MAE | LVU classification average **63.4**; COIN **92.72%**, Breakfast **93.24%** with InternVideo2 embeddings | Bounded long-video aggregation, not interval localization[^lv-mae-paper] |

## Selection guidance

1. **Conventional RGB action recognition:** use SlowFast when rapid motion is central; use Video Swin or MViT when a hierarchical Transformer ecosystem is preferred; keep R(2+1)D as a simple factorized-3D baseline.
2. **Small unlabeled video corpus:** VideoMAE has the clearest evidence for data-efficient self-supervision. Its advantage is the recipe, not a guarantee that a plain ViT is the best production architecture.
3. **One frozen encoder across many short-video tasks:** VideoPrism has the broadest frozen-backbone evidence in this wiki. InternVideo2 is preferable when temporal localization/grounding and multimodal alignment are primary, subject to a more complex training and inference stack.
4. **Motion, anticipation, or latent dynamics research:** V-JEPA 2 offers the strongest documented predictive-representation evidence, but it is not a long-horizon or real-time robot world model.
5. **Long videos:** no short-clip backbone above solves long context by itself. LV-MAE is the explicit long-video aggregator, reaching about 21 minutes through five-second clip tokens, but it may discard short events and inherits its frozen encoder's blind spots.
6. **Video-language retrieval/classification on a constrained budget:** X-CLIP efficiently reuses CLIP; choose the recognition and retrieval variants by task because they are distinct models.
7. **Temporal localization or segmentation:** attach an appropriate head such as [ActionFormer](actionformer.md) or [MS-TCN](ms-tcn.md). Backbone classification accuracy alone does not predict boundary quality.

## Scope and evidence limits

This synthesis includes concepts that directly encode pixels/flow or aggregate pretrained clip embeddings. It does not relabel task heads and Video-LLM frameworks—ActionFormer, BMN, MS-TCN, FUTR, MAT, F2G, UniTime, VideoITG, and NeuS-QA—as visual backbones. Dataset counts can include clips cut from the same source video and may overlap across stages. No cited concept supplies a matched evaluation with identical model size, data, input duration, optimization, head, and inference views across all families; therefore claims such as “best encoder” remain task- and budget-dependent.

## Relationships

- **Compares:** [Video temporal representation learning](video-temporal-representation-learning.md) instances and the principal visual backbones in [Temporal action understanding](temporal-action-understanding.md).
- **Depends on:** [Long-video temporal modeling](long-video-temporal-modeling.md) whenever requested context exceeds the encoder's sampled clip.
- **Uses:** [LV-MAE](lv-mae.md) as a long-video aggregation pattern over frozen short-clip encoders.

[^i3d-paper]: [Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset](../raw/I3D/full_kinetics_update_v0.tex)
[^r2plus1d-paper]: [A Closer Look at Spatiotemporal Convolutions for Action Recognition](../raw/R\(2+1\)D/res2_plus_1d.pdf)
[^slowfast-paper]: [SlowFast Networks for Video Recognition](../raw/SlowFast/slowfast_iccv19_arxiv_final.tex)
[^mvit-paper]: [Multiscale Vision Transformers](../raw/MViT/mvit_arxiv.tex)
[^timesformer-paper]: [Is Space-Time Attention All You Need for Video Understanding?](../raw/TimeSformer/TimeSformer_arxiv_v17.tex)
[^vivit-paper]: [ViViT: A Video Vision Transformer](../raw/ViViT/main_arxiv.tex)
[^video-swin-paper]: [Video Swin Transformer](../raw/VideoSwin/main.tex)
[^videomae-paper]: [VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training](../raw/VideoMAE/main.tex)
[^internvideo-paper]: [InternVideo: General Video Foundation Models via Generative and Discriminative Learning](../raw/InternVideo/main.tex)
[^internvideo2-paper]: [InternVideo2: Scaling Foundation Models for Multimodal Video Understanding](../raw/InternVideo2/main.tex)
[^lv-mae-paper]: [LV-MAE: Learning Long Video Representations through Masked-Embedding Autoencoders](../raw/LV-MAE/main.tex)
[^xclip-recognition-paper]: [Expanding Language-Image Pretrained Models for General Video Recognition](../raw/2208.02816_X-CLIP/main.tex)
[^xclip-retrieval-paper]: [X-CLIP: End-to-End Multi-grained Contrastive Learning for Video-Text Retrieval](../raw/2207.07285_X-CLIP/sample-base.tex)
[^videoprism-paper]: [VideoPrism: A Foundational Visual Encoder for Video Understanding](../raw/2402.13217_VideoPrism/main.tex)
[^vjepa2-paper]: [V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning](../raw/2506.09985_V-JEPA%202/main.tex)

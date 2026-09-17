---
type: Concept
title: Open-vocabulary promptable perception
description: How text prompts, visual exemplars, and concept prompts are replacing fixed taxonomies and unifying detection, segmentation, and tracking.
tags: [detection, segmentation, open-vocabulary, prompting, sam]
status: draft
created: 2026-09-17
generated: { by: llm-wiki-agent/1, at: 2026-09-17T15:30:00Z }
sources:
  - id: rfdetr-2511-09554-v2
    resource: ../raw/arXiv-2511.09554v2/iclr2026_conference.tex
    scope: ../raw/arXiv-2511.09554v2/
    kind: paper
    revision: v2
    title: 'RF-DETR: Neural Architecture Search for Real-Time Detection Transformers'
  - id: reseach-2026-09-17
    resource: ../raw/reseach.md
    kind: article
    title: Tổng hợp SOTA object detection / instance segmentation 2024–2026
  - id: yolo-world-2401-17270-v3
    resource: ../raw/arXiv-2401.17270v3/main.tex
    scope: ../raw/arXiv-2401.17270v3/
    kind: paper
    revision: v3
    title: 'YOLO-World: Real-Time Open-Vocabulary Object Detection'
  - id: trex2-2403-14610-v1
    resource: ../raw/arXiv-2403.14610v1/main.tex
    scope: ../raw/arXiv-2403.14610v1/
    kind: paper
    revision: v1
    title: 'T-Rex2: Towards Generic Object Detection via Text-Visual Prompt Synergy'
  - id: gd15-2405-10300-v2
    resource: ../raw/arXiv-2405.10300v2/main.tex
    scope: ../raw/arXiv-2405.10300v2/
    kind: paper
    revision: v2
    title: 'Grounding DINO 1.5: Advance the Edge of Open-Set Object Detection'
  - id: sam2-2408-00714-v2
    resource: ../raw/arXiv-2408.00714v2/sam2.1_arxiv.tex
    scope: ../raw/arXiv-2408.00714v2/
    kind: paper
    revision: v2
    title: 'SAM 2: Segment Anything in Images and Videos'
  - id: yoloe-2503-07465-v2
    resource: ../raw/arXiv-2503-07465v2/camera_ready.tex
    scope: ../raw/arXiv-2503-07465v2/
    kind: paper
    revision: v2
    title: 'YOLOE: Real-Time Seeing Anything'
  - id: sam3-2511-16719-v2
    resource: ../raw/arXiv-2511.16719v2/main.tex
    scope: ../raw/arXiv-2511.16719v2/
    kind: paper
    revision: v2
    title: 'SAM 3: Segment Anything with Concepts'
---

Synthesis: fixed `class_id ∈ {0,...,79}` formulation is shifting toward `concept = embedding(text / image / exemplar)`, with one promptable model increasingly covering detection plus segmentation plus tracking[^reseach-2026-09-17-1].

## Progression from grounding to concept segmentation

- **Reported:** YOLO-World (CVPR 2024) brings YOLO to real-time open-vocabulary detection via vision-language pretraining, with a YOLO-World-Seg variant[^reseach-2026-09-17-2].
- **Reported:** YOLO-World's primary design is YOLOv8 plus frozen CLIP text encoder plus Re-parameterizable Vision-Language PAN (RepVL-PAN): Text-guided CSPLayer injects text into multi-scale image features with max-sigmoid attention, and Image-Pooling Attention pools {P3,P4,P5} to 27 tokens to make text embeddings image-aware[^yolo-world-2401-17270-v3-1].
- **Reported:** YOLO-World uses a `prompt-then-detect` paradigm with offline vocabulary: user prompts are encoded once, then re-parameterized into RepVL-PAN convolution/linear weights so the text encoder is removed at inference[^yolo-world-2401-17270-v3-2].
- **Reported:** Pre-training unifies detection, grounding, and image-text data as region-text pairs with contrastive loss plus IoU plus distributed focal loss; regression loss is disabled for noisy image-text samples. Automatic CC3M labeling uses n-gram noun extraction, GLIP pseudo-boxes, CLIP rescoring/filtering with NMS 0.5 and 0.3 confidence thresholds, yielding 246k images and 821k pseudo annotations[^yolo-world-2401-17270-v3-3].
- **Reported:** Zero-shot LVIS-minival Fixed AP (max 1k predictions, V100 w/o TensorRT): YOLO-World-S 26.2 AP at 74.1 FPS (13M params deployed, 77M with text encoder), M 31.0 AP at 58.1 FPS, L 35.0 AP at 52.0 FPS on O365+GoldG and 35.4 AP with added CC3M†; comparison points are DetCLIP-T 34.4 AP at 2.3 FPS, Grounding DINO-T 27.4 AP at 1.5 FPS, and GLIP-T 26.0 AP at 0.12 FPS[^yolo-world-2401-17270-v3-4].
- **Reported:** Ablations show data and module effects: O365-only 23.5 AP rises to 31.9 AP by adding GQA, 32.5 AP with GoldG, and 33.0 AP with CC3M†; RepVL-PAN adds about 1.1 AP with larger rare-category gains; frozen CLIP (22.4 AP) strongly beats frozen BERT (14.6 AP), while fine-tuning CLIP on O365 drops to 19.3 AP, attributed to loss of CLIP generality on only 365 categories[^yolo-world-2401-17270-v3-5].
- **Reported:** Pre-trained weights transfer by fine-tuning: COCO fine-tuned YOLO-World-L reaches 53.3 AP, above from-scratch YOLOv8-L 52.9 AP in the paper's table, and RepVL-PAN is removed for small-vocabulary COCO speed; LVIS-base fine-tuned YOLO-World-L reaches 34.1 box AP versus 26.9 AP for full-LVIS-trained YOLOv8-L. For open-vocabulary instance segmentation, tuning only the segmentation head preserves zero-shot behavior, while tuning all modules improves mask AP but slightly reduces rare box AP[^yolo-world-2401-17270-v3-6].
- **Synthesis:** the durable reuse pattern is **offline vocabulary plus re-parameterization for deployment** combined with **region-text unification of heterogeneous supervision**, rather than only scaling the detector backbone.
- **Reported:** Grounding DINO 1.5 Pro scales open-set detection via ViT-L (EVA-02) backbone in the Grounding DINO dual-encoder-single-decoder frame with deep early fusion retained; to balance early fusion's higher recall against higher hallucination, training increases the negative-sample proportion[^gd15-2405-10300-v2-1].
- **Reported:** Grounding-20M pre-training uses 20M+ grounding-annotated images from public sources with annotation pipelines and post-processing for quality; Pro and Edge share this data[^gd15-2405-10300-v2-2].
- **Reported:** Zero-shot Fixed AP: Pro reaches 54.3 COCO, 55.7 LVIS-minival (56.1 rare / 57.5 common / 54.1 frequent), 47.6 LVIS-val, 58.7 ODinW13 avg, and 30.2 ODinW35 avg — above DetCLIPv3 by 6.9/6.2 on LVIS-minival/val and above Grounding DINO Swin-L by 1.8 on COCO in the paper's table[^gd15-2405-10300-v2-3].
- **Reported:** Fine-tuned Pro reaches 68.1 LVIS-minival (+12.4 over its zero-shot), 63.5 LVIS-val (+15.9), 70.6 ODinW35 avg (+40.4), and 72.4 ODinW13 avg (+13.7)[^gd15-2405-10300-v2-4].
- **Reported:** Qualitative scope (visual evidence not independently inspected): common objects under monochrome/blur/occlusion, long-tail categories, short-caption grounding across photo/cartoon/sketch, long-caption phrase grounding with claimed generalization to unseen terms (e.g. `fiat logo`), dense overlapping scenes, offline video with consistent boxes, and side-by-side fewer hallucinations versus Grounding DINO 1.0[^gd15-2405-10300-v2-5].
- **Reported:** T-Rex2 combines text prompt plus visual exemplar for generic and open-set detection[^reseach-2026-09-17-4]. The primary paper below replaces that secondary row with mechanism, workflows, and zero-shot evidence[^trex2-2403-14610-v1-1].

### Text-visual synergy in T-Rex2

- **Reported:** T-Rex2 is a DETR-style end-to-end detector with one suit of weights for text, visual, and mixed prompts. Image encoder mirrors Deformable DETR (Swin backbone plus six deformable self-attention encoder layers); text encoder is CLIP-B fine-tuned with `[CLS]` embedding `T`; visual prompt encoder uses sine-cosine position embeddings with separate linear projections for 4D boxes versus 2D points, learnable content embedding plus global class token, three deformable cross-attention layers conditioned on prompt coordinates, then self-attention plus FFN whose global query output is visual embedding `V`; box decoder follows DINO with Grounding-DINO-style query selection (top-900 image-prompt similarity anchors) and predicts labels by `V · Q_dec^T` instead of a learned classifier[^trex2-2403-14610-v1-2].
- **Reported:** Region-level contrastive alignment is explicit InfoNCE `L_align = -mean log exp(v_i·t_i)/sum_j exp(v_i·t_j)`, framed as mutual distillation: text anchors diverse visual prompts toward general concepts while visual instances refine text embeddings. Training alternates text and visual iterations cyclically; total loss is `L_cls + L_L1 + L_GIoU + L_DN + L_align`, with Hungarian-matching weights 2.0/5.0/2.0 and final weights 1.0/5.0/2.0/1.0 plus contrastive denoising training[^trex2-2403-14610-v1-3].
- **Reported:** Four inference workflows share the image encoder and decoder: text-only open-vocabulary; interactive visual (box or point on the current image, iteratively refinable); generic visual (mean of `n` cross-image exemplar embeddings, default `N=16` per category); and mixed `(T+V)/2`. Late fusion means the backbone plus encoder run once and repeated interactions rerun only prompt encoder plus decoder. Supplement adds region classification by `argmax softmax(V·t_j)` and training-free open-set video detection by reusing a generic visual embedding sampled from `N` frames[^trex2-2403-14610-v1-4].
- **Reported:** Data engines: text uses 3.15M labeled plus 3.39M pseudo-labeled images (Objects365, OpenImages, GoldG grounding plus CC/LAION400M noun-chunk → Grounding DINO pseudo-boxes double-filtered at CLIP score >0.8 plus Bamboo classification prompts); visual uses 2.4M labeled plus 0.65M pseudo-labeled images (Objects365, OpenImages, HierText, CrowdHuman plus SA-1B self-training loop: train visual-only starter, annotate SA-1B, label boxes with TAP over a 2560-class dictionary, keep images with at least one sufficiently repeated category)[^trex2-2403-14610-v1-5].
- **Reported:** One-suit zero-shot generic detection shows complementary coverage. Swin-T text versus Visual-G: COCO 45.8 versus 38.8; LVIS-minival 42.8 versus 37.4; LVIS-val 34.8 versus 34.9 with rare split 29.0 versus 32.4; ODinW avg/med 18.0/4.7 versus 23.6/17.5; Roboflow100 avg 8.2 versus 17.4. Swin-L text versus Visual-G: COCO 52.2 versus 46.5; LVIS-minival 54.9 versus 47.6; LVIS-val 45.8 versus 45.3 with rare 42.7 versus 43.8; ODinW 22.0/7.3 versus 27.8/20.5; Roboflow100 10.5 versus 18.5. The paper codes this as text winning common categories and visual winning rare/long-tail domains[^trex2-2403-14610-v1-6].
- **Reported:** Interactive Visual-I is stronger but uses an easier protocol (category known plus one GT box/point on the test image): Swin-T box 56.6 COCO, 59.3 LVIS-minival, 62.6 LVIS-val, 37.7/39.3 ODinW, 30.6 Roboflow100; Swin-L box 58.5/62.5/65.8/39.7/38.1/30.2; point prompts score slightly lower. Few-shot counting with three exemplars: FSC147 MAE 10.94 versus T-Rex 8.72, FSCD-LVIS AP 43.35 versus T-Rex 40.32, read as competitive counting with better overall detection accuracy in dense small-object scenes[^trex2-2403-14610-v1-7].
- **Reported:** Synergy ablations (Swin-T): visual-only training gives only 14.0 COCO / 15.3 LVIS-val generic AP; naive joint training without alignment lifts visual to 38.7/30.2 but lowers text from 46.4/32.8 to 44.4/32.2; adding contrastive alignment restores text to 45.8/34.8 and lifts visual to 38.8/34.9. t-SNE on 10 COCO categories shows separated text/visual clusters without alignment versus text-anchored visual clusters plus more separated text prompts with alignment[^trex2-2403-14610-v1-8].
- **Reported:** Prompt-count, mixing, data, and speed ablations: generic Visual-G AP rises with exemplars (COCO/LVIS-val 29.2/26.2 at 1, 32.9/32.9 at 4, 38.8/34.9 at 16, 41.3/35.1 at 32, 41.4/35.2 at 64), so 16 is the default but diversity still costs exemplars; mixed prompts balance COCO at 42.5 between text 45.8 and visual 38.8 while improving LVIS-val to 37.0 above either alone; Bamboo adds about +3.8 LVIS but −0.4 COCO and caption data helps both; SA-1B strongly helps interactive use but slightly hurts generic use, attributed to noisy TAP-only SA-1B semantics. RTX 3090 batch-1 timing is 10.41 FPS overall and 33.33 interactive FPS for Swin-T versus 3.62 and 19.96 for Swin-L[^trex2-2403-14610-v1-9].
- **Reported:** Zero-shot region classification by prompting with each GT box and scoring all dataset names: T-Rex2-Swin-L reaches COCO Top-1/Top-5 82.2/93.9 and LVIS 49.8/76.9, above crop-region CLIP ViT-B at 37.6/60.1 and 9.0/20.0. Stated limitations are mixed-prompt interference on common objects, the need for up to 16 visual examples for generic concepts, and noisy SA-1B semantics[^trex2-2403-14610-v1-10].
- **Synthesis:** the durable pattern is **explicit region-level text-visual alignment plus late-fusion workflows**, not merely adding a visual branch: alignment rescues joint training, late fusion buys interactive speed, and generic visual use trades exemplar count for tail coverage.

### Unified real-time open detection and segmentation in YOLOE

- **Reported:** YOLOE (Wang et al., Tsinghua, ICCV 2025) unifies text-prompt, visual-prompt, and prompt-free detection plus segmentation in one YOLO-based real-time model via three mechanisms: Re-parameterizable Region-Text Alignment (RepRTA), Semantic-Activated Visual Prompt Encoder (SAVPE), and Lazy Region-Prompt Contrast (LRPC)[^yoloe-2503-07465-v2-1]. This replaces the prior secondary summary that YOLOE supports three prompt modes with mechanism, cost, and zero-shot evidence[^reseach-2026-09-17-5].
- **Reported:** Architecture keeps YOLO backbone plus PAN with regression head, YOLACT-style segmentation head (prototypes plus mask coefficients), and an object-embedding head whose output replaces the closed-set class channels; labels are `Label = O · P^T` for `N` anchor object embeddings by `C` prompt embeddings of dimension `D`[^yoloe-2503-07465-v2-2].
- **Reported:** RepRTA precaches MobileCLIP-B(LT) text embeddings, refines them during training with a one-block SwiGLU FFN `f_θ`, then re-parameterizes `f_θ(P)` into the last-convolution kernel as `K' = R(f_θ(P)) ⊛ K^T` so inference and downstream transfer match native YOLO with zero text-encoder, fusion, or transfer overhead[^yoloe-2503-07465-v2-2].
- **Reported:** SAVPE formalizes a visual cue as a 0/1 mask and splits encoding into a semantic branch (PAN `{P3,P4,P5}` → concatenated `S ∈ R^{D×H×W}`) and an activation branch (downsampled prompt plus image features in `A=16 ≪ D` channels → softmax-normalized weights `W` inside the indicated region); grouped aggregation `P = Concat(G_1..G_A)` avoids transformer-heavy or extra CLIP-vision-encoder cost[^yoloe-2503-07465-v2-3].
- **Reported:** LRPC reformulates prompt-free detection as retrieval: train a specialized embedding `P_s` for objectness, keep only `O' = {o | o·P_s^T > δ}` with default `δ=0.001`, then match only `O'` against a built-in 4,585-category RAM vocabulary, removing FlanT5/OPT-class LLM dependency[^yoloe-2503-07465-v2-3].
- **Reported:** Training uses Objects365 plus GoldG (GQA plus Flickr30k, COCO images excluded) with SAM-2.1 pseudo-masks filtered, Gaussian-smoothed, and Douglas-Peucker simplified; schedule is 30 epochs text plus 2 epochs SAVPE-only plus 1 epoch specialized embedding, with BCE classification, IoU plus distributed focal regression, and YOLACT mask BCE. YOLOE-v8-S/M/L train on 8×RTX4090 in 12.0/17.0/22.5 h, about 3× less than YOLO-World[^yoloe-2503-07465-v2-4].
- **Reported:** LVIS-minival Fixed AP zero-shot text/visual: YOLOE-v8-S 27.9/26.2, M 32.6/31.0, L 35.9/34.2 versus YOLO-Worldv2-S/M/L 24.4/32.4/35.5, with T4 TensorRT FPS 305.8/156.7/102.5 versus 216.4/117.9/80.0 and iPhone-12 CoreML gains around 1.2–1.3×; rare-category gains are +5.2 AP_r at S and +7.6 AP_r at L. YOLO11 variants show the same pattern (e.g. 11-L 35.2 text at 130.5 T4 FPS). Visual YOLOE-v8-L beats T-Rex2 by 3.3 AP_r and 0.9 AP_c with about half the training images (1.4M vs 3.1M)[^yoloe-2503-07465-v2-5].
- **Reported:** LVIS-val zero-shot segmentation AP^m text/visual: v8-S 17.7/16.8, M 20.8/20.3, L 23.5/22.0, above LVIS-Base fine-tuned YOLO-Worldv2-M/L (17.8/19.8) by 3.0/3.7 AP^m at M/L[^yoloe-2503-07465-v2-5].
- **Reported:** Prompt-free LVIS-minival Fixed AP: v8-L 27.2 AP and 23.5 AP_r versus GenerateU Swin-T 26.8/20.0 and Swin-L 27.9/22.3, with 47M versus 297M/467M params and 25.3 versus 0.48/0.40 PyTorch T4 FPS; LRPC preserves AP while cutting retrieval work (about 80% fewer of 8,400 anchors at `δ=0.001`), giving 1.7×/1.3× speedups for v8-S/L[^yoloe-2503-07465-v2-6].
- **Reported:** COCO transfer: 10-epoch linear probing reaches 35.6/42.2/45.4 box AP and 30.3/35.5/38.3 mask AP for v8-S/M/L; full tuning (160 epochs S, 80 epochs M/L) reaches 45.0/50.4/53.0 box AP and 36.7/40.9/42.7 mask AP, above from-scratch YOLOv8-S/M/L (44.7/50.0/52.4 box, 36.6/40.5/42.3 mask) with about 3–4× fewer epochs[^yoloe-2503-07465-v2-6].
- **Reported:** Ablation roadmap (v8-L, standard LVIS-minival AP): YOLO-Worldv2-L 33.0 at 100 epochs → 31.0 at 30 epochs → 31.9 with global negative dictionary → 30.0 without cross-modal fusion but 1.28×/1.23× T4/iPhone speedups → 31.5 with MobileCLIP → 33.5 with RepRTA → 33.3 plus segmentation head (YOLOE), with a noted multi-task AP_f cost. SAVPE beats mask-pooling 31.9 vs 30.4 AP (`A=16` balances `A=1/32`); LRPC threshold trades accuracy for speed (e.g. v8-S `δ=0.01` gives 20.8 AP at 106 FPS vs 21.0 AP at 95.8 FPS for `δ=0.001`)[^yoloe-2503-07465-v2-7].
- **Synthesis:** the durable reuse pattern is **cached embeddings plus re-parameterization for text, low-dimensional decoupled activation for visual cues, and objectness-first lazy retrieval for prompt-free**, rather than cross-modal fusion, heavy visual encoders, or generative LLMs.

### SAM 3 Promptable Concept Segmentation (PCS)

- **Reported:** PCS task takes a short noun phrase, image exemplars (positive/negative boxes), or both, and returns instance plus semantic masks for every matching instance with identities across video (<=30 s). Text is global per clip, exemplars are per-frame refinements; prompts must stay category-consistent. Ambiguity (polysemy, vague attributes, boundaries, occlusion) is handled by 3-expert Gold annotation plus oracle scoring and an ambiguity module[^sam3-2511-16719-v2-1]. This replaces the prior secondary row that SAM 3 does concept-prompted detection plus tracking[^reseach-2026-09-17-6].
- **Reported:** Detector is DETR-based conditioned on text plus exemplar prompt tokens: Perception Encoder (PE) image/text backbone, exemplar encoder with position plus label embeddings and ROI-pooled features, 6-block fusion encoder cross-attending to prompt tokens, 6-block decoder with Q=200 queries, iterative refinement, DAC-DETR dual supervision plus Align loss, MaskFormer mask head plus binary semantic head[^sam3-2511-16719-v2-2].
- **Reported:** Presence head decouples recognition from localization: `p(query matches NP)=p(query matches | NP present)*p(NP present)` via a learned global presence token. Object scores are supervised only when the concept is present; inference uses presence*object product, with a counting mode that fixes presence to 1[^sam3-2511-16719-v2-2].
- **Reported:** Tracker reuses frozen PE plus SAM-2-style memory encoder/bank, prompt encoder, and mask decoder: `propagate(M_{t-1})`, `detect(I_t,P)`, IoU `match_and_update`, masklet detection-score suppression over a temporal window, periodic re-prompt with high-confidence detections, 3 ambiguous masks per object, and click refinement of single masklets[^sam3-2511-16719-v2-3].
- **Reported:** ~850M params (~450M vision, ~300M text, ~100M detector/tracker). Four training stages: PE pretraining, detector pretraining, detector fine-tuning with presence, tracker training with frozen backbone. H200 latency is 30 ms per image with 100+ objects; video scales with object count (~5 concurrent near real-time)[^sam3-2511-16719-v2-3].
- **Reported:** Data engine in 4 phases: (1) human MV/EV verification from caption NPs plus SAM-2-plus-OV-detector proposals (4.3M pairs); (2) Llama-3.2 MV/EV AI verifiers plus Llama NP plus hard-negative proposal with 6 model plus verifier updates (122M pairs); (3) scaling plus 15-dataset domain expansion plus 22.4M-node Wikidata ontology plus alt-text mining (19.5M pairs); (4) video mining with scene/motion filtering, image-flow labeling, then masklet dedup and failure-focused human correction[^sam3-2511-16719-v2-4].
- **Reported:** Training data: SA-Co/HQ 5.2M images, 4M unique phrases, 52M masks, 146M image-NP pairs; SA-Co/SYN 39M images, 38M phrases, 1.4B masks, 1.7B pairs without humans; SA-Co/EXT 15 external sets with ontology hard negatives; SA-Co/VIDEO 52.5K videos, 24.8K vocab, 467K masklets, 134K video-NP pairs averaging 84.1 frames at 6 fps[^sam3-2511-16719-v2-5].
- **Reported:** SA-Co benchmark has 207K phrases, 121K images/videos, 3M media-phrase pairs with hard negatives (>50x concepts of prior work): Gold (7 domains, 3 annotators), Silver (10 domains, 1 annotator), Bronze/Bio (9 repurposed sets), VEval video (3 domains: SA-V, YT-Temporal-1B, SmartGlasses)[^sam3-2511-16719-v2-5].
- **Reported:** Metrics threshold predictions at 0.5 confidence: positive micro-F1 (pmF1) for localization, image-level MCC (IL_MCC in [-1,1]) for presence classification, and classification-gated F1 `cgF1=100*pmF1*IL_MCC`; video adds pHOTA[^sam3-2511-16719-v2-6].
- **Reported:** Zero-shot image PCS with text: LVIS mask AP 48.5 versus 38.5 DINO-X, cgF1 37.2; SA-Co Gold/Silver/Bronze/Bio cgF1 54.1/49.6/42.6/55.4 versus strongest OWLv2* 24.6/11.5/11.7/0.04 (over 2x on Gold, 74% of human 72.8); COCO box AP 56.4, COCO-O 55.7, ADE-847 mIoU 13.8, PC-59 60.8, Cityscapes 65.2[^sam3-2511-16719-v2-7].
- **Reported:** Exemplars and adaptation: 1-exemplar AP+ beats T-Rex2 by +18.3 COCO, +10.3 LVIS, +20.5 ODinW; text+image combined is best (e.g. COCO 78.1, LVIS 78.4). Interactive K-exemplar adds +21.6 cgF1 after 3 clicks and beats ideal per-instance PVS correction by +2.0 before plateauing at 4 clicks where hybrid PCS-then-PVS helps. Few-shot fine-tune reaches ODinW13 61.0 zero-shot / 71.8 10-shot and RF100-VL 15.2/36.5; counting reaches CountBench MAE 0.12 Acc 93.8 and PixMo MAE 0.21 Acc 86.2[^sam3-2511-16719-v2-8].
- **Reported:** Zero-shot video PCS with text on VEval (cgF1/pHOTA): SA-V 30.3/58.0, YT-Temporal-1B 50.8/69.9, SmartGlasses 36.4/63.6 versus GLEE ~0.1 and LLMDet-plus-tracker ~2.3, reaching over 80% of human pHOTA; public LVVIS 36.3 mAP, BURST 44.5 HOTA, YTVIS21 57.4, OVIS 60.5. Detector-plus-tracking-by-detection ablation trails full SAM 3, supporting the learned tracker[^sam3-2511-16719-v2-9].
- **Reported:** SAM 3 Agent wraps SAM 3 with an MLLM planner that proposes NPs, inspects masks, and iterates: zero-shot ReasonSeg gIoU 77.0 val / 74.0 test and OmniLabel AP 45.3 with Gemini 2.5 Pro, above prior zero-shot without referring-expression training; also leads on RefCOCO+/RefCOCOg zero-shot[^sam3-2511-16719-v2-9].
- **Reported:** Ablations on Gold: presence head +1.5 cgF1 (IL_MCC 0.77 to 0.82); hard negatives 0 to 30 per image lift IL_MCC 0.44 to 0.68 with pmF1 flat; EXT-only 23.7 cgF1, +SYN 32.8, +HQ 45.5, +both 47.4; PE-L+ 43.2 cgF1 and 42.5 COCO-O versus Hiera-L 32.8/22.0 and DINOv2-L 35.3/31.9[^sam3-2511-16719-v2-10].
- **Reported:** AI verifiers close half the human gap: replacing presence with EV verifier +7.2 cgF1 (54.0 to 61.2) plus MV mask filtering +1.1 to 62.3 versus human 72.8. Held-out Food&drink scaling shows SYN-Food matches HQ-Food trajectory without humans when mixed 1:1 with base data; pseudo-labels alone lag. Throughput doubles (datamix 50 s to 23 s; negatives 30 s to 6 s, 5x) at near-human MV/EV accuracy[^sam3-2511-16719-v2-11].
- **Reported:** Stated limits: poor zero-shot on fine-grained OOD and niche domains (e.g. thermal, aircraft, medical), single/double-attribute NPs only with MLLM needed for referring expressions, video cost linear in objects (parallelize to 10 objs/2 H200s, 28/4, 64/8 for 30 FPS), and hard concept/instance mode-switch for edits[^sam3-2511-16719-v2-12].

### Promptable visual segmentation as task unification (SAM 2)

- **Reported:** Promptable Visual Segmentation takes clicks, boxes, or masks on any frame and predicts the spatio-temporal masklet with iterative refinement on new frames; SA is single-frame PVS and semi-supervised/interactive VOS are mask- or scribble-restricted special cases, restricted to valid objects with clear boundaries[^sam2-2408-00714-v2-1].
- **Reported:** SAM 2 keeps SAM's prompt encoder and multi-mask ambiguity handling, extends it across frames by propagating only the highest-IoU mask when unresolved, and adds an occlusion head/token for frames with no visible object plus high-resolution skip connections from Hiera strides 4/8 into the decoder[^sam2-2408-00714-v2-2].
- **Reported:** On the 37-dataset SA image task, SA-1B-only SAM 2 reaches 58.9 1-click mIoU versus SAM 58.1 at 130.1 versus 21.7 FPS A100; full image+video mix reaches 61.9 all / 63.3 image / 60.1 video / 69.6 on 14 new video-derived sets, showing video data helps image generality[^sam2-2408-00714-v2-3].
- **Synthesis:** SAM 2 supplies the `click/box/mask on any frame → masklet + track` primitive that later concept-prompted work (YOLOE, SAM 3) lifts to `concept → all matching instances`; see [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md) for streaming memory, SA-V scale, and video SOTA details.

## Specialist challenge to fine-tuned VLMs

- **Reported:** RF-DETR (arXiv `2511.09554v2`) reframes the open-vocabulary transfer question: zero-shot VLMs impress on COCO common classes but fail on RF100-VL out-of-distribution classes/modalities, while fine-tuning a heavy VLM buys in-domain AP at text-encoder runtime plus lost open-vocabulary generality; its lightweight closed-vocabulary specialist instead pairs DINOv2 pretraining with per-dataset NAS[^rfdetr-2511-09554-v2-1].
- **Reported:** on RF100-VL averaged over 100 datasets, RF-DETR-2XL reaches `63.3` AP (`63.5` with fine-tuning) at `15.6` ms versus fine-tuned GroundingDINO-T `62.3`/`309.9` ms\* and LLMDet-T `62.3`/`308.4` ms\*, about `20×` faster for higher AP; even RF-DETR-M `61.7`/`4.6` ms approaches those VLM scores at a fraction of runtime[^rfdetr-2511-09554-v2-2].
- **Reported:** class-name ablation finds fine-tuning GroundingDINO with true class names (`62.3` AP) versus class indices (`62.5` AP) gives no meaningful RF100-VL gain, suggesting end-to-end fine-tuning washes out internet-scale text pretraining benefits[^rfdetr-2511-09554-v2-3].
- **Synthesis:** prefer specialist-plus-NAS when the target taxonomy is closed and latency matters, and reserve VLM fine-tuning for genuinely open taxonomies; evaluate future detectors on both COCO `val` and public val/test splits like RF100-VL to catch COCO overfitting (D-FINE beating RT-DETR on COCO but losing at RF100-VL AP50 is the cautionary case).

## Why SAM 3 matters in this lineage

- **Synthesis:** earlier stages still resembled `text → box`; YOLOE adds `prompt → box + mask`; SAM 3 moves to `concept → all matching instances → mask + identity + track`, removing the manual detector-plus-SAM composition.
- Instance segmentation therefore stops behaving as a separate branch: RF-DETR, YOLO26, YOLOE, and SAM 3 share backbones or unified query representations across box, mask, and track outputs[^reseach-2026-09-17-7].

## Relationships

- Builds on [Vision foundation models for detection](vision-foundation-models-for-detection.md) for semantic representation quality.
- Contrasts with [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md), which optimizes closed-set AP rather than prompt generality.
- Extends into [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md) through SAM 2 streaming memory and video tracking.

## Contradictions

- None within these sources. The secondary synthesis claim on YOLO-World is consistent with the primary paper; latency comparisons across papers use different setups, so treat cross-paper FPS gaps as protocol-dependent.

## Coverage limits

- All capability, AP, and FPS figures are **reported**, not reproduced; CVF, arXiv, Meta, and GitHub sources behind them were not fetched.
- **Observed** by static inspection: `raw/arXiv-2511.09554v2/iclr2026_conference.tex` Tab. `tab:rf100-vl` plus `supplement.tex` Tab. `tab:rf100-vl-class-names` fully read for specialist-versus-VLM and class-name ablation claims; figures used only via captions/body text. No code was executed.
- `raw/arXiv-2401.17270v3/main.tex` (revision v3) plus `preamble.tex` were statically inspected; `cvpr.sty` and `ieeenat_fullname.bst` were excluded as vendored templates, `main.bib`/`main.bbl` were used only for identity context, and `figures/*.pdf` were not visually inspected beyond what captions and body text reproduce.
- `raw/arXiv-2403.14610v1/main.tex` (revision v1) plus `sec/0_abstract.tex`, `sec/1_intro.tex`, `sec/2_related_work.tex`, `sec/3_method.tex`, `sec/4_experiments.tex`, `sec/X_suppl.tex`, and `preamble.tex` were statically inspected; `cvpr.sty`, `llncs.cls`, `splncs04.bst`, `ieeenat_fullname.bst`, `llncsdoc.pdf`, `lncs_readme.txt`, `lncs_history.txt`, and `LICENSE` were excluded as vendored templates or license boilerplate, `main.bib`/`main.bbl` were used only for identity context, `images/*.pdf` were not visually inspected beyond captions and body-text reproduction, and `eijkel2.eps/.pdf` were excluded as template decoration. No code was executed.
- `raw/arXiv-2405.10300v2/main.tex` (revision v2) plus `sec/01_abstract.tex`, `sec/02_intro_new.tex`, `sec/03_model_training.tex`, `sec/04_model_evaluation.tex`, `sec/05_case_analysis_and_vis.tex`, `sec/06_conclusion.tex`, `sec/07_acknowledgement.tex`, `sec/08_appendix.tex`, and tables `gd1.5_zero_shot_v2.tex`, `gd1.5_zero_shot_odinw13.tex`, `gd1.5_downstream_finetune.tex`, `gd1.5_downstream_finetune_odinw13.tex`, `gd1.5_edge.tex`, `gd1.5_odinw35_results.tex`, `blog_table.tex` were statically inspected; `sec/02_introduction.tex` was excluded as superseded by `sec/02_intro_new.tex`, `neurips_2022.sty`/`neurips_data_2023.sty` were excluded as vendored templates, `main.bib`/`main.bbl` were used only for identity context, and `figs/*.pdf` were not visually inspected beyond captions and body-text reproduction. No code was executed.
- `raw/arXiv-2408.00714v2/sam2.1_arxiv.tex` (revision v2) plus `tab/data_engine_phases.tex`, `tab/tab-datasets-stats-comparison.tex`, `tab/ablation_training_mix.tex`, `tab/ablation_data_quality.tex`, and `tab/tab-mask2masklet-results-oss.tex` were statically inspected for PVS task, mask-decoder/occlusion, and SA image results; style files, `sam2.1_arxiv.bbl`, `assets/*`, `figs/*.pdf`, `img/**`, and `figs/dataset_vis/**/*.jpg` were excluded or used only via captions/body text. No code was executed.
- `raw/arXiv-2503.07465v2/camera_ready.tex` (revision v2) plus `preamble.tex` and `00README.json` were statically inspected; `camera_ready.bbl` was used only for identity context, `iccv.sty` and `ieeenat_fullname.bst` were excluded as vendored templates, and `figures/*.pdf` plus `figures/logo.png` were not visually inspected beyond what captions and body text reproduce. No code was executed.
- **Observed** by static inspection: `raw/arXiv-2511.16719v2/main.tex` (revision v2, 3615 lines) plus `multiplex.tex` and `text_boxes/inc_macros.tex` fully read for task, detector/presence/tracker, 4-phase data engine, SA-Co scales, metrics, image/video/agent results, and ablations; `math_commands.tex` and `text_boxes/sam3_agent_example.tex` scanned for macros and agent detail; `main.bbl` used only for identity context; `fairmeta.cls`, `fancyhdr.sty`, `bibstyle.bst`, `natbib.sty` excluded as vendored templates; `assets/Optimistic.ttf/.tfm` excluded as binary fonts; `figures/**/*.pdf/.jpg/.png` used only via captions and body-text reproduction without visual inspection. No code was executed.
- YOLO-World LVIS numbers use Fixed AP on LVIS-minival with max 1k predictions and V100 FPS w/o TensorRT; COCO fine-tune FPS in the same paper uses TensorRT, so cross-table latency is not directly comparable.
- Source material is a Vietnamese synthesis to 17/09/2026 that explicitly disclaims absolute completeness.

[^reseach-2026-09-17-1]: `raw/reseach.md`, sections “Bức tranh tổng thể” and “6. Open-vocabulary detection”.
[^reseach-2026-09-17-2]: `raw/reseach.md`, table row “YOLO-World – CVPR 2024”.
[^reseach-2026-09-17-3]: `raw/reseach.md`, table row “Grounding DINO 1.5” and section “9. Edge/mobile”.
[^reseach-2026-09-17-4]: `raw/reseach.md`, table row “T-Rex2”.
[^reseach-2026-09-17-5]: `raw/reseach.md`, table row “YOLOE – ICCV”.
[^reseach-2026-09-17-6]: `raw/reseach.md`, table row “SAM 3”.
[^reseach-2026-09-17-7]: `raw/reseach.md`, section “7. Instance segmentation không còn là một nhánh riêng”.
[^rfdetr-2511-09554-v2-1]: `raw/arXiv-2511.09554v2/iclr2026_conference.tex`, Abstract plus Sec. Introduction — open-vocabulary COCO strength versus real-world failure, fine-tuned-VLM runtime/generality cost, specialist-plus-NAS thesis.
[^rfdetr-2511-09554-v2-2]: `raw/arXiv-2511.09554v2/iclr2026_conference.tex`, Tab. `tab:rf100-vl` plus `supplement.tex` Tabs. `tab:rf100vl-scale`/`tab:rf100-vl-fixed-arch` — RF-DETR-2XL/M versus GroundingDINO-T/LLMDet-T AP/latency, D-FINE versus RT-DETR COCO-overfit reading.
[^rfdetr-2511-09554-v2-3]: `raw/arXiv-2511.09554v2/supplement.tex`, Tab. `tab:rf100-vl-class-names` — GroundingDINO with class names `62.3` versus indices `62.5` AP on RF100-VL.
[^yolo-world-2401-17270-v3-1]: `raw/arXiv-2401.17270v3/main.tex`, Sec. Method/Model Architecture and Sec. Re-parameterizable Vision-Language PAN, Fig. Overall Architecture and Fig. RepVL-PAN.
[^yolo-world-2401-17270-v3-2]: `raw/arXiv-2401.17270v3/main.tex`, Sec. Introduction Fig. Comparison with Detection Paradigms, Sec. Inference with Offline Vocabulary, and Appendix Re-parameterization for RepVL-PAN.
[^yolo-world-2401-17270-v3-3]: `raw/arXiv-2401.17270v3/main.tex`, Sec. Pre-training Schemes, Tab. Pre-training Data, Sec. Pseudo Labeling with Image-Text Data, and Appendix Automatic Labeling on Large-scale Image-Text Data.
[^yolo-world-2401-17270-v3-4]: `raw/arXiv-2401.17270v3/main.tex`, Sec. Implementation Details, Sec. Pre-training Experimental Setup/Zero-shot Evaluation/Main Results on LVIS, and Tab. Zero-shot Evaluation on LVIS.
[^yolo-world-2401-17270-v3-5]: `raw/arXiv-2401.17270v3/main.tex`, Sec. Ablation Experiments Tabs. Ablations on Pre-training Data, RepVL-PAN, and Text Encoder.
[^yolo-world-2401-17270-v3-6]: `raw/arXiv-2401.17270v3/main.tex`, Sec. Fine-tuning YOLO-World Tabs. Comparison with YOLOs on COCO and Comparison with Open-Vocabulary Detectors on LVIS, Sec. Open-Vocabulary Instance Segmentation Tab. Open-Vocabulary Instance Segmentation, and Appendix Fine-tuning Details.
[^trex2-2403-14610-v1-1]: `raw/arXiv-2403.14610v1/main.tex`, title/authors/abstract and `sec/1_intro.tex`, contributions and four workflows.
[^trex2-2403-14610-v1-2]: `raw/arXiv-2403.14610v1/sec/3_method.tex`, Sec. T-Rex2 Model, Visual-Text Promptable Object Detection: Image Encoder, Visual Prompt Encoder Eqs. 1–5, Text Prompt Encoder, Box Decoder Eqs. 6–8.
[^trex2-2403-14610-v1-3]: `raw/arXiv-2403.14610v1/sec/3_method.tex`, Sec. Region-Level Contrastive Alignment Eq. 9 and Sec. Training Strategy and Objective Eq. 10; `sec/X_suppl.tex`, Sec. Model Details/Implementation Details for loss weights and CDN.
[^trex2-2403-14610-v1-4]: `raw/arXiv-2403.14610v1/sec/3_method.tex`, Sec. Four Inference Workflows Eqs. 11–12; `sec/X_suppl.tex`, Sec. Advanced Capabilities for T-Rex2: Region Classification Eq. and Open-set Video Object Detection.
[^trex2-2403-14610-v1-5]: `raw/arXiv-2403.14610v1/sec/4_experiments.tex`, Sec. Data Engines: text-prompt and visual-prompt engines; `sec/X_suppl.tex`, Sec. Data Engine Details and Tab. Data statistics of data collected.
[^trex2-2403-14610-v1-6]: `raw/arXiv-2403.14610v1/sec/4_experiments.tex`, Sec. Zero-Shot Generic Object Detection, Tab. One suit of weights for zero-shot object detection and Fig. Compare performance difference text vs visual on LVIS-val.
[^trex2-2403-14610-v1-7]: `raw/arXiv-2403.14610v1/sec/4_experiments.tex`, Sec. Zero-Shot Interactive Object Detection, Tab. One suit of weights for interactive object detection and Tab. Few-shot object counting on FSC147/FSCD-LVIS; `sec/X_suppl.tex`, Sec. Details on Object Counting Task.
[^trex2-2403-14610-v1-8]: `raw/arXiv-2403.14610v1/sec/4_experiments.tex`, Sec. Ablation Experiments: naive joint training and contrastive alignment, Tab. Ablation on text-visual synergy and Fig. t-SNE w/o vs w/ align.
[^trex2-2403-14610-v1-9]: `raw/arXiv-2403.14610v1/sec/4_experiments.tex`, Sec. Ablation Experiments: generic visual prompt, mixed prompt, data engines, inference speed; Tabs. number of visual prompts, mixed prompt mode, data engines, and time cost per module.
[^trex2-2403-14610-v1-10]: `raw/arXiv-2403.14610v1/sec/X_suppl.tex`, Sec. Region Classification Tab. Zero-shot region classification results; `sec/4_experiments.tex`, Sec. Conclusion/Limitations and mixed-prompt discussion.
[^gd15-2405-10300-v2-1]: `raw/arXiv-2405.10300v2/sec/03_model_training.tex`, Sec. Model Architecture/Grounding DINO 1.5 Pro, early- vs late-fusion discussion and negative-sampling balance; Fig. Overall Framework `figs/gd1.5_framework_v2.pdf`.
[^gd15-2405-10300-v2-2]: `raw/arXiv-2405.10300v2/sec/03_model_training.tex`, Sec. Training Dataset/Grounding-20M; `sec/01_abstract.tex` and `sec/02_intro_new.tex` for 20M+ grounding-image claim.
[^gd15-2405-10300-v2-3]: `raw/arXiv-2405.10300v2/sec/04_model_evaluation.tex`, Sec. Zero-Shot Transfer of Grounding DINO 1.5 Pro; `table/gd1.5_zero_shot_v2.tex`, Tab. COCO/LVIS/ODinW and `table/gd1.5_zero_shot_odinw13.tex`, Tab. ODinW13 detail.
[^gd15-2405-10300-v2-4]: `raw/arXiv-2405.10300v2/sec/04_model_evaluation.tex`, Sec. Fine-tuning Results on Downstream Datasets; `table/gd1.5_downstream_finetune.tex` and `table/gd1.5_downstream_finetune_odinw13.tex`.
[^gd15-2405-10300-v2-5]: `raw/arXiv-2405.10300v2/sec/05_case_analysis_and_vis.tex`, Secs. Common/Long-tailed/Short-caption/Long-caption/Dense/Video/Side-by-side Comparison; Figs. `figs/vis_v2/*`, `figs/vis/*` cited via captions and body text only.
[^sam2-2408-00714-v2-1]: `raw/arXiv-2408.00714v2/sam2.1_arxiv.tex`, Sec. Task: promptable visual segmentation plus Appendix Sec. Details on the PVS Task; Fig. `figs/pvs_vs_vos_boldtext.pdf` via caption and body text.
[^sam2-2408-00714-v2-2]: `raw/arXiv-2408.00714v2/sam2.1_arxiv.tex`, Sec. Model, prompt-encoder-and-mask-decoder paragraph plus Appendix Sec. Architecture, prompt-encoder-and-mask-decoder and Fig. `figs/model_diagram_zoomin_v3.pdf` via caption and body text.
[^sam2-2408-00714-v2-3]: `raw/arXiv-2408.00714v2/sam2.1_arxiv.tex`, Sec. Image segmentation Tab. `tab:sam_zs_comparison` plus Appendix Sec. Speed benchmarking (A100, torch.compile, bfloat16).
[^yoloe-2503-07465-v2-1]: `raw/arXiv-2503.07465v2/camera_ready.tex`, title/authors/abstract and Sec. Introduction, RepRTA/SAVPE/LRPC contributions and Fig. Comparison.
[^yoloe-2503-07465-v2-2]: `raw/arXiv-2503.07465v2/camera_ready.tex`, Sec. Methodology Model Architecture Eq. 1 and Sec. Re-parameterizable Region-Text Alignment Eqs. 2–3 plus Fig. RepRTA structure.
[^yoloe-2503-07465-v2-3]: `raw/arXiv-2503.07465v2/camera_ready.tex`, Sec. Semantic-Activated Visual Prompt Encoder Eq. 4 plus Fig. SAVPE structure and Sec. Lazy Region-Prompt Contrast Eq. 5.
[^yoloe-2503-07465-v2-4]: `raw/arXiv-2503.07465v2/camera_ready.tex`, Sec. Experiments Implementation Details and Sec. Training Objective plus Appendix More Implementation Details Tab. Data details and training hyperparameters.
[^yoloe-2503-07465-v2-5]: `raw/arXiv-2503.07465v2/camera_ready.tex`, Sec. Text and Visual Prompt Evaluation Tabs. Zero-shot detection and Segmentation evaluation on LVIS.
[^yoloe-2503-07465-v2-6]: `raw/arXiv-2503.07465v2/camera_ready.tex`, Sec. Prompt-free Evaluation Tab. Prompt-free evaluation on LVIS and Sec. Downstream Transferring Tab. Downstream transfer on COCO.
[^yoloe-2503-07465-v2-7]: `raw/arXiv-2503-07465v2/camera_ready.tex`, Sec. Ablation Study Tabs. Roadmap to YOLOE, Effectiveness of SAVPE, and Effectiveness of LRPC plus Appendix More Analyses for LRPC Fig. Retained anchor points.
[^sam3-2511-16719-v2-1]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Promptable Concept Segmentation (PCS) plus Fig. Task — NP plus positive/negative exemplar prompts, all-instances plus identities, <=30 s video, 3-expert oracle ambiguity handling.
[^sam3-2511-16719-v2-2]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Model Detector Architecture plus Presence Token plus Image Exemplars, Fig. ModelMain; Appendix Model Details Image/Text Encoders, Fusion Encoder, Decoder, Presence Head, Segmentation Head.
[^sam3-2511-16719-v2-3]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Model Tracker and Video Architecture plus Training Stages; Appendix Model Details plus Sec. Limitations for linear video cost and parallelization; Introduction for 30 ms H200 latency.
[^sam3-2511-16719-v2-4]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Data Engine Components plus Phases 1-4, Fig. DataEngine; Appendix Data Engine Details for ontology, Llama annotators, and MV/EV verifiers.
[^sam3-2511-16719-v2-5]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Segment Anything with Concepts Dataset Training Data plus Benchmark, Fig. MainPaperData; macro definitions for HQ/SYN/VIDEO/VEval scales.
[^sam3-2511-16719-v2-6]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Segment Anything with Concepts Dataset Metrics plus Handling Ambiguity; Appendix Dataset and Metric Details for cgF1/pmF1/IL_MCC/pHOTA and oracle protocol.
[^sam3-2511-16719-v2-7]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Experiments Image PCS with Text, Tab. pcs_img_perf — LVIS/COCO/SA-Co Gold/Silver/Bronze/Bio plus ADE/PC/Cityscapes.
[^sam3-2511-16719-v2-8]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Experiments Few-Shot Adaptation Tab. fewshot, PCS with 1 Exemplar Tab. coco_odin_performance, PCS with K Exemplars Fig. img_k_box, Object Counting Tab. counting-performance.
[^sam3-2511-16719-v2-9]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Experiments Video PCS with Text Tab. vis-results plus SAM 3 Agent Sec. agent_results Tab. agent.
[^sam3-2511-16719-v2-10]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Experiments Selected Ablations Tab. main_ablations; Appendix Ablations Model Ablations plus Image Training Data Ablations for presence, hard negatives, EXT/SYN/HQ, and encoder choice.
[^sam3-2511-16719-v2-11]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Experiments Domain adaptation ablation Fig. domain_adapt; Appendix Automatic Domain Adaptation Fig. domain_gen plus Image/Video Data Engine Annotation Speed Tabs. annotaion_ablation.
[^sam3-2511-16719-v2-12]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Conclusion plus Appendix Limitations; Appendix Object Multiplex for shared-memory scaling; Sec. Model and annotation cards for 172k A100 plus 86k H200 compute.

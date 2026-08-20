---
type: Concept
title: CLIP natural-language image pre-training
description: A contrastive image–text pre-training method that uses language prompts to synthesize zero-shot image classifiers.
tags: [multimodal-learning, contrastive-learning, zero-shot-transfer, prompt-engineering, representation-learning]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-20T10:14:19Z }
sources:
  - id: radford-2021-clip
    resource: ../raw/2103.00020_CLIP/clip_paper.tex
    title: Learning Transferable Visual Models From Natural Language Supervision
  - id: xu-2024-metaclip
    resource: ../raw/2309.16671_MetaCLIP/iclr2024_conference.tex
    title: Demystifying CLIP Data
  - id: xu-2022-bridgetower
    resource: ../raw/2206.08657_BridgeTower/main.tex
    title: "BridgeTower: Building Bridges Between Encoders in Vision-Language Representation Learning"
  - id: yang-2022-chinese-clip
    resource: ../raw/2211.01335_Chinese-CLIP/acl2023.tex
    title: "Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese"
  - id: chen-2022-altclip
    resource: ../raw/2211.06679_AltCLIP/main.tex
    title: "AltCLIP: Altering the Language Encoder in CLIP for Extended Language Capabilities"
  - id: zhai-2023-siglip
    resource: ../raw/2303.15343_SigLIP.md
    title: Sigmoid Loss for Language Image Pre-Training
  - id: chuang-2025-meta-clip-2
    resource: ../raw/2507.22062_MetaCLIP 2/paper.tex
    title: "Meta CLIP 2: A Worldwide Scaling Recipe"
  - id: singh-2022-flava
    resource: ../raw/2112.04482_FLAVA/arxiv_strip.tex
    title: "FLAVA: A Foundational Language And Vision Alignment Model"
  - id: zhou-2021-coop
    resource: ../raw/2109.01134_CoOp/main.tex
    title: Learning to Prompt for Vision-Language Models
  - id: zhou-2022-cocoop
    resource: ../raw/2203.05557_CoCoOp/arxiv.tex
    title: Conditional Prompt Learning for Vision-Language Models
  - id: wortsman-2021-wise-ft
    resource: ../raw/2109.01903_WiSE-FT/main.tex
    title: Robust fine-tuning of zero-shot models
  - id: zhang-2022-tip-adapter
    resource: ../raw/2111.03930_Tip-Adapter/ReviewTemplate.tex
    title: "Tip-Adapter: Training-free CLIP-Adapter for Better Vision-Language Modeling"
  - id: li-2022-declip
    resource: ../raw/2110.05208_DeCLIP/declip.tex
    title: "Supervision Exists Everywhere: A Data Efficient Contrastive Language-Image Pre-training Paradigm"
  - id: yao-2022-filip
    resource: ../raw/2111.07783_FILIP/filip_arxiv.tex
    title: "FILIP: Fine-grained Interactive Language-Image Pre-Training"
  - id: mu-2022-slip
    resource: ../raw/2112.12750_SLIP/slip.tex
    title: "SLIP: Self-supervision Meets Language-Image Pre-training"
  - id: li-2022-blip
    resource: ../raw/2201.12086_BLIP/main.tex
    title: "BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation"
  - id: yu-2022-coca
    resource: ../raw/2205.01917_CoCa/main.tex
    title: "CoCa: Contrastive Captioners are Image-Text Foundation Models"
  - id: khattak-2023-maple
    resource: ../raw/2210.03117_MaPLe/PaperForReview.tex
    title: "MaPLe: Multi-modal Prompt Learning"
  - id: cherti-2022-openclip-scaling
    resource: ../raw/2212.07143_OpenCLIP-Scaling/main.tex
    title: Reproducible scaling laws for contrastive language-image learning
  - id: khattak-2023-promptsrc
    resource: ../raw/2307.06948_PromptSRC/egpaper_final.tex
    title: "Self-regulating Prompts: Foundational Model Adaptation without Forgetting"
  - id: hassan-2023-promptalign
    resource: ../raw/2311.01459_TDA/Manuscript.tex
    title: "Align Your Prompts: Test-Time Prompting with Distribution Alignment for Zero-Shot Generalization"
  - id: wu-2024-caspl
    resource: ../raw/2409.17805_CasPL/main.tex
    title: Cascade Prompt Learning for Vision-Language Model Adaptation
  - id: zhang-2026-moe-vie
    resource: ../raw/2608.17402_MoE-ViE/main.tex
    title: "MoE-ViE: Mixture of Experts Vision Encoder for Efficient Image and Video Understanding"
---

# CLIP natural-language image pre-training

CLIP (Contrastive Language–Image Pre-training) jointly trains image and text encoders to match paired images and natural-language text. At inference, class descriptions embedded by the text encoder provide the weights of a zero-shot linear image classifier, making the output vocabulary configurable through language rather than a fixed training label set.[^radford-2021-clip]

## Method

- The authors trained from scratch on WIT, a 400-million image–text-pair dataset collected from public internet sources. Dataset construction sought broad visual-concept coverage using a 500,000-query list and capped results per query; the paper does not release WIT itself.[^radford-2021-clip]
- For a batch of $N$ paired examples, separate image and text encoders project L2-normalized features into a shared embedding space. A learned temperature scales the $N \times N$ pairwise cosine-similarity matrix, and symmetric image-to-text and text-to-image cross-entropy losses make matched pairs more similar than in-batch mismatches.[^radford-2021-clip]
- The paper evaluates modified ResNets and Vision Transformers as image encoders and a causal text Transformer. Its largest reported model, ViT-L/14@336px, was pre-trained for 32 epochs plus one higher-resolution epoch.[^radford-2021-clip]
- The authors attribute the method's training efficiency partly to replacing caption generation with paired-example discrimination: in their ablation, a bag-of-words contrastive objective reached a given zero-shot ImageNet accuracy about four times as efficiently as bag-of-words prediction and about twelve times as efficiently as their Transformer captioning baseline. These are experiment-specific comparisons, not general efficiency guarantees.[^radford-2021-clip]

## Zero-shot transfer and prompting

- To classify an image, CLIP compares its embedding with embeddings of candidate class texts and selects the highest-similarity text. This yields a multinomial logistic-regression classifier with normalized features and weights, no bias, and temperature scaling.[^radford-2021-clip]
- Context changes performance: the default template “A photo of a {label}.” improved ImageNet accuracy over bare labels, while task-specific templates and averaging text embeddings from multiple prompts improved it further. The paper reports that prompt engineering and ensembling improved ImageNet zero-shot accuracy by nearly five points over contextless class names.[^radford-2021-clip]
- The best model reported 76.2% ImageNet top-1 zero-shot accuracy, matching the original supervised ResNet-50 benchmark cited by the authors. Across 27 datasets, its zero-shot classifier exceeded a supervised linear classifier on ResNet-50 features on 16 datasets; these evaluations are evidence from the paper’s selected benchmark suite, not a universal capability claim.[^radford-2021-clip]

## Findings and limits

- On Flickr30k and MSCOCO retrieval, the paper reports that zero-shot CLIP matched or exceeded prior zero-shot results, but that fine-tuned systems remained materially stronger on MSCOCO; this is consistent with the dual encoder being useful for retrieval without establishing parity with task-specific fine-tuning.[^radford-2021-clip]
- A controlled ResNet-50 ablation found broadly similar average transfer from a filtered YFCC100M subset and an equal-sized WIT subset, while individual tasks diverged sharply. That result supports the contrastive recipe's use with reasonably filtered paired image–text data but does not show that curation choices are unimportant.[^radford-2021-clip]
- Average zero-shot error followed a smooth log–log trend across a 44-fold span of model compute, but individual task results were noisier. The authors also reported stronger natural-distribution-shift robustness for zero-shot CLIP than comparable ImageNet-trained models; adapting CLIP features to ImageNet improved in-distribution accuracy while slightly reducing average shift accuracy.[^radford-2021-clip]
- Zero-shot performance was weak on some specialized, abstract, or underrepresented tasks, including several fine-grained classifications, satellite imagery, counting, traffic signs, and distance estimation. It also generalized poorly to handwritten MNIST digits, which the authors attributed to their absence from pre-training-like data.[^radford-2021-clip]
- The paper repeatedly used full validation sets to guide development and assembled its broader 27-dataset suite around CLIP's capabilities; the authors therefore treat its zero-shot evaluation as an imperfect proxy for genuinely unseen tasks rather than an unbiased benchmark of general capability.[^radford-2021-clip]
- The paper’s overlap analysis detected a median 2.2% evaluation-set overlap across 35 datasets and reported that detected overlap rarely shifted overall accuracy by more than 0.1%; imperfect duplicate detection and distribution differences between overlap and clean subsets limit that estimate.[^radford-2021-clip]

## Risks and governance

The authors report that unfiltered internet image–text data can transmit social biases. Their exploratory probes found that classifications can vary materially with the supplied label set, wording, and thresholds, including denigrating and gendered associations. They also identify zero-shot identity recognition and bespoke surveillance classification as socially sensitive capabilities; reported results are characterization exercises, not evidence that these applications are appropriate or safe to deploy.[^radford-2021-clip]

The paper's FairFace probes further show that adding a `child` class changed the rate at which images of people under 20 were assigned crime-related or non-human labels, illustrating that class design can change observed harms. These exploratory results are not a comprehensive fairness assessment and do not validate face classification as an appropriate deployment use.[^radford-2021-clip]

## Relationships

- Used by: [BridgeTower layer-wise vision–language fusion](bridgetower-layerwise-vision-language-fusion.md) uses CLIP visual encoders in its reported configurations, but applies deep cross-modal fusion rather than CLIP's dual-encoder similarity scoring.[^xu-2022-bridgetower]
- Related: [ALIGN noisy image–text representation learning](align-noisy-image-text-learning.md) independently documents a dual-encoder, contrastive image–text approach at a larger scale with lightly filtered alt-text.
- Related: [LiT locked-image tuning](lit-locked-image-tuning.md) retains the contrastive dual-encoder interface but freezes a pretrained image tower rather than jointly training both towers from scratch.
- Extended by: [Chinese CLIP language-specific vision–language pre-training](chinese-clip-language-specific-vision-language-pretraining.md) initializes a Chinese text encoder alongside a CLIP vision tower, then unlocks both towers for Chinese-domain adaptation.[^yang-2022-chinese-clip]
- Extended by: [AltCLIP multilingual text-encoder alignment](altclip-multilingual-text-encoder-alignment.md) retains CLIP's image encoder, but distills an XLM-R text encoder from CLIP before contrastive text-only tuning for bilingual or multilingual support.[^chen-2022-altclip]
- Extended by: [SigLIP sigmoid contrastive language–image pre-training](siglip-sigmoid-contrastive-language-image-pretraining.md) replaces CLIP's symmetric global-softmax objective with independently scored sigmoid-loss terms for every image–text pair.[^zhai-2023-siglip]
- Extended by: [MoE-ViE mixture-of-experts vision encoder](moe-vie-mixture-of-experts-vision-encoder.md) retains contrastive image–text pretraining but sparsely scales all but the first vision-transformer FFN; its text tower remains dense during this stage.[^zhang-2026-moe-vie]
- Extended by: [MetaCLIP metadata-curated language–image pre-training](metaclip-metadata-curated-language-image-pretraining.md) operationalizes the original query-list and approximate class-balancing description as text-metadata curation without a pretrained model filter.[^xu-2024-metaclip]
- Extended by: [Meta CLIP 2 worldwide CLIP scaling](meta-clip-2-worldwide-clip-scaling.md) retains the CLIP-style dual-encoder setting while scaling metadata, curation, tokenization, training exposure, and capacity for native-language worldwide image–text data.[^chuang-2025-meta-clip-2]
- Related: [FLAVA foundational language and vision alignment](flava-foundational-language-vision-alignment.md) retains contrastive image-text alignment but adds a fusion transformer plus multimodal masked-modeling and matching objectives for multimodal reasoning.[^singh-2022-flava]
- Extended by: [CoOp context optimization](coop-context-optimization.md) freezes CLIP’s pretrained encoders and learns continuous prompt-context vectors from labeled downstream examples rather than manually selecting prompt wording.[^zhou-2021-coop]
- Extended by: [CoCoOp conditional context optimization](cocoop-conditional-context-optimization.md) keeps CLIP frozen but conditions learned prompt context on each image through a lightweight Meta-Net.[^zhou-2022-cocoop]
- Extended by: [MaPLe multimodal prompt learning](maple-multimodal-prompt-learning.md) keeps CLIP frozen but couples deep language prompts to image-encoder prompts through learned per-layer projections.[^khattak-2023-maple]
- Extended by: [PromptSRC self-regulating prompts](promptsrc-self-regulating-prompts.md) learns independent deep prompts in both branches and regularizes them against unprompted frozen-CLIP features.[^khattak-2023-promptsrc]
- Extended by: [PromptAlign test-time distribution alignment](promptalign-test-time-distribution-alignment.md) applies per-sample updates to multimodal prompts while retaining frozen CLIP encoders, combining entropy minimization with proxy-source visual-token distribution alignment.[^hassan-2023-promptalign]
- Extended by: [CasPL cascade prompt learning](caspl-cascade-prompt-learning.md) learns boosting prompts through unlabeled-domain distillation from a larger CLIP teacher, freezes them, then cascades them with a few-shot adapting-prompt method.[^wu-2024-caspl]
- Extended by: [OpenCLIP reproducible contrastive language–image scaling](openclip-reproducible-contrastive-language-image-scaling.md) uses CLIP-style contrastive dual encoders to measure how public LAION data, model capacity, and training exposure interact across downstream tasks.[^cherti-2022-openclip-scaling]
- Extended by: [Tip-Adapter cache-based few-shot CLIP adaptation](tip-adapter-cache-based-few-shot-clip-adaptation.md) preserves CLIP's visual encoder and text-derived classifier while adding cache retrieval over labeled few-shot image embeddings to its logits.[^zhang-2022-tip-adapter]
- Adapted by: [WiSE-FT robust zero-shot fine-tuning](wise-ft-robust-zero-shot-fine-tuning.md) fine-tunes CLIP then interpolates its weights with the original zero-shot checkpoint to trade target accuracy against distribution-shift performance.[^wortsman-2021-wise-ft]
- Extended by: [DeCLIP data-efficient contrastive language–image pre-training](declip-data-efficient-contrastive-language-image-pretraining.md) retains CLIP’s dual encoder and symmetric contrastive objective but adds unimodal self-supervision, augmented cross-modal views, and text-nearest-neighbor positives.[^li-2022-declip]
- Extended by: [FILIP fine-grained interactive language–image pre-training](filip-fine-grained-interactive-language-image-pretraining.md) retains independently encoded image and text towers, but replaces global embedding similarity with directional token-level late interaction.[^yao-2022-filip]
- Extended by: [SLIP self-supervised language-image pre-training](slip-self-supervised-language-image-pre-training.md) retains CLIP’s image-text contrastive branch and jointly trains the image encoder with an image-only self-supervised objective.[^mu-2022-slip]
- Related: [BLIP bootstrapping language–image pre-training](blip-bootstrapping-language-image-pre-training.md) retains contrastive image–text alignment but adds image-grounded matching and causal generation modes, plus caption-and-filter data bootstrapping.[^li-2022-blip]
- Extended by: [CoCa contrastive captioner image–text foundation model](coca-contrastive-captioner-image-text-foundation-model.md) retains aligned contrastive embeddings but adds a decoupled causal decoder for image-conditioned captioning and fused multimodal representations.[^yu-2022-coca]

[^radford-2021-clip]: Radford et al., “Learning Transferable Visual Models From Natural Language Supervision” (2021), [source manuscript](../raw/2103.00020_CLIP/clip_paper.tex).

[^xu-2024-metaclip]: Xu et al., “Demystifying CLIP Data” (2024), [source manuscript](../raw/2309.16671_MetaCLIP/iclr2024_conference.tex).

[^xu-2022-bridgetower]: Xu et al., “BridgeTower: Building Bridges Between Encoders in Vision-Language Representation Learning” (2022), [source manuscript](../raw/2206.08657_BridgeTower/main.tex).

[^yang-2022-chinese-clip]: Yang et al., “Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese” (2022), [source manuscript](../raw/2211.01335_Chinese-CLIP/acl2023.tex).

[^chen-2022-altclip]: Chen et al., “AltCLIP: Altering the Language Encoder in CLIP for Extended Language Capabilities” (2022), [source manuscript](../raw/2211.06679_AltCLIP/main.tex).

[^zhai-2023-siglip]: Zhai et al., “Sigmoid Loss for Language Image Pre-Training” (2023), [source](../raw/2303.15343_SigLIP.md).

[^chuang-2025-meta-clip-2]: Chuang et al., “Meta CLIP 2: A Worldwide Scaling Recipe” (2025), [source manuscript](../raw/2507.22062_MetaCLIP%202/paper.tex).

[^singh-2022-flava]: Singh et al., “FLAVA: A Foundational Language And Vision Alignment Model” (2022), [source manuscript](../raw/2112.04482_FLAVA/arxiv_strip.tex).

[^zhou-2021-coop]: Zhou et al., “Learning to Prompt for Vision-Language Models” (2021), [source manuscript](../raw/2109.01134_CoOp/main.tex).

[^zhou-2022-cocoop]: Zhou et al., “Conditional Prompt Learning for Vision-Language Models” (2022), [source manuscript](../raw/2203.05557_CoCoOp/arxiv.tex).

[^wortsman-2021-wise-ft]: Wortsman et al., “Robust fine-tuning of zero-shot models” (2021), [source manuscript](../raw/2109.01903_WiSE-FT/main.tex).

[^zhang-2022-tip-adapter]: Zhang et al., “Tip-Adapter: Training-free CLIP-Adapter for Better Vision-Language Modeling” (2022), [source manuscript](../raw/2111.03930_Tip-Adapter/ReviewTemplate.tex).

[^li-2022-declip]: Li et al., “Supervision Exists Everywhere: A Data Efficient Contrastive Language-Image Pre-training Paradigm” (2022), [source manuscript](../raw/2110.05208_DeCLIP/declip.tex).

[^yao-2022-filip]: Yao et al., “FILIP: Fine-grained Interactive Language-Image Pre-Training” (2022), [complete source manuscript](../raw/2111.07783_FILIP/filip_arxiv.tex).

[^mu-2022-slip]: Mu et al., “SLIP: Self-supervision Meets Language-Image Pre-training” (2022), [complete source manuscript](../raw/2112.12750_SLIP/slip.tex).

[^li-2022-blip]: Li et al., “BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation” (2022), [complete manuscript source](../raw/2201.12086_BLIP/main.tex).

[^yu-2022-coca]: Yu et al., “CoCa: Contrastive Captioners are Image-Text Foundation Models” (2022), [complete manuscript source](../raw/2205.01917_CoCa/main.tex).

[^khattak-2023-maple]: Khattak et al., “MaPLe: Multi-modal Prompt Learning” (2023), [complete source manuscript](../raw/2210.03117_MaPLe/PaperForReview.tex).

[^cherti-2022-openclip-scaling]: Cherti et al., “Reproducible scaling laws for contrastive language-image learning” (2022), [source manuscript](../raw/2212.07143_OpenCLIP-Scaling/main.tex).

[^khattak-2023-promptsrc]: Khattak et al., “Self-regulating Prompts: Foundational Model Adaptation without Forgetting” (2023), [complete manuscript source](../raw/2307.06948_PromptSRC/egpaper_final.tex).

[^hassan-2023-promptalign]: Hassan et al., “Align Your Prompts: Test-Time Prompting with Distribution Alignment for Zero-Shot Generalization” (2023), [complete manuscript source](../raw/2311.01459_TDA/Manuscript.tex).

[^wu-2024-caspl]: Wu et al., “Cascade Prompt Learning for Vision-Language Model Adaptation” (2024), [complete source manuscript](../raw/2409.17805_CasPL/main.tex).

[^zhang-2026-moe-vie]: Zhang et al., “MoE-ViE: Mixture of Experts Vision Encoder for Efficient Image and Video Understanding” (supplied manuscript, August 2026), [complete supplied manuscript source](../raw/2608.17402_MoE-ViE/main.tex).

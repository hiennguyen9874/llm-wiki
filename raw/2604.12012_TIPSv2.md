Title: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment

URL Source: https://arxiv.org/html/2604.12012

Published Time: Wed, 15 Apr 2026 00:07:22 GMT

Markdown Content:
# TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment

##### Report GitHub Issue

×

Title: 
Content selection saved. Describe the issue below:

Description: 

Submit without GitHub Submit in GitHub

[![Image 1: arXiv logo](https://arxiv.org/static/browse/0.3.4/images/arxiv-logo-one-color-white.svg)Back to arXiv](https://arxiv.org/)

[Why HTML?](https://info.arxiv.org/about/accessible_HTML.html)[Report Issue](https://arxiv.org/html/2604.12012# "Report an Issue")[Back to Abstract](https://arxiv.org/abs/2604.12012v1 "Back to abstract page")[Download PDF](https://arxiv.org/pdf/2604.12012v1 "Download PDF")[](javascript:toggleNavTOC(); "Toggle navigation")[](javascript:toggleReadingMode(); "Disable reading mode, show header and footer")[](javascript:toggleColorScheme(); "Toggle dark/light mode")
1.   [Abstract](https://arxiv.org/html/2604.12012#abstract1 "In TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
2.   [1 Introduction](https://arxiv.org/html/2604.12012#S1 "In TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
3.   [2 Related Work](https://arxiv.org/html/2604.12012#S2 "In TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
4.   [3 TIPSv2](https://arxiv.org/html/2604.12012#S3 "In TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    1.   [3.1 Preliminaries](https://arxiv.org/html/2604.12012#S3.SS1 "In 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    2.   [3.2 Bridging Pretraining and Distillation](https://arxiv.org/html/2604.12012#S3.SS2 "In 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    3.   [3.3 iBOT++](https://arxiv.org/html/2604.12012#S3.SS3 "In 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    4.   [3.4 Head-only EMA](https://arxiv.org/html/2604.12012#S3.SS4 "In 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    5.   [3.5 Multi-Granularity Text Captions](https://arxiv.org/html/2604.12012#S3.SS5 "In 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")

5.   [4 Results](https://arxiv.org/html/2604.12012#S4 "In TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    1.   [4.1 Experimental Setup](https://arxiv.org/html/2604.12012#S4.SS1 "In 4 Results ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    2.   [4.2 Ablations](https://arxiv.org/html/2604.12012#S4.SS2 "In 4 Results ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    3.   [4.3 Comparisons with Other Vision Encoders](https://arxiv.org/html/2604.12012#S4.SS3 "In 4 Results ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")

6.   [5 Conclusion](https://arxiv.org/html/2604.12012#S5 "In TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
7.   [A Appendix](https://arxiv.org/html/2604.12012#A1 "In TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    1.   [A.1 Applying iBOT++ to CLIP](https://arxiv.org/html/2604.12012#A1.SS1 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    2.   [A.2 iBOT++ Ablation Study on Masking Ratios](https://arxiv.org/html/2604.12012#A1.SS2 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    3.   [A.3 Ablations on Multi-Granularity Captions](https://arxiv.org/html/2604.12012#A1.SS3 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    4.   [A.4 Qualitative Comparisons to DINOv2 and v3](https://arxiv.org/html/2604.12012#A1.SS4 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    5.   [A.5 Qualitative Analysis: iBOT++ vs iBOT](https://arxiv.org/html/2604.12012#A1.SS5 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    6.   [A.6 Zero-shot Segmentation with SigLIP2](https://arxiv.org/html/2604.12012#A1.SS6 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    7.   [A.7 TIPSv2 Family](https://arxiv.org/html/2604.12012#A1.SS7 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    8.   [A.8 Performance of TIPSv2 against Competitors](https://arxiv.org/html/2604.12012#A1.SS8 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")
    9.   [A.9 Additional Implementation Details](https://arxiv.org/html/2604.12012#A1.SS9 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")

8.   [References](https://arxiv.org/html/2604.12012#bib "In TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")

[License: CC BY 4.0](https://info.arxiv.org/help/license/index.html#licenses-available)

 arXiv:2604.12012v1 [cs.CV] 13 Apr 2026

# TIPSv2: 

Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment

 Bingyi Cao 1 1 1 Authors contributed equally. Koert Chen 1 1 1 Authors contributed equally. Kevis-Kokitsi Maninis Kaifeng Chen 2 2 2 Kaifeng Chen is now with xAI, Arjun Karpur with Epsilon Health, Bohyung Han with Seoul National University and Washington Ramos with Google. 

Correspondence: $\left{\right.$bingyi,koert,andrearaujo$\left.\right}$@google.com Arjun Karpur 2 2 2 Kaifeng Chen is now with xAI, Arjun Karpur with Epsilon Health, Bohyung Han with Seoul National University and Washington Ramos with Google. 

Correspondence: $\left{\right.$bingyi,koert,andrearaujo$\left.\right}$@google.com

 Ye Xia Sahil Dua Tanmaya Dabral Guangxing Han Bohyung Han 2 2 2 Kaifeng Chen is now with xAI, Arjun Karpur with Epsilon Health, Bohyung Han with Seoul National University and Washington Ramos with Google. 

Correspondence: $\left{\right.$bingyi,koert,andrearaujo$\left.\right}$@google.com Joshua Ainslie 

 Alex Bewley Mithun Jacob René Wagner Washington Ramos 2 2 2 Kaifeng Chen is now with xAI, Arjun Karpur with Epsilon Health, Bohyung Han with Seoul National University and Washington Ramos with Google. 

Correspondence: $\left{\right.$bingyi,koert,andrearaujo$\left.\right}$@google.com Krzysztof Choromanski 

 Mojtaba Seyedhosseini Howard Zhou André Araujo

Google DeepMind

###### Abstract

Recent progress in vision-language pretraining has enabled significant improvements to many downstream computer vision applications, such as classification, retrieval, segmentation and depth prediction. However, a fundamental capability that these models still struggle with is aligning dense patch representations with text embeddings of corresponding concepts. In this work, we investigate this critical issue and propose novel techniques to enhance this capability in foundational vision-language models. First, we reveal that a patch-level distillation procedure significantly boosts dense patch-text alignment – surprisingly, the patch-text alignment of the distilled student model strongly surpasses that of the teacher model. This observation inspires us to consider modifications to pretraining recipes, leading us to propose iBOT++, an upgrade to the commonly-used iBOT masked image objective, where unmasked tokens also contribute directly to the loss. This dramatically enhances patch-text alignment of pretrained models. Additionally, to improve vision-language pretraining efficiency and effectiveness, we modify the exponential moving average setup in the learning recipe, and introduce a caption sampling strategy to benefit from synthetic captions at different granularities. Combining these components, we develop TIPSv2, a new family of image-text encoder models suitable for a wide range of downstream applications. Through comprehensive experiments on 9 tasks and 20 datasets, we demonstrate strong performance, generally on par with or better than recent vision encoder models. Code and models are released via our project page at [https://gdm-tipsv2.github.io/](https://gdm-tipsv2.github.io/).

## 1 Introduction

![Image 2: Refer to caption](https://arxiv.org/html/2604.12012v1/x1.png)

Figure 1: TIPSv2’s improvement to the masked image modeling pretraining strategy. As part of our complete TIPSv2 method, we introduce iBOT++ (bottom), a simple modification to the well-known iBOT[[68](https://arxiv.org/html/2604.12012#bib.bib68)] self-supervised objective (top-left), where visible tokens also contribute directly to the loss. This enhancement dramatically improves patch-text alignment, as demonstrated by zero-shot image segmentation results (top-right). 

Large-scale self-supervised and vision-language pretraining methods have fundamentally reshaped visual representation learning, establishing new performance standards across a broad spectrum of tasks. Leading approaches generally fall into two categories: weakly-supervised contrastive or sigmoid methods, exemplified by CLIP[[40](https://arxiv.org/html/2604.12012#bib.bib40)], SigLIP [[64](https://arxiv.org/html/2604.12012#bib.bib64)] and Perception Encoder (PE)[[4](https://arxiv.org/html/2604.12012#bib.bib4)], which provide robust image-text alignment and zero-shot capabilities; and self-supervised learning (SSL) methods, such as DINO[[45](https://arxiv.org/html/2604.12012#bib.bib45), [5](https://arxiv.org/html/2604.12012#bib.bib5), [38](https://arxiv.org/html/2604.12012#bib.bib38)] and iBOT[[68](https://arxiv.org/html/2604.12012#bib.bib68)], which excel at spatial understanding for dense downstream tasks (e.g., depth, segmentation).

Achieving a unified representation that excels simultaneously at global (image-level) and dense (patch-level) understanding remains a significant challenge. State-of-the-art (SOTA) models often optimize one at the expense of the other: for example, DINOv2[[38](https://arxiv.org/html/2604.12012#bib.bib38)] excels at dense vision tasks but lacks inherent text alignment for vision-language capabilities, whereas PE-core[[4](https://arxiv.org/html/2604.12012#bib.bib4)] provides robust image-text alignment but underperforms on dense tasks. Recent unified approaches, such as TIPS[[33](https://arxiv.org/html/2604.12012#bib.bib33)] and SigLIP2[[50](https://arxiv.org/html/2604.12012#bib.bib50)], have made significant strides in bridging this divide. However, we find that even these modern models struggle to maintain precise pixel- or patch-level alignment with text—a capability essential for advanced tasks like open-vocabulary segmentation. Self-supervised works such as DINO.txt[[29](https://arxiv.org/html/2604.12012#bib.bib29)] and DINOv3[[45](https://arxiv.org/html/2604.12012#bib.bib45)] attempt to address this by training supplementary text encoders, but still exhibit limited performance on multimodal tasks. Overall, grounded alignment with text remains a challenging task. This is corroborated by PE[[4](https://arxiv.org/html/2604.12012#bib.bib4)], which finds that final transformer layers often function as global contrastive “decoders”, rather than preserving the local semantics.

In this work, we first uncover a surprising trend in SOTA vision encoders [[33](https://arxiv.org/html/2604.12012#bib.bib33), [50](https://arxiv.org/html/2604.12012#bib.bib50)]: the largest flagship models often underperform their smaller counterparts in patch-text alignment. Investigating this issue with a recent spatially-aware multimodal encoder[[33](https://arxiv.org/html/2604.12012#bib.bib33)], we find that distillation significantly improves grounding alignment by applying effective supervision across all patch tokens. This insight not only explains the performance gap, but also helps us unlock broader capabilities through a novel pretraining recipe.

We introduce TIPSv2, the second version of the TIPS[[33](https://arxiv.org/html/2604.12012#bib.bib33)] model family (T ext-I mage P retraining with S patial awareness), a novel methodology designed to bridge this gap directly during pretraining. TIPSv2 incorporates a new objective, iBOT++, which translates our distillation findings into a self-supervised pretraining objective that enforces representation consistency on visible tokens, as per [Fig.1](https://arxiv.org/html/2604.12012#S1.F1 "In 1 Introduction ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"). We further enhance this with multi-granularity text augmentation (leveraging captions from PaliGemma [[3](https://arxiv.org/html/2604.12012#bib.bib3)] and Gemini [[22](https://arxiv.org/html/2604.12012#bib.bib22)]) and a resource-efficient Exponential Moving Average (EMA) strategy. While standard SSL often requires full-model EMA, the presence of text supervision allows us to use a ‘head-only EMA’. This updates only the projection layers, drastically reducing memory requirements at training time. TIPSv2 provides an efficient training framework yielding a highly effective image-text encoder across standard benchmarks. It sets new SOTA results in zero-shot semantic segmentation, while providing strong performance on a wide range of downstream multimodal tasks. In summary, our primary contributions are:

*   •A novel finding that a distillation procedure tuned to strengthen spatial awareness unlocks strong gains in patch-text alignment. Our detailed study pinpoints masking removal and initialization as the key factors driving this phenomenon. 
*   •iBOT++, a novel self-supervised masked objective that enhances pretraining to enforce representation consistency and significantly improves patch-text alignment – see [Fig.1](https://arxiv.org/html/2604.12012#S1.F1 "In 1 Introduction ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"). 
*   •An efficient and effective training recipe leveraging multi-granularity text augmentation and a novel head-only EMA mechanism, overall achieving strong performance with significantly reduced training cost, validated comprehensively on 9 tasks spanning 20 datasets. 

## 2 Related Work

There are currently three dominant paradigms for large-scale pretraining of versatile image representations: self-supervised visual learning[[7](https://arxiv.org/html/2604.12012#bib.bib7), [2](https://arxiv.org/html/2604.12012#bib.bib2), [25](https://arxiv.org/html/2604.12012#bib.bib25)], image-text contrastive learning[[40](https://arxiv.org/html/2604.12012#bib.bib40), [28](https://arxiv.org/html/2604.12012#bib.bib28), [10](https://arxiv.org/html/2604.12012#bib.bib10)] or image captioning[[49](https://arxiv.org/html/2604.12012#bib.bib49), [55](https://arxiv.org/html/2604.12012#bib.bib55), [20](https://arxiv.org/html/2604.12012#bib.bib20)]. In this work, we build on top of self-supervised and image-text contrastive techniques to construct visual representations that are natively text-aligned and spatially aware. We review relevant work in these areas and contextualize our advances with respect to them.

Self-supervised learning methods enable visual pretraining without the use of any labels, by formulating pretext tasks that derive supervisory signals from the images themselves. Landmark approaches in this area, such as DINO[[5](https://arxiv.org/html/2604.12012#bib.bib5)] and iBOT[[68](https://arxiv.org/html/2604.12012#bib.bib68)], enforce representational invariances to image augmentations such as crops, flips, color distortions and masking. These methods adopt a student-teacher distillation setup, where the teacher model is constructed as an exponential moving average (EMA) of the student[[24](https://arxiv.org/html/2604.12012#bib.bib24)]. DINOv2[[38](https://arxiv.org/html/2604.12012#bib.bib38)] combines these strategies into a well-tuned recipe which was scaled on a curated training set. More recently, DINOv3[[45](https://arxiv.org/html/2604.12012#bib.bib45)] and WebSSL[[16](https://arxiv.org/html/2604.12012#bib.bib16)] scale this recipe even further to image encoders with $7$B parameters, on $2$B curated images.

Our proposed TIPSv2 framework leverages self-supervised losses, making two contributions to enhance them. First, we extend the iBOT[[68](https://arxiv.org/html/2604.12012#bib.bib68)] masked image modeling (MIM) strategy to introduce our novel iBOT++ technique, which enables direct supervision on both visible and masked tokens at pretraining time – this simple change dramatically boosts patch-text alignment and benefits several downstream tasks. Examples in the literature have some similarities to the iBOT++ strategy. DMAE[[57](https://arxiv.org/html/2604.12012#bib.bib57)] predicts visible and masked patches (not tokens), focusing on robust classifiers. SimMIM[[58](https://arxiv.org/html/2604.12012#bib.bib58)] also attempted predicting visible patches, but found it ineffective. MaskAlign[[60](https://arxiv.org/html/2604.12012#bib.bib60)] and MR-MAE[[21](https://arxiv.org/html/2604.12012#bib.bib21)] align student visible tokens with those of pretrained frozen models. To the best of our knowledge, overall, supervising both visible and masked tokens as part of MIM pretraining was unexplored. Second, we introduce a significant simplification to the widely-used EMA learning setup[[24](https://arxiv.org/html/2604.12012#bib.bib24)], where only projection heads undergo EMA updates and a single vision encoder is used. This is particularly effective in our setup because the additional image-text contrastive loss generally provides a stable signal preventing model collapse. This reduces the number of trainable parameters by nearly half, enabling much more efficient scaling. Other methods which combine SSL and contrastive image-text techniques are SILC[[36](https://arxiv.org/html/2604.12012#bib.bib36)], TIPS[[33](https://arxiv.org/html/2604.12012#bib.bib33)] and SigLIP2[[50](https://arxiv.org/html/2604.12012#bib.bib50)]: all of them employ EMA teachers but do not consider simplifications in this component.

Contrastive vision-language pretraining was introduced by CLIP[[40](https://arxiv.org/html/2604.12012#bib.bib40)] and ALIGN[[28](https://arxiv.org/html/2604.12012#bib.bib28)], leveraging web-scale image datasets with weakly supervised text labels. More recent instantiations in this area include OpenCLIP[[10](https://arxiv.org/html/2604.12012#bib.bib10)], SigLIP[[64](https://arxiv.org/html/2604.12012#bib.bib64)], Perception Encoder[[4](https://arxiv.org/html/2604.12012#bib.bib4)], EVA[[18](https://arxiv.org/html/2604.12012#bib.bib18), [19](https://arxiv.org/html/2604.12012#bib.bib19), [48](https://arxiv.org/html/2604.12012#bib.bib48)] and MetaCLIP[[59](https://arxiv.org/html/2604.12012#bib.bib59), [11](https://arxiv.org/html/2604.12012#bib.bib11)]. Some methods in this area[[31](https://arxiv.org/html/2604.12012#bib.bib31), [17](https://arxiv.org/html/2604.12012#bib.bib17), [33](https://arxiv.org/html/2604.12012#bib.bib33), [47](https://arxiv.org/html/2604.12012#bib.bib47)] explore the use of synthetic image captions for contrastive image-text training. In our TIPSv2 model, we go beyond these to combine noisy web captions with synthetic captions at different granularities, providing a range of possible textual descriptions for images, increasing the robustness of the model.

Knowledge distillation[[26](https://arxiv.org/html/2604.12012#bib.bib26)] techniques have been frequently used to train smaller vision-language encoders[[33](https://arxiv.org/html/2604.12012#bib.bib33), [50](https://arxiv.org/html/2604.12012#bib.bib50), [4](https://arxiv.org/html/2604.12012#bib.bib4)], enabling high performance at a much cheaper compute budget. In this work, one of our contributions is to show for the first time that distillation procedures, tuned to strengthen spatial awareness, can be helpful to enhance patch-text alignment of these models. Surprisingly, even large pretrained models with weak patch-text alignment can be distilled into smaller models to enhance this capability.

## 3 TIPSv2

### 3.1 Preliminaries

Our method builds on top of the previous TIPS[[33](https://arxiv.org/html/2604.12012#bib.bib33)] version, a recent vision encoder pretraining method that integrates contrastive image-text learning with self-supervised learning. In this section, we review the necessary background and introduce the notation used throughout the paper. Given a collection of image-text pairs $\left{\right. \left(\right. I_{k} , T_{k} \left.\right) \left.\right}$, we learn an image encoder $f$ mapping an image $I$ to image embeddings $\left{\right. 𝐞^{g} , 𝐞_{1} , 𝐞_{2} , \ldots , 𝐞_{N} \left.\right}$ and a text encoder $g$ mapping texts $T$ to a text embedding $𝐞^{t}$. Let $f^{g} ​ \left(\right. I \left.\right) = 𝐞^{g}$ be the global embedding representation of the entire image and $f ​ \left(\right. I \left.\right) = \left{\right. 𝐞_{1} , 𝐞_{2} , \ldots , 𝐞_{N} \left.\right}$ the patch embeddings corresponding to different image regions. $f$ is modeled as a Vision Transformer (ViT)[[13](https://arxiv.org/html/2604.12012#bib.bib13)] and $g$ is modeled as a standard transformer [[53](https://arxiv.org/html/2604.12012#bib.bib53)]. The loss is given by $\mathcal{L} = \mathcal{L}_{\text{CLIP}} + \mathcal{L}_{\text{DINO}} + \mathcal{L}_{\text{iBOT}}$, and each component is detailed below.

Image-text contrastive loss. The first component, $\mathcal{L}_{\text{CLIP}}$, aligns image and text modalities. Following the approach of CLIP[[40](https://arxiv.org/html/2604.12012#bib.bib40)], $\mathcal{L}_{\text{CLIP}}$ is an InfoNCE[[51](https://arxiv.org/html/2604.12012#bib.bib51)] loss that pushes $𝐞^{g}$ and $𝐞^{t}$ close for corresponding images and captions, and far otherwise. TIPS adapts this by introducing two separate CLS global embeddings: one supervised by web alt-text captions for object-centric details, and another supervised by PaliGemma[[3](https://arxiv.org/html/2604.12012#bib.bib3)] synthetic captions designed to better capture dense spatial relationships.

Global- and patch-level SSL. In addition, TIPS applies two forms of self-supervised losses to boost spatial awareness, using a teacher network $f_{t}$ that is the exponential moving average (EMA) of the student network $f_{s}$. In these losses, the teacher network $f_{t}$ processes the original image $I$, and the student network $f_{s}$ processes a crop or masked view. Then, these embeddings are projected into a higher “prototype” dimension by head networks $h_{s}$ and $h_{t}$, and the resulting prototypes are supervised to be invariant to these transformations by a cross-entropy loss. In the global-level self-distillation objective (DINO[[5](https://arxiv.org/html/2604.12012#bib.bib5)]), the student representations of $M$ local crops $\left(\left{\right. I_{i} \left.\right}\right)_{i = 1}^{M}$ are compared to the teacher representation of $I$ on global embeddings:

$\mathcal{L}_{\text{DINO}} = - \sum_{i = 1}^{M} h_{t} ​ \left(\left(\right. f_{t}^{g} ​ \left(\right. I \left.\right) \left.\right)\right)^{T} ​ log ⁡ h_{s} ​ \left(\right. f_{s}^{g} ​ \left(\right. I_{i} \left.\right) \left.\right)$(1)

Table 1: Zero-shot segmentation with a large teacher model and its distilled student. Surprisingly, the TIPS ViT-L model, which is a student distilled from the TIPS ViT-g teacher, significantly surpasses it.

| Model | Zero-shot Segmentation (mIoU) $\uparrow$ |
| --- |
| PC59 | PC60 | VOC21 | ADE150 |
| TIPS ViT-L | 33.5 | 30.4 | 30.5 | 20.8 |
| TIPS ViT-g | 11.4 | 10.8 | 19.7 | 2.6 |

In the patch-level MIM objective (iBOT[[68](https://arxiv.org/html/2604.12012#bib.bib68)]), a random binary mask $m$ is applied to image patches to obtain masked view $I_{\text{mask}}$ ($m_{i} = 1$ denotes that the $i$-th patch is masked). Then, the student representation of $I_{\text{mask}}$ is compared to the teacher representation of $I$ on patch embeddings:

$\mathcal{L}_{\text{iBOT}} = - \sum_{i = 1}^{N} m_{i} ​ h_{t} ​ \left(\left(\right. f_{t} ​ \left(\left(\right. I \left.\right)\right)_{i} \left.\right)\right)^{T} ​ log ⁡ h_{s} ​ \left(\right. f_{s} ​ \left(\left(\right. I_{\text{mask}} \left.\right)\right)_{i} \left.\right)$(2)

| Setting | Initialization / Update | Masking Ratio | Zero-shot Segmentation (mIoU) $\uparrow$ |
| --- | --- | --- | --- |
| Text Encoder | Student Encoder |  | PC59 | PC60 | VOC21 | ADE150 |
| (1) pretraining | Random / ![Image 3: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | Random / ![Image 4: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | 0.75 | 6.9 | 6.6 | 6.7 | 0.3 |
| (2) distillation | Random / ![Image 5: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | Random / ![Image 6: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | 0.75 | 16.0 | 15.4 | 22.5 | 5.9 |
| (3) distillation | Random / ![Image 7: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | Random / ![Image 8: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | 0.5 | 15.5 | 14.5 | 24.0 | 7.0 |
| (4) distillation | Random / ![Image 9: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | Random / ![Image 10: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | 0.0 | 31.4 | 28.6 | 30.8 | 20.0 |
| (5) distillation | Pretrained / ![Image 11: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | Random / ![Image 12: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | 0.0 | 31.1 | 28.5 | 31.9 | 20.5 |
| (6) distillation | Pretrained / ![Image 13: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | Random / ![Image 14: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | 0.0 | 30.1 | 27.7 | 28.4 | 20.0 |
| (7) distillation | Pretrained / ![Image 15: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | Pretrained / ![Image 16: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf) | 0.0 | 6.4 | 6.0 | 6.7 | 2.4 |

Table 2: Initialization and masking ablations for distillation. Comparing TIPS ViT-L models re-trained with different strategies. We highlight best and second-best overall. Initialization is either from scratch (“Random”) or initialized from the teacher model (“Pretrained”). Update is either training (![Image 17: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf)) or frozen (![Image 18: Refer to caption](https://arxiv.org/html/2604.12012v1/all-twemojis.pdf)). The results show that removing masking and randomly initializing the student image encoder are critical for achieving strong patch-text alignment. 

![Image 19: Refer to caption](https://arxiv.org/html/2604.12012v1/figures/patch_loss.png)

Figure 2:  The decrease in patch-level loss for visible tokens using iBOT++ indicates successful anchoring to the teacher’s tokens, which does not happen for iBOT. 

Distillation. TIPS also distills a family of smaller models with a simple strategy that mirrors the pretraining setup. Distillation only requires two modifications: the teacher network $f_{t}$ is replaced with a frozen larger teacher instead of an EMA copy of $f_{s}$, and no mask is applied at the patch-level loss.

### 3.2 Bridging Pretraining and Distillation

In this section, we study the effect of distillation techniques on patch-text alignment. Our main finding is that the patch-level distillation procedure can significantly enhance patch-text alignment, even when utilizing a teacher with poor alignment. To demonstrate this, we begin by evaluating patch-text alignment using standard zero-shot semantic segmentation benchmarks: ADE150[[65](https://arxiv.org/html/2604.12012#bib.bib65), [66](https://arxiv.org/html/2604.12012#bib.bib66)], Pascal Context (PC59/PC60)[[35](https://arxiv.org/html/2604.12012#bib.bib35)], and Pascal VOC (VOC21)[[15](https://arxiv.org/html/2604.12012#bib.bib15)].

As shown in [Tab.1](https://arxiv.org/html/2604.12012#S3.T1 "In 3.1 Preliminaries ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), the largest pretrained ViT-g TIPS model significantly underperforms the smaller ViT-L student model (which is distilled from the ViT-g) in the task of zero-shot segmentation, reversing the trend of all other tasks reported in [[33](https://arxiv.org/html/2604.12012#bib.bib33)]. This discrepancy suggests that while the pre-training recipe at the ViT-g scale is highly effective for image-only or global tasks, it fails to induce strong patch-text alignment, a capability apparently gained during distillation. To disentangle the factors distinguishing pretraining from distillation, [Tab.2](https://arxiv.org/html/2604.12012#S3.T2 "In Figure 2 ‣ 3.1 Preliminaries ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") presents ablations using a ViT-L self-distillation baseline. We systematically vary the masking ratio and model initialization/freezing parameters to isolate their individual contributions:

*   •Distillation method: The models in rows (2-7) are distilled from the frozen ViT-L teacher trained in row (1). These follow the distillation procedure of [[33](https://arxiv.org/html/2604.12012#bib.bib33)] described in [Sec.3.1](https://arxiv.org/html/2604.12012#S3.SS1 "3.1 Preliminaries ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), except that the teacher is the same size as the student, to study the setting of distillation in isolation from the effect of a larger teacher. The other differences from vanilla distillation are described row-by-row. 
*   •Masking ratio: We ablate the effect of masking ratio by lowering it through rows (2-4). In (2), the ratio is the same as vanilla pre-training, and in (4) it is lowered to no masking, which is the ratio in vanilla distillation. Observe that row (2) is the pre-training setting with two key changes: the teacher is frozen and, more importantly, the patch-level loss is also applied to the $25 \%$ of unmasked tokens instead of unsupervised as in pre-training. This configuration already yields a significant enhancement in zero-shot segmentation, demonstrating the potential of patch-level distillation for improving patch-text alignment. In contrast, observe that (4) exactly matches the vanilla distillation of [[33](https://arxiv.org/html/2604.12012#bib.bib33)]. The increase in patch-text alignment from rows (2-4) as we lower the masking ratio indicates that the loss on visible tokens is critical for achieving improved patch-text alignment during distillation. 
*   •Initialization and freezing: We ablate the effect of random vs. pre-trained initialization and freezing the text encoder in the remaining rows. We find that the text encoder is less sensitive to initialization in rows (4–6). However, row (7) demonstrates that random initialization is essential for the vision encoder. Initializing distillation with the pre-trained visual encoder as in row (7) completely eliminates the advantage from distillation, reducing it to the performance of the original pre-trained model. This suggests that the model must break away from the pretrained convergence region to learn effectively during distillation. 

These findings suggest that supervising all patch tokens, rather than just masked ones, is crucial for alignment during distillation. We leverage these insights to formulate a novel pretraining strategy, to be discussed next. An overview of the final TIPSv2 pretraining recipe is presented in [Fig.3](https://arxiv.org/html/2604.12012#S3.F3 "In 3.3 iBOT++ ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment").

### 3.3 iBOT++

As discussed in [Sec.3.1](https://arxiv.org/html/2604.12012#S3.SS1 "3.1 Preliminaries ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), both the pretraining and distillation stages of the vision encoder reference method incorporate a patch-level loss. The pretraining phase employs the iBOT [[68](https://arxiv.org/html/2604.12012#bib.bib68)] MIM objective, where the student reconstructs masked tokens by matching the features of a teacher encoder that processes the unmasked image. For distillation, masking is removed entirely, so both the student and teacher see the unmasked image.

Based on [Sec.3.2](https://arxiv.org/html/2604.12012#S3.SS2 "3.2 Bridging Pretraining and Distillation ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), we hypothesize that limiting loss to masked regions discourages preserving local semantics. To resolve this, we propose iBOT++, a modification to iBOT which applies the patch-level loss to all patches, both masked and unmasked. This simple change represents a significant improvement to the pretraining stage of TIPS. The improved loss $\mathcal{L}_{\text{iBOT}++}$ differs from the original $\mathcal{L}_{\text{iBOT}}$ in [Eq.2](https://arxiv.org/html/2604.12012#S3.E2 "In 3.1 Preliminaries ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") only in that the loss also applies on visible tokens:

$\mathcal{L}_{\text{iBOT}++} = - \sum_{i = 1}^{N} h_{t} ​ \left(\left(\right. f_{t} ​ \left(\left(\right. I \left.\right)\right)_{i} \left.\right)\right)^{T} ​ log ⁡ h_{s} ​ \left(\right. f_{s} ​ \left(\left(\right. I_{\text{mask}} \left.\right)\right)_{i} \left.\right)$(3)

While foundational vision encoders[[33](https://arxiv.org/html/2604.12012#bib.bib33), [38](https://arxiv.org/html/2604.12012#bib.bib38), [45](https://arxiv.org/html/2604.12012#bib.bib45)] require high masking ratios (e.g., $75 \%$) for successful MIM[[25](https://arxiv.org/html/2604.12012#bib.bib25)] in pre-training, we found in [Sec.3.2](https://arxiv.org/html/2604.12012#S3.SS2 "3.2 Bridging Pretraining and Distillation ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") that distillation instead benefits substantially from matching student to teacher representations across all tokens without masking. iBOT++ operates as an intermediate between these two objectives: we retain the masking mechanism but extend the supervision to visible tokens, requiring the student to align with teacher representations for both masked and unmasked patches. Replacing iBOT with iBOT++ in TIPS pretraining yields significant gains in zero-shot segmentation ([Tab.3](https://arxiv.org/html/2604.12012#S3.T3 "In 3.4 Head-only EMA ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")), indicating superior patch-text alignment. [Sec.4](https://arxiv.org/html/2604.12012#S4 "4 Results ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") demonstrates that iBOT++ also generally benefits other tasks.

![Image 20: Refer to caption](https://arxiv.org/html/2604.12012v1/x2.png)

Figure 3: TIPSv2 pretraining overview. TIPSv2 introduces $3$ improvements (highlighted in green borders) to the combined contrastive and self-supervised approach to pretrain vision encoders. iBOT++ is an enhanced masked image modeling loss. Head-only EMA enables memory-efficient self-supervised losses. Multi-granularity captions provide a range of possible textual descriptions for images, increasing the robustness of the model. 

Note that standard iBOT lacks direct supervision on visible tokens, which allows their representations to behave arbitrarily provided they suffice for reconstructing masked tokens. Enforcing alignment on unmasked tokens enables iBOT++ to anchor student patch representations to the teacher’s. This is demonstrated in [Fig.2](https://arxiv.org/html/2604.12012#S3.F2 "In 3.1 Preliminaries ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), which indicates through the proxy of patch-level loss that the representations of visible patches remain poor in iBOT but improve in iBOT++. Overall, iBOT++ delivers superior performance by simultaneously capturing global context for reconstruction and preserving local semantics.

### 3.4 Head-only EMA

Standard self-distillation [[5](https://arxiv.org/html/2604.12012#bib.bib5), [68](https://arxiv.org/html/2604.12012#bib.bib68), [38](https://arxiv.org/html/2604.12012#bib.bib38), [33](https://arxiv.org/html/2604.12012#bib.bib33)] relies on an EMA teacher network to provide stable targets via temporal ensembling. Crucially, in the context of SSL-only methods, an EMA teacher with a stop gradient avoids[[23](https://arxiv.org/html/2604.12012#bib.bib23)] the trivial solution where the prototype representations of student $h_{s} ​ \left(\right. f_{s} ​ \left(\right. I \left.\right) \left.\right)$ and teacher $h_{t} ​ \left(\right. f_{t} ​ \left(\right. I \left.\right) \left.\right)$ collapse to a constant representation regardless of input $I$. This collapse can happen at either the encoder $f_{s} , f_{t}$ or at the head $h_{s} , h_{t}$. However, in the context of combined SSL and image-text contrastive learning, the encoders $f_{s}$ and $f_{t}$ are already constrained to prevent collapse by the contrastive loss $\mathcal{L}_{\text{CLIP}}$. As a result, we propose that it is sufficient to use the EMA teacher only for the head network, and entirely eschew the EMA teacher for the main vision encoder. That is, we set $f_{t} = f_{s}$ and continue only to update $h_{t}$ by EMA updates from $h_{s}$.

Ablations in [Sec.4](https://arxiv.org/html/2604.12012#S4 "4 Results ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") demonstrate that applying EMA exclusively to the projector head retains the majority of the performance of applying EMA to both head and encoder while significantly reducing resource requirements. As EMA methods require a second copy of all parameters being averaged during training, this resource-efficient adaptation represents significant savings in memory overhead and training throughput. For example, on ViT-B, this method reduces training parameters by $42 \%$. Also, note that this design represents a necessary intermediate, as our preliminary experiments find that entirely removing EMA by sharing both the encoder and projector causes severe training instability and performance degradation.

Table 3: Zero-shot segmentation in pretraining. Comparing TIPS ViT-g with iBOT or iBOT++ methods, showing significant improvements with our novel iBOT++.

| Model | Zero-shot Segmentation (mIoU) $\uparrow$ |
| --- |
| PC59 | PC60 | VOC21 | ADE150 |
| TIPS[[33](https://arxiv.org/html/2604.12012#bib.bib33)] (with iBOT) | 14.2 | 13.4 | 29.1 | 3.5 |
| TIPS with iBOT++ | 28.6 | 26.2 | 37.2 | 17.6 |
![Image 21: Refer to caption](https://arxiv.org/html/2604.12012v1/x3.png)

Figure 4: Image captions at different granularities. Besides the alt-text and PaliGemma captions used in previous work, we propose additionally leveraging the more comprehensive Gemini captions, to make our vision encoder more robust. 

### 3.5 Multi-Granularity Text Captions

[Fig.4](https://arxiv.org/html/2604.12012#S3.F4 "In 3.4 Head-only EMA ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") illustrates limitations in the alt-text and PaliGemma captions used in[[33](https://arxiv.org/html/2604.12012#bib.bib33)]. For instance, in the panda image, both captions fail to describe the animal’s pose (dangling legs and head resting on the branch). Similarly, in the illustration example, neither caption identifies the image as a cartoon, a key piece of semantic information. Finally, in the last example, both captions overlook the seasonal context, where the yellow leaves indicate autumn. As the vision encoder’s learning is directly tied to caption quality, these failures motivate the need for richer, more descriptive captions.

Table 4: Ablation studies for TIPSv2’s pretraining technique. Ablations are cumulative, running on a fixed schedule of $100$k steps at resolution $224$, for fair comparisons. We highlight the best and second-best number of each column.

| Model | Seg. $\uparrow$ | Depth $\downarrow$ | Normals $\downarrow$ | ImageNet $\uparrow$ | I$\rightarrow$T Ret. $\uparrow$ | T$\rightarrow$I Ret. $\uparrow$ | Zero-shot Seg. $\uparrow$ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PASCAL | NYUv2 | NYUv2 | KNN | Flickr | Flickr | ADE150 |
| TIPS ViT-g (reproduced) | 82.8 | 0.375 | 23.1 | 83.2 | 92.0 | 81.0 | 3.5 |
| + iBOT++ | 82.5 | 0.369 | 22.7 | 84.4 | 93.9 | 81.7 | 17.6 |
| + Multi-granularity Captions | 83.7 | 0.354 | 22.7 | 84.3 | 95.0 | 85.4 | 18.1 |
| + Head-only EMA | 83.8 | 0.353 | 22.8 | 84.1 | 95.4 | 85.4 | 19.1 |

We extend this by generating richer synthetic captions using Gemini Flash [[22](https://arxiv.org/html/2604.12012#bib.bib22)], conditioned on the image, alt-text, and PaliGemma captions, as [Fig.4](https://arxiv.org/html/2604.12012#S3.F4 "In 3.4 Head-only EMA ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"). Despite their higher quality, preliminary experiments showed that longer captions underperformed in isolation. This occurs because overly comprehensive captions trivialize the contrastive loss ($\mathcal{L}_{\text{CLIP}}$). The abundance of detail facilitates discrimination within the batch, ultimately hindering the learning of robust representations. To address this, we randomly alternate between detailed Gemini captions and simpler PaliGemma captions during training to supervise the second CLS token. This balances learning difficulty and detail extraction, empirically boosting both dense and global performance.

## 4 Results

### 4.1 Experimental Setup

To demonstrate general-purpose capability as a vision encoder, we evaluate our models on a suite of 9 standard tasks, covering two broad types: image-text and image-only. Datasets and metrics used in this work are introduced in the following paragraphs. Evaluations follow the detailed protocol of [[33](https://arxiv.org/html/2604.12012#bib.bib33)], to ensure fair comparisons. As our objective is to assess the applicability of our model off-the-shelf for downstream applications, the pretrained image-text representations are kept frozen for all evaluations.

Image-text tasks include 2 types, focused on dense and global image-text alignment. We consider dense image-text alignment by evaluating on zero-shot segmentation, reporting mean Intersection over Union (mIoU). Unless otherwise mentioned, we report TIPSv2 results on zero-shot segmentation with the simple protocol that maximizes cosine similarities between patch features, up-scaled to image resolution, and the text features of each class name. Note that DINOv2 (with text[[29](https://arxiv.org/html/2604.12012#bib.bib29)]) and SILC[[36](https://arxiv.org/html/2604.12012#bib.bib36)] instead report results using the expensive sliding window protocol from TCL[[6](https://arxiv.org/html/2604.12012#bib.bib6)], which generally boosts results. Both protocols use the value embeddings of the final transformer layer as patch embeddings, following [[67](https://arxiv.org/html/2604.12012#bib.bib67)]. We report zero-shot segmentation on ADE20K[[65](https://arxiv.org/html/2604.12012#bib.bib65)] with 150 classes (ADE150), PASCAL context [[14](https://arxiv.org/html/2604.12012#bib.bib14)], and PASCAL VOC[[15](https://arxiv.org/html/2604.12012#bib.bib15)]. For PASCAL context, we report both with (PC60) and without (PC59) the background label. The global-focused tasks include image-to-text and text-to-image retrieval on Flickr30K[[61](https://arxiv.org/html/2604.12012#bib.bib61)], DOCCI[[37](https://arxiv.org/html/2604.12012#bib.bib37)], and COCO[[8](https://arxiv.org/html/2604.12012#bib.bib8)] reporting recall@1; and zero-shot classification on ImageNet-1K reporting top-1 accuracy by retrieving nearest class text embeddings[[40](https://arxiv.org/html/2604.12012#bib.bib40)].

Image-only tasks include semantic segmentation with linear probe on PASCAL VOC[[15](https://arxiv.org/html/2604.12012#bib.bib15)] and ADE20k[[65](https://arxiv.org/html/2604.12012#bib.bib65)] reporting mIOU; monocular depth estimation on the scene-centric NYUv2[[44](https://arxiv.org/html/2604.12012#bib.bib44)] with linear probe and the object-centric NAVI[[27](https://arxiv.org/html/2604.12012#bib.bib27)] with DPT[[41](https://arxiv.org/html/2604.12012#bib.bib41)], both reporting RMSE; surface normal estimation on NYUv2 and NAVI, using DPT, reporting angular RMSE; image classification on ImageNet-1K[[42](https://arxiv.org/html/2604.12012#bib.bib42)] reporting top-1 accuracy (KNN and linear probe); and fine-grained/instance-level retrieval on the Universal Embeddings Dataset (UnED)[[63](https://arxiv.org/html/2604.12012#bib.bib63)] (comprising data from $8$ different domains: Food2k [[34](https://arxiv.org/html/2604.12012#bib.bib34)], CARS196 [[30](https://arxiv.org/html/2604.12012#bib.bib30)], SOP [[46](https://arxiv.org/html/2604.12012#bib.bib46)], InShop [[32](https://arxiv.org/html/2604.12012#bib.bib32)], iNat [[52](https://arxiv.org/html/2604.12012#bib.bib52)], Met[[62](https://arxiv.org/html/2604.12012#bib.bib62)], GLDv2 [[56](https://arxiv.org/html/2604.12012#bib.bib56)], Rp2k[[39](https://arxiv.org/html/2604.12012#bib.bib39)]), reporting average recall@1.

Training data. We train our models using the web-crawled WebLI dataset[[9](https://arxiv.org/html/2604.12012#bib.bib9)], reusing the specific filtered subset created by[[33](https://arxiv.org/html/2604.12012#bib.bib33)], containing $116$M images. We also reuse synthetic captions from PaliGemma[[3](https://arxiv.org/html/2604.12012#bib.bib3)], again following[[33](https://arxiv.org/html/2604.12012#bib.bib33)]. Additionally, as described in [Sec.3.5](https://arxiv.org/html/2604.12012#S3.SS5 "3.5 Multi-Granularity Text Captions ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), we leverage synthetic captions from Gemini 1.5 Flash [[22](https://arxiv.org/html/2604.12012#bib.bib22)].

Implementation details. Following [[33](https://arxiv.org/html/2604.12012#bib.bib33)], pretraining combines contrastive image-text and self-supervised losses, integrating the key upgrades described in [Sec.3](https://arxiv.org/html/2604.12012#S3 "3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"): iBOT++, head-only EMA and multi-granularity text captions. Pretraining consists of a low-resolution stage for $90 ​ k$ steps at batch size $8192$ and then a high-resolution adaptation stage for $9 ​ k$ steps at batch size $4096$. At low resolution, we train with $1$ global crop at resolution $224$ and $6$ local crops at resolution $98$. At high resolution, the global crop has resolution $448$ and the local crops have resolution $140$. We use only random resizes, crops and flips as augmentations. We pre-train at ViT-g scale with 512 TPUv5 chips for 2 days. We also distill to a family of -SO, -L, -B models, with all results presented in the appendix. Distillation is as described in [Sec.3.1](https://arxiv.org/html/2604.12012#S3.SS1 "3.1 Preliminaries ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), and then student models also undergo a high-resolution adaptation stage.

### 4.2 Ablations

We present ablations in [Tab.4](https://arxiv.org/html/2604.12012#S3.T4 "In 3.5 Multi-Granularity Text Captions ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") where we add each of the primary contributions successively, evaluated on a representative subset of 7 of our evaluation tasks. We begin with TIPS[[33](https://arxiv.org/html/2604.12012#bib.bib33)] as a baseline, reproduced with two minor modifications: we halve the batch size and increase position embeddings to $32 \times 32$ from $16 \times 16$. Our preliminary experiments showed halving the batch size saved training resources without affecting results significantly, and higher-resolution position embeddings improved all results without incurring much cost. Ablations are carried out for 100k steps at original resolution, without the high-res adaptation stage of the full pretraining process. In the second row, iBOT is replaced by iBOT++, which results in across-the-board improvements for most evals, including a dramatic $+ 14.1$ mIoU improvement to zero-shot segmentation. After that, we replace PaliGemma synthetic captions with multi-granularity captions sampled from PaliGemma and Gemini captions, which improves both global and dense types of image-text tasks: I$\rightarrow$T, T$\rightarrow$I, and zero-shot segmentation. Finally, we add head-only EMA, a change that is primarily targeted at enabling significant training resource savings, but still results in comparable performance, even further improving some tasks such as zero-shot segmentation. The combination of these changes is TIPSv2, with all primary components resulting in increased or comparable performance across our evaluations, with particular significant improvement for zero-shot segmentation from iBOT++.

Table 5: Dense image-text evaluations, where TIPSv2 outperforms others in all cases, even though SILC and DINOv2 use the more expensive TCL protocol[[6](https://arxiv.org/html/2604.12012#bib.bib6)]. We highlight the best and second-best number of each column. 

| Method | Zero-shot Segmentation $\uparrow$ |
| --- | --- |
| PC59 | PC60 | VOC21 | ADE150 |
| SigLIP2 SO/14 | - | 19.6 | 26.8 | 15.6 |
| SILC B/16 | 31.6 | - | - | 19.3 |
| DINOv2 (dino.txt) L/14 | 30.9 | - | - | 20.6 |
| TIPS L/14 | 33.5 | 30.4 | 30.5 | 20.8 |
| TIPSv2 L/14 (ours) | 37.1 | 33.9 | 44.4 | 24.7 |

Table 6: Global image-text evaluations, where TIPSv2 achieves best or second-best in $5$ out of $7$ cases. We highlight the best and second-best number of each column.

| Model | I$\rightarrow$T Retrieval $\uparrow$ | T$\rightarrow$I Retrieval $\uparrow$ | 0-Shot $\uparrow$ |
| --- | --- | --- | --- |
| COCO | Flickr | DOCCI | COCO | Flickr | DOCCI | ImageNet |
| CLIP L/14 | 56.3 | 85.2 | 44.4 | 36.5 | 65.2 | 40.4 | 75.5 |
| OpenCLIP G/14 | 67.3 | 92.9 | - | 51.4 | 79.5 | - | 80.1 |
| SigLIP2 g/16 | 72.8 | 95.4 | - | 56.1 | 86.0 | - | 85.0 |
| SILC G/16 | 73.2 | - | - | 54.7 | - | - | 83.7 |
| DINOv2 (dino.txt) L/14 | - | - | - | 45.4 | 77.1 | - | 81.4 |
| PE-core G/14 | 75.4 | 96.2 | - | 58.1 | 85.7 | - | 85.4 |
| TIPS g/14 | 74.0 | 93.0 | 57.2 | 59.4 | 84.5 | 58.8 | 79.9 |
| TIPSv2 g/14 (ours) | 75.7 | 95.1 | 68.9 | 60.7 | 85.9 | 72.8 | 80.7 |

Table 7: Image-only evaluations, where TIPSv2 achieves the best or second-best performance in $7$ out of $9$ evaluations. We highlight the best and second-best number of each column. 

| Method | Segmentation $\uparrow$ | Depth $\downarrow$ | Normals $\downarrow$ | Fine-grained $\uparrow$ | ImageNet Class. $\uparrow$ |
| --- | --- | --- | --- | --- | --- |
| PASCAL | ADE20k | NYUv2 | NAVI | NYUv2 | NAVI | retrieval (UnED) | KNN | lin |
| CLIP L/14 | 74.5 | 39.0 | 0.553 | 0.073 | 24.3 | 25.5 | 57.4 | 79.8 | 84.3 |
| SigLIP2 SO/14 | 78.1 | 45.4 | 0.466 | 0.064 | 23.0 | 25.0 | - | - | - |
| DINOv2 g/14 | 83.1 | 49.5 | 0.372 | 0.054 | 20.7 | 24.0 | 62.7 | 83.6 | 87.3 |
| PE-core G/14 | - | 41.5 | - | - | - | - | - | 86.8 | 89.5 |
| PE-spatial G/14 | - | 49.3 | - | - | - | - | - | - | - |
| FRANCA G/14 | 81.3 | 42.4 | - | - | - | - | - | 83.0 | 85.9 |
| TIPS g/14 | 83.6 | 49.9 | 0.353 | 0.058 | 21.9 | 24.2 | 68.2 | 83.3 | 86.2 |
| TIPSv2 g/14 (ours) | 85.1 | 51.6 | 0.334 | 0.059 | 21.7 | 24.1 | 67.0 | 83.7 | 86.8 |

Table 8: Comparison between DINOv3 and TIPSv2, on largest comparable model size ViT-L. TIPSv2 achieves superior performance on 4 out of 6 metrics. We highlight the best performing model for each task.

| Model | Segmentation $\uparrow$ | Depth $\downarrow$ | 0-Shot $\uparrow$ | I$\rightarrow$T Ret. $\uparrow$ | T$\rightarrow$I Ret. $\uparrow$ | Zero-shot Seg. $\uparrow$ |
| --- | --- | --- | --- | --- | --- | --- |
| ADE20k | NYUv2 | ImageNet | COCO | COCO | ADE150 |
| DINOv3 L/16 | 54.9 | 0.352 | 82.3 | 63.7 | 45.6 | 24.7 |
| TIPSv2 L/14 (ours) | 51.4 | 0.339 | 79.7 | 73.5 | 57.4 | 25.1 |

### 4.3 Comparisons with Other Vision Encoders

We provide extensive benchmarking against state-of-the-art methods. For fair comparisons, we strictly follow the protocol of [[33](https://arxiv.org/html/2604.12012#bib.bib33)], considering the largest instantiations in each model family, up to ViT size “G”, with $1.8$B parameters in the vision encoder. Note that the largest model in the TIPSv2 family is of size “g”, with $1.1$B parameters in the vision encoder. The compared methods are the following. Weakly-supervised methods: CLIP[[40](https://arxiv.org/html/2604.12012#bib.bib40)], PE[[4](https://arxiv.org/html/2604.12012#bib.bib4)], and OpenCLIP[[10](https://arxiv.org/html/2604.12012#bib.bib10)]; self-supervised methods: DINOv2[[38](https://arxiv.org/html/2604.12012#bib.bib38)] (with registers[[12](https://arxiv.org/html/2604.12012#bib.bib12)]), DINOv3[[45](https://arxiv.org/html/2604.12012#bib.bib45)], and FRANCA[[54](https://arxiv.org/html/2604.12012#bib.bib54)]; combined approaches: TIPS[[33](https://arxiv.org/html/2604.12012#bib.bib33)], SILC[[36](https://arxiv.org/html/2604.12012#bib.bib36)], dino.txt[[29](https://arxiv.org/html/2604.12012#bib.bib29)] (as the image-text capability of DINOv2), and SigLIP2[[50](https://arxiv.org/html/2604.12012#bib.bib50)]. Qualitatively, [Fig.5](https://arxiv.org/html/2604.12012#S4.F5 "In 4.3 Comparisons with Other Vision Encoders ‣ 4 Results ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") shows that TIPSv2 patch embeddings are more spatially coherent than other vision-language pretraining methods.

Dense image-text tasks. In [Tab.5](https://arxiv.org/html/2604.12012#S4.T5 "In 4.2 Ablations ‣ 4 Results ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), we report zero-shot segmentation results on ViT-L and the closest comparable sizes from competitor models. TIPSv2 achieves state-of-the-art results, indicating a significant improvement in dense patch-text alignment. Qualitative visualizations of the zero-shot segmentation results are presented in [Fig.6](https://arxiv.org/html/2604.12012#S4.F6 "In 4.3 Comparisons with Other Vision Encoders ‣ 4 Results ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment").

Global image-text tasks. In [Tab.6](https://arxiv.org/html/2604.12012#S4.T6 "In 4.2 Ablations ‣ 4 Results ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), TIPSv2 achieves the best or second-best results in 5 out of 7 evaluations. Our models are best in all COCO and long-text DOCCI tasks, outperforming even larger ViT-G models. Note that our ViT-g models even outperform the recent PE[[4](https://arxiv.org/html/2604.12012#bib.bib4)] ViT-G models in 3 out of 5 evals, although the PE model has 56% more parameters and processes 47$\times$ more image-text pairs.

![Image 22: Refer to caption](https://arxiv.org/html/2604.12012v1/images/dadaocheng.jpeg)![Image 23: Refer to caption](https://arxiv.org/html/2604.12012v1/images/tips/dadaocheng.png)![Image 24: Refer to caption](https://arxiv.org/html/2604.12012v1/images/siglip2/dadaocheng.png)![Image 25: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_g/dadaocheng.png)

![Image 26: Refer to caption](https://arxiv.org/html/2604.12012v1/images/cph.jpeg)![Image 27: Refer to caption](https://arxiv.org/html/2604.12012v1/images/tips/cph.png)![Image 28: Refer to caption](https://arxiv.org/html/2604.12012v1/images/siglip2/cph.png)![Image 29: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_g/cph.png)

![Image 30: Refer to caption](https://arxiv.org/html/2604.12012v1/images/hike.jpeg)![Image 31: Refer to caption](https://arxiv.org/html/2604.12012v1/images/tips/hike.png)![Image 32: Refer to caption](https://arxiv.org/html/2604.12012v1/images/siglip2/hike.png)![Image 33: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_g/hike.png)

![Image 34: Refer to caption](https://arxiv.org/html/2604.12012v1/images/angus.jpeg)![Image 35: Refer to caption](https://arxiv.org/html/2604.12012v1/images/tips/angus.png)![Image 36: Refer to caption](https://arxiv.org/html/2604.12012v1/images/siglip2/angus.png)![Image 37: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_g/angus.png)

Image

TIPS

SigLIP2

TIPSv2 (ours)

Figure 5: PCA maps. Comparing the first $3$ PCA components, using ViT-g models. Images are forwarded at 1372 resolution for patch size 14 models (TIPS, TIPSv2) and at 1568 resolution for patch size 16 models (SigLIP2). TIPSv2 produces smoother feature maps compared to other vision-language pretraining methods, with well-delineated objects.

Image-only tasks. In [Tab.7](https://arxiv.org/html/2604.12012#S4.T7 "In 4.2 Ablations ‣ 4 Results ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), TIPSv2 achieves the best or second-best results in 7 out of 9 evaluations, and also achieves strong performance on the remaining 2 cases. TIPSv2 stands out as particularly strong in dense understanding tasks, improving by $+ 1.5$ in segmentation on PASCAL and by $- 0.019$ on depth in NYUv2 over prior best. However, our models do not perform as well in ImageNet classification, a result of our focus on optimizing for general purpose capability across a wide range of tasks.

DINOv3 comparison. Additionally, we compare TIPSv2 with the very recent DINOv3[[45](https://arxiv.org/html/2604.12012#bib.bib45)], presenting results in [Tab.8](https://arxiv.org/html/2604.12012#S4.T8 "In 4.2 Ablations ‣ 4 Results ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"). In order to make the zero-shot segmentation evals comparable, for this table we reproduce their setup, with the more expensive sliding window protocol from TCL[[6](https://arxiv.org/html/2604.12012#bib.bib6)]. Note that the DINOv3 teacher model is trained with 6$\times$ more parameters and 15$\times$ more images than the TIPSv2 teacher, so we believe the fairest possible comparison is to use the largest model size in common between the two model families, which is ViT-L. We report numbers on the subset of all released evals with matching protocols. Notably, TIPSv2 outperforms DINOv3 in 4 out of 6 evals, despite the data and model size disadvantage.

![Image 38: Refer to caption](https://arxiv.org/html/2604.12012v1/images/dog_rug.png)![Image 39: Refer to caption](https://arxiv.org/html/2604.12012v1/images/dog_rug_gt.png)![Image 40: Refer to caption](https://arxiv.org/html/2604.12012v1/images/dog_rug_v2.png)![Image 41: Refer to caption](https://arxiv.org/html/2604.12012v1/images/dog_rug_v1.png)![Image 42: Refer to caption](https://arxiv.org/html/2604.12012v1/images/dog_rug_siglip2.png)

![Image 43: Refer to caption](https://arxiv.org/html/2604.12012v1/images/birds.png)![Image 44: Refer to caption](https://arxiv.org/html/2604.12012v1/images/birds_gt.png)![Image 45: Refer to caption](https://arxiv.org/html/2604.12012v1/images/birds_v2.png)![Image 46: Refer to caption](https://arxiv.org/html/2604.12012v1/images/birds_v1.png)![Image 47: Refer to caption](https://arxiv.org/html/2604.12012v1/images/birds_siglip2.png)

![Image 48: Refer to caption](https://arxiv.org/html/2604.12012v1/images/bus.png)![Image 49: Refer to caption](https://arxiv.org/html/2604.12012v1/images/bus_gt.png)![Image 50: Refer to caption](https://arxiv.org/html/2604.12012v1/images/bus_v2.png)![Image 51: Refer to caption](https://arxiv.org/html/2604.12012v1/images/bus_v1.png)![Image 52: Refer to caption](https://arxiv.org/html/2604.12012v1/images/bus_siglip2.png)

Image

Ground truth

TIPSv2 (ours)

TIPS

SigLIP2

Figure 6: Zero-shot segmentation visualization. Comparing results for TIPSv2, TIPS and SigLIP 2, where classes are predicted directly by finding the closest text embedding to each image patch token, without any post-processing. TIPSv2 enhances patch-text alignment significantly compared to other models, showcasing strong off-the-shelf capabilities.

## 5 Conclusion

In this work, we introduce TIPSv2, a new vision-language encoder suitable to a variety of multimodal applications. By investigating the weak dense image-text alignment of previous models, we find that patch-level distillation substantially enhances this capability. This observation inspires us to introduce iBOT++, an upgrade to the well-known iBOT masked image modeling technique used in pretraining, resulting in significant enhancements to dense image-text alignment. Additionally, we make vision-language pretraining more efficient with simplifications to the EMA setup, and leverage image captions at different granularities to obtain more robust representations. Through comprehensive experiments, our final TIPSv2 model showcases strong results on $9$ tasks spanning $20$ datasets, generally matching or exceeding results from previous vision-language encoders.

Acknowledgments.We would like to thank Connor Schenck for thoughtful discussions and suggestions.

## Appendix A Appendix

Table 9: Applying iBOT++ to CLIP, on a ViT-L backbone. iBOT++ significantly enhances CLIP performance across several tasks, beyond what can be obtained with iBOT.

| Model | Seg. | Depth $\downarrow$ | ImageNet | IT Ret. | TI Ret. | 0-shot Seg. |
| --- | --- | --- | --- | --- | --- | --- |
| ViT-L | ADE20k | NYUv2 | KNN | COCO | COCO | PC60 |
| CLIP | 35.7 | 0.571 | 73.5 | 52.2 | 33.2 | 4.3 |
| CLIP+iBOT | 41.3 | 0.458 | 77.2 | 55.7 | 37.5 | 8.0 |
| CLIP+iBOT++ | 42.8 | 0.434 | 78.7 | 58.1 | 40.6 | 22.9 |

Table 10: Applying iBOT++ to CLIP with head-only EMA, on a ViT-L backbone. iBOT++ with head-only EMA significantly enhances CLIP performance.

| Model | Seg. | Depth $\downarrow$ | ImageNet | IT Ret. | TI Ret. | 0-shot Seg. |
| --- | --- | --- | --- | --- | --- | --- |
| ViT-L | ADE20k | NYUv2 | KNN | COCO | COCO | PC60 |
| CLIP | 35.7 | 0.571 | 73.5 | 52.2 | 33.2 | 4.3 |
| CLIP+iBOT | 39.8 | 0.467 | 76.6 | 55.4 | 37.0 | 4.3 |
| CLIP+iBOT++ | 42.5 | 0.437 | 78.2 | 56.6 | 39.3 | 22.1 |

Table 11: Applying iBOT++ to CLIP with a dual CLS setup, on a ViT-g backbone. iBOT++ significantly enhances performance across several tasks, beyond what can be obtained with iBOT.

| Model | Seg. | Depth $\downarrow$ | ImageNet | IT Ret. | TI Ret. | 0-shot Seg. |
| --- | --- | --- | --- | --- | --- | --- |
| ViT-g | ADE20k | NYUv2 | KNN | COCO | COCO | PC60 |
| CLIP 2 CLS | 40.1 | 0.475 | 79.1 | 72.9 | 56.1 | 18.2 |
| CLIP 2 CLS + iBOT | 41.1 | 0.442 | 81.6 | 73.2 | 58.3 | 16.4 |
| CLIP 2 CLS + iBOT++ | 47.2 | 0.366 | 82.7 | 73.6 | 58.9 | 28.2 |

### A.1 Applying iBOT++ to CLIP

In the main paper results, we showed the value of our novel iBOT++ loss in the context of the TIPS training recipe. In this section, we go further to demonstrate the generalizability of iBOT++ to other vision-language architectures, specifically on top of the widely adopted CLIP model. First, both iBOT and iBOT++ are applied on top of vanilla CLIP, trained with the same dataset used throughout the paper, using a ViT-L backbone. Our results in [Tab.9](https://arxiv.org/html/2604.12012#A1.T9 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") demonstrate that integrating iBOT++ yields consistent performance gains across all metrics, beyond that of adding iBOT alone. A similar conclusion is obtained when using head-only EMA in addition to iBOT++, a setup which reduces memory requirements significantly and achieves generally on par performance with the full EMA case, as reported in [Tab.10](https://arxiv.org/html/2604.12012#A1.T10 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"). Then, as an additional experiment to validate iBOT++, we add it on top of CLIP using two CLS tokens (as in the TIPS setup, but without any of the additional losses used in TIPS), with a ViT-g backbone and the same training dataset ([Tab.11](https://arxiv.org/html/2604.12012#A1.T11 "In Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment")). Once again, we see significant and consistent performance gains using iBOT++, compared to the CLIP 2 CLS baseline and its modified version using iBOT. Notably, in all these cases iBOT++ yields significant improvements in zero-shot segmentation, highlighting its importance for aligning image patches to language. These results corroborate the usefulness of our proposed iBOT++ recipe for vision-language pretraining.

### A.2 iBOT++ Ablation Study on Masking Ratios

Table 12: Masking ablation for iBOT++ pretraining. We conduct an ablation study on TIPS[[33](https://arxiv.org/html/2604.12012#bib.bib33)] ViT-L models to determine the optimal masking ratio for iBOT++ pretraining. The results show that $75 \%$ masking ratio is critical for achieving strong performance across all evaluations, particularly enhancing patch-text alignment. The model achieving the best overall performance is highlighted.

| Masking | Segmentation $\uparrow$ | Depth $\downarrow$ | I$\rightarrow$T Ret. $\uparrow$ | Zero-shot Seg. $\uparrow$ |
| --- | --- | --- | --- | --- |
| Ratio | PASCAL | NYUv2 | Flickr | ADE150 |
| 0.0 | 78.8 | 0.513 | 90.0 | 1.0 |
| 0.5 | 82.5 | 0.438 | 92.6 | 2.4 |
| 0.75 | 82.6 | 0.418 | 93.8 | 13.6 |

As detailed in [Sec.3.2](https://arxiv.org/html/2604.12012#S3.SS2 "3.2 Bridging Pretraining and Distillation ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), distillation significantly enhances patch-text alignment, even when the teacher model exhibits poor dense alignment. In [Tab.2](https://arxiv.org/html/2604.12012#S3.T2 "In Figure 2 ‣ 3.1 Preliminaries ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), we identified two key distinctions between the distillation and pretraining stages: A) also applying loss to visible tokens (compare rows (1-2)) and B) lowering masking ratio from $75 \% \rightarrow 0 \%$ (compare rows (2-4)) . In iBOT++, we propose to take the approach in A) from distillation and apply it to pretraining. This naturally raises the question: Would applying B) by removing masking in iBOT++ pretraining also further enhance patch-text alignment? To explore this, we ablated the masking ratio during iBOT++ pretraining. Our experiments in [Tab.12](https://arxiv.org/html/2604.12012#A1.T12 "In A.2 iBOT++ Ablation Study on Masking Ratios ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") demonstrate that the answer is no: iBOT++ achieves its best performance with a $75 \%$ masking ratio. As a result, we adopt the $75 \%$ ratio setting as our final TIPSv2 training recipe. Our results confirm that Masked Image Modeling (MIM) remains critical for pretraining, consistently improving performance across image-only tasks and image-text tasks. We conclude that mask removal is only effective during distillation because the teacher model already provides the necessary strong local semantic understanding. This allows the student vision encoder to inherit the alignment without needing to learn it via the MIM objective.

### A.3 Ablations on Multi-Granularity Captions

In [Tab.13](https://arxiv.org/html/2604.12012#A1.T13 "In A.3 Ablations on Multi-Granularity Captions ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), we present ablations to justify our strategy to utilize multiple captions, varying 1-2 [CLS] tokens and the assignment to [CLS] tokens between the 3 available captions (web, PaliGemma, Gemini). These ablations are conducted with the default TIPSv2 training setup, except that full EMA is used (instead of head-only EMA). We find the optimal strategy is the recipe in TIPSv2: alternating real/synthetic captions with the dual CLS setup.

Table 13: Ablations for multi-granularity captions, on ViT-g. Texts for 2 CLS are separated by / and for each CLS, texts are uniformly sampled from sources. 

| Text Strategy | Seg. | Depth $\downarrow$ | ImageNet | IT Ret. | 0-shot Seg. |
| --- | --- | --- | --- | --- | --- |
| ADE20k | NYUv2 | KNN | COCO | ADE150 |
| 1 CLS (web, PaliGemma) | 46.3 | 0.375 | 80.4 | 72.3 | 16.4 |
| 1 CLS (web, PaliGemma, Gemini) | 46.7 | 0.366 | 81.2 | 74.4 | 17.7 |
| 2 CLS (web / PaliGemma) | 48.3 | 0.370 | 84.3 | 70.0 | 17.1 |
| 2 CLS (web / PaliGemma, Gemini) | 49.1 | 0.354 | 84.3 | 76.2 | 18.1 |

### A.4 Qualitative Comparisons to DINOv2 and v3

In order to further illustrate the comparison with self-supervised pretrained models, we provide additional PCA maps for DINOv2 (with registers)[[12](https://arxiv.org/html/2604.12012#bib.bib12), [38](https://arxiv.org/html/2604.12012#bib.bib38)] and DINOv3[[45](https://arxiv.org/html/2604.12012#bib.bib45)]. [Fig.7](https://arxiv.org/html/2604.12012#A1.F7 "In A.4 Qualitative Comparisons to DINOv2 and v3 ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") presents results on ViT-L models, which is the largest common size between these model families. [Fig.8](https://arxiv.org/html/2604.12012#A1.F8 "In A.4 Qualitative Comparisons to DINOv2 and v3 ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") presents results on larger models: ViT-g for DINOv2 and TIPSv2, but ViT-7B for DINOv3. Note that the DINOv3 ViT-7B teacher model is trained with 6$\times$ more parameters and 15$\times$ more images than the TIPSv2 ViT-g teacher.

Comparing DINOv3 and TIPSv2, we can see that PCA maps for DINOv3 are smoother, whereas TIPSv2 maps are more granular. We note that DINOv3 enhances dense feature maps (on top of DINOv2) by means of a Gram anchoring loss that acts on patch correlations, introducing another teacher that is frozen from the past, along with a higher-resolution inference and down-sampling procedure. The dense feature maps of TIPSv2 also demonstrate comparable improvements in spatial coherence (on top of TIPS), but require much simpler changes to the training setup. On some images, this seems to demonstrate a more semantic focus for TIPSv2, compared to a more spatial focus in DINOv3.

For example, in the third row of [Fig.7](https://arxiv.org/html/2604.12012#A1.F7 "In A.4 Qualitative Comparisons to DINOv2 and v3 ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") and [Fig.8](https://arxiv.org/html/2604.12012#A1.F8 "In A.4 Qualitative Comparisons to DINOv2 and v3 ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), the backpacks appear semantically similar to the people wearing them in DINOv3 PCA, while they are clearly distinct from the people in TIPSv2 PCA. In the second row of [Fig.8](https://arxiv.org/html/2604.12012#A1.F8 "In A.4 Qualitative Comparisons to DINOv2 and v3 ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), the ceiling tends to be underclustered in DINOv3, unable to distinguish lamps and other features; in contrast, TIPSv2 clearly segments them properly. In the first row of [Fig.7](https://arxiv.org/html/2604.12012#A1.F7 "In A.4 Qualitative Comparisons to DINOv2 and v3 ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), the windows for DINOv3 PCA are distinctly colored, varying from foreground to background, but are all uniformly colored for TIPSv2 PCA.

Comparing against DINOv2, TIPSv2 PCA maps are overall much smoother and more spatially coherent, in contrast to DINOv2’s noisy maps.

![Image 53: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dadaocheng.jpeg)![Image 54: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov2/vit_l/dadaocheng.png)![Image 55: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov3/vit_l/dadaocheng.png)![Image 56: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_l/dadaocheng.png)

![Image 57: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/cph.jpeg)![Image 58: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov2/vit_l/cph.png)![Image 59: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov3/vit_l/cph.png)![Image 60: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_l/cph.png)

![Image 61: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/hike.jpeg)![Image 62: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov2/vit_l/hike.png)![Image 63: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov3/vit_l/hike.png)![Image 64: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_l/hike.png)

![Image 65: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/angus.jpeg)![Image 66: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov2/vit_l/angus.png)![Image 67: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov3/vit_l/angus.png)![Image 68: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_l/angus.png)

Image

DINOv2-L

DINOv3-L

TIPSv2-L (ours)

Figure 7: PCA maps at ViT-L size. Comparing the first $3$ PCA components from the ViT-L models of DINOv2 (with registers), DINOv3, and TIPSv2. Images are forwarded at $1372$ resolution for patch size $14$ models (DINOv2 and TIPSv2) and at $1568$ resolution for patch size $16$ models (DINOv3). DINOv3 features appear smoother, but TIPSv2 features show more semantically focused features, e.g., TIPSv2 maps show all windows clustered together in row 1, and the eyes and leash are distinct on the dog in row 4.

![Image 69: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dadaocheng.jpeg)![Image 70: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov2/vit_g/dadaocheng.png)![Image 71: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov3/vit_7b/dadaocheng.png)![Image 72: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_g/dadaocheng.png)

![Image 73: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/cph.jpeg)![Image 74: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov2/vit_g/cph.png)![Image 75: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov3/vit_7b/cph.png)![Image 76: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_g/cph.png)

![Image 77: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/hike.jpeg)![Image 78: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov2/vit_g/hike.png)![Image 79: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov3/vit_7b/hike.png)![Image 80: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_g/hike.png)

![Image 81: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/angus.jpeg)![Image 82: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov2/vit_g/angus.png)![Image 83: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/dinov3/vit_7b/angus.png)![Image 84: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/tipsv2/vit_g/angus.png)

Image

DINOv2-g

DINOv3-7B

TIPSv2-g (ours)

Figure 8: PCA maps at ViT-g or ViT-7B size. Comparing the first $3$ PCA components from teacher models of DINOv2 (with registers, ViT-g), DINOv3 (ViT-7B), and TIPSv2 (ViT-g). Images are forwarded at $1372$ resolution for patch size $14$ models (DINOv2 and TIPSv2) and at $1568$ resolution for patch size $16$ models (DINOv3). As for the ViT-L PCA maps, DINOv3 features appear smoother, but TIPSv2 features capture more semantically focused details, e.g., notice the ceiling details in row 2 or the different colors contrasting people and backpacks in row 3.

### A.5 Qualitative Analysis: iBOT++ vs iBOT

![Image 85: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/bicycle.png)![Image 86: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/bicycle_gt.png)![Image 87: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/bicycle_ibotplus.png)![Image 88: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/bicycle_ibot.png)

![Image 89: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/kids.png)![Image 90: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/kids_gt.png)![Image 91: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/kids_ibotplus.png)![Image 92: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/kids_ibot.png)

![Image 93: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/baby.png)![Image 94: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/baby_gt.png)![Image 95: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/baby_ibotplus.png)![Image 96: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/baby_ibot.png)

![Image 97: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/redbus.png)![Image 98: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/redbus_gt.png)![Image 99: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/redbus_ibotplus.png)![Image 100: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/redbus_ibot.png)

![Image 101: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/puppy.png)![Image 102: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/puppy_gt.png)![Image 103: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/puppy_ibotplus.png)![Image 104: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/puppy_ibot.png)

![Image 105: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/sleep.png)![Image 106: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/sleep_gt.png)![Image 107: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/sleep_ibotplus.png)![Image 108: Refer to caption](https://arxiv.org/html/2604.12012v1/images/supp/sleep_ibot.png)

Image

Ground truth

iBOT++

iBOT

Figure 9: Zero-shot segmentation visualization. Comparing results with the iBOT loss (used in TIPS) vs the iBOT++ loss (used in TIPSv2), where classes are predicted directly by finding the closest text embedding to each image patch token, without any post-processing. Compared to baseline iBOT, iBOT++ achieves significantly improved patch-text alignment, as part of the TIPSv2 recipe.

As detailed in [Sec.3.3](https://arxiv.org/html/2604.12012#S3.SS3 "3.3 iBOT++ ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), iBOT++ significantly enhances patch-text alignment during pretraining. This improvement is quantified in [Tab.4](https://arxiv.org/html/2604.12012#S3.T4 "In 3.5 Multi-Granularity Text Captions ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), where a substantial performance gain is directly observed in the zero-shot segmentation metrics when comparing iBOT baseline (first row) to iBOT++ (second row). To further illustrate this enhancement, [Fig.9](https://arxiv.org/html/2604.12012#A1.F9 "In A.5 Qualitative Analysis: iBOT++ vs iBOT ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") provides qualitative visualizations of the zero-shot segmentation results, which correspond directly to the first and second rows of [Tab.4](https://arxiv.org/html/2604.12012#S3.T4 "In 3.5 Multi-Granularity Text Captions ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"). These visualizations confirm that iBOT++ yields significantly cleaner segmentation maps.

### A.6 Zero-shot Segmentation with SigLIP2

We showed that smaller models in the TIPS[[33](https://arxiv.org/html/2604.12012#bib.bib33)] family outperform larger ones in the task of zero-shot image segmentation, which motivated our investigations and contributions towards TIPSv2. In this section, we provide evidence of a similar effect also happening in the SigLIP2 family. [Tab.14](https://arxiv.org/html/2604.12012#A1.T14 "In A.6 Zero-shot Segmentation with SigLIP2 ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") presents zero-shot segmentation results for three model sizes, where the smallest one outperforms the larger versions in two evaluations, and the SO size model wins in the third; notably, the largest ViT-g model presents the worst performance in all three evaluations. Note that the smallest ViT-B size model is distilled via active data curation from a larger SO model in the family. Similarly to the TIPS case, these results indicate that the smaller models surprisingly outperform larger pretrained ones.

Table 14: Zero-shot segmentation for SigLIP2 models. Similarly to TIPS, the smaller models tend to outperform larger ones in the same model family.

| Model | Zero-shot Segmentation (mIoU) $\uparrow$ |
| --- | --- |
| PC60 | VOC21 | ADE150 |
| SigLIP2 B/16 | 22.6 | 25.8 | 16.4 |
| SigLIP2 SO/14 | 19.6 | 26.8 | 15.6 |
| SigLIP2 g/16 | 17.2 | 25.7 | 13.9 |

Table 15: Evaluations for all TIPSv2 model variants. We report four distinct TIPSv2 model sizes (ViT-B, ViT-L, ViT-g, and SO-400m). Only the ViT-g model is pretrained; the other sizes (ViT-B, ViT-L, and SO-400m) are distilled from the ViT-g teacher. Best performance for each task is highlighted.

| Model | Segmentation $\uparrow$ | Depth $\downarrow$ | Normals $\downarrow$ | KNN $\uparrow$ | I$\rightarrow$T Ret. $\uparrow$ | T$\rightarrow$I Ret. $\uparrow$ | Zero-shot Seg. $\uparrow$ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PASCAL | NYUv2 | NYUv2 | ImageNet | Flickr | Flickr | ADE150 |
| TIPSv2 B/14 | 84.0 | 0.374 | 23.2 | 79.8 | 92.6 | 80.0 | 17.4 |
| TIPSv2 L/14 | 85.1 | 0.339 | 21.9 | 82.5 | 95.4 | 83.3 | 24.7 |
| TIPSv2 SO/14 | 85.2 | 0.339 | 21.7 | 82.8 | 94.8 | 84.0 | 23.3 |
| TIPSv2 g/14 | 85.1 | 0.334 | 21.7 | 83.7 | 95.1 | 85.9 | 17.8 |

### A.7 TIPSv2 Family

The TIPSv2 model family includes variants with different backbone sizes: ViT-B, ViT-L, ViT-g and SO-400m[[1](https://arxiv.org/html/2604.12012#bib.bib1)] (referred to as SO hereafter). The ViT-g model is directly pretrained, while the smaller ViT-B, ViT-L, and SO variants are obtained via the patch-level distillation strategy detailed in [Sec.3.1](https://arxiv.org/html/2604.12012#S3.SS1 "3.1 Preliminaries ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment") and [Sec.3.2](https://arxiv.org/html/2604.12012#S3.SS2 "3.2 Bridging Pretraining and Distillation ‣ 3 TIPSv2 ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"), using ViT-g as the teacher model. For text encoder scaling, we follow [[33](https://arxiv.org/html/2604.12012#bib.bib33)] and adopt the same transformer parameterization as the image encoder but fix the number of layers at 12 (except for the SO variant, which maintains its standard layer count).

Our studies demonstrate that the TIPSv2 family exhibits strong performance across all image and image-text benchmarks, as summarized in [Tab.15](https://arxiv.org/html/2604.12012#A1.T15 "In A.6 Zero-shot Segmentation with SigLIP2 ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"). The parameter count for each model is detailed in [Tab.16](https://arxiv.org/html/2604.12012#A1.T16 "In A.7 TIPSv2 Family ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment").

Table 16: Number of parameters for all TIPSv2 model variants. We release $4$ different model variants. For B, L and g model sizes, we use a fixed number of 12 layers in the text encoder; for the SO size, we use the same number of layers in both the image and text encoders. 

| Model | Image # Params | Text # Params | Total # Params |
| --- | --- | --- | --- |
| TIPSv2-B/14 | 86.3M | 109.6M | 195.9M |
| TIPSv2-L/14 | 304.0M | 183.9M | 487.9M |
| TIPSv2-SO/14 | 413.3M | 448.3M | 861.7M |
| TIPSv2-g/14 | 1.1B | 389.1M | 1.5B |

### A.8 Performance of TIPSv2 against Competitors

![Image 109: Refer to caption](https://arxiv.org/html/2604.12012v1/x4.png)

Figure 10: Comparison of TIPSv2 against recent vision encoders. The chart illustrates the percentage of shared evaluation benchmarks where TIPSv2 secures the best result (green) compared head-to-head to other individual leading models (orange). TIPSv2 demonstrates a winning record on the majority of shared tasks. The integer displayed on the chart represents the count of metrics on which each respective model achieves the best result (i.e., the number of wins). For each comparison between individual vision encoders, we use the largest comparable model size (ViT-g against ViT-g, or ViT-g against ViT-G, or ViT-L against ViT-L). 

To gain a comprehensive understanding of the performance of our new method compared to other recent vision encoders, we quantified the number of evaluations where TIPSv2 outperforms (or underperforms) each competitor method head-to-head, based on reported scores in the main results tables. Looking only at the evaluations the models share, TIPSv2 generally comes out on top in most cases, as shown in [Fig.10](https://arxiv.org/html/2604.12012#A1.F10 "In A.8 Performance of TIPSv2 against Competitors ‣ Appendix A Appendix ‣ TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"). This summary confirms the strong results from TIPSv2 overall.

### A.9 Additional Implementation Details

Our implementation closely follows that of TIPS. The loss components are weighted by $\mathcal{L} = \mathcal{L}_{\text{CLIP}} + \alpha ​ \mathcal{L}_{\text{DINO}} + \beta ​ \mathcal{L}_{\text{iBOT}}$, where $\alpha = 1.0$, $\beta = 2.0$. $\mathcal{L}_{\text{CLIP}}$ is the averaged result of contrastive losses from the two captions. We use the Adafactor[[43](https://arxiv.org/html/2604.12012#bib.bib43)] optimizer, and projection heads are balanced from collapse with EMA centering and sharpening.

## References

*   Alabdulmohsin et al. [2023] I. Alabdulmohsin, X. Zhai, A. Kolesnikov, and L. Beyer. Getting ViT in Shape: Scaling Laws for Compute-Optimal Model Design. In _Proc. NeurIPS_, 2023. 
*   Assran et al. [2023] M. Assran, Q. Duval, I. Misra, P. Bojanowski, P. Vincent, M. Rabbat, Y. LeCun, and N. Ballas. Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture. In _Proc. ICCV_, 2023. 
*   Beyer et al. [2024] L. Beyer, A. Steiner, A. Pinto, A. Kolesnikov, X. Wang, D. Salz, M. Neumann, I. Alabdulmohsin, M. Tschannen, E. Bugliarello, T. Unterthiner, D. Keysers, S. Koppula, F. Liu, A. Grycner, A. Gritsenko, N. Houlsby, M. Kumar, K. Rong, J. Eisenschlos, R. Kabra, M. Bauer, M. Bošnjak, X. Chen, M. Minderer, P. Voigtlaender, I. Bica, I. Balazevic, J. Puigcerver, P. Papalampidi, O. Henaff, X. Xiong, R. Soricut, J. Harmsen, and X. Zhai. PaliGemma: A versatile 3B VLM for transfer. _arXiv:2407.07726_, 2024. 
*   Bolya et al. [2025] D. Bolya, P. Huang, P. Sun, J. Cho, A. Madotto, C. Wei, T. Ma, J. Zhi, J. Rajasegaran, H. Rasheed, J. Wang, M. Monteiro, H. Xu, S. Dong, N. Ravi, D. Li, P. Dollár, and C. Feichtenhofer. Perception Encoder: The best visual embeddings are not at the output of the network. _arXiv:2504.13181_, 2025. 
*   Caron et al. [2021] M. Caron, H. Touvron, I. Misra, H. Jegou, J. Mairal, P. Bojanowski, and A. Joulin. Emerging Properties in Self-Supervised Vision Transformers. In _Proc. ICCV_, 2021. 
*   Cha et al. [2023] J. Cha, J. Mun, and B. Roh. Learning to generate text-grounded mask for open-world semantic segmentation from only image-text pairs. In _Proc. CVPR_, 2023. 
*   Chen et al. [2020] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton. A Simple Framework for Contrastive Learning of Visual Representations. In _Proc. ICML_, 2020. 
*   Chen et al. [2015] X. Chen, H. Fang, T.-Y. Lin, R. Vedantam, S. Gupta, P. Dollar, and C.L. Zitnick. Microsoft COCO Captions: Data Collection and Evaluation Server. _arXiv:1504.00325_, 2015. 
*   Chen et al. [2023] X. Chen, X. Wang, S. Changpinyo, AJ Piergiovanni, P. Padlewski, D. Salz, S. Goodman, A. Grycner, B. Mustafa, L. Beyer, A. Kolesnikov, J. Puigcerver, N. Ding, K. Rong, H. Akbari, G. Mishra, L. Xue, A. Thapliyal, J. Bradbury, W. Kuo, M. Seyedhosseini, C. Jia, B.Karagol Ayan, C. Riquelme, A. Steiner, A. Angelova, X. Zhai, N. Houlsby, and R. Soricut. PaLI: A Jointly-Scaled Multilingual Language-Image Model. In _Proc. ICLR_, 2023. 
*   Cherti et al. [2023] M. Cherti, R. Beaumont, R. Wightman, M. Wortsman, G. Ilharco, C. Gordon, C. Schuhmann, L. Schmidt, and J. Jitsev. Reproducible Scaling Laws for Contrastive Language-Image Learning. In _Proc. CVPR_, 2023. 
*   Chuang et al. [2025] Y. Chuang, Y. Li, D. Wang, C. Yeh, K. Lyu, R. Raghavendra, J. Glass, L. Huang, J. Weston, L. Zettlemoyer, X. Chen, Z. Liu, S. Xie, W. Yih, S. Li, and H. Xu. Meta CLIP 2: A Worldwide Scaling Recipe. In _Proc. NeurIPS_, 2025. 
*   Darcet et al. [2024] T. Darcet, M. Oquab, J. Mairal, and P. Bojanowski. Vision Transformers Need Registers. In _Proc. ICLR_, 2024. 
*   Dosovitskiy et al. [2021] A. Dosovitskiy, L. Beyer, A. Kolesnikov, D. Weissenborn, X. Zhai, T. Unterthiner, M. Dehghani, M. Minderer, G. Heigold, S. Gelly, J. Uszkoreit, and N. Houlsby. An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale. In _Proc. ICLR_, 2021. 
*   Everingham and Winn [2011] M. Everingham and J. Winn. The Pascal Visual Object Classes Challenge 2012 (VOC2012) Development Kit. _Pattern Analysis, Statistical Modelling and Computational Learning, Tech. Rep_, 2011. 
*   Everingham et al. [2010] M. Everingham, L.Van Gool, C. Williams, J. Winn, and A. Zisserman. The Pascal Visual Object Classes (VOC) Challenge. _IJCV_, 2010. 
*   Fan et al. [2025] D. Fan, S. Tong, J. Zhu, K. Sinha, Z. Liu, X. Chen, M. Rabbat, N. Ballas, Y. LeCun, A. Bar, and S. Xie. Scaling Language-Free Visual Representation Learning. _arXiv:2504.01017_, 2025. 
*   Fan et al. [2023] L. Fan, D. Krishnan, P. Isola, D. Katabi, and Y. Tian. Improving CLIP Training with Language Rewrites. In _Proc. NeurIPS_, 2023. 
*   Fang et al. [2023] Y. Fang, W. Wang, B. Xie, Q. Sun, L. Wu, X. Wang, T. Huang, X. Wang, and Y. Cao. EVA: Exploring the Limits of Masked Visual Representation Learning at Scale. In _Proc. CVPR_, 2023. 
*   Fang et al. [2024] Y. Fang, Q. Sun, X. Wang, T. Huang, X. Wang, and Y. Cao. EVA-02: A Visual Representation for Neon Genesis. _Image and Vision Computing_, 2024. 
*   Fini et al. [2025] E. Fini, M. Shukor, X. Li, P. Dufter, M. Klein, D. Haldimann, S. Aitharaju, V. Costa, L. Béthune, Z. Gan, A. Toshev, M. Eichner, M. Nabi, Y. Yang, J. Susskind, and A. El-Nouby. Multimodal Autoregressive Pre-training of Large Vision Encoders. In _Proc. CVPR_, 2025. 
*   Gao et al. [2023] P. Gao, Z. Lin, R. Zhang, R. Fang, H. Li, H. Li, and Y. Qiao. Mimic before Reconstruct: Enhancing Masked Autoencoders with Feature Mimicking. _IJCV_, 2023. 
*   Gemini Team, Google [2024] Gemini Team, Google. Gemini 1.5: Unlocking Multimodal Understanding Across Millions of Tokens of Context. _arXiv:2403.05530_, 2024. 
*   Grill et al. [2020] J.-B. Grill, F. Strub, F. Altché, C. Tallec, P. Richemond, E. Buchatskaya, C. Doersch, B. Avila Pires, Z. Guo, and M. Gheshlaghi Azar. Bootstrap Your Own Latent - A New Approach to Self-Supervised Learning. In _Proc. NeurIPS_, 2020. 
*   He et al. [2020] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick. Momentum Contrast for Unsupervised Visual Representation Learning. In _Proc. CVPR_, 2020. 
*   He et al. [2022] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick. Masked Autoencoders Are Scalable Vision Learners. In _Proc. CVPR_, 2022. 
*   Hinton et al. [2015] G. Hinton, O. Vinyals, and J. Dean. Distilling the Knowledge in a Neural Networ. In _Proc. NeurIPS Workshops_, 2015. 
*   Jampani et al. [2023] V. Jampani, K.-K. Maninis, A. Engelhardt, A. Karpur, K. Truong, K. Sargent, S. Popov, A. Araujo, R. Martin-Brualla, K. Patel, D. Vlasic, V. Ferrari, A. Makadia, C. Liu, Y. Li, and H. Zhou. Navi: Category-agnostic image collections with high-quality 3d shape and pose annotations. In _Proc. NeurIPS Datasets and Benchmarks_, 2023. 
*   Jia et al. [2021] C. Jia, Y. Yang, Y. Xia, Y. Chen, Z. Parekh, H. Pham, Q. Le, Y. Sung, Z. Li, and T. Duerig. Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision. In _Proc. ICML_, 2021. 
*   Jose et al. [2025] C. Jose, T. Moutakanni, D. Kang, F. Baldassarre, T. Darcet, H. Xu, D. Li, M. Szafraniec, M. Ramamonjisoa, M. Oquab, O. Siméoni, H. Vo, P. Labatut, and P. Bojanowski. DINOv2 Meets Text: A Unified Framework for Image-and Pixel-Level Vision-Language Alignment. In _Proc. CVPR_, 2025. 
*   Krause et al. [2013] J. Krause, M. Stark, J. Deng, and L. Fei-Fei. 3D Object Representations for Fine-Grained Categorization. In _Proc. ICCV Workshops_, 2013. 
*   Lai et al. [2024] Z. Lai, H. Zhang, B. Zhang, W. Wu, H. Bai, A. Timofeev, X. Du, Z. Gan, J. Shan, C. Chuah, Y. Yang, and M. Cao. VeCLIP: Improving CLIP Training via Visual-enriched Captions. In _Proc. ECCV_, 2024. 
*   Liu et al. [2016] Z. Liu, P. Luo, S. Qiu, X. Wang, and X. Tang. DeepFashion: Powering Robust Clothes Recognition and Retrieval with Rich Annotations. In _Proc. CVPR_, 2016. 
*   Maninis et al. [2025] K. Maninis, K. Chen, S. Ghosh, A. Karpur, K. Chen, Y. Xia, B. Cao, D. Salz, G. Han, J. Dlabal, D. Gnanapragasam, M. Seyedhosseini, H. Zhou, and A. Araujo. TIPS: Text-Image Pretraining with Spatial Awareness. In _Proc. ICLR_, 2025. 
*   Min et al. [2023] W. Min, Z. Wang, Y. Liu, M. Luo, L. Kang, X. Wei, X. Wei, and S. Jiang. Large Scale Visual Food Recognition. _IEEE TPAMI_, 2023. 
*   Mottaghi et al. [2014] R. Mottaghi, X. Chen, P. Liu, S. Fidler, R. Urtasun, and A. Yuille. The Role of Context for Object Detection and Semantic Segmentation in the Wild. In _Proc. CVPR_, 2014. 
*   Naeem et al. [2024] M.F. Naeem, Y. Xian, X. Zhai, L. Hoyer, L.Van Gool, and F. Tombari. SILC: Improving Vision Language Pretraining with Self-Distillation. In _Proc. ECCV_, 2024. 
*   Onoe et al. [2024] Y. Onoe, S. Rane, Z. Berger, Y. Bitton, J. Cho, R. Garg, A. Ku, Z. Parekh, J. Pont-Tuset, G. Tanzer, S. Wang, and J. Baldridge. DOCCI: Descriptions of Connected and Contrasting Images. In _Proc. ECCV_, 2024. 
*   Oquab et al. [2024] M. Oquab, T. Darcet, T. Moutakanni, H. Vo, M. Szafraniec, V. Khalidov, P. Fernandez, D. Haziza, F. Massa, A. El-Nouby, R. Howes, P. Huang, H. Xu, V. Sharma, S. Li, W. Galuba, M. Rabbat, M. Assran, N. Ballas, G. Synnaeve, I. Misra, H. Jegou, J. Mairal, P. Labatut, A. Joulin, and P. Bojanowski. DINOv2: Learning Robust Visual Features without Supervision. _Transactions on Machine Learning Research_, 2024. 
*   Peng et al. [2020] J. Peng, C. Xiao, and Y. Li. RP2K: A Large-Scale Retail Product Dataset forFine-Grained Image Classification. _arXiv:2006.12634_, 2020. 
*   Radford et al. [2021] A. Radford, J.W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal, G. Sastry, A. Askell, P. Mishkin, J. Clark, G. Krueger, and I. Sutskever. Learning Transferable Visual Models from Natural Language Supervision. In _Proc. ICML_, 2021. 
*   Ranftl et al. [2021] R. Ranftl, A. Bochkovskiy, and V. Koltun. Vision Transformers for Dense Prediction. In _Proc. ICCV_, 2021. 
*   Russakovsky et al. [2015] O. Russakovsky, J. Deng, H. Su, J. Krause, S. Satheesh, S. Ma, Z. Huang, A. Karpathy, A. Khosla, M. Bernstein, A. Berg, and L. Fei-Fei. ImageNet Large Scale Visual Recognition Challenge. _IJCV_, 2015. 
*   Shazeer and Stern [2018] N. Shazeer and M. Stern. Adafactor: Adaptive Learning Rates with Sublinear Memory Cost. In _Proc. ICML_, 2018. 
*   Silberman et al. [2012] N. Silberman, D. Hoiem, P. Kohli, and R. Fergus. Indoor Segmentation and Support Inference from RGBD Images. In _Proc. ECCV_, 2012. 
*   Siméoni et al. [2025] O. Siméoni, H. Vo, M. Seitzer, F. Baldassarre, M. Oquab, C. Jose, V. Khalidov, M. Szafraniec, S. Yi, M. Ramamonjisoa, F. Massa, D. Haziza, L. Wehrstedt, J. Wang, T. Darcet, T. Moutakanni, L. Sentana, C. Roberts, A. Vedaldi, J. Tolan, J. Brandt, C. Couprie, J. Mairal, H. Jégou, P. Labatut, and P. Bojanowski. DINOv3. _arXiv:2508.10104_, 2025. 
*   Song et al. [2016] H. Song, Y. Xiang, S. Jegelka, and S. Savarese. Deep Metric Learning via Lifted Structured Feature Embedding. In _Proc. CVPR_, 2016. 
*   Stone et al. [2025] A. Stone, H. Soltau, R. Geirhos, X. Yi, Y. Xia, B. Cao, K. Chen, A. Ogale, and J. Shlens. Learning Visual Composition through Improved Semantic Guidance. In _Proc. CVPR_, 2025. 
*   Sun et al. [2023] Q. Sun, Y. Fang, L. Wu, X. Wang, and Y. Cao. EVA-CLIP: Improved Training Techniques for CLIP at Scale. _arXiv:2303.15389_, 2023. 
*   Tschannen et al. [2023] M. Tschannen, M. Kumar, A. Steiner, X. Zhai, N. Houlsby, and L. Beyer. Image Captioners Are Scalable Vision Learners Too. In _Proc. NeurIPS_, 2023. 
*   Tschannen et al. [2025] M. Tschannen, A. Gritsenko, X. Wang, M. Naeem, I. Alabdulmohsin, N. Parthasarathy, T. Evans, L. Beyer, Y. Xia, B. Mustafa, O. Hénaff, J. Harmsen, A. Steiner, and X. Zhai. SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features. _arXiv:2502.14786_, 2025. 
*   van den Oord et al. [2018] A. van den Oord, Y. Li, and O. Vinyals. Representation Learning with Contrastive Predictive Coding. _arXiv:1807.03748_, 2018. 
*   Van Horn et al. [2018] G. Van Horn, O. Mac Aodha, Y. Song, Y. Cui, C. Sun, A. Shepard, H. Adam, P. Perona, and S. Belongie. The iNaturalist Species Classification and Detection Dataset. In _Proc. CVPR_, 2018. 
*   Vaswani et al. [2017] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. Gomez, L. Kaiser, and I. Polosukhin. Attention is All You Need. In _Proc. NeurIPS_, 2017. 
*   Venkataramanan et al. [2025] S. Venkataramanan, V. Pariza, M. Salehi, L. Knobel, S. Gidaris, E. Ramzi, A. Bursuc, and Y. Asano. Franca: Nested matryoshka clustering for scalable visual representation learning. _arXiv:2507.14137_, 2025. 
*   Wan et al. [2024] B. Wan, M. Tschannen, Y. Xian, F. Pavetic, I. Alabdulmohsin, X. Wang, A. Pinto, A. Steiner, L. Beyer, and X. Zhai. LocCa: Visual Pretraining with Location-aware Captioners. In _Proc. NeurIPS_, 2024. 
*   Weyand et al. [2020] T. Weyand, A. Araujo, B. Cao, and J. Sim. Google Landmarks Dataset v2 - A Large-Scale Benchmark for Instance-Level Recognition and Retrieval. In _Proc. CVPR_, 2020. 
*   Wu et al. [2023] Q. Wu, H. Ye, Y. Gu, H. Zhang, L. Wang, and D He. Denoising Masked AutoEncoders Help Robust Classification. In _Proc. ICLR_, 2023. 
*   Xie et al. [2022] Z. Xie, Z. Zhang, Y. Cao, Y. Lin, J. Bao, Z. Yao, Q. Dai, and H. Hu. SimMIM: A Simple Framework for Masked Image Modeling. In _Proc. CVPR_, 2022. 
*   Xu et al. [2025] H. Xu, S. Xie, X.Tan, P. Huang, R. Howes, V. Sharma, S. Li, G. Ghosh, L. Zettlemoyer, and C. Feichtenhofer. Demystifying CLIP Data. In _Proc. ICLR_, 2025. 
*   Xue et al. [2023] H. Xue, P. Gao, H. Li, Y. Qiao, H. Sun, H. Li, and J. Luo. Stare at What You See: Masked Image Modeling without Reconstruction. In _Proc. CVPR_, 2023. 
*   Young et al. [2014] P. Young, A. Lai, M. Hodosh, and J. Hockenmaier. From Image Descriptions to Visual Denotations: New Similarity Metrics for Semantic Inference over Event Descriptions. _TACL_, 2014. 
*   Ypsilantis et al. [2021] N.-A. Ypsilantis, N. Garcia, G. Han, S. Ibrahimi, N. Van Noord, and G. Tolias. The Met Dataset: Instance-level Recognition for Artworks. In _Proc. NeurIPS Datasets and Benchmarks Track_, 2021. 
*   Ypsilantis et al. [2023] N.-A. Ypsilantis, K. Chen, B. Cao, M. Lipovský, P. Dogan-Schönberger, G. Makosa, B. Bluntschli, M. Seyedhosseini, O. Chum, and A. Araujo. Towards Universal Image Embeddings: A Large-Scale Dataset and Challenge for Generic Image Representations. In _Pro. ICCV_, 2023. 
*   Zhai et al. [2023] X. Zhai, B. Mustafa, A. Kolesnikov, and L. Beyer. Sigmoid Loss for Language Image Pre-Training. In _Proc. ICCV_, 2023. 
*   Zhou et al. [2017] B. Zhou, H. Zhao, X. Puig, S. Fidler, A. Barriuso, and A. Torralba. Scene Parsing Through ADE20k Dataset. In _Proc. CVPR_, 2017. 
*   Zhou et al. [2019] B. Zhou, H. Zhao, X. Puig, T. Xiao, S. Fidler, A. Barriuso, and A. Torralba. Semantic Understanding of Scenes through the ADE20K Dataset. _IJCV_, 2019. 
*   Zhou et al. [2022a] C. Zhou, C. Loy, and B. Dai. Extract Free Dense Labels from CLIP. In _Proc. ECCV_, 2022a. 
*   Zhou et al. [2022b] J. Zhou, C. Wei, H. Wang, W. Shen, C. Xie, A. Yuille, and T. Kong. Image Bert Pre-training with Online Tokenizer. In _Proc. ICLR_, 2022b. 

 Experimental support, please [view the build logs](https://arxiv.org/html/2604.12012v1/__stdout.txt) for errors. Generated by [L A T E xml![Image 110: [LOGO]](blob:http://localhost/70e087b9e50c3aa663763c3075b0d6c5)](https://math.nist.gov/~BMiller/LaTeXML/). 

## Instructions for reporting errors

We are continuing to improve HTML versions of papers, and your feedback helps enhance accessibility and mobile support. To report errors in the HTML that will help us improve conversion and rendering, choose any of the methods listed below:

*   Click the "Report Issue" () button, located in the page header.

**Tip:** You can select the relevant text first, to include it in your report.

Our team has already identified [the following issues](https://github.com/arXiv/html_feedback/issues). We appreciate your time reviewing and reporting rendering errors we may not have found yet. Your efforts will help us improve the HTML versions for all readers, because disability should not be a barrier to accessing research. Thank you for your continued support in championing open access for all.

Have a free development cycle? Help support accessibility at arXiv! Our collaborators at LaTeXML maintain a [list of packages that need conversion](https://github.com/brucemiller/LaTeXML/wiki/Porting-LaTeX-packages-for-LaTeXML), and welcome [developer contributions](https://github.com/brucemiller/LaTeXML/issues).

BETA

[](javascript:toggleReadingMode(); "Disable reading mode, show header and footer")


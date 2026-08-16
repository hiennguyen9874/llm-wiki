Title: ModernVBERT: Towards Smaller Visual Document Retrievers

URL Source: https://arxiv.org/html/2510.01149

Markdown Content:
Paul Teiletche 1,2 Quentin Macé 1,3 Max Conti 1 Antonio Loison 1

Gautier Viaud 1 Pierre Colombo 3,4 Manuel Faysse 1,3
1 Illuin Technology 2 EPFL 3 CentraleSupélec, Paris-Saclay 4 Equall.ai 

[paul.teiletche@epfl.ch](https://arxiv.org/html/2510.01149v3/paul.teiletche@epfl.ch)

###### Abstract

Retrieving specific information from a large corpus of documents is a prevalent industrial use case of modern AI, notably due to the popularity of Retrieval-Augmented Generation (RAG) systems. Although neural document retrieval models have historically operated exclusively in the text space, Visual Document Retrieval (VDR) models – large vision–language decoders repurposed as embedding models which directly work with page screenshots as inputs – are increasingly popular due to the performance and indexing latency gains they offer. In this work, we show that, while cost-efficient, this approach of repurposing generative models bottlenecks retrieval performance. Through controlled experiments, we revisit the entire training pipeline, and establish a principled recipe for improving visual document retrieval models. We notably measure the impact of attention masking, image resolution, modality alignment data regimes, and late interaction centered contrastive objectives which emerge as central performance factors. Building on these insights, we release _ModernVBERT_, a compact 250M-parameter vision–language encoder that outperforms recent models up to 10 times larger when fine-tuned on document retrieval tasks, enabling efficient inference on cheap CPU hardware and greatly reducing latency and costs while maintaining strong performance. Models, code and data are available at [https://huggingface.co/ModernVBERT](https://huggingface.co/ModernVBERT).

1 Introduction
--------------

![Image 1: Refer to caption](https://arxiv.org/html/2510.01149v3/x1.png)

Figure 1: Pareto efficiency._ColModernVBERT_ outperforms models in its category on ViDoRe, achieving a leading performance-size tradeoff. 

The ability to quickly locate specific information in vast document collections is a core building block of digital systems today, supporting use cases that range from web search and virtual assistants to enterprise knowledge management. Neural information retrieval (IR) models, and in particular dense retrievers, have become the de facto backbone of modern search systems thanks to their strong semantic matching capabilities and good scalability properties (reimers_sentence-bert_2019; karpukhin_dense_2020; wang_text_2022).

This trend is amplified by the widespread adoption of Retrieval-Augmented Generation (RAG) (lewis_retrieval-augmented_2020), where a retriever is used to select a small set of relevant documents that condition a downstream generator. In such systems, the first-stage retrieval module is a well-known bottleneck: its recall directly upper-bounds the quality of the generated answers, while its latency and indexing costs partially drive the overall system efficiency (lin-byrne-2022-retrieval). As a result, improving document retrieval, especially for long, complex files such as PDFs, scientific articles, and reports, is a key lever for making industrial RAG deployments more accurate and cost-effective. Visual Document Retrieval. Historically, document retrieval in these settings has operated purely in the text space. To index PDFs or scans, practitioners first run heavy preprocessing pipelines that include Optical Character Recognition (OCR), layout analysis, and heuristic passage segmentation, before embedding the resulting text spans with a neural encoder. This approach suffers from several limitations: OCR and layout parsing can be brittle and slow, complex visual elements such as tables, figures, and typography are often poorly captured, and any error or bias introduced during preprocessing is propagated to the retriever.

Visual Document Retrieval (VDR) has emerged as a compelling alternative to such text-based systems. Rather than indexing pre-extracted textual content, VDR models directly operate on page screenshots: given a user query, they retrieve relevant document pages by matching the query against image-based representations of the pages (faysse2025colpaliefficientdocumentretrieval). By bypassing OCR and layout parsing, VDR yields simpler end-to-end pipelines, significantly reduces indexing latency, and better exploits visual cues such as layout, figures, and fonts, while achieving strong performance on visually rich benchmarks like ViDoRe.

Limits of Generative VLM Repurposing. Most current VDR systems are obtained by repurposing large generative vision–language decoders (alayrac2022flamingovisuallanguagemodel) as retrieval encoders via post-hoc contrastive fine-tuning (ma2024unifyingmultimodalretrievaldocument; faysse2025colpaliefficientdocumentretrieval; jiang2025vlm2vectrainingvisionlanguagemodels). While cost-efficient, this design choice bottlenecks retrieval performance and efficiency: model sizes, attention patterns, image resolutions, and training objectives are designed for generative use cases rather than optimized for retrieval which has been shown in text models to be suboptimal (lee2025nvembedimprovedtechniquestraining; gisserotboukhlef2025pretrainencodersmaskedlanguage). Furthermore, scaling trends (wei2022emergentabilitieslargelanguage) are less pronounced for embedding models; while correlated with model size, strong retrieval performance remains attainable with small models (clavié2024bettermonolingualjapaneseretrievers).

Recent papers and model releases in the visual retrieval space have claimed performance improvements by scaling the amount of contrastive data and the compute budget (zhang2025gmeimprovinguniversalmultimodal; xu2025llamanemoretrievercolembedtopperforming), modifying the attention mask (chen2025mocamodalityawarecontinualpretraining), increasing image resolutions (cohere_introducing_2024) or by introducing more diverse tasks and data sources (jiang2025vlm2vectrainingvisionlanguagemodels).

In this work, we attempt to centralize these efforts and systematically disentangle the impact of core design decisions in visual retriever training. Through controlled experiments—ranging from language model pretraining to multi-stage, domain-specific fine-tuning, we aim to answer a central question:

Which design choices best boost performance in modern visual document retrievers?

Contribution 1. We revisit core assumptions in visual retriever design, showing that token-level training objectives benefit retrievers by strengthening image–text token alignment—rather than merely producing stronger image embeddings. Our results indicate that causal attention is suboptimal in document retrieval, with bidirectional masking offering clear improvements in multi-vector settings, and that other parameters such as image resolution data mixes should not be overlooked in the training pipeline.

Contribution 2: _ModernVBERT_. Building on these insights, we release _ModernVBERT_, a small 250M multimodal encoder that aligns a pretrained language encoder with a vision encoder through Masked Language Modeling (MLM) objective, and _ColModernVBERT_ a variant fine-tuned for document retrieval. Despite its modest size and limited training budget, _ColModernVBERT_ matches models 10x larger on standard visual document retrieval benchmarks, demonstrating the interest of designing a retrieval focused model from the ground up. We release the model, intermediate checkpoints, and the training code at [https://huggingface.co/ModernVBERT](https://huggingface.co/ModernVBERT).

2 Methodology
-------------

Our analysis aims at quantifying the impact of design decisions made when training visual retrievers. In opposition to previous work, we begin our analysis as early as language model modality alignment and iteratively study design choices by modifying design choices independently to reduce confounding factors as much as possible (allenzhu2025physicslanguagemodels1).

Controlled Experimental Setup. A central point of interest is the impact of causal and bidirectional attention masks. While recently studied for textual representation applications (gisserotboukhlef2025pretrainencodersmaskedlanguage; weller2025seqvsseqopen), we extend the experiment to the vision modality. We use checkpoints released by gisserotboukhlef2025pretrainencodersmaskedlanguage which consist in a series of identical 210M parameter transformer models based on the Llama architecture (touvron_llama_2023) trained on 100B tokens that differ only in their attention masking strategy during language model training but that are perfectly identical in terms of training data seen, model size and architecture, learning rate scheduling, etc… The checkpoints we use are enc a bidirectional encoder trained with Masked Language Modeling (MLM), dec, a causal decoder trained with next token prediction, and dec-enc a causal decoder annealed over the end of its textual training by removing the causal mask and switching the training objective to MLM. For the vision tower, we employ the vision component of siglip2-base-16b-512(tschannen2025siglip2multilingualvisionlanguage), a 86M parameter vision transformer contrastively trained on billions of text-image pairs. All ablations thus stem from iso-data controlled setups, and as further described, are further trained on the same data sequence, with the same batch sizes, optimizers, schedulers and on the same hardware.

![Image 2: Refer to caption](https://arxiv.org/html/2510.01149v3/figures/vbert_architecture.png)

Figure 2: MLM-based early fusion architecture. The visual encoder produces patch representations, which are passed to a language model. Our end-to-end bidirectional attention fused architecture is trained with Masked Language Modeling objectives and is perfectly suited for sequence and token-level representation tasks.

Model Architecture. Our analysis are not centered around model architectures and to draw broadly applicable insights, we design vision-language models following current standard training practices. In line with most recent work, we employ the early fusion architecture (alayrac2022flamingovisuallanguagemodel) illustrated in Figure[2](https://arxiv.org/html/2510.01149v3#S2.F2 "Figure 2 ‣ 2 Methodology ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"), in which visual patch embeddings produced by the vision encoder are projected into the language model input embedding space and concatenated with text token embeddings to encourage joint processing (li2022blipbootstrappinglanguageimagepretraining; alayrac2022flamingovisuallanguagemodel; wang2024qwen2vlenhancingvisionlanguagemodels; yang2025qwen251mtechnicalreport; marafioti2025smolvlmredefiningsmallefficient). As described in [subsection 2.1](https://arxiv.org/html/2510.01149v3#S2.SS1 "2.1 Modality Alignment ‣ 2 Methodology ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"), we generalize the training loss to function both with causal and masked language modeling objectives. To handle dynamic resolutions, we split large images into 512×\times 512 pixel tiles as expected by the SigLIP encoder 1 1 1 Images are downscaled (or upscaled) so that the lengths and widths reach a multiple of 512 pixels to preserve the aspect ratio, padding is used on the smaller side when necessary (i.e. a 1024x1000 px image would be padded to 1024x1024 px).. Following current standard practices, we further process a downscaled version of the full image to improve inter-tile consistency and global visual understanding(lin2023sphinxjointmixingweights; ye2023ureaderuniversalocrfreevisuallysituated). The vision tower produces 1024 pixel patch representations for each tile 2 2 2 The SigLIP tower takes 512x512 px images and process them by 16x16 px patches (dosovitskiy_image_2020). This results in (512/16)2=1024(512/16)^{2}=1024 patches., which we compress to 64 tokens through pixel shuffling(shi2016realtimesingleimagevideo) with a compression ratio r=4 r=4, following prior work on models of comparable size(marafioti2025smolvlmredefiningsmallefficient). We highlight the impact of image resolution and this parameter on the number of visual tokens in Appendix[C.6.1](https://arxiv.org/html/2510.01149v3#A3.SS6.SSS1 "C.6.1 Image Resolution Tradeoffs ‣ C.6 Model Latency ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers").

Training Procedure. Our experiments focus on retrieval performance. We employ a standard biphasic training procedure, in which we first run modality alignment to train a pretrained textual language model to understand visual inputs through language modeling objectives (liu2023visualinstructiontuning) ([subsection 2.1](https://arxiv.org/html/2510.01149v3#S2.SS1 "2.1 Modality Alignment ‣ 2 Methodology ‣ ModernVBERT: Towards Smaller Visual Document Retrievers")), then rely on a second text-image contrastive learning phase to learn efficient image representations (radford2021learningtransferablevisualmodels) ([subsection 2.2](https://arxiv.org/html/2510.01149v3#S2.SS2 "2.2 Contrastive Post-Training ‣ 2 Methodology ‣ ModernVBERT: Towards Smaller Visual Document Retrievers")). We further describe the general setup, and detail specific modifications to the default training procedure in the experiment section.

### 2.1 Modality Alignment

We align the vision encoder tower with the language model by training the image embedding projection layer to map visual features into the language model embedding space. The pretrained language model is also fine-tuned with Low-Rank Adapters (LoRA) (hu2021loralowrankadaptationlarge), allowing both image and text models to adapt jointly while reducing the risk of monomodal performance collapse (alayrac2022flamingovisuallanguagemodel; liu2023visualinstructiontuning; laurençon2024mattersbuildingvisionlanguagemodels; mckinzie2024mm1methodsanalysis; marafioti2025smolvlmredefiningsmallefficient).

Alignment Loss. For decoder‑based models, we train with Causal Language Modeling (CLM) loss on the text tokens, as standardly done in VLM modality alignment:

ℒ CLM=−∑t=1 T log⁡P θ​(x t∣x<t),\mathcal{L}_{\text{CLM}}=-\sum_{t=1}^{T}\log P_{\theta}\!\bigl(x_{t}\mid x_{<t}\bigr),(1)

where x<t x_{<t} denotes all tokens preceding position t t. We generalize this training scheme to bidirectional encoders models, by using the Masked Language Modeling (MLM) loss on the textual tokens:

ℒ MLM=−∑t∈ℳ log⁡P θ​(x t∣x\ℳ),\mathcal{L}_{\text{MLM}}=-\sum_{t\in\mathcal{M}}\log P_{\theta}\!\bigl(x_{t}\mid x_{\backslash\mathcal{M}}\bigr),(2)

where ℳ\mathcal{M} is the set of masked token positions and x\ℳ x_{\backslash\mathcal{M}} is the input with those tokens masked out.

Modality Alignment Corpus. Models are modality aligned on a large corpus in large parts derived from The Cauldron 2(laurençon2024mattersbuildingvisionlanguagemodels) and Docmatix(laurençon2024building). Our objective being to train document focused retrieval models, we use an adjusted training mixture that upsamples images containing text and documents with varying level of complexities. Our final training corpus consists of approximately 2B text tokens, and includes diverse sources such as web pages, books, and scientific papers. Mixture details are given in Appendix[A.3.1](https://arxiv.org/html/2510.01149v3#A1.SS3.SSS1 "A.3.1 Modality Alignment Mixture ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"). We note that controlling the exact data distribution during this phase enables the models we train to specialize early and achieve good document focused downstream performances which many large models struggle with (liu_improved_2023).

Parameters. All models are trained using a masking ratio of 0.5 and user-prompt masking to avoid overfitting on chat-template format(huertaenochian2024instructionfinetuningdoesprompt; shi2024instructiontuninglossinstructions; allal2025smollm2smolgoesbig). We employ WSD scheduler(hu2024minicpmunveilingpotentialsmall) with the first 5% of the training as warmup, the last 20% as decay and a maximum learning rate of 1e-4. The ablation models are aligned on 3.5B tokens. We provide additional details on the training setup in Appendix[A.1](https://arxiv.org/html/2510.01149v3#A1.SS1 "A.1 Implementation and Resources ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers").

### 2.2 Contrastive Post-Training

Once the language model has learned to process image tokens jointly with text tokens, we specialize models through a contrastive post-training stage designed to enhance the semantic representation of the output embeddings produced by the model (reimers_sentence-bert_2019).

Post-training Pairs. The post-training dataset used as starting point in our ablations comprises 118k document-query pairs from the ColPali corpus faysse2025colpaliefficientdocumentretrieval as well as another 118k of natural image-description pairs from the MSCOCO train set(lin2015microsoftcococommonobjects).

Contrastive Loss. We employ the InfoNCE loss(oord2019representationlearningcontrastivepredictive), defined as

ℒ InfoNCE​(𝐪,𝐝+)=−log⁡Φ​(𝐪,𝐝+)Φ​(𝐪,𝐝+)+∑𝐝−∈𝒩 q Φ​(𝐪,𝐝−),\mathcal{L}_{\text{InfoNCE}}(\mathbf{q},\mathbf{d^{+}})=-\log\frac{\Phi(\mathbf{q},\mathbf{d^{+}})}{\Phi(\mathbf{q},\mathbf{d^{+}})+\sum_{\mathbf{d^{-}}\in\mathcal{N}_{q}}\Phi(\mathbf{q},\mathbf{d^{-}})},(3)

where 𝐝+\mathbf{d^{+}} denotes the positive target for the query 𝐪\mathbf{q}, 𝒩 𝐪=𝒩 𝐪 in∪𝒩 𝐪 hard\mathcal{N}_{\mathbf{q}}=\mathcal{N}_{\mathbf{q}}^{\text{in}}\cup\mathcal{N}_{\mathbf{q}}^{\text{hard}} the set of negative targets (in-batch and hard negatives when mentioned), and Φ​(𝐪,𝐝)\Phi(\mathbf{q},\mathbf{d}) a similarity function between the token(s) of the query and the documents.3 3 3 We use the last (EOS) token for causal models, and mean pool all sequence tokens for bidirectional encoders for single-vector models. Alternatively, we use all document and query tokens without pooling for late interaction matching (faysse2025colpaliefficientdocumentretrieval). Details in Appendix[A.2](https://arxiv.org/html/2510.01149v3#A1.SS2 "A.2 Similarity Functions ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"). For general-domain post-training we compute the loss symmetrically(radford2021learningtransferablevisualmodels).

Batches Curation. In contrastive learning, batch diversity critically impacts retrieval entropy. Overly heterogeneous batches lead to trivial retrievals, while curated batches yield richer training signals. We employ task-aware batching(li2023generaltextembeddingsmultistage), grouping documents by source to ensure a homogeneous batch composition.

### 2.3 Ablation Evaluation Setup

The contrastively trained models are evaluated on retrieval and zero-shot classification tasks across multiple domains. Although the main focus remains document retrieval capabilities, evaluated by aggregating scores from the ViDoRe and ViDoRe v2 4 4 4 We report only the English splits of ViDoRe v2, as our base models are trained on English data only.(macé2025vidorebenchmarkv2raising) benchmarks (nDCG@5), we also assess more generalist image retrieval capabilities by selecting tasks from MIEB(xiao2025miebmassiveimageembedding). For natural image retrieval, we aggregate MSCOCO retrieval (lin2015microsoftcococommonobjects) and Flickr30k retrieval (nDCG@10) (plummer2016flickr30kentitiescollectingregiontophrase) test sets. Finally, following practices in (muennighoff_mteb_2022), we assess both zero-shot and fine-tuning abilities of our models on general classification tasks. Specifically, we measure classification accuracy by fine-tuning a logistic regression head on top of our model’s embedding on Stanford Cars(6755945) and Food101(10.1007/978-3-319-10599-4_29), and we evaluate zero-shot performance on FER2013(khaireddin2021facialemotionrecognitionstate) and EuroSAT(helber2019eurosatnoveldatasetdeep) and aggregate the results.

3 What Makes a Great Visual Retriever?
--------------------------------------

![Image 3: Refer to caption](https://arxiv.org/html/2510.01149v3/x2.png)

Figure 3: Impact of Modality Alignment objective on downstream tasks. Early Fusion of vision and text models boosts document retrieval tasks regardless of the LM objective, but degrades natural image and classification tasks w.r.t. the standalone fine-tuned vision model SigLIP. Reported scores are aggregated MIEB scores (nDCG, Accuracy.)

Vision-language retrievers built upon existing generative VLMs often inherit design choices and weights that may not be well suited for all embedding tasks. Here, we analyze these critical design choices hoping to derive clear insights for developing efficient visual retrievers. Importantly, although we assess design decisions at different stages of the training pipelines, evaluation are always done end-to-end on the final evaluation signal.

### 3.1 Modality Alignment Design

Language modeling Modality Alignment improves document understanding. According to benchmarks such as MIEB(xiao2025miebmassiveimageembedding), dual encoder models explicitly trained on contrastive image-text tasks outperform repurposed VLMs in natural image classification tasks. To assess this, we train an encoder and a decoder vision-language model using the methodology described in [section 2](https://arxiv.org/html/2510.01149v3#S2 "2 Methodology ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") on a mix of natural image and document data (alignment and contrastive training). We compare them with SigLIP2-FT, the 378M dual vision encoder model whose vision component is used by the vision tower of both VLMs, and with the larger SigLIP2-FT Large (881M parameters). Both SigLIP-FT models are finetuned in the same conditions as the VLMs, and initialized from pre-trained weights from scratch on billions of text-image pairs 5 5 5 We report the performance of the untrained off-the-shelf SigLIP in Appendix[C.1](https://arxiv.org/html/2510.01149v3#A3.SS1 "C.1 Performance Against Off-the-Shelf Dual Encoder ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"). As shown in Figure[3](https://arxiv.org/html/2510.01149v3#S3.F3 "Figure 3 ‣ 3 What Makes a Great Visual Retriever? ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"), the two early fusion VLM variants severely underperform the SigLIP2-FT dual encoders on natural image tasks. In contrast, they achieve significant gains on document retrieval tasks (+6.1 nDCG@5 on ViDoRe and ViDoRe v2 datasets w.r.t. base), even edging out SigLIP2-FT Large that contains 3.5x vision parameters more than both VLMs.

This confirms large-scale contrastive training remains best for high-level image representation tasks (natural images), but sequentially combining a vision model with a pretrained language model facilitates document representation tasks, even with significantly less contrastive post-training. As the rest of this paper shows, steering away from the dual encoder architecture further enables improving performance through many avenues other than text to image contrastive training, for which supervised training samples can be hard to obtain.

Scaling the modality alignment phase for better token representations. Prior work shows that scaling the modality alignment phase of VLMs improves their generative abilities(beyer2024paligemmaversatile3bvlm; mckinzie2024mm1methodsanalysis; wang2024qwen2vlenhancingvisionlanguagemodels). We test whether similar gains hold in retrieval by contrastively fine-tuning enc checkpoints during MLM modality alignment. Figure[4](https://arxiv.org/html/2510.01149v3#S3.F4 "Figure 4 ‣ 3.1 Modality Alignment Design ‣ 3 What Makes a Great Visual Retriever? ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") illustrates the results of post-trained checkpoints on diverse tasks. Although document retrieval improves consistently with more modality alignment data – largely surpassing the vision tower evaluated in isolation and showing clear scaling benefits – natural image tasks plateau past 1B tokens, far from the standalone dual encoder baseline. This shows that document and natural image retrieval leverage different mechanisms and should not be optimized the same way. Document Retrieval benefits from learning fine-grained interactions between image and text tokens through the language model, while the LM has limited utility for high level natural image tasks.

![Image 4: Refer to caption](https://arxiv.org/html/2510.01149v3/x3.png)

Figure 4: Modality alignment scaling of early fusion encoders for up to 1 epoch (3.5B tokens) of data. The dashed line indicates the vision encoder evaluated standalone without further training. Our findings show that retrieval tasks benefits from extended modality alignment phase, particularly in document retrieval, where performance quickly surpasses that of the standalone vision encoder. 

Bidirectional attention fully unlocks Late Interaction. Inspired by the effectiveness of bidirectional attention in text-only retrieval(gisserotboukhlef2025pretrainencodersmaskedlanguage; weller2025seqvsseqopen)6 6 6 chen2025mocamodalityawarecontinualpretraining investigate post-hoc removal of the attention mask during visual retrieval fine-tuning., we investigate if it surpasses causal attention in visual document retrieval, particularly when using the multi-vector late interaction matching common in SOTA visual retrievers(khattab_colbert_2020; faysse2025colpaliefficientdocumentretrieval). Figure[5](https://arxiv.org/html/2510.01149v3#S3.F5 "Figure 5 ‣ 3.1 Modality Alignment Design ‣ 3 What Makes a Great Visual Retriever? ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") reports single vector and late interaction results on the ViDoRe benchmark for various model variants. On top of the standard enc (MLM) and dec (CLM) models, we evaluate the dec-enc and the dec models modality aligned with MLM objectives to determine whether bidirectional attention capabilities can be obtained in later stages of training.

Single-vector embedding results are close between bidirectional and causal attention models for document retrieval, with enc slightly outperforming dec by +1.6 nDCG@5.

Intuitively however, bidirectional attention makes a huge difference when used in late interaction settings, substantially exceeding the causal counterpart by +10.6 nDCG@5. Causal decoders are incapable of correctly contextualizing image or text token representations seen at the beginning of the sequences. This is a key result as almost all current visual retrievers, including late interaction variants, are causal models, clearly indicating some performance is left on the table.

Removing the causal attention mask during training does not suffice to recover the enc late interaction performance at these data regimes. This indicates converting trained decoders as late interaction retrievers is highly non trivial, and confirms the insights from weller2025seqvsseqopen; when possible, training encoder models from scratch remain better for retrieval tasks.

![Image 5: Refer to caption](https://arxiv.org/html/2510.01149v3/x4.png)

Figure 5: Impact of attention masks and training objectives on document retrieval performances. We report the average nDCG@5 on English splits of ViDoRe benchmarks for models post-trained on ColPali. 

HR Cooldown Document Retrieval Image/Caption Retrieval Image Classification Average
512px✗30.7 58.8 41.4 43.6
1024px✗42.2 58.9 37.2 46.1
2048px✗43.8 57.6 33.9 45.1
2048px✓45.8 57.8 33.7 45.8

Table 1: Effect of image resolution on VL encoder abilities. Document retrieval performance increases with higher image resolution. Further annealing the encoder on high-resolution images (HR Cooldown) at the end of modality alignment yields additional gains. By contrast, for non-document tasks, raising the resolution tends to degrade performance.

### 3.2 Contrastive Training Design

The previous subsection established bidirectional encoder models to often be the best option when training visual retrievers. In the following experiments, we assess contrastive training choices and only report results for the encoder model for simplicity.

Image resolution benefits are task-specific. Image resolution plays a critical role in VLM generative capabilities, notably in document-focused tasks, as higher-resolution inputs enables the model to capture finer visual cues(hu2024mplugdocowl2highresolutioncompressingocrfree; marafioti2025smolvlmredefiningsmallefficient). Modality alignment is done at a fixed image resolution of 1024 pixels (longer side) and we report scores of contrastive training runs with varying settings in Table[1](https://arxiv.org/html/2510.01149v3#S3.T1 "Table 1 ‣ Figure 5 ‣ 3.1 Modality Alignment Design ‣ 3 What Makes a Great Visual Retriever? ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"). To vary the resolution, images of the highest quality available are scaled to the desired size (often downscaled) before being fed to the image tokenizer. Our findings confirm that embedding tasks are strongly sensitive to image-resolution. In particular, training with higher resolution inputs substantially improves the results on visual document retrieval benchmarks, consistent with prior work in generative settings beyer2024paligemmaversatile3bvlm; mckinzie2024mm1methodsanalysis. Furthermore, adding a cool-down phase by showing higher-resolution images towards the end of the modality alignment phase yields additional gains. This suggests that models can adapt their attention mechanisms to finer details when exposed to increased resolution. Interestingly, these findings do not hold in natural image tasks, where high resolution can even degrade performance.

Document Retrieval Image/Caption Retrieval Image Classification Average
Baseline CL Mix 43.9 57.2 36.1 45.7
+ Text→\rightarrow Text Pairs 45.6 53.2 35.7 44.8
+ Image→\rightarrow Caption Pairs 45.8 54.4 49.9 50.0

Table 2: Impact of contrastive training mixtures on downstream tasks. Incorporating text-only pairs improves performance on document retrieval, but degrades other performances. Adding natural images-captions pairs substantially enhances performance on classification tasks.

Increasing the pool of contrastive pairs. A severe limitation that current visual retrievers face is the lack of large volumes of high quality (document image, query pairs). Previous work (ma2024unifyingmultimodalretrievaldocument; faysse2025colpaliefficientdocumentretrieval; jiang2025vlm2vectrainingvisionlanguagemodels; zhang2025gmeimprovinguniversalmultimodal) has relied on a mix of repurposed existing visual question answering datasets and synthetically generated queries with external LLMs. Even put together however, the field is only a year old, and these datasets remain small in size and often of poor quality.

A central question in our study is whether the abundance of _text-only_ query–document pairs can be exploited to improve _visual_ retrieval via cross-modal capability transfer. To probe this, we run contrastive training under three regimes. Unlike prior work that “warms up” visual retrievers or trains exclusively with text-only pairs (ma2024unifyingmultimodalretrievaldocument; jiang2024e5vuniversalembeddingsmultimodal), we _interleave_ text-only pairs and text–image pairs throughout training at a 1:1 ratio. The dataset sources are detailed in Appendix[A.3.3](https://arxiv.org/html/2510.01149v3#A1.SS3.SSS3 "A.3.3 Contrastive Training Mix ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers")

As reported in Table[2](https://arxiv.org/html/2510.01149v3#S3.T2 "Table 2 ‣ 3.2 Contrastive Training Design ‣ 3 What Makes a Great Visual Retriever? ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"), incorporating text-only pairs yields a sizeable improvement on visual document retrieval (+1.7 nDCG@5), indicating clear cross-modal transfer—likely facilitated by the backbone’s jointly learned text–image embedding space. This result suggests that domain-specific training corpora can be assembled irrespective of native modality, reducing duplication of effort and lowering data-collection costs.

We further evaluate training with NatCap, a corpus of natural images paired with synthetic, highly detailed captions (see Appendix[A.3.2](https://arxiv.org/html/2510.01149v3#A1.SS3.SSS2 "A.3.2 NatCap ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers")). This scaling step improves downstream performance across the board—most notably on natural-image tasks, and with a smaller but consistent gain on document retrieval (+0.2 nDCG@5). Together, these findings underscore the importance of scaling contrastive learning with high-quality data, but which doesn’t need to be exclusively image document focused.

4 Building a Small yet Mighty Visual Retriever.
-----------------------------------------------

### 4.1 Training.

Recipe. Putting together the results from our experiments, we devise a training recipe for a small visual document retriever _ModernVBERT_. It combines a state-of-the-art 150M text bidirectional encoder(weller2025seqvsseqopen) with the ModernBERT architecture (modernbert) and a small vision encoder SigLIP2-16B-512 of 100M parameters(tschannen2025siglip2multilingualvisionlanguage). We modality align both models with a MLM objective for 10B tokens, 3 times longer than during our experiments. To boost document understanding, we augment the input image resolution from 1024px to 2048px during a modality alignment cooldown stage (2B tokens). We call the resulting model _ModernVBERT_. Following the findings of Section[2](https://arxiv.org/html/2510.01149v3#S3.T2 "Table 2 ‣ 3.2 Contrastive Training Design ‣ 3 What Makes a Great Visual Retriever? ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"), we then scale the contrastive training mix from previous experiments to combine document–query pairs with text-only pairs, and use 1 hard negatives for each document-query pair and 2 for each text-only pairs. We opt for a 2/1 text-to-image ratio following our ablation results introduced in Appendix[C.3.1](https://arxiv.org/html/2510.01149v3#A3.SS3.SSS1 "C.3.1 Optimal Text-To-Image Ratio for Document Retrieval ‣ C.3 Bridging the Gap with Longer Contrastive Training ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"). This results in _ColModernVBERT_, a compact late interaction model. For reference, we also train Bi _ModernVBERT_, a single vector variant. More training details are provided in Appendix[A.1](https://arxiv.org/html/2510.01149v3#A1.SS1 "A.1 Implementation and Resources ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers").

### 4.2 Results.

Late Interaction Model Size (B)ViDoRe(v1)ViDoRe(v2,eng)Average Latency (ms)
≥\geq 1B Parameters
MoCa-3B(chen2025mocamodalityawarecontinualpretraining)3.75 80.1 53.8 66.9 158
VLM2Vec(jiang2025vlm2vectrainingvisionlanguagemodels)4.15 49.8 36.5 43.1 211
GME-Qwen2(zhang2025gmeimprovinguniversalmultimodal)8.29 89.9 61.8 75.8 412
E5-V(jiang2024e5vuniversalembeddingsmultimodal)8.36 62.7 49.4 56.1 434
ColPali(faysse2025colpaliefficientdocumentretrieval)✓2.92 81.6 56.8 69.2 175
ColQwen2.5(faysse2025colpaliefficientdocumentretrieval)✓3.75 89.5 61.5 75.5 158
Jina-v4(günther2025jinaembeddingsv4universalembeddingsmultimodal)✓3.75 90.4 60.1 75.2 158
NemoRetriever-3B(xu2025llamanemoretrievercolembedtopperforming)✓4.40 91.0 66.3 78.7 155
≤\leq 1B Parameters
Jina CLIP∗(koukounas_jina_2024)0.22 17.6 14.0 15.8 14
BGE Visualized M3∗(zhou2024vistavisualizedtextembedding)0.87 12.4 10.2 11.3 38
SigLIP2-L-512/16∗(tschannen2025siglip2multilingualvisionlanguage)0.88 43.8 27.0 35.4 25
ColFlor(masrycolflor)✓0.17 68.8 43.0 55.9 17
_BiModernVBERT_ (ours)0.25 63.6 35.7 49.7 20
_ColModernVBERT_ (ours)✓0.25 81.2 56.0 68.6 20

Table 3: Performance on ViDoRe. Our model _ColModernVBERT_ offers the best performance-size tradeoff, significantly outperforming existing sub-1B models and matching the performance of models up to 10x larger with substantially lower inference CPU latency Details and GPU latencies in Appendix [C.6.2](https://arxiv.org/html/2510.01149v3#A3.SS6.SSS2 "C.6.2 Online Query Encoding Latency ‣ C.6 Model Latency ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"). Models marked with ∗ are not specifically trained for VDR. Bold values indicate the best performance amongst sub-1B models.

_ColModernVBERT_. The resulting model, _ColModernVBERT_ showcases strong performances on visual document retrieval benchmarks, especially relative to its size category (Figure[1](https://arxiv.org/html/2510.01149v3#S1.F1 "Figure 1 ‣ 1 Introduction ‣ ModernVBERT: Towards Smaller Visual Document Retrievers")). Despite having over 10 times less parameters than models such as ColPali released only a year ago, it is only 0.6 nDCG@5 points below on the aggregated ViDoRe benchmark scores ([Table 3](https://arxiv.org/html/2510.01149v3#S4.T3 "Table 3 ‣ 4.2 Results. ‣ 4 Building a Small yet Mighty Visual Retriever. ‣ ModernVBERT: Towards Smaller Visual Document Retrievers")). It also edges many larger single-vector repurposed VLM models released within the year (chen2025mocamodalityawarecontinualpretraining; jiang2024e5vuniversalembeddingsmultimodal; jiang2025vlm2vectrainingvisionlanguagemodels). It however falls short of top model performance on ViDoRe which are built on larger decoder VLMs pretrained and aligned on billions of tokens of text and image data.

Most sub-1B parameter models evaluated on document retrieval benchmarks are dual encoder models, since early fusion generative models that perform well are not common at this scale. The most related model is a 176M late interaction model, ColFlor (masrycolflor), trained from the Florence2 model (xiao2023florence2advancingunifiedrepresentation). ColFlor is 12.7 nDCG@5 points under _ColModernVBERT_. _ColModernVBERT_ also largely outperforms off-the-shelf dual encoders, even when those have substantially larger parameter counts. These results highlights the benefits of multi-phase training and early fusion architectures for multi-modal document related tasks, even at smaller parameter counts. We also attribute the strong performance of _ColModernVBERT_ at smaller model sizes to the symbiosis of native bidirectional attention and Late Interaction matching, which largely boosts performance relative to comparable decoder models (Section[3.1](https://arxiv.org/html/2510.01149v3#S3.SS1 "3.1 Modality Alignment Design ‣ 3 What Makes a Great Visual Retriever? ‣ ModernVBERT: Towards Smaller Visual Document Retrievers")).

Speed. As noted by xiao2025metaembedscalingmultimodalretrieval, multi-vector visual retrievers are not bottlenecked in their inference speed by the late interaction matching operation, but rather by the latency required to encode queries with the text model. Our model demonstrates that strong performance is not incompatible with speed, even when running inference on consumer CPUs, which is the standard setting in most industrial local deployments of text embedding models. Latencies are computed by averaging query encoding times of all NanoBEIR queries, which are 23.4 word and 147.5 character long on average, and are run with batch size 1 to replicate online use cases. To prevent RAM bottlenecks, we benchmark on very high RAM (2TB) CPU cloud environments, but note models larger than 3B parameter require more than 12 GB RAM to run optimally.7 7 7 With more standard CPU RAM settings such as those found in low-end servers or Google Colab (12GB RAM), models above 3B parameters must rely on memory offloading to run, which adds up to dozens of seconds of latency per query. ([Table 3](https://arxiv.org/html/2510.01149v3#S4.T3 "Table 3 ‣ 4.2 Results. ‣ 4 Building a Small yet Mighty Visual Retriever. ‣ ModernVBERT: Towards Smaller Visual Document Retrievers")). _ModernVBERT_ achieves more than a 7x speedup on CPU over models with similar performances on ViDoRe. We further report model latency results on GPU hardware in Appendix[C.6.2](https://arxiv.org/html/2510.01149v3#A3.SS6.SSS2 "C.6.2 Online Query Encoding Latency ‣ C.6 Model Latency ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"). We notably demonstrate that with batched inference, _ModernVBERT_ based query encoders are able to encode 5000 queries per second on Nvidia H100 GPUs. ModernVBert’s small model size also enables efficient batching when encoding documents.

5 Related Work
--------------

Repurposing VLMs for Representation Learning. Motivated by the zero-shot performances of generative VLMs(alayrac2022flamingovisuallanguagemodel; lucas_beyer_paligemma_2024; bai_qwen-vl_2023), recent studies have explored repurposing these for multimodal embedding tasks(ma2024unifyingmultimodalretrievaldocument; faysse2025colpaliefficientdocumentretrieval; jiang2025vlm2vectrainingvisionlanguagemodels; zhang2025gmeimprovinguniversalmultimodal). As backbone generative models improved, retriever performance improved as well showcasing the central impact of language model pretraining and modality alignment (xu2025llamanemoretrievercolembedtopperforming; nussbaum2025nomicembedtrainingreproducible). These model remain inherently constrained by their causal attention mechanisms which has been shown in text settings to limits represational efficiency (gisserotboukhlef2025pretrainencodersmaskedlanguage; weller2025seqvsseqopen). Recent work attempts to address this issue by modifying VLM attention during continual pretraining (chen2025mocamodalityawarecontinualpretraining) or contrastive tuning (jiang2025vlm2vectrainingvisionlanguagemodels; xu2025llamanemoretrievercolembedtopperforming), but no recent work attempts to align natively bidirectional language encoder models with vision encoders. The recent release of long sequence text encoders (modernbert; boizard2025eurobertscalingmultilingualencoders) makes this possible.

Late Interaction in Visual Document Retrieval To further boost performance, visual document retrievers leverage the late interaction mechanism(khattab_colbert_2020) which matches multiple query embeddings with multiple document embeddings through the MaxSim operation (faysse2025colpaliefficientdocumentretrieval; günther2025jinaembeddingsv4universalembeddingsmultimodal; xu2025llamanemoretrievercolembedtopperforming). This enables more granular interactions between image and query tokens, at the cost of additional storage and a slight compute overhead during the matching operation. Efficiency gains have come from improving the storage costs through quantization (vespaScalingColPali), token pruning (faysse_croissantllm_2024) and more recently the use of Matrioshka losses to compact multi-token representations (xiao2025metaembedscalingmultimodalretrieval). Ultimately, the performance bottleneck when running visual retrieval inference with such models now resides mostly in the necessity to rely on costly GPU hardware to encode queries, which sets apart text from vision retrieval. This paper fills this gap by using encoders that run on CPU, of parameter sizes comparable to commonly used local text embedding models (chen_bge_2024; enevoldsen2025mmtebmassivemultilingualtext).

6 Conclusion
------------

In this paper we question design decisions of current VLM-based retriever models, providing crucial insights into what matters when training early-fusion vision encoders. Our study notably shows that these models generally do not improve retrieval on natural-image tasks compared to dual encoders, yet strong vision-language alignment is essential for document-centric retrieval. We uncover a tight synergy between bidirectional attention and late-interaction retrieval, which underscores a fundamental limitation of repurposing decoder-style generative VLMs for retrieval. To mitigate data scarcity in contrastive learning, we propose augmenting limited image-document/text-query pairs with larger, lower-cost corpora from other modalities. Guided by these insights, we trained _ColModernVBERT_, a compact yet powerful 250 250 M-parameter multimodal encoder that matches the performance of models up to 10×10\times larger on visual retrieval benchmarks. We release models and training code to help practitioners reduce cost and latency when deploying visual retrievers in real-world applications, and to encourage research on efficient multimodal embedding models.

Future Work & Limitations. By design, our analysis targets relatively small models. An important next step is to test whether the observed patterns persist at larger scales—for example, to more rigorously probe the interplay between late interaction and bidirectional attention. Our study also focuses exclusively on English. While we expect the broad trends to generalize and see clear value in releasing multilingual variants, it remains unclear how allocating parameters to additional languages trades off against the understanding of the vision modality, and to what extent this penalizes English retrieval performance as the number of languages are scaled (pmlr-v202-fernandes23a). Finally, although we center on retrieval and sequence-level zero-shot classification, the modality-aligned encoder can be fine-tuned for a range of token-level tasks, including OCR error detection, token-level classification, visual named entity recognition, visually grounded token-level object detection, contextual embeddings (conti2025context). We release our base model to encourage exploration of these directions.

Ethics Statement
----------------

Environmental Costs. Training _ColModernVBERT_ required approximately 2,000 H100 GPU-hours in total, which we estimate corresponds to 41 kg of CO 2 8 8 8 Carbon footprint estimated with Green Algorithms(Lannelongue2021GreenAlgorithms): E=t×P×PUE,CO 2​e=E×CI E=t\times P\times\mathrm{PUE},\;\mathrm{CO_{2}e}=E\times\mathrm{CI}. With t=2000 t=2000 GPUh, P=0.35 P=0.35 kW (H100 PCIe), PUE=1.3\mathrm{PUE}=1.3, and CI=45\mathrm{CI}=45 gCO 2/kWh, this gives E≈910 E\approx 910 kWh and CO 2​e≈41\mathrm{CO_{2}e}\approx 41 kg., based on standard assumptions of GPU power draw, datacenter efficiency, and grid carbon intensity. This estimate follows methodologies such as Green Algorithms (Lannelongue2021GreenAlgorithms) and related analyses of the carbon footprint of machine learning (Strubell2019Energy; Patterson2021Carbon). Across the entire project, all combined experiments totaled about 18k H100-hours. To mitigate costs and promote sustainable research practices, we release all model checkpoints and training artifacts to facilitate reuse, extension, and reproducibility without necessitating retraining. Additionally, this work shows efficiency gains with smaller models to aim to limit the inference costs of visual retrieval, and consequently reduce the environmental footprint. Our model performs query encoding efficiently on CPUs, keeping inference costs low and reducing barriers to adoption.

Safety and Bias. From a safety perspective, our encoder-only retriever poses less risk than generative models: it produces fixed-length embeddings rather than free-form content, reducing avenues for harmful content generation, hallucination, or deceptive outputs; nonetheless, retrieval systems can still propagate biases present in the underlying data, which we address through dataset curation open release.

AI Assistance. Parts of this paper were prepared with the assistance of an AI-based writing tool used for copy editing and stylistic refinement. All generated text was carefully reviewed, verified, and revised by the authors, who take full responsibility for the accuracy and originality of the final manuscript.

Reproducibility Statement
-------------------------

For transparency and to foster future work, we release our training data, model checkpoints (base models and adapters), and the complete codebase under the MIT License, as detailed in the main paper and repository. The supplementary material specifies training configurations for all models (also provided in the corresponding HuggingFace repositories), describes our synthetic data generation process, and reports expanded evaluation results to support exact replication.

Detailed Contributions
----------------------

PT is the first author of the project. Notably, he designed the modality alignement codebase, ran and supervised most large scale experiments across modality alignment and contrastive training, coordinated work, and was key in paper writing. QM ran large scale ablations on the data mixtures, contrastive training, and was responsible for the final training run. MC ran multiple experiments, including investigations into model merging and contributed to paper writing. AL focused on optimizing the data mixture and the contrastive training codebase. He was notably responsible for the initial cross-modality positive transfer results. GV and PC are senior contributors who helped with project framing, grant obtention, industry expertise and paper review. MF is last author and scientific lead of this work. He initiated and closely supervised the project from beginning to end, wrote the initial version of the multimodal contrastive training framework and greatly contributed to paper writing.

Acknowledgments
---------------

This work was carried out within the framework of the LIAGORA ”LabCom”, a joint laboratory supported by the French National Research Agency (ANR) and established between ILLUIN Technology and the MICS laboratory of CentraleSupélec. This work was performed using HPC resources from IDRIS with grant AD011016393. We warmly thank Hippolyte Gisserot-Boukhlef and Nicolas Boizard for sharing the controlled experiments LM checkpoints, Antoine Chaffin for his feedback on the modality alignment codebase and insights on Ettin’s modeling, as well as Andi Marafioti, Orr Zohar, and Miquel Farré for their valuable input and help on gathering the modality alignment dataset.

Appendix A Training
-------------------

### A.1 Implementation and Resources

Model Batch Size Learning Rate Training Steps Training GPU Hours
Modality Alignment
_ModernVBERT_-base (Table[5](https://arxiv.org/html/2510.01149v3#A1.T5 "Table 5 ‣ A.3.1 Modality Alignment Mixture ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"))4096 1e-4 5500 1920h
Contrastive Learning
Generalist contrastive training (Table[7](https://arxiv.org/html/2510.01149v3#A1.T7 "Table 7 ‣ A.3.3 Contrastive Training Mix ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"))256 2e-4 3917 80h
Document Specialization
Document-focused contrastive training w/ hard negatives (Table[7](https://arxiv.org/html/2510.01149v3#A1.T7 "Table 7 ‣ A.3.3 Contrastive Training Mix ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"))64 2e-4 19602 160h

Table 4: Training details of our final models at each training stage. GPU Hours are on 80GB H100 GPUs.

We list hyperparameters and resource details in [Table 4](https://arxiv.org/html/2510.01149v3#A1.T4 "Table 4 ‣ A.1 Implementation and Resources ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") for the various training stages of our final models. We employ ZeRO stage 1 optimizer(rajbhandari2020zeromemoryoptimizationstraining) for our modality alignment runs. All ablation models are contrastively trained with gradient checkpointing(chen2016trainingdeepnetssublinear) to reduce memory usage. All training runs are performed with FlashAttention 2.0(dao2023flashattention2fasterattentionbetter). For LoRA configurations, we consistently use a rank r of 32 32, lora_alpha of 32 32, and a dropout of 0.1 0.1. For the implementation, we start from m4 9 9 9 SmolVLM trainer, [https://github.com/huggingface/smollm](https://github.com/huggingface/smollm) and ColPali 10 10 10[https://github.com/illuin-tech/colpali](https://github.com/illuin-tech/colpali) codebases for training, and use the MTEB 11 11 11[https://github.com/embeddings-benchmark/mteb](https://github.com/embeddings-benchmark/mteb) repository for evaluation.12 12 12[https://github.com/illuin-tech/modernvbert](https://github.com/illuin-tech/modernvbert)

### A.2 Similarity Functions

Single-Vector Similarity. For single-vector models, we apply mean pooling for MLM-aligned encoders and end-of-sequence (EOS) pooling for CLM-based models and compute the cosine similarity of a query q q and a document d d as

Φ CosSim​(𝐪,𝐝)=exp⁡(cos⁡(𝐄 q,𝐄 d)/τ)\Phi_{\mathrm{CosSim}}(\mathbf{q},\mathbf{d})=\exp(\cos(\mathbf{E}_{q},\mathbf{E}_{d})/\tau)(4)

Multi-Vector Similarity. For multi-vector models, we adopt the standard late-interaction scoring function defined as:

Φ LI​(q,d)=∑i∈⟦1,N q⟧max j∈⟦1,N d⟧⁡⟨𝐄 q(i),𝐄 d(j)⟩,\Phi_{\mathrm{LI}}(q,d)=\sum_{i\in\llbracket 1,N_{q}\rrbracket}\max_{j\in\llbracket 1,N_{d}\rrbracket}\left\langle\mathbf{E}_{q}^{(i)},\mathbf{E}_{d}^{(j)}\right\rangle,(5)

where 𝐄 q(i)\mathbf{E}_{q}^{(i)} and 𝐄 d(j)\mathbf{E}_{d}^{(j)} denote token-level embeddings for the query and document, respectively.

### A.3 Data

#### A.3.1 Modality Alignment Mixture

For our modality alignment trainings, we rely on The Cauldron dataset (laurencon_what_2024) and its Docmatix extension (laurençon2024building). [Table 5](https://arxiv.org/html/2510.01149v3#A1.T5 "Table 5 ‣ A.3.1 Modality Alignment Mixture ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") provides further details on the constitution of this dataset.

Dataset Subsection# Images# QA Pairs# Tokens% Mix
Captioning 609,843 609,843 612,768 612,768 62,906,011 62,906,011 3.13 3.13
Real-world VQA 457,360 457,360 2,125,615 2,125,615 23,318,335 23,318,335 1.16 1.16
OCR, Document Understanding 2,499,258 2,499,258 11,415,478 11,415,478 426,806,479 426,806,479 21.21 21.21
Chart/Figure Understanding 539,743 539,743 24,444,120 24,444,120 30,315,784 30,315,784 1.51 1.51
Table Understanding 163,568 163,568 229,077 229,077 21,371,931 21,371,931 1.06 1.06
Reasoning, Logic, Maths 490,870 490,870 2,212,629 2,212,629 32,450,213 32,450,213 1.61 1.61
Screenshot to Code 547,974 547,974 548,296 548,296 336,299,551 336,299,551 16.71 16.71
Text-only Instructions 0 21,482,682 21,482,682 1,079,001,075 1,079,001,075 53.61 53.61
Total 5308616 63070665 2012469379 100.00

Table 5: Aggregated statistics of modality alignment datasets from The Cauldron 2(laurençon2024mattersbuildingvisionlanguagemodels) and Docmatix(laurençon2024building), showing image counts, QA pairs, token counts, and the proportional contribution of each subsection to the overall mixture.

#### A.3.2 NatCap

To enrich our contrastive learning data mixture, we construct NatCap (Natural Captions), a large-scale dataset containing around 333000 contextualized image–caption pairs. This dataset is created by generating synthetic captions, along with cross-class and in-class discriminative tags, from existing image classification datasets (see Table[6](https://arxiv.org/html/2510.01149v3#A1.T6 "Table 6 ‣ A.3.2 NatCap ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers")). For this purpose, we leverage Gemini-flash-2.5 13 13 13[https://ai.google.dev/gemini-api/docs/models?hl=fr#gemini-2.5-flash](https://ai.google.dev/gemini-api/docs/models?hl=fr#gemini-2.5-flash) which produces captions conditioned on both the image content and the accompanying dataset metadata, as illustrated in Figure[6](https://arxiv.org/html/2510.01149v3#A1.F6 "Figure 6 ‣ A.3.2 NatCap ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"). We detail the prompt below.

Dataset Description# Items
Caltech101 General objects.3.000 3.000
Caltech256 General objects.30.000 30.000
Cars Car model classification.8.000 8.000
Country211 Country where the picture is taken.28.000 28.000
DTD Describable textures (texture attributes).4.000 4.000
EuroSat Land use / area zone type.16.000 16.000
FER2013 Facial emotion recognition.28.000 28.000
FGCVAircraft Aircraft model recognition.3.000 3.000
Food101 Food categories.75.000 75.000
OxfordPets Dog/cat species.3.000 3.000
RESISC45 Aerial scene / area zone type.18.000 18.000
SUN397 General scenes.109.000 109.000
VOC2007 General objects.8.000 8.000
TOTAL 333000

Table 6: NatCap Dataset Composition.NatCap spans 13 different sources covering various images types. The total dataset is composed of 333k pairs

![Image 6: Refer to caption](https://arxiv.org/html/2510.01149v3/x5.png)

Figure 6: Example from the NatCap dataset

#### A.3.3 Contrastive Training Mix

In this subsection, we describe the composition of our data mixes used in the contrastive training stages. [Table 7](https://arxiv.org/html/2510.01149v3#A1.T7 "Table 7 ‣ A.3.3 Contrastive Training Mix ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") outlines the datasets included in each mix, including the Document-Focused variant employed for _ColModernVBERT_.

Source Description Pairs Epochs
Generalist Mix
ColPali(faysse2025colpaliefficientdocumentretrieval)Query–Document images for visual retrieval 118k 1
MSCOCO(lin_microsoft_2014)Natural images with human-written captions 118k 1
NatCap(ours, subsampled)Diverse images with synthetic captions 118k 1
RLHN(thakur2025rlhn)Text–text pairs for complex retrieval 680k 1
TOTAL 1030k
Document-Focused Mix
ColPali(faysse2025colpaliefficientdocumentretrieval)Query–Document images for visual retrieval 118k 3
RLHN(thakur2025rlhn)Text–text pairs for complex retrieval 300k 3
TOTAL 1254k

Table 7: Data mixes for contrastive trainings. The Generalist Mix spans over 1M diverse pairs, while the Document-Focused Mix emphasizes document retrieval with extra ColPali epochs.

Appendix B Baselines Details
----------------------------

In this section, we describe the models evaluated in as comparison to our document retriever model.

MoCa-3B(chen2025mocamodalityawarecontinualpretraining). A modality-aware continual pretraining model that transforms a causal vision-language model into a bidirectional multimodal embedding model, using interleaved image-text reconstruction and contrastive alignment to support cross-modal retrieval.

GME-Qwen2(zhang2025gmeimprovinguniversalmultimodal). A unified multimodal embedder built on Qwen2-VL(wang2024qwen2vlenhancingvisionlanguagemodels), which produces shared embedding representations across text, image, and fused input modalities, enabling universal multimodal retrieval.

VLM2Vec(jiang2025vlm2vectrainingvisionlanguagemodels). A method that trains a vision-language encoder by converting a VLM through extensive contrastive post-training. Flagship model is based on the model Phi-3.5(abdin_phi-3_2024).

E5-V(jiang2024e5vuniversalembeddingsmultimodal). An adaptation of the E5 embedding approach to multimodal models: it trains only on text pairs yet bridges the modality gap to handle image inputs, reducing cost while achieving universal embeddings.

ColPali(faysse2025colpaliefficientdocumentretrieval). A vision-based document retrieval model that processes document pages as images (no OCR) and produces multi-vector embeddings via a late-interaction mechanism over PaliGemma(beyer2024paligemmaversatile3bvlm), enabling efficient and accurate retrieval.

ColQwen2.5(faysse2025colpaliefficientdocumentretrieval). An extension of ColPali(faysse2025colpaliefficientdocumentretrieval) using Qwen2-VL(wang2024qwen2vlenhancingvisionlanguagemodels) as the backbone, carrying forward the late interaction retrieval paradigm over page image embeddings, capturing layout and textual context without OCR.

Jina-v4(günther2025jinaembeddingsv4universalembeddingsmultimodal). A multimodal embedding model combining visual and textual inputs with support for multi-vector (late interaction) embeddings, using adapters over a unified backbone to excel on visually rich document retrieval.

NemoRetriever(xu2025llamanemoretrievercolembedtopperforming). An LI retriever that combines vision-language embeddings with a ColEmbed design, enabling high performance on visual document retrieval with structured patch matching and efficient similarity.

Jina CLIP(koukounas_jina_2024). A smaller scale vision-language model using CLIP embeddings, applied to document retrieval tasks; although not LI, it offers a lightweight multimodal baseline.

BGE Visualized M3(zhou2024vistavisualizedtextembedding). A vision-enhanced version of BGE M3(chen_bge_2024) that supports visual inputs and extends embedding models into multimodal domains.

SigLIP2-L-512/16(tschannen2025siglip2multilingualvisionlanguage). A multilingual vision-language bi-encoder model, which combines image and text modalities to yield unified embeddings across languages. This configuration handles images of 512x512 pixels and create subpatches of 16x16 pixels.

ColFlor(masrycolflor). A lightweight OCR-free visual document retriever with only 174M parameters built over Florence-2 and DaViT, delivering strong performance near ColPali with much lower computational cost and much faster encoding.

Appendix C Additional Ablations
-------------------------------

### C.1 Performance Against Off-the-Shelf Dual Encoder

We study whether using off-the-shelf performances of the standalone vision tower are not outweighing the burden of adding language parameters and re-training through language modeling, as proposed in our work. Figure[7](https://arxiv.org/html/2510.01149v3#A3.F7 "Figure 7 ‣ C.1 Performance Against Off-the-Shelf Dual Encoder ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") shows the results of the various models on the tasks described in Section[2](https://arxiv.org/html/2510.01149v3#S2 "2 Methodology ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"). Similarly to Section[3.1](https://arxiv.org/html/2510.01149v3#S3.SS1 "3.1 Modality Alignment Design ‣ 3 What Makes a Great Visual Retriever? ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"), we observe that the early fusion model trained with LM objective significantly outperform the standalone vision tower on document retrieval tasks (+10.9 nDCG@5). It even surpass the larger dual encoder (+4.8 nDCG@5) on these latest tasks. We note that the standalone vision tower largely outperform the early fusion models on the other natural images tasks, supporting for the use of the SigLIP model for these tasks as found in various general benchmarks(xiao2025miebmassiveimageembedding).

![Image 7: Refer to caption](https://arxiv.org/html/2510.01149v3/x6.png)

Figure 7: Impact of Modality Alignment objective on downstream tasks. Early Fusion of vision and text models boosts document retrieval tasks regardless of the LM objective, but degrades natural image and classification tasks w.r.t. the standalone off-the-shelf vision model SigLIP. Reported scores are aggregated MIEB scores (nDCG, Accuracy.)

### C.2 Scaling Dynamics of Attention Masks

We study the different training dynamics of the different training objectives. We compare the enc (MLM) approach with a traditional dec (CLM) objective. Figure[8](https://arxiv.org/html/2510.01149v3#A3.F8 "Figure 8 ‣ C.2 Scaling Dynamics of Attention Masks ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") presents the performance of the two training objectives across a diverse set of tasks. While starting dec offers an advantage in low-data regimes, enc seems to catches up. In document retrieval tasks, it eventually surpasses dec and scales better.

![Image 8: Refer to caption](https://arxiv.org/html/2510.01149v3/x7.png)

Figure 8: Attention masks impact on modality alignment phase scaling. The dashed line marks the vision tower baseline. The orange curve shows the model initialized from a decoder LM with a CLM objective, and the blue curve shows the model trained with an MLM objective from an encoder LM. CLM performs better in low-data regimes, but MLM scales more effectively, surpassing CLM in document retrieval, while captioning and classification remain below the CLIP baseline.

### C.3 Bridging the Gap with Longer Contrastive Training

We study the impact of additional in-distribution training pairs on embedding tasks by scaling the contrastive training stage. Starting from the final checkpoint of our encoder-based ablation model, we double the contrastive dataset size at each step and train until convergence 14 14 14 To avoid overfitting, we set an early stopping on an eval set. We limit the number of step to one epoch on the full dataset.. This setup tests whether scaling continues to improve performance. Figure[9](https://arxiv.org/html/2510.01149v3#A3.F9 "Figure 9 ‣ C.3 Bridging the Gap with Longer Contrastive Training ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") shows the scaling behavior. Performance improves overall with more in-distribution data. The vision-tower baseline is quickly surpassed on visual document benchmarks, and scaling narrows the gap on other tasks 15 15 15 Note that the models probably won’t fully recover baseline vision-tower performance. This highlights the need to choose models according to use case (e.g., lightweight CLIP-like models for image classification).. We note a plateau in captioning and classification, pointing to the need for more diverse data.

![Image 9: Refer to caption](https://arxiv.org/html/2510.01149v3/x8.png)

Figure 9: Contrastive training scaling. Each dot on the blue curve represents one fraction of the baseline contrastive training mix (ColPali + MSCOCO). Performance improves with more in-distribution data, surpassing the baseline on document benchmarks and narrowing the gap on image captioning. There is no clear improvement in image classification, highlighting the need for more diverse pairs.

#### C.3.1 Optimal Text-To-Image Ratio for Document Retrieval

Our findings in subsection[2](https://arxiv.org/html/2510.01149v3#S3.T2 "Table 2 ‣ 3.2 Contrastive Training Design ‣ 3 What Makes a Great Visual Retriever? ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") indicate that incorporating additional text-only pairs boosts document retrieval performance. While our initial experiment employed a 1:1 text-to-image ratio, we further investigate how varying this ratio impacts our broad set of tasks. We start from the best contrastive mix in Table[2](https://arxiv.org/html/2510.01149v3#S3.T2 "Table 2 ‣ 3.2 Contrastive Training Design ‣ 3 What Makes a Great Visual Retriever? ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"), and vary the text-to-image ratio. As shown in Figure[10](https://arxiv.org/html/2510.01149v3#A3.F10 "Figure 10 ‣ C.3.1 Optimal Text-To-Image Ratio for Document Retrieval ‣ C.3 Bridging the Gap with Longer Contrastive Training ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"), increasing the number of text-only pairs for a fixed amount of image pairs consistently enhances retrieval performance. However, for natural image classification tasks, adding more text does not appear to provide benefits.

![Image 10: Refer to caption](https://arxiv.org/html/2510.01149v3/x9.png)

Figure 10: Optimal text-to-image ratio in contrastive training mix. Increasing the ratio in retrieval tasks consistently improves the performances. 

### C.4 Late Interaction for Non-Documental Retrieval

Document Retrieval Image/Caption Retrieval
Model Size ViDoRe(v1)ViDoRe(v2)MSCOCO (T→\rightarrow I)Flickr30k (T→\rightarrow I)Average
CLIP Encoders
siglip2-base-patch16-512 376M 36.6 23.4 66.2 86.9 53.3
siglip2-large-patch16-512 882M 43.8 27.0 67.1 88.9 56.7
clip-vit-base-patch16 151M 25.5 20.4 50.3 76.8 43.3
clip-vit-large-patch14 428M 38.0 28.6 52.7 79.3 49.6
VLM-based Encoders
VLM2Vec-Full 4150M 49.8 36.5 59.5 81.8 56.9
e5-v 8360M 62.7 49.4 68.1 89.8 67.5
Early Fusion Encoders
bge-visualized-base 196M 10.3 9.0 50.0 74.1 35.9
bge-visualized-m3 873M 12.4 10.2 39.6 69.0 32.8
_ModernVBERT_-embed 252M 58.4 36.9 56.5 76.0 56.9
_ModernVBERT_-embed (multi-vector)252M 76.5 53.9 61.8 81.4 68.4

Table 8: Generalist retrieval performances. Late interaction benefits extend to non-documental retrieval tasks. Our multi-vector model increases its single-vector counterpart across all tasks, surpassing larger VLM-based retrievers. 

We want to study if the multi-vector gains transfer to non-documental retrieval. To do so, we contrastively post-train our base model on our generalist post-training mix presented in Table[7](https://arxiv.org/html/2510.01149v3#A1.T7 "Table 7 ‣ A.3.3 Contrastive Training Mix ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"). The late interaction generalist exhibits superior performance in retrieval setting, improving its single-vector performance by +20.2% (11.5 points), matching the performance of substantially larger VLM-based retrievers like E5-V (8.3B parameters, 67.5 points) and surpassing dual encoders like SigLIP (882M parameters, 56.7 points). This matches the capabilities observed in Section[3.1](https://arxiv.org/html/2510.01149v3#S3.SS1 "3.1 Modality Alignment Design ‣ 3 What Makes a Great Visual Retriever? ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") for documental settings for models with native bidirectional attention, extending it to natural image tasks. This result extends the prevailing understanding from the document retrieval community, where the superiority of late-interaction is well-documented (khattab_colbert_2020, GTE-ModernColBERT, faysse2025colpaliefficientdocumentretrieval). While this performance gap is widely accepted for document retrieval, its applicability to caption matching tasks has not really been addressed. Our findings provide strong evidence that the fine-grained matching capabilities of late-interaction models are a key driver of performance in this domain too.

#### C.4.1 Model Merging

Our contrastive learning stage provides direct performance trade-offs on different tasks. Following recent trends, we evaluate how model merging techniques allow to mitigate performance degradation on specific tasks, while maintaining the performance enabled by the contrastive training (sung2023empiricalstudymultimodalmodelmerging; dziadzio2024mergemultimodalmodelstime; li2024improvinggeneraltextembeddingmerging; zhang2025qwen3embeddingadvancingtext). We merge our ablation model after modality alignment with the checkpoint after the full contrastive learning with two methods: SLERP (ilharco2022patchingopenvocabularymodelsinterpolating) and average merging (slerp_original). For SLERP, we compare three values for the λ\lambda coefficient (0.25 0.25, 0.5 0.5, 0.75 0.75). [Figure 11](https://arxiv.org/html/2510.01149v3#A3.F11 "Figure 11 ‣ C.4.1 Model Merging ‣ C.4 Late Interaction for Non-Documental Retrieval ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") displays the the trends with the best method (SLERP, λ=0.75\lambda=0.75). As we can see, the merged model mitigates the performance drop in Image/Caption Retrieval tasks, while maintaining significant gains on Image Classification tasks. However, merging strongly degrades performance on Document Retrieval, showing that benefits of merging embedding models are task-dependent.

![Image 11: Refer to caption](https://arxiv.org/html/2510.01149v3/x10.png)

Figure 11: Merging model results across tasks. Benefits are task-dependent, with performance degradation w.r.t. both original models in Document Retrieval.

#### C.4.2 Curriculum For Document Retriever Contrastive Post-Training

ViDoRe(v1)ViDoRe(v2)Average
Document retrieval contrastive training starting checkpoint
_ModernVBERT_-base 81.2 56.0 68.6
+ multi-vector generalist CL 80.7 55.4 68.1
+ single-vector generalist CL 80.6 54.0 67.3

Table 9: Performance of _ModernVBERT_ Document Specialisation Curriculums. This table presents the performance of various contrastive training curriculums starting from _ModernVBERT_-base, on the ViDoRe(v1) and ViDoRe(v2) benchmarks. The generalist contrastive learning mix used in the last two models is detailed in Table[7](https://arxiv.org/html/2510.01149v3#A1.T7 "Table 7 ‣ A.3.3 Contrastive Training Mix ‣ A.3 Data ‣ Appendix A Training ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"). We see that a preliminary stage of generalist contrastive learning harms the final document retrieval performance, regardless of whether a multi-vector approach is used.

We conduct an ablation study to determine the optimal contrastive training curriculum for specializing _ModernVBERT_ in document retrieval. Specifically, we investigate whether a preliminary generalist contrastive training phase, intended to leverage a larger dataset, improves downstream performance. As shown in Table [9](https://arxiv.org/html/2510.01149v3#A3.T9 "Table 9 ‣ C.4.2 Curriculum For Document Retriever Contrastive Post-Training ‣ C.4 Late Interaction for Non-Documental Retrieval ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"), our results demonstrate that this initial generalist phase is detrimental to final performance (−0.5%-0.5\%). The optimal strategy is to specialize the model on the target task directly after its initial Masked Language Modeling (MLM) alignment.

### C.5 Text-Only Retrieval

Model Params (M)NDCG@5
Statistical
BM25s—0.559
Single Vector
Jina Embeddings v4 3577*0.623
E5-large-v2 335 0.605
bge-m3 (Bi Encoder)567 0.590
Qwen3-Embedding-0.6B 600 0.567
Multi Vector
LightOn GTE-ModernColBERT v1 149 0.669
Jina ColBERT v2 137 0.642
bge-m3 (Late Interaction)567 0.606
ColBERT v2 110 0.593
Colqwen2-v1.0 1580*0.593
_ColModernVBERT_ 150*0.589
Colqwen2.5-v0.2 3145*0.589

Table 10: Average NDCG@5 of _ColModernVBERT_ on NanoBEIR, a text retrieval benchmark with multiple sub domains. *For multimodal models, we only consider parameters of the text encoder

The results in Table [10](https://arxiv.org/html/2510.01149v3#A3.T10 "Table 10 ‣ C.5 Text-Only Retrieval ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") detail the performance of _ColModernVBERT_ and other baselines on the NanoBEIR text retrieval benchmark. It achieves an average NDCG@5 score competitive with single and multi vector models specialized for text, even without explicit optimization for this modality. This performance is encouraging and indicates a promising direction for training a unified model for both text and image retrieval.

### C.6 Model Latency

#### C.6.1 Image Resolution Tradeoffs

Figure[12](https://arxiv.org/html/2510.01149v3#A3.F12 "Figure 12 ‣ C.6.1 Image Resolution Tradeoffs ‣ C.6 Model Latency ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") presents the pixel shuffling trade-off. Processing larger images creates more visual tokens, leading to very long sequences (around 17′​500 17^{\prime}500 tokens for a 2048x2048 px image with no pixel shuffling). Pixel shuffling allow to compress these sequence by concatenating the embeddings of spatially close patches. This diminishes the number of tokens for longer visual token embeddings. Table[11](https://arxiv.org/html/2510.01149v3#A3.T11 "Table 11 ‣ C.6.1 Image Resolution Tradeoffs ‣ C.6 Model Latency ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers") presents the latency to process one image of various resolutions on one L4 GPU and CPU.

![Image 12: Refer to caption](https://arxiv.org/html/2510.01149v3/x11.png)

Figure 12: Image processing parameters impact on visual tokens. Here we assume a square image for simplicity. Scaling the image size introduces naturally more tokens, but having a large enough pixel shuffling ratio (r≥4 r\geq 4) allows to counterbalance by concatenating spatially close patch representations.

Num. Visual Tokens CPU Latency (ms)GPU Latency (ms)
512 512 px 128 128 287.2(±7.8)287.2_{(\pm 7.8)}43.6(±1.4)43.6_{(\pm 1.4)}
1024 1024 px 320 320 1015.8(±58.1)1015.8_{(\pm 58.1)}150.3(±2.5)150.3_{(\pm 2.5)}
2048 2048 px 1088 1088 2572.0(±63.9)2572.0_{(\pm 63.9)}363.4(±4.6)363.4_{(\pm 4.6)}

Table 11: _ModernVBERT_ image processing latency. Computing the average time to process a single image on GPU and CPU. The average is computed on 100 images. The values represent the mean latency in milliseconds, with the standard deviation included in parenthesis.

#### C.6.2 Online Query Encoding Latency

We evaluate the query embedding speed of our model on GPU. We use a single Nvidia H100 with 80GB of VRAM. As for Section[4.2](https://arxiv.org/html/2510.01149v3#S4.SS2 "4.2 Results. ‣ 4 Building a Small yet Mighty Visual Retriever. ‣ ModernVBERT: Towards Smaller Visual Document Retrievers"), latencies are computed in batch size 1 to simulate online situations, and are averaged over all NanoBEIR queries. Only the text parameters are loaded and run, to minimize memory usage. Parameters are cast to bfloat16 and Flash Attention 2 is used. The resulting speeds are often much faster than those obtained by running inference through each model’s reference implementation. Results are shown in Table[12](https://arxiv.org/html/2510.01149v3#A3.T12 "Table 12 ‣ C.6.2 Online Query Encoding Latency ‣ C.6 Model Latency ‣ Appendix C Additional Ablations ‣ ModernVBERT: Towards Smaller Visual Document Retrievers")). Interestingly in this setup where memory is not a bottleneck, model depth seems to be a large performance driver, sometimes more the parameter count. We finally evaluate batched GPU throughput. We use batches of size 512 by default and iteratively half it when memory is insufficient. We observe that _ModernVBERT_ based models are extremely fast and can process 5000 queries per second. In the table, the reported figures correspond to the inverted throughput (latency per batch divided by the number of queries per batch). These speed and throughput gains are made possible due to a combination of size, and efficient hardware-informed design as well as the support of flash attention and sequence packing other models of the size often lack (warner2024smarterbetterfasterlonger).

Late Interaction Model Size (B)CPU Latency (ms)GPU Latency (ms)GPU Batching (ms)
≥\geq 1B Parameters
MoCa-3B 3.75 158(±147)158_{(\pm 147)}26(±3)26_{(\pm 3)}4.54 4.54
VLM2Vec 4.15 211(±253)211_{(\pm 253)}21(±3)21_{(\pm 3)}2.82 2.82
GME-Qwen2-7B 8.29 412(±411)412_{(\pm 411)}25(±1)25_{(\pm 1)}9.07 9.07
E5-V 8.36 434(±379)434_{(\pm 379)}22(±2)22_{(\pm 2)}9.55 9.55
ColPali✓2.92 175(±113)175_{(\pm 113)}14(±1)14_{(\pm 1)}3.07 3.07
ColQwen2.5✓3.75 158(±147)158_{(\pm 147)}26(±2)26_{(\pm 2)}26 26
Jina-v4✓3.75 158(±147)158_{(\pm 147)}26(±2)26_{(\pm 2)}4.54 4.54
NemoRetriever-3B✓4.40 155(±118)155_{(\pm 118)}20(±2)20_{(\pm 2)}4.59 4.59
≤\leq 1B Parameters
Jina CLIP.22 14(±7)14_{(\pm 7)}6(±2)6_{(\pm 2)}.69.69
BGE Visualized M3.87 38(±42)38_{(\pm 42)}10(±2)10_{(\pm 2)}.77.77
SigLIP2-L-512/16.88 25(±8)25_{(\pm 8)}6(±1)6_{(\pm 1)}.10.10
ColFlor✓.17 17(±9)17_{(\pm 9)}8(±2)8_{(\pm 2)}.31.31
_BiModernVBERT_ (ours).25 20(±11)20_{(\pm 11)}14(±2)14_{(\pm 2)}.20.20
_ColModernVBERT_ (ours)✓.25 20(±11)20_{(\pm 11)}14(±2)14_{(\pm 2)}.20.20

Table 12: Text query encoding latency. The latency is computed both on high-end CPUs (1TB RAM, 128 cores) and GPU (Nvidia H100, 80GB) (mean ± std). Since only 649 queries are used, standard deviations are not reported in GPU batching mode (batches of 512 queries by default), for which we report the inverse throughput (average latency per batch divided by the batch size).


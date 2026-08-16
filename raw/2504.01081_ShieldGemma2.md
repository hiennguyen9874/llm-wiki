Title: ShieldGemma 2: Robust and Tractable Image Content Moderation

URL Source: https://arxiv.org/html/2504.01081

Published Time: Thu, 10 Apr 2025 00:04:30 GMT

Markdown Content:
###### Abstract

We introduce ShieldGemma 2, a 4B parameter image content moderation model built on Gemma 3. This model provides robust safety risk predictions across the following key harm categories: Sexually Explicit, Violence & Gore, and Dangerous Content for synthetic images (e.g. output of any image generation model) and natural images (e.g. any image input to a Vision-Language Model). We evaluated on both internal and external benchmarks to demonstrate state-of-the-art performance compared to LlavaGuard (Helff et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib15)), GPT-4o mini (Hurst et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib16)), and the base Gemma 3 model (Gemma Team, [2025](https://arxiv.org/html/2504.01081v2#bib.bib11)) based on our policies. Additionally, we present a novel adversarial data generation pipeline which enables a controlled, diverse, and robust image generation. ShieldGemma 2 provides an open image moderation tool to advance multimodal safety and responsible AI development.

![Image 1: [Uncaptioned image]](https://arxiv.org/html/2504.01081v2/x1.png)

[https://huggingface.co/google/shieldgemma-2-4b-it](https://huggingface.co/google/shieldgemma-2-4b-it)

![Image 2: [Uncaptioned image]](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/kaggle.png)

[https://www.kaggle.com/models/google/shieldgemma-2](https://www.kaggle.com/models/google/shieldgemma-2)

![Image 3: [Uncaptioned image]](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/google.png)

[http://ai.google.dev/gemma/docs/shieldgemma/model_card_2](http://ai.google.dev/gemma/docs/shieldgemma/model_card_2)

1 Introduction
--------------

Vision-Language Models (VLMs) have experienced rapid advancements, demonstrating impressive capabilities in understanding and generating visual content (Gemini Team et al., [2023](https://arxiv.org/html/2504.01081v2#bib.bib10); Achiam et al., [2023](https://arxiv.org/html/2504.01081v2#bib.bib2); Li et al., [2023](https://arxiv.org/html/2504.01081v2#bib.bib18); Dubey et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib9)). These models offer a wide range of functionalities, including image caption generation, visual question answering (VQA), Visual Dialogue, Image Editing, image generation, etc. Examples of such advancements include: (i) Conversation models like Gemini Gemini Team et al. ([2023](https://arxiv.org/html/2504.01081v2#bib.bib10)) and GPT-4o (Achiam et al., [2023](https://arxiv.org/html/2504.01081v2#bib.bib2)) exhibit strong long-context understanding across image and text modalities, allowing them to analyze complex visual scenes and answer nuanced questions that require reasoning over extended visual and textual information. (ii) Image generation models like Stable Diffusion (Rombach et al., [2022](https://arxiv.org/html/2504.01081v2#bib.bib26)), Imagen (Saharia et al., [2022](https://arxiv.org/html/2504.01081v2#bib.bib27)), MidJourney, DALL-E(Ramesh et al., [2021](https://arxiv.org/html/2504.01081v2#bib.bib25)), etc have democratized the creation of highly realistic and diverse visual content from textual prompts. Their increasing accessibility and ease of use empower a wide range of users to generate imagery with unprecedented fidelity and creative control.

The increasing prevalence and capabilities of VLMs increases the criticality of robust safety mechanisms for VLMs across both input and output. For VLMs that accept image inputs, whether synthetic or natural images, it is crucial to build safeguards that prevent harmful content from surfacing. For image generation models, it is crucial to verify compliance with safety policies, preventing the generation of harmful or inappropriate content. This dual challenge underscores the urgent need for highly effective image safety classifiers capable of handling both natural and synthetic images.

The field of image classification has undergone significant transformation with the advent of transformer-based architectures. For example, the Vision Transformer (ViT) (Dosovitskiy et al., [2020](https://arxiv.org/html/2504.01081v2#bib.bib8)) processes an image by dividing it into non-overlapping patches, flattening them into sequences, and feeding them into a standard transformer encoder. The Swin Transformer (Liu et al., [2021](https://arxiv.org/html/2504.01081v2#bib.bib23)) introduces a hierarchical structure and a shifted window mechanism to enhance efficiency and scalability while preserving locality. Extending beyond traditional image classification, VLMs such as Gemini, GPT-4o, and Llava have emerged as powerful tools for more comprehensive image understanding tasks, leveraging their ability to process and reason across both visual and textual modalities. However, their direct applicability to specialized vertical domains like image safety classification faces several limitations such as being non-open-sourced, too large and expensive for vertical applications like safety, and not being specifically designed for safety tasks. To bridge this performance gap, recent research has focused on fine-tuning VLMs specifically for image safety classification. Examples include LlavaGuard (Helff et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib15)) and PerspectiveVision (Qu et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib24)), achieving notable improvements.

Despite these advancements, several key limitations remain: (i) Synthetic Data Generation Bottleneck: Existing models often lack automated and targeted training data generation methods. Ideally, a system should be able to produce synthetic images that specifically probe safety boundaries relevant to a particular policy, topic or application. Current approaches often rely on general-purpose datasets that may not adequately cover the diverse and adversarial scenarios necessary for robust safety classification. (ii) Lack of Threshold Customization: some of the existing safety classifiers only provide binary classifications (safe/unsafe) without offering customizable thresholds. Different applications have varying risk tolerances, and the ability to adjust the classification threshold is crucial for balancing precision and recall.

To address these limitations, we propose ShieldGemma 2 (SG2), a robust image safety classifier fine-tuned on top of the Gemma 3 4B model Gemma Team ([2025](https://arxiv.org/html/2504.01081v2#bib.bib11)). SG2 offers the following key advantages:

*   •Policy-Aware Classification: SG2 accepts both a user-defined safety policy and an image as input, providing classifications for both natural and synthetic images, tailored to the specific policy guidelines. 
*   •Novel Adversarial Synthetic Data Generation: We introduce a novel method for generating synthetic images that are both diverse and adversarial, specifically designed to challenge the classifier based on the needs of the target application. This method ensures more thorough testing and training across a wider range of potential safety violations. 
*   •State-of-the-Art Performance (SoTA) with Flexible Thresholding: Internal and external evaluations demonstrate that SG2 achieves SoTA performance on our policies, outperforming prominent models such as LLavaGuard 7B, GPT-4o mini, and Gemma 3. SG2 outputs a continuous confidence score for each prediction, empowering downstream users to dynamically adjust the classification threshold according to their specific use cases and risk management strategies. 

2 Literature Review
-------------------

Source of Unsafe Images. Unsafe images encountered in community settings can be categorized as synthetic or natural. Natural unsafe images are captured from real-world scenes. These images may be included in foundation model training data or used to mislead/jailbreak models during inference, particularly Multimodal LLMs (Gong et al., [2023](https://arxiv.org/html/2504.01081v2#bib.bib12); Liu et al., [2024c](https://arxiv.org/html/2504.01081v2#bib.bib22); Chen et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib4)). Synthetic unsafe images represent a distinct form of harmful content. Research demonstrates that even state-of-the-art image generation models are susceptible to prompts designed to generate harmful content, even after being trained to prevent such generation (Schramowski et al., [2023](https://arxiv.org/html/2504.01081v2#bib.bib28); Li et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib17); Liu et al., [2024a](https://arxiv.org/html/2504.01081v2#bib.bib20), [b](https://arxiv.org/html/2504.01081v2#bib.bib21); Cheng et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib6)).

Moderation of Unsafe Images. To mitigate the risks posed by unsafe images, various efforts have been undertaken. Recent research focuses on reducing the generation of such images. Specifically, during training, safe text-to-image generation models are developed by curating safe training data. At inference, unsafe text prompts are banned or modified (Liu et al., [2024a](https://arxiv.org/html/2504.01081v2#bib.bib20)). The generation process can also be manipulated to avoid harmful concepts in the synthetic images (Schramowski et al., [2023](https://arxiv.org/html/2504.01081v2#bib.bib28); Li et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib17)). Additionally, synthetic images can be screened for safety before user delivery. Such detectors can be based on traditional image classifiers or multimodal LLMs, including Gemini (Team et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib30)), GPT-4V (gpt, [2023](https://arxiv.org/html/2504.01081v2#bib.bib1)), LLaVA (Liu et al., [2023](https://arxiv.org/html/2504.01081v2#bib.bib19)), and LlavaGuard (Helff et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib15)). To ensure consistent safe/unsafe labels from VLM outputs, a classifier is often added. LlavaGuard Helff et al. ([2024](https://arxiv.org/html/2504.01081v2#bib.bib15)) is an open-source framework with VLM-based vision safeguards, designed to assess the safety of visual content using a customized taxonomy. In this work, we contribute to build a precise and efficient open-source detector based on our Gemma 3 (Gemma Team, [2025](https://arxiv.org/html/2504.01081v2#bib.bib11)) for the unsafe image detection.

Image Synthetic for Training. In the past years, significant progress has been made for image generation, which makes it feasible to generate large-scale high-quality images (Baldridge et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib3); Rombach et al., [2022](https://arxiv.org/html/2504.01081v2#bib.bib26)). Given the progress, our community has also explored such image generation models or propose new ones to generate training data, such as training data for classification, segmentation and detection (Wu et al., [2023a](https://arxiv.org/html/2504.01081v2#bib.bib31); Suri et al., [2023](https://arxiv.org/html/2504.01081v2#bib.bib29); Wu et al., [2023b](https://arxiv.org/html/2504.01081v2#bib.bib32); Zeng et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib34)). In this work, we propose to generate images for building safety classifiers, specifically, we generate high-quality data that follow predefined policies and generated taxonomies.

3 Safety Policy
---------------

We define a detailed content safety taxonomy for SG2, initially focusing on three primary harm categories. A key feature of our approach is the provision for users to input customized safety policies, allowing for fine-grained control and adaptation to specific use-case requirements. Our default policies for SG2 cover:

*   •No Sexually Explicit Information 1 1 1 Henceforth, we will use sexual, danger, and violence to refer to the categories of sexually explicit information, dangerous content, and violence/Gore Content, respectively.. The image shall not contain content that depicts explicit or graphic sexual acts (e.g., pornography, erotic nudity, depictions of rape or sexual assault). 
*   •No Dangerous Content. The image shall not contain content that facilitates or encourages activities that could cause real-world harm (e.g., building firearms and explosive devices, promotion of terrorism, instructions for suicide). 
*   •No Violence/Gore Content. The image shall not contain content that depicts shocking, sensational, or gratuitous violence (e.g., excessive blood and gore, gratuitous violence against animals, extreme injury or moment of death). 

Users of SG2 can decide to employ one or multiple of these policies, or curate their own bespoke policy for their use cases.

![Image 4: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/data_synth_pipeline.png)

Figure 1: Synthetic Image Generation Pipeline.

4 Training Data Curation
------------------------

### 4.1 Synthetic Data Generation

The development of SG2 involved a meticulous process of generating synthetic training dataset. This was crucial for creating a robust and comprehensive dataset to train SG2, with the best balance of diversity and severity of images.

Introduced in Davidson et al. ([2025](https://arxiv.org/html/2504.01081v2#bib.bib7)), our internal data generation pipeline generates controlled prompts and corresponding images. As illustrated in Fig.[1](https://arxiv.org/html/2504.01081v2#S3.F1 "Figure 1 ‣ 3 Safety Policy ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation"), the process includes:

*   •Problem Definition. Encompassing policy definitions, exceptions, input/output formats, and few-shot examples. 
*   •Taxonomy Generation. Our Taxonomy & Synthetic Data Generator produces taxonomy in a one or multi-layer tree structure for each of the dimensions like topics, target demographics (e.g., gender, sexual orientation), the context, regional aspects and image styles (e.g., pixel art, vintage), etc. For example, for the taxonomy of topic, the first layer includes a coarse-grained topics for this harm policy, and the second layer includes additional fine-grained sub-topics. 
*   •Image Query Generation. Our generator creates prompts by combining these leaf nodes across all these tree-structured taxonomies. As an example, a dangerous policy with (Topic=terrorism, sub-topic=arms and ammunition, context=social media, locale=Africa, image style=Pointillism) could generate: Pointillist painting of a man firing an AK-47 into a bustling souk in Marrakech, with market stalls overturned and people scattering in fear. 
*   •Image Generation. We leverage Imagen models (Saharia et al., [2022](https://arxiv.org/html/2504.01081v2#bib.bib27)) to generate around 10⁢k 10 𝑘 10k 10 italic_k images per policy with various aspect ratios and resolutions. The data generation process follows an iterative approach, wherein assessment results informed enhancements, including adjustments to model parameters, refinement of taxonomies, and the incorporation of additional few-shot examples. 

### 4.2 Real Image Selection

To enhance SG2’s performance on real-world images, we leveraged the extensive WebLI (Web Language and Image) dataset (Chen et al., [2022](https://arxiv.org/html/2504.01081v2#bib.bib5)), a large-scale collection containing approximately 10 billion images and captions:

*   •Randomly sampled a substantial subset of images from the WebLI dataset. 
*   •Utilized a high-performing text safety classifier to analyze the captions associated with each sampled image. 
*   •Retained images where at least one of these categories had a violation probability exceeding 0.1. 
*   •From the filtered set of images identified as potentially violating our safety policies, we randomly selected a final training set of 120⁢k 120 𝑘 120k 120 italic_k images. 

### 4.3 Borderline Adversarial Data Generation (BADG)

Our training labels are generated using in-context learning with the Gemini model (detailed in the section [Label Generation](https://arxiv.org/html/2504.01081v2#S5.SS1 "In 5 Methodology ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation")). To bridge the performance gap between Gemini’s in-context learning capabilities and SG2, we generated image prompts which intentionally cause ShieldGemma 1 (Zeng et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib34)) to produce misclassifications (both false positives and false negatives) when compared against a much larger auto-rater (i.e. LLM-as-a-judge (Gu, [2024](https://arxiv.org/html/2504.01081v2#bib.bib14))) based on Gemini. By creating a diverse dataset of adversarial images based on these prompts, we specifically designed it to enhance SG2’s classification ability for borderline cases.

5 Methodology
-------------

You are a policy expert trying to help determine whether a generated or real image is in violation of the safety policy below. Your decision must very clearly follow the specific language used in the safety policy and should not include any interpretation outside of the safety policy. 

<BEGIN_SAFETY_POLICY>

"No Sexually Explicit Information": The image shall not contain content that depicts explicit or graphic sexual acts (e.g., pornography, erotic nudity, depictions of rape or sexual assault). 

</END_SAFETY_POLICY>

Does the image violate the above policy? Your Answer must start with ’Yes’ or ’No’.

Figure 2: Instructions for Supervised Fine-Tuning. The input to SG2 consists of the image followed by the prompt instruction here.

### 5.1 Label Generation

We automated training label generation using Gemini 2 Flash (Google, [2024](https://arxiv.org/html/2504.01081v2#bib.bib13)) with in-context learning. This process involved constructing carefully designed prompts that included detailed Safety Policies and few-shot examples. To enhance reasoning, Tree-of-Thoughts (ToT) (Yao et al., [2023](https://arxiv.org/html/2504.01081v2#bib.bib33)) was implemented, decomposing the labeling task into sub-problems via decision tree traversal, guided by few-shot examples. By requiring only a small set of few-shot examples, we eliminated the need for extensive human annotation, facilitating rapid policy adaptation, efficient new policy initialization, and significant annotation cost savings.

### 5.2 Supervised Fine-Tuning

During supervised fine-tuning, we employed a dual-objective training strategy to enhance both classification accuracy and safety reasoning capabilities. The training data was split into two equal portions: (i) Binary Classification: For a randomly selected 50% of the training data to return a binary Yes or No output, indicating whether the image violated any of the specified safety policies. The prompt instruction is described in Fig. [2](https://arxiv.org/html/2504.01081v2#S5.F2 "Figure 2 ‣ 5 Methodology ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation"). (ii) Rationale-Enhanced Classification: For the remaining 50% of the training data, we aimed to improve the model’s safety reasoning capability. We used a separate LLM to generate simplified rationales from the detailed ToT-based rationales. Then the model was prompted to output JSON objects containing safety labels (Yes or No) and the simplified rationale.

We supervise fine-tune (SFT) Gemma 3 4B Instruction-Tuned (IT) models (Gemma Team, [2025](https://arxiv.org/html/2504.01081v2#bib.bib11)). Our models are trained on TPUv5 lite with batch size of 64, a max sequence of 8⁢k 8 𝑘 8k 8 italic_k and the model is trained for 4⁢k 4 𝑘 4k 4 italic_k steps.

### 5.3 Inference

The same as ShieldGemma 1 (Zeng et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib34)), we calculate our predicted probability based on Eq. [1](https://arxiv.org/html/2504.01081v2#S5.E1 "Equation 1 ‣ 5.3 Inference ‣ 5 Methodology ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation") below:

exp⁡(𝐿𝐿⁢(𝑌𝑒𝑠)/T)+α exp⁡(𝐿𝐿⁢(𝑌𝑒𝑠)/T)+exp⁡(𝐿𝐿⁢(𝑁𝑜)/T)+2⁢α 𝐿𝐿 𝑌𝑒𝑠 𝑇 𝛼 𝐿𝐿 𝑌𝑒𝑠 𝑇 𝐿𝐿 𝑁𝑜 𝑇 2 𝛼\frac{\exp(\mathit{LL(Yes)}/T)+\alpha}{\exp(\mathit{LL(Yes)}/T)+\exp(\mathit{% LL(No)}/T)+2\alpha}divide start_ARG roman_exp ( italic_LL ( italic_Yes ) / italic_T ) + italic_α end_ARG start_ARG roman_exp ( italic_LL ( italic_Yes ) / italic_T ) + roman_exp ( italic_LL ( italic_No ) / italic_T ) + 2 italic_α end_ARG(1)

Here LL(·) is the log likelihood of the token generated by the model; T and α 𝛼\alpha italic_α are hyperparameters to control temperature and uncertainty estimate.

Despite each request specifying a single unique policy, the majority of the model input (e.g., image, part of the preamble) remains identical. We recommend enabling context caching to minimize the computational overhead of safety predictions for several policies of the same image.

6 Experiments
-------------

Policy SG2 LlavaGuard(Our Policy)LlavaGuard(Original Policy)GPT-4o mini Gemma 3 SG2 (w/o BADG)
Sexual 87.6/89.7/88.6 67.2/98.9/80.0 47.6/93.1/63.0 68.3/97.7/80.3 77.7/87.9/82.5 85.9/91.4/88.6
Danger 95.6/91.9/93.7 82.3/89.6/85.8 67.0/100.0/80.3 84.4/99.0/91.0 75.9/94.5/84.2 91.8/90.9/91.3
Violence 80.3/90.4/85.0 39.8/100.0/57.0 36.8/100.0/53.8 40.2/100.0/57.3 78.2/82.2/80.1 76.1/89.6/82.3

Table 1: Precision/Recall/F1 (%, higher is better) on our internal benchmark. SG2 outperforms all other models across all three policies. GPT-4o mini exhibits a very high recall; however, it suffers significantly from over-triggering, resulting in a much lower precision. Without BADG, SG2 experiences a 2.6%/2.7% drop in F1 score for danger and violence, respectively.

Policy metrics SG2 LlavaGuard(Our Policy)LlavaGuard(Original Policy)GPT-4o mini Gemma 3
Sexual F1 64.2 42.1 37.8 57.1 50.4
Danger 1 - FPR 88.7 68.6 27.3 92.3 93.8
Violence 1 - FPR 95.9 40.1 13.0 62.5 57.3

Table 2: UnsafeBench external benchmark performance (%, higher is better) after relabeling with our policies. F1 score is used for sexual evaluation, while 1-FPR (false positive rate) is used for evaluating violence and danger.

### 6.1 Setup

Despite the abundance of safety-related benchmark datasets, direct comparison remains challenging due to several factors: (i) variations in policy definitions and supported harm types across datasets; (ii) inconsistencies in policy definitions even within the same harm type. To overcome these challenges, we mainly focuses on evaluation based on our policies. Baseline model results are reported for both our policies and the original policies, when applicable. For external benchmarks, images are re-annotated using our policies.

### 6.2 Benchmark Datasets and Baseline Models

UnsafeBench Dataset. (Qu et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib24)) is a dataset that comprises roughly 10⁢k 10 𝑘 10k 10 italic_k images (2⁢k 2 𝑘 2k 2 italic_k in the test set), and is annotated for 11 different types of unsafe content, namely: hate, harassment, violence, self-harm, sexual, shocking, illegal activity, deception, political, public and personal health, and spam. Here we only keep the test examples that are closely aligned with our policies. We re-annotate the examples of sexual, violence, self-harm based on our internal policies of sexual, violence, danger respectively. Relabeling resulted in a significant reduction of positive examples. Figures [3](https://arxiv.org/html/2504.01081v2#A1.F3 "Figure 3 ‣ A.1 Label Comparisons ‣ Appendix A Appendix ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation"), [4](https://arxiv.org/html/2504.01081v2#A1.F4 "Figure 4 ‣ A.1 Label Comparisons ‣ Appendix A Appendix ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation"), and [5](https://arxiv.org/html/2504.01081v2#A1.F5 "Figure 5 ‣ A.1 Label Comparisons ‣ Appendix A Appendix ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation") in the Appendix provide examples of instances that were originally labeled as positive but re-annotated as negative. In total, it has 603 examples including both synthetic and natural images.

Internal Benchmark Dataset. is synthetically generated through our internal image data curation pipeline. This pipeline includes key steps such as problem definition, safety taxonomy generation, image query generation, image generation, attribute analysis, label quality validation, and more. We have approximately 500 examples for each harm policy. The positive ratios are 39%, 67%, 32% for sexual, danger, violence respectively.

Our model is evaluated against the following baselines: LlavaGuard 7B (Helff et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib15)), GPT-4o mini (Hurst et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib16)), and out-of-the-box Gemma-3-4B-IT (Gemma Team, [2025](https://arxiv.org/html/2504.01081v2#bib.bib11)). For GPT-4o mini, we utilize the OpenAI API (model=gpt-4o-mini). For LlavaGuard 7B, we evaluate based on both our policies/template in Fig. [2](https://arxiv.org/html/2504.01081v2#S5.F2 "Figure 2 ‣ 5 Methodology ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation") and the original LlavaGuard policies/template in the appendix (subsection [LlavaGuard Prompt Instruction](https://arxiv.org/html/2504.01081v2#A1.SS2 "In Appendix A Appendix ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation")). For GPT-4o mini and Gemma 3, we use our policies/template in Fig. [2](https://arxiv.org/html/2504.01081v2#S5.F2 "Figure 2 ‣ 5 Methodology ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation").

### 6.3 Results

Our internal evaluation results are presented in Table [1](https://arxiv.org/html/2504.01081v2#S6.T1 "Table 1 ‣ 6 Experiments ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation"). SG2 consistently outperforms all other models across all three policies, achieving an average PR-AUC of 89.1%. This represents improvements of 6.8%, 12.9%, and 14.8% over Gemma-3-4B-IT, GPT-4o mini, and LlavaGuard 7B, respectively. For SG2 and Gemma-3-4B-IT, optimal thresholds were applied. Without thresholding, directly predicting ‘Yes’/‘No’ tokens leads to a marginal 0.8% reduction F1 score for SG2.

To evaluate the impact of BADG, we performed an ablation study comparing SG2 with a model trained without the BADG dataset. As shown in Table [1](https://arxiv.org/html/2504.01081v2#S6.T1 "Table 1 ‣ 6 Experiments ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation"), excluding BADG resulted in a 2.6% and 2.7% decrease in F1 score for danger and violence. Notably, precision was significantly enhanced.

Our External Evaluation Results. On UnsafeBench dataset are shown in Table [2](https://arxiv.org/html/2504.01081v2#S6.T2 "Table 2 ‣ 6 Experiments ‣ ShieldGemma 2: Robust and Tractable Image Content Moderation"). Following the relabeling of the UnsafeBench dataset according to our policy, the number of positive instances for danger and violence became significantly reduced. Consequently, performance for these categories is reported using 1-FPR (false positive rate), where FPR represents the percentage of benign examples incorrectly classified as positive. SG2 demonstrates superior performance over all baseline models in sexual and violence. For danger, SG2’s performance is comparable to GPT-4o mini and Gemma 3, but SG2 achieves perfect (100%) recall compared to 80% for the other two models.

7 Limitations
-------------

Despite a robust performance shown in our model, several limitations remains:

Images with Text Overlays. Prior research (Liu et al., [2024c](https://arxiv.org/html/2504.01081v2#bib.bib22)) indicates that integrating multiple modalities within a single image (e.g., visual elements combined with overlaid text) can create nuanced harmfulness. A visually benign image, for instance, might be rendered unsafe by the specific meaning of text embedded within the image itself. It is beyond the scope of our detector for this specific challenge of evaluating unsafe content that emerges pragmatically from the interplay of different modalities co-existing within one image.

Interleaving Conversation. A limitation of our model is its focus on single-image classification. It is not designed for, and therefore beyond the scope of this work, to process interleaved sequences of text and images, such as those found in conversational contexts.

Limited policy coverage. Even though our model can be generalized into customized policies, it’s not specifically fine-tuned for policies other than sexual, danger and violence. We leave that in future work to further increase our harm policy coverage.

8 Conclusion
------------

This paper introduces ShieldGemma 2, a 4B parameter image content moderation model based on the Gemma 3. We demonstrate a superior safety classification performance based on our internal and external benchmark evaluations. A key contribution is a novel adversarial image generation pipeline that produces high-quality, diverse, and adversarial training data. This pipeline offers a valuable resource for developing robust multimodal safety systems. We release these resources to facilitate further research and development in multimodal safety.

9 ShieldGemma Team
------------------

Core Contributors

Wenjun Zeng 

Dana Kurniawan 

Ryan Mullins 

Yuchi Liu 

Tamoghna Saha

Contributors

Dirichi Ike-Njoku 

Jindong Gu 

Yiwen Song 

Cai Xu 

Jingjing Zhou 

Aparna Joshi 

Shravan Dheep 

Mani Malek 

Hamid Palangi 

Joon Baek 

Rick Pereira 

Karthik Narasimhan

Central Support 

Will Hawkins 

Dawn Bloxwich 

Helen King 

William Isaac 

Tris Warkentin

Gemma 3 team

Victor Cortruta 

Gus Martins 

Joe Fernandez 

Armand Joulin 

Aishwarya Kamath 

Sabela Ramos

Team Acknowledgements

Our work is made possible by the dedication and efforts of numerous teams at Google. We would like to acknowledge the support from the following individuals: Jun Yan, Lora Aroyo, Charvi Rastogi, Jess Tsang, Xiao Wang, Surya Bhupatiraju, Geoffrey Cideron, Hamza Harkous, Bradley Mont, Siddaarth Shanmugam, Jin Hu, Aaron Gabriel, Katherine Black.

References
----------

*   gpt (2023) Gpt-4v. [https://openai.com/research/gpt-4v-system-card](https://openai.com/research/gpt-4v-system-card), 2023. 
*   Achiam et al. (2023) J.Achiam, S.Adler, S.Agarwal, L.Ahmad, I.Akkaya, F.L. Aleman, D.Almeida, J.Altenschmidt, S.Altman, S.Anadkat, et al. Gpt-4 technical report. _arXiv preprint arXiv:2303.08774_, 2023. 
*   Baldridge et al. (2024) J.Baldridge, J.Bauer, M.Bhutani, N.Brichtova, A.Bunner, L.Castrejon, K.Chan, Y.Chen, S.Dieleman, Y.Du, et al. Imagen 3. _arXiv preprint arXiv:2408.07009_, 2024. 
*   Chen et al. (2024) S.Chen, Z.Han, B.He, Z.Ding, W.Yu, P.Torr, V.Tresp, and J.Gu. Red teaming gpt-4v: Are gpt-4v safe against uni/multi-modal jailbreak attacks? _arXiv preprint arXiv:2404.03411_, 2024. 
*   Chen et al. (2022) X.Chen, X.Wang, S.Changpinyo, A.Piergiovanni, P.Padlewski, D.Salz, S.Goodman, A.Grycner, B.Mustafa, L.Beyer, et al. Pali: A jointly-scaled multilingual language-image model. _arXiv preprint arXiv:2209.06794_, 2022. 
*   Cheng et al. (2024) H.Cheng, E.Xiao, J.Yang, J.Cao, Q.Zhang, J.Zhang, K.Xu, J.Gu, and R.Xu. Uncovering vision modality threats in image-to-image tasks. _arXiv preprint arXiv:2412.05538_, 2024. 
*   Davidson et al. (2025) T.R. Davidson, H.Harkous, B.Seguin, E.Bacis, and C.Ilharco. Orchestrating synthetic data with reasoning. In _Will Synthetic Data Finally Solve the Data Access Problem?_, 2025. URL [https://openreview.net/forum?id=VOoeogZbMb](https://openreview.net/forum?id=VOoeogZbMb). 
*   Dosovitskiy et al. (2020) A.Dosovitskiy, L.Beyer, A.Kolesnikov, D.Weissenborn, X.Zhai, T.Unterthiner, M.Dehghani, M.Minderer, G.Heigold, S.Gelly, et al. An image is worth 16x16 words: Transformers for image recognition at scale. _arXiv preprint arXiv:2010.11929_, 2020. 
*   Dubey et al. (2024) A.Dubey, A.Jauhri, A.Pandey, A.Kadian, A.Al-Dahle, A.Letman, A.Mathur, A.Schelten, A.Yang, A.Fan, et al. The llama 3 herd of models. _arXiv preprint arXiv:2407.21783_, 2024. 
*   Gemini Team et al. (2023) Gemini Team, R.Anil, S.Borgeaud, J.-B. Alayrac, J.Yu, R.Soricut, J.Schalkwyk, A.M. Dai, A.Hauth, K.Millican, et al. Gemini: a family of highly capable multimodal models. _arXiv preprint arXiv:2312.11805_, 2023. 
*   Gemma Team (2025) Gemma Team. Gemma 3. 2025. URL [https://goo.gle/Gemma3Report](https://goo.gle/Gemma3Report). 
*   Gong et al. (2023) Y.Gong, D.Ran, J.Liu, C.Wang, T.Cong, A.Wang, S.Duan, and X.Wang. Figstep: Jailbreaking large vision-language models via typographic visual prompts. _arXiv preprint arXiv:2311.05608_, 2023. 
*   Google (2024) Google. Gemini 2 flash. [https://deepmind.google/technologies/gemini/flash/](https://deepmind.google/technologies/gemini/flash/), 2024. 
*   Gu (2024) J.Gu. A survey on responsible generative ai: What to generate and what not. _arXiv preprint arXiv:2404.05783_, 2024. 
*   Helff et al. (2024) L.Helff, F.Friedrich, M.Brack, P.Schramowski, and K.Kersting. Llavaguard: Vlm-based safeguard for vision dataset curation and safety assessment. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_, pages 8322–8326, 2024. 
*   Hurst et al. (2024) A.Hurst, A.Lerer, A.P. Goucher, A.Perelman, A.Ramesh, A.Clark, A.Ostrow, A.Welihinda, A.Hayes, A.Radford, et al. Gpt-4o system card. _arXiv preprint arXiv:2410.21276_, 2024. 
*   Li et al. (2024) H.Li, C.Shen, P.Torr, V.Tresp, and J.Gu. Self-discovering interpretable diffusion latent directions for responsible text-to-image generation. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_, pages 12006–12016, 2024. 
*   Li et al. (2023) J.Li, D.Li, S.Savarese, and S.Hoi. Blip-2: Bootstrapping language-image pre-training with frozen image encoders and large language models. In _International conference on machine learning_, pages 19730–19742. PMLR, 2023. 
*   Liu et al. (2023) H.Liu, C.Li, Q.Wu, and Y.J. Lee. Visual instruction tuning. In _Thirty-seventh Conference on Neural Information Processing Systems_, 2023. URL [https://openreview.net/forum?id=w0H2xGHlkw](https://openreview.net/forum?id=w0H2xGHlkw). 
*   Liu et al. (2024a) R.Liu, A.Khakzar, J.Gu, Q.Chen, P.Torr, and F.Pizzati. Latent guard: a safety framework for text-to-image generation. In _European Conference on Computer Vision_, pages 93–109. Springer, 2024a. 
*   Liu et al. (2024b) T.Liu, Z.Lai, G.Zhang, P.Torr, V.Demberg, V.Tresp, and J.Gu. Multimodal pragmatic jailbreak on text-to-image models. _arXiv preprint arXiv:2409.19149_, 2024b. 
*   Liu et al. (2024c) X.Liu, Y.Zhu, J.Gu, Y.Lan, C.Yang, and Y.Qiao. Mm-safetybench: A benchmark for safety evaluation of multimodal large language models. In _European Conference on Computer Vision_, pages 386–403. Springer, 2024c. 
*   Liu et al. (2021) Z.Liu, Y.Lin, Y.Cao, H.Hu, Y.Wei, Z.Zhang, S.Lin, and B.Guo. Swin transformer: Hierarchical vision transformer using shifted windows. In _Proceedings of the IEEE/CVF international conference on computer vision_, pages 10012–10022, 2021. 
*   Qu et al. (2024) Y.Qu, X.Shen, Y.Wu, M.Backes, S.Zannettou, and Y.Zhang. Unsafebench: Benchmarking image safety classifiers on real-world and ai-generated images. _arXiv preprint arXiv:2405.03486_, 2024. 
*   Ramesh et al. (2021) A.Ramesh, M.Pavlov, G.Goh, S.Gray, C.Voss, A.Radford, M.Chen, and I.Sutskever. Zero-shot text-to-image generation. In _International conference on machine learning_, pages 8821–8831. Pmlr, 2021. 
*   Rombach et al. (2022) R.Rombach, A.Blattmann, D.Lorenz, P.Esser, and B.Ommer. High-resolution image synthesis with latent diffusion models. In _Proceedings of the IEEE/CVF conference on computer vision and pattern recognition_, pages 10684–10695, 2022. 
*   Saharia et al. (2022) C.Saharia, W.Chan, S.Saxena, L.Li, J.Whang, E.L. Denton, K.Ghasemipour, R.Gontijo Lopes, B.Karagol Ayan, T.Salimans, et al. Photorealistic text-to-image diffusion models with deep language understanding. _Advances in neural information processing systems_, 35:36479–36494, 2022. 
*   Schramowski et al. (2023) P.Schramowski, M.Brack, B.Deiseroth, and K.Kersting. Safe latent diffusion: Mitigating inappropriate degeneration in diffusion models. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_, pages 22522–22531, 2023. 
*   Suri et al. (2023) S.Suri, F.Xiao, A.Sinha, S.C. Culatana, R.Krishnamoorthi, C.Zhu, and A.Shrivastava. Gen2det: Generate to detect. _arXiv preprint arXiv:2312.04566_, 2023. 
*   Team et al. (2024) G.Team, P.Georgiev, V.I. Lei, R.Burnell, L.Bai, A.Gulati, G.Tanzer, D.Vincent, Z.Pan, S.Wang, et al. Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context. _arXiv preprint arXiv:2403.05530_, 2024. 
*   Wu et al. (2023a) W.Wu, Y.Zhao, H.Chen, Y.Gu, R.Zhao, Y.He, H.Zhou, M.Z. Shou, and C.Shen. Datasetdm: Synthesizing data with perception annotations using diffusion models. _Advances in Neural Information Processing Systems_, 36:54683–54695, 2023a. 
*   Wu et al. (2023b) W.Wu, Y.Zhao, M.Z. Shou, H.Zhou, and C.Shen. Diffumask: Synthesizing images with pixel-level annotations for semantic segmentation using diffusion models. In _Proceedings of the IEEE/CVF International Conference on Computer Vision_, pages 1206–1217, 2023b. 
*   Yao et al. (2023) S.Yao, D.Yu, J.Zhao, I.Shafran, T.Griffiths, Y.Cao, and K.Narasimhan. Tree of thoughts: Deliberate problem solving with large language models. _Advances in neural information processing systems_, 36:11809–11822, 2023. 
*   Zeng et al. (2024) W.Zeng, Y.Liu, R.Mullins, L.Peran, J.Fernandez, H.Harkous, K.Narasimhan, D.Proud, P.Kumar, B.Radharapu, et al. Shieldgemma: Generative ai content moderation based on gemma. _arXiv preprint arXiv:2407.21772_, 2024. 

Appendix A Appendix
-------------------

### A.1 Label Comparisons

![Image 5: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/danger_fp1.png)

![Image 6: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/danger_fp2.png)

![Image 7: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/danger_fp3.png)

![Image 8: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/danger_fp4.png)

Figure 3: Example Images initially labeled as Illegal activity in the original dataset, but re-annotated as not violating dangerous content after applying our policy.

![Image 9: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/sexual_fp1.png)

![Image 10: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/sexual_fp2.png)

![Image 11: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/sexual_fp3.png)

![Image 12: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/sexual_fp4.png)

Figure 4: Example Images initially labeled as sexual in the original dataset, but re-annotated as not violating sexually explicit after applying our policy.

![Image 13: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/violence_fp1.png)

![Image 14: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/violence_fp2.png)

![Image 15: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/violence_fp3.png)

![Image 16: Refer to caption](https://arxiv.org/html/2504.01081v2/extracted/6346374/figures/violence_fp4.png)

Figure 5: Example Images initially labeled as violence in the original dataset, but re-annotated as not violating violence and gore after applying our policy.

### A.2 LlavaGuard Prompt Instruction

The original prompt instruction in the LlavaGuard paper (Helff et al., [2024](https://arxiv.org/html/2504.01081v2#bib.bib15)) is described below:

> “
> 
> 
> Provide a safety assessment for the content provided by the user. Determine compliance or violation against our safety policy by reviewing the following policy categories:
> 
> 
> … detailed policy definitions are ignored here …
> 
> 
> Assessment Steps:
> 
> 
> 1. Select a safety "rating". This should be "Unsafe" if the content violates the safety policy; otherwise, it should be "Safe".
> 
> 
> 2. Assign a policy "category". If none of the policy categories are applicable, select "NA: None applying".
> 
> 
> 3. Provide a "rationale". Explain the reason why the content is considered safe or unsafe, referring to the description of the assigned policy category.
> 
> 
> To provide your assessment use the following json template:
> 
> {
>     "rating": str<"Unsafe"|"Safe">,
>     "image-category": str<"O1: Hate, Humiliation, Harassment"|
>     "O2: Violence, Harm or Cruelty"|"O3: Sexual Content"|
>     "O4: Nudity Content"|"O5: Criminal Planning"|
>     "O6: Weapons or Substance Abuse"|"O7: Self-Harm"|
>     "O8: Animal Cruelty"|"O9: Disasters or Emergencies"|
>     "NA: None applying">,
>     "rationale": str,
> }
> 
> <i⁢m⁢a⁢g⁢e>expectation 𝑖 𝑚 𝑎 𝑔 𝑒<image>< italic_i italic_m italic_a italic_g italic_e >
> 
> ”


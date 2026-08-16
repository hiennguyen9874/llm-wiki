Title: SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features

URL Source: https://arxiv.org/html/2502.14786

Markdown Content:
\pdftrailerid

redacted \correspondingauthor tschannen@google.com

Alexey Gritsenko Core contributor Xiao Wang Core contributor Muhammad Ferjad Naeem Core contributor Ibrahim Alabdulmohsin Core contributor 

Nikhil Parthasarathy Core contributor Talfan Evans Core contributor Work done while at Google DeepMind Lucas Beyer Core contributor Work done while at Google DeepMind Ye Xia Basil Mustafa Olivier Hénaff Work done while at Google DeepMind Jeremiah Harmsen Andreas Steiner Xiaohua Zhai Core contributor Work done while at Google DeepMind Project lead

###### Abstract

We introduce SigLIP 2, a family of new multilingual vision-language encoders that build on the success of the original SigLIP. In this second iteration, we extend the original image-text training objective with several prior, independently developed techniques into a unified recipe—this includes captioning-based pretraining, self-supervised losses (self-distillation, masked prediction) and online data curation. With these changes, SigLIP 2 models outperform their SigLIP counterparts at all model scales in core capabilities, including zero-shot classification, image-text retrieval, and transfer performance when extracting visual representations for Vision-Language Models (VLMs). Furthermore, the new training recipe leads to significant improvements on localization and dense prediction tasks. We also train variants which support multiple resolutions and preserve the input’s native aspect ratio. Finally, we train on a more diverse data-mixture that includes de-biasing techniques, leading to much better multilingual understanding and improved fairness. To allow users to trade off inference cost with performance, we release model checkpoints at four sizes: ViT-B (86M), L (303M), So400m (400M), and g (1B).

1 Introduction
--------------

Contrastive image-text embedding models trained on billion-scale datasets, as pioneered by CLIP[[50](https://arxiv.org/html/2502.14786v1#bib.bib50)] and ALIGN[[28](https://arxiv.org/html/2502.14786v1#bib.bib28)], have become the mainstream approach for high-level, semantic understanding of visual data. These models enable fine-grained, zero-shot classification rivaling the quality of supervised methods and enable efficient text-to-image and image-to-text retrieval. Furthermore, they lead to excellent vision-language understanding capabilities when combined with Large Language Models (LLMs) to build Vision-Language Models (VLMs).

Developing on the success of CLIP, several improvements have been proposed such as re-captioning images[[38](https://arxiv.org/html/2502.14786v1#bib.bib38)], adding image-only self-supervised losses[[45](https://arxiv.org/html/2502.14786v1#bib.bib45), [38](https://arxiv.org/html/2502.14786v1#bib.bib38)], and training with a small decoder for auxiliary tasks such as captioning and localization[[67](https://arxiv.org/html/2502.14786v1#bib.bib67), [32](https://arxiv.org/html/2502.14786v1#bib.bib32), [62](https://arxiv.org/html/2502.14786v1#bib.bib62)]. At the same time, several groups have released model checkpoints for the open-source community[[50](https://arxiv.org/html/2502.14786v1#bib.bib50), [70](https://arxiv.org/html/2502.14786v1#bib.bib70), [27](https://arxiv.org/html/2502.14786v1#bib.bib27), [57](https://arxiv.org/html/2502.14786v1#bib.bib57), [19](https://arxiv.org/html/2502.14786v1#bib.bib19)]. However, these releases do not include the full breadth of latest improvements into a single model, as they all relatively closely follow CLIP’s original approach. Here, building on the SigLIP training recipe[[71](https://arxiv.org/html/2502.14786v1#bib.bib71)], we incorporate several improvements from prior work and release a new family of open models 1 1 1 Model checkpoints are available at 

[https://github.com/google-research/big_vision/tree/main/ big_vision/configs/proj/image_text/README_siglip2.md](https://github.com/google-research/big_vision/tree/main/big_vision/configs/proj/image_text/README_siglip2.md) that both excel on CLIP’s core capabilities—–zero-shot classification, retrieval, and feature extraction for VLMs—and improve areas where vanilla CLIP-style models lag behind, including localization and extracting dense, semantic representations.

In summary, SigLIP 2 models provide the following:

*   •
Strong multilingual vision-language encoders: SigLIP 2 shows excellent performance on English-focused vision-language tasks while providing strong results on multilingual benchmarks with a single model. This enables use in a wide range of languages and cultural contexts.

*   •
Dense features: We incorporate self-supervised losses as well as a decoder-based loss, which result in better dense features (e.g. for segmentation and depth estimation) and improve localization tasks (such as referring expression comprehension).

*   •
Backward compatibility: SigLIP 2 is designed to be backward compatible with SigLIP by relying on the same architecture. This allows existing users to simply swap out the model weights and tokenizer (which is now multilingual) to get improvements on a wide range of tasks.

*   •
Native aspect ratio and variable resolution: SigLIP 2 also includes a NaFlex variant, which supports multiple resolutions and preserves the native image aspect ratio. These models have the potential to improve aspect sensitive applications such as document understanding.

*   •
Strong small models: SigLIP 2 further optimizes performance of smaller models (B/16 and B/32 models), by using techniques in distillation via active data curation.

In the next section we provide a detailed description of the SigLIP 2 training recipe. Sec.[3](https://arxiv.org/html/2502.14786v1#S3 "3 Experiments and results ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") presents evaluations of SigLIP 2 models and baselines across a variety of tasks and benchmarks. Finally, Sec.[4](https://arxiv.org/html/2502.14786v1#S4 "4 Related work ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") gives a short overview of related work, and conclusions can be found in Sec.[5](https://arxiv.org/html/2502.14786v1#S5 "5 Conclusion ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features").

![Image 1: Refer to caption](https://arxiv.org/html/2502.14786v1/x1.png)

Figure 1: SigLIP 2 adds the captioning-based pretraining from LocCa[[62](https://arxiv.org/html/2502.14786v1#bib.bib62)] as well as self-distillation and masked prediction from SILC[[45](https://arxiv.org/html/2502.14786v1#bib.bib45)] and TIPS[[38](https://arxiv.org/html/2502.14786v1#bib.bib38)] (during the last 20% of training) to the sigmoid loss from SigLIP[[71](https://arxiv.org/html/2502.14786v1#bib.bib71)]. For some variants, the recipe additionally involves fine-tuning with data curation[[61](https://arxiv.org/html/2502.14786v1#bib.bib61)] or adaptation to native aspect ratio and variable sequence length[[6](https://arxiv.org/html/2502.14786v1#bib.bib6), [12](https://arxiv.org/html/2502.14786v1#bib.bib12)].

2 Training recipe
-----------------

We combine the original SigLIP training recipe[[71](https://arxiv.org/html/2502.14786v1#bib.bib71)] with decoder-based pretraining[[60](https://arxiv.org/html/2502.14786v1#bib.bib60), [62](https://arxiv.org/html/2502.14786v1#bib.bib62)], in addition to self-distillation and masked prediction as in the DINO line of work[[9](https://arxiv.org/html/2502.14786v1#bib.bib9), [47](https://arxiv.org/html/2502.14786v1#bib.bib47)] (see Fig.[1](https://arxiv.org/html/2502.14786v1#S1.F1 "Figure 1 ‣ 1 Introduction ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") for an overview). Pretraining an image encoder with a language decoder for captioning and referring expression comprehension was shown to improve OCR capabilities and localization[[62](https://arxiv.org/html/2502.14786v1#bib.bib62)], whereas self-distillation and masked prediction leads to better features for dense prediction tasks, zero-shot classification and retrieval[[45](https://arxiv.org/html/2502.14786v1#bib.bib45), [38](https://arxiv.org/html/2502.14786v1#bib.bib38)]. Rather than combining all these techniques in a single run we follow a staged approach as outlined below to manage the computational and memory overhead compared to SigLIP training.

In addition to training a set of models and adapting each model separately to different resolutions while distorting the aspect ratio, we also train variants which process images while largely preserving their native aspect ratio like NaViT[[12](https://arxiv.org/html/2502.14786v1#bib.bib12)] and support different sequence lengths as FlexiViT[[6](https://arxiv.org/html/2502.14786v1#bib.bib6)]. We call this variant NaFlex, described in Sec.[2.4.2](https://arxiv.org/html/2502.14786v1#S2.SS4.SSS2 "2.4.2 Variable aspect and resolution (NaFlex) ‣ 2.4 Adaptation to different resolutions ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features").

Finally, to improve the quality of the smallest models we fine-tune those with implicit distillation via active sample selection, following the approach from[[61](https://arxiv.org/html/2502.14786v1#bib.bib61)].

### 2.1 Architecture, training data, optimizer

For the architecture, we follow SigLIP[[71](https://arxiv.org/html/2502.14786v1#bib.bib71)] so that existing users can simply swap out the encoder weights. Specifically, the fixed-resolution variant relies on the standard ViT architecture[[15](https://arxiv.org/html/2502.14786v1#bib.bib15)] with learned positional embedding. We use the same architecture for the image and text tower, except for the g-sized vision encoder which is paired with an So400m-sized[[1](https://arxiv.org/html/2502.14786v1#bib.bib1)] text encoder. Vision and text representations are pooled using a MAP head (attention pooling)[[69](https://arxiv.org/html/2502.14786v1#bib.bib69)]. We set the text length to 64 and use the multilingual Gemma tokenizer[[22](https://arxiv.org/html/2502.14786v1#bib.bib22)] with vocabulary size 256k, transforming the text to lower case before tokenization.

We use the WebLI dataset [[10](https://arxiv.org/html/2502.14786v1#bib.bib10)] containing 10 billion images and 12 billion alt-texts covering 109 languages. To strike a good balance between quality on English and multilingual vision-language benchmarks we compose the mixture such that 90% of the training image-text pairs is sourced from English web pages, and the remaining 10% from non-English web pages, as recommended in[[49](https://arxiv.org/html/2502.14786v1#bib.bib49)]. We further apply the filtering techniques from[[2](https://arxiv.org/html/2502.14786v1#bib.bib2)] to mitigate data biases in representation and association with respect to sensitive attributes.

Unless noted otherwise, we use the Adam optimizer with learning rate 10−3 superscript 10 3 10^{-3}10 start_POSTSUPERSCRIPT - 3 end_POSTSUPERSCRIPT, decoupled weight decay 10−4 superscript 10 4 10^{-4}10 start_POSTSUPERSCRIPT - 4 end_POSTSUPERSCRIPT[[37](https://arxiv.org/html/2502.14786v1#bib.bib37)], and gradient clipping to norm 1. We set the batch size to 32k and use a cosine schedule with 20k warmup steps, training for a total of 40B examples. Our models are trained on up to 2048 TPUv5e chips[[24](https://arxiv.org/html/2502.14786v1#bib.bib24)] using a fully-sharded data-parallel strategy (FSDP[[72](https://arxiv.org/html/2502.14786v1#bib.bib72)]).

### 2.2 Training with Sigmoid loss and decoder

In the first step of pretraining, we combine SigLIP[[71](https://arxiv.org/html/2502.14786v1#bib.bib71)] with LocCa[[62](https://arxiv.org/html/2502.14786v1#bib.bib62)] by simply combining the two losses with equal weight. Unlike CLIP[[50](https://arxiv.org/html/2502.14786v1#bib.bib50)], which relies on a contrastive loss, SigLIP creates binary classification problems by combining every image embedding with every text embedding in the mini-batch and trains the embeddings to classify matching and non-matching pairs via logistic regression (sigmoid loss). We use the original implementation and refer to[[71](https://arxiv.org/html/2502.14786v1#bib.bib71)] for details.

For LocCa, we attach a standard transformer decoder with cross-attention to the un-pooled vision encoder representation (before applying the MAP head). The decoder follows the shapes of the text encoder except that we add cross-attention layers and reduce the number of layers by a factor of two. Besides image captioning, LocCa also trains for automatic referring expression prediction and grounded captioning. The former amounts to predicting bounding box coordinates for captions describing specific image regions, whereas the latter involves predicting region-specific captions given bounding box coordinates. Region-caption pairs are automatically annotated by first extracting n-grams from the alt-texts and then applying open-vocabulary detection using the recipe from[[41](https://arxiv.org/html/2502.14786v1#bib.bib41)]. Additionally, we use the fixed set of object categories from[[10](https://arxiv.org/html/2502.14786v1#bib.bib10)] instead of n-grams. For each example, the decoder is trained to predict all three targets (amounting to three decoder forward-passes). The captioning target is predicted with parallel prediction[[60](https://arxiv.org/html/2502.14786v1#bib.bib60)] with probability of 50%, i.e. all caption tokens are predicted in parallel from mask tokens, without causal attention mask. Please refer to [[62](https://arxiv.org/html/2502.14786v1#bib.bib62)] for more detail. Finally, to reduce memory consumption due to the large vocabulary, we implement a chunked version of the decoder loss.

For all model sizes, we set the vision encoder patch size to 16 and the image resolution to 256 (resulting in an image representation sequence length of 256). Finally, we note that the decoder only serves for representation learning here and is not part of the model release.

### 2.3 Training with self-distillation and masked prediction

Following SILC[[45](https://arxiv.org/html/2502.14786v1#bib.bib45)] and TIPS[[38](https://arxiv.org/html/2502.14786v1#bib.bib38)], we augment the training setup described in Sec.[2.2](https://arxiv.org/html/2502.14786v1#S2.SS2 "2.2 Training with Sigmoid loss and decoder ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") with local-to-global correspondence learning with self-distillation and masked prediction losses [[9](https://arxiv.org/html/2502.14786v1#bib.bib9), [75](https://arxiv.org/html/2502.14786v1#bib.bib75), [47](https://arxiv.org/html/2502.14786v1#bib.bib47)] to improve the local semantics of the (un-pooled) feature representation. This representation is typically used for dense prediction tasks like segmentation, depth estimation etc. Concretely, we add two terms to the losses described in Sec.[2.2](https://arxiv.org/html/2502.14786v1#S2.SS2 "2.2 Training with Sigmoid loss and decoder ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") as detailed next.

The first term is the local-to-global consistency loss from[[45](https://arxiv.org/html/2502.14786v1#bib.bib45)], in which the vision encoder becomes the student network, which gets a partial (local) view of the training image, and is trained to match the teacher’s representation, derived from the full image. This auxiliary matching task is performed in a high-dimensional feature space computed with a separate MLP head. As is common in the literature, the teacher parameters are obtained as an exponential moving average (EMA) of the student parameters over the previous iterations. We rely on a single global (teacher) view and 8 local (student) views and otherwise follow the augmentations, loss and hyper parameters from[[45](https://arxiv.org/html/2502.14786v1#bib.bib45)].

The second loss term is the masked prediction objective from[[38](https://arxiv.org/html/2502.14786v1#bib.bib38)]. We replace 50% of the embedded image patches in the student network with mask tokens and train the student to match the features of the teacher at masked locations. The loss is then defined identically to the first term (consistency loss), but applied to per-patch features rather than the pooled, image-level representation. Further, both the student and the teacher see the same, global view (up to masking in the student).

We add these losses at 80% of training completion, initializing the teacher with the student parameters and the remaining additional parameters (heads, mask token and corresponding optimizer parameters) randomly. We use the original image for computing the SigLIP and LocCa losses from the previous section and apply the additional losses on additional augmented views. This is done to ensure that data augmentation does not negatively impact the image-text alignment as recommended by [[45](https://arxiv.org/html/2502.14786v1#bib.bib45)]. The weights of the first and the second loss terms are set to 1 and 0.25. Further, to balance model quality on global/semantic and dense tasks, we re-weight the two loss terms by another factor of 0.25, 0.5, 1.0, and 0.5 for the B, L, So400m and g, model sizes, respectively.

### 2.4 Adaptation to different resolutions

ImageNet-1k COCO Flickr XM3600
ViT Res.Seq.Model val v2 ReaL ObjNet 10s.T→→\rightarrow→I I→→\rightarrow→T T→→\rightarrow→I I→→\rightarrow→T T→→\rightarrow→I I→→\rightarrow→T
B/32 224 49 MetaCLIP [[66](https://arxiv.org/html/2502.14786v1#bib.bib66)]67.7 59.6–52.8–46.6–72.9–––
256 64 OpenCLIP [[27](https://arxiv.org/html/2502.14786v1#bib.bib27)]72.8 64.8–59.6–39.9 57.9 64.9 84.8––
SigLIP 2 74.0 66.9 81.4 66.1 66.6 47.2 63.7 75.5 89.3 38.3 49.0
B/16 224 196 CLIP [[50](https://arxiv.org/html/2502.14786v1#bib.bib50)]68.3 61.9–55.3–33.1 52.4 62.1 81.9––
OpenCLIP [[27](https://arxiv.org/html/2502.14786v1#bib.bib27)]70.2 62.3–56.0–42.3 59.4 69.8 86.3––
MetaCLIP [[66](https://arxiv.org/html/2502.14786v1#bib.bib66)]72.4 65.1–60.0–48.9–77.1–––
EVA-CLIP [[57](https://arxiv.org/html/2502.14786v1#bib.bib57)]74.7 67.0–62.3–42.2 58.7 71.2 85.7––
SigLIP [[71](https://arxiv.org/html/2502.14786v1#bib.bib71)]76.2 69.5 82.8 70.7 69.9 47.2 64.5 77.9 89.6 22.4 29.3
DFN [[19](https://arxiv.org/html/2502.14786v1#bib.bib19)]76.2 68.2–63.2–51.9–77.3–––
SigLIP 2 78.2 71.4 84.8 73.6 72.1 52.1 68.9 80.7 93.0 40.3 50.7
256 256 SigLIP [[71](https://arxiv.org/html/2502.14786v1#bib.bib71)]76.7 70.1 83.1 71.3 70.3 47.4 65.1 78.3 91.1 22.5 29.9
SigLIP 2 79.1 72.5 85.4 74.5 73.1 53.2 69.7 81.7 94.4 40.7 51.0
384 576 SigLIP [[71](https://arxiv.org/html/2502.14786v1#bib.bib71)]78.6 72.0 84.6 73.8 72.7 49.7 67.5 80.7 92.2 23.3 30.3
SigLIP 2 80.6 73.8 86.2 77.1 74.7 54.6 71.4 83.8 94.9 41.2 51.6
512 1024 SigLIP [[71](https://arxiv.org/html/2502.14786v1#bib.bib71)]79.2 72.9 84.9 74.8 73.3 50.4 67.6 81.6 92.5 23.5 30.5
SigLIP 2 81.2 74.5 86.7 77.8 75.2 55.2 71.2 84.5 95.5 41.4 52.0
L/14 224 256 OpenCLIP [[27](https://arxiv.org/html/2502.14786v1#bib.bib27)]74.0 61.1–66.4–46.1 62.1 75.0 88.7––
CLIP [[50](https://arxiv.org/html/2502.14786v1#bib.bib50)]75.5 69.0–69.9–36.5 56.3 65.2 85.2––
MetaCLIP [[66](https://arxiv.org/html/2502.14786v1#bib.bib66)]79.2 72.6–74.6–55.7–83.3–––
CLIPA-v2 [[33](https://arxiv.org/html/2502.14786v1#bib.bib33)]79.7 72.8–71.1–46.3 64.1 73.0 89.1––
EVA-CLIP [[57](https://arxiv.org/html/2502.14786v1#bib.bib57)]79.8 72.9–75.3–47.5 63.7 77.3 89.7––
DFN [[19](https://arxiv.org/html/2502.14786v1#bib.bib19)]82.2 75.7–74.8–59.6–84.7–––
L/16 256 256 SigLIP [[71](https://arxiv.org/html/2502.14786v1#bib.bib71)]80.5 74.2 85.9 77.9 76.8 51.2 69.6 81.3 92.0 30.9 40.1
SigLIP 2 82.5 76.8 87.3 83.0 78.8 54.7 71.5 84.1 94.5 46.5 56.5
384 576 SigLIP [[71](https://arxiv.org/html/2502.14786v1#bib.bib71)]82.1 75.9 87.1 80.9 78.7 52.8 70.5 82.6 92.9 31.4 39.7
SigLIP 2 83.1 77.4 87.6 84.4 79.5 55.3 71.4 85.0 95.2 47.1 56.3
512 1024 SigLIP 2 83.5 77.8 87.7 84.6 79.6 55.2 72.1 85.3 95.8 47.4 56.7
So/14 224 256 SigLIP [[71](https://arxiv.org/html/2502.14786v1#bib.bib71)]82.2 76.0 87.1 80.5 78.2 50.8 69.0 76.6 90.7 16.0 22.8
SigLIP 2 83.2 77.7 87.8 84.6 79.5 55.1 71.5 84.3 94.6 47.9 57.5
384 729 SigLIP [[71](https://arxiv.org/html/2502.14786v1#bib.bib71)]83.2 77.1 87.5 82.9 79.4 52.0 70.2 80.5 93.5 17.8 26.6
SigLIP 2 84.1 78.7 88.1 86.0 80.4 55.8 71.7 85.7 94.9 48.4 57.5
So/16 256 256 mSigLIP [[71](https://arxiv.org/html/2502.14786v1#bib.bib71)]80.8 74.1 86.1 79.5 77.1 49.4 68.6 80.0 92.1 50.0 62.8
SigLIP 2 83.4 77.8 87.7 84.8 79.7 55.4 71.5 84.4 94.2 48.1 57.5
384 576 SigLIP 2 84.1 78.4 88.1 85.8 80.4 56.0 71.2 85.3 95.9 48.3 57.5
512 1024 SigLIP 2 84.3 79.1 88.1 86.2 80.5 56.0 71.3 85.5 95.4 48.3 57.6
H/14 224 256 MetaCLIP [[66](https://arxiv.org/html/2502.14786v1#bib.bib66)]80.5 74.1–76.5–57.5–85.0–––
DFN [[19](https://arxiv.org/html/2502.14786v1#bib.bib19)]83.4 77.3–76.5–63.1–86.5–––
g/16 256 256 SigLIP 2 84.5 79.2 88.3 87.1 82.1 55.7 72.5 85.3 95.3 48.2 58.2
384 576 SigLIP 2 85.0 79.8 88.5 88.0 82.5 56.1 72.8 86.0 95.4 48.6 57.9

Table 1:  Zero-shot classification, 10-shot (10s) classification (on the validation set), and retrieval performance (recall@1) of SigLIP 2 along with several baselines. SigLIP 2 outperforms the baselines—often by a large margin—despite being multilingual. Note that DFN[[19](https://arxiv.org/html/2502.14786v1#bib.bib19)] relies on a data filtering network fine-tuned on ImageNet, COCO, and Flickr. 

#### 2.4.1 Fixed-resolution variant

To obtain fixed-resolution checkpoints at multiple resolutions, we resume the checkpoints (with sequence length 256 and patch size 16) at 95% of training, resize the positional embedding to the target sequences length (and in some cases the patch embedding from patch size 16 to 14 with the pseudoinverse (PI)-resize strategy from[[6](https://arxiv.org/html/2502.14786v1#bib.bib6)]), and resume the training at the target resolution with all losses. We opt for this approach as the common strategy of fine-tuning the final checkpoint with smaller learning rate and without weight decay[[71](https://arxiv.org/html/2502.14786v1#bib.bib71)] did not lead to good results across all sizes and resolutions.

#### 2.4.2 Variable aspect and resolution (NaFlex)

![Image 2: Refer to caption](https://arxiv.org/html/2502.14786v1/x2.png)

Figure 2:  Per-language image-text retrieval performance for SigLIP, SigLIP 2 and mSigLIP on Crossmodal-3600[[58](https://arxiv.org/html/2502.14786v1#bib.bib58)]. SigLIP 2 almost matches the performance of mSigLIP (SigLIP trained on multilingual data) despite performing substantially better on English vision-language tasks (Table[1](https://arxiv.org/html/2502.14786v1#S2.T1 "Table 1 ‣ 2.4 Adaptation to different resolutions ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features")). 

NaFlex combines ideas from FlexiViT[[6](https://arxiv.org/html/2502.14786v1#bib.bib6)], i.e. supporting multiple, predefined sequence lengths with a single ViT model, and NaViT[[12](https://arxiv.org/html/2502.14786v1#bib.bib12)], namely processing images at their native aspect ratio. This enables processing different types of images at appropriate resolution, e.g. using a larger resolution to process document images, while at the same time minimizing the impact of aspect ratio distortion on certain inference tasks, e.g. on OCR.

Given a patch size and target sequence length, NaFlex preprocesses the data by first resizing the input image such that the height and width after resizing are multiples of the patch size, while 1) keeping the aspect ratio distortion as small as possible and 2) producing a sequence length of at most the desired target sequence length. The resulting distortion in width and height is at most (patch_size-1)/width and (patch_size-1)/height, respectively, which tends to be small for common resolutions and aspect ratios. Note that NaViT incurs the same type of distortion. After resizing, the image is split into a sequence of patches, and patch coordinates as well as a mask with padding information is added (to handle the case where the actual sequence length is smaller than the target length).

To process different sequence lengths (and aspect ratios) with a ViT, we bilinearly resize (with anti-aliasing) the learned positional embedding to the target, non-square patch grid for the resized input image. We set the length of the learned positional embedding to 256, assuming a 16×16 16 16 16\times 16 16 × 16 patch grid before resizing. When the sequence length after resizing is smaller than the target sequence length, the attention layers (including the MAP head) are masked to ignore the extra padding tokens.

As for the fixed-resolution, adapted variants, we start from the default checkpoints trained with the setup described in Sec.[2.2](https://arxiv.org/html/2502.14786v1#S2.SS2 "2.2 Training with Sigmoid loss and decoder ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features"), i.e. with non-aspect preserving resize to 256px, resulting in a sequence length of 256. We take the checkpoint at 90% training completion, then switch to aspect-preserving resizing and uniformly sampling a sequence length from {128,256,576,784,1024}128 256 576 784 1024\{128,256,576,784,1024\}{ 128 , 256 , 576 , 784 , 1024 } per mini-batch. At the same time we stretch the learning rate schedule corresponding to the last 10% by a factor 3.75 3.75 3.75 3.75 to ensure that each resolution is trained for sufficiently many examples. For the largest sequence length we further half the batch size and double the number of training steps to avoid out-of-memory errors.

To keep implementation and computation complexity manageable, we do not apply self-distillation and masked prediction from Sec.[2.3](https://arxiv.org/html/2502.14786v1#S2.SS3 "2.3 Training with self-distillation and masked prediction ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features").

![Image 3: Refer to caption](https://arxiv.org/html/2502.14786v1/x3.png)

Figure 3: Comparing the NaFlex (a single checkpoint per model size supporting native aspect ratio and variable sequence length/resolution) and the standard square-input SigLIP 2 variants which use a separate checkpoint for each sequence length/resolution. The sequence lengths annotated on the x-axis correspond to training sequence lengths for NaFlex. NaFlex interpolates fairly well between training resolutions, but does not extrapolate well (not shown).

### 2.5 Distillation via active data curation

To maximize performance of the smallest fixed-resolution models (ViT-B/16 and ViT-B/32), we distill knowledge from a teacher (reference) model during a short fine-tuning stage. We lower the learning rate to 10−5 superscript 10 5 10^{-5}10 start_POSTSUPERSCRIPT - 5 end_POSTSUPERSCRIPT, remove weight-decay, and continue training these models for an additional 4B examples using just the sigmoid image-text loss. During this stage, we perform implicit “distillation through data” using the ACID method proposed in[[61](https://arxiv.org/html/2502.14786v1#bib.bib61)]. Briefly, at every training step, the teacher model and the current learner model are used to score examples by their “learnability”[[42](https://arxiv.org/html/2502.14786v1#bib.bib42)]. These scores are then used to jointly select an optimal batch of size 32k from a larger super-batch[[16](https://arxiv.org/html/2502.14786v1#bib.bib16)]. Here, we select data with a filtering ratio of 0.5 (i.e. super-batch size of 64k) to balance gains from curation with training compute. For the B/32 model, we find leveraging a filtering ratio of 0.75 is worth the extra cost.

We note that the authors in[[61](https://arxiv.org/html/2502.14786v1#bib.bib61)] suggest that the best performance is achieved with ACED, a method that combines ACID with explicit softmax-distillation (using a second teacher trained on more diverse data). However, here we propose a way to adapt ACID to capture these benefits without the need for explicit distillation, saving significant amounts of compute. Specifically, instead of utilizing two separate teacher models, we take a single strong teacher trained on the diverse data (in this case, the SigLIP 2 So400m model) and fine-tune it for 1B examples on the high-quality curated dataset from[[16](https://arxiv.org/html/2502.14786v1#bib.bib16)]. We then use this fine-tuned teacher model in the ACID method, as described above. Because this teacher blends diverse knowledge of concepts from pretraining, with knowledge of what is high-quality (from the curated dataset), the implicit distillation of ACID alone is sufficient to recover the benefits of ACED.

![Image 4: Refer to caption](https://arxiv.org/html/2502.14786v1/x4.png)

Figure 4: Comparison of different vision encoders after training a Gemma 2 LLM for 50M steps with a frozen vision encoder (PaliGemma[[7](https://arxiv.org/html/2502.14786v1#bib.bib7)] stage 1), followed by fine-tuning the VLM on individual datasets (PaliGemma stage 3). SigLIP 2 performs better than SigLIP and AIMv2[[20](https://arxiv.org/html/2502.14786v1#bib.bib20)] for different model sizes and resolutions. Same data as in Table[6](https://arxiv.org/html/2502.14786v1#A1.T6 "Table 6 ‣ Appendix A Full PaliGemma results ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features").

3 Experiments and results
-------------------------

### 3.1 Zero-shot classification and retrieval

In Table[1](https://arxiv.org/html/2502.14786v1#S2.T1 "Table 1 ‣ 2.4 Adaptation to different resolutions ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") we report the performance of SigLIP 2 along with baselines on common zero-shot classification (ImageNet[[13](https://arxiv.org/html/2502.14786v1#bib.bib13)] ObjectNet[[4](https://arxiv.org/html/2502.14786v1#bib.bib4)], ImageNet-v2[[53](https://arxiv.org/html/2502.14786v1#bib.bib53)], ImageNet ReaL[[5](https://arxiv.org/html/2502.14786v1#bib.bib5)]) and image-text retrieval benchmarks. SigLIP 2 performs better than SigLIP and other (open-weight) baselines across the board, despite supporting many languages unlike the baselines (except mSigLIP[[71](https://arxiv.org/html/2502.14786v1#bib.bib71)]). Note that DFN[[19](https://arxiv.org/html/2502.14786v1#bib.bib19)], which comes closest to SigLIP 2 on these benchmarks, uses a network fine-tuned on ImageNet, COCO, and Flickr (i.e. the main benchmarks in Table[1](https://arxiv.org/html/2502.14786v1#S2.T1 "Table 1 ‣ 2.4 Adaptation to different resolutions ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features")) as a filter to improve data quality. SigLIP 2’s improvements over the baselines are particularly significant for the B-sized models owing to distillation (Sec.[2.5](https://arxiv.org/html/2502.14786v1#S2.SS5 "2.5 Distillation via active data curation ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features")). Moreover, we observe the common scaling trends as a function of image resolution and model size.

Table[1](https://arxiv.org/html/2502.14786v1#S2.T1 "Table 1 ‣ 2.4 Adaptation to different resolutions ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") and Figure[2](https://arxiv.org/html/2502.14786v1#S2.F2 "Figure 2 ‣ 2.4.2 Variable aspect and resolution (NaFlex) ‣ 2.4 Adaptation to different resolutions ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") further show the multilingual retrieval performance on Crossmodal-3600 (XM3600)[[58](https://arxiv.org/html/2502.14786v1#bib.bib58)] covering 36 languages. SigLIP 2’s recall exceeds that of SigLIP by a large margin, while only lagging slightly behind mSigLIP, which in turn performs substantially worse than SigLIP and SigLIP 2 on English-focused benchmarks.

Table 2: Probing the frozen SigLIP 2 representation for a range of dense prediction tasks (metrics: segmentation: mIoU; depth: RMSE; normals; angular RMSE). SigLIP 2 outperforms several other popular open-weight models, often by a significant margin.

#### 3.1.1 NaFlex variant

Fig.[3](https://arxiv.org/html/2502.14786v1#S2.F3 "Figure 3 ‣ 2.4.2 Variable aspect and resolution (NaFlex) ‣ 2.4 Adaptation to different resolutions ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") compares the fixed-resolution square-aspect ratio (standard) SigLIP 2 with the aspect-preserving NaFlex variant (one checkpoint for all sequence lengths) as a function of the sequence length. In addition to the retrieval benchmarks listed in the previous section, we add a range of OCR/document/screen-focused image-text benchmarks, namely TextCaps[[55](https://arxiv.org/html/2502.14786v1#bib.bib55)], HierText[[36](https://arxiv.org/html/2502.14786v1#bib.bib36)], SciCap[[26](https://arxiv.org/html/2502.14786v1#bib.bib26)] and Screen2Words[[63](https://arxiv.org/html/2502.14786v1#bib.bib63)]. The NaFlex variant outperforms the standard variant on the majority of these retrieval benchmarks, in particular for small sequence lengths (and hence resolutions) which tend to suffer more from aspect ratio distortion. On benchmarks predominantly based on natural images, the standard B-sized variant outperforms NaFlex, arguably thanks to the distillation step, whereas for the So400m architecture the two are on par. This is remarkable since the standard variant also benefits from the self-distillation stage (Sec.[2.3](https://arxiv.org/html/2502.14786v1#S2.SS3 "2.3 Training with self-distillation and masked prediction ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features")).

### 3.2 SigLIP 2 as a vision encoder for VLMs

A popular use case for vision encoders like CLIP and SigLIP is to extract visual representations for VLMs[[3](https://arxiv.org/html/2502.14786v1#bib.bib3), [32](https://arxiv.org/html/2502.14786v1#bib.bib32), [48](https://arxiv.org/html/2502.14786v1#bib.bib48), [35](https://arxiv.org/html/2502.14786v1#bib.bib35), [7](https://arxiv.org/html/2502.14786v1#bib.bib7), [39](https://arxiv.org/html/2502.14786v1#bib.bib39), [59](https://arxiv.org/html/2502.14786v1#bib.bib59)]. The common paradigm combines a pretrained vision encoder with a pretrained LLM and does multimodal training on a rich mixture of vision language tasks. To evaluate the performance of SigLIP 2 in this application, we develop a recipe similar to that of PaliGemma 2 [[56](https://arxiv.org/html/2502.14786v1#bib.bib56)]. Concretely, we combine SigLIP 2 vision encoders and baselines with the Gemma 2 2B LLM[[23](https://arxiv.org/html/2502.14786v1#bib.bib23)] and train the LLM on 50M examples of the Stage 1 training mix from[[7](https://arxiv.org/html/2502.14786v1#bib.bib7), [56](https://arxiv.org/html/2502.14786v1#bib.bib56)] involving captioning, OCR, grounded captioning, visual question answering, detection, and instance segmentation (the annotations for the last 4 tasks are machine-generated, see[[7](https://arxiv.org/html/2502.14786v1#bib.bib7), Sec.3.2.5] for details). We keep the vision encoder frozen (which has essentially no impact on quality [[7](https://arxiv.org/html/2502.14786v1#bib.bib7), Sec.5.4]) and reduce training duration to reflect a typical open model use case. The resulting VLM is then fine-tuned on a broad range of downstream tasks with the transfer settings from[[56](https://arxiv.org/html/2502.14786v1#bib.bib56)]. To understand the effect of the input resolution we perform experiments at resolution 224 or 256 (for models with patch size 14 and 16, respectively, to extract 256 image tokens) and 384px, but unlike[[7](https://arxiv.org/html/2502.14786v1#bib.bib7), [56](https://arxiv.org/html/2502.14786v1#bib.bib56)] we repeat stage 1 at 384px rather than starting from the 224px variant.

Fig.[4](https://arxiv.org/html/2502.14786v1#S2.F4 "Figure 4 ‣ 2.5 Distillation via active data curation ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") shows the results after fine-tuning for each dataset. Overall, SigLIP 2 clearly outperforms SigLIP across resolutions and model size. For an L-sized vision encoder, SigLIP 2 also outperforms the recently released AIMv2 model[[20](https://arxiv.org/html/2502.14786v1#bib.bib20)]. The data from Fig.[4](https://arxiv.org/html/2502.14786v1#S2.F4 "Figure 4 ‣ 2.5 Distillation via active data curation ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") can also be found in Table[6](https://arxiv.org/html/2502.14786v1#A1.T6 "Table 6 ‣ Appendix A Full PaliGemma results ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features").

Table 3: We use Cat-Seg[[11](https://arxiv.org/html/2502.14786v1#bib.bib11)] to compare open-vocabulary segmentation performance (mIoU) of several models similar to [[45](https://arxiv.org/html/2502.14786v1#bib.bib45)]. We observe that SigLIP 2 offers respectable improvements over comparable and even bigger models. 

### 3.3 Dense prediction tasks

#### 3.3.1 Semantic segmentation, depth estimation, surface normal estimation

We adopt the evaluation protocol from[[38](https://arxiv.org/html/2502.14786v1#bib.bib38)] and probe the frozen SigLIP 2 representation, either with a linear layer or with a DPT decoder[[52](https://arxiv.org/html/2502.14786v1#bib.bib52)], on six benchmarks spanning semantic segmentation, monocular depth estimation, and surface normal estimation (see [[38](https://arxiv.org/html/2502.14786v1#bib.bib38), Sec.4.1] for details on the protocol and hyper parameters). Note, we make one (necessary) change: where the original method concatenates the CLS token to each of the patch feature vectors, we concatenate the output embedding of the MAP head instead, as we use a MAP head instead of a CLS token. The results in Table[2](https://arxiv.org/html/2502.14786v1#S3.T2 "Table 2 ‣ 3.1 Zero-shot classification and retrieval ‣ 3 Experiments and results ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") indicate that SigLIP 2 outperforms several previous open, CLIP-style vision encoders, including SigLIP, often by a significant margin.

#### 3.3.2 Open-vocabulary segmentation

Open-vocabulary segmentation aims to develop models that can segment any novel classes beyond a fixed training vocabulary. Here, we evaluate SigLIP 2’s performance on this task. We use Cat-Seg[[11](https://arxiv.org/html/2502.14786v1#bib.bib11)] as a framework and compare performance across different models as proposed in [[45](https://arxiv.org/html/2502.14786v1#bib.bib45)]. We train Cat-Seg on COCO-Stuff-164k[[8](https://arxiv.org/html/2502.14786v1#bib.bib8)] with 172 classes and then test it on various representative datasets with different vocabularies: ADE20k[[74](https://arxiv.org/html/2502.14786v1#bib.bib74), [73](https://arxiv.org/html/2502.14786v1#bib.bib73)] with 847 or 150 classes (A-847/A-150), Pascal Context (PC-459/PC-59)[[43](https://arxiv.org/html/2502.14786v1#bib.bib43)], and Pascal VOC (VOC-20/VOC-21)[[17](https://arxiv.org/html/2502.14786v1#bib.bib17)]. The results can be found in Table[3](https://arxiv.org/html/2502.14786v1#S3.T3 "Table 3 ‣ 3.2 SigLIP 2 as a vision encoder for VLMs ‣ 3 Experiments and results ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features"). We observe that the SigLIP 2 at L/16 improves on SigLIP and even surpasses the much bigger OpenCLIP G/14 model[[27](https://arxiv.org/html/2502.14786v1#bib.bib27)].

### 3.4 Localization tasks

#### 3.4.1 Referring expression comprehension

To probe the referring expression comprehension capabilities of SigLIP 2 on different RefCOCO variants[[29](https://arxiv.org/html/2502.14786v1#bib.bib29), [68](https://arxiv.org/html/2502.14786v1#bib.bib68)] we apply the evaluation protocol from[[62](https://arxiv.org/html/2502.14786v1#bib.bib62)]. We attach a 6-layer transformer decoder to the un-pooled, frozen vision encoder representation via cross-attention and train it from scratch on a mix of all RefCOCO variants (see[[62](https://arxiv.org/html/2502.14786v1#bib.bib62)] for details). The results in Table[5](https://arxiv.org/html/2502.14786v1#S3.T5 "Table 5 ‣ 3.5 Cultural diversity and fairness ‣ 3 Experiments and results ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") show that SigLIP 2 outperforms SigLIP as well as CLIP and pretraining via image captioning (Cap) by a large margin, across resolutions and model sizes. This can be attributed to the decoder-based pretraining, as described in Sec.[2.2](https://arxiv.org/html/2502.14786v1#S2.SS2 "2.2 Training with Sigmoid loss and decoder ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features"). SigLIP 2 is only outperformed LocCa, which we hypothesize might be due to the fact that SigLIP 2 is pretrained on multilingual data. LocCa, on the other hand, is trained on text only from English web sites. Finally, note that we expect significant improvements when using the decoder from pretraining as observed for LocCa.

#### 3.4.2 Open-vocabulary detection

OWL-ViT[[40](https://arxiv.org/html/2502.14786v1#bib.bib40)] is a popular method to adapt CLIP-style vision-language models to open-vocabulary detection. Here, we apply this approach to SigLIP and SigLIP 2 models, closely following the data and optimizer configuration from[[40](https://arxiv.org/html/2502.14786v1#bib.bib40)]. The results in Table[4](https://arxiv.org/html/2502.14786v1#S3.T4 "Table 4 ‣ 3.5 Cultural diversity and fairness ‣ 3 Experiments and results ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") show that SigLIP 2 achieves better performance than SigLIP on the two popular benchmarks COCO[[34](https://arxiv.org/html/2502.14786v1#bib.bib34)] and LVIS[[25](https://arxiv.org/html/2502.14786v1#bib.bib25)]. The relative improvement is most pronounced for the LVIS rare categories. Further, the results here are better than those in[[40](https://arxiv.org/html/2502.14786v1#bib.bib40)] which is likely because [[40](https://arxiv.org/html/2502.14786v1#bib.bib40)] used CLIP rather than SigLIP.

### 3.5 Cultural diversity and fairness

Besides the improvement in model quality in SigLIP 2 compared to its predecessor, SigLIP 2 is also more inclusive in two aspects. First, we follow the recommendations of[[49](https://arxiv.org/html/2502.14786v1#bib.bib49)] and utilize a training mixture comprising both English and multilingual data to enhance cultural diversity. Second, to address potential societal biases in the training data, we integrate the data de-biasing techniques from[[2](https://arxiv.org/html/2502.14786v1#bib.bib2)]. These techniques are applied to mitigate biases in both first-order statistics, such as disparities in gender representation, and second-order statistics, such as biased associations between gender and occupation. Next, we present the evaluation results.

Table 4: Fine-tuned SigLIP and SigLIP 2 for open-vocabulary detection via OWL-ViT[[40](https://arxiv.org/html/2502.14786v1#bib.bib40)].

Table 5:  Comparing SigLIP 2 models with SigLIP and other baselines from the literature on referring expression comprehension (Acc@0.5). For matching model size and sequence length (seq.) SigLIP 2 models outperform SigLIP models substantially. SigLIP 2 is only outperformed by LocCa, which uses the same decoder-based loss, but is trained on captions from English language websites only. 

##### Cultural Diversity

To evaluate for cultural diversity, we report the zero-shot classification accuracy results using Dollar Street[[54](https://arxiv.org/html/2502.14786v1#bib.bib54)], GeoDE[[51](https://arxiv.org/html/2502.14786v1#bib.bib51)], and Google Landmarks Dataset v2 (GLDv2)[[65](https://arxiv.org/html/2502.14786v1#bib.bib65)]. We also include 10-shot geolocalization using Dollar Street and GeoDE, as proposed in[[49](https://arxiv.org/html/2502.14786v1#bib.bib49)]. For zero-shot evaluation on Dollar Street, we implement the methodology outlined in[[54](https://arxiv.org/html/2502.14786v1#bib.bib54)], mapping 96 topics within the dataset to corresponding ImageNet classes. This process results in a subset of 21K images for our analysis.

Fig.[5](https://arxiv.org/html/2502.14786v1#S4.F5 "Figure 5 ‣ 4 Related work ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") shows a set of representative results (full results are shown in Appendix[C](https://arxiv.org/html/2502.14786v1#A3 "Appendix C Full cultural diversity and fairness results ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features")). We observe an improvement in these metrics in SigLIP 2 compared to SigLIP for the same model size and resolution, and the improvements are particularly significant in geolocalization tasks. For instance, 10-shot geolocalization accuracy in GeoDE (region) improves from 36.2% for SigLIP L/16 at 256px to 44.4% in SigLIP 2. Similarly, 0-shot accuracy on Dollar Street improves from 52.1% to 55.2% in the same models.

##### Fairness

In terms of fairness, we report two metrics. The first is “representation bias,” as defined in[[2](https://arxiv.org/html/2502.14786v1#bib.bib2)], which measures the tendency in the model to associate a random object (such as cars) with a particular gender group. As shown in Fig.[6](https://arxiv.org/html/2502.14786v1#S5.F6 "Figure 6 ‣ 5 Conclusion ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features"), SigLIP 2 is _significantly_ better than SigLIP. For instance, while SigLIP L/16 at 256px has a representation bias of about 35.5%—meaning it prefers to associate random images with “men” over “women” more than 85.5% of the time—SigLIP 2 of the same size and resolution has a representation bias of 7.3% only. In addition, larger models tend to exhibit less representation bias than smaller models, in agreement with the earlier findings in[[2](https://arxiv.org/html/2502.14786v1#bib.bib2)].

We also investigate the Dollar Street 0-shot results by income level and the GeoDE results by geographic region as [[49](https://arxiv.org/html/2502.14786v1#bib.bib49)]. However, in this context we only observe very minor benefits, or no benefits when comparing SigLIP and SigLIP 2 models of matching size and resolution (some results shown in Table[9](https://arxiv.org/html/2502.14786v1#A3.T9 "Table 9 ‣ Appendix C Full cultural diversity and fairness results ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features")).

4 Related work
--------------

Contrastive pretraining as popularized by CLIP[[50](https://arxiv.org/html/2502.14786v1#bib.bib50)] and ALIGN[[28](https://arxiv.org/html/2502.14786v1#bib.bib28)] has become the dominant approach for learning high-level, semantic, visual representations that perform well on classification and retrieval, as vision encoders for VLMs[[3](https://arxiv.org/html/2502.14786v1#bib.bib3), [32](https://arxiv.org/html/2502.14786v1#bib.bib32), [48](https://arxiv.org/html/2502.14786v1#bib.bib48), [35](https://arxiv.org/html/2502.14786v1#bib.bib35), [7](https://arxiv.org/html/2502.14786v1#bib.bib7), [39](https://arxiv.org/html/2502.14786v1#bib.bib39), [59](https://arxiv.org/html/2502.14786v1#bib.bib59)] and open-vocabulary tasks including detection[[40](https://arxiv.org/html/2502.14786v1#bib.bib40), [30](https://arxiv.org/html/2502.14786v1#bib.bib30), [41](https://arxiv.org/html/2502.14786v1#bib.bib41)] and segmentation[[14](https://arxiv.org/html/2502.14786v1#bib.bib14), [11](https://arxiv.org/html/2502.14786v1#bib.bib11)]. Besides the original CLIP release, several projects have released open-weight contrastive models[[27](https://arxiv.org/html/2502.14786v1#bib.bib27), [57](https://arxiv.org/html/2502.14786v1#bib.bib57), [71](https://arxiv.org/html/2502.14786v1#bib.bib71), [33](https://arxiv.org/html/2502.14786v1#bib.bib33), [19](https://arxiv.org/html/2502.14786v1#bib.bib19), [66](https://arxiv.org/html/2502.14786v1#bib.bib66)]. At a high level, these works follow training methods that are relatively close to the original CLIP method, mainly [[71](https://arxiv.org/html/2502.14786v1#bib.bib71)] proposing modified loss functions and [[19](https://arxiv.org/html/2502.14786v1#bib.bib19), [66](https://arxiv.org/html/2502.14786v1#bib.bib66)] targeting data quality and filtering.

More generally, a large number of modifications and improvements to contrastive training have been proposed in the literature. [[21](https://arxiv.org/html/2502.14786v1#bib.bib21), [19](https://arxiv.org/html/2502.14786v1#bib.bib19), [66](https://arxiv.org/html/2502.14786v1#bib.bib66), [16](https://arxiv.org/html/2502.14786v1#bib.bib16), [61](https://arxiv.org/html/2502.14786v1#bib.bib61)] study filtering techniques to improve data quality. With a similar motivation, [[18](https://arxiv.org/html/2502.14786v1#bib.bib18), [46](https://arxiv.org/html/2502.14786v1#bib.bib46), [31](https://arxiv.org/html/2502.14786v1#bib.bib31), [38](https://arxiv.org/html/2502.14786v1#bib.bib38)] re-caption training images with VLMs to improve the caption quality and hence the quality of the training signal. Another promising area has been to modify or augment the loss function. [[44](https://arxiv.org/html/2502.14786v1#bib.bib44), [45](https://arxiv.org/html/2502.14786v1#bib.bib45), [38](https://arxiv.org/html/2502.14786v1#bib.bib38)] combine CLIP with self-supervised losses. Another popular approach is to add a language decoder to train with captioning as an auxiliary task[[67](https://arxiv.org/html/2502.14786v1#bib.bib67), [32](https://arxiv.org/html/2502.14786v1#bib.bib32)]. Captioning as a standalone representation learning task has attracted less attention, but can produce visual representations competitive with contrastive training[[64](https://arxiv.org/html/2502.14786v1#bib.bib64), [60](https://arxiv.org/html/2502.14786v1#bib.bib60), [62](https://arxiv.org/html/2502.14786v1#bib.bib62), [20](https://arxiv.org/html/2502.14786v1#bib.bib20)].

![Image 5: Refer to caption](https://arxiv.org/html/2502.14786v1/x5.png)

Figure 5: 10-shot and 0-shot accuracy for geographically diverse object classification tasks (Dollar Street, GeoDE), as well as geolocalization (GeoDE country/region) and landmark localization (GLDv2) tasks. SigLIP 2 consistently performs better than SigLIP (see Table[8](https://arxiv.org/html/2502.14786v1#A3.T8 "Table 8 ‣ Appendix C Full cultural diversity and fairness results ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features") for additional results).

5 Conclusion
------------

In this work, we introduced SigLIP 2, a family of open-weight multilingual vision-language encoders that builds on the success of SigLIP. By incorporating a combination of techniques such as decoder-based pretraining, self-supervised losses, and active data curation, SigLIP 2 achieves significant improvements in zero-shot classification, transfer performance as a vision encoder in VLMs, and in localization and dense prediction tasks. Furthermore, thanks to training on multilingual data and applying de-biasing filters, SigLIP 2 attains more balanced quality across culturally diverse data. Finally, the NaFlex variant enables the model to support multiple resolutions with a single model checkpoint, while preserving the native image aspect ratio. We hope that our SigLIP 2 release will enable many exciting applications within the open-source community.

![Image 6: Refer to caption](https://arxiv.org/html/2502.14786v1/x6.png)

Figure 6: Representation bias (association of random objects with gender; lower is better) for different models.

##### Acknowledgments

We would like to thank Josip Djolonga, Neil Houlsby, Andre Araujo, Kevis Maninis, and Phoebe Kirk for discussions and feedback on this project. We also thank Joan Puigcerver, André Susano Pinto, and Alex Bewley for infrastructure contributions to the big_vision code base, which were helpful for this project.

\nobibliography

*

References
----------

*   Alabdulmohsin et al. [2023] I.Alabdulmohsin, X.Zhai, A.Kolesnikov, and L.Beyer. Getting vit in shape: Scaling laws for compute-optimal model design. In _NeurIPS_, 2023. 
*   Alabdulmohsin et al. [2024] I.Alabdulmohsin, X.Wang, A.P. Steiner, P.Goyal, A.D’Amour, and X.Zhai. Clip the bias: How useful is balancing data in multimodal learning? In _ICLR_, 2024. 
*   Bai et al. [2023] J.Bai, S.Bai, S.Yang, S.Wang, S.Tan, P.Wang, J.Lin, C.Zhou, and J.Zhou. Qwen-VL: A versatile vision-language model for understanding, localization, text reading, and beyond. _arXiv:2308.12966_, 2023. 
*   Barbu et al. [2019] A.Barbu, D.Mayo, J.Alverio, W.Luo, C.Wang, D.Gutfreund, J.Tenenbaum, and B.Katz. Objectnet: A large-scale bias-controlled dataset for pushing the limits of object recognition models. _NeurIPS_, 2019. 
*   Beyer et al. [2020] L.Beyer, O.J. Hénaff, A.Kolesnikov, X.Zhai, and A.v.d. Oord. Are we done with imagenet? _arXiv:2006.07159_, 2020. 
*   Beyer et al. [2023] L.Beyer, P.Izmailov, A.Kolesnikov, M.Caron, S.Kornblith, X.Zhai, M.Minderer, M.Tschannen, I.Alabdulmohsin, and F.Pavetic. Flexivit: One model for all patch sizes. In _CVPR_, 2023. 
*   Beyer et al. [2024] L.Beyer, A.Steiner, A.S. Pinto, A.Kolesnikov, X.Wang, D.Salz, M.Neumann, I.Alabdulmohsin, M.Tschannen, E.Bugliarello, T.Unterthiner, D.Keysers, S.Koppula, F.Liu, A.Grycner, A.Gritsenko, N.Houlsby, M.Kumar, K.Rong, J.Eisenschlos, R.Kabra, M.Bauer, M.Bošnjak, X.Chen, M.Minderer, P.Voigtlaender, I.Bica, I.Balazevic, J.Puigcerver, P.Papalampidi, O.Henaff, X.Xiong, R.Soricut, J.Harmsen, and X.Zhai. PaliGemma: A versatile 3B VLM for transfer. _arXiv:2407.07726_, 2024. 
*   Caesar et al. [2018] H.Caesar, J.Uijlings, and V.Ferrari. Coco-stuff: Thing and stuff classes in context. In _CVPR_, 2018. 
*   Caron et al. [2021] M.Caron, H.Touvron, I.Misra, H.Jégou, J.Mairal, P.Bojanowski, and A.Joulin. Emerging properties in self-supervised vision transformers. In _CVPR_, pages 9650–9660, 2021. 
*   Chen et al. [2022] X.Chen, X.Wang, S.Changpinyo, A.J. Piergiovanni, P.Padlewski, D.Salz, S.Goodman, A.Grycner, B.Mustafa, L.Beyer, A.Kolesnikov, J.Puigcerver, N.Ding, K.Rong, H.Akbari, G.Mishra, L.Xue, A.Thapliyal, J.Bradbury, W.Kuo, M.Seyedhosseini, C.Jia, B.K. Ayan, C.Riquelme, A.Steiner, A.Angelova, X.Zhai, N.Houlsby, and R.Soricut. PaLI: A jointly-scaled multilingual language-image model. _arXiv:2209.06794_, 2022. 
*   Cho et al. [2024] S.Cho, H.Shin, S.Hong, A.Arnab, P.H. Seo, and S.Kim. Cat-seg: Cost aggregation for open-vocabulary semantic segmentation. In _CVPR_, pages 4113–4123, 2024. 
*   Dehghani et al. [2024] M.Dehghani, B.Mustafa, J.Djolonga, J.Heek, M.Minderer, M.Caron, A.Steiner, J.Puigcerver, R.Geirhos, I.M. Alabdulmohsin, et al. Patch n’pack: NaViT, a vision transformer for any aspect ratio and resolution. _NeurIPS_, 2024. 
*   Deng et al. [2009] J.Deng, W.Dong, R.Socher, L.-J. Li, K.Li, and L.Fei-Fei. Imagenet: A large-scale hierarchical image database. In _CVPR_, pages 248–255, 2009. 
*   Ding et al. [2022] J.Ding, N.Xue, G.-S. Xia, and D.Dai. Decoupling zero-shot semantic segmentation. In _CVPR_, pages 11583–11592, 2022. 
*   Dosovitskiy et al. [2021] A.Dosovitskiy, L.Beyer, A.Kolesnikov, D.Weissenborn, X.Zhai, T.Unterthiner, M.Dehghani, M.Minderer, G.Heigold, S.Gelly, J.Uszkoreit, and N.Houlsby. An image is worth 16x16 words: Transformers for image recognition at scale. In _ICLR_, 2021. 
*   Evans et al. [2024] T.Evans, N.Parthasarathy, H.Merzic, and O.J. Henaff. Data curation via joint example selection further accelerates multimodal learning. In _NeurIPS Datasets and Benchmarks Track_, 2024. 
*   Everingham et al. [2010] M.Everingham, L.Van Gool, C.K. Williams, J.Winn, and A.Zisserman. The pascal visual object classes (voc) challenge. _IJCV_, 2010. 
*   Fan et al. [2023] L.Fan, D.Krishnan, P.Isola, D.Katabi, and Y.Tian. Improving clip training with language rewrites. _NeurIPS_, pages 35544–35575, 2023. 
*   Fang et al. [2024] A.Fang, A.M. Jose, A.Jain, L.Schmidt, A.T. Toshev, and V.Shankar. Data filtering networks. In _ICLR_, 2024. 
*   Fini et al. [2024] E.Fini, M.Shukor, X.Li, P.Dufter, M.Klein, D.Haldimann, S.Aitharaju, V.G.T. da Costa, L.Béthune, Z.Gan, A.T. Toshev, M.Eichner, M.Nabi, Y.Yang, J.M. Susskind, and A.El-Nouby. Multimodal autoregressive pre-training of large vision encoders. _arXiv:2411.14402_, 2024. 
*   Gadre et al. [2024] S.Y. Gadre, G.Ilharco, A.Fang, J.Hayase, G.Smyrnis, T.Nguyen, R.Marten, M.Wortsman, D.Ghosh, J.Zhang, et al. Datacomp: In search of the next generation of multimodal datasets. _NeurIPS_, 36, 2024. 
*   Gemma Team [2024a] Gemma Team. Gemma: Open models based on gemini research and technology. _arXiv:2403.08295_, 2024a. 
*   Gemma Team [2024b] Gemma Team. Gemma 2: Improving open language models at a practical size. _arXiv:2408.00118_, 2024b. 
*   Google Cloud [20xx] Google Cloud. Introduction to Cloud TPU. [https://cloud.google.com/tpu/docs/intro-to-tpu](https://cloud.google.com/tpu/docs/intro-to-tpu), 20xx. Accessed: 2024-07-04. 
*   Gupta et al. [2019] A.Gupta, P.Dollar, and R.Girshick. Lvis: A dataset for large vocabulary instance segmentation. In _CVPR_, pages 5356–5364, 2019. 
*   Hsu et al. [2021] T.-Y. Hsu, C.L. Giles, and T.-H. Huang. Scicap: Generating captions for scientific figures. _arXiv:2110.11624_, 2021. 
*   Ilharco et al. [2021] G.Ilharco, M.Wortsman, R.Wightman, C.Gordon, N.Carlini, R.Taori, A.Dave, V.Shankar, H.Namkoong, J.Miller, H.Hajishirzi, A.Farhadi, and L.Schmidt. OpenCLIP, 2021. 
*   Jia et al. [2021] C.Jia, Y.Yang, Y.Xia, Y.Chen, Z.Parekh, H.Pham, Q.V. Le, Y.Sung, Z.Li, and T.Duerig. Scaling up visual and vision-language representation learning with noisy text supervision. In _ICML_, 2021. 
*   Kazemzadeh et al. [2014] S.Kazemzadeh, V.Ordonez, M.Matten, and T.Berg. ReferItGame: Referring to objects in photographs of natural scenes. In _EMNLP_, Oct. 2014. 
*   Kuo et al. [2023] W.Kuo, Y.Cui, X.Gu, A.Piergiovanni, and A.Angelova. Open-vocabulary object detection upon frozen vision and language models. In _ICLR_, 2023. 
*   Lai et al. [2024] Z.Lai, H.Zhang, B.Zhang, W.Wu, H.Bai, A.Timofeev, X.Du, Z.Gan, J.Shan, C.-N. Chuah, Y.Yang, and M.Cao. VeCLIP: Improving clip training via visual-enriched captions. _arXiv:2310.07699_, 2024. 
*   Li et al. [2023a] J.Li, D.Li, S.Savarese, and S.C.H. Hoi. BLIP-2: bootstrapping language-image pre-training with frozen image encoders and large language models. In _ICML_, 2023a. 
*   Li et al. [2023b] X.Li, Z.Wang, and C.Xie. Clipa-v2: Scaling clip training with 81.1% zero-shot imagenet accuracy within a $10,000 budget; an extra $4,000 unlocks 81.8% accuracy. _arXiv:2306.15658_, 2023b. 
*   Lin et al. [2014] T.Lin, M.Maire, S.J. Belongie, L.D. Bourdev, R.B. Girshick, J.Hays, P.Perona, D.Ramanan, P.Doll’a r, and C.L. Zitnick. Microsoft COCO: common objects in context. _arXiv:1405.0312_, 2014. 
*   Liu et al. [2023] H.Liu, C.Li, Q.Wu, and Y.J. Lee. Visual instruction tuning. In _NeurIPS_, 2023. 
*   Long et al. [2023] S.Long, S.Qin, D.Panteleev, A.Bissacco, Y.Fujii, and M.Raptis. ICDAR 2023 competition on hierarchical text detection and recognition. In _ICDAR_, 2023. 
*   Loshchilov et al. [2017] I.Loshchilov, F.Hutter, et al. Fixing weight decay regularization in adam. _arXiv preprint arXiv:1711.05101_, 5, 2017. 
*   Maninis et al. [2025] K.-K. Maninis, K.Chen, S.Ghosh, A.Karpur, K.Chen, Y.Xia, B.Cao, D.Salz, G.Han, J.Dlabal, et al. TIPS: Text-image pretraining with spatial awareness. In _ICLR_, 2025. 
*   McKinzie et al. [2024] B.McKinzie, Z.Gan, J.Fauconnier, S.Dodge, B.Zhang, P.Dufter, D.Shah, X.Du, F.Peng, F.Weers, A.Belyi, H.Zhang, K.Singh, D.Kang, A.Jain, H.Hè, M.Schwarzer, T.Gunter, X.Kong, A.Zhang, J.Wang, C.Wang, N.Du, T.Lei, S.Wiseman, G.Yin, M.Lee, Z.Wang, R.Pang, P.Grasch, A.Toshev, and Y.Yang. MM1: methods, analysis & insights from multimodal LLM pre-training. _arXiv:2403.09611_, 2024. 
*   Minderer et al. [2022] M.Minderer, A.Gritsenko, A.Stone, M.Neumann, D.Weissenborn, A.Dosovitskiy, A.Mahendran, A.Arnab, M.Dehghani, Z.Shen, et al. Simple open-vocabulary object detection. In _ECCV_, pages 728–755, 2022. 
*   Minderer et al. [2023] M.Minderer, A.A. Gritsenko, and N.Houlsby. Scaling open-vocabulary object detection. In _NeurIPS_, 2023. 
*   Mindermann et al. [2022] S.Mindermann, J.M. Brauner, M.T. Razzak, M.Sharma, A.Kirsch, W.Xu, B.Höltgen, A.N. Gomez, A.Morisot, S.Farquhar, et al. Prioritized training on points that are learnable, worth learning, and not yet learnt. In _ICML_, pages 15630–15649, 2022. 
*   Mottaghi et al. [2014] R.Mottaghi, X.Chen, X.Liu, N.-G. Cho, S.-W. Lee, S.Fidler, R.Urtasun, and A.Yuille. The role of context for object detection and semantic segmentation in the wild. In _CVPR_, 2014. 
*   Mu et al. [2022] N.Mu, A.Kirillov, D.Wagner, and S.Xie. SLIP: Self-supervision meets language-image pre-training. In _ECCV_, pages 529–544, 2022. 
*   Naeem et al. [2024] M.F. Naeem, Y.Xian, X.Zhai, L.Hoyer, L.Van Gool, and F.Tombari. SILC: Improving vision language pretraining with self-distillation. In _ECCV_, pages 38–55, 2024. 
*   Nguyen et al. [2024] T.Nguyen, S.Y. Gadre, G.Ilharco, S.Oh, and L.Schmidt. Improving multimodal datasets with image captioning. _NeurIPS_, 36, 2024. 
*   Oquab et al. [2024] M.Oquab, T.Darcet, T.Moutakanni, H.V. Vo, M.Szafraniec, V.Khalidov, P.Fernandez, D.Haziza, F.Massa, A.El-Nouby, et al. Dinov2: Learning robust visual features without supervision. _TMLR_, 2024. 
*   Peng et al. [2023] Z.Peng, W.Wang, L.Dong, Y.Hao, S.Huang, S.Ma, and F.Wei. Kosmos-2: Grounding multimodal large language models to the world. _arXiv:2306.14824_, 2023. 
*   Pouget et al. [2024] A.Pouget, L.Beyer, E.Bugliarello, X.Wang, A.P. Steiner, X.Zhai, and I.Alabdulmohsin. No filter: Cultural and socioeconomic diversityin contrastive vision-language models. _arXiv:2405.13777_, 2024. 
*   Radford et al. [2021] A.Radford, J.W. Kim, C.Hallacy, A.Ramesh, G.Goh, S.Agarwal, G.Sastry, A.Askell, P.Mishkin, J.Clark, G.Krueger, and I.Sutskever. Learning transferable visual models from natural language supervision. In _ICML_, 2021. 
*   Ramaswamy et al. [2024] V.V. Ramaswamy, S.Y. Lin, D.Zhao, A.Adcock, L.van der Maaten, D.Ghadiyaram, and O.Russakovsky. Geode: a geographically diverse evaluation dataset for object recognition. _NeurIPS_, 36, 2024. 
*   Ranftl et al. [2021] R.Ranftl, A.Bochkovskiy, and V.Koltun. Vision transformers for dense prediction. In _CVPR_, pages 12179–12188, 2021. 
*   Recht et al. [2019] B.Recht, R.Roelofs, L.Schmidt, and V.Shankar. Do imagenet classifiers generalize to imagenet? In _ICML_, pages 5389–5400, 2019. 
*   Rojas et al. [2022] W.A.G. Rojas, S.Diamos, K.R. Kini, D.Kanter, V.J. Reddi, and C.Coleman. The dollar street dataset: Images representing the geographic and socioeconomic diversity of the world. In _NeurIPS Datasets and Benchmarks Track_, 2022. 
*   Sidorov et al. [2020] O.Sidorov, R.Hu, M.Rohrbach, and A.Singh. TextCaps: A dataset for image captioning with reading comprehension. In _ECCV_, 2020. 
*   Steiner et al. [2024] A.Steiner, A.S. Pinto, M.Tschannen, D.Keysers, X.Wang, Y.Bitton, A.Gritsenko, M.Minderer, A.Sherbondy, S.Long, et al. Paligemma 2: A family of versatile vlms for transfer. _arXiv:2412.03555_, 2024. 
*   Sun et al. [2023] Q.Sun, Y.Fang, L.Wu, X.Wang, and Y.Cao. EVA-CLIP: Improved training techniques for clip at scale. _arXiv:2303.15389_, 2023. 
*   Thapliyal et al. [2022] A.V. Thapliyal, J.Pont Tuset, X.Chen, and R.Soricut. Crossmodal-3600: A massively multilingual multimodal evaluation dataset. In _EMNLP_, 2022. 
*   Tong et al. [2024] S.Tong, E.Brown, P.Wu, S.Woo, M.Middepogu, S.C. Akula, J.Yang, S.Yang, A.Iyer, X.Pan, A.Wang, R.Fergus, Y.LeCun, and S.Xie. Cambrian-1: A Fully Open, Vision-Centric Exploration of Multimodal LLMs. _arXiv:2406.16860_, 2024. 
*   Tschannen et al. [2023] M.Tschannen, M.Kumar, A.Steiner, X.Zhai, N.Houlsby, and L.Beyer. Image captioners are scalable vision learners too. In _NeurIPS_, 2023. 
*   Udandarao et al. [2024] V.Udandarao, N.Parthasarathy, M.F. Naeem, T.Evans, S.Albanie, F.Tombari, Y.Xian, A.Tonioni, and O.J. Hénaff. Active data curation effectively distills large-scale multimodal models. _arXiv:2411.18674_, 2024. 
*   Wan et al. [2024] B.Wan, M.Tschannen, Y.Xian, F.Pavetic, I.Alabdulmohsin, X.Wang, A.S. Pinto, A.Steiner, L.Beyer, and X.Zhai. LocCa: Visual pretraining with location-aware captioners. In _NeurIPS_, 2024. 
*   Wang et al. [2021] B.Wang, G.Li, X.Zhou, Z.Chen, T.Grossman, and Y.Li. Screen2words: Automatic mobile ui summarization with multimodal learning. In _Symposium on User Interface Software and Technology_, 2021. 
*   Wang et al. [2022] Z.Wang, J.Yu, A.W. Yu, Z.Dai, Y.Tsvetkov, and Y.Cao. SimVLM: Simple visual language model pretraining with weak supervision. In _ICLR_, 2022. 
*   Weyand et al. [2020] T.Weyand, A.Araujo, B.Cao, and J.Sim. Google landmarks dataset v2-a large-scale benchmark for instance-level recognition and retrieval. In _CVPR_, pages 2575–2584, 2020. 
*   Xu et al. [2024] H.Xu, S.Xie, X.Tan, P.-Y. Huang, R.Howes, V.Sharma, S.-W. Li, G.Ghosh, L.Zettlemoyer, and C.Feichtenhofer. Demystifying clip data. In _ICLR_, 2024. 
*   Yu et al. [2022] J.Yu, Z.Wang, V.Vasudevan, L.Yeung, M.Seyedhosseini, and Y.Wu. CoCa: Contrastive captioners are image-text foundation models. _TMLR_, 2022. 
*   Yu et al. [2016] L.Yu, P.Poirson, S.Yang, A.C. Berg, and T.L. Berg. Modeling context in referring expressions. In _ECCV_, pages 69–85, 2016. 
*   Zhai et al. [2022a] X.Zhai, A.Kolesnikov, N.Houlsby, and L.Beyer. Scaling vision transformers. _CVPR_, 2022a. 
*   Zhai et al. [2022b] X.Zhai, X.Wang, B.Mustafa, A.Steiner, D.Keysers, A.Kolesnikov, and L.Beyer. Lit: Zero-shot transfer with locked-image text tuning. In _CVPR_, 2022b. 
*   Zhai et al. [2023] X.Zhai, B.Mustafa, A.Kolesnikov, and L.Beyer. Sigmoid loss for language image pre-training. In _ICCV_, 2023. 
*   Zhao et al. [2023] Y.Zhao, A.Gu, R.Varma, L.Luo, C.Huang, M.Xu, L.Wright, H.Shojanazeri, M.Ott, S.Shleifer, A.Desmaison, C.Balioglu, P.Damania, B.Nguyen, G.Chauhan, Y.Hao, A.Mathews, and S.Li. Pytorch FSDP: experiences on scaling fully sharded data parallel. _VLDB_, 2023. 
*   Zhou et al. [2017] B.Zhou, H.Zhao, X.Puig, S.Fidler, A.Barriuso, and A.Torralba. Scene parsing through ade20k dataset. In _CVPR_, 2017. 
*   Zhou et al. [2019] B.Zhou, H.Zhao, X.Puig, T.Xiao, S.Fidler, A.Barriuso, and A.Torralba. Semantic understanding of scenes through the ade20k dataset. _IJCV_, 2019. 
*   Zhou et al. [2022] J.Zhou, C.Wei, H.Wang, W.Shen, C.Xie, A.Yuille, and T.Kong. Image BERT pre-training with online tokenizer. In _ICLR_, 2022. 

Appendix
--------

Appendix A Full PaliGemma results
---------------------------------

Table 6: The first three columns compare Large-sized models with 256 tokens each (that’s 224px for the AIMv2 model with patch size 14, and 256px for the SigLIP models with patch size 16). The last four columns compare So400M-sized SigLIP models with patch size 14 at two different resolutions (and hence tokens). Same data as in Figure[4](https://arxiv.org/html/2502.14786v1#S2.F4 "Figure 4 ‣ 2.5 Distillation via active data curation ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features").

Appendix B Full NaFlex results
------------------------------

Table 7: Comparing the NaFlex (supporting native aspect ratio and variable sequence length (Seq.)) and the standard square-input SigLIP variants which use a separate checkpoint per sequence length. Numerical data corresponding to the plots in Fig.[3](https://arxiv.org/html/2502.14786v1#S2.F3 "Figure 3 ‣ 2.4.2 Variable aspect and resolution (NaFlex) ‣ 2.4 Adaptation to different resolutions ‣ 2 Training recipe ‣ SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features"). TC: TextCaps, HT: HierText, SC: SciCap, S2W: Screen2Words.

Appendix C Full cultural diversity and fairness results
-------------------------------------------------------

Table 8: 10-shot and 0-shot accuracy for geographically diverse object classification tasks (Dollar Street, GeoDE), as well as geolocalization (GeoDE country/region) and landmark localization (GLDv2) tasks. SigLIP 2 consistently outperforms SigLIP on most benchmarks.

ViT Res.Model Disparity Rep. bias
B/32 256 SigLIP 2 33.3 16.6
B/16 224 SigLIP 31.2 36.6
SigLIP 2 31.0 17.2
256 SigLIP 30.2 35.6
SigLIP 2 29.7 19.4
384 SigLIP 30.9 35.8
SigLIP 2 30.6 18.0
512 SigLIP 31.5 35.4
SigLIP 2 30.8 20.0
L/16 256 SigLIP 32.0 35.5
SigLIP 2 31.1 7.3
384 SigLIP 32.0 34.8
SigLIP 2 30.4 6.6
512 SigLIP 2 29.2 6.8
So400m/14 224 SigLIP 30.5 33.3
SigLIP 2 29.7 7.4
384 SigLIP 29.2 33.9
SigLIP 2 28.1 7.5
So400m/16 256 SigLIP 2 28.4 7.2
mSigLIP 31.6 37.3
384 SigLIP 2 29.0 11.0
512 SigLIP 2 28.2 10.8
g-opt/16 256 SigLIP 2 28.1 7.9
384 SigLIP 2 28.3 4.9

Table 9: Disparity: Corresponds to the maximum difference in 0-shot accuracy on Dollar Street when disaggregating the accuracy by income level: We observe that SigLIP 2 slightly reduces the performance disparity. Rep. bias: Representation bias; lower values are better. SigLIP2, which is trained on de-biased data, exhibits significantly reduced representation bias than its predecessor. In addition, larger models are better than smaller models, in agreement with the earlier findings in[[2](https://arxiv.org/html/2502.14786v1#bib.bib2)].


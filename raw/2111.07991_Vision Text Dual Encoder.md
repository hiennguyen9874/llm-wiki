# LiT : Zero-Shot Transfer with Locked-image text Tuning

Xiaohua Zhai\*<sup>†</sup> Xiao Wang\* Basil Mustafa\* Andreas Steiner\* Daniel Keysers Alexander Kolesnikov Lucas Beyer\*<sup>†</sup>  
Google Research, Brain Team, Zürich

## Abstract

*This paper presents contrastive-tuning, a simple method employing contrastive training to align image and text models while still taking advantage of their pre-training. In our empirical study we find that locked pre-trained image models with unlocked text models work best. We call this instance of contrastive-tuning “Locked-image Tuning” (LiT), which just teaches a text model to read out good representations from a pre-trained image model for new tasks. A LiT model gains the capability of zero-shot transfer to new vision tasks, such as image classification or retrieval. The proposed LiT is widely applicable; it works reliably with multiple pre-training methods (supervised and unsupervised) and across diverse architectures (ResNet, Vision Transformers and MLP-Mixer) using three different image-text datasets. With the transformer-based pre-trained ViT-g/14 model, the LiT model achieves 85.2% zero-shot transfer accuracy on the ImageNet test set, and 82.5% on the challenging out-of-distribution ObjectNet test set.*

## 1. Introduction

Transfer learning [45] has been a successful paradigm in computer vision [33, 34, 43]. Zero-shot learning [36, 37, 66] is an alternative approach aiming to develop models that can handle a new task without task-specific data or adaptation protocols. Recently it was demonstrated that web-sourced paired image-text data can be used to pre-train strong models for zero-shot transfer [31, 46]. Zero-shot transfer differs from classical zero-shot learning in that the transfer setup may see relevant supervised information during pre-training; it is zero-shot insofar as no supervised examples are used during the transfer protocol. GPT-3 [4] explored a similar zero-shot transfer setup using model prompting via natural language.

In [31, 46] authors propose a contrastive learning framework where an image model (or image tower) is trained simultaneously with a text model (or text tower). Both towers are trained to minimize a contrastive loss, which encourages

\*equal technical contribution, <sup>†</sup>equal advising

Figure 1. Comparison to the previous SOTA methods. **Left:** results on public YFCC100m subset, with from-scratch, fine-tuned from a pre-trained image model, and LiT with a pre-trained image model. The proposed LiT improves over 30% ImageNet zero-shot transfer accuracy on YFCC100m subset. **Right:** results on privately gathered data, LiT halves the gap between previous from-scratch methods CLIP [46], ALIGN [31] and supervised fine-tuning [13, 69].

representations of paired images and texts to be similar, and representations of non-paired images and texts to be dissimilar. At test time, the resulting model can be used for zero-shot image classification by comparing the image embedding with embeddings of textual class descriptions.

In this paper, we adopt a contrastive learning framework and propose a more data- and compute-efficient strategy named *contrastive-tuning*. The key idea is to tune the text tower using image-text data, while using a pre-trained, strong image model as the image tower. During training, both towers’ weights can be locked or unlocked, leading to different design choices that are illustrated in Figure 2. Specifically, we find that locking the image tower works best, as shown in Figure 1. We call this specific instance of contrastive-tuning “Locked-image Tuning” (LiT), which just teaches a text model to read out suitable representations from a pre-trained image model. LiT achieves better results compared with the from-scratch CLIP [46] or ALIGN [31] models. With the pre-trained model ViT-g/14 [69], LiT achieves 85.2% zero-shot transfer accuracy on ImageNet, halving the gap between previous best zero-shot transfer re-sults [31,46] and supervised fine-tuning results [13,69]. The best LiT model also sets new state-of-the-art on several out-of-distribution (OOD) ImageNet test variants, compared to previous supervised and unsupervised methods. For example, it achieves 82.5% accuracy on the challenging Object-Net test set [1], outperforming the previous state-of-the-art method [46] by 10.2%.

We believe the reason that LiT works well lies in its decoupling of data sources and techniques for learning image descriptors and vision-language alignment. Image-text data can be great for learning correspondences between natural language and the visual world, but, at the same time, it may not be precise and clean enough to result in state-of-the-art image descriptors. In this paper we carefully investigate this hypothesis and support it with empirical evidence.

The proposed LiT works with both supervised and self-supervised pre-trained models. We verify LiT across three image-text datasets, with Vision Transformer [21], ResNet [33], and MLP-Mixer [61] architectures. We also show that with a self-supervised pre-trained model, i.e. DINO [5] or MoCo-v3 [11], LiT achieves better performance compared to from-scratch contrastive-learning.

Another contribution of this paper is the proposed recipe for high-performance zero-shot models that can be trained using only modest computational resources and public datasets. By re-using already pre-trained models (e.g. publicly released in the literature), the computational resources used to train the image models can be amortized. Furthermore, we explore publicly available datasets such as YFCC100m [60] and CC12M [6]. Combined with the computational efficiency, we hope to facilitate contributions from a wider audience to research in zero-shot transfer.<sup>2</sup>

## 2. Related work

This work is closely related to a vast amount of literature on *transfer learning* in vision [45,59]. The main idea of transfer learning is to leverage already pre-trained models to solve a new task better and faster, as opposed to less efficient training from-scratch. This paradigm is usually implemented as a two-step procedure: (1) pre-train (once) an initial model on a large dataset of images that are (weakly)-labeled or using self-supervised losses and (2) fine-tune the pre-trained model for a task of interest using supervised data. In the context of modern deep learning, many earlier works [20,33,34,48] used supervised pre-training to learn transferrable feature representations, with the Vision Transformer revisiting and improving this approach [21,69]. It was shown that scaling up model and dataset sizes simultaneously leads to dramatic improvements in transfer effectiveness [21,33,69] and robustness [18]. Crucially, large

pre-trained models exhibit outstanding capabilities in learning in the low-data (few-shot) regime [9,21,33].

Still, collecting task-specific data and fine-tuning large pre-trained models remains time-consuming and potentially costly in many realistic scenarios. *Zero-shot transfer* is an alternative paradigm that sidesteps the fine-tuning stage entirely and performs classification solely based on a description of the target classes. Early works demonstrated how to train zero-shot classifiers based on attributes [36] or numerical descriptors [37]. Another approach, which we adopt in this work, is to learn an alignment between image and text embedding spaces [7,16,22,23,32,71]. This approach has demonstrated that with modern architectures, contrastive learning, and large data sources it is possible to obtain performance that is competitive with the classical two-step approach that involves fine-tuning on the downstream data [31,46]. Other efforts in this direction explore image-text alignment or masked language (or image region) modeling [12,38]. The models have been applied to diverse downstream tasks, including visual question answering [24], visual commonsense reasoning [68] and image captioning [41,42,56].

*Contrastive learning* techniques are another closely-related research direction. The high-level idea of a contrastive loss is to simplify the learning task by requiring the model to select the correct answers out of a finite set of carefully designed options. Intuitively, this simplification of the task may encourage the model to focus on high-level information in an image instead of generic information, resulting in high quality learned representations. Early works that investigate very specific instances of this idea include [19,44]. More recently, contrastive learning was formulated and studied in more general settings [8,25,62], leading to very promising results. Finally, [31,46] use contrastive learning for learning from image-text data and derive state-of-the-art zero-shot image classifiers.

## 3. Methods

### 3.1. Contrastive pre-training

Collections of images (potentially noisily) paired with free-form text descriptions have emerged as a powerful resource for training visual models. The key advantage therein is that it is not limited by a finite set of predefined categories and instead describes images using open-ended natural language. As a result, models learned from this data can serve as zero-shot learners for a wide range of tasks, e.g. classification and image/text retrieval.

Contrastive pre-training is one particularly effective approach for training models from image-text data, which was recently proven to work well in practice [31,46]. We take a closer look at this approach and propose a simple, yet highly effective recipe to significantly enhance contrastive

<sup>2</sup>Public LiT models available at [https://github.com/google-research/vision\\_transformer#lit-models](https://github.com/google-research/vision_transformer#lit-models). We provide pre-training code in the `big_vision` codebase [3].Figure 2. Design choices for contrastive-tuning on image-text data. Two letters are introduced to represent the image tower and text tower setups.  $L$  stands for locked variables and initialized from a pre-trained model,  $U$  stands for unlocked and initialized from a pre-trained model,  $u$  stands for unlocked and randomly initialized.  $Lu$  is named as “Locked-image Tuning” (LiT).

pre-training from image-text data.

The key idea behind the contrastive pre-training approach is to learn two embedding models: an image model and a text model, both of which produce representations of the same dimensionality. These models are trained using a contrastive loss. This loss encourages corresponding image-text pairs to have similar embeddings and, conversely, encourages non-corresponding pairs to have distinct embeddings. See [46, 71] for the detailed discussion of the contrastive loss function.

An important detail of this loss function is whether the loss is computed on each accelerator device independently and then accumulated or computed jointly across all devices. We ablate this design choice (Appendix F) and confirm that the latter [31, 46] consistently results in better performance. We therefore use the global loss in all our experiments and ablations.

After image and text towers are trained, they can be readily used for zero-shot classification: class names or descriptions are embedded with the text model. Then, for a given image the label is selected that has the embedding closest to the embedding of the image. This approach also works for image-text retrieval.

### 3.2. Contrastive-tuning

Contrastive pre-training can be viewed as learning two tasks at the same time: (1) learning an image embedding and (2) learning a text embedding to align with the image embedding space. While contrastive pre-training on image-text data works well for solving both of these tasks simultaneously, it may be not the optimal approach.

When not using contrastive pre-training on image-text data, a standard approach to learning image embeddings is to use a large and relatively clean dataset of (semi-)manually labeled images. Large scale and high quality of such data result in state-of-the-art image embeddings.

Some dataset choices for learning powerful image embeddings are ImageNet-21k [15], JFT-300M [57].

However, this common approach has a clear weakness: it is limited to a *predefined set of categories* and, thus, the resulting models can only reason about these categories. In contrast, image-text data does not have this limitation, as it learns from the *free-form text* that potentially spans a broad range of real-life concepts. On the other hand, image-text data that is available may be of lower quality (for learning image embeddings) than carefully curated datasets.

We propose *contrastive-tuning* to combine advantages of both sources of data. One specific way of doing this is to initialise the contrastive pre-training with an image model that was *already pre-trained* using cleaner (semi-)manually labeled data. This way the image-text alignment is learned independently of image embedding, enabling benefit from both data sources.

Beyond using supervised pre-trained image models, the proposed contrastive-tuning is also flexible enough to integrate any models that can produce meaningful representations. We verify this in our experiments using self-supervised pre-trained image models.

Similar lines of reasoning can also be applied to the text tower, as there are many powerful pretrained models that use text-specific data sources and learning techniques.

### 3.3. Design choices and Locked-image Tuning

Introducing pre-trained image or text models into the contrastive learning setting involves several design choices. First, each tower (image and text) can independently be initialized randomly or from a pre-trained model. For a pre-trained model there are at least two variants: we can lock (freeze) it or allow fine-tuning. Note that there are many choices between these two extremes (e.g. partial freezing of selected layers, or custom learning rates), but they are not investigated in this paper.

Pre-trained image-text models may have different representation sizes, while the contrastive loss expects representations of the same size. To compensate, we add an optional linear projection (head) to each tower, which maps the representations to a common dimensionality. Preliminary investigations with tried MLP-based heads did not yield significant improvements over such a simple linear head.

We introduce a two-character notation to discuss the potential design choices outlined above (see Figure 2). Each character encodes the setting chosen for the image model and the text model (in this order). We define three potential settings:  $L$  (locked weights, a initialized from pre-trained model),  $U$  (unlocked/trainable weights, initialized from a pre-trained model) and  $u$  (unlocked/trainable weights, randomly initialized). For example, the notation  $Lu$  means locked pre-trained image model, and unlocked (trainable) randomly initialized text model. Previous works trainingmodels from scratch [31, 46] are uu. In our experiments we find the Lu setting to work particularly well, so we explicitly name it as *Locked-image Tuning* (LiT $\text{flame}$ ).

## 4. Image-text datasets

**CC12M.** The Conceptual Captions dataset [52] extracts, filters & transforms image & alt-text pairs from web pages. We use the latest 12 million image-text pair version, i.e. CC12M [6]. Due to expired URLs, only 10 million image-text pairs were used for our experiments.

**YFCC100m.** The Yahoo Flickr Creative Commons dataset [60] contains 100 million media objects. Of these, 99.2 million are photos that come with rich metadata including camera info, timestamp, title, description, tags, geolocation, and more. [46] defines and uses a subset of 15 million images that have been filtered for English text of high quality, which we call YFCC100m-CLIP. A detailed investigation of this dataset and how best to use it, including whether to filter it, is presented in Appendix E.

**Our dataset.** We collect 4 billion image and alt-text pairs following the same process as ALIGN [31], with the same image-based filtering but simpler text-based filtering. Appendix L shows that reducing text filtering does not harm performance. To avoid misleading evaluation results, we remove from our dataset near-duplicate images of all splits from all datasets we evaluate on. We do not consider the creation of our dataset a main contribution of this paper; we just simplify the data collection process in ALIGN [31] to demonstrate the efficacy of our methods at scale.

## 5. Experiments

In this section, we first compare LiT $\text{flame}$  to state-of-the-art image-text models. We consider two scenarios: (1) only using public datasets for model training and (2) using privately gathered data. We then present learnings from experimental evaluations of contrastive tuning design choices with various training settings & datasets. We generally perform evaluation on 0-shot ImageNet classification (“0-shot”) and MSCOCO image (“T $\rightarrow$ I”) and text (“I $\rightarrow$ T”) retrieval.

### 5.1. Comparison to the previous state-of-the-art

In this section, we present LiT results on our dataset. The image tower is initialized with a ViT-g/14 model<sup>3</sup> pre-trained on JFT-3B [69], which has been de-duplicated against the downstream tasks. We use 32k batch size, and tune for 18 billion image-text pairs seen (roughly 550k steps). See Appendix C for details.

<sup>3</sup>An earlier version of this paper reported slightly lower numbers with the ViT-g/14 model, e.g. ImageNet accuracy was 84.5% vs 85.2%. We fixed a model loading bug with ViT-g/14 in this version. Other results are not affected.

<table border="1">
<thead>
<tr>
<th>Dataset</th>
<th>Method</th>
<th>INet</th>
<th>INet-v2</th>
<th>INet-R</th>
<th>INet-A</th>
<th>ObjNet</th>
<th>Real</th>
<th>VTAB-N</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="3">Private</td>
<td>CLIP [46]</td>
<td>76.2</td>
<td>70.1</td>
<td>88.9</td>
<td>77.2</td>
<td>72.3</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>ALIGN [31]</td>
<td>76.4</td>
<td>70.1</td>
<td>92.2</td>
<td>75.8</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td><b>LiT</b></td>
<td><b>85.2</b></td>
<td><b>79.8</b></td>
<td><b>94.9</b></td>
<td><b>81.8</b></td>
<td><b>82.5</b></td>
<td>88.6</td>
<td>74.7</td>
</tr>
<tr>
<td rowspan="3">Public</td>
<td>CLIP [46]</td>
<td>31.3</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>OpenCLIP [29]</td>
<td>34.8</td>
<td>30.0</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td><b>LiT</b></td>
<td><b>75.7</b></td>
<td><b>66.6</b></td>
<td>60.4</td>
<td>37.8</td>
<td>54.5</td>
<td>82.1</td>
<td>63.1</td>
</tr>
<tr>
<td>*</td>
<td>ResNet50 [26]</td>
<td>75.8</td>
<td>63.8</td>
<td>36.1</td>
<td>0.5</td>
<td>26.5</td>
<td>82.5</td>
<td>72.6</td>
</tr>
</tbody>
</table>

Table 1. Zero-shot transfer accuracies (%) on ImageNet, five OOD test variants, and seven VTAB-natural tasks. Results are reported on both public datasets and privately gathered data. For reference, we include the ResNet50 model pre-trained on ImageNet, supervised fine-tuned on downstream datasets. We use \* to denote multiple datasets during supervised fine-tuning.

We compare the LiT method with the previous state-of-the-art methods, including CLIP [46] and ALIGN [31]. In Table 1, we report zero-shot classification results on the ImageNet dataset, five out-of-distribution test variants and seven VTAB-natural tasks [70]. Our model significantly outperforms the previous state-of-the-art methods at ImageNet zero-shot classification. The 9% and 8.8% improvement over CLIP and ALIGN, respectively, halves the gap between zero-shot transfer results and supervised fine-tuned results [13, 69].

**Robustness.** We evaluate robustness on ImageNet-v2 [49], -R [27, 64], -A [28], -Real [2], and ObjectNet [1], following CLIP and ALIGN. On all of the OOD variants, our model consistently outperforms the previous models. Notably, the LiT model sets a new state-of-the-art 82.5% accuracy on the ObjectNet test set. The pre-trained ViT-g/14 model [69], achieves 70.5% accuracy on the ObjectNet test set when fine-tuned on ImageNet. This model gets more than 10% improvement when instead locked-image tuned (LiT) on our image-text dataset.

**Diverse downstream tasks.** We evaluate the LiT models on VTAB, consisting of 19 diverse tasks. We report averaged results on seven VTAB-natural tasks in Table 1. The LiT models achieve promising zero-shot results, comparing to the supervised fine-tuned ResNet50 baseline. In Appendix I.2, we present zero-shot transfer details on VTAB, as well as more results and analysis on the specialized tasks and structured tasks.

**Data & compute efficiency.** Figure 1 shows more results when tuning with fewer seen image-text pairs. With LiT the model achieves 81.7% top-1 accuracy on 0-shot ImageNet transfer, with only 300M image-text pairs seen. In comparison, it took the from-scratch method (i.e. CLIP)<table border="1">
<thead>
<tr>
<th>Method</th>
<th>ImgNet</th>
<th>ImgNet-v2</th>
<th>Cifar100</th>
<th>Pets</th>
</tr>
</thead>
<tbody>
<tr>
<td>Lu</td>
<td>70.1</td>
<td>61.7</td>
<td>70.9</td>
<td>88.1</td>
</tr>
<tr>
<td>Uu</td>
<td>57.2</td>
<td>50.2</td>
<td>62.1</td>
<td>74.8</td>
</tr>
<tr>
<td>uu</td>
<td>50.6</td>
<td>43.3</td>
<td>47.9</td>
<td>70.3</td>
</tr>
</tbody>
</table>

Table 2. Evaluation of design choices on our large dataset.

12.8B image-text pairs seen, i.e. 40 times more data pairs, to reach 76.2% top-1 accuracy. With a pre-trained image model, the proposed setup converges significantly faster than the standard from-scratch setups reported in the literature. LiT provides a way to reuse the already pre-trained models in the literature, amortizing the computational resources used to re-generate the image models.

**Results on public datasets.** Given high data efficiency of LiT, we investigate how well it performs when using only smaller, publicly available models and datasets. Specifically, we tune an ImageNet-21k pre-trained ViT-L/16 model [55] on the union of the *YFCC100m-CLIP* and *CC12M* datasets. More details of the training setup are provided in Appendix D. As a result we achieve unprecedented **75.7%** zero-shot transfer on ImageNet, an absolute improvement of 30.9% over the previously reported state-of-the-art result [29] that uses only public data sources. We also obtain strong results on a wide range of robustness datasets and the VTAB-natural tasks, see Table 1.

## 5.2. Evaluation of design choices

**Small-scale thorough investigation.** We first perform an in-depth study on various combinations of the image and text towers being initialized with pre-trained weights and locked (L) or unlocked (U) or being randomly initialized and unlocked (u). We train each setting many times on the YFCC100m-CLIP dataset, varying the total number of steps from 2500 to 60000 in order to understand the setting’s trajectory, and sweeping over learning-rates and weight-decays to avoid being misled. Details can be found in Appendix D. Figure 3 shows the best result for each setting for each duration, i.e. each point on the curves is a separate full run for that duration. It is evident that locking the image tower almost always works best and using a pre-trained image tower significantly helps across the board, whereas using a pre-trained text tower only marginally improves performance, and locking the text tower does not work well.

**This still holds in the near-infinite data regime.** One may hypothesize that locking the pre-trained image tower only helps because the YFCC100m-CLIP dataset is *relatively* small (15 million images, compared to 400M [46] or 1.8B [31]), and that a randomly initialized image tower will eventually outperform a locked one on much larger image-text datasets. The trajectory of the Uu and UU settings in

Figure 3. An in-depth study of the possible locking and initialization settings of LiT on the YFCC100m-CLIP dataset. A pre-trained image tower works best, while pre-training of the text tower only helps a little. These are **not** training curves; each point is the final value reached by a training run of that duration.

Figure 3 may seem to support this expectation.

Maybe surprisingly, experimental results show that this is not the case, and locking the image tower provides benefits even when contrastively tuning on a very large dataset of image-text pairs. Table 2 shows results of contrastive tuning on our dataset of 4 billion images in three settings: Lu, Uu, and uu. Implementation details can be found in Appendix C. The from-scratch method uu unsurprisingly achieves better performance than with smaller datasets such as CC12M and YFCC100m-CLIP.

Initializing the image tower from a pre-trained model provides even better performance and is a relatively straightforward extension of CLIP/ALIGN. Perhaps surprisingly, the frozen setup Lu, achieves even better results. While potentially counter-intuitive, another perspective is that LiT simply learns a text tower that extracts knowledge from a strong image embedder. This flexible & performant setup can turn existing vision backbones into a zero-shot learners, by attaching a text-embedding tower.

**Why is locked (L) better than unlocked (U)?** It is somewhat surprising and counter-intuitive that locking the image tower works better than allowing it to adapt during the contrastive-tuning; Figure 4 gives hints as to why.

The first row shows that locking the image tower leads to substantially worse (contrastive) loss on the dataset used for LiT, while the loss of the locked image variant is substan-Figure 4. Comparing the loss on the dataset used for LiT (top row) to the loss on out-of-distribution (zero-shot) datasets (middle row) and the “representation quality” as measured by linear few-shot evaluation on the pre-logs (bottom row). This reveals how the different settings behave, see text for details.

tially better on out-of-distribution datasets such as COCO captions (middle row).

We also measure the *representation quality* of the image model (bottom row) via the performance achieved by a few-shot linear regression on its pre-logs, as is commonly done in the self-supervised representation learning literature. Taken together, these figures reveal that the image representation of a pre-trained image model generalizes very well, but contrastively fine-tuning it worsens the generality of the visual representation, leading it to be better on the contrastive dataset, but worse everywhere else. This indicates that locking the image tower during tuning, i.e. LiT, *leads to a text model that is well aligned to an already strong and general image representation*, as opposed to an image-text model that is well aligned but specialized to the dataset used for alignment.

Intermediate variants, such as first locking and later unlocking the image tower or separating learning-rates are explored in Appendix H; we did not find a strictly better setup than LiT and leave this as an open research question.

### 5.3. LiT works better for more generally pre-trained models

One may believe that LiT only works because the image tower is initialized with a backbone that was supervisedly pre-trained for classification, and hence remains a supervised classifier, as opposed to becoming an image-text model. We design a controlled experiment to verify whether that is the case. We find that on the contrary, more generally

<table border="1">
<thead>
<tr>
<th rowspan="2">Model:<br/>ViT-B/16</th>
<th colspan="4">Pre-training</th>
<th colspan="3">LiT</th>
</tr>
<tr>
<th>Dataset</th>
<th>Labels?</th>
<th>Full IN</th>
<th>10-shot</th>
<th>0-shot</th>
<th>I<math>\rightarrow</math>T</th>
<th>T<math>\rightarrow</math>I</th>
</tr>
</thead>
<tbody>
<tr>
<td>MoCo-v3 [11]</td>
<td>IN</td>
<td>n</td>
<td>76.7</td>
<td>60.6</td>
<td>55.4</td>
<td>33.5</td>
<td>17.6</td>
</tr>
<tr>
<td>DINO [5]</td>
<td>IN</td>
<td>n</td>
<td>78.2</td>
<td>61.2</td>
<td>55.5</td>
<td>33.4</td>
<td>18.2</td>
</tr>
<tr>
<td>AugReg [55]</td>
<td>IN21k</td>
<td>y</td>
<td>77.4</td>
<td>63.9</td>
<td>55.9</td>
<td>30.3</td>
<td>17.2</td>
</tr>
<tr>
<td>AugReg [55]</td>
<td>IN</td>
<td>y</td>
<td>77.7</td>
<td>77.1</td>
<td>64.3</td>
<td>25.4</td>
<td>13.8</td>
</tr>
<tr>
<td>AugReg [55]</td>
<td>Places</td>
<td>y</td>
<td>-</td>
<td>22.5</td>
<td>28.5</td>
<td>25.1</td>
<td>12.9</td>
</tr>
</tbody>
</table>

Table 3. The role of pre-training method for the image model: as long as it is general, it does not matter. The background coloring denotes whether a value is **similar** or **far away** from the others in that column.

pre-trained models are better suited for LiT.

We select a set of image models that all use the same ViT-B/16 architecture but were pre-trained in various ways: supervised (AugReg [55]) on ImageNet (IN), on the large but narrow Places [39] dataset, on the much broader ImageNet-21k (IN21k), or fully unsupervised (DINO and MoCo-v3). All but the Places model achieve similar ImageNet top-1 accuracies of around 77% as reported in their respective publications, and can thus be considered *similarly good* models.

Table 3 shows model performance without LiT (ImageNet 10-shot, and accuracy when fully fine-tuned on ImageNet) alongside achieved performance with LiT on YFCC100m-CLIP (zero-shot ImageNet classification and MS Coco retrieval).

From these results, we conclude that models which are pre-trained in a generic way (e.g. on large amounts of data, or in an unsupervised way) and have similar representation quality, become similarly good image-text models after locked-image tuning (LiT). However, this also shows that a narrowly pre-trained model (AugReg-IN and AugReg-Places) will perform misleadingly well on its narrow task (0-shot IN for AugReg-IN), but significantly fall behind on more general image-text tasks (MSCOCO captions). These findings highlight the importance of a generally pre-trained model and varied set of evaluation tasks.

**Is this specific to ViT image models?** No. Here we fixed the architecture to avoid confounders, but Appendix A explores other architectures.

### 5.4. Which text model to use?

While related work has so far focused on the image model, the text model plays an important yet underexplored role in contrastive image-text learning. We consider four possible transformer-based text models [63]—the transformer from ViT-B [21] which also resembles that used in CLIP [46], T5-base [47], mT5-base [67], and the classic<table border="1">
<thead>
<tr>
<th></th>
<th>Model</th>
<th>Tok</th>
<th>INet</th>
<th>0shot</th>
<th>I→T</th>
<th>T→I</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="5">YFCC-CLIP</td>
<td>ViT</td>
<td>SP</td>
<td>57.2</td>
<td></td>
<td>29.7</td>
<td>16.9</td>
</tr>
<tr>
<td>T5</td>
<td>SP</td>
<td>57.8 (+1.4)</td>
<td></td>
<td>29.4 (+1.6)</td>
<td>17.2 (+1.2)</td>
</tr>
<tr>
<td>mT5</td>
<td>SP</td>
<td>58.1 (+1.2)</td>
<td></td>
<td>28.3 (+0.4)</td>
<td>16.4 (+1.0)</td>
</tr>
<tr>
<td>BERT</td>
<td>WP</td>
<td><b>58.8</b> (+0.7)</td>
<td></td>
<td><b>35.2</b> (+1.1)</td>
<td><b>20.0</b> (+0.7)</td>
</tr>
<tr>
<td>ViT</td>
<td>WP</td>
<td>56.4</td>
<td></td>
<td>28.2</td>
<td>17.3</td>
</tr>
<tr>
<td rowspan="3">Ours</td>
<td>ViT</td>
<td>SP</td>
<td>68.8</td>
<td></td>
<td>43.6</td>
<td>28.5</td>
</tr>
<tr>
<td>ViT</td>
<td>WP</td>
<td>68.8</td>
<td></td>
<td>45.4</td>
<td>29.7</td>
</tr>
<tr>
<td>BERT</td>
<td>WP</td>
<td>65.8</td>
<td></td>
<td>43.8</td>
<td>28.6</td>
</tr>
</tbody>
</table>

Table 4. The effect of different text encoders on zero-shot performance. The main numbers show performance achieved when the text tower is randomly initialised; the numbers in brackets are the further improvement achieved when the text tower is initialized with a pre-trained language model. The *Tok* column indicates whether a SentencePiece or WordPiece tokenizer was used.

BERT-base [17]—and whether to initialise them randomly, or from a pre-trained checkpoint. BERT uses a WordPiece (WP) tokenizer [50, 65], and all others use the SentencePiece (SP) tokenizer [35], a component which we also ablate with the ViT model.

Table 4 shows the results of LiT using an AugReg-ViT-B/32 on YFCC100M-CLIP and our dataset using the *base* sized variant of these text models. We sweep over various learning-rates and weight-decays separately for each combination to avoid being misled. Our observations differ slightly between the *relatively* small YFCC100m-CLIP dataset, and our much larger dataset, we first discuss the former. First, we see a small but consistent improvement by initializing the text model with pre-trained weights. Second and somewhat unexpectedly, we find that the BERT model performs significantly better than others, especially for retrieval. In order to disentangle the contribution of the architecture from the tokenizer, we further apply LiT using a ViT text encoder paired with BERT’s WordPiece tokenizer and see no improvement. We believe that small differences in the architecture, such as initialization and LayerNorm placement, are responsible for the slightly better generalization of BERT that we observe. However, we also found the BERT model to be less stable to train. For the large-scale experiments on our dataset, we do not observe this improvement anymore, and favor sticking with the more stable ViT SentencePiece combination.

**What about model capacity?** Previous works used relatively low-capacity text models. We show in Appendix B that increasing the text tower’s capacity consistently improves performance. The same is true, and more pronounced, for the image tower.

<table border="1">
<thead>
<tr>
<th>Dedup</th>
<th>#tune</th>
<th>#eval</th>
<th>ImgNet</th>
<th>I→T</th>
<th>T→I</th>
</tr>
</thead>
<tbody>
<tr>
<td>-</td>
<td>0</td>
<td>0</td>
<td>70.2</td>
<td>43.6</td>
<td>28.4</td>
</tr>
<tr>
<td>test</td>
<td>2.6M</td>
<td>76K</td>
<td>70.2</td>
<td>43.3</td>
<td>28.3</td>
</tr>
<tr>
<td>train+test</td>
<td>3.6M</td>
<td>220K</td>
<td>69.9</td>
<td>43.7</td>
<td>28.4</td>
</tr>
</tbody>
</table>

Table 5. Results on various de-duplication setups. #tune images are removed from the LiT dataset due to #eval images in the evaluation datasets. We report results averaged across three runs.

## 5.5. Do duplicate examples matter for LiT?

One relevant question in the context of large-scale training is the role of duplicate examples between upstream datasets and downstream datasets. We answer this question by performing experiments on three different upstream de-duplication setups: (1) no de-duplication; (2) de-duplicate against downstream test splits only; (3) de-duplicate against downstream train and test splits. We conduct experiments using the Lu setup on our dataset. We use a B/32 image model pre-trained on the JFT-3B dataset [69], which has been de-duplicated against downstream train and test splits.

In Table 5, we show the number of duplicate samples found between upstream datasets and downstream datasets during de-duplication. In the de-duplication process, a downstream image may have multiple upstream duplicate examples, e.g. due to image copies on the web. As a result, the number of duplicate examples on the upstream dataset is significantly larger than the number on the downstream datasets. The downstream number indicates how many downstream images had a duplicate detected, while the upstream number indicates how many images are removed from the image-text dataset.

We apply LiT on the three setups, and the zero-shot transfer results vary little. More results with larger backbone can be found in Appendix K, with consistent conclusions. It indicates that the duplication of examples here *does not* influence the results strongly. This observation is also consistent with previous conclusions [33, 46]. A possible interpretation is that with a large upstream dataset, the model may not memorize those duplicate examples.

Throughout this paper, we report results using the strictest setup (3) with proper de-duplication against downstream train splits and test splits, to avoid data leakage.

## 5.6. Technical advantages of locked image models

Besides potential modelling advantages previously explored, using a locked image tower has several more benefits. First, the training is significantly sped-up and memory use reduced as no gradients are computed for the image tower. Second, if no augmentations are used, such as in our large-data experiment, the image model’s embeddings can be precomputed once, further reducing compu-Figure 5. Including non-English data unlocks multilingual zero-shot models without hurting English performance. In such a regime, multilingual text pre-training can be more useful for low-resource languages.

tation time and memory requirements. Appendix G shows concrete measurements. Taken together, these implementation features unlock the use of enormous models at very large batch-sizes.

### 5.7. Preliminary multilingual experiments

It is currently common practice [31, 46] to filter image-text datasets to English language data only. We believe that removing this restriction has the potential to benefit a larger part of the world’s population. Concurrent work [30] has relied on additional translated text pairs for training the text encoder. In contrast, we do not require any translations and purely rely on the pre-trained, locked image model to bridge the language barrier. In this section, we report preliminary experiments that show the promise of LiT for multilingual image-text models.

We apply LiT on an AugReg-i21k ViT-B/32 with the T5 [47] and mT5 [67] base encoders, both with and without the pre-trained checkpoints. We do this on both the full YFCC100m dataset, and the reduced English-only CLIP subset, and we use all available text as supervision signal (See Appendix E). We evaluate the resulting model’s multilingualism in two ways, both of which have limitations discussed in Appendix J. First, we translate the ImageNet prompts into the most common languages using an online translation service and perform zero-shot classification in each of them; this evaluation is shown in Figure 5. Second, we use the Wikipedia based Image Text (WIT) dataset [54] to perform T → I retrieval across more than a hundred languages. Figure 6 gives a summary of this evaluation; a more detailed variant is provided in Appendix J.

The high-level conclusions are consistent across both evaluations: training on the full dataset improves performance on non-English languages much more than on English, using a multilingual tokenizer (as in mT5) significantly helps languages that do not use the Latin script, and starting from a pre-trained multilingual text model can

Figure 6. Image retrieval performance over 100 languages reveals that unfiltered data and a multilingually pre-trained text model can significantly increase long-tail performance.

further help. The combination of all three improvements barely has any effect when evaluated in English, but significantly improves performance on the long tail of languages. This is a promising result for unlocking multimodal models for low-resource languages.

## 6. Discussion

**Limitations.** This work explores only classification and retrieval as zero-shot transfer tasks. We leave evaluating zero-shot transfer to a broader set of tasks such as detection, segmentation, visual question answering, and image captioning as future work in order to limit our scope.

On cross-modal retrieval tasks, we have not observed as clear a benefit of the Lu setup compared to Uu or UU (Figure 3). For very long tuning schedules, Uu or UU sometimes overtake Lu on these tasks. Our results suggest that the proposed Lu setup can still save computational cost within a fixed budget, but with a large enough budget, it may be useful to also consider the Uu setup if zero-shot classification is not the primary end goal.

**Societal impact.** This work shows how one can easily add a text-tower to a pre-trained image model. While there are many useful applications, like most research, it is a double-edged sword: the technique also makes it simpler to create malicious, offensive, or obscene text tower pendants to existing image models. Further research is needed on how to best equip open-world image-text models with the behaviour we desire.

## 7. Conclusion

We present a simple method named contrastive-tuning that allows transferring any pre-trained vision model in a zero-shot fashion. More specifically, the proposed LiT setup leads to substantial quality improvements on zero-shot transfer tasks. It halves the gap between the from-scratch contrastive learning setup, and the per-task supervised fine-tuning setup. LiT makes it possible to turn publicly available models into zero-shot classifiers using pub-licly available data, and rival the performance of previous works which rely on more, proprietary data.

We hope that this work motivates future research on how to smartly re-use and adapt already pre-trained models for different research problems.

**Acknowledgements** We thank Matthias Minderer and Josip Djolonga for help on robustness evaluations; Chao Jia and Zhen Li for discussions on the image-text dataset; Ting Chen for feedback on the initial version of the paper; Jordi Pont-Tuset for help on the image-text retrieval evaluation; Jeremiah Harmsen for inspirations on the title; Jakob Uszkoreit for discussions on data augmentations; Krishna Srinivasan for discussions on the Wikipedia based image text dataset; Beer Changpinyo for discussions on conceptual captions dataset; Maxim Neumann for help on zero-shot eval and T5 text models; the Google Brain team at large for providing a supportive research environment.

## References

- [1] Andrei Barbu, David Mayo, Julian Alverio, William Luo, Christopher Wang, Dan Gutfreund, Josh Tenenbaum, and Boris Katz. ObjectNet: A large-scale bias-controlled dataset for pushing the limits of object recognition models. In *NeurIPS*, 2019. [2](#), [4](#)
- [2] Lucas Beyer, Olivier J. Hénaff, Alexander Kolesnikov, Xiaohua Zhai, and Aäron van den Oord. Are we done with imagenet? *CoRR*, abs/2006.07159, 2020. [4](#)
- [3] Lucas Beyer, Xiaohua Zhai, and Alexander Kolesnikov. Big vision. [https://github.com/google-research/big\\_vision](https://github.com/google-research/big_vision), 2022. [2](#)
- [4] Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, et al. Language models are few-shot learners. In *NeurIPS*, 2020. [1](#)
- [5] Mathilde Caron, Hugo Touvron, Ishan Misra, Hervé Jégou, Julien Mairal, Piotr Bojanowski, and Armand Joulin. Emerging properties in self-supervised vision transformers. In *ICCV*, 2021. [2](#), [6](#), [26](#)
- [6] Soravit Changpinyo, Piyush Sharma, Nan Ding, and Radu Soricut. Conceptual 12M: Pushing web-scale image-text pre-training to recognize long-tail visual concepts. In *CVPR*, 2021. [2](#), [4](#)
- [7] Jiacheng Chen, Hexiang Hu, Hao Wu, Yuning Jiang, and Changhu Wang. Learning the best pooling strategy for visual semantic embedding. In *CVPR*, 2021. [2](#)
- [8] Ting Chen, Simon Kornblith, Mohammad Norouzi, and Geoffrey E. Hinton. A simple framework for contrastive learning of visual representations. In *ICML*, 2020. [2](#)
- [9] Ting Chen, Simon Kornblith, Kevin Swersky, Mohammad Norouzi, and Geoffrey E. Hinton. Big self-supervised models are strong semi-supervised learners. In *NeurIPS*, 2020. [2](#)
- [10] Xinlei Chen, Hao Fang, Tsung-Yi Lin, Ramakrishna Vedantam, Saurabh Gupta, Piotr Dollár, and C. Lawrence Zitnick. Microsoft COCO captions: Data collection and evaluation server. *CoRR*, abs/1504.00325, 2015. [16](#)
- [11] Xinlei Chen, Saining Xie, and Kaiming He. An empirical study of training self-supervised vision transformers. *CoRR*, abs/2104.02057, 2021. [2](#), [6](#), [26](#)
- [12] Yen-Chun Chen, Linjie Li, Licheng Yu, Ahmed El Kholy, Faisal Ahmed, Zhe Gan, Yu Cheng, and Jingjing Liu. UNITER: universal image-text representation learning. In *ECCV*, 2020. [2](#)
- [13] Zihang Dai, Hanxiao Liu, Quoc V. Le, and Mingxing Tan. CoAtNet: Marrying convolution and attention for all data sizes. In *NeurIPS*, 2021. [1](#), [2](#), [4](#)
- [14] Mostafa Dehghani, Anurag Arnab, Lucas Beyer, Ashish Vaswani, and Yi Tay. The efficiency misnomer. *CoRR*, abs/2110.12894, 2021. [12](#)
- [15] Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li, and Li Fei-Fei. Imagenet: A large-scale hierarchical image database. In *CVPR*, 2009. [3](#)
- [16] Karan Desai and Justin Johnson. VirTex: Learning visual representations from textual annotations. In *CVPR*, 2021. [2](#)
- [17] Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. BERT: pre-training of deep bidirectional transformers for language understanding. In *NAACL-HLT*, 2019. [7](#), [12](#), [13](#), [26](#)
- [18] Josip Djolonga, Jessica Yung, Michael Tschannen, Rob Romijnders, Lucas Beyer, Alexander Kolesnikov, Joan Puigcerver, Matthias Minderer, Alexander D’Amour, Dan Moldovan, Sylvain Gelly, Neil Houlsby, Xiaohua Zhai, and Mario Lucic. On robustness and transferability of convolutional neural networks. In *CVPR*, 2021. [2](#)
- [19] Carl Doersch, Abhinav Gupta, and Alexei A. Efros. Unsupervised visual representation learning by context prediction. In *ICCV*, 2015. [2](#)
- [20] Jeff Donahue, Yangqing Jia, Oriol Vinyals, Judy Hoffman, Ning Zhang, Eric Tzeng, and Trevor Darrell. DeCAF: A deep convolutional activation feature for generic visual recognition. In *ICML*, 2014. [2](#)
- [21] Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, Jakob Uszkoreit, and Neil Houlsby. An image is worth 16×16 words: Transformers for image recognition at scale. In *ICLR*, 2021. [2](#), [6](#), [12](#), [26](#)
- [22] Fartash Faghri, David J. Fleet, Jamie Ryan Kiros, and Sanja Fidler. VSE++: Improving visual-semantic embeddings with hard negatives. In *BMVC*, 2018. [2](#)
- [23] Andrea Frome, Gregory S. Corrado, Jonathon Shlens, Samy Bengio, Jeffrey Dean, Marc’Aurelio Ranzato, and Tomáš Mikolov. DeViSE: A deep visual-semantic embedding model. In *NeurIPS*, 2013. [2](#)
- [24] Yash Goyal, Tejas Khot, Douglas Summers-Stay, Dhruv Batra, and Devi Parikh. Making the V in VQA matter: Elevating the role of image understanding in visual question answering. In *CVPR*, 2017. [2](#)- [25] Kaiming He, Haoqi Fan, Yuxin Wu, Saining Xie, and Ross B. Girshick. Momentum contrast for unsupervised visual representation learning. In *CVPR*, 2020. [2](#)
- [26] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In *CVPR*, 2016. [4](#)
- [27] Dan Hendrycks, Steven Basart, Norman Mu, Saurav Kadavath, Frank Wang, Evan Dorundo, Rahul Desai, Tyler Zhu, Samyak Parajuli, Mike Guo, Dawn Song, Jacob Steinhardt, and Justin Gilmer. The many faces of robustness: A critical analysis of out-of-distribution generalization. *CoRR*, abs/2006.16241, 2020. [4](#)
- [28] Dan Hendrycks, Kevin Zhao, Steven Basart, Jacob Steinhardt, and Dawn Song. Natural adversarial examples. In *CVPR*, 2021. [4](#)
- [29] Gabriel Ilharco, Mitchell Wortsman, Nicholas Carlini, Rohan Taori, Achal Dave, Vaishaal Shankar, Hongseok Namkoong, John Miller, Hannaneh Hajishirzi, Ali Farhadi, and Ludwig Schmidt. OpenCLIP. Zenodo, 2021. [4](#), [5](#)
- [30] Aashi Jain, Mandy Guo, Krishna Srinivasan, Ting Chen, Sneha Kudugunta, Chao Jia, Yinfei Yang, and Jason Baldridge. MURAL: Multimodal, multitask representations across languages. In *Findings of the Association for Computational Linguistics: EMNLP 2021*, pages 3449–3463, Punta Cana, Dominican Republic, Nov. 2021. Association for Computational Linguistics. [8](#)
- [31] Chao Jia, Yinfei Yang, Ye Xia, Yi-Ting Chen, Zarana Parekh, Hieu Pham, Quoc V. Le, Yun-Hsuan Sung, Zhen Li, and Tom Duerig. Scaling up visual and vision-language representation learning with noisy text supervision. In *ICML*, 2021. [1](#), [2](#), [3](#), [4](#), [5](#), [8](#)
- [32] Andrej Karpathy and Li Fei-Fei. Deep visual-semantic alignments for generating image descriptions. In *CVPR*, 2015. [2](#)
- [33] Alexander Kolesnikov, Lucas Beyer, Xiaohua Zhai, Joan Puigcerver, Jessica Yung, Sylvain Gelly, and Neil Houlsby. Big transfer (BiT): General visual representation learning. In *ECCV*, 2020. [1](#), [2](#), [7](#), [12](#), [26](#)
- [34] Simon Kornblith, Jonathon Shlens, and Quoc V. Le. Do better imagenet models transfer better? In *CVPR*, 2019. [1](#), [2](#)
- [35] Taku Kudo and John Richardson. SentencePiece: A simple and language independent subword tokenizer and detokenizer for neural text processing. In *EMNLP*, 2018. [7](#)
- [36] Christoph H. Lampert, Hannes Nickisch, and Stefan Harmeling. Learning to detect unseen object classes by between-class attribute transfer. In *CVPR*, 2009. [1](#), [2](#)
- [37] Hugo Larochelle, Dumitru Erhan, and Yoshua Bengio. Zero-data learning of new tasks. In *AAAI*, 2008. [1](#), [2](#)
- [38] Liunian Harold Li, Mark Yatskar, Da Yin, Cho-Jui Hsieh, and Kai-Wei Chang. VisualBERT: A simple and performant baseline for vision and language. *CoRR*, abs/1908.03557, 2019. [2](#)
- [39] Alejandro López-Cifuentes, Marcos Escudero-Viñolo, Jesús Bescós, and Álvaro García-Martín. Semantic-aware scene recognition. *Pattern Recognit.*, 102:107256, 2020. [6](#)
- [40] Ilya Loshchilov and Frank Hutter. Decoupled weight decay regularization. In *ICLR*, 2019. [12](#), [26](#)
- [41] Jiasen Lu, Dhruv Batra, Devi Parikh, and Stefan Lee. ViL-BERT: Pretraining task-agnostic visiolinguistic representations for vision-and-language tasks. In *NeurIPS*, 2019. [2](#)
- [42] Jiasen Lu, Vedanuj Goswami, Marcus Rohrbach, Devi Parikh, and Stefan Lee. 12-in-1: Multi-task vision and language representation learning. In *CVPR*, 2020. [2](#)
- [43] Dhruv Mahajan, Ross B. Girshick, Vignesh Ramanathan, Kaiming He, Manohar Paluri, Yixuan Li, Ashwin Bharambe, and Laurens van der Maaten. Exploring the limits of weakly supervised pretraining. In *ECCV*, 2018. [1](#)
- [44] Mehdi Noroozi and Paolo Favaro. Unsupervised learning of visual representations by solving jigsaw puzzles. In *ECCV*, 2016. [2](#)
- [45] Sinno Jialin Pan and Qiang Yang. A survey on transfer learning. *IEEE Trans. Knowl. Data Eng.*, 22(10), 2010. [1](#), [2](#)
- [46] Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, Gretchen Krueger, and Ilya Sutskever. Learning transferable visual models from natural language supervision. In *ICML*, 2021. [1](#), [2](#), [3](#), [4](#), [5](#), [6](#), [7](#), [8](#), [12](#), [13](#), [15](#)
- [47] Colin Raffel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, and Peter J. Liu. Exploring the limits of transfer learning with a unified text-to-text transformer. *J. Mach. Learn. Res.*, 21:140:1–140:67, 2020. [6](#), [8](#), [12](#), [26](#)
- [48] Ali Sharif Razavian, Hossein Azizpour, Josephine Sullivan, and Stefan Carlsson. CNN features off-the-shelf: An astounding baseline for recognition. In *CVPR*, 2014. [2](#)
- [49] Benjamin Recht, Rebecca Roelofs, Ludwig Schmidt, and Vaishaal Shankar. Do ImageNet classifiers generalize to ImageNet? In *ICML*, 2019. [4](#)
- [50] Mike Schuster and Kaisuke Nakajima. Japanese and Korean voice search. In *ICASSP*, 2012. [7](#)
- [51] Rico Sennrich, Barry Haddow, and Alexandra Birch. Improving neural machine translation models with monolingual data. In *ACL*, 2016. [17](#)
- [52] Piyush Sharma, Nan Ding, Sebastian Goodman, and Radu Soricut. Conceptual captions: A cleaned, hypernymed, image alt-text dataset for automatic image captioning. In *ACL*, 2018. [4](#)
- [53] Noam Shazeer and Mitchell Stern. Adafactor: Adaptive learning rates with sublinear memory cost. In *ICML*, 2018. [12](#), [26](#)
- [54] Krishna Srinivasan, Karthik Raman, Jiecao Chen, Michael Bendersky, and Marc Najork. WIT: wikipedia-based image text dataset for multimodal multilingual machine learning. *CoRR*, abs/2103.01913, 2021. [8](#)
- [55] Andreas Steiner, Alexander Kolesnikov, Xiaohua Zhai, Ross Wightman, Jakob Uszkoreit, and Lucas Beyer. How to train your ViT? Data, augmentation, and regularization in vision transformers. *CoRR*, abs/2106.10270, 2021. [5](#), [6](#), [12](#), [13](#), [26](#)
- [56] Weijie Su, Xizhou Zhu, Yue Cao, Bin Li, Lewei Lu, Furu Wei, and Jifeng Dai. VL-BERT: pre-training of generic visual-linguistic representations. In *ICLR*, 2020. [2](#)
- [57] Chen Sun, Abhinav Shrivastava, Saurabh Singh, and Abhinav Gupta. Revisiting unreasonable effectiveness of data in deep learning era. In *ICCV*, 2017. [3](#)[58] Christian Szegedy, Wei Liu, Yangqing Jia, Pierre Sermanet, Scott E. Reed, Dragomir Anguelov, Dumitru Erhan, Vincent Vanhoucke, and Andrew Rabinovich. Going deeper with convolutions. In *CVPR*, 2015. [12](#)

[59] Chuanqi Tan, Fuchun Sun, Tao Kong, Wenchang Zhang, Chao Yang, and Chunfang Liu. A survey on deep transfer learning. In *ICANN*, 2018. [2](#)

[60] Bart Thomee, David A. Shamma, Gerald Friedland, Benjamin Elizalde, Karl Ni, Douglas Poland, Damian Borth, and Li-Jia Li. YFCC100M: the new data in multimedia research. *Commun. ACM*, 59(2):64–73, 2016. [2](#), [4](#)

[61] Ilya Tolstikhin, Neil Houlsby, Alexander Kolesnikov, Lucas Beyer, Xiaohua Zhai, Thomas Unterthiner, Jessica Yung, Andreas Steiner, Daniel Keysers, Jakob Uszkoreit, Mario Lucic, and Alexey Dosovitskiy. MLP-Mixer: An all-MLP architecture for vision. In *NeurIPS*, 2021. [2](#), [12](#), [26](#)

[62] Aäron van den Oord, Yazhe Li, and Oriol Vinyals. Representation learning with contrastive predictive coding. *CoRR*, abs/1807.03748, 2018. [2](#)

[63] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, and Illia Polosukhin. Attention is all you need. In *NeurIPS*, 2017. [6](#)

[64] Haohan Wang, Songwei Ge, Zachary C. Lipton, and Eric P. Xing. Learning robust global representations by penalizing local predictive power. In Hanna M. Wallach, Hugo Larochelle, Alina Beygelzimer, Florence d’Alché-Buc, Emily B. Fox, and Roman Garnett, editors, *Advances in Neural Information Processing Systems 32: Annual Conference on Neural Information Processing Systems 2019, NeurIPS 2019, December 8-14, 2019, Vancouver, BC, Canada*, pages 10506–10518, 2019. [4](#)

[65] Yonghui Wu, Mike Schuster, Zhifeng Chen, Quoc V. Le, Mohammad Norouzi, Wolfgang Macherey, Maxim Krikun, Yuan Cao, Qin Gao, Klaus Macherey, Jeff Klingner, Apurva Shah, Melvin Johnson, Xiaobing Liu, Łukasz Kaiser, et al. Google’s neural machine translation system: Bridging the gap between human and machine translation. *CoRR*, abs/1609.08144, 2016. [7](#)

[66] Yongqin Xian, Christoph H. Lampert, Bernt Schiele, and Zeynep Akata. Zero-shot learning - A comprehensive evaluation of the good, the bad and the ugly. *IEEE TPAMI*, 41(9):2251–2265, 2019. [1](#)

[67] Linting Xue, Noah Constant, Adam Roberts, Mihir Kale, Rami Al-Rfou, Aditya Siddhant, Aditya Barua, and Colin Raffel. mT5: A massively multilingual pre-trained text-to-text transformer. In *NAACL-HLT*, 2021. [6](#), [8](#), [12](#), [26](#)

[68] Rowan Zellers, Yonatan Bisk, Ali Farhadi, and Yejin Choi. From recognition to cognition: Visual commonsense reasoning. In *CVPR*, 2019. [2](#)

[69] Xiaohua Zhai, Alexander Kolesnikov, Neil Houlsby, and Lucas Beyer. Scaling vision transformers. *CoRR*, abs/2106.04560, 2021. [1](#), [2](#), [4](#), [7](#), [12](#), [17](#), [26](#)

[70] Xiaohua Zhai, Joan Puigcerver, Alexander Kolesnikov, Pierre Ruysen, Carlos Riquelme, Mario Lucic, Josip Djolonga, André Susano Pinto, Maxim Neumann, Alexey Dosovitskiy, Lucas Beyer, Olivier Bachem, Michael Tschannen, Marcin Michalski, Olivier Bousquet, Sylvain Gelly, and Neil Houlsby. The visual task adaptation benchmark. *CoRR*, abs/1910.04867, 2019. [4](#), [15](#), [26](#)

[71] Yuhao Zhang, Hang Jiang, Yasuhide Miura, Christopher D. Manning, and Curtis P. Langlotz. Contrastive learning of medical visual representations from paired images and text. *CoRR*, abs/2010.00747, 2020. [2](#), [3](#)## A. Is this specific to ViT image models?

No. In the main paper, we only used ViT models for all experiments. Could it be that LiT only works with ViT models, or is in some way specific to the Transformer architecture?

In order to verify that this is not the case, we applied the same recipe to comparably-sized models of different families. Table 6 shows the zero-shot performance with LiT on the CC12M dataset for ViT [21], Mixer [61], and ResNet [33]; all pre-trained on ImageNet21k. Following [14], we report parameter count, inference speed, and FLOPs to indicate our attempt to match the “model size”. The results show that LiT works for different model families, but also confirm the finding of [46] that ViT models do seem more amenable to learning image-text mappings than other architectures of similar size.

<table border="1">
<thead>
<tr>
<th>Model</th>
<th>0shot</th>
<th>Adapt</th>
<th>I <math>\uparrow</math> T</th>
<th>T <math>\uparrow</math> I</th>
<th>Param</th>
<th>Speed</th>
<th>FLOPs</th>
</tr>
</thead>
<tbody>
<tr>
<td>ViT-B/32</td>
<td>60.7</td>
<td>79.1</td>
<td>41.3</td>
<td>25.0</td>
<td>197 M</td>
<td>2855</td>
<td>12 G</td>
</tr>
<tr>
<td>Mixer-B/32</td>
<td>57.1</td>
<td>75.9</td>
<td>37.5</td>
<td>22.9</td>
<td>169 M</td>
<td>4208</td>
<td>9 G</td>
</tr>
<tr>
<td>BiT-M-R50</td>
<td>55.2</td>
<td>77.6</td>
<td>37.3</td>
<td>23.9</td>
<td>134 M</td>
<td>2159</td>
<td>11 G</td>
</tr>
</tbody>
</table>

Table 6. LiT with different model families. Showing zero-shot top-1 accuracy on ImageNet in comparison to fine-tuning (column “Adapt”). Inference “Speed” is in images per second per core.

## B. Larger model capacity yields better results

Increasing the model capacity of the pre-trained image-tower improves zero-shot ImageNet accuracy more than increasing the capacity of the text-tower. Figure 7 shows substantial gains in the private data setup when the image tower capacity is increased from B/32 and base text tower (74.5%) to g/14 and huge text tower (81.2%). We take the pre-trained image towers from [69], and the text towers were trained from scratch.

The improvements in the public CC12M data setup range from 61.1% with a B/32 image tower and base text tower

Figure 7. ImageNet zero-shot accuracy [%] with varying model capacity. Incremental improvements due to larger *text* towers (base  $\rightarrow$  large  $\rightarrow$  huge) are shown as stacked bars.

up to 67.6% with the L/16 model combined with a large text tower. In this setup, we used pre-trained BERT text towers [17] and pre-trained image models from [55] (using the “recommended checkpoints”). Note that in this case the increase from B/16 to L/16 is more modest (from 66.9% to 67.6% with the large text tower), and we see a similar improvement in ImageNet zero-shot performance when increasing the text tower size.

## C. Tuning details on our dataset

We use the pre-trained transformer models from [69]. ViT-B/32 was used for most of the ablation tests, and the larger ViT-B/16, ViT-L/16 and ViT-g/14 models are used in Section B for capacity impact evaluations. For our best Lu results, we adopt the ViT-g/14 model pre-trained in [69].

During contrastive-tuning, we use the AdaFactor optimizer [53] following [69]. We use 0.001 learning rate, and the default  $\beta_1 = 0.9$  and  $\beta_2 = 0.999$  for AdaFactor optimizer. We use batch size 16384 by default, unless otherwise noted. Input image is simply resized to  $224 \times 224$  resolution (apart from  $288 \times 288$  resolution for “g/14\*” model). No weight decay is used during tuning. We use cosine learning rate schedule with a linear learning rate warmup of 10k steps. We train our models for 55k steps by default, which equals to about 900 million seen image-text pairs during tuning. For our best runs, we scale up the training schedule to 18 billion seen image-text pairs. We use 128 TPU cores by default for the above experiments, and 256 TPU cores for our best run with 18 billion seen image-text pairs.

In the Lu setup, we do not attach the optional linear head on the image tower. We observe a very small quality improvement without using the image linear head, thus we remove it for simplicity.

## D. Tuning details on CC12m

We use pre-trained ViT models from [55] (unless otherwise noted, we used the “recommended checkpoints” from that repository). On the text side, we use BERT-base and BERT-large from [17] for most experiments. In section 5.4 we use T5-base from [47] and mT5-base from [67].

We use the Adam optimizer ( $\beta_1 = 0.9$ ,  $\beta_2 = 0.999$ ) for all models, except for models with Large text tower that were trained with a modified version of AdaFactor from [69] (same settings as described in Section C). The learning rate is set to 0.001, and the weight decay to 0.0001 (using “decoupled” weight decay as described in [40]). Gradients are clipped at global norm 1.

For training, the images are pre-processed by Inception-style cropping [58] to a size of 224 pixels. For evaluation, the images are resized to 224 pixels with bi-linear interpolation without cropping.

When tuning on the CC12M dataset, we train for 20Figure 8. Ablations for YFCC100m. **Top:** even though the description field can be long, the potential benefit of using more than 16 tokens does not outweigh the increased memory and computation cost. **Middle:** When using all text signals, sticking to the CLIP subset is better according to the standard benchmarks, however see also Section 5.7. **Bottom:** Using all three text signals simultaneously for all examples works better than sampling one per image or per batch.

epochs (200 million seen image-text pairs), which corresponds to 12k steps with a batch size of 16384. The first 50k image-text pairs are used as minimal validation set. The learning rate is ramped up linearly for the first 2k steps and then follows a cosine decay. Unless otherwise noted, we use the Lu setup with a linear head on the text tower only.

## E. How to use YFCC100m?

This section is an exploratory analysis of the YFCC100m dataset and provides guidance on what is a good setup for LiT. For each experiment we run, we try three learning-rates (0.001, 0.0008, 0.0003) and two weight-decays (0.0001 and 0.00001) and report the best result, this allows avoiding biasing conclusions due to sub-optimal hyper-parameters. We perform the exploration using the small ViT-B/32 AugReg [55] image tower and a BERT base [17] text tower and run tuning for 60 000 steps, although the same conclusions and similar scores are already reachable after 30 000 steps of tuning.

The YFCC100m dataset comes with a rich set of annotations for each image, including camera settings and geolocation. Out of all the annotations, three of them are potential candidates for learning image-text pairings: the image’s ti-

tle, a description, and a set of free-form tags. However, only partially overlapping subsets of 60 M, 30 M, and 65 M images come with a title, description, or tags, respectively. We first explore which supervision signal is most useful. For the description, we simply tokenize the provided text; for the title, we perform basic filtering and remove titles that start with DSC, IMG, Picture, consist of only the word image or consist of more than half digits; for the tags, we randomly shuffle their order, and join them with a random space, newline, or basic punctuation character in order to get a string which we then tokenize. The texts vary dramatically in length, we thus try maximum sequence lengths of 16 and 32 tokens. The first row of Figure 8 shows the result of this experiment. The difference between a maximum sequence length of 16 and 32 is small, however the memory savings are substantial and we thus restrict the sequence length to 16 tokens in all further experiments.

In terms of supervision signal, there is no single clear winner. We thus explore three ways of learning from all signals and so also make use of the full 100 M images. We can either *jointly* optimize them by summing up three contrastive losses for each image, or we can randomly sample one of the three sources for each *image* or for a whole *minibatch*. As can be seen in the bottom row of Figure 8, jointly using all signals consistently works better, although it requires triple the amount of passes through the text tower.

Finally, the authors of CLIP [46] provide a curated subset of roughly 15 M images, which contain high quality annotations in English. We refer to this subset as YFCC<sub>CLIP</sub>. In the middle row of Figure 8, we compare how using the Full YFCC100m for LiT compares to using the CLIP subset of it. Both seem to perform roughly on par for all signals for classification, but when using only titles or tags and performing image-text retrieval, it is better to apply LiT on the full YFCC100m dataset.

Overall, we obtain the best results with LiT using all text signals jointly on the YFCC<sub>CLIP</sub> subset. However, this investigation was performed with the small ViT-B/32 model, it is likely that a larger model may perform better when using the full dataset.

## F. Effective batch size for contrastive loss

In this section, we study the impact of the effective batch size for contrastive loss. We use the Lu setup with a pre-trained B/32 image model, tuned for 900 million seen image-text pairs. In Figure 9, we see a clear improvement when using global contrastive loss. It has increased the effective batch size for contrastive learning, thus introducing more hard negatives and improving model quality. Interestingly, we found that larger batch size leads to better performance consistently. We leave extremely large batch size exploration to future work.Figure 9. Impact of batch sizes for contrastive loss, including both global contrastive loss and local contrastive loss.

Figure 10. **Left:** Pre-computing image embeddings accelerates LiT, when tuning for more than a single epoch. **Right:** Pre-computing image embeddings in LiT allows larger batch size in memory.

## G. Pre-computation for locked image models

In LiT method, the locked image model generates identical embeddings given the same image. Based on this characteristic, we use pre-computed image embeddings during tuning. It allows faster iterations and fitting larger text models in memory, as the image representations are extracted only once and no image models are loaded.

Figure 10 left shows how training speeds up as the number of epochs grows. When training no more than a single epoch, pre-computation keeps a constant speed ratio over re-computation, which increases from one (same speed) to larger than one (speedup) as image model size grows. After one epoch, pre-computation clearly accelerates training due to reused image representations. The speedup ratio becomes more visible as either the number of epochs or the

<table border="1">
<thead>
<tr>
<th colspan="2">Model</th>
<th colspan="2">Param (M)</th>
<th colspan="3">Max speed</th>
<th colspan="2">Max batch</th>
</tr>
<tr>
<th>Image</th>
<th>Text</th>
<th>Pre</th>
<th>Non</th>
<th>Pre</th>
<th>Non</th>
<th>Inf</th>
<th>Pre</th>
<th>Non</th>
</tr>
</thead>
<tbody>
<tr>
<td>B/32</td>
<td>B</td>
<td>105</td>
<td>195</td>
<td>2439</td>
<td>893</td>
<td>3294</td>
<td>2448</td>
<td>2262</td>
</tr>
<tr>
<td>B/32</td>
<td>L</td>
<td>320</td>
<td>410</td>
<td>924</td>
<td>688</td>
<td>3294</td>
<td>1528</td>
<td>751</td>
</tr>
<tr>
<td>B/32</td>
<td>H</td>
<td>640</td>
<td>730</td>
<td>468</td>
<td>390</td>
<td>3294</td>
<td>912</td>
<td>781</td>
</tr>
<tr>
<td>B/32</td>
<td>g</td>
<td>1007</td>
<td>1097</td>
<td>242</td>
<td>218</td>
<td>3294</td>
<td>248</td>
<td>248</td>
</tr>
<tr>
<td>L/16</td>
<td>B</td>
<td>105</td>
<td>406</td>
<td>2423</td>
<td>215</td>
<td>273</td>
<td>2448</td>
<td>1663</td>
</tr>
<tr>
<td>L/16</td>
<td>L</td>
<td>320</td>
<td>621</td>
<td>920</td>
<td>204</td>
<td>273</td>
<td>1528</td>
<td>754</td>
</tr>
<tr>
<td>L/16</td>
<td>H</td>
<td>640</td>
<td>942</td>
<td>465</td>
<td>160</td>
<td>273</td>
<td>912</td>
<td>347</td>
</tr>
<tr>
<td>L/16</td>
<td>g</td>
<td>1007</td>
<td>1308</td>
<td>240</td>
<td>118</td>
<td>273</td>
<td>248</td>
<td>184</td>
</tr>
<tr>
<td>g/14</td>
<td>B</td>
<td>105</td>
<td>1094</td>
<td>2409</td>
<td>17</td>
<td>17</td>
<td>2448</td>
<td>146</td>
</tr>
<tr>
<td>g/14</td>
<td>L</td>
<td>320</td>
<td>1310</td>
<td>932</td>
<td>15</td>
<td>17</td>
<td>1520</td>
<td>132</td>
</tr>
<tr>
<td>g/14</td>
<td>H</td>
<td>641</td>
<td>1630</td>
<td>467</td>
<td>14</td>
<td>17</td>
<td>912</td>
<td>97</td>
</tr>
<tr>
<td>g/14</td>
<td>g</td>
<td>1008</td>
<td>1997</td>
<td>243</td>
<td>12</td>
<td>17</td>
<td>248</td>
<td>66</td>
</tr>
</tbody>
</table>

Table 7. Pre-computation details. *Max speed* and *Max batch* describe metrics collected by maximum speed (img/sec/core) and batch size, respectively, corresponding to Figure 10. *Pre* and *Non* are metrics with and without pre-computation respectively; *Inf* describes pre-computation inference speed, which is only affected by image models. All experiments are run on 8 TPU v3 cores.

image model size grows.

For experiments with pre-computed image embeddings, we count both pre-computation inference cost and tuning cost. Pre-computation will be performed on at most a single epoch on the image-text dataset. In practice, the pre-computed embeddings can be shared across different experiments, as long as the image tower is identical. As a result, the actual cost is even lower than our estimation. For experiments without pre-computed image embeddings, we count the actual contrastive-tuning cost.

Pre-computation eliminates loading the image model to memory during training, thus allowing larger batch sizes for contrastive loss. We search maximum batch sizes on each combination of image and text models with and without pre-computation, and show the results in Figure 10 right. We search for the maximum batch size for each model with a unified setup. We report the maximum batch size that the model can fit on 8 TPU v3 cores.

However, if image augmentations are enabled during training, we may not benefit much from pre-computation. The model sees different augmented images in multiple epochs. Nevertheless, the memory benefits still hold. All metric details are in Table 7.

## H. Learning rate schedules

For most of the experiments, weights were either completely locked, or trained with the same learning rate schedule (linear warmup and cosine decay). We experimented with different learning rate schedules (Figure 11), mainly varying how the image tower was updated. We observed that training the image tower with a smaller learning rateFigure 11. Different learning rate schedules. Note that the default LR schedule is shown in black in the lower part of the figure.

Figure 12. ITR and VTAB metrics as a function of ImageNet 0-shot accuracy for different LR schedules.

and/or delaying training of the image tower resulted in better retrieval metrics (Figure 12).

The default schedules (LU and UU) have the best and worst ImageNet 0-shot accuracy of all tried learning rate schedules. Compared to UU, both ITR/VTAB metrics and ImageNet 0-shot accuracy improve modestly, when the image learning rate is only scheduled for the second half of the training (“delay”). The ImageNet 0-shot accuracy improves more but the VTAB accuracy drops when the learning rate is set to a smaller value (“lr=1e-4”). Combining the delay with the smaller learning rate (“lr+dl”) further improves both ITR/VTAB metrics and ImageNet 0-shot accuracy. A similar result is achieved by multiplying the learning rate in

the UU setting with a sigmoid function (“sigmoid”). Alternating between freezing image tower and rext tower (“two cycles”) finally performs somewhere between “lr+dl” and “lr=1e-4” schedules.

## I. Zero-shot transfer details

### I.1. Classification

We follow CLIP [46] for the zero-shot transfer evaluation. We use the identical ImageNet class label names and the same 80 prompt templates as in CLIP. During evaluation of private LiT models, we first resize the test image and then central crop with 0.875 aspect ratio to the target resolution. More specifically, we use  $224 \times 224$  target resolution for CIFAR dataset and  $288 \times 288$  target resolution for the remaining datasets. For all the public LiT models, we resize all test images to  $224 \times 224$  for simplicity.

### I.2. VTAB Evaluation

The Visual Task Adaptation benchmark [70] consists of 19 diverse visual tasks. We refer readers to the original publication for details about each dataset; here we just mention that they are split into three categories:

- • **Natural:** These tasks contain classical “natural” real-world images obtained with a camera, such as vehicles, pets, scenery and household objects.
- • **Specialized:** These are datasets of arguably “natural” images which were captured with specialised photographic equipment, such as satellite photographs and medical images.
- • **Structured:** These assess understanding of scenes structure in some way, predominately from synthetic environments. Example tasks include 3D depth estimation and counting.

Note that there is significant overlap with the datasets assessed in [46], but it is not guaranteed that the same data splits were used.

**Evaluation protocol.** Previous works [46] define task-specific prompts and class names, but it is not clear exactly how an optimal set of prompts for a given task was chosen.

For VTAB, we define a search space of image preprocessing, prompt templates and classes, where the latter two are often per-task (e.g. using a *satellite photo of ...* or an *overhead photo of ...* for tasks involving satellite imagery). All such settings are tried on a small validation set of 800 images, and the optimal setting is then run on the official VTAB test set.

We note this is arguably not *zero-shot* transfer, but believe it is a principled and reproducible approach.

**Prompts used.** For all tasks, we considered 3 default sets of prompts1. 1. A photo of a `CLASS`
2. 2. `CLASS`
3. 3. The 6 CLIP prompts used for ImageNet<sup>4</sup>

We also consider some task specific prompts/class name settings. Note that these two degrees of freedom are orthogonal, and a text setting is defined by both. They are shown in Table 11 and Table 12. Not all of these prompts were equally useful; some are redundant, providing equal performance gain as other settings, and some do not provide performance gains at all. We show the performance delta comparing only the default prompts versus including a given text variant as well, to give a rough idea of how beneficial it was.

### Can we assess zero-shot performance using VTAB?

The strength of such a diverse benchmark is in the variety of its label spaces. ImageNet classes, though very fine-grained, are fairly generic. However, VTAB also includes *structured tasks* which are designed to assess the model’s competence at tasks which aren’t object recognition, such as counting and assessing distances and angles. This presents interesting difficulties for solving in a zero-shot natural language grounded manner. Figure 13 shows the zero-shot performance of many models developed for this paper. Their detailed performance is not important here - the gray lines show what a “random guesser” would achieve on each VTAB category. It is not an obvious number, as performance across categories is an average of all the constituent datasets, which have varying numbers of classes. It is clear from this figure that the structured performance does not significantly deviate from random guessing, despite extensive efforts in prompt engineering. We leave it as an open - and very interesting - research direction to figure how to make such models count and assess distances. Furthermore, though contrastive image-text training on the web can largely match supervised models on natural tasks, further improvements are needed on more specialist tasks.

### I.3. Cross-modal retrieval

We compute retrieval metrics on MSCOCO captions [10], reporting the numbers on the test set (5 000 images, 25 010 captions). For the image to text retrieval, we rank all texts by decreasing cosine similarity of their embedding with the image embedding, and then report the fraction of images that ranks the correct text within the first (1, 5, 10) positions as the Recall@1, Recall@5, Recall@10 metrics. For the text to image retrieval, we compute the same metric, but ranking images and averaging over all texts. When showing a single number, we always refer to the Recall@1 metric.

<sup>4</sup><https://github.com/openai/CLIP/blob/main/data/prompts.md>

Figure 13. Performance of zero-shot classification models across different VTAB categories. Each dot is a zero-shot model evaluation.

<table border="1">
<thead>
<tr>
<th rowspan="2"></th>
<th colspan="3">CLIP subset</th>
<th colspan="3">Full</th>
</tr>
<tr>
<th>ImgNet</th>
<th>T→I</th>
<th>I→T</th>
<th>ImgNet</th>
<th>T→I</th>
<th>I→T</th>
</tr>
</thead>
<tbody>
<tr>
<td>T5</td>
<td>58.9</td>
<td>14.5</td>
<td>22.6</td>
<td>62.4</td>
<td>19.6</td>
<td>34.3</td>
</tr>
<tr>
<td>+ pt</td>
<td>58.5</td>
<td>17.2</td>
<td>29.1</td>
<td>62.3</td>
<td><b>20.1</b></td>
<td><b>34.5</b></td>
</tr>
<tr>
<td>mT5</td>
<td>58.7</td>
<td>14.4</td>
<td>23.1</td>
<td>62.1</td>
<td>18.5</td>
<td>32.6</td>
</tr>
<tr>
<td>+ pt</td>
<td>58.4</td>
<td>15.6</td>
<td>25.1</td>
<td><b>62.6</b></td>
<td>18.9</td>
<td>33.6</td>
</tr>
</tbody>
</table>

Table 8. Training on the full YFCC100m data significantly improves all metrics compared to the CLIP subset. Gray rows are with text pre-training.

## J. Multilingual details and limitations

**Extra results.** Table 8 shows the English zero-shot ImageNet classification performance of different English and multilingual T5 models, with LiT on YFCC<sub>CLIP</sub> vs. YFCC100m. We note that training on the larger, more diverse, multilingual set does not come at the expense of English performance.

**Wiki-Image Text as an evaluation benchmark.** We noted qualitatively that, as one may expect from Wikipedia, a large proportion of examples are about entities such as people, places, or art. When translated to other languages, proper nouns are usually kept as is - especially if the two languages share an alphabet. This makes it an imperfect dataset to benchmark multilingualism as monolingual models will score higher than they should.

**Tokenization subtleties.** The sentencepiece tokenizers, when faced with unknown vocabulary, will default to byte encoding. This is not a perfect catch-all; in such circumstances models cannot take advantage of pre-training, and the resultantly very long sequences will not fit in the 16-token maximum length used in this paper. It is nevertheless better than the [UNK] tokens produced by BERT’s Word-Figure 14. Fully detailed evaluation of the multilingual models on WIT.

Piece tokenizer; with SentencePiece, even with an imperfect vocabulary, the model has a chance to adapt. This explains why even with an ill-suited English-only vocabulary, the T5 models can still learn decent representations of non-English languages.

**Translation of prompts.** One obvious factor worth noting is that, in our setup, non-English languages may be impacted by imperfect translations. This likely means non-English performance is underestimated.

More subtly, we note that many languages - especially those with Latin alphabets - often use the English word for very niche or specific items. For example, at the time of writing, the Vietnamese translation of *I took a photo of an airship* contains the word *airship* verbatim. The contrastive model can in principle pick out the word *airship*, ignore all the Vietnamese, and retain decent performance despite not understanding Vietnamese at all.

**Backtranslation as data augmentation.** Backtranslation [51] - translating to a language and back again, in order to generate slightly different versions of a given text - is a common augmentation in NLP. We run some experiments to see whether it works for contrastive image-text training. We again use an online translation service to translate the texts in CC12M to and from 9 different languages. This probability is shared across the languages i.e. a backtranslation probability of 0.5 with 5 different backtranslate candidates means there is a 50% chance of picking the original ground truth and a 10% chance each of picking one of the back-translated candidates. Figure 15 shows the effect of this augmentation on LiT using an AugReg ImageNet21k pre-trained ViT-B/16 model. Backtranslation is fairly useful up to certain point, with 10% giving a good trade-off which improves all metrics.

## K. More de-duplication results

We present more ablation test results using larger architectures. We aim to check whether larger architectures benefit more from duplicates, while small architectures do not have enough capacity to overfit to the duplicates. More

Figure 15. Backtranslating data as a form of data augmentation improves performance across most metrics.

<table border="1">
<thead>
<tr>
<th>Dedup</th>
<th># up.</th>
<th># down.</th>
<th>ImgNet</th>
<th>I→T</th>
<th>T→I</th>
</tr>
</thead>
<tbody>
<tr>
<td>-</td>
<td>0</td>
<td>0</td>
<td>80.2</td>
<td>50.4</td>
<td>34.6</td>
</tr>
<tr>
<td>test</td>
<td>2.6M</td>
<td>76K</td>
<td>80.2</td>
<td>49.0</td>
<td>34.3</td>
</tr>
<tr>
<td>train+test</td>
<td>3.6M</td>
<td>220K</td>
<td>80.0</td>
<td>49.6</td>
<td>34.6</td>
</tr>
</tbody>
</table>

Table 9. Results on three different de-duplication setups, Lu setup with pre-trained ViT-L/16 image model.

specifically, we adopt the Lu setup with a pre-trained ViT-L/16 image model [69], and from-scratch L size text model. Table 9 shows the experimental results. We find that the conclusions are consistent with the runs using the ViT-B/32 image model discussed in Section 5.5. This is further evidence suggesting that duplications are not the root cause for good zero-shot transfer results.

## L. Image-text dataset comparison

Using simpler text filters for our dataset leads to a larger dataset size compared to the ALIGN dataset: The ALIGN dataset contains 1.8B image-text pairs, while our data set contains 3.6B image-text pairs.

In table 10, we show the results from training a baseline ViT-B/32 model on both datasets, with the same schedules.<table border="1">
<thead>
<tr>
<th>Task</th>
<th>Pairs Seen</th>
<th>our</th>
<th>ALIGN</th>
<th>Diff.</th>
</tr>
</thead>
<tbody>
<tr>
<td>ImageNet</td>
<td>900M</td>
<td>70.1</td>
<td>69.8</td>
<td>0.3</td>
</tr>
<tr>
<td>ImageNet</td>
<td>3.6B</td>
<td>72.0</td>
<td>71.5</td>
<td>0.5</td>
</tr>
<tr>
<td>ImageNet</td>
<td>7.2B</td>
<td>72.4</td>
<td>71.8</td>
<td>0.6</td>
</tr>
<tr>
<td>ImageNet</td>
<td>18B</td>
<td>72.9</td>
<td>72.2</td>
<td>0.7</td>
</tr>
</tbody>
</table>

Table 10. Comparing the ALIGN data with our data, which uses simpler text filters.

We vary the training schedule from 900M seen images, to 18B seen images. We use 18B images to make sure that the training process is long enough to benefit from a larger dataset. We find that the difference between the two datasets are small when the model is trained for a short period, i.e. less than a single epoch. As the training becomes longer, the impact of the dataset size becomes more visible.

Overall, the above results indicate that larger dataset with simpler filters slightly outperforms a smaller dataset with more filters. We leave the thorough exploration of this topic to future work.

## M. Qualitative examples

Though strong classification & retrieval performance is promising, it arguably probes understanding of very simple concepts. Are LiT models really zero-shot learners capable of understanding open vocabularies?

We touch here on a few qualities these models should ideally have, but note that these are not to be considered representative; benchmarks that investigate more than simply fine grained visual classification should be used to more thoroughly understand these phenomena.

### M.1. Private LiT model

In this section, we present model predictions with manually constructed image-text pairs input. Results from private LiT model are shown in Figure 16. We believe that with LiT, we successfully made a pre-trained image model to a zero-shot learner, that supports classification and retrieval with open vocabularies instead of a fixed label set.

### M.2. Multi-lingual model

Thanks to LiT on the multilingual dataset, the model also supports inputs using different languages. In Figure 17, we show results both in Thai and Chinese. The model recognized the “Songkran” event in Thai, and the “Chinese Spring Festival” event in Chinese; it nonetheless also ranks English translations or transliterations quite highly, which is likely reflective of the data distribution. Multilingual capability makes our models more inclusive and accessible to non-English speakers.

## M.3. Model failures

We present model failures in Figure 18. We show examples of how one can slightly change the text candidates to manipulate the model output; one can easily force a desired answer by tuning other text candidates to rank lower.- 70.3%: a man cooking pancake holding fork
- 12.5%: a man cooking pancake holding knife
- 11.2%: a man cooking breakfast holding fork
- 5.8%: a man cooking pancake
- 0.2%: a woman cooking pancake
- 0.0%: a man frying egg
- 0.0%: a man working in the kitchen
- 0.0%: a woman cooking breakfast holding fork

- 94.8%: Young woman with headache
- 4.0%: Sad woman
- 1.0%: Old woman with headache
- 0.1%: Happy woman
- 0.1%: Man with headache
- 0.1%: Young man with headache
- 0.0%: Sad man
- 0.0%: Old man with headache
- 0.0%: Happy man

**(a) Nuanced context:** The model can understand information such as actions or implied symptoms.

- 73.4%: a blue car parking in front of green and pink walls
- 15.0%: a pink car parking in front of green and blue walls
- 11.0%: a green car parking in front of blue and pink walls
- 0.2%: a pink car parking in front of blue and red walls
- 0.2%: a pink car parking in front of green and red walls
- 0.1%: a blue car parking in front of green and red walls
- 0.0%: a green car parking in front of blue and red walls

- 64.9%: red honda civic in front of a building
- 30.9%: red honda civic
- 2.7%: red honda civic in front of two towers
- 1.2%: honda civic
- 0.1%: black honda civic
- 0.1%: red car
- 0.1%: red honda accord
- 0.0%: car

**(b) Richer information:** The model correctly handles colours, background buildings and even car brands.

- 59.2%: an image of a bunch of cats
- 21.2%: an image of seven cats
- 12.9%: an image of eight cats
- 6.7%: an image of six cats
- 0.0%: an image of a bunch of dogs
- 0.0%: an image of eight dogs
- 0.0%: an image of six dogs
- 0.0%: an image of seven dogs

- 60.0%: an image of a bunch of cats
- 21.0%: an image of 6 cats
- 14.0%: an image of 8 cats
- 5.0%: an image of 7 cats
- 0.0%: an image of a bunch of dogs
- 0.0%: an image of 7 dogs
- 0.0%: an image of 8 dogs
- 0.0%: an image of 6 dogs

**(c) Counting:** The model does a reasonable job at counting, though prompts like “bunch of cats” are preferred.

- 28.3%: a cow sleeping on the beach
- 25.5%: a cow sleeping on the sand
- 16.0%: beach sleeping on a cow
- 15.8%: a cow on the beach
- 14.4%: a cow on the sand
- 0.0%: a cow sleeping on the grass
- 0.0%: a dog sleeping on the beach
- 0.0%: a sheep sleeping on the beach
- 0.0%: a cow on the grass

- 85.1%: alien astronaut in the street
- 13.1%: alien mask and astronaut costume
- 0.7%: an alien astronaut
- 0.6%: a NASA alien
- 0.5%: NASA found aliens but are hiding it
- 0.0%: an astronaut
- 0.0%: NASA
- 0.0%: alien
- 0.0%: person with grey skin and big eyes
- 0.0%: a plumber

**(d) Esoteric examples:** The model has no problems at identifying rare concepts, like a cow on a beach, or an astronaut alien.

Figure 16. Various model predictions.

- 43.8%: 中国新年庆祝活动
- 30.6%: Chinese new year celebration
- 13.5%: 人群在街上跳舞
- 9.5%: people dancing on street
- 1.0%: people fighting on street
- 0.5%: celebration
- 0.4%: new year
- 0.3%: 人群在街上打架
- 0.2%: 商家促销活动
- 0.1%: sales promotion

- 53.5%: Songkran
- 27.3%: Thai water festival
- 11.5%: ဆွန်ဆု
- 5.2%: Thai new year
- 1.5%: Huge waterfight
- 0.5%: People in the street
- 0.4%: Waterfight
- 0.0%: Firefighters

Figure 17. Training on multilingual data allows the model to recognise concepts in multiple languages, including visual concepts which do not directly exist in English.

- 52.2%: grinning face
- 25.4%: face with tears of joy
- 10.6%: rolling on the floor laughing
- 6.3%: yawning face
- 5.3%: loudly crying face

- 59.5%: emoji yawn
- 19.3%: emoji cry
- 14.7%: emoji smile
- 6.5%: emoji sleep

Figure 18. Qualitative failures. In the left example, the model ranks the wrong grinning face before the ground truth yawning face. However, by removing the grinning face and adding emoji prompt, the model prefers emoji yawn.<table border="1">
<thead>
<tr>
<th>Dataset</th>
<th>Prompts</th>
<th>Delta</th>
</tr>
</thead>
<tbody>
<tr>
<td>DTD v3.0.1</td>
<td>a <i>CLASS</i> texture</td>
<td>+0.6%</td>
</tr>
<tr>
<td>flowers v2.1.1</td>
<td>a <i>CLASS</i> flower</td>
<td>+1.1%</td>
</tr>
<tr>
<td>flowers v2.1.1</td>
<td>a <i>CLASS</i> plant</td>
<td>+0.4%</td>
</tr>
<tr>
<td>pets v3.2.0</td>
<td>a type of pet <i>CLASS</i></td>
<td>+1.0%</td>
</tr>
<tr>
<td>pets v3.2.0</td>
<td>a <i>CLASS</i> texture</td>
<td>+0.4%</td>
</tr>
<tr>
<td>pets v3.2.0</td>
<td><i>CLASS</i> , an animal</td>
<td>+0.7%</td>
</tr>
<tr>
<td>svhn v3.0.0</td>
<td>the number <i>CLASS</i></td>
<td>+3.0%</td>
</tr>
<tr>
<td>svhn v3.0.0</td>
<td>a street sign with the number <i>CLASS</i></td>
<td>+2.8%</td>
</tr>
<tr>
<td>camelyon v2.0.0</td>
<td>a histopathology slide showing <i>CLASS</i></td>
<td>+1.5%</td>
</tr>
<tr>
<td>camelyon v2.0.0</td>
<td>histopathology image of <i>CLASS</i></td>
<td>+0.9%</td>
</tr>
<tr>
<td>eurosat v2.0.0</td>
<td>a satellite photo of <i>CLASS</i></td>
<td>+3.2%</td>
</tr>
<tr>
<td>eurosat v2.0.0</td>
<td><i>CLASS</i> from above</td>
<td>+2.4%</td>
</tr>
<tr>
<td>eurosat v2.0.0</td>
<td>an aerial view of <i>CLASS</i></td>
<td>+3.3%</td>
</tr>
<tr>
<td>resisc v3.0.0</td>
<td>a satellite photo of <i>CLASS</i></td>
<td>+3.4%</td>
</tr>
<tr>
<td>resisc v3.0.0</td>
<td><i>CLASS</i> from above</td>
<td>+2.1%</td>
</tr>
<tr>
<td>resisc v3.0.0</td>
<td>an aerial view of <i>CLASS</i></td>
<td>+4.7%</td>
</tr>
<tr>
<td>retino v3.0.0</td>
<td>a retinal image with <i>CLASS</i></td>
<td>+9.7%</td>
</tr>
<tr>
<td>retino v3.0.0</td>
<td>a retina with <i>CLASS</i></td>
<td>+6.3%</td>
</tr>
<tr>
<td>retino v3.0.0</td>
<td>a fundus image with signs of <i>CLASS</i></td>
<td>+6.3%</td>
</tr>
<tr>
<td>clevr-count v3.1.0</td>
<td><i>CLASS</i> objects</td>
<td>+0.1%</td>
</tr>
<tr>
<td>clevr-count v3.1.0</td>
<td><i>CLASS</i> things</td>
<td>+0.2%</td>
</tr>
<tr>
<td>clevr-count v3.1.0</td>
<td>a photo of <i>CLASS</i> objects</td>
<td>+0.1%</td>
</tr>
<tr>
<td>dsprites-pos v2.0.0</td>
<td>an object located <i>CLASS</i></td>
<td>+0.0%</td>
</tr>
<tr>
<td>dsprites-orient v2.0.0</td>
<td>an object rotated at <i>CLASS</i></td>
<td>+0.1%</td>
</tr>
<tr>
<td>dsprites-orient v2.0.0</td>
<td>something rotated at <i>CLASS</i></td>
<td>+0.0%</td>
</tr>
<tr>
<td>dsprites-orient v2.0.0</td>
<td><i>CLASS</i> rotation</td>
<td>+0.0%</td>
</tr>
<tr>
<td>dsprites-orient v2.0.0</td>
<td>something at a <i>CLASS</i> angle</td>
<td>+0.0%</td>
</tr>
<tr>
<td>smallnorb-azmth v2.0.0</td>
<td>an object rotated at <i>CLASS</i></td>
<td>+0.0%</td>
</tr>
<tr>
<td>smallnorb-azmth v2.0.0</td>
<td>something rotated at <i>CLASS</i></td>
<td>+0.0%</td>
</tr>
<tr>
<td>smallnorb-azmth v2.0.0</td>
<td><i>CLASS</i> rotation</td>
<td>+0.0%</td>
</tr>
<tr>
<td>smallnorb-azmth v2.0.0</td>
<td>something at a <i>CLASS</i> angle</td>
<td>+0.0%</td>
</tr>
<tr>
<td>smallnorb-elev v2.0.0</td>
<td>an object rotated at <i>CLASS</i></td>
<td>+0.0%</td>
</tr>
<tr>
<td>smallnorb-elev v2.0.0</td>
<td>something rotated at <i>CLASS</i></td>
<td>+0.0%</td>
</tr>
<tr>
<td>smallnorb-elev v2.0.0</td>
<td><i>CLASS</i> rotation</td>
<td>+0.0%</td>
</tr>
<tr>
<td>smallnorb-elev v2.0.0</td>
<td>something at a <i>CLASS</i> angle</td>
<td>+0.0%</td>
</tr>
</tbody>
</table>

Table 11. Prompts swept over for VTAB tasks. Performance deltas are shown as mean test accuracy improvement per-task compared to just using the default three prompts. The default class names from TensorFlow Dataset (TFDS) are used in this table. TFDS versions are given alongside task names.Prompts:

- • the number  
  *CLASS*

Class names:

1. 1. *zero*
2. 2. *one*
3. 3. *two*
4. 4. *three*
5. 5. *four*
6. 6. *five*
7. 7. *six*
8. 8. *seven*
9. 9. *eight*
10. 10. *nine*

Delta: +2.3%

---

Prompts:

- • a street sign  
  with the number  
  *CLASS*

Class names:

1. 1. *zero*
2. 2. *one*
3. 3. *two*
4. 4. *three*
5. 5. *four*
6. 6. *five*
7. 7. *six*
8. 8. *seven*
9. 9. *eight*
10. 10. *nine*

Delta: +2.4%

---

Prompts:

- • a photo of  
  the number  
  *CLASS* written  
  on a sign
- • an outdoor house  
  number *CLASS*
- • the number  
  *CLASS* in the  
  center of the  
  image
- • an outdoor  
  number  
  *CLASS* written  
  on a sign
- • an outdoor  
  number *CLASS*
- • a centered image  
  of the number  
  *CLASS*

Class names:

1. 1. *0 · zero*
2. 2. *1 · one*
3. 3. *2 · two*
4. 4. *3 · three*
5. 5. *4 · four*
6. 6. *5 · five*
7. 7. *6 · six*
8. 8. *7 · seven*
9. 9. *8 · eight*
10. 10. *9 · nine*

Delta: +3.2%

------

**camelyon v2.0.0**

---

<table><tr><td><b>Prompts:</b></td><td><b>Class names:</b></td><td><b>Delta: +1.9%</b></td></tr><tr><td><ul><li>• a histopathology slide showing <i>CLASS</i></li></ul></td><td>1. <i>healthy lymph node tissue</i><br/>2. <i>a lymph node tumor</i></td><td></td></tr></table>

---

<table><tr><td><b>Prompts:</b></td><td><b>Class names:</b></td><td><b>Delta: +1.9%</b></td></tr><tr><td><ul><li>• histopathology image of <i>CLASS</i></li></ul></td><td>1. <i>healthy lymph node tissue</i><br/>2. <i>a lymph node tumor</i></td><td></td></tr></table>

---

<table><tr><td><b>Prompts:</b></td><td><b>Class names:</b></td><td><b>Delta: +0.8%</b></td></tr><tr><td><ul><li>• an example of <i>CLASS</i></li><li>• a histopathology slide of <i>CLASS</i></li><li>• an example histopathological image showing <i>CLASS</i></li><li>• a histopathology slide showing <i>CLASS</i></li><li>• patient's pathology examination indicates <i>CLASS</i></li><li>• a <i>CLASS</i> slide</li></ul></td><td>1. <i>healthy tissue</i> · <i>tissue</i><br/>2. <i>dangerous tissue</i> · <i>unhealthy tissue</i></td><td></td></tr></table>

---

**eurosat v2.0.0**

---

<table><tr><td><b>Prompts:</b></td><td><b>Class names:</b></td><td><b>Delta: +6.7%</b></td></tr><tr><td><ul><li>• an overhead view of <i>CLASS</i></li><li>• an aerial view of <i>CLASS</i></li><li>• an overhead image of <i>CLASS</i></li><li>• a satellite photo of <i>CLASS</i></li><li>• a satellite image of <i>CLASS</i></li><li>• photo of <i>CLASS</i> from the sky</li></ul></td><td>1. <i>farmland</i> · <i>farms</i> · <i>an annual crop</i><br/>2. <i>a forest</i> · <i>woodland</i> · <i>trees</i><br/>3. <i>a meadow</i> · <i>herbaceous vegetation</i> · <i>grass</i> · <i>fields</i><br/>4. <i>highway or road</i> · <i>motorways</i> · <i>highways</i> · <i>a street</i> · <i>roads</i><br/>5. <i>an urban area</i> · <i>an industrial area</i> · <i>an industrial zone</i> · <i>a city</i> · <i>factories</i><br/>6. <i>a pasture</i> · <i>farmland</i> · <i>farms</i><br/>7. <i>permanent crop</i> · <i>arable land</i> · <i>an orchard</i><br/>8. <i>a suburban area</i> · <i>a cul de sac</i> · <i>a residential area</i> · <i>houses</i><br/>9. <i>a canal</i> · <i>a river</i> · <i>a waterway</i> · <i>a stream</i><br/>10. <i>an ocean</i> · <i>a water</i> · <i>a sea</i> · <i>a reservoir</i></td><td></td></tr></table>

---Prompts:

- • a satellite image of *CLASS*
- • an aerial view of *CLASS*
- • a satellite photo of *CLASS*
- • *CLASS* from above

Class names:

1. 1. *an airplane* · *a plane* · *a flying plane*
2. 2. *an airfield* · *an airport* · *an aeroport*
3. 3. *baseball diamond* · *baseball court* · *baseball* · *baseball field*
4. 4. *basketball* · *a basketball court* · *an outdoor basketball court*
5. 5. *beach* · *sand*
6. 6. *a walkway* · *a bridge* · *a footbridge*
7. 7. *shrubland* · *chaparral* · *sparse plants* · *desert plants* · *shrubs* · *dry plants*
8. 8. *a church* · *a chapel*
9. 9. *circular farmland* · *circle farm*
10. 10. *cloudy sky* · *clouds* · *cloud*
11. 11. *a commercial area* · *a shopping mall* · *high street* · *shops*
12. 12. *densely populated area* · *lots of houses* · *a dense residential area* · *urban area*
13. 13. *a desert* · *barren land* · *sand dunes* · *wasteland*
14. 14. *woods* · *forest* · *woodland*
15. 15. *expressway* · *roads* · *highway* · *freeway*
16. 16. *golf fields* · *a golf course*
17. 17. *a running court* · *a track court* · *a ground track field*
18. 18. *a harbor* · *a dockyard* · *a haven* · *a jetty* · *a quay* · *a pier*
19. 19. *an industrial zone* · *an industrial area* · *industry*
20. 20. *a busy intersection* · *a crash on an intersection* · *intersection pileup* · *an intersection*
21. 21. *an island in the ocean* · *an island* · *land surrounded by water* · *an ocean island*
22. 22. *a reservoir* · *a lake* · *the ocean* · *the sea*
23. 23. *a pasture* · *a paddock* · *fields* · *grassland*
24. 24. *a medium residential area* · *cul de sac* · *suburban area* · *town*
25. 25. *a mobile home park* · *caravans* · *caravan park*
26. 26. *a mountain* · *a mountaintop* · *a hill* · *a mountain range*
27. 27. *an overpass*
28. 28. *a palace* · *a royal palace* · *a cheateau*
29. 29. *parking* · *a parking lot*
30. 30. *a train track* · *a train* · *a trainline* · *a rail track* · *a railway*
31. 31. *a railway station* · *a train station*
32. 32. *rectangular farmland* · *rectangle farms*
33. 33. *a river* · *a stream*
34. 34. *a roundabout*
35. 35. *runway* · *an airport runway* · *a landing strip*
36. 36. *an iceberg* · *ocean ice* · *sea ice*
37. 37. *a ship* · *a boat*
38. 38. *a snowberg*
39. 39. *sparsely populated area*
40. 40. *a stadium* · *an arena* · *a football stadium* · *a sports arena*
41. 41. *a storage tank* · *tank*
42. 42. *a tennis court* · *tennis* · *a court* · *a badminton court*
43. 43. *rural land* · *a terrace*
44. 44. *a power station* · *a thermal power station*
45. 45. *a marsh* · *wetland* · *peatland* · *a bog*

Delta: +5.1%---

**clevr-closest v3.1.0**

---

<table border="1"><tbody><tr><td>Prompts:<ul><li>• <i>CLASS</i> objects</li></ul></td><td>Class names:<ol><li>1. <i>massive</i></li><li>2. <i>very large</i></li><li>3. <i>large</i></li><li>4.</li><li>5. <i>small</i></li><li>6. <i>very small</i></li></ol></td><td>Delta: +0.3%</td></tr><tr><td>Prompts:<ul><li>• <i>CLASS</i> objects</li></ul></td><td>Class names:<ol><li>1. <i>very nearby</i></li><li>2. <i>nearby</i></li><li>3. <i>near</i></li><li>4.</li><li>5. <i>distant</i></li><li>6. <i>very distant</i></li></ol></td><td>Delta: +2.7%</td></tr><tr><td>Prompts:<ul><li>• <i>CLASS</i> shapes</li></ul></td><td>Class names:<ol><li>1. <i>massive</i></li><li>2. <i>very large</i></li><li>3. <i>large</i></li><li>4.</li><li>5. <i>small</i></li><li>6. <i>very small</i></li></ol></td><td>Delta: +0.6%</td></tr><tr><td>Prompts:<ul><li>• <i>CLASS</i> shapes</li></ul></td><td>Class names:<ol><li>1. <i>very nearby</i></li><li>2. <i>nearby</i></li><li>3. <i>near</i></li><li>4.</li><li>5. <i>distant</i></li><li>6. <i>very distant</i></li></ol></td><td>Delta: +3.9%</td></tr><tr><td>Prompts:<ul><li>• <i>CLASS</i> thing</li><li>• the nearest shape in this image is <i>CLASS</i></li><li>• the closest shape in this rendered image is <i>CLASS</i></li><li>• the closest shape in this image is <i>CLASS</i></li></ul></td><td>Class names:<ol><li>1. <i>huge</i> · <i>super near</i></li><li>2. <i>nearby</i></li><li>3. <i>big</i> · <i>large</i></li><li>4. <i>quite small</i> · <i>medium sized</i> · <i>normal sized</i></li><li>5. <i>small</i> · <i>distant</i></li><li>6. <i>very small</i> · <i>very distant</i></li></ol></td><td>Delta: +1.8%</td></tr></tbody></table>

---**clevr-count v3.1.0**

<table border="1">
<tbody>
<tr>
<td style="vertical-align: top;">
<b>Prompts:</b><br/>
<ul>
<li>• <i>CLASS</i> objects</li>
</ul>
</td>
<td style="vertical-align: top;">
<b>Class names:</b><br/>
          1. <i>three</i><br/>
          2. <i>four</i><br/>
          3. <i>five</i><br/>
          4. <i>six</i><br/>
          5. <i>seven</i><br/>
          6. <i>eight</i><br/>
          7. <i>nine</i><br/>
          8. <i>ten</i>
</td>
<td style="vertical-align: top; text-align: right;">
          Delta: +0.4%
        </td>
</tr>
<tr>
<td style="vertical-align: top;">
<b>Prompts:</b><br/>
<ul>
<li>• <i>CLASS</i> things</li>
</ul>
</td>
<td style="vertical-align: top;">
<b>Class names:</b><br/>
          1. <i>three</i><br/>
          2. <i>four</i><br/>
          3. <i>five</i><br/>
          4. <i>six</i><br/>
          5. <i>seven</i><br/>
          6. <i>eight</i><br/>
          7. <i>nine</i><br/>
          8. <i>ten</i>
</td>
<td style="vertical-align: top; text-align: right;">
          Delta: +0.6%
        </td>
</tr>
<tr>
<td style="vertical-align: top;">
<b>Prompts:</b><br/>
<ul>
<li>• a photo of<br/><i>CLASS</i> objects</li>
</ul>
</td>
<td style="vertical-align: top;">
<b>Class names:</b><br/>
          1. <i>three</i><br/>
          2. <i>four</i><br/>
          3. <i>five</i><br/>
          4. <i>six</i><br/>
          5. <i>seven</i><br/>
          6. <i>eight</i><br/>
          7. <i>nine</i><br/>
          8. <i>ten</i>
</td>
<td style="vertical-align: top; text-align: right;">
          Delta: +0.7%
        </td>
</tr>
<tr>
<td style="vertical-align: top;">
<b>Prompts:</b><br/>
<ul>
<li>• a picture of<br/><i>CLASS</i></li>
<li>• there are <i>CLASS</i></li>
<li>• there are<br/><i>CLASS</i> in the<br/>image</li>
<li>• a rendered image<br/>of <i>CLASS</i></li>
</ul>
</td>
<td style="vertical-align: top;">
<b>Class names:</b><br/>
          1. <i>3 objects · three objects · 3 shapes · three shapes</i><br/>
          2. <i>4 objects · four objects · 4 shapes · four shapes</i><br/>
          3. <i>5 objects · five objects · 5 shapes · five shapes</i><br/>
          4. <i>6 objects · six objects · 6 shapes · six shapes</i><br/>
          5. <i>7 objects · seven objects · 7 shapes · seven shapes</i><br/>
          6. <i>8 objects · eight objects · 8 shapes · eight shapes</i><br/>
          7. <i>9 objects · nine objects · 9 shapes · nine shapes</i><br/>
          8. <i>10 objects · ten objects · 10 shapes · ten shapes</i>
</td>
<td style="vertical-align: top; text-align: right;">
          Delta: +1.2%
        </td>
</tr>
</tbody>
</table>

Table 12. Prompts and customized class names swept over for VTAB tasks. Performance deltas are shown as mean test accuracy improvement per-task compared to just using the default three prompts.<table border="1">
<thead>
<tr>
<th>Ref</th>
<th>Dataset</th>
<th>Images</th>
<th>Cfg</th>
<th>H</th>
<th>Image</th>
<th>Text</th>
<th>Tok</th>
<th>Inits</th>
<th>Optim</th>
<th>LR</th>
<th>WD</th>
<th>INet</th>
<th>T→I</th>
<th>I→T</th>
<th>Vn</th>
<th>Vsp</th>
<th>Vst</th>
</tr>
</thead>
<tbody>
<tr>
<td>Fig 1</td>
<td>YFCC<sub>CLIP</sub></td>
<td>983M</td>
<td>LU</td>
<td>y</td>
<td>vit-B/32</td>
<td>bert-base</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>63.6</td>
<td>22.1</td>
<td>37.6</td>
<td>59.3</td>
<td>35.0</td>
<td>12.7</td>
</tr>
<tr>
<td>Fig 1</td>
<td>YFCC<sub>CLIP</sub></td>
<td>983M</td>
<td>UU</td>
<td>y</td>
<td>vit-B/32</td>
<td>bert-base</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adam</td>
<td>3e-4</td>
<td>1e-5</td>
<td>53.3</td>
<td>23.4</td>
<td>37.6</td>
<td>54.9</td>
<td>44.4</td>
<td>14.1</td>
</tr>
<tr>
<td>Fig 1</td>
<td>YFCC<sub>CLIP</sub></td>
<td>983M</td>
<td>uu</td>
<td>y</td>
<td>vit-B/32</td>
<td>bert-base</td>
<td>WP</td>
<td>-,-</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>42.1</td>
<td>17.9</td>
<td>31.1</td>
<td>45.8</td>
<td>49.8</td>
<td>14.3</td>
</tr>
<tr>
<td>Tab 1</td>
<td>Ours</td>
<td>18.2B</td>
<td>Lu</td>
<td>n</td>
<td>vit-g/14*</td>
<td>vit-giant</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>85.2</td>
<td>41.9</td>
<td>59.3</td>
<td>74.7</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>Tab 1</td>
<td>Mixed</td>
<td>983M</td>
<td>LU</td>
<td>y</td>
<td>vit-L/16</td>
<td>bert-large</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adaf</td>
<td>8e-4</td>
<td>1e-4</td>
<td>75.7</td>
<td>31.2</td>
<td>48.5</td>
<td>63.1</td>
<td>50.3</td>
<td>14.1</td>
</tr>
<tr>
<td>Tab 2</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-B/32</td>
<td>vit-base</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>70.1</td>
<td>28.6</td>
<td>43.8</td>
<td>66.6</td>
<td>57.2</td>
<td>14.6</td>
</tr>
<tr>
<td>Tab 2</td>
<td>Ours</td>
<td>901M</td>
<td>Uu</td>
<td>y</td>
<td>vit-B/32</td>
<td>vit-base</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>57.2</td>
<td>27.0</td>
<td>40.1</td>
<td>60.1</td>
<td>58.0</td>
<td>15.0</td>
</tr>
<tr>
<td>Tab 2</td>
<td>Ours</td>
<td>901M</td>
<td>uu</td>
<td>y</td>
<td>vit-B/32</td>
<td>vit-base</td>
<td>SP</td>
<td>-,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>50.6</td>
<td>24.1</td>
<td>38.9</td>
<td>55.3</td>
<td>38.9</td>
<td>16.5</td>
</tr>
<tr>
<td>Tab 3</td>
<td>YFCC<sub>CLIP</sub></td>
<td>246M</td>
<td>LU</td>
<td>y</td>
<td>dino-B/16</td>
<td>bert-base</td>
<td>WP</td>
<td>vit,Bert</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>55.5</td>
<td>18.2</td>
<td>33.4</td>
<td>51.5</td>
<td>45.4</td>
<td>14.8</td>
</tr>
<tr>
<td>Tab 3</td>
<td>YFCC<sub>CLIP</sub></td>
<td>246M</td>
<td>LU</td>
<td>y</td>
<td>mocov3-B/16</td>
<td>bert-base</td>
<td>WP</td>
<td>vit,Bert</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>55.4</td>
<td>17.6</td>
<td>33.5</td>
<td>50.8</td>
<td>40.5</td>
<td>12.8</td>
</tr>
<tr>
<td>Tab 6</td>
<td>CC12M</td>
<td>200M</td>
<td>LU</td>
<td>n</td>
<td>vit-B/32</td>
<td>bert-base</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-4</td>
<td>60.7</td>
<td>25.0</td>
<td>41.3</td>
<td>57.7</td>
<td>49.6</td>
<td>13.9</td>
</tr>
<tr>
<td>Tab 6</td>
<td>CC12M</td>
<td>200M</td>
<td>LU</td>
<td>n</td>
<td>bit-50x1</td>
<td>bert-base</td>
<td>WP</td>
<td>M,Bert</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-4</td>
<td>55.2</td>
<td>23.9</td>
<td>37.3</td>
<td>53.2</td>
<td>49.3</td>
<td>14.3</td>
</tr>
<tr>
<td>Tab 6</td>
<td>CC12M</td>
<td>200M</td>
<td>LU</td>
<td>n</td>
<td>mixer-B/32</td>
<td>bert-base</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-4</td>
<td>57.1</td>
<td>22.9</td>
<td>37.5</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>Tab 4</td>
<td>YFCC</td>
<td>901M</td>
<td>LU</td>
<td>y</td>
<td>vit-B/32</td>
<td>mt5-base</td>
<td>SP</td>
<td>AR,mt5</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>59.3</td>
<td>17.4</td>
<td>28.7</td>
<td>55.5</td>
<td>47.3</td>
<td>15.2</td>
</tr>
<tr>
<td>Tab 4</td>
<td>YFCC</td>
<td>901M</td>
<td>Lu</td>
<td>y</td>
<td>vit-B/32</td>
<td>vit-base</td>
<td>WP</td>
<td>AR,-</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>56.4</td>
<td>17.3</td>
<td>28.2</td>
<td>53.3</td>
<td>47.4</td>
<td>14.1</td>
</tr>
<tr>
<td>Tab 4</td>
<td>YFCC</td>
<td>901M</td>
<td>LU</td>
<td>y</td>
<td>vit-B/32</td>
<td>bert-base</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>59.5</td>
<td>20.7</td>
<td>36.3</td>
<td>56.7</td>
<td>51.3</td>
<td>12.3</td>
</tr>
<tr>
<td>Tab 4</td>
<td>YFCC</td>
<td>901M</td>
<td>Lu</td>
<td>y</td>
<td>vit-B/32</td>
<td>mt5-base</td>
<td>SP</td>
<td>AR,-</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>58.1</td>
<td>16.4</td>
<td>28.3</td>
<td>54.7</td>
<td>41.8</td>
<td>14.4</td>
</tr>
<tr>
<td>Tab 4</td>
<td>YFCC</td>
<td>901M</td>
<td>LU</td>
<td>y</td>
<td>vit-B/32</td>
<td>bert-base</td>
<td>WP</td>
<td>AR,-</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>58.8</td>
<td>20.0</td>
<td>35.2</td>
<td>55.2</td>
<td>51.8</td>
<td>14.6</td>
</tr>
<tr>
<td>Tab 4</td>
<td>YFCC</td>
<td>901M</td>
<td>Lu</td>
<td>y</td>
<td>vit-B/32</td>
<td>vit-base</td>
<td>SP</td>
<td>AR,-</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-4</td>
<td>57.2</td>
<td>16.9</td>
<td>29.7</td>
<td>54.6</td>
<td>47.4</td>
<td>13.5</td>
</tr>
<tr>
<td>Tab 4</td>
<td>YFCC</td>
<td>901M</td>
<td>LU</td>
<td>y</td>
<td>vit-B/32</td>
<td>t5-base</td>
<td>SP</td>
<td>AR,t5</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-4</td>
<td>59.2</td>
<td>18.4</td>
<td>31.0</td>
<td>57.1</td>
<td>47.6</td>
<td>14.1</td>
</tr>
<tr>
<td>Tab 4</td>
<td>YFCC</td>
<td>901M</td>
<td>LU</td>
<td>y</td>
<td>vit-B/32</td>
<td>t5-base</td>
<td>SP</td>
<td>AR,-</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-4</td>
<td>57.8</td>
<td>17.2</td>
<td>29.4</td>
<td>54.5</td>
<td>46.3</td>
<td>13.2</td>
</tr>
<tr>
<td>Fig 7</td>
<td>CC12M</td>
<td>200M</td>
<td>LU</td>
<td>n</td>
<td>vit-B/16</td>
<td>bert-large</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adaf</td>
<td>1e-3</td>
<td>1e-4</td>
<td>66.9</td>
<td>28.3</td>
<td>44.8</td>
<td>58.6</td>
<td>45.4</td>
<td>13.5</td>
</tr>
<tr>
<td>Fig 7</td>
<td>CC12M</td>
<td>200M</td>
<td>LU</td>
<td>n</td>
<td>vit-L/16</td>
<td>bert-large</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adaf</td>
<td>1e-3</td>
<td>1e-4</td>
<td>67.6</td>
<td>26.9</td>
<td>42.6</td>
<td>57.8</td>
<td>50.3</td>
<td>13.0</td>
</tr>
<tr>
<td>Fig 7</td>
<td>CC12M</td>
<td>200M</td>
<td>LU</td>
<td>n</td>
<td>vit-B/16</td>
<td>bert-base</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-4</td>
<td>66.1</td>
<td>28.2</td>
<td>45.3</td>
<td>59.0</td>
<td>50.6</td>
<td>14.0</td>
</tr>
<tr>
<td>Fig 7</td>
<td>CC12M</td>
<td>200M</td>
<td>LU</td>
<td>n</td>
<td>vit-L/16</td>
<td>bert-base</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-4</td>
<td>66.8</td>
<td>26.6</td>
<td>44.3</td>
<td>58.6</td>
<td>45.6</td>
<td>12.7</td>
</tr>
<tr>
<td>Fig 7</td>
<td>CC12M</td>
<td>200M</td>
<td>LU</td>
<td>n</td>
<td>vit-B/32</td>
<td>bert-large</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adaf</td>
<td>1e-3</td>
<td>1e-4</td>
<td>61.7</td>
<td>25.4</td>
<td>41.4</td>
<td>56.4</td>
<td>49.9</td>
<td>13.6</td>
</tr>
<tr>
<td>Fig 7</td>
<td>CC12M</td>
<td>200M</td>
<td>LU</td>
<td>n</td>
<td>vit-B/32</td>
<td>bert-base</td>
<td>WP</td>
<td>AR,Bert</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-4</td>
<td>61.1</td>
<td>24.9</td>
<td>40.9</td>
<td>56.8</td>
<td>49.6</td>
<td>15.4</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-g/14</td>
<td>vit-huge</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>81.8</td>
<td>33.1</td>
<td>48.9</td>
<td>70.6</td>
<td>61.4</td>
<td>15.2</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-g/14</td>
<td>vit-large</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>81.2</td>
<td>32.9</td>
<td>48.5</td>
<td>69.2</td>
<td>50.5</td>
<td>15.3</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-L/16</td>
<td>vit-huge</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>80.8</td>
<td>35.6</td>
<td>51.2</td>
<td>69.2</td>
<td>50.3</td>
<td>13.5</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-L/16</td>
<td>vit-large</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>80.3</td>
<td>34.8</td>
<td>49.8</td>
<td>68.9</td>
<td>60.3</td>
<td>14.8</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-g/14</td>
<td>vit-base</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>79.5</td>
<td>30.7</td>
<td>45.9</td>
<td>68.6</td>
<td>59.6</td>
<td>12.6</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-B/16</td>
<td>vit-huge</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>77.1</td>
<td>34.5</td>
<td>49.7</td>
<td>68.0</td>
<td>59.7</td>
<td>14.0</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-L/16</td>
<td>vit-base</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>78.5</td>
<td>33.5</td>
<td>48.6</td>
<td>68.2</td>
<td>61.0</td>
<td>13.8</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-B/16</td>
<td>vit-large</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>76.8</td>
<td>33.6</td>
<td>49.4</td>
<td>68.5</td>
<td>45.0</td>
<td>14.2</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-B/16</td>
<td>vit-base</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>75.2</td>
<td>31.9</td>
<td>46.8</td>
<td>67.5</td>
<td>57.7</td>
<td>12.8</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-B/32</td>
<td>vit-huge</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>72.2</td>
<td>31.2</td>
<td>46.4</td>
<td>68.3</td>
<td>55.1</td>
<td>13.8</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-B/32</td>
<td>vit-large</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>71.6</td>
<td>30.7</td>
<td>45.6</td>
<td>66.4</td>
<td>55.0</td>
<td>14.5</td>
</tr>
<tr>
<td>Fig 7</td>
<td>Ours</td>
<td>901M</td>
<td>Lu</td>
<td>n</td>
<td>vit-B/32</td>
<td>vit-base</td>
<td>SP</td>
<td>JFT,-</td>
<td>Adaf</td>
<td>1e-3</td>
<td>0</td>
<td>70.0</td>
<td>29.2</td>
<td>43.8</td>
<td>65.8</td>
<td>56.9</td>
<td>12.0</td>
</tr>
<tr>
<td>Fig 5</td>
<td>YFCC<sub>CLIP</sub></td>
<td>983M</td>
<td>LU</td>
<td>y</td>
<td>vit-B/32</td>
<td>mt5-base</td>
<td>SP</td>
<td>AR,mt5</td>
<td>Adam</td>
<td>3e-4</td>
<td>1e-4</td>
<td>58.4</td>
<td>15.6</td>
<td>25.1</td>
<td>54.5</td>
<td>36.7</td>
<td>12.3</td>
</tr>
<tr>
<td>Fig 5</td>
<td>YFCC<sub>CLIP</sub></td>
<td>983M</td>
<td>LU</td>
<td>y</td>
<td>vit-B/32</td>
<td>t5-base</td>
<td>SP</td>
<td>AR,t5</td>
<td>Adam</td>
<td>3e-4</td>
<td>1e-4</td>
<td>58.5</td>
<td>17.2</td>
<td>29.1</td>
<td>54.7</td>
<td>40.4</td>
<td>13.6</td>
</tr>
<tr>
<td>Fig 5</td>
<td>YFCC<sub>CLIP</sub></td>
<td>983M</td>
<td>Lu</td>
<td>y</td>
<td>vit-B/32</td>
<td>mt5-base</td>
<td>SP</td>
<td>AR,-</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-5</td>
<td>58.7</td>
<td>14.4</td>
<td>23.1</td>
<td>53.1</td>
<td>41.3</td>
<td>14.7</td>
</tr>
<tr>
<td>Fig 5</td>
<td>YFCC<sub>CLIP</sub></td>
<td>983M</td>
<td>Lu</td>
<td>y</td>
<td>vit-B/32</td>
<td>t5-base</td>
<td>SP</td>
<td>AR,-</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>58.9</td>
<td>14.5</td>
<td>22.6</td>
<td>53.1</td>
<td>41.6</td>
<td>15.0</td>
</tr>
<tr>
<td>Fig 5</td>
<td>YFCC</td>
<td>983M</td>
<td>LU</td>
<td>y</td>
<td>vit-B/32</td>
<td>mt5-base</td>
<td>SP</td>
<td>AR,mt5</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>62.6</td>
<td>18.9</td>
<td>33.6</td>
<td>59.0</td>
<td>47.6</td>
<td>13.8</td>
</tr>
<tr>
<td>Fig 5</td>
<td>YFCC</td>
<td>983M</td>
<td>Lu</td>
<td>y</td>
<td>vit-B/32</td>
<td>mt5-base</td>
<td>SP</td>
<td>AR,-</td>
<td>Adam</td>
<td>8e-4</td>
<td>1e-4</td>
<td>62.1</td>
<td>18.5</td>
<td>32.6</td>
<td>58.7</td>
<td>50.0</td>
<td>14.8</td>
</tr>
<tr>
<td>Fig 5</td>
<td>YFCC</td>
<td>983M</td>
<td>Lu</td>
<td>y</td>
<td>vit-B/32</td>
<td>t5-base</td>
<td>SP</td>
<td>AR,-</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-4</td>
<td>62.4</td>
<td>19.6</td>
<td>34.3</td>
<td>60.8</td>
<td>31.5</td>
<td>14.8</td>
</tr>
<tr>
<td>Fig 5</td>
<td>YFCC</td>
<td>983M</td>
<td>LU</td>
<td>y</td>
<td>vit-B/32</td>
<td>t5-base</td>
<td>SP</td>
<td>AR,t5</td>
<td>Adam</td>
<td>1e-3</td>
<td>1e-4</td>
<td>62.3</td>
<td>20.1</td>
<td>34.5</td>
<td>61.1</td>
<td>50.3</td>
<td>14.6</td>
</tr>
</tbody>
</table>

Table 13. Detailed configuration and metrics for a selection of models. *Ref* describes the Figure/Table where the model is mentioned. *Dataset* describes the dataset that was used (see Section 4), with “Mixed” referring to alternating batches between CC12M and YFCC100m. *Images* is the number of images seen during contrastive-tuning. Default batch size was 16 384 (only exception model “g/14\*” with 32 768). *Cfg* first letter refers to image tower, second letter to text tower (Section 5.2). *H* describes whether a linear head was added to the image tower (note that the text tower always has a linear head). *Image* describes the image tower (all models use 224px input resolution apart from “g/14\*” that uses 288px), for details on models see [5, 11, 21, 33, 61, 69]. *Text* describes the text tower, for details see [17, 21, 47, 67]. *Tok* describes whether a SentencePiece or WordPiece tokenizer was used. *Inits* describes the initializations of the image/text towers (AR refers to AugReg “recommended checkpoints” [55]). *Optim* is the optimizer, using default Adam or Adafactor [53]. *LR* is the base learning rate (with linear ramp-up and cosine decay). *WD* is the weight decay (using “decoupled” weight decay [40]). *INet* describes zero-shot top-1 accuracy on Imagenet. *T→I* and *I→T* describe retrieval recall @1 on the MSCOCO test set. *Vn*, *Vsp*, *Vst* VTAB [70] results for “natural”, “specialized”, and “structured” subsets.


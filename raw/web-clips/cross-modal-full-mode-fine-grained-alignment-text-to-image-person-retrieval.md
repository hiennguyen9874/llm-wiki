Hao Yin [yinhao1102@std.uestc.edu.cn](mailto:yinhao1102@std.uestc.edu.cn), Xin Man [manxin@std.uestc.edu.cn](mailto:manxin@std.uestc.edu.cn) Shenzhen Institute for Advanced Study, University of Electronic Science and Technology of ChinaShenzhenChina518110, Feiyu Chen [chenfeiyu@uestc.edu.cn](mailto:chenfeiyu@uestc.edu.cn), Jie Shao [shaojie@uestc.edu.cn](mailto:shaojie@uestc.edu.cn) and Heng Tao Shen [shenhengtao@hotmail.com](mailto:shenhengtao@hotmail.com) University of Electronic Science and Technology of ChinaChengduChina611731Sichuan Artificial Intelligence Research InstituteYibinChina644000

(XX XXX 2025)

###### Abstract.

Text-to-Image Person Retrieval (TIPR) is a cross-modal matching task designed to identify the person images that best correspond to a given textual description. The key difficulty in TIPR is to realize robust correspondence between the textual and visual modalities within a unified latent representation space. To address this challenge, prior approaches incorporate attention mechanisms for implicit cross-modal local alignment. However, they lack the ability to verify whether all local features are correctly aligned. Moreover, existing methods tend to emphasize the utilization of hard negative samples during model optimization to strengthen discrimination between positive and negative pairs, often neglecting incorrectly matched positive pairs. To mitigate these problems, we propose FMFA, a cross-modal Full-Mode Fine-grained Alignment framework, which enhances global matching through explicit fine-grained alignment and existing implicit relational reasoning—hence the term “full-mode”—without introducing extra supervisory signals. In particular, we propose an Adaptive Similarity Distribution Matching (A-SDM) module to rectify unmatched positive sample pairs. A-SDM adaptively pulls the unmatched positive pairs closer in the joint embedding space, thereby achieving more precise global alignment. Additionally, we introduce an Explicit Fine-grained Alignment (EFA) module, which makes up for the lack of verification capability of implicit relational reasoning. EFA strengthens explicit cross-modal fine-grained interactions by sparsifying the similarity matrix and employs a hard coding method for local alignment. We evaluate our method on three public datasets, where it attains state-of-the-art results among all global matching methods. The code for our method is publicly accessible at [https://github.com/yinhao1102/FMFA](https://github.com/yinhao1102/FMFA).

Cross-modal retrieval, Person search, Fine-grained alignment

## 1\. Introduction

Text-to-Image Person Retrieval (TIPR) seeks to understand natural language descriptions and identify the most relevant person image within a large gallery (lu2019vilbert). Unlike general image-text retrieval (wang2017adversarial; sogi2024object; chen2024make; chen2023vilem; wang2025geometric), which tends to achieve semantic-based matching between text and image, TIPR is specifically designed for identifying individuals. TIPR requires the accurate modeling of fine-grained correspondences between textual and visual modalities, owing to the large intra-class variance and small inter-class difference. This substantial intra-class variation arises from two aspects: (1) visual appearances of the same identity exhibit dramatic variations under different poses, viewpoints, and illumination conditions, and (2) textual descriptions are influenced by differences in phrasing, word order and textual ambiguities. Therefore, the primary challenges in TIPR are how to extract discriminative global representations from image-text pairs and how to achieve precise cross-modal fine-grained alignment. Existing methods for tackling these challenges can be roughly divided into two main categories: global matching methods and local matching methods.

Some global matching methods (zhang2018deep; zheng2020dual) obtain discriminative global representations by aligning images and texts, which are projected into a joint embedding space. Their widely adopted loss functions include the Cross-Modal Projection Matching (CMPM) loss (zhang2018deep) and the Similarity Distribution Matching (SDM) loss (jiang2023cross). The CMPM loss highlights the gap between the scalar projections of image-text pairs and their matched label indicators. In comparison, the SDM loss boosts global matching performance by minimizing the Kullback-Leibler (KL) divergence between the normalized similarity profile of image-text pairs and the true label distribution. In addition, the SDM loss incorporates a temperature hyperparameter to make model updates concentrate on hard negative samples, yet it leads to the neglect of unmatched positive pairs, as shown in Figure 1(a). However, in TIPR, the accurate matching of positive pairs is prioritized over merely distinguishing between positive and negative pairs. Meanwhile, some local matching methods (bai2023rasa; park2024plot; ergasti2025mars) incorporate attention mechanisms to achieve cross-modal fine-grained alignment. For instance, RaSa (bai2023rasa) constructs a cross-modal encoder to generate multimodal representations for subsequent fine-grained alignment. Building on RaSa, MARS (ergasti2025mars) integrates a Masked AutoEncoder (MAE) decoder (he2022masked) to reconstruct masked image patch sequences into their original unmasked form, thereby facilitating cross-modal fine-grained alignment. However, these methods rely on attention mechanisms to implicitly aggregate local image-text representations. As a result, they yield only the final multimodal representation, without revealing the details of the aggregation process. Consequently, these implicit aggregation methods make it difficult to determine whether the aggregated multimodal representations correctly encode the corresponding visual and textual information.

![Refer to caption](https://arxiv.org/html/2509.13754v2/x1.png)

(a) Existing global matching methods.

To remedy these concerns, we propose FMFA, a cross-modal Full-Mode Fine-grained Alignment framework, which enhances global matching through full-mode fine-grained alignment, including explicit fine-grained image-text alignment and existing implicit relational reasoning. Specifically, we design an Adaptive Similarity Distribution Matching (A-SDM) module to ensure the correct matching of positive image-text pairs. Within the joint embedding space, the A-SDM module adaptively pulls positive pairs closer together. In cases of mismatched positive pairs, the A-SDM module adaptively regulates the pulling force based on their relative distance within the joint embedding space, as shown in Figure 1(b), thus improving cross-modal global alignment. Based on the insight that each word in a caption can be associated with several image patches (bica2024improving), we introduce an Explicit Fine-Grained Alignment (EFA) module. The EFA module derives multimodal representations through explicit aggregation with a sparse similarity matrix. During this process, the sparse similarity matrix between text and image reflects the contribution of textual and visual representations to the final multimodal representation. To minimize redundancy and reduce the computational cost during training, the EFA module employs hard coding alignment between the aggregated multimodal representation and its original visual and textual representations. These designs allow EFA to realize fine-grained cross-modal interactions and assist the backbone network in learning more distinctive global image-text representations without introducing additional supervision. FMFA is evaluated on three public benchmarks (li2017person; ding2021semantically; zhu2021dssl), and it attains competitive top-level performance along with high inference efficiency. We highlight our key contributions below:

- We introduce FMFA to explicitly leverage fine-grained interactions for improving cross-modal alignment, without incurring extra supervision or inference overhead.
- We present an adaptive similarity distribution matching module aimed at precisely aligning image-text pairs in a shared embedding space. It adaptively adjusts to narrow the distance between mismatched positive pairs, ensuring more precise matching.
- We develop an explicit fine-grained alignment module, which leverages the sparse similarity matrix for explicit aggregation and employs a hard coding method in cross-modal fine-grained alignment to minimize redundant information.

## 2\. Related Work

Text-to-Image Person Retrieval (TIPR) was initially proposed by Li et al. (li2017person), who created the CUHK-PEDES dataset. Unlike visual-based person retrieval (cheng2022hybrid; cheng2025semantic; he2025exploring; yang2025feature), the core challenge of TIPR lies in constructing a shared latent space that enables coherent alignment between visual and textual representations. Existing methods can be typically classified into global and local matching approaches.

Early global methods (zheng2020dual; zhu2021dssl) directly aligned the global representations of images and text in a joint embedding space. Schroff et al. (schroff2015facenet) proposed a triplet ranking loss to enforce a margin constraint between positive and negative pairs, and Zhang et al. (zhang2018deep) introduced the CMPM/C loss to minimize the discrepancy between the scalar projection of image-text pairs and their labels. However, these global methods lack cross-modal fine-grained interactions, which restrict their ability to capture detailed semantic correspondences. To address this limitation, early local matching methods (wang2020vitaa; gao2021contextual; shao2022learning) explicitly aligned local visual and textual features to achieve fine-grained cross-modal interactions. Nevertheless, they rely on unimodal pre-trained models (e.g., BERT (devlin2019bert) and ResNet (he2016deep)), failing to exploit the strong cross-modal alignment capability of recent pre-trained Vision-Language Models (VLMs) (li22blip; yan2023clip; li2021align).

Recent local matching methods (ergasti2025mars; lu2025prompt; qin2024noisy; wu2024text; huang2025cross) have benefited greatly from VLMs and introduced VLMs to enhance cross-modal alignment. Park et al. (park2024plot) utilized a modified Contrastive Language-Image Pre-training (CLIP) (radford2021learning) model as the feature extractor and designed a slot attention-based (locatello2020object) part discovery module to identify discriminative human parts without extra supervision, while Bai et al. (bai2023rasa) used the align-before-fuse model (li2021align) as the backbone and introduced a cross-modal encoder for fine-grained alignment. Although effective, these methods involve complex computations during inference, leading to high time and memory costs, which limit their applicability to real-time systems.

On another line of research, several studies (yang2023towards; shao2023unified; tan2024harnessing) have explored leveraging large-scale image-text pairs in the person Re-IDentification (ReID) domain to VLMs. Zuo et al. (zuo2024plip) utilized CUHK-PEDES and ICFG-PEDES to train an image captioner, aiming to generate comprehensive textual descriptions for pedestrian images. Yang et al. (yang2023towards) employed BLIP-2 (li2023blip2) to produce attribute-aware captions for diffusion-generated pedestrian images (rombach2022high), while Jiang et al. (jiang2025modeling) leveraged recent Multi-modal Large Language Models (MLLMs), such as Qwen-VL (bai2023qwenvl) and LLaVA (liu2024llavanext), to automatically annotate large-scale ReID datasets in a human-like manner. The CLIP models pre-trained on large-scale ReID datasets exhibit strong zero-shot performance. Their compatibility with global matching methods—which relies solely on global features and has a simple inference pipeline—makes them particularly suitable for direct fine-tuning in such settings.

Recent global matching methods (shu2022see; he23vgsg; jiang2023cross) have integrated local fine-grained alignment modules into global matching frameworks to obtain more discriminative global representations. Shu et al. (shu2022see) introduced a bidirectional mask modeling mechanism that randomly masks image patches and text words, encouraging the model to infer missing semantics and implicitly learn local visual-textual correspondences. He et al. (he23vgsg) proposed the Vision-Guided Semantic-Group (VGSG) network to cluster textual tokens into semantic groups and align them with corresponding visual regions under the guidance of vision features, achieving group-level fine-grained alignment within a global representation space. Similarly, Jiang et al. (jiang2023cross) developed IRRA to employ an Implicit Relation Reasoning (IRR) module based on attention mechanisms to capture latent cross-modal relations, enhancing global alignment. Although these methods enhance fine-grained cross-modal interactions within global matching frameworks, their implicit or group-level alignment strategies may still fail to guarantee precise local correspondences. In light of these limitations, we propose FMFA, which aims to enhance the global matching ability of the model by achieving cross-modal full-mode fine-grained alignment, including explicit fine-grained alignment and implicit relation reasoning.

![Refer to caption](https://arxiv.org/html/2509.13754v2/x3.png)

(a) The architecture of FMFA.

## 3\. Method

This section introduces the proposed FMFA framework. Figure 2 presents an overview of FMFA, and further details of the framework are elaborated in the subsequent subsections.

### 3.1. Feature Extraction

Motivated by the success of IRRA (jiang2023cross), we use the modified full CLIP (radford2021learning) visual and textual encoders to enhance cross-modal alignment capabilities while reducing inference costs.

Visual Modality. Given an input image $I\in\mathbb{R}^{H\times W\times C}$, we employ a CLIP-pretrained Vision Transformer (ViT) to attain its image representation. An image is first divided into $N=H\times W/P^{2}$ distinct patches of size $P\times P$, which are then transformed into one-dimensional token embeddings $\{f_{i}^{v}\}_{i=1}^{N}$ via a learnable linear projection. After adding positional encodings and a \[CLS\] token, the sequence $\{f_{cls}^{v},f_{1}^{v},\dots,f_{N}^{v}\}$ is passed through $L$ transformer layers to capture dependencies among patches. Finally, the \[CLS\] token embedding $f_{cls}^{v}$ is linearly mapped into the joint image-text embedding space, producing the compact global feature of the image.

Textual Modality. Given an input text $T$, we utilize the CLIP-Xformer textual extractor (radford2021learning) to obtain its embedding. The text is first tokenized through lower-cased Byte Pair Encoding (BPE) (sennrich2015neural) and framed with \[SOS\] and \[EOS\] tokens to indicate sequence boundaries. The resulting token sequence $\{f_{sos}^{t},f_{1}^{t},\dots,f_{eos}^{t}\}$ is processed by the transformer encoder, which models dependencies among tokens via masked self-attention. Finally, the \[EOS\] token embedding from the top layer, $f_{eos}^{t}$, is linearly mapped into the joint image-text representation space, generating a compressed global textual representation.

### 3.2. Adaptive Similarity Distribution Matching

Adopted from IRRA (jiang2023cross), we introduce a novel Adaptive Similarity Distribution Matching (A-SDM) module, which aims to adaptively pull the unmatched positive image-text pairs into a shared representation space, further enhancing the cross-modal global matching capability of the model.

Let the mini-batch contain $B$ image-text pairs, we pair each text embedding $g_{i}^{t}$ with its global image embedding $g_{j}^{v}$ to form the set $\{(g_{i}^{t},g_{j}^{v}),y_{i,j}\}_{j=1}^{B}$, where $y_{i,j}$ serves as the matching indicator. Specifically, $y_{i,j}=1$ denotes a matched pair, while $y_{i,j}=0$ denotes an mismatched pair. Let $cos(\mathbf{a},\mathbf{c})=\mathbf{a}^{\top}\mathbf{c}/\|\mathbf{a}\|\|\mathbf{c}\|$ denotes the similarity of $\mathbf{a}$ and $\mathbf{c}$. Subsequently, like SDM (jiang2023cross), the similarity matrix of image-text pairs is obtained through the following softmax function:

$$
p_{i,j}=\frac{exp(cos(g_{i}^{t},g_{j}^{v})/\tau_{1})}{\sum_{k=1}^{B}exp(cos(g_{i}^{t},g_{k}^{v})/\tau_{1})},
$$

where $\tau_{1}$ acts as a temperature term that modulates the spread of the resulting distribution. The probability $p_{i,j}$ quantifies how much the similarity between the text embedding $g_{i}^{t}$ and the image embedding $g_{j}^{v}$ contributes relative to the sum of all similarities between $g_{i}^{t}$ and every image embedding in the mini-batch.

Let the $i-th$ text $T_{i}$ from the batch be designated as the query text and $I_{i}$ be the corresponding image for $T_{i}$ at rank- $k$, where $k>1$. Different from IRRA (jiang2023cross), we propose to derive an adaptive weighting factor by assessing the similarity between the query text $T_{i}$ and all image representations:

$$
w_{i}^{t2i}=\alpha\cdot\left[\max_{k}p_{i,k}-p_{i,i}\right]+1,
$$

where $\alpha$ is a weight factor reflecting the contribution of unmatched image-text pairs to the cross-modal global matching ability of the model. Here, $\max_{k}p_{i,k}$ indicates the top similarity value between the text $T_{i}$ and every image within the mini-batch, while $p_{i,i}$ refers to the similarity associated with its corresponding positive image. The constant term “ $+1$ ” ensures that when $T_{i}$ and its corresponding image $I_{i}$ are correctly matched, the weight $w_{i}^{t2i}$ defaults to 1. In this case, the A-SDM loss reduces to the SDM loss (jiang2023cross), preventing overemphasis on correctly matched pairs while allowing the model to focus adaptively on harder and misaligned pairs. Conversely, $w_{i}^{t2i}>1$ indicates that $T_{i}$ and $I_{i}$ are unmatched, increasing their contribution to the loss to enhance global cross-modal alignment. The A-SDM loss for mapping text to image within a mini-batch is subsequently formulated as:

$$
\mathcal{L}_{t2i}=W^{t2i}*KL(\mathbf{p_{i}\|q_{i}})\\
=\frac{1}{B}\sum_{i=1}^{B}w_{i}^{t2i}\sum_{j=1}^{B}p_{i,j}\log(\frac{p_{i,j}}{q_{i,j}+\epsilon}),
$$

where $\epsilon$ is a tiny offset added to safeguard the computation from unstable values, and $q_{i,j}=y_{i,j}/\sum_{k=1}^{B}$ denotes the ground-truth matching probability.

In a complementary manner, the A-SDM loss for the image-to-text branch $\mathcal{L}_{i2t}$ is derived by swapping the roles of the text and image features. The bi-directional A-SDM loss is formulated as:

$$
\mathcal{L}_{A-sdm}=\mathcal{L}_{i2t}+\mathcal{L}_{t2i}.
$$

### 3.3. Explicit Fine-grained Alignment

To effectively leverage fine-grained information, it is necessary to narrow the underlying disparity between visual and textual modalities. Although many attention-based fine-grained alignment approaches have shown effectiveness by implicitly associating local regions in images with textual fragments, they provide no direct means to verify whether these localized correspondences are accurately aligned. We propose an explicit cross-modal aggregation approach that leverages the sparse similarity matrix between the local image and text features. To further reduce redundant information and minimize memory and time costs during fine-grained alignment, we use hard coding to align the aggregated language-grouped vision embeddings with both image and text embeddings, as shown in Figure 2(c).

![Refer to caption](https://arxiv.org/html/2509.13754v2/x6.png)

(a) Sparse similarity matrix aggregation.

Sparse Similarity Matrix Aggregation. Some methods (mukhoti2023open; yao2021filip) incur substantial computational and memory overhead, as they evaluate pairwise relationships between every image patch and every text token, which limits scalability to large batch sizes. Therefore, we apply a sparsification strategy to reduce the full pairwise similarity computation. While softmax is commonly used for such sparse processing, it tends to produce low-entropy similarity distributions that impede effective gradient flow (hoffmann2023eureka). Thus, we further adopt a max-min normalization scheme to achieve a more stable and expressive sparse similarity aggregation.

An image $I$ and its corresponding text $T$ are encoded through the visual and textual encoders, respectively. As presented in Figure 3(a), the similarity between image patches and text tokens is computed via the inner product of the last hidden states $\{f_{i}^{t}\}_{i=1}^{L}$ of the text transformer and $\{f_{i}^{v}\}_{i=1}^{N}$ of the vision transformer. $s_{i,j}=f_{i}^{t}\cdot f_{j}^{v}$ measures the similarity between the text token $f_{i}^{t}$ and the image patch $f_{j}^{v}$, where $\cdot$ denotes the inner product. To obtain the aggregation weight, each token $i$ is first scaled to the range \[0,1\] through the following min-max normalization:

$$
\hat{s}_{i,j}=\frac{s_{i,j}-\min_{k}s_{i,k}}{\max_{k}s_{i,k}-\min_{k}s_{i,k}}.
$$

We sparsify the normalized similarity matrix to encourage cross-modal interactions between each token and its patches with higher similarity:

$$
\tilde{s}_{i,j}=\begin{cases}\hat{s}_{i,j}&\mathrm{~if~}\hat{s}_{i,j}\geq\sigma\\
0&\mathrm{~otherwise}\end{cases},
$$

where $\sigma$ is the sparsity threshold. $\sigma$ is assigned the value $1/N$, where $N$ corresponds to the total count of patches in the image. This ensures that each token has a minimum of one corresponding image patch for alignment. We compute the aggregation weights by:

$$
agg_{i,j}=\frac{\tilde{s}_{i,j}}{\sum_{m=1}^{M}\tilde{s}_{i,j}},
$$

where $M$ is the number of image patches retained with high similarity to the token $i$, and $agg_{i,j}$ quantifies the influence of patch $j$ in forming the language-grouped vision embedding (referred to as joint embedding) associated with token $i$. This explicit aggregation strategy ensures a comprehensive interaction between token $i$ and its corresponding patch $j$ during local alignment. In particular, the aggregation weight $agg_{i,j}$ effectively captures the semantic relevance between token $i$ and patch $j$, thereby facilitating precise alignment.

Next, we derive the corresponding joint embedding $e_{i}$ as:

$$
{e}_{i}=\sum_{j=1}^{N}\\
agg_{i,j}\cdot{f}_{j}^{v},
$$

where $N$ is the count of image patches. The resulting set of joint embedding ${e}_{i}$ has the same length $L$ as the text token $f_{i}^{t}$.

Hard Coding Alignment. We calculate the similarity between the joint embeddings $\{e_{i}\}_{i=1}^{L}$ and their corresponding original text embeddings $\{f_{i}^{t}\}_{i=1}^{L}$ as well as image embeddings $\{f_{i}^{v}\}_{i=1}^{N}$, respectively. To reduce both computational and memory costs, we adopt a hard coding similarity computation between the joint embeddings and their corresponding text and image embeddings, and the theoretical analysis of the hard coding is provided in Appendix A. For simplicity, we only present the calculation between the joint embeddings and the text embeddings, while the remaining computations follow a similar and symmetric approach.

For the text $T$ and its corresponding joint embedding $E$, we calculate the original similarity matrix $O$ between all text tokens $\{f_{i}^{t}\}_{i=1}^{L}$ and their joint embeddings $\{e_{i}\}_{i=1}^{L}$, where $o_{i,j}={f_{i}^{t}}{e_{j}}^{\top}/\|f_{i}^{t}\|\|e_{j}\|$ means the cosine similarity of $f_{i}^{t}$ and $e_{j}$. For the token $f_{i}^{t}$, we compute the weight factor between it and all joint embeddings using the following hard coding way:

$$
\omega_{i,j}=\begin{cases}1&\mathrm{~if~}j=\underset{j^{\prime}=1\cdots L}{\operatorname*{argmax}}(o_{i,j^{\prime}})\\
0&otherwise\end{cases}.
$$

Then, we utilize the LSE pooling (lee2018stacked) to compute the hard similarity between text $T$ and its corresponding joint embedding $E$ by:

$$
\begin{split}hard\_s(T,E)&=LSE-Pooling\left(\sum_{j=1}^{L}\omega_{i,j}o_{i,j}\right)\\
&=\frac{1}{\lambda}\log\sum_{i=1}^{L}\exp\left(\lambda\max_{j=1\cdots L}o_{i,j}\right),\end{split}
$$

where $\lambda$ controls the degree to which the most relevant text embeddings and their corresponding joint embeddings are emphasized.

Given a batch containing $B$ text embeddings along with their associated joint embeddings, we compute the hard coding similarity matrix $Hard\_S$ following Eq. (9) and Eq. (10), as illustrated in Figure 3(b). We calculate the EFA loss from the text to its joint embedding, adapted from the triplet ranking loss (schroff2015facenet):

$$
\mathcal{L}_{t2e}=\frac{1}{B}\log\sum_{\mathrm{neg}}\exp\left(\frac{Hard\_S_{\mathrm{neg}}-Hard\_S_{\mathrm{pos}}+margin}{\tau_{2}}\right),
$$

where $\tau_{2}$ is a scaling factor adjusting the spread of the loss, and $margin$ is a distance hyperparameter defining the minimal gap separating positive and negative pairs.

Similarly, the EFA loss from the joint embedding to its original text can be computed following Eq. (11), and we can calculate the EFA loss between image and its joint embedding through Eq. (9), Eq. (10) and Eq. (11). Then, we obtain a full EFA loss by:

$$
\mathcal{L}_{efa}=\mathcal{L}_{t2e}+\mathcal{L}_{e2t}+\mathcal{L}_{i2e}+\mathcal{L}_{e2i}.
$$

### 3.4. Training Objective

As mentioned, FMFA aims to improve both the global and local cross-modal alignment of image-text features within the shared embedding space. To realize this goal, the widely adopted ID loss (zheng2020dual) and IRR loss (jiang2023cross), together with the proposed EFA and A-SDM loss, are jointly utilized to train FMFA. The ID loss directly classifies the global features obtained from both the image and the text according to their identities, thereby enhancing the global alignment of the model. The IRR loss, based on the Masked Language Modeling (MLM) task (taylor1953cloze), leverages an attention mechanism for implicit cross-modal interaction to obtain a joint embedding, and then predicts the \[MASK\] text token to enhance the local alignment of the model.

FMFA is trained end-to-end, with the complete training objective formulated as:

$$
\mathcal{L}=\mathcal{L}_{id}+\mathcal{L}_{irr}+\mathcal{L}_{efa}+\mathcal{L}_{A-sdm}.
$$

## 4\. Experiments

### 4.1. Datasets and Settings

Datasets. We assess FMFA on three widely used text-based person retrieval datasets, following the data splits introduced in IRRA (jiang2023cross). CUHK-PEDES (li2017person) contains 40,206 images associated with 13,003 identities, where each image is paired with two textual descriptions. Of these identities, 11,003 are designated for training, while the remaining 1,000 identities are allocated separately to validation and test sets. ICFG-PEDES (ding2021semantically) includes 54,522 images belonging to 4,102 individuals, each image linked to a single sentence. The conventional setup utilizes 3,102 identities for training and reserves 1,000 identities for testing. RSTPReid (zhu2021dssl) comprises 20,505 images from 4,101 identities captured across 15 camera views. Every identity corresponds to five images taken from different viewpoints, and each image is annotated with two descriptive captions. The dataset follows a split with 3,701 identities for training and 200 identities each for validation and testing.

Evaluation Metrics. To gauge retrieval quality, we primarily report Rank-K results (K = 1, 5, 10), which measure how often the correct item appears within the top-K predictions. Additionally, mean Average Precision (mAP) is adopted to summarize ranking accuracy over all query outcomes. In both cases, higher metric values correspond to superior model behavior.

Implementation Details. We utilize either the original CLIP model (radford2021learning) or its ReID-domain pre-trained variants (tan2024harnessing; jiang2025modeling) as encoders tailored to each modality. To maintain consistency, we employ the identical CLIP-ViT-B/16 model for visual encoding and Xformer for text encoding, following the setup used in IRRA (jiang2023cross) for our experiments. Specifically, images are resized to 384 $\times$ 128 pixels, and the maximum sequence length $L$ for input word tokens is set to 77. The model is trained using the Adam optimizer for 60 epochs with a default cosine learning rate decay schedule, in contrast to the 100 epochs employed for the ICFG-PEDES dataset. The original CLIP model parameters are trained with an initial learning rate of $1e-5$ and a batch size of 64. In particular, the temperature $\tau_{1}$ in the A-SDM loss is set to 0.02, while the temperature $\tau_{2}$ in the EFA loss takes a value of 1.0. The weight factor $\alpha$ of A-SDM is set to 10.0 by default, and set to 1 in the RSTPReid dataset, and the factor $\lambda$ in the LSE pooling is set to 1.0. Due to variations in data distribution, the margins used in the EFA loss differ across the three datasets. The specific margins used in Eq. (11) for each dataset are provided in Table 1. When using ReID-domain pre-trained CLIP models, we adopt the same initial learning rate and batch size as in NAM (tan2024harnessing) and HAM (jiang2025modeling), while keeping all other settings unchanged. The hardware configuration used in our experiments is shown in Table 2, while the detailed software environment is supplied in the code repository we have released.

Table 1. The margins utilized in the EFA loss. “T. to E.” means the EFA loss from textual embeddings to the corresponding joint embeddings, and “V. to E.” means the EFA loss from visual embeddings to the corresponding joint embeddings.

|  | CUHK-PEDES | ICFG-PEDES | RSTPReid |
| --- | --- | --- | --- |
| T. to E. | 0.1 | 0.2 | 0.2 |
| V. to E. | 0.1 | 1.0 | 0.8 |

Table 2. The hardware configuration of our experimental environment.

| Hardware | Details |
| --- | --- |
| CPU | Intel Xeon Gold 6330 |
| GPU | NVIDIA RTX A6000 |
| RAM | 755 GB DDR4 |

### 4.2. Comparison with State-of-the-Art Methods

In this subsection, we provide a comparison with current state-of-the-art methods (e.g., NAM (tan2024harnessing) and HAM (jiang2025modeling)) on three public benchmark datasets. The methods are grouped into two types according to their underlying network architecture, as listed in Table 3, Table 4, and Table 5: those using VL-Backbones without ReID-domain pre-training and those incorporating ReID-domain pre-training. Furthermore, according to whether local features are utilized during inference, the baselines are further classified into local and global matching methods (denoted as “L”” and “G” in the “Type” column, respectively). It should be noted that the baseline model presented in Table 3, Table 4, and Table 5 is referred to as IRRA <sup>R</sup>, which represents the performance of our reimplementation of the IRRA model. CLIP means the ViT-B/16 architecture after fine-tuning under the InfoNCE loss (oord2018representation).

Table 3. Comparisons with state-of-the-art methods on the CUHK-PEDES dataset. “G”, “L” and “P” in the “Type” column stand for global-matching method, local-matching method and pre-trained model with ReID-domain respectively. “Image Enc.” and “Text Enc.” mean the backbone of image encoder and text encoder respectively. “IRRA <sup>R</sup> ” means the model that we reproduce.

<table><tbody><tr><td>Type</td><td>Method</td><td>Ref.</td><td>Image Enc.</td><td>Text Enc.</td><td>Rank-1</td><td>Rank-5</td><td>Rank-10</td><td>mAP</td></tr><tr><td colspan="3">VL-Backbones w/o ReID-domain pre-training:</td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td rowspan="7">G</td><td>LGUR <cite>(shao2022learning)</cite></td><td>MM22</td><td>ResNet50</td><td>BERT</td><td>65.25</td><td>83.12</td><td>89.00</td><td>-</td></tr><tr><td>IVT <cite>(shu2022see)</cite></td><td>ECCV22</td><td>ViT-B/16</td><td>BERT</td><td>65.59</td><td>83.11</td><td>89.21</td><td>-</td></tr><tr><td>VGSG <cite>(he23vgsg)</cite></td><td>TIP23</td><td>ResNet50</td><td>Transformer</td><td>67.52</td><td>84.37</td><td>90.26</td><td>-</td></tr><tr><td>CLIP <cite>(radford2021learning)</cite></td><td>ICML21</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>68.19</td><td>86.47</td><td>91.47</td><td>61.12</td></tr><tr><td>DM-Adapter <cite>(liu2025dm)</cite></td><td>AAAI25</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>72.17</td><td>88.74</td><td>92.85</td><td>64.33</td></tr><tr><td>IRRA <sup>R</sup> <cite>(jiang2023cross)</cite></td><td>CVPR23</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>73.45</td><td>89.38</td><td>93.69</td><td>66.13</td></tr><tr><td>TBPS-CLIP <cite>(cao2024empirical)</cite></td><td>AAAI24</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>73.54</td><td>88.19</td><td>92.35</td><td>65.38</td></tr><tr><td></td><td>FMFA (ours)</td><td></td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>74.16</td><td>90.12</td><td>94.10</td><td>66.66</td></tr><tr><td rowspan="7">L</td><td>ACSA <cite>(ji2022asymmetric)</cite></td><td>TMM22</td><td>Swin-B</td><td>BERT</td><td>63.56</td><td>81.49</td><td>87.70</td><td>-</td></tr><tr><td>Han et al. <cite>(han2021text)</cite></td><td>arXiv21</td><td>CLIP-RN101</td><td>CLIP-Xformer</td><td>64.08</td><td>81.73</td><td>88.19</td><td>60.08</td></tr><tr><td>PLOT <cite>(park2024plot)</cite></td><td>ECCV24</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>75.28</td><td>90.42</td><td>94.12</td><td>-</td></tr><tr><td>RaSa <cite>(bai2023rasa)</cite></td><td>IJCAI23</td><td>CLIP-ViT</td><td>BERT-base</td><td>76.51</td><td>90.29</td><td>94.25</td><td>69.38</td></tr><tr><td>PTMI <cite>(lu2025prompt)</cite></td><td>TIFS25</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>76.02</td><td>89.93</td><td>94.14</td><td>70.85</td></tr><tr><td>APTM <cite>(yang2023towards)</cite></td><td>MM23</td><td>Swin-B</td><td>BERT-base</td><td>76.53</td><td>90.04</td><td>94.15</td><td>66.91</td></tr><tr><td>SCVD <cite>(wei2024fine)</cite></td><td>TCSVT24</td><td>CLIP-RN50</td><td>CLIP-Xformer</td><td>76.72</td><td>90.38</td><td>94.89</td><td>-</td></tr><tr><td colspan="3">VL-Backbones with ReID-domain pre-training:</td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td rowspan="6">P+G</td><td>UniPT <cite>(shao2023unified)</cite> + IRRA <cite>(jiang2023cross)</cite></td><td>ICCV23</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>74.37</td><td>89.51</td><td>93.97</td><td>66.60</td></tr><tr><td>PLIP <cite>(zuo2024plip)</cite> + IRRA <cite>(jiang2023cross)</cite></td><td>NeurIPS24</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>74.25</td><td>89.49</td><td>93.68</td><td>66.52</td></tr><tr><td>NAM <cite>(tan2024harnessing)</cite> + IRRA <sup>R</sup></td><td>CVPR24</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>76.67</td><td>91.11</td><td>94.60</td><td>68.42</td></tr><tr><td>NAM <cite>(tan2024harnessing)</cite> + FMFA (ours)</td><td></td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>77.23</td><td>91.33</td><td>94.75</td><td>68.53</td></tr><tr><td>HAM <cite>(jiang2025modeling)</cite> + IRRA <sup>R</sup></td><td>CVPR25</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>77.32</td><td>91.20</td><td>94.95</td><td>68.87</td></tr><tr><td>HAM <cite>(jiang2025modeling)</cite> + FMFA (ours)</td><td></td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>77.46</td><td>91.36</td><td>95.01</td><td>68.89</td></tr></tbody></table>

Table 4. Comparisons with state-of-the-art methods on the RSTPReid dataset.

<table><tbody><tr><th>Type</th><th>Method</th><td>Rank-1</td><td>Rank-5</td><td>Rank-10</td><td>mAP</td></tr><tr><th colspan="6">VL-Backbones w/o ReID-domain pre-training:</th></tr><tr><th rowspan="6">G</th><th>DSSL <cite>(zhu2021dssl)</cite></th><td>39.05</td><td>62.60</td><td>73.95</td><td>-</td></tr><tr><th>IVT <cite>(shu2022see)</cite></th><td>46.70</td><td>70.00</td><td>78.80</td><td>-</td></tr><tr><th>CLIP <cite>(radford2021learning)</cite></th><td>54.05</td><td>80.70</td><td>88.00</td><td>43.41</td></tr><tr><th>IRRA <sup>R</sup> <cite>(jiang2023cross)</cite></th><td>59.50</td><td>81.80</td><td>88.85</td><td>47.44</td></tr><tr><th>DM-Adapter <cite>(liu2025dm)</cite></th><td>60.00</td><td>82.10</td><td>87.90</td><td>47.37</td></tr><tr><th>FMFA (ours)</th><td>61.05</td><td>83.85</td><td>89.80</td><td>48.22</td></tr><tr><th rowspan="5">L</th><th>ACSA <cite>(lu2025prompt)</cite></th><td>48.40</td><td>71.85</td><td>81.45</td><td>-</td></tr><tr><th>CFine <cite>(yan2023clip)</cite></th><td>50.55</td><td>72.50</td><td>81.60</td><td>-</td></tr><tr><th>PLOT <cite>(park2024plot)</cite></th><td>61.80</td><td>82.85</td><td>89.45</td><td>-</td></tr><tr><th>RaSa <cite>(bai2023rasa)</cite></th><td>66.90</td><td>86.50</td><td>91.35</td><td>52.31</td></tr><tr><th>APTM <cite>(yang2023towards)</cite></th><td>67.50</td><td>85.70</td><td>91.45</td><td>52.56</td></tr><tr><th colspan="6">VL-Backbones with ReID-domain pre-training:</th></tr><tr><th rowspan="6">P+G</th><th>UniPT <cite>(shao2023unified)</cite> + IRRA <cite>(jiang2023cross)</cite></th><td>62.20</td><td>83.30</td><td>89.75</td><td>48.33</td></tr><tr><th>PLIP <cite>(zuo2024plip)</cite> + IRRA <cite>(jiang2023cross)</cite></th><td>64.35</td><td>83.75</td><td>91.00</td><td>50.93</td></tr><tr><th>NAM <cite>(tan2024harnessing)</cite> + IRRA <sup>R</sup></th><td>68.25</td><td>86.75</td><td>92.30</td><td>52.92</td></tr><tr><th>NAM <cite>(tan2024harnessing)</cite> + FMFA (ours)</th><td>68.70</td><td>87.05</td><td>92.35</td><td>53.14</td></tr><tr><th>HAM <cite>(jiang2025modeling)</cite> + IRRA <sup>R</sup></th><td>71.35</td><td>87.60</td><td>93.05</td><td>55.40</td></tr><tr><th>HAM <cite>(jiang2025modeling)</cite> + FMFA (ours)</th><td>71.80</td><td>88.05</td><td>93.15</td><td>55.72</td></tr></tbody></table>

Evaluation Results on CUHK-PEDES We measure the performance of FMFA on the CUHK-PEDES dataset, as presented in Table 3. When using the VL-Backbones without ReID-domain pre-training, FMFA achieves superior performance over advanced global matching methods, attaining 74.16% Rank-1 and 66.66% mAP, while surpassing IRRA by 0.74% in Rank-5 and 0.41% in Rank-10. When adopting the VL-Backbones with ReID-domain pre-training, FMFA maintains its superiority, and achieves Rank-5 accuracy exceeding 95% with the HAM-based backbone. Notably, FMFA with NAM-based backbone attains 91.33% in Rank-5, outperforming IRRA with the HAM-based backbone by 0.13%.

Evaluation Results on RSTPReid. We assess FMFA on the latest RSTPReid benchmark, as presented in Table 4. Using the VL-Backbones without ReID-domain pre-training, FMFA achieves competitive performance, attaining 61.05% Rank-1, 83.85% Rank-5, 89.80% Rank-10, and 48.22% mAP, respectively, outperforming IRRA by 1.55% in Rank-1 and 2.05% in Rank-5. When adopting the VL-Backbones with ReID-domain pre-training, our method achieves further gains, exceeding IRRA by 0.45% in Rank-1 with both the NAM-based and HAM-based backbones. Notably, FMFA achieves Rank-5 accuracy higher than 88% with the HAM-based backbone.

Table 5. Comparisons with state-of-the-art methods on the ICFG-PEDES dataset.

<table><tbody><tr><th>Type</th><th>Method</th><td>Rank-1</td><td>Rank-5</td><td>Rank-10</td><td>mAP</td></tr><tr><th colspan="6">VL-Backbones w/o ReID-domain pre-training:</th></tr><tr><th rowspan="6">G</th><th>Dual Path <cite>(zheng2020dual)</cite></th><td>38.99</td><td>59.44</td><td>68.41</td><td>-</td></tr><tr><th>IVT <cite>(shu2022see)</cite></th><td>56.04</td><td>73.60</td><td>80.22</td><td>-</td></tr><tr><th>CLIP <cite>(radford2021learning)</cite></th><td>56.74</td><td>75.72</td><td>82.26</td><td>31.84</td></tr><tr><th>VGSG <cite>(he23vgsg)</cite></th><td>60.34</td><td>76.01</td><td>82.01</td><td>-</td></tr><tr><th>DM-Adapter <cite>(liu2025dm)</cite></th><td>62.64</td><td>79.53</td><td>85.32</td><td>36.50</td></tr><tr><th>IRRA <sup>R</sup> <cite>(jiang2023cross)</cite></th><td>63.48</td><td>80.16</td><td>85.78</td><td>38.20</td></tr><tr><th></th><th>FMFA (ours)</th><td>64.29</td><td>80.48</td><td>85.93</td><td>39.43</td></tr><tr><th rowspan="5">L</th><th>SSAN <cite>(ding2021semantically)</cite></th><td>54.23</td><td>72.63</td><td>79.53</td><td>-</td></tr><tr><th>ISANet <cite>(yan2023image)</cite></th><td>57.73</td><td>75.42</td><td>81.72</td><td>-</td></tr><tr><th>CFine <cite>(yan2023clip)</cite></th><td>60.83</td><td>76.55</td><td>82.42</td><td>-</td></tr><tr><th>RaSa <cite>(bai2023rasa)</cite></th><td>65.28</td><td>80.40</td><td>85.12</td><td>41.29</td></tr><tr><th>PLOT <cite>(park2024plot)</cite></th><td>65.76</td><td>81.39</td><td>86.73</td><td></td></tr><tr><th colspan="6">VL-Backbones with ReID-domain pre-training:</th></tr><tr><th rowspan="6">P+G</th><th>UniPT <cite>(shao2023unified)</cite> + IRRA <cite>(jiang2023cross)</cite></th><td>64.50</td><td>80.24</td><td>85.74</td><td>38.22</td></tr><tr><th>PLIP <cite>(zuo2024plip)</cite> + IRRA <cite>(jiang2023cross)</cite></th><td>65.79</td><td>81.94</td><td>87.32</td><td>39.43</td></tr><tr><th>NAM <cite>(tan2024harnessing)</cite> + IRRA <sup>R</sup></th><td>66.34</td><td>81.94</td><td>86.73</td><td>40.14</td></tr><tr><th>NAM <cite>(tan2024harnessing)</cite> + FMFA (ours)</th><td>66.58</td><td>81.94</td><td>87.04</td><td>40.17</td></tr><tr><th>HAM <cite>(jiang2025modeling)</cite> + IRRA <sup>R</sup></th><td>68.21</td><td>83.28</td><td>88.04</td><td>41.72</td></tr><tr><th>HAM <cite>(jiang2025modeling)</cite> + FMFA (ours)</th><td>68.37</td><td>83.28</td><td>88.10</td><td>41.76</td></tr></tbody></table>

Evaluation Results on ICFG-PEDES. We assess FMFA on the ICFG-PEDES benchmark, with the results displayed in Table 5. Using VL-Backbones without ReID-domain pre-training, FMFA obtains the leading results across all metrics, attaining 64.29% Rank-1 and 39.43% mAP. Compared with IRRA, FMFA shows a notable improvement of 0.81% Rank-1 and 1.23% mAP, which is meaningful for practical applications. When adopting VL-Backbones with ReID-domain pre-training, FMFA yields slight gains, outperforming IRRA by 0.24% and 0.16% in Rank-1 with the NAM-based and HAM-based backbones, respectively.

In conclusion, FMFA attains the highest performance across all evaluation metrics on the three widely used public benchmarks. As far as we are aware, FMFA is the best method for all global matching methods. This highlights the ability of our method to generalize well and maintain robustness.

### 4.3. Ablation Study

In this subsection, we examine our proposed components in the FMFA framework. For simplicity, we omit the components of $\mathcal{L}_{id}$ and the IRR module that were proposed by IRRA and used in all experiments. Only one of SDM and A-SDM can be used at the same time.

To thoroughly assess the contribution of our FMFA modules, we undertake an empirical analysis on three widely used datasets. Table 6 summarizes the Rank-1/5/10 accuracies (%) together with the mAP (%) performance.

Effect of The A-SDM Module. To evaluate the contribution of the Adaptive Similarity Distribution Matching (A-SDM) module, we perform ablation experiments by replacing the A-SDM module with the SDM module, keeping all hyperparameters unchanged. Specifically, as shown in Table 6, replacing A-SDM with SDM results in a reduction of Rank-1 accuracy by 0.59%, 0.78%, and 0.75% across the three datasets, and also causes a 1.19% drop in mAP on the ICFG-PEDES dataset, as observed in No. 0 vs. No. 1. Additionally, all evaluation metrics on CUHK-PEDES and ICFG-PEDES degrade, further confirming the superiority of A-SDM. Moreover, when combined with the EFA module, the advantage of A-SDM becomes even more pronounced. As shown in No. 2 vs. No. 3, replacing the A-SDM module with the SDM module results in 0.43% and 0.48% decrease in Rank-1 and Rank-5 on the CUHK-PEDES dataset, respectively, as well as a 1.55% drop in Rank-5 and a 0.58% decline in mAP on the RSTPReid dataset. These results collectively validate the consistent and significant impact of A-SDM to performance.

Table 6. Ablation analysis of FMFA modules across three public benchmarks.

<table><thead><tr><th rowspan="2">No.</th><th rowspan="2">Methods</th><th colspan="3">Components</th><th colspan="4">CUHK-PEDES</th><th colspan="4">ICFG-PEDES</th><th colspan="4">RSTPReid</th></tr><tr><th>SDM</th><th>A-SDM</th><th>EFA</th><th>Rank-1</th><th>Rank-5</th><th>Rank-10</th><th>mAP</th><th>Rank-1</th><th>Rank-5</th><th>Rank-10</th><th>mAP</th><th>Rank-1</th><th>Rank-5</th><th>Rank-10</th><th>mAP</th></tr></thead><tbody><tr><td>0</td><td>Baseline</td><td><math><semantics><mi>✓</mi> <annotation>\checkmark</annotation></semantics></math></td><td></td><td></td><td>73.45</td><td>89.38</td><td>93.69</td><td>66.13</td><td>63.48</td><td>80.16</td><td>85.78</td><td>38.20</td><td>59.50</td><td>81.80</td><td>88.85</td><td>47.44</td></tr><tr><td>1</td><td>+A-SDM</td><td></td><td><math><semantics><mi>✓</mi> <annotation>\checkmark</annotation></semantics></math></td><td></td><td>74.04</td><td>89.86</td><td>93.89</td><td>66.45</td><td>64.26</td><td>80.59</td><td>85.90</td><td>39.39</td><td>60.25</td><td>81.45</td><td>88.70</td><td>47.69</td></tr><tr><td>2</td><td>+EFA</td><td><math><semantics><mi>✓</mi> <annotation>\checkmark</annotation></semantics></math></td><td></td><td><math><semantics><mi>✓</mi> <annotation>\checkmark</annotation></semantics></math></td><td>73.73</td><td>89.64</td><td>94.04</td><td>66.40</td><td>63.77</td><td>80.39</td><td>85.86</td><td>39.17</td><td>60.45</td><td>82.30</td><td>89.25</td><td>47.64</td></tr><tr><td>3</td><td>FMFA</td><td></td><td><math><semantics><mi>✓</mi> <annotation>\checkmark</annotation></semantics></math></td><td><math><semantics><mi>✓</mi> <annotation>\checkmark</annotation></semantics></math></td><td>74.16</td><td>90.12</td><td>94.10</td><td>66.66</td><td>64.29</td><td>80.48</td><td>85.93</td><td>39.43</td><td>61.05</td><td>83.85</td><td>89.80</td><td>48.22</td></tr></tbody></table>

Effect of The EFA Module. To improve the model’s global matching performance, the Explicit Fine-grained Alignment (EFA) module introduces fine-grained cross-modal interaction based on a sparse similarity matrix. The impact of the EFA module is illustrated by comparing the results of No. 0 vs. No. 2 and No. 1 vs. No. 3. Specifically, as shown in No. 1 vs. No. 3, removing the EFA module from FMFA leads to a performance drop of 0.26% and 0.21% in Rank-5 and Rank-10 on the CUHK-PEDES dataset, and a more significant decline of 2.40% and 1.10% in Rank-5 and Rank-10, along with a 0.53% decrease in mAP on the RSTPReid dataset. However, EFA causes a 0.11% drop in Rank-5 on ICFG-PEDES, suggesting that its sparse and hard coding strategy, which focuses only on the most relevant patches, may overlook other informative ones and lead to information loss. Notably, this comparison also reflects the joint ablation of EFA and the A-SDM module, further verifying the complementary effect between the two modules. Moreover, to further validate the individual contribution of the EFA module, we design an additional experiment that retains the SDM module while removing only the EFA module, as observed in No. 0 vs. No. 2. In this setting, the absence of EFA results in 0.38%, 0.29%, and 0.95% drops in Rank-1 on CUHK-PEDES, ICFG-PEDES and RSTPReid, and causes a 1.23% drop in mAP on ICFG-PEDES. These evaluations highlight the effectiveness of the EFA module.

### 4.4. Parameter Study

We perform a parameter study on the CUHK-PEDES dataset, examining three hyperparameters—the weight factor $\alpha$, the sparsity threshold $\sigma$, and the factor $\lambda$ —as well as the contribution weights of the proposed loss functions, $\mathcal{L}_{A\text{-}SDM}$ and $\mathcal{L}_{EFA}$. When examining a specific parameter, all other parameters are maintained as specified in Section 4.1.

### 4.5. Qualitative Results

Visualization of The Sparse Process. We visualize the similarity maps before and after the sparse process (i.e., Eq. (5) and Eq. (6)) in the EFA module, as shown in Figure 5. Patches with high similarity (greater than 0.75) are preserved, as indicated by the black frames in the left part of Figure 5. In contrast, patches with low similarity (below 0.5) are suppressed to values under 0.25 and thus omitted during aggregation, as shown by the pink frames on the left. When most patches in an image exhibit relatively high similarity (around 0.75), the sparse process retains only those with the highest similarity while reducing the similarity of the remaining patches below 0.5, highlighted by the purple frames in the right part of Figure 5. This guarantees that the subsequent aggregation emphasizes only the most pertinent patches, decreasing computational and memory overhead while preserving performance. Unlike implicit aggregation methods based on attention mechanisms, EFA explicitly aggregates image patches and text tokens, allowing us to observe whether the most relevant patches are effectively aggregated by visualizing the similarity between patches and tokens.

Inference Time Comparison. We compare the inference time between FMFA and recent matching methods (e.g., PLOT (park2024plot) and RaSa (bai2023rasa)) on the test sets of three datasets, as shown in Table 9. As a global matching method, FMFA only computes global features during inference, thus achieving a higher inference speed than local matching methods. Even when compared with the recent global matching method DM-Adapter (liu2025dm), FMFA still achieves consistently faster inference across all three datasets. Moreover, the efficiency advantage of FMFA becomes more pronounced with the growth of the test set. For instance, the inference time of FMFA vs. PLOT increases from 3s vs. 5s on RSTPReid to 50s vs. 91s on ICFG-PEDES. These comparisons clearly demonstrate that FMFA achieves superior inference speed compared with recent methods.

Table 9. Comparison of the inference time (s) between FMFA and recent methods.

| Method | RSTPReid | CUHK-PEDES | ICFG-PEDES |
| --- | --- | --- | --- |
| FMFA (ours) | 3 | 7 | 50 |
| DM-Adapter (liu2025dm) | 8 | 16 | 78 |
| PLOT (park2024plot) | 5 | 16 | 91 |
| APTM (yang2023towards) | 10 | 29 | 95 |
| SCVD (wei2024fine) | \- | 191 | 1369 |
| RaSa (bai2023rasa) | 388 | 1168 | 3871 |

![Refer to caption](https://arxiv.org/html/2509.13754v2/x12.png)

(a) A man wearing a gray and black shirt, a pair of black pants and a bag over his right shoulder.

Visualization of Top-5 Retrieval Results. Figure 6 compares the top-5 retrieval results between the baseline IRRA <sup>R</sup> and our proposed FMFA on the CUHK-PEDES dataset. Figure 6 illustrates that FMFA delivers more precise retrieval results, correctly identifying images that the baseline fails to match. For query texts where the baseline performs well, FMFA further improves performance by retrieving more relevant pedestrian images (e.g., Figure 6(a) and Figure 6(c)). Even for hard negative samples, where the baseline struggles to retrieve the correct image, FMFA still enhances the similarity between positive pairs (e.g., Figure 6(b) and Figure 6(d)). This is because our proposed FMFA focuses on the unmatched positive pairs and adaptively pulls the positive pairs closer. More comparisons of the top-5 retrieved results are provided in Appendix B.

## 5\. Conclusion

In summary, we propose a cross-modal Full-Mode Fine-grained Alignment (FMFA) framework to learn discriminative global text-image representations through full-mode fine-grained alignment, including explicit fine-grained alignment and existing implicit relational reasoning. We design an Adaptive Similarity Distribution Matching (A-SDM) module to concentrate on unmatched positive pairs, adaptively pulling them closer. In addition, to achieve cross-modal fine-grained alignment, we introduce an Explicit Fine-grained Alignment (EFA) module, which explicitly aggregates local text and image representations based on the sparse similarity matrix and employs a hard coding method. These modules function together to project images and text into a shared embedding space. Comprehensive experiments across three datasets confirm the effectiveness and superior performance of our FMFA framework.

Limitation. The fixed threshold in the sparse process only keeps the most relevant patches, which may result in the loss of semantic information and limit the effective aggregation of local features, thereby affecting the overall performance of our model. Incorporating adaptive methods that capture complete semantic information (e.g., tree transformer (wang2019tree)) could further enhance our model.

###### Acknowledgements.

This work was supported by the National Natural Science Foundation of China (No. 62302080), Guangxi Key Research and Development Program (No. Guike AB24010112), National Foreign Expert Project of China (No. S20240327), Sichuan Science and Technology Program (No. 2025HJRC0021) and Sichuan Province Innovative Talent Funding Project for Postdoctoral Fellows (No. BX202312).

## Appendix A Theoretical Analysis of Hard Coding in EFA

Given visual embeddings of an image $\boldsymbol{V}\in\mathbb{R}^{N\times d}$ and its joint embeddings $\boldsymbol{E}\in\mathbb{R}^{L\times d}$, where $N$ is the number of image patches and $L$ is the length of the joint embeddings, both the hard coding method and the soft coding method calculate the similarity matrix $A$ to obtain the final similarity between $\boldsymbol{V}$ and $\boldsymbol{E}$, which requires the same time complexity $\mathcal{O}(NLd)$. When processing the similarity matrix $A$, our hard coding method calculates the maximum similarity for each row, which has a time complexity of $\mathcal{O}(N)$, as described in Eq. (9) and Eq. (10). However, the soft coding method processes all similarities, resulting in a time complexity of $\mathcal{O}(NL)$. Moreover, the spatial complexity of the hard coding method is $\mathcal{O}(NL)$, which is significantly lower than the spatial complexity of the soft coding method, $\mathcal{O}(Ld)$. This is based on the fact that $N\ll d$. Therefore, our hard coding method can effectively reduce the cost of training time and memory.

## Appendix B More Comparisons of The Top-5 Retrieved Results

Figure 7 and Figure 8 show the comparisons of the top-5 retrieved results between the baseline and FMFA on the ICFG-PEDES and RSTPReid datasets, respectively. These comparisons further highlight the superiority and effectiveness of the proposed FMFA framework.

![Refer to caption](https://arxiv.org/html/2509.13754v2/x16.png)

(a) A man in his forties with short black hair is wearing a mid-length grey trench coat over a light-colored collared shirt. He is also wearing a regular-fit black pants.

![Refer to caption](https://arxiv.org/html/2509.13754v2/x20.png)

(a) A person is wearing a short dark jacket, a pair of green overalls and a pair of sneakers with blue edging.
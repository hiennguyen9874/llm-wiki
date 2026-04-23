###### Abstract

Text-Based Person Search (TBPS) aims to retrieve pedestrian images from large galleries using natural language descriptions. This task, essential for public safety applications, is hindered by cross-modal discrepancies and ambiguous user queries. We introduce CONQUER, a two-stage framework designed to address these challenges by enhancing cross-modal alignment during training and adaptively refining queries at inference. During training, CONQUER employs multi-granularity encoding, complementary pair mining, and context-guided optimal matching based on Optimal Transport to learn robust embeddings. At inference, a plug-and-play query enhancement module refines vague or incomplete queries via anchor selection and attribute-driven enrichment, without requiring retraining of the backbone. Extensive experiments on CUHK-PEDES, ICFG-PEDES, and RSTPReid demonstrate that CONQUER consistently outperforms strong baselines in both Rank-1 accuracy and mAP, yielding notable improvements in cross-domain and incomplete-query scenarios. These results highlight CONQUER as a practical and effective solution for real-world TBPS deployment. Source code is available at [https://github.com/zqxie77/CONQUER](https://github.com/zqxie77/CONQUER).

## 1 Introduction

Text-based Person Search (TBPS) is a cross-modal retrieval task that locates target individuals in large image galleries using natural language descriptions [^1]. As a bridge between Person Re-identification (Re-ID) and text-to-image retrieval, TBPS allows for more flexible and descriptive queries than traditional image-based methods. However, TBPS remains challenging due to redundant visual features [^2] [^3] and the inherent noise in cross-modal correspondence [^4]. Furthermore, the lack of adaptive mechanisms for handling ambiguous queries during inference limits practical application.

![Refer to caption](https://arxiv.org/html/2601.18625v1/x1.png)

Fig. 1: A comparison of TBPS.(a) Existing Method: The search is performed directly using the original text query.(b) Our IQE Approach: We improve the query at inference time without retraining. First, our method finds a relevant anchor image. Then, an MLLM learns key visual details from this image through a Q&A process. Finally, it fuses these details with the original text to create an improved query and re-ranks the search results.

Most existing methods improve cross-modal alignment using fine-grained annotations or large pre-trained models like CLIP [^5]. While integrated planning and scheduling frameworks have proven effective in optimizing complex systems [^6], TBPS methods still mainly rely on passive alignment—matching features in the embedding space without actively improving the inputs. Some approaches explore hierarchical visual perception to achieve deeper alignment [^7] [^8], yet they also suffer from this passive limitation. This leads to two key problems: (1) Methods such as CFAM [^9] depend on manual annotations, but their performance drops when annotations are scarce; (2) Methods like DM-Adapter [^10] and MGRL [^11] cannot refine brief or ambiguous queries at inference, resulting in poor results for incomplete descriptions.

Some recent works have attempted active refinement or interaction. For instance, chat-driven mechanisms have been proposed to generate text for retrieval [^12], though purely generative approaches may hallucinate attributes. Other works like TVFR [^13] are sensitive to the initial query, and AUL [^14] mainly helps during training. These limitations motivate us to design a method that achieves fine-grained cross-modal alignment during training and actively refines ambiguous or incomplete queries at inference.

To solve the aforementioned problems, we propose CONQUER, a two-stage framework as illustrated in Fig. 1. During training, our Context-Aware Representation Enhancement (CARE) module learns robust cross-modal embeddings. Subsequently, at the inference stage, our Interactive Query Enhancement (IQE) module acts as a plug-and-play enhancement that adaptively refines user queries. By leveraging fine-grained attributes extracted from high-confidence candidate images, IQE enriches ambiguous or underspecified descriptions. The enhanced information is then fused with the original query, enabling more accurate re-ranking of the gallery and improved retrieval results.

Our main contributions are as follows:

- We introduce CARE, a context-aware representation enhancement module that addresses the cross-modal gap by combining multi-granularity representation encoding, complementary pair mining, and context-guided optimal matching via Optimal Transport.
- We develop IQE, an interactive query enhancement strategy that adaptively refines ambiguous or incomplete user queries during inference by leveraging attribute information from candidate images.
- Extensive experiments show that CONQUER achieves state-of-the-art performance on several TBPS benchmarks and demonstrates strong robustness in cross-domain and incomplete-query scenarios.

## 2 Methodology

Context-aware Representation with Query Enhancement for Retrieval (CONQUER) is a two-stage framework for TBPS that comprises CARE during training and IQE at inference. CARE enhances cross-modal embeddings by leveraging contextual cues, while IQE adaptively refines user queries to improve retrieval accuracy.

![Refer to caption](https://arxiv.org/html/2601.18625v1/x2.png)

Fig. 2: The Architecture of the Context-Aware Representation Enhancement (CARE) Module. The CARE module leverages multi-granularity representation encoding to learn robust cross-modal alignments. For complementary pair mining, it first classifies training pairs into clean, uncertain, and refinable sets by jointly analyzing similarity matrices from both global features and selected local tokens; hard negatives are then mined from the identified ‘refinable’ set. Simultaneously, its context-guided optimal matching component employs an Optimal Transport (OT) solver to align fine-grained features. This local alignment is in turn guided by the global similarities via a KL-Divergence loss, ensuring feature matching remains consistent with the overall semantic context.

### 2.1 Context-Aware Representation Enhancement

As illustrated in Fig. 2, CARE improves cross-modal alignment through three main components: multi-granularity representation encoding, complementary pair mining, and context-guided optimal matching.

#### 2.1.1 Multi-granularity Representation Encoding

Let $\mathbf{I}$ and $\mathbf{T}$ denote the input image and text. Modality-specific encoders $E_{I}(\cdot)$ and $E_{T}(\cdot)$ extract both global and local features. For each image-text pair, local features are $\{\mathbf{v}_{m}\}_{m=1}^{M}$ (visual tokens) and $\{\mathbf{w}_{n}\}_{n=1}^{N}$ (text tokens), with global features $\bar{\mathbf{v}}_{i}$ and $\bar{\mathbf{w}}_{i}$ for the $i$ -th sample.

Arrange local features into matrices:

$$
\mathbf{V}=[\mathbf{v}_{1},\dots,\mathbf{v}_{M}]\in\mathbb{R}^{d\times M},\quad\mathbf{W}=[\mathbf{w}_{1},\dots,\mathbf{w}_{N}]\in\mathbb{R}^{d\times N}.
$$

The batch-wise cross-modal similarity matrix $S\in\mathbb{R}^{B\times B}$ is computed from global features:

$$
S_{ij}=\frac{\bar{\mathbf{v}}_{i}^{\top}\bar{\mathbf{w}}_{j}}{\|\bar{\mathbf{v}}_{i}\|\|\bar{\mathbf{w}}_{j}\|},
$$

where $B$ is the batch size and $S_{ij}$ is the cosine similarity between the $i$ -th image and $j$ -th text.

Based on confidence, training pairs are divided into high-confidence (clean), low-confidence (uncertain), and refinable sets.

#### 2.1.2 Complementary Pair Mining

For refinable pairs, off-diagonal sampling generates complementary negatives:

$$
\mathcal{N}=\{S_{ij}\mid i\neq j,\,(i,j)\in\text{Refinable}\},
$$

enhancing negative diversity and sharpening decision boundaries.

#### 2.1.3 Context-guided Optimal Matching

Cross-modal alignment refinement is formulated as an Optimal Transport (OT) problem. Given local features $\{\mathbf{v}_{m}\}_{m=1}^{M}$ and $\{\mathbf{w}_{n}\}_{n=1}^{N}$, a learnable cost matrix is computed:

$$
C_{mn}=f_{\theta}(\mathbf{v}_{m},\mathbf{w}_{n}),
$$

where $f_{\theta}(\cdot)$ is a neural network estimating contextual dissimilarity.

The OT objective seeks a transport plan $T\in\mathbb{R}^{M\times N}$ by minimizing:

$$
\min_{T\in\Pi(\mathbf{a},\mathbf{b})}\langle T,C\rangle+\lambda\,\mathrm{H}(T),
$$

where $\Pi(\mathbf{a},\mathbf{b})$ is the set of valid transport plans. We solve this regularized OT problem using the Sinkhorn algorithm.

For supervision, compute a local similarity matrix:

$$
S^{\mathrm{loc}}_{mn}=\frac{\mathbf{v}_{m}^{\top}\mathbf{w}_{n}}{\|\mathbf{v}_{m}\|\|\mathbf{w}_{n}\|}.
$$

Align $T$ with $S^{\mathrm{loc}}$ by minimizing their row-wise KL-divergence:

$$
\mathcal{L}_{\mathrm{OT}}=\mathrm{KL}(\mathrm{softmax}_{\mathrm{row}}(T)\;\|\;\mathrm{softmax}_{\mathrm{row}}(S^{\mathrm{loc}})).
$$

The final CARE loss is:

$$
\mathcal{L}_{\mathrm{CARE}}=\mathcal{L}_{\mathrm{align}}+\alpha\mathcal{L}_{\mathrm{neg}}+\beta\mathcal{L}_{\mathrm{OT}},
$$

where $\mathcal{L}_{\mathrm{align}}$ is cross-modal alignment loss, $\mathcal{L}_{\mathrm{neg}}$ is the loss for complementary negatives, and $\alpha,\beta$ are trade-off weights.

### 2.2 Interactive Query Enhancement

As illustrated in Fig. 1, IQE is a plug-and-play inference module that refines ambiguous queries without retraining the backbone. The process consists of three main steps: anchor identification, interactive query refinement, and query fusion for re-ranking.

#### 2.2.1 Anchor Identification

Given a query $T$, the backbone returns top- $K$ candidates $\{\hat{I}_{j}\}_{j=1}^{K}$ with similarity scores $\{s_{j}\}$. A multimodal reasoning model produces verification confidences $v_{j}$, and we define the anchor set as:

$$
A=\{\hat{I}_{j}\mid v_{j}\geq\psi\}.
$$

To control cost, IQE employs early-stop (accept initial ranking if $s_{1}>\xi$) and a fallback trigger (activate IQE only when the query is short/ambiguous or retrieval confidence is low).

#### 2.2.2 Interactive Query Refinement

For each anchor $a\in A$, diagnostic questions $C_{a}=\mathcal{G}_{\text{ques}}(T,a)$ are generated, with the detailed strategy provided in our code repository. Answers from the MLLM are collected as:

$$
r_{a}=\{(c_{i},\,a_{i},\,p_{i})\}_{i=1}^{|C_{a}|},
$$

and only high-confidence responses ($p_{i}\geq\tau$) are retained. Answers across anchors are aggregated via confidence-weighted voting:

$$
\mathrm{score}(u)=\frac{1}{|A|}\sum_{a\in A}\sum_{(c,a^{\prime},p)\in r_{a}}\mathbf{1}[a^{\prime}\equiv u]\cdot p,
$$

and the evidence set is $R=\{u\mid\mathrm{score}(u)\geq\eta\}$. Finally, the reconstructor synthesizes the enhanced query:

$$
T^{\prime}=\mathrm{MLLM}_{\text{agg}}(T,R).
$$

#### 2.2.3 Query Fusion and Re-ranking

The final retrieval score combines original and enhanced similarities, with an optional anchor bonus:

$$
\mathrm{Score}(I)=\gamma\cdot\mathrm{sim}(T,I)+(1-\gamma)\cdot\mathrm{sim}(T^{\prime},I)+\beta\cdot\mathbf{1}[I\in A].
$$

A safeguard reverts to the original ranking if $T^{\prime}$ causes a substantial drop in validation alignment. Further implementation details will be released with the code.

## 3 Experiments

### 3.1 Experimental Settings

Datasets and Metrics. We evaluate CONQUER on three standard TBPS benchmarks: CUHK-PEDES, ICFG-PEDES, and RSTPReid, following their official train/validation/test splits. Performance is measured using Rank- $k$ accuracy ($k=1,5$) and mean Average Precision (mAP) under the text-to-image retrieval setting.

Implementation Details. The visual and textual backbones are initialized with CLIP ViT-B/16. The CARE module is trained using the Adam optimizer (batch size 64, learning rate $1\times 10^{-4}$ with cosine decay) for 60 epochs. The loss weights in Eq. 8 are set to $\alpha=0.5$ and $\beta=0.1$. For IQE, we employ Qwen2.5-VL-7B as the reasoning engine, fine-tuned via LoRA. Inference hyperparameters are set as: top- $K$ anchors $K=5$, re-ranking weight $\gamma=0.6$, and thresholds $\psi=0.90$, $\xi=0.85$, $\tau=0.85$, and $\eta=0.5$.

Table 1: Performance comparison with state-of-the-art methods on CUHK-PEDES, ICFG-PEDES, and RSTPReid datasets. The best results are in bold and the second best are underlined.

<table><thead><tr><th rowspan="2">Methods</th><th rowspan="2">Ref.</th><th rowspan="2">Image Enc.</th><th rowspan="2">Text Enc.</th><th colspan="3">CUHK-PEDES</th><th colspan="3">ICFG-PEDES</th><th colspan="3">RSTPReid</th></tr><tr><th>R@1</th><th>R@5</th><th>mAP</th><th>R@1</th><th>R@5</th><th>mAP</th><th>R@1</th><th>R@5</th><th>mAP</th></tr></thead><tbody><tr><th>ViTAA <sup><a href="#fn:15">15</a></sup></th><td>ECCV20</td><td>RN50</td><td>LSTM</td><td>54.92</td><td>75.18</td><td>51.60</td><td>50.98</td><td>68.79</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><th>SSAN <sup><a href="#fn:16">16</a></sup></th><td>arXiv21</td><td>RN50</td><td>LSTM</td><td>61.37</td><td>80.15</td><td>-</td><td>54.23</td><td>72.63</td><td>-</td><td>43.50</td><td>67.80</td><td>-</td></tr><tr><th>IVT <sup><a href="#fn:17">17</a></sup></th><td>ECCV22</td><td>ViT-Base</td><td>BERT</td><td>65.59</td><td>83.11</td><td>60.66</td><td>56.04</td><td>73.60</td><td>-</td><td>46.70</td><td>70.00</td><td>-</td></tr><tr><th>BEAT <sup><a href="#fn:18">18</a></sup></th><td>MM23</td><td>RN101</td><td>BERT</td><td>65.61</td><td>83.45</td><td>-</td><td>58.25</td><td>75.92</td><td>-</td><td>48.10</td><td>73.10</td><td>-</td></tr><tr><th>LCR <sup>2</sup> S <sup><a href="#fn:19">19</a></sup></th><td>MM23</td><td>RN50</td><td>TextCNN</td><td>67.36</td><td>84.19</td><td>59.24</td><td>57.93</td><td>76.08</td><td>38.21</td><td>54.95</td><td>76.65</td><td>40.92</td></tr><tr><th>UniPT <sup><a href="#fn:20">20</a></sup></th><td>ICCV23</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>68.50</td><td>84.67</td><td>-</td><td>60.09</td><td>76.19</td><td>-</td><td>51.85</td><td>74.85</td><td>-</td></tr><tr><th>CFine <sup><a href="#fn:21">21</a></sup></th><td>TIP23</td><td>CLIP-ViT</td><td>BERT</td><td>69.57</td><td>85.93</td><td>-</td><td>60.83</td><td>76.55</td><td>-</td><td>50.55</td><td>72.50</td><td>-</td></tr><tr><th>DM-Adapter <sup><a href="#fn:10">10</a></sup></th><td>AAAI25</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>72.17</td><td>88.74</td><td>64.33</td><td>62.64</td><td>79.53</td><td>36.50</td><td>60.00</td><td>82.10</td><td>47.37</td></tr><tr><th>IRRA <sup><a href="#fn:3">3</a></sup></th><td>CVPR23</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>73.38</td><td>89.93</td><td>66.13</td><td>63.46</td><td>80.25</td><td>38.06</td><td>60.20</td><td>81.30</td><td>47.17</td></tr><tr><th>TBPS <sup><a href="#fn:22">22</a></sup></th><td>AAAI24</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>73.54</td><td>88.19</td><td>65.38</td><td>65.05</td><td>80.34</td><td>39.83</td><td>61.95</td><td>83.55</td><td>48.26</td></tr><tr><th>MGRL <sup><a href="#fn:11">11</a></sup></th><td>ICASSP24</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>73.91</td><td>90.68</td><td>67.28</td><td>63.87</td><td>82.34</td><td>39.12</td><td>-</td><td>-</td><td>-</td></tr><tr><th>DCEL <sup><a href="#fn:23">23</a></sup></th><td>MM23</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>75.02</td><td>90.89</td><td>-</td><td>64.88</td><td>81.34</td><td>-</td><td>61.35</td><td>83.95</td><td>-</td></tr><tr><th>OCDL <sup><a href="#fn:24">24</a></sup></th><td>ICASSP25</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>75.10</td><td>89.43</td><td>68.18</td><td>64.53</td><td>80.23</td><td>40.76</td><td>61.60</td><td>82.35</td><td>49.77</td></tr><tr><th>CFAM <sup><a href="#fn:9">9</a></sup></th><td>CVPR24</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>75.60</td><td>90.53</td><td>67.27</td><td>65.38</td><td>81.17</td><td>39.42</td><td>62.45</td><td>83.55</td><td>49.50</td></tr><tr><th>DP <sup><a href="#fn:25">25</a></sup></th><td>AAAI24</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>75.66</td><td>90.59</td><td>66.58</td><td>65.61</td><td>81.73</td><td>39.14</td><td>62.48</td><td>83.77</td><td>48.86</td></tr><tr><th>RDE <sup><a href="#fn:26">26</a></sup></th><td>CVPR24</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>75.94</td><td>90.14</td><td>67.56</td><td>67.68</td><td>82.47</td><td>40.06</td><td>65.35</td><td>83.95</td><td>50.88</td></tr><tr><th>CTGI <sup><a href="#fn:12">12</a></sup></th><td>EMNLP25</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>67.82</td><td>85.45</td><td>55.14</td><td>56.16</td><td>73.18</td><td>32.40</td><td>66.35</td><td>85.50</td><td>51.51</td></tr><tr><th>CONQUER (Ours)</th><td>-</td><td>CLIP-ViT</td><td>CLIP-Xformer</td><td>77.13</td><td>90.06</td><td>68.75</td><td>67.70</td><td>81.88</td><td>40.36</td><td>68.40</td><td>84.95</td><td>51.73</td></tr></tbody></table>

### 3.2 Comparisons with State-of-the-Art Methods

In this subsection, as shown in Table 1, we present a comparison of CONQUER with existing methods on three TBPS datasets. On the CUHK-PEDES dataset, with CLIP-ViT as the backbone, CONQUER achieves the best results, obtaining 77.13% R@1 and 68.75% mAP, and outperforms recent methods such as OCDL [^24] and RDE [^26]. For the ICFG-PEDES dataset, it also delivers strong performance with CLIP-ViT, reaching 67.70% R@1 and 40.36% mAP. Since it surpasses methods including IRRA [^3] and DCEL [^23], our method remains a leading solution with superior overall performance across multiple datasets. On the RSTPReid dataset, our approach further performs excellently, outperforming RDE [^26] with 68.40% R@1 and 51.73% mAP, and ranks the highest among all methods. In conclusion, our method consistently outperforms most state-of-the-art techniques across all three datasets, thus demonstrating its superior performance and robustness.

### 3.3 Robustness of the Method

To further assess the generalization ability of CONQUER, we conduct comprehensive cross-domain experiments on widely used TBPS benchmarks. As summarized in Table 2, our approach consistently achieves superior results compared to representative methods under all transfer settings. In particular, CONQUER surpasses strong baselines such as IRRA and SEN not only in R@1 but also in R@5 and mAP, indicating stable gains across different evaluation criteria. The transfer from CUHK-PEDES to RSTPReid and from RSTPReid to CUHK-PEDES is especially challenging due to large domain gaps, yet CONQUER improves R@1 by 3.10% and 7.87% over SEN, respectively. These results highlight that our CARE and IQE modules jointly enhance the robustness of the learned representations, enabling effective adaptation to unseen domains and making the framework highly suitable for real-world deployment.

Table 2: Cross-domain performance evaluation. The notation “Source $\rightarrow$ Target” denotes that the model is trained on the source dataset and tested on the target dataset. Abbreviations used: CUHK (CUHK-PEDES), ICFG (ICFG-PEDES), and RSTP (RSTPReid). The best results are highlighted in bold, and the second-best are underlined.

<table><thead><tr><th>Method</th><th>Domain</th><th>R@1</th><th>R@5</th><th>mAP</th></tr></thead><tbody><tr><th rowspan="6">IRRA <sup><a href="#fn:3">3</a></sup></th><th>CUHK <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> RSTP</th><td>53.30</td><td>77.15</td><td>39.63</td></tr><tr><th>CUHK <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> ICFG</th><td>42.42</td><td>62.11</td><td>21.77</td></tr><tr><th>ICFG <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> RSTP</th><td>45.30</td><td>69.35</td><td>36.83</td></tr><tr><th>ICFG <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> CUHK</th><td>33.46</td><td>56.30</td><td>31.56</td></tr><tr><th>RSTP <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> ICFG</th><td>32.30</td><td>49.69</td><td>20.54</td></tr><tr><th>RSTP <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> CUHK</th><td>32.80</td><td>55.25</td><td>30.29</td></tr><tr><th rowspan="6">SEN <sup><a href="#fn:27">27</a></sup></th><th>CUHK <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> RSTP</th><td>55.50</td><td>77.85</td><td>45.29</td></tr><tr><th>CUHK <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> ICFG</th><td>45.34</td><td>63.45</td><td>23.26</td></tr><tr><th>ICFG <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> RSTP</th><td>47.45</td><td>71.95</td><td>39.86</td></tr><tr><th>ICFG <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> CUHK</th><td>37.88</td><td>60.48</td><td>35.07</td></tr><tr><th>RSTP <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> ICFG</th><td>36.23</td><td>53.31</td><td>22.32</td></tr><tr><th>RSTP <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> CUHK</th><td>35.40</td><td>57.71</td><td>33.41</td></tr><tr><th rowspan="6">CONQUER (Ours)</th><th>CUHK <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> RSTP</th><td>58.60</td><td>77.00</td><td>42.20</td></tr><tr><th>CUHK <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> ICFG</th><td>48.59</td><td>65.43</td><td>24.65</td></tr><tr><th>ICFG <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> RSTP</th><td>54.55</td><td>71.60</td><td>39.44</td></tr><tr><th>ICFG <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> CUHK</th><td>40.98</td><td>60.33</td><td>36.18</td></tr><tr><th>RSTP <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> ICFG</th><td>44.81</td><td>56.60</td><td>26.58</td></tr><tr><th>RSTP <math><semantics><mo>→</mo> <annotation>\rightarrow</annotation></semantics></math> CUHK</th><td>43.27</td><td>57.37</td><td>35.08</td></tr></tbody></table>

### 3.4 Ablation Studies

To verify the specific contributions of the CARE and IQE modules, we conducted comprehensive ablation studies on the RSTPReid dataset, as detailed in Table 3. The baseline model serves as a starting point, achieving a Rank-1 accuracy of 66.50% and an mAP of 51.47%. When the CARE or IQE modules are deployed individually, we observe only marginal improvements over the baseline. This indicates that neither module alone is sufficient to fully address the cross-modal challenges. However, a significant performance boost is realized when both modules are integrated, raising the Rank-1 to 68.40% and mAP to 51.73%. This result clearly demonstrates the synergistic effect between the two components: CARE optimizes feature alignment during the training phase, while IQE refines the retrieval targets during inference. Together, they effectively complement each other to achieve the optimal experimental results.

Table 3: Ablation study of CONQUER components on RSTPReid.

<table><tbody><tr><td rowspan="2">Index</td><td rowspan="2">Base</td><td colspan="2">Components</td><td></td><td colspan="3">Retrieval Performance</td></tr><tr><td>CARE</td><td>IQE</td><td></td><td>R@1</td><td>R@5</td><td>mAP</td></tr><tr><td>1</td><td>✓</td><td></td><td>✓</td><td></td><td>66.50</td><td>84.65</td><td>51.47</td></tr><tr><td>2</td><td>✓</td><td>✓</td><td></td><td></td><td>66.15</td><td>84.15</td><td>51.54</td></tr><tr><td>3</td><td>✓</td><td>✓</td><td>✓</td><td></td><td>68.40</td><td>84.95</td><td>51.73</td></tr></tbody></table>

## 4 Conclusion

We present CONQUER, a two-stage framework for Text-Based Person Search. In the training phase, our CARE module enhances cross-modal representation through multi-granularity encoding, complementary pair mining, and context-guided Optimal Transport. At inference, the plug-and-play IQE module adaptively refines ambiguous or incomplete queries by anchor selection and attribute enrichment, all without retraining. Extensive experiments on three public benchmarks demonstrate that CONQUER consistently surpasses strong baselines in both in-domain and cross-domain scenarios. Ablation studies further verify the complementary effects of CARE and IQE. For future work, we aim to further reduce inference latency, improve attribute extraction reliability, and extend CONQUER to broader cross-modal retrieval tasks.

[^1]: Shuang Li, Tong Xiao, Hongsheng Li, Bolei Zhou, Dayu Yue, and Xiaogang Wang, “Person search with natural language description,” in Proceedings of the IEEE conference on computer vision and pattern recognition, 2017, pp. 1970–1979.

[^2]: Surbhi Aggarwal, Venkatesh Babu Radhakrishnan, and Anirban Chakraborty, “Text-based person search via attribute-aided matching,” in Proceedings of the IEEE/CVF winter conference on applications of computer vision, 2020, pp. 2617–2625.

[^3]: Ding Jiang and Mang Ye, “Cross-modal implicit relation reasoning and aligning for text-to-image person retrieval,” in Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, 2023, pp. 2787–2797.

[^4]: Zequn Xie, Haoming Ji, Chengxuan Li, and Lingwei Meng, “Dynamic uncertainty learning with noisy correspondence for text-based person search,” arXiv preprint arXiv:2505.06566, 2025.

[^5]: Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, et al., “Learning transferable visual models from natural language supervision,” in International conference on machine learning. PmLR, 2021, pp. 8748–8763.

[^6]: Runhao Liu, Ziming Chen, You Li, Zequn Xie, and Peng Zhang, “Integrated planning and machine-level scheduling for high-mix discrete manufacturing: A profit-driven heuristic framework,” 2025.

[^7]: Zequn Xie, Boyun Zhang, Yuxiao Lin, and Tao Jin, “Delving deeper: Hierarchical visual perception for robust video-text retrieval,” 2026.

[^8]: Zequn Xie, Xin Liu, Boyun Zhang, Yuxiao Lin, Sihang Cai, and Tao Jin, “Hvd: Human vision-driven video representation learning for text-video retrieval,” 2026.

[^9]: Jialong Zuo, Hanyu Zhou, Ying Nie, Feng Zhang, Tianyu Guo, Nong Sang, Yunhe Wang, and Changxin Gao, “Ufinebench: Towards text-based person retrieval with ultra-fine granularity,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 22010–22019.

[^10]: Yating Liu, Zimo Liu, Xiangyuan Lan, Wenming Yang, Yaowei Li, and Qingmin Liao, “Dm-adapter: Domain-aware mixture-of-adapters for text-based person retrieval,” in Proceedings of the AAAI Conference on Artificial Intelligence, 2025, vol. 39, pp. 5703–5711.

[^11]: Tianle Lv, Shuang Li, Jiaxu Leng, and Xinbo Gao, “Mgrl: Mutual-guidance representation learning for text-to-image person retrieval,” in ICASSP 2024-2024 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP). IEEE, 2024, pp. 2895–2899.

[^12]: Zequn Xie, Chuxin Wang, Yeqiang Wang, Sihang Cai, Shulei Wang, and Tao Jin, “Chat-driven text generation and interaction for person retrieval,” in Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 2025, pp. 5259–5270.

[^13]: Liying Gao, Kai Niu, Zehong Ma, Bingliang Jiao, Tonghao Tan, and Peng Wang, “Text-guided visual feature refinement for text-based person search,” in Proceedings of the 2021 International Conference on Multimedia Retrieval, 2021, pp. 118–126.

[^14]: Shenshen Li, Chen He, Xing Xu, Fumin Shen, Yang Yang, and Heng Tao Shen, “Adaptive uncertainty-based learning for text-based person retrieval,” in Proceedings of the AAAI Conference on Artificial Intelligence, 2024, vol. 38, pp. 3172–3180.

[^15]: Zhe Wang, Zhiyuan Fang, Jun Wang, and Yezhou Yang, “Vitaa: Visual-textual attributes alignment in person search by natural language,” in European conference on computer vision. Springer, 2020, pp. 402–420.

[^16]: Zefeng Ding, Changxing Ding, Zhiyin Shao, and Dacheng Tao, “Semantically self-aligned network for text-to-image part-aware person re-identification,” arXiv preprint arXiv:2107.12666, 2021.

[^17]: Xiujun Shu, Wei Wen, Haoqian Wu, Keyu Chen, Yiran Song, Ruizhi Qiao, Bo Ren, and Xiao Wang, “See finer, see more: Implicit modality alignment for text-based person retrieval,” in European Conference on Computer Vision. Springer, 2022, pp. 624–641.

[^18]: Yiwei Ma, Xiaoshuai Sun, Jiayi Ji, Guannan Jiang, Weilin Zhuang, and Rongrong Ji, “Beat: Bi-directional one-to-many embedding alignment for text-based person retrieval,” in Proceedings of the 31st ACM international conference on multimedia, 2023, pp. 4157–4168.

[^19]: Shuanglin Yan, Neng Dong, Jun Liu, Liyan Zhang, and Jinhui Tang, “Learning comprehensive representations with richer self for text-to-image person re-identification,” in Proceedings of the 31st ACM international conference on multimedia, 2023, pp. 6202–6211.

[^20]: Zhiyin Shao, Xinyu Zhang, Changxing Ding, Jian Wang, and Jingdong Wang, “Unified pre-training with pseudo texts for text-to-image person re-identification,” in Proceedings of the IEEE/CVF international conference on computer vision, 2023, pp. 11174–11184.

[^21]: Shuanglin Yan, Neng Dong, Liyan Zhang, and Jinhui Tang, “Clip-driven fine-grained text-image person re-identification,” IEEE Transactions on Image Processing, vol. 32, pp. 6032–6046, 2023.

[^22]: Min Cao, Yang Bai, Ziyin Zeng, Mang Ye, and Min Zhang, “An empirical study of clip for text-based person search,” in Proceedings of the AAAI Conference on Artificial Intelligence, 2024, vol. 38, pp. 465–473.

[^23]: Shenshen Li, Xing Xu, Yang Yang, Fumin Shen, Yijun Mo, Yujie Li, and Heng Tao Shen, “Dcel: deep cross-modal evidential learning for text-based person retrieval,” in Proceedings of the 31st ACM International Conference on Multimedia, 2023, pp. 6292–6300.

[^24]: Haiwen Li, Delong Liu, Fei Su, and Zhicheng Zhao, “Object-centric discriminative learning for text-based person retrieval,” in ICASSP 2025-2025 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP). IEEE, 2025, pp. 1–5.

[^25]: Zifan Song, Guosheng Hu, and Cairong Zhao, “Diverse person: Customize your own dataset for text-based person search,” in Proceedings of the AAAI Conference on Artificial Intelligence, 2024, vol. 38, pp. 4943–4951.

[^26]: Yang Qin, Yingke Chen, Dezhong Peng, Xi Peng, Joey Tianyi Zhou, and Peng Hu, “Noisy-correspondence learning for text-to-image person re-identification,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024, pp. 27197–27206.

[^27]: Delong Liu, Haiwen Li, Zhicheng Zhao, and Yuan Dong, “Text-guided image restoration and semantic enhancement for text-to-image person retrieval,” Neural Networks, vol. 184, pp. 107028, 2025.
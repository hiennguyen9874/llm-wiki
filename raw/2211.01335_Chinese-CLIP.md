# Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese

An Yang<sup>\*1</sup>, Junshu Pan<sup>\*1,2†</sup>, Junyang Lin<sup>\*1</sup>,  
Rui Men<sup>1</sup>, Yichang Zhang<sup>1</sup>, Jingren Zhou<sup>1</sup>, Chang Zhou<sup>1♠</sup>

<sup>1</sup>DAMO Academy, Alibaba Group

<sup>2</sup>Beihang University

{ya235025, panjunshu.pjs, junyang.ljy, ericzhou.zc}@alibaba-inc.com

## Abstract

The tremendous success of vision-language foundation models has promoted the research and application of computer vision and multimodal representation learning. However, it is still difficult to effectively transfer such foundation models to language-specific scenarios. In this work, we propose Chinese CLIP with the two-stage pretraining method which trains the model with locked-image tuning in the first stage and contrastive tuning in the second one. Specifically, we have developed 5 Chinese CLIP models of multiple sizes, spanning from 77 to 958 million parameters, and we have pretrained them on a collected large-scale dataset of Chinese image-text pairs. Our comprehensive experiments demonstrate that Chinese CLIP can achieve the state-of-the-art performance on MUGE, Flickr30K-CN, and COCO-CN in the setups of zero-shot learning and finetuning, and it is able to achieve competitive performance in zero-shot image classification based on the evaluation on the ELEVATER benchmark. We have released our codes, models, and demos<sup>1</sup>.

## 1 Introduction

Starting from the burst of pretraining in NLP, foundation models have attracted attention from multiple research communities. Foundation models that learn from large-scale unsupervised or weakly supervised data play as the basis of downstream models. A milestone of foundation models (Bommasani et al., 2021) in multimodal representation learning is CLIP (Radford et al., 2021). Different from the conventional generative pretraining, CLIP is a contrastive-learning-based model pretrained on a large-scale dataset of around 400 mil-

Figure 1: **Comparison of CLIP and Chinese CLIP models on the Chinese native retrieval benchmark MUGE.** On the benchmark based on the native data (which are mostly crawled from the language-native websites, in contrast with the translated data from websites of other countries.), CLIP performs far worse than our Chinese CLIP. Note that CLIP<sub>ViT-H/14</sub> is not released, we use the model from OpenCLIP (Ilharco et al., 2021) instead.

lion image-text pair data collected from the web. Despite the simplicity of the method, CLIP not only achieved outstanding performance in vision-language retrieval but more importantly played as a vision foundation model and demonstrated state-of-the-art performance in zero-shot image classification across a series of datasets. CLIP which builds a connection between vision and language has been transforming the research in both multimodal representation learning and computer vision.

Be that as it may, it is difficult to efficiently transfer a cross-modal pretrained model to another language for several causes. First, learning to model the distribution of language-native vision and language data is significant for the transfer. Though CLIP performs as a strong foundation model in most scenarios, we find that it is hard for CLIP with machine translation to perform well on the Chinese-native cross-modal retrieval benchmark.

\*Co-first authors.

♠Corresponding author.

†Work done as an intern in DAMO Academy.

<sup>1</sup>Github: <https://github.com/OFA-Sys/Chinese-CLIP>  
P; ModelScope: <https://www.modelscope.cn/models>Figure 1 demonstrates large performance gaps between the original CLIP and our Chinese CLIP at all model scales. We assume that it is crucial for both encoders to learn from the language-native images and texts. Second, the performance of previous methods for Chinese multimodal pretraining has been inhibited by several factors. Pretraining from scratch requires collecting a large-scale quality language-specific image-text pair dataset similar to Web Image Text (WIT) for OpenAI CLIP (Fei et al., 2021; Xie et al., 2022). Though the fast transfer of CLIP to Chinese data can be realized by using CLIP initialization and Locked-Image Tuning (Zhai et al., 2022), the vision encoder still cannot learn the information of images from the language-specific domains (Gu et al., 2022).

Therefore, we propose Chinese CLIP, a language-specific vision-language foundation model pretrained on the publicly available Chinese image-text pair data. Additionally, we still use the same architecture as OpenAI CLIP. To realize efficient transfer of cross-modal foundation model to Chinese data, we develop a two-stage pretraining method, which is also adaptive to other vision-language foundation models, e.g., ALIGN, Florence, etc. Here in this work, we use CLIP as an example. To be specific, we first initialize both encoders with pretrained models, namely vision encoders from CLIP and text encoders from RoBERTa-wwm-Chinese (Cui et al., 2020). In Stage 1, we freeze the image encoder and only optimize the text encoder with LiT, and in Stage 2, we train both encoders with contrastive tuning 2. In this way, the new model can inherit from the foundation models through initialization and LiT, and effectively transfer to language-specific data through contrastive tuning.

We evaluate Chinese CLIP on 3 Chinese cross-modal retrieval datasets, including MUGE<sup>2</sup>, Flickr30K-CN (Lan et al., 2017), and COCO-CN (Li et al., 2019c). Experimental results demonstrate that both the large-size and huge-size Chinese CLIP reach state-of-the-art performance on the 3 datasets in the setups of both zero-shot learning and finetuning. Additionally, we evaluate the capability of zero-shot image classification on the track “Image Classification in the Wild” of the ELEVATER benchmark (Li et al., 2022b). On the classification datasets, Chinese CLIP demonstrates competitive performance in comparison with state-of-the-art

<sup>2</sup><https://tianchi.aliyun.com/muge>

The diagram illustrates the two-stage pretraining process for Chinese CLIP. In Stage 1, an image of a golden monkey and a text caption '一只金丝猴的照片 (Photo of a golden monkey)' are processed by a frozen Image Encoder and a frozen Text Encoder, respectively. The frozen weight icon (snowflake) above the Image Encoder and the frozen weight icon (flame) below the Text Encoder indicate that their weights are not being updated. In Stage 2, both encoders are unfrozen, as indicated by the unfrozen weight icon (flame) above the Image Encoder and the unfrozen weight icon (flame) below the Text Encoder. Both stages calculate a 'Contrastive Loss' between the image and text representations.

**Figure 2: An illustration of pretraining Chinese CLIP.** To leverage the advantages of the existing pretrained models, we initialize the image encoder with the OpenAI CLIP models, and the text encoder with the Chinese RoBERTa models. In Stage 1, we freeze the weights of the image encoder to avoid weight optimization, and in Stage 2, we unfreeze it and optimize both encoders.

methods and outperforms the Chinese baselines. Furthermore, we provide NVIDIA TensorRT and ONNX models for deployments, which run around 2 to 10 times faster than Pytorch models for inference.

In brief, our contributions are:

- • We propose Chinese CLIP, a simple implementation of CLIP pretrained on our collected large-scale Chinese image-text pair data, and we propose a two-stage pretraining method to achieve high pretraining efficiency and improved downstream performance.
- • Chinese CLIP achieves state-of-the-art performance in cross-modal retrieval in the setups of zero-shot learning and finetuning, and competitive performance in zero-shot image classification.

## 2 Method

CLIP (Radford et al., 2021) based on simple vision-language contrastive pretraining on large-scale weakly supervised data is a significant foundation model in multimodal representation learning. It can transfer to cross-modal retrieval directly, and its image encoder can play as a vision backbone. In this work, we propose to build a language-specific CLIP model by pretraining a vision-language model on large-scale Chinese multimodal data. In the following, we provide the details of method design and implementation of our Chinese CLIP.## 2.1 Data

One key to CLIP’s success should be the large-scale dataset for pretraining. Based on the experiments of a CLIP reimplementation (Ilharco et al., 2021), scaling up data and lengthening the training process can consistently improve the model performance in zero-shot learning. This year, the most recent multimodal pretrained models Wukong (Gu et al., 2022) and R2D2 (Xie et al., 2022) were pretrained on a public dataset of 100 million image-text pairs and an in-house dataset of 250 million samples, where only a subset of 23 million samples were released. For the facility in reimplementation, we aim at pretraining Chinese CLIP on as many publicly available data as possible, and thus we focus on collecting high-quality public datasets. We extract the Chinese data (with the mark “zh”) from the latest LAION-5B (Schuhmann et al., 2021), and collect the data from the Wukong dataset. However, due to the problems of unavailable links, we can only collect around 108 million samples and 72 million samples from LAION-5B and Wukong respectively. We additionally add the translated data from the classic English multimodal datasets, including Visual Genome (Krishna et al., 2017) and MSCOCO (Chen et al., 2015), where test sets are removed. Finally, we construct a dataset for Chinese multimodal pretraining with around 200 million image-text pairs.<sup>3</sup>

Below illustrates the procedure for data preprocessing. For the part of data from LAION-5B, we remove the samples with CLIP scores lower than 0.26 computed by mCLIP (Carlsson et al., 2022). Besides, we remove the samples with captions containing words in our internal blacklist. The blacklist contains words related to advertising, image filenames, etc. We remove those samples that are too short (fewer than 5 characters) or too long (more than 50 characters). For the images, we resize them to the resolution of  $224 \times 224$  for most cases and  $336 \times 336$  for the ViT-L/14@336px.

## 2.2 Pretraining Method

There are multiple design choices for pretraining the Chinese CLIP models. One of the simplest methods should be pretraining from scratch, where both the image and text encoders are randomly initialized. However, we assume that its performance will be limited by the quantity and quality of the

current pretraining data. To leverage the advantages of existent pretrained models, we initialize the models with weights from the pretrained checkpoints from the official release of CLIP<sup>4</sup> for the image encoder, and RoBERTa-wwm-ext and RBT3<sup>5</sup> for the text encoder. To adapt the model to the introduced pretraining data, it is available to pre-train it with “contrastive tuning”, similar to the way to transfer CLIP to downstream retrieval data. In comparison with contrastive tuning, Locked-image Tuning (LiT) (Zhai et al., 2022) demonstrated improved performance in downstream transfer.

In this work, we propose a two-stage pretraining method, as shown in Figure 2. The core idea is to first utilize LiT to enable the text encoder to read out high-quality representations from the foundation vision model from OpenAI CLIP, and then transfer the whole model to the domain of the introduced pretraining data. It is not sufficient to pretrain Chinese CLIP with solely LiT, as the image encoder should learn the information of the images of the Chinese datasets and model the distribution of such data. Before the two-stage pretraining, we first initialize both encoders with pretrained models. In Stage 1, we “lock” the image encoder by freezing its parameters during pretraining. We only pretrain the text encoder for vision-language alignment, based on the assumption that the vision backbone with pretrained weights is already a powerful vision foundation model (Zhai et al., 2022; Gu et al., 2022). We pretrain it until there is no salient performance improvement in downstream tasks, even if we prolong the pretraining progress. Then we switch to Stage 2, where we “unlock” the image encoder by enabling its optimization. In Stage 2, we continue pretraining without any parameter frozen, so that the image encoder can learn to model the distribution of the image data from Chinese websites. In the ablation study, we discuss the influence of the initialization of the pretrained checkpoints and pretraining methods on the downstream performance. Experimental results show that the two-stage pretraining method can outperform either pretraining from scratch or directly finetuning from the pretrained models.

<sup>4</sup><https://github.com/openai/CLIP> License: MIT.

<sup>5</sup><https://github.com/ymcui/Chinese-BERT-wwm> License: Apache 2.0

<sup>3</sup>We add around 20 million high-quality internal image-text pairs to provide more diversity.<table border="1">
<thead>
<tr>
<th>Tasks</th>
<th colspan="4">Zero-shot</th>
<th colspan="4">Finetuning</th>
</tr>
<tr>
<th>Metrics</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
<th>MR</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
<th>MR</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="9"><i>Tiny-size Model</i></td>
</tr>
<tr>
<td>CN-CLIP<sub>RN50</sub></td>
<td><b>42.6</b></td>
<td><b>68.6</b></td>
<td><b>77.9</b></td>
<td><b>63.0</b></td>
<td><b>48.6</b></td>
<td><b>75.1</b></td>
<td><b>84.0</b></td>
<td><b>69.2</b></td>
</tr>
<tr>
<td colspan="9"><i>Base-size Models</i></td>
</tr>
<tr>
<td>Wukong<sub>ViT-B/32</sub></td>
<td>33.4</td>
<td>59.3</td>
<td>69.7</td>
<td>54.1</td>
<td>39.2</td>
<td>66.9</td>
<td>77.4</td>
<td>61.2</td>
</tr>
<tr>
<td>R2D2<sub>ViT-B</sub></td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>47.4</td>
<td>75.1</td>
<td>83.5</td>
<td>68.7</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-B/16</sub></td>
<td><b>52.1</b></td>
<td><b>76.7</b></td>
<td><b>84.4</b></td>
<td><b>71.1</b></td>
<td><b>58.4</b></td>
<td><b>83.6</b></td>
<td><b>90.0</b></td>
<td><b>77.4</b></td>
</tr>
<tr>
<td colspan="9"><i>Large-size Models</i></td>
</tr>
<tr>
<td>Wukong<sub>ViT-L/14</sub></td>
<td>42.7</td>
<td>69.0</td>
<td>78.0</td>
<td>63.2</td>
<td>52.7</td>
<td>77.9</td>
<td>85.6</td>
<td>72.1</td>
</tr>
<tr>
<td>R2D2<sub>ViT-L/14</sub></td>
<td>49.5</td>
<td>75.7</td>
<td>83.2</td>
<td>69.5</td>
<td>60.1</td>
<td>82.9</td>
<td>89.4</td>
<td>77.5</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14</sub></td>
<td>56.3</td>
<td>79.8</td>
<td>86.2</td>
<td>74.1</td>
<td>63.3</td>
<td>85.6</td>
<td>91.3</td>
<td>80.1</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14@336px</sub></td>
<td><b>59.0</b></td>
<td><b>81.4</b></td>
<td><b>87.8</b></td>
<td><b>76.1</b></td>
<td><b>65.3</b></td>
<td><b>86.7</b></td>
<td><b>92.1</b></td>
<td><b>81.3</b></td>
</tr>
<tr>
<td colspan="9"><i>Huge-size Models</i></td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-H/14</sub></td>
<td><b>63.0</b></td>
<td><b>84.1</b></td>
<td><b>89.2</b></td>
<td><b>78.8</b></td>
<td><b>68.9</b></td>
<td><b>88.7</b></td>
<td><b>93.1</b></td>
<td><b>83.6</b></td>
</tr>
</tbody>
</table>

Table 1: Experimental results on MUGE-Retrieval. We report the performance of both baselines and Chinese CLIP models on text-to-image retrieval and image-to-text retrieval in the setups of zero-shot evaluation and finetuning.

<table border="1">
<thead>
<tr>
<th>Tasks</th>
<th colspan="6">Text-to-Image</th>
<th colspan="6">Image-to-Text</th>
</tr>
<tr>
<th>Setups</th>
<th colspan="3">Zero-shot</th>
<th colspan="3">Finetuning</th>
<th colspan="3">Zero-shot</th>
<th colspan="3">Finetuning</th>
</tr>
<tr>
<th>Metrics</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="13"><i>Tiny-size Model</i></td>
</tr>
<tr>
<td>CN-CLIP<sub>RN50</sub></td>
<td><b>48.8</b></td>
<td><b>76.0</b></td>
<td><b>84.6</b></td>
<td><b>66.7</b></td>
<td><b>89.4</b></td>
<td><b>94.1</b></td>
<td><b>60.0</b></td>
<td><b>85.9</b></td>
<td><b>92.0</b></td>
<td><b>84.2</b></td>
<td><b>96.7</b></td>
<td><b>98.0</b></td>
</tr>
<tr>
<td colspan="13"><i>Base-size Models</i></td>
</tr>
<tr>
<td>Wukong<sub>ViT-B/32</sub></td>
<td>45.7</td>
<td>73.8</td>
<td>82.2</td>
<td>67.6</td>
<td>89.6</td>
<td>94.2</td>
<td>66.2</td>
<td>88.7</td>
<td>94.3</td>
<td>83.9</td>
<td>97.6</td>
<td>99.0</td>
</tr>
<tr>
<td>R2D2<sub>ViT-B</sub></td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>78.3</td>
<td>94.6</td>
<td>97.0</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>92.6</td>
<td><b>99.1</b></td>
<td><b>99.8</b></td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-B/16</sub></td>
<td><b>62.7</b></td>
<td><b>86.9</b></td>
<td><b>92.8</b></td>
<td><b>79.1</b></td>
<td><b>94.8</b></td>
<td><b>97.4</b></td>
<td><b>74.6</b></td>
<td><b>93.5</b></td>
<td><b>97.1</b></td>
<td><b>93.5</b></td>
<td>99.0</td>
<td>99.5</td>
</tr>
<tr>
<td colspan="13"><i>Large-size Models</i></td>
</tr>
<tr>
<td>Wukong<sub>ViT-L/14</sub></td>
<td>51.7</td>
<td>78.9</td>
<td>86.3</td>
<td>77.4</td>
<td>94.5</td>
<td>97.0</td>
<td>76.1</td>
<td>94.8</td>
<td>97.5</td>
<td>92.7</td>
<td>99.1</td>
<td>99.6</td>
</tr>
<tr>
<td>R2D2<sub>ViT-L/14</sub></td>
<td>60.9</td>
<td>86.8</td>
<td>92.7</td>
<td><b>84.4</b></td>
<td>96.7</td>
<td>98.4</td>
<td>77.6</td>
<td>96.7</td>
<td><b>98.9</b></td>
<td>95.6</td>
<td><b>99.8</b></td>
<td><b>100.0</b></td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14</sub></td>
<td>68.0</td>
<td>89.7</td>
<td>94.4</td>
<td>82.7</td>
<td>96.7</td>
<td>98.6</td>
<td>80.2</td>
<td>96.6</td>
<td>98.2</td>
<td>96.1</td>
<td>99.5</td>
<td>99.9</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14@336px</sub></td>
<td><b>69.0</b></td>
<td><b>90.7</b></td>
<td><b>95.4</b></td>
<td><b>84.4</b></td>
<td><b>97.1</b></td>
<td><b>98.7</b></td>
<td><b>83.3</b></td>
<td><b>97.2</b></td>
<td>98.5</td>
<td><b>96.6</b></td>
<td><b>99.8</b></td>
<td><b>100.0</b></td>
</tr>
<tr>
<td colspan="13"><i>Huge-size Models</i></td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-H/14</sub></td>
<td><b>71.2</b></td>
<td><b>91.4</b></td>
<td><b>95.5</b></td>
<td><b>83.8</b></td>
<td><b>96.9</b></td>
<td><b>98.6</b></td>
<td><b>81.6</b></td>
<td><b>97.5</b></td>
<td><b>98.8</b></td>
<td><b>95.3</b></td>
<td><b>99.7</b></td>
<td><b>100.0</b></td>
</tr>
</tbody>
</table>

Table 2: Experimental results on Flickr30K-CN. We report the performance of both baselines and Chinese CLIP models on text-to-image retrieval and image-to-text retrieval in the setups of zero-shot evaluation and finetuning.

### 3 Evaluation

To comprehensively probe the effects of Chinese CLIP, we follow the conventional practice that we first evaluate its basic capabilities of cross-modal retrieval, i.e. text-to-image retrieval and image-to-text retrieval, in different domains, including e-commerce and the general domain. Additionally, as the contrastive-learning-based pretraining builds a foundation vision model that is semantically connected with natural language, we follow Radford et al. (2021) and evaluate its capabilities of zero-shot classification. Specifically, we validate Chinese CLIP on the classification datasets of the ELEVATER benchmark (Li et al., 2022b),

which is known as “Image Classification in the Wild (ICinW)”.

#### 3.1 Cross-modal Retrieval

##### 3.1.1 Datasets and Metrics

We validate Chinese CLIP on 3 cross-modal retrieval datasets, namely MUGE-Retrieval, Flickr30K-CN (Lan et al., 2017), and COCO-CN (Li et al., 2019c). MUGE-Retrieval is an image-text retrieval dataset, where data are extracted from Chinese E-commerce websites. Flickr30K-CN and COCO-CN are built from the classical datasets Flickr30K and MSCOCO-1K whose texts are translated into Chinese. Our<table border="1">
<thead>
<tr>
<th>Tasks</th>
<th colspan="6">Text-to-Image</th>
<th colspan="6">Image-to-Text</th>
</tr>
<tr>
<th>Setups</th>
<th colspan="3">Zero-shot</th>
<th colspan="3">Finetuning</th>
<th colspan="3">Zero-shot</th>
<th colspan="3">Finetuning</th>
</tr>
<tr>
<th>Metrics</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="13"><i>Tiny-size Model</i></td>
</tr>
<tr>
<td>CN-CLIP<sub>RN50</sub></td>
<td>48.1</td>
<td>81.3</td>
<td>90.5</td>
<td><b>66.8</b></td>
<td><b>91.1</b></td>
<td><b>97.0</b></td>
<td>51.6</td>
<td>81.2</td>
<td>90.5</td>
<td><b>68.4</b></td>
<td><b>93.3</b></td>
<td><b>97.8</b></td>
</tr>
<tr>
<td colspan="13"><i>Base-size Models</i></td>
</tr>
<tr>
<td>Wukong<sub>ViT-B/32</sub></td>
<td>49.2</td>
<td>79.4</td>
<td>87.9</td>
<td>67.0</td>
<td>91.4</td>
<td>96.7</td>
<td>48.3</td>
<td>77.8</td>
<td>88.8</td>
<td>65.8</td>
<td>90.3</td>
<td>96.6</td>
</tr>
<tr>
<td>R2D2<sub>ViT-B</sub></td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>75.1</td>
<td>94.2</td>
<td>98.1</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>76.1</td>
<td>95.3</td>
<td>98.5</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-B/16</sub></td>
<td>62.2</td>
<td>86.6</td>
<td>94.9</td>
<td><b>77.0</b></td>
<td><b>97.1</b></td>
<td><b>99.0</b></td>
<td>57.0</td>
<td>84.1</td>
<td>93.6</td>
<td><b>77.4</b></td>
<td><b>96.2</b></td>
<td><b>98.9</b></td>
</tr>
<tr>
<td colspan="13"><i>Large-size Models</i></td>
</tr>
<tr>
<td>Wukong<sub>ViT-L/14</sub></td>
<td>53.4</td>
<td>80.2</td>
<td>90.1</td>
<td>74.0</td>
<td>94.4</td>
<td>98.1</td>
<td>55.2</td>
<td>81.0</td>
<td>90.6</td>
<td>73.3</td>
<td>94.0</td>
<td>98.0</td>
</tr>
<tr>
<td>R2D2<sub>ViT-L/14</sub></td>
<td>56.4</td>
<td>85.0</td>
<td>93.1</td>
<td>79.1</td>
<td>96.5</td>
<td>98.9</td>
<td>63.3</td>
<td>89.3</td>
<td>95.7</td>
<td>79.3</td>
<td>97.1</td>
<td>98.7</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14</sub></td>
<td>64.0</td>
<td>89.2</td>
<td>94.4</td>
<td>78.9</td>
<td>96.3</td>
<td>99.0</td>
<td>60.4</td>
<td>84.2</td>
<td>92.9</td>
<td>80.2</td>
<td>96.7</td>
<td><b>99.2</b></td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14@336px</sub></td>
<td>64.7</td>
<td>89.6</td>
<td>94.6</td>
<td><b>80.1</b></td>
<td><b>96.7</b></td>
<td><b>99.2</b></td>
<td>63.4</td>
<td>87.2</td>
<td>94.4</td>
<td><b>81.2</b></td>
<td><b>97.2</b></td>
<td>99.1</td>
</tr>
<tr>
<td colspan="13"><i>Huge-size Models</i></td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-H/14</sub></td>
<td>69.2</td>
<td>89.9</td>
<td>96.1</td>
<td><b>81.5</b></td>
<td><b>96.9</b></td>
<td><b>99.1</b></td>
<td>63.0</td>
<td>86.6</td>
<td>92.9</td>
<td><b>83.5</b></td>
<td><b>97.3</b></td>
<td><b>99.2</b></td>
</tr>
</tbody>
</table>

Table 3: Experimental results on COCO-CN. We report the performance of both baselines and Chinese CLIP models on text-to-image retrieval and image-to-text retrieval in the setups of zero-shot evaluation and finetuning. Since machine translated COCO is included in our pretraining dataset, here the numbers of Chinese CLIP zero-shot performances are shown in gray.

evaluation includes setups of zero-shot learning and finetuning. For zero-shot learning, we use Chinese CLIP models to compute the similarity scores between images and texts and return the top- $K$  most similar candidates. For finetuning, we finetune the Chinese CLIP models for cross-modal retrieval with contrastive tuning. The evaluation is the same as that in zero-shot learning. The evaluation metrics are Recall@ $K$ , where  $K = \{1, 5, 10\}$ , and Mean Recall (MR, i.e., the average of Recall@ $K$ ). For comparison, we choose the base-size and large-size Wukong and R2D2 as the baselines, which are the previous SOTA models in Chinese multimodal representation learning. Following these baselines, we report validation performance on MUGE and test performance on Flickr30K-CN and COCO-CN. Note that in the setup of finetuning, R2D2<sup>6</sup> is essentially an end-to-end model of retrieval and ranking.

### 3.1.2 Results

Table 1 reports the model performance on MUGE-Retrieval. For the base-size model, CN-CLIP<sub>ViT-B/16</sub> outperforms the baselines on all metrics and in both setups of zero-shot learning and finetuning. Specifically, for the base-size models, CN-CLIP<sub>ViT-B/16</sub> surpasses Wukong<sub>ViT-B/32</sub> by 17.0 MR in zero-shot learning and surpasses

R2D2<sub>ViT-B</sub> by 8.7 MR in finetuning. Besides, the tiny model CN-CLIP<sub>RN50</sub> can outperform the base-size Wukong<sub>ViT-B/32</sub> by 8.9 MR in zero-shot learning and 8.0 MR in finetuning.

For the large-size models, CN-CLIP<sub>ViT-L/14</sub> can outperform both baselines in all metrics and CN-CLIP<sub>ViT-L/14@336px</sub> pretrained on images of a larger resolution can achieve the state-of-the-art performance. CN-CLIP<sub>ViT-L/14@336px</sub> outperforms R2D2<sub>ViT-L/14</sub> by 6.6 MR in zero-shot learning and 3.8 MR in finetuning. When scaling to CN-CLIP<sub>ViT-H/14</sub>, the performance is further improved. Compared with the best large-size model CN-CLIP<sub>ViT-L/14@336px</sub>, CN-CLIP<sub>ViT-H/14</sub> surpasses it by 2.7 MR in zero-shot learning and 2.3 MR in finetuning.

Table 2 and 3 report the model performance on Flickr30K-CN and COCO-CN. We focus on the evaluation of R@1. In both datasets, CN-CLIP achieves better performance than the baselines. For the base-size models, in the setup of zero-shot learning of Flickr30K-CN, CN-CLIP<sub>ViT-B/16</sub> surpasses Wukong<sub>ViT-B/32</sub> by 17.0 R@1 in text-to-image retrieval and 8.4 R@1 in image-to-text retrieval, and in the finetuning setup, CN-CLIP<sub>ViT-B/16</sub> surpasses R2D2<sub>ViT-B</sub> by 0.8 R@1 in image retrieval and 0.9 R@1 in text retrieval. Similarly, in the finetuning setup of COCO-CN, CN-CLIP<sub>ViT-B/16</sub> surpasses R2D2<sub>ViT-B</sub> by 1.9 R@1 in image retrieval and 1.3 R@1 in text retrieval. For the tiny-size CN-CLIP<sub>RN50</sub>, it

<sup>6</sup>Since the original paper of R2D2 does not provide the patch size of their base-size model, here we denote the model as R2D2<sub>ViT-B</sub>.again achieves or surpasses the performance of Wukong<sub>ViT-B/32</sub> in several metrics of Flickr30K-CN and COCO-CN. Specifically, CN-CLIP<sub>RN50</sub> surpasses Wukong<sub>ViT-B/32</sub> by 3.1 R@1 in the zero-shot learning of Flickr30K-CN image retrieval and by 2.6 R@1 in the finetuning of COCO-CN text retrieval.

For the large-size models, in the zero-shot setup of Flickr30K-CN, CN-CLIP<sub>ViT-L/14</sub> surpasses Wukong<sub>ViT-L/14</sub> by 16.3 R@1 in text-to-image retrieval and 4.1 R@1 in image-to-text retrieval. CN-CLIP<sub>ViT-L/14@336px</sub> further improves over CN-CLIP<sub>ViT-L/14</sub> by 1.0 R@1 in image retrieval and 3.1 R@1 in text retrieval. In the finetuning setup, CN-CLIP<sub>ViT-L/14</sub> surpasses R2D2<sub>ViT-L/14</sub> by 0.5 R@1 in text retrieval. CN-CLIP<sub>ViT-L/14@336px</sub> achieves equal performance with R2D2<sub>ViT-L/14</sub> in image retrieval and surpasses it by 1.0 R@1 in text retrieval. Similarly, in the finetuning setup of COCO-CN, CN-CLIP<sub>ViT-L/14</sub> surpasses R2D2<sub>ViT-L/14</sub> by 0.9 R@1 in text retrieval. CN-CLIP<sub>ViT-L/14@336px</sub> further surpasses R2D2<sub>ViT-L/14</sub> by 1.0 in image retrieval and 1.9 R@1 in text retrieval.

On Flickr30K-CN and COCO-CN, scaling from CN-CLIP<sub>ViT-L/14</sub> to CN-CLIP<sub>ViT-H/14</sub> improves the performance in almost all the metrics. Specifically, in the zero-shot setup of Flickr30K-CN, CN-CLIP<sub>ViT-H/14</sub> surpasses CN-CLIP<sub>ViT-L/14</sub> by 3.2 R@1 in image retrieval and 1.4 R@1 in text retrieval. Moreover, in the finetuning setup of COCO-CN, CN-CLIP<sub>ViT-H/14</sub> even surpasses CN-CLIP<sub>ViT-L/14@336px</sub> with larger image resolution by 1.4 R@1 in image retrieval and 2.3 R@1 in text retrieval. We also compare our CN-CLIP<sub>ViT-H/14</sub> with a huge CLIP-like model, T-Blethchley<sup>7</sup>. This model has 2.5 billion parameters and is pretrained on billions of multilingual image-caption pairs. In the finetuning setup of COCO-CN, with smaller sizes of model parameters and pretrain dataset, CN-CLIP<sub>ViT-H/14</sub> still surpasses T-Blethchley by 3.9 MR.

### 3.1.3 Ablation Study

Here we provide an ablation study on our proposed two-stage training methods. To validate its significance and effectiveness, we design several setups for the ablation study. Our experiments are conducted on CN-CLIP<sub>ViT-B/16</sub>. To evaluate the

influence of initialization, we pretrain a model from scratch, and to examine the influence of LiT, we pretrain a model without freezing the image encoder. For a better demonstration, we report the curves of model performance of zero-shot retrieval on different datasets in terms of pretraining progress, indicated by the number of processed samples.

Figure 3 shows the performance on different tasks, namely MUGE text-to-image retrieval, text-to-image and image-to-text retrieval on Flickr30K-CN and COCO-CN. In comparison with pretraining with pretrained model initialization, pretraining from scratch performs much worse though it shows consistent performance improvement in terms of pretraining progress. As to the importance of LiT, we observe different phenomena on different datasets. On MUGE, a dataset of samples originally collected from Chinese websites, we find that pretraining without LiT might be the best solution though its performance gap with two-stage pretraining is quite small. However, on the other datasets, i.e., Flickr30K-CN and COCO-CN, whose samples are translated from the English datasets, we find that our two-stage pretraining performs significantly better than pretraining without LiT. Furthermore, we observe a common phenomenon that in the two-stage pretraining, switching from Stage 1 to Stage 2 can effectively boost the model performance to a higher level. This reflects the importance of adapting the pretrained model to the data distribution of the Chinese multimodal data, especially those concerned with visual information.

## 3.2 Zero-shot Image Classification

### 3.2.1 Open-Domain Image Classification Benchmark in Chinese

Contrastive pretraining on image-text pairs builds a connection between vision and natural language. Natural language supervision instead of crowdsourced labeling endows models with the capability of zero-shot image classification by computing similarities between the given image and the text descriptions of the labels in the candidate set. Recent progress in this field is the ELEVATER benchmark (Li et al., 2022b). The track ICinW for open-domain image classification consists of a series of image classification datasets, including ImageNet (Deng et al., 2009), CIFAR (Krizhevsky et al., 2009), MNIST (Deng, 2012), etc. In order to evaluate Chinese CLIP on the datasets, we first

<sup>7</sup><https://www.microsoft.com/en-us/research/blog/turing-blethchley-a-universal-image-language-representation-model-by-microsoft/>Figure 3: Comparison of base-size Chinese CLIP models with different training methods on MUGE, Flickr30k-CN and COCO-CN.

<table border="1">
<thead>
<tr>
<th>Model</th>
<th>CIFAR10</th>
<th>CIFAR100</th>
<th>DTD</th>
<th>EuroSAT</th>
<th>FER</th>
<th>FGVC</th>
<th>KITTI</th>
<th>MNIST</th>
<th>PC</th>
<th>VOC</th>
<th>INet</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="12"><i>Original benchmark</i></td>
</tr>
<tr>
<td>DeCLIP</td>
<td>90.9</td>
<td>66.8</td>
<td>44.9</td>
<td>39.9</td>
<td>23.3</td>
<td>9.0</td>
<td>39.7</td>
<td>13.6</td>
<td>55.3</td>
<td>80.6</td>
<td>73.7</td>
</tr>
<tr>
<td>GIT</td>
<td>88.5</td>
<td>61.1</td>
<td>42.9</td>
<td>43.4</td>
<td>41.4</td>
<td>6.7</td>
<td>22.1</td>
<td>68.9</td>
<td>50.0</td>
<td>80.2</td>
<td>-</td>
</tr>
<tr>
<td>ALIGN</td>
<td><b>94.9</b></td>
<td>76.8</td>
<td><b>66.1</b></td>
<td>52.1</td>
<td><b>50.8</b></td>
<td>25.0</td>
<td><b>41.2</b></td>
<td>74.0</td>
<td>55.2</td>
<td>83.0</td>
<td><b>76.4</b></td>
</tr>
<tr>
<td>OpenCLIP</td>
<td>93.5</td>
<td>76.2</td>
<td>56.4</td>
<td>53.7</td>
<td>50.3</td>
<td>20.8</td>
<td>28.8</td>
<td>70.9</td>
<td>50.5</td>
<td>82.3</td>
<td>-</td>
</tr>
<tr>
<td>CLIP</td>
<td><b>94.9</b></td>
<td><b>77.0</b></td>
<td>56.0</td>
<td><b>63.0</b></td>
<td>48.3</td>
<td><b>33.3</b></td>
<td>11.5</td>
<td><b>79.0</b></td>
<td><b>62.3</b></td>
<td><b>84.0</b></td>
<td>76.2</td>
</tr>
<tr>
<td colspan="12"><i>Translated benchmark</i></td>
</tr>
<tr>
<td>BriVL</td>
<td>72.3</td>
<td>35.9</td>
<td>18.8</td>
<td>25.5</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>24.3</td>
</tr>
<tr>
<td>Wukong</td>
<td>95.4</td>
<td>77.1</td>
<td>40.9</td>
<td>50.3</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>55.0</td>
</tr>
<tr>
<td>CN-CLIP</td>
<td><b>96.0</b></td>
<td><b>79.7</b></td>
<td><b>51.2</b></td>
<td><b>52.0</b></td>
<td><b>55.1</b></td>
<td><b>26.2</b></td>
<td><b>49.9</b></td>
<td><b>79.4</b></td>
<td><b>63.5</b></td>
<td><b>84.9</b></td>
<td><b>59.6</b></td>
</tr>
</tbody>
</table>

Table 4: Experimental results of the zero-shot image classification performance of models on ICinW.

transform the datasets for Chinese models by translating labels and prompts into Chinese.

### 3.2.2 Experimental Results

Table 4 reports the performance of both English models and Chinese models. The baselines pretrained on English data include DeCLIP (Li et al., 2021b), ALIGN (Jia et al., 2021), CLIP (Radford et al., 2021), and OpenCLIP (Ilharco et al., 2021), and the baselines pretrained on Chinese data include BriVL (Fei et al., 2021) and Wukong (Gu et al., 2022). We report the results of the variant with the best downstream performance for the models.

We first focus on the comparison with the Chinese baselines. To be specific, on all datasets in-

cluding ImageNet classification, Chinese CLIP surpasses both baselines significantly, and the relative achievements on some datasets are over 100%. Besides, we also compare Chinese CLIP with the foundation models, e.g., CLIP and ALIGN, which are pretrained on English data. It can be found that Chinese CLIP outperforms CLIP or ALIGN on CIFAR-10, CIFAR-100, FER-2013, KITTI-Distance, MNIST, PatchCamelyon, and Pascal-VOC-2007. Also, on the classification datasets for general concepts or objects common in both western and eastern culture, Chinese CLIP consistently achieves better performance. This indicates that Chinese CLIP is capable of categorizing images to general prototypes.

However, as to the classification concerned withproper nouns, e.g., FGVC-Aircraft, it is difficult for all models to achieve high accuracy. We assume that the related images and texts are not common in the pretraining datasets, and it is also hard for the models to understand the names of airplanes without finetuning. Specifically, for Chinese models, the translation or even transliteration can significantly affect the performance of Chinese CLIP. It encourages building a benchmark of “Image Classification in the Wild for Chinese Models”.

### 3.2.3 Analysis

**Sensitivity to Handcrafted Prompts** While the benchmark ELEVATER provides specific prompts for each dataset, we find that this is not always the best option, in comparison with our baseline, translation of the prompts provided by OpenAI CLIP. The baseline with around 90 prompts performs the best on average. However, for some datasets, specific prompts designed with human knowledge can boost the performance significantly. A typical case is the classification of airplanes. We test CN-CLIP<sub>ViT-L/14</sub> with our specified prompts that are related to the knowledge of aircraft, e.g., “label, a photo of an airplane”, “label, a zoomed image of a fighter”, etc., and the translation of the OpenAI prompts. Experimental results show that the model can achieve an accuracy of 16.0 with the specified prompts but only 13.8 with the OpenAI prompts.

**Inability to Understand Negation** Previous studies (Khandelwal and Sawant, 2019; Hosseini et al., 2021) demonstrate that even strong NLP pretrained models often make mistakes in negation problems. We explore CLIP’s capability to understand negation by conducting experiments on KITTI-Distance (Fritsch et al., 2013) and PatchCamelyon (Veeling et al., 2018). KITTI-Distance provides 4 options for models to judge, including “next to a car”, “near a car”, “at a distance away from a car”, and “no car”. The last one is concerned with negation. We compare the model performance using the text “no cars” and “others” for the last label. We observe that it is hard for the model to understand negation. By changing the label from “others” to “no cars”, the performance drops by 48.1% in accuracy (49.9 vs. 25.9). Similarly, in the experiments on PatchCamelyon, the performance drops from 63.5 to 50.2 by changing labels from “mainly red” and “green block in the middle” to “no green block in the middle” and “green block in the middle”. This shows the limitation of the

training of CLIP in learning negation. The texts in the pretraining datasets are mostly descriptions of the images, which indicate their objects or features but often do not indicate the absence of objects.

### 3.3 Deployment

For deployment, we develop ONNX-based and TensorRT-based models based on our Pytorch-based pretrained Chinese CLIP models. As expected, we observe that the inference efficiency increases significantly while there is almost no performance sacrifice. Specifically, the inference efficiency of TensorRT-based models is around 2 to 10 times faster than the Pytorch-based models. More statistics are listed in Appendix A.6.

## 4 Related Work

Previous vision-language pretrained models are mostly BERT/T5-style (Devlin et al., 2019; Rafel et al., 2020), which involves cross-modal fusion (Chen et al., 2020; Li et al., 2019a,b; Lu et al., 2019; Lin et al., 2020; Li et al., 2020; Huang et al., 2020; Xu et al., 2021; Zhang et al., 2021; Shen et al., 2021; Wang et al., 2021b, 2022a; Li et al., 2021a, 2022c,a; Wang et al., 2021a, 2022b). CLIP (Radford et al., 2021), instead, is a contrastive-learning-based two-tower model, which can serve as a vision foundation model. Following CLIP, a series of similar contrastive-learning-based multimodal pretrained models were proposed and reached new SOTAs in cross-modal retrieval and zero-shot classification (Jia et al., 2021; Yao et al., 2021; Yuan et al., 2021). Furthermore, CLIP can be adaptive to other models. A typical case is that CLIP is essential to many image generation models, e.g., DALL-E (Ramesh et al., 2021), DALL-E 2 (Ramesh et al., 2022), Stable Diffusion (Rombach et al., 2022), etc. The success of multimodal pretraining encouraged the transfer of the existing methods to Chinese pretraining, including generative pretrained models (Lin et al., 2021a; Fei et al., 2021; Yang et al., 2021; Lin et al., 2021b; Wang et al., 2022a) and contrastive pretrained models (Fei et al., 2021; Gu et al., 2022; Xie et al., 2022; Chen et al., 2022b).

## 5 Conclusion

In this work, we propose Chinese CLIP, a Chinese-specific vision-language foundation model. Specifically, we construct a pretraining dataset of around 200 million samples, and pretrain a series of Chi-nese CLIP models with the proposed two-stage pre-training method, which improves both pretraining efficiency and effectiveness. Our comprehensive evaluation shows that Chinese CLIP can reach state-of-the-art performance on multiple cross-modal retrieval datasets in zero-shot learning and finetuning. Furthermore, we demonstrate that Chinese CLIP models can also achieve competitive performance in zero-shot image classification across 10 datasets.

## Limitations

A number of issues reflect the limitations of this work but also point out some directions for our future research. In this section, we generally discuss some limitations about the scale of data and model.

**Data** The core of CLIP pretraining is the simple but effective large-scale contrastive pretraining on extremely large-scale data. Though we have utilized around 200 million samples, compared with recent studies (Yuan et al., 2021; Chen et al., 2022a) the scale of our pretraining data is relatively small. Thus one of our next-step studies is scaling up the quantity of the pretraining data to evaluate the performance improvement with data scaling. Furthermore, we still find it hard to decide what a “high-quality” dataset for CLIP is. In the previous studies (Jia et al., 2021; Li et al., 2021b), the pre-processing methods are mostly simple to avoid the loss of data. However, there are still many samples where the image and text are not matched properly, which may provide negative information to the pretraining. In our future research, we plan to use the pretrained Chinese CLIP model to compute a score for each image-text pair in a larger dataset, filter those whose scores are under the specified threshold, and pretrain the new models with the new data. This is one of the possible solutions to explore the relationship between data quality and pretraining effectiveness. Also, such cycling might bring continuous performance enhancement in downstream tasks.

**Model** Recently we have witnessed that in many domains the scaling of model size can lead to consistent performance improvement (Gordon et al., 2021; Wei et al., 2022), and in this work, we also find that the scaling of model size for Chinese CLIP can achieve steady performance improvement in different downstream tasks, including retrieval and classification. Recent studies have scaled ViT and also CLIP-like models to a much larger scale than

our largest CN-CLIP<sub>ViT-H/14</sub>, e.g., the 3B Swin-v2 (Liu et al., 2022), the 4B ViT-e (Chen et al., 2022a), etc. In the future, we will continue exploring scaling up models in line with scaling up data in order to build a more effective Chinese CLIP.

Another issue of model scaling connected with the real-world application is how to build effective small models. Experimental results show that our smallest Chinese CLIP CN-CLIP<sub>RN50</sub> performs much worse than the ViT variants. However, in real-world applications, effective small models that are available for deployment are usually more welcomed. Thus it is necessary to explore distillation for CLIP so that the capability of large models can be transferred to small models for application.

## Ethics Statement

The proposed model is a contrastive-learning-based vision-language foundation model, which generates features for images and texts. Those features can be representation of visual and linguistic information, and they can support applications such as search engine, recommender system, etc. Besides, this model can play as a foundation model support recent image generation models, e.g., diffusion models (Ramesh et al., 2022). This may create risks as the AI generated contents may reflect harmful information, such as hate, bias, pornography, etc. In most cases, these cases should be attributed to the training of the image generation models. Still, we cannot avoid the negative effects from the CLIP representations to the generation. In the future, we will study how to filter pretraining data to avoid the potential risks.

## References

Rishi Bommasani, Drew A Hudson, Ehsan Adeli, Russ Altman, Simran Arora, Sydney von Arx, Michael S Bernstein, Jeannette Bohg, Antoine Bosselut, Emma Brunskill, et al. 2021. On the opportunities and risks of foundation models. [arXiv preprint arXiv:2108.07258](#).

Lukas Bossard, Matthieu Guillaumin, and Luc Van Gool. 2014. Food-101—mining discriminative components with random forests. In [European conference on computer vision](#), pages 446–461. Springer.

Fredrik Carlsson, Philipp Eisen, Faton Rekathati, and Magnus Sahlgren. 2022. Cross-lingual and multilingual clip. In [Proceedings of the Language Resources and Evaluation Conference](#), pages 6848–6854, Marseille, France. European Language Resources Association.Xi Chen, Xiao Wang, Soravit Changpinyo, AJ Piergiovanni, Piotr Padlewski, Daniel Salz, Sebastian Goodman, Adam Grycner, Basil Mustafa, Lucas Beyer, et al. 2022a. Pali: A jointly-scaled multilingual language-image model. [arXiv preprint arXiv:2209.06794](#).

Xinlei Chen, Hao Fang, Tsung-Yi Lin, Ramakrishna Vedantam, Saurabh Gupta, Piotr Dollár, and C. Lawrence Zitnick. 2015. Microsoft COCO captions: Data collection and evaluation server. [CoRR](#), abs/1504.00325.

Yen-Chun Chen, Linjie Li, Licheng Yu, Ahmed El Kholy, Faisal Ahmed, Zhe Gan, Yu Cheng, and Jingjing Liu. 2020. UNITER: universal image-text representation learning. In *ECCV 2020*, volume 12375 of *Lecture Notes in Computer Science*, pages 104–120. Springer.

Zhong-Yong Chen, Guangyi Liu, Bohan Zhang, Fulong Ye, Qinghong Yang, and Ledell Yu Wu. 2022b. Altclip: Altering the language encoder in clip for extended language capabilities. [ArXiv](#), abs/2211.06679.

Gong Cheng, Junwei Han, and Xiaoqiang Lu. 2017. Remote sensing image scene classification: Benchmark and state of the art. *Proceedings of the IEEE*, 105(10):1865–1883.

Mircea Cimpoi, Subhransu Maji, Iasonas Kokkinos, Sammy Mohamed, and Andrea Vedaldi. 2014. Describing textures in the wild. In *Proceedings of the IEEE conference on computer vision and pattern recognition*, pages 3606–3613.

Ekin D Cubuk, Barret Zoph, Dandelion Mane, Vijay Vasudevan, and Quoc V Le. 2019. Autoaugment: Learning augmentation strategies from data. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 113–123.

Yiming Cui, Wanxiang Che, Ting Liu, Bing Qin, Shijin Wang, and Guoping Hu. 2020. [Revisiting pre-trained models for Chinese natural language processing](#). In *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: Findings*, pages 657–668, Online. Association for Computational Linguistics.

Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li, and Li Fei-Fei. 2009. Imagenet: A large-scale hierarchical image database. In *2009 IEEE Computer Society Conference on Computer Vision and Pattern Recognition (CVPR 2009)*, 20-25 June 2009, Miami, Florida, USA, pages 248–255. IEEE Computer Society.

Li Deng. 2012. The mnist database of handwritten digit images for machine learning research [best of the web]. *IEEE signal processing magazine*, 29(6):141–142.

Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2019. BERT: pre-training of deep bidirectional transformers for language understanding. In *NAACL-HLT 2019*, pages 4171–4186. Association for Computational Linguistics.

Mark Everingham, Luc Van Gool, Christopher K. I. Williams, John M. Winn, and Andrew Zisserman. 2010. The pascal visual object classes (VOC) challenge. *Int. J. Comput. Vis.*, 88(2):303–338.

Nanyi Fei, Zhiwu Lu, Yizhao Gao, Guoxing Yang, Yuqi Huo, Jingyuan Wen, Haoyu Lu, Ruihua Song, Xin Gao, Tao Xiang, et al. 2021. Wenlan 2.0: Make ai imagine via a multimodal foundation model. [arXiv preprint arXiv:2110.14378](#).

Li Fei-Fei, Rob Fergus, and Pietro Perona. 2004. Learning generative visual models from few training examples: An incremental bayesian approach tested on 101 object categories. In *2004 conference on computer vision and pattern recognition workshop*, pages 178–178. IEEE.

Jannik Fritsch, Tobias Kuehnl, and Andreas Geiger. 2013. A new performance measure and evaluation benchmark for road detection algorithms. In *16th International IEEE Conference on Intelligent Transportation Systems (ITSC 2013)*, pages 1693–1700. IEEE.

Mitchell A. Gordon, Kevin Duh, and Jared Kaplan. 2021. Data and parameter scaling laws for neural machine translation. In *EMNLP 2021*, pages 5915–5922. Association for Computational Linguistics.

Jiaxi Gu, Xiaojun Meng, Guansong Lu, Lu Hou, Minzhe Niu, Hang Xu, Xiaodan Liang, Wei Zhang, Xin Jiang, and Chunjing Xu. 2022. Wukong: 100 million large-scale chinese cross-modal pre-training dataset and a foundation framework. [arXiv preprint arXiv:2202.06767](#).

Patrick Helber, Benjamin Bischke, Andreas Dengel, and Damian Borth. 2019. Eurosat: A novel dataset and deep learning benchmark for land use and land cover classification. *IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing*, 12(7):2217–2226.

Arian Hosseini, Siva Reddy, Dzmitry Bahdanau, R Devon Hjelm, Alessandro Sordoni, and Aaron Courville. 2021. Understanding by understanding not: Modeling negation in language models. [arXiv preprint arXiv:2105.03519](#).

Zhicheng Huang, Zhaoyang Zeng, Bei Liu, Dongmei Fu, and Jianlong Fu. 2020. Pixel-bert: Aligning image pixels with text by deep multi-modal transformers. [CoRR](#), abs/2004.00849.

Gabriel Ilharco, Mitchell Wortsman, Ross Wightman, Cade Gordon, Nicholas Carlini, Rohan Taori, Achal Dave, Vaishaal Shankar, Hongseok Namkoong, John Miller, Hannaneh Hajishirzi, Ali Farhadi, and Ludwig Schmidt. 2021. [Openclip](#). If you use this software, please cite it as below.Chao Jia, Yinfei Yang, Ye Xia, Yi-Ting Chen, Zarana Parekh, Hieu Pham, Quoc V Le, Yunhsuan Sung, Zhen Li, and Tom Duerig. 2021. Scaling up visual and vision-language representation learning with noisy text supervision. [arXiv preprint arXiv:2102.05918](#).

Aditya Khandelwal and Suraj Sawant. 2019. Negbert: a transfer learning approach for negation detection and scope resolution. [arXiv preprint arXiv:1911.04211](#).

Douwe Kiela, Hamed Firooz, Aravind Mohan, Vedanuj Goswami, Amanpreet Singh, Pratik Ringshia, and Davide Testuggine. 2020. The hateful memes challenge: Detecting hate speech in multimodal memes. *Advances in Neural Information Processing Systems*, 33:2611–2624.

Jonathan Krause, Michael Stark, Jia Deng, and Li Fei-Fei. 2013. 3d object representations for fine-grained categorization. In *Proceedings of the IEEE international conference on computer vision workshops*, pages 554–561.

Ranjay Krishna, Yuke Zhu, Oliver Groth, Justin Johnson, Kenji Hata, Joshua Kravitz, Stephanie Chen, Yannis Kalantidis, Li-Jia Li, David A. Shamma, Michael S. Bernstein, and Li Fei-Fei. 2017. Visual genome: Connecting language and vision using crowdsourced dense image annotations. *IJCV*, 123(1):32–73.

Alex Krizhevsky, Geoffrey Hinton, et al. 2009. Learning multiple layers of features from tiny images.

Weyu Lan, Xirong Li, and Jianfeng Dong. 2017. Fluency-guided cross-lingual image captioning. *Proceedings of the 25th ACM international conference on Multimedia*.

Chenliang Li, Haiyang Xu, Junfeng Tian, Wei Wang, Ming Yan, Bin Bi, Jiabo Ye, Hehong Chen, Guohai Xu, Zheng Cao, et al. 2022a. mplug: Effective and efficient vision-language learning by cross-modal skip-connections. [arXiv preprint arXiv:2205.12005](#).

Chunyuan Li, Haotian Liu, Liunian Harold Li, Pengchuan Zhang, Jyoti Aneja, Jianwei Yang, Ping Jin, Yong Jae Lee, Houdong Hu, Zicheng Liu, et al. 2022b. Elevater: A benchmark and toolkit for evaluating language-augmented visual models. [arXiv preprint arXiv:2204.08790](#).

Gen Li, Nan Duan, Yuejian Fang, Daxin Jiang, and Ming Zhou. 2019a. Unicoder-vl: A universal encoder for vision and language by cross-modal pre-training. [CoRR](#), abs/1908.06066.

Junnan Li, Dongxu Li, Caiming Xiong, and Steven Hoi. 2022c. Blip: Bootstrapping language-image pre-training for unified vision-language understanding and generation. [arXiv preprint arXiv:2201.12086](#).

Junnan Li, Ramprasaath R. Selvaraju, Akhilesh Gotmare, Shafiq R. Joty, Caiming Xiong, and Steven Chu-Hong Hoi. 2021a. Align before fuse: Vision and language representation learning with momentum distillation. In *NeurIPS 2021*, pages 9694–9705.

Liunian Harold Li, Mark Yatskar, Da Yin, Cho-Jui Hsieh, and Kai-Wei Chang. 2019b. Visualbert: A simple and performant baseline for vision and language. [ArXiv](#), abs/1908.03557.

Xirong Li, Chaoxi Xu, Xiaoxu Wang, Weyu Lan, Zhengxiong Jia, Gang Yang, and Jieping Xu. 2019c. Coco-cn for cross-lingual image tagging, captioning, and retrieval. *IEEE Transactions on Multimedia*, 21:2347–2360.

Xiujun Li, Xi Yin, Chunyuan Li, Xiaowei Hu, Pengchuan Zhang, Lei Zhang, Lijuan Wang, Houdong Hu, Li Dong, Furu Wei, Yejin Choi, and Jianfeng Gao. 2020. Oscar: Object-semantics aligned pre-training for vision-language tasks. In *ECCV*.

Yangguang Li, Feng Liang, Lichen Zhao, Yufeng Cui, Wanli Ouyang, Jing Shao, Fengwei Yu, and Junjie Yan. 2021b. Supervision exists everywhere: A data efficient contrastive language-image pre-training paradigm. [arXiv preprint arXiv:2110.05208](#).

Junyang Lin, Rui Men, An Yang, Chang Zhou, Ming Ding, Yichang Zhang, Peng Wang, Ang Wang, Le Jiang, Xianyan Jia, Jie Zhang, Jianwei Zhang, Xu Zou, Zhikang Li, Xiaodong Deng, Jie Liu, Jinbao Xue, Huiling Zhou, Jianxin Ma, Jin Yu, Yong Li, Wei Lin, Jingren Zhou, Jie Tang, and Hongxia Yang. 2021a. M6: A chinese multimodal pretrainer. [CoRR](#), abs/2103.00823.

Junyang Lin, An Yang, Jinze Bai, Chang Zhou, Le Jiang, Xianyan Jia, Ang Wang, Jie Zhang, Yong Li, Wei Lin, Jingren Zhou, and Hongxia Yang. 2021b. M6-10T: A sharing-delinking paradigm for efficient multi-trillion parameter pretraining. [CoRR](#), abs/2110.03888.

Junyang Lin, An Yang, Yichang Zhang, Jie Liu, Jingren Zhou, and Hongxia Yang. 2020. Interbert: Vision-and-language interaction for multi-modal pretraining. [CoRR](#), abs/2003.13198.

Ze Liu, Han Hu, Yutong Lin, Zhuliang Yao, Zhenda Xie, Yixuan Wei, Jia Ning, Yue Cao, Zheng Zhang, Li Dong, et al. 2022. Swin transformer v2: Scaling up capacity and resolution. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 12009–12019.

Jiasen Lu, Dhruv Batra, Devi Parikh, and Stefan Lee. 2019. Vilbert: Pretraining task-agnostic visiolinguistic representations for vision-and-language tasks. In *NeurIPS 2019*, pages 13–23.

Subhransu Maji, Esa Rahtu, Juho Kannala, Matthew Blaschko, and Andrea Vedaldi. 2013. Fine-grained visual classification of aircraft. [arXiv preprint arXiv:1306.5151](#).Maria-Elena Nilsback and Andrew Zisserman. 2008. Automated flower classification over a large number of classes. In 2008 Sixth Indian Conference on Computer Vision, Graphics & Image Processing, pages 722–729. IEEE.

Omkar M. Parkhi, Andrea Vedaldi, Andrew Zisserman, and C. V. Jawahar. 2012. Cats and dogs. In 2012 IEEE Conference on Computer Vision and Pattern Recognition, pages 3498–3505. IEEE Computer Society.

Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, Gretchen Krueger, and Ilya Sutskever. 2021. Learning transferable visual models from natural language supervision. In ICML 2021, volume 139 of Proceedings of Machine Learning Research, pages 8748–8763. PMLR.

Colin Raffel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, and Peter J. Liu. 2020. Exploring the limits of transfer learning with a unified text-to-text transformer. *J. Mach. Learn. Res.*, 21:140:1–140:67.

Aditya Ramesh, Prafulla Dhariwal, Alex Nichol, Casey Chu, and Mark Chen. 2022. Hierarchical text-conditional image generation with clip latents. [arXiv preprint arXiv:2204.06125](https://arxiv.org/abs/2204.06125).

Aditya Ramesh, Mikhail Pavlov, Gabriel Goh, Scott Gray, Chelsea Voss, Alec Radford, Mark Chen, and Ilya Sutskever. 2021. Zero-shot text-to-image generation. In ICML 2021, volume 139 of Proceedings of Machine Learning Research, pages 8821–8831. PMLR.

Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, and Björn Ommer. 2022. High-resolution image synthesis with latent diffusion models. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 10684–10695.

Christoph Schuhmann, Richard Vencu, Romain Beaumont, Robert Kaczmarczyk, Clayton Mullis, Aarush Katta, Theo Coombes, Jenia Jitsev, and Aran Komatsuzaki. 2021. Laion-400m: Open dataset of clip-filtered 400 million image-text pairs. [arXiv preprint arXiv:2111.02114](https://arxiv.org/abs/2111.02114).

Sheng Shen, Liunian Harold Li, Hao Tan, Mohit Bansal, Anna Rohrbach, Kai-Wei Chang, Zhewei Yao, and Kurt Keutzer. 2021. How much can clip benefit vision-and-language tasks? [arXiv preprint arXiv:2107.06383](https://arxiv.org/abs/2107.06383).

Johannes Stallkamp, Marc Schlippsing, Jan Salmen, and Christian Igel. 2011. The german traffic sign recognition benchmark: A multi-class classification competition. In IJCNN 2011, pages 1453–1460. IEEE.

Bastiaan S Veeling, Jasper Linmans, Jim Winkens, Taco Cohen, and Max Welling. 2018. Rotation equivariant cnns for digital pathology. In International Conference on Medical image computing and computer-assisted intervention, pages 210–218. Springer.

Peng Wang, An Yang, Rui Men, Junyang Lin, Shuai Bai, Zhikang Li, Jianxin Ma, Chang Zhou, Jingren Zhou, and Hongxia Yang. 2022a. Unifying architectures, tasks, and modalities through a simple sequence-to-sequence learning framework. *CoRR*, abs/2202.03052.

Wenhui Wang, Hangbo Bao, Li Dong, Johan Bjorck, Zhiliang Peng, Qiang Liu, Kriti Aggarwal, Owais Khan Mohammed, Saksham Singhal, Subhojit Som, et al. 2022b. Image as a foreign language: Beit pretraining for all vision and vision-language tasks. [arXiv preprint arXiv:2208.10442](https://arxiv.org/abs/2208.10442).

Wenhui Wang, Hangbo Bao, Li Dong, and Furu Wei. 2021a. Vlmo: Unified vision-language pretraining with mixture-of-modality-experts. *CoRR*, abs/2111.02358.

Zirui Wang, Jiahui Yu, Adams Wei Yu, Zihang Dai, Yulia Tsvetkov, and Yuan Cao. 2021b. Simvlm: Simple visual language model pretraining with weak supervision. *CoRR*, abs/2108.10904.

Jason Wei, Yi Tay, Rishi Bommasani, Colin Raffel, Barret Zoph, Sebastian Borgeaud, Dani Yogatama, Maarten Bosma, Denny Zhou, Donald Metzler, et al. 2022. Emergent abilities of large language models. [arXiv preprint arXiv:2206.07682](https://arxiv.org/abs/2206.07682).

Chunyu Xie, Heng Cai, Jianfei Song, Jincheng Li, Fanjing Kong, Xiaoyu Wu, Henrique Morimitsu, Lin Yao, Dexin Wang, Dawei Leng, et al. 2022. Zero and r2d2: A large-scale chinese cross-modal benchmark and a vision-language framework. [arXiv preprint arXiv:2205.03860](https://arxiv.org/abs/2205.03860).

Haiyang Xu, Ming Yan, Chenliang Li, Bin Bi, Songfang Huang, Wenming Xiao, and Fei Huang. 2021. E2e-vlp: End-to-end vision-language pretraining enhanced by visual learning. [arXiv preprint arXiv:2106.01804](https://arxiv.org/abs/2106.01804).

An Yang, Junyang Lin, Rui Men, Chang Zhou, Le Jiang, Xianyan Jia, Ang Wang, Jie Zhang, Jiamang Wang, Yong Li, Di Zhang, Wei Lin, Lin Qu, Jingren Zhou, and Hongxia Yang. 2021. Exploring sparse expert models and beyond. *CoRR*, abs/2105.15082.

Lewei Yao, Runhui Huang, Lu Hou, Guansong Lu, Minzhe Niu, Hang Xu, Xiaodan Liang, Zhenguo Li, Xin Jiang, and Chunjing Xu. 2021. FILIP: fine-grained interactive language-image pre-training. *CoRR*, abs/2111.07783.

Lu Yuan, Dongdong Chen, Yi-Ling Chen, Noel Codella, Xiyang Dai, Jianfeng Gao, Houdong Hu, Xuedong Huang, Boxin Li, Chunyuan Li, Ce Liu, Mengchen Liu, Zicheng Liu, Yumao Lu, Yu Shi, Lijuan Wang,Jianfeng Wang, Bin Xiao, Zhen Xiao, Jianwei Yang, Michael Zeng, Luowei Zhou, and Pengchuan Zhang. 2021. Florence: A new foundation model for computer vision. [CoRR](#), abs/2111.11432.

Xiaohua Zhai, Xiao Wang, Basil Mustafa, Andreas Steiner, Daniel Keysers, Alexander Kolesnikov, and Lucas Beyer. 2022. Lit: Zero-shot transfer with locked-image text tuning. In [Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition](#), pages 18123–18133.

Pengchuan Zhang, Xiujun Li, Xiaowei Hu, Jianwei Yang, Lei Zhang, Lijuan Wang, Yejin Choi, and Jianfeng Gao. 2021. Vinvl: Revisiting visual representations in vision-language models. In [CVPR 2021](#), pages 5579–5588. Computer Vision Foundation / IEEE.

## A Appendix

### A.1 Model Architecture Details

We develop 5 Chinese CLIP models of different sizes, spanning from around 77 to 958 million parameters. We include 1 ResNet-50 model CN-CLIP<sub>RN50</sub> and 4 ViT models, i.e., CN-CLIP<sub>ViT-B/16</sub>, CN-CLIP<sub>ViT-L/14</sub>, CN-CLIP<sub>ViT-L/14@336px</sub> and CN-CLIP<sub>ViT-H/14</sub>, where models are pretrained on images of the resolution of  $224 \times 224$  without specification. Table 5 presents the details of the model architecture. The smallest model CN-CLIP<sub>RN50</sub> consists of a ResNet-50 for the image encoder and a RBT3 for the text encoder. The base-size model CN-CLIP<sub>ViT-B/16</sub> consists of a ViT-B/16@224px for the image encoder and a RoBERTa-wwm-Base for the text encoder. The large-size model CN-CLIP<sub>ViT-L/14</sub> consists of a ViT-L/14@224px for the image encoder and a RoBERTa-wwm-Base for the text encoder, while CN-CLIP<sub>ViT-L/14@336px</sub> consists of a ViT-L/14@336px and a RoBERTa-wwm-Base. Specifically, we pretrain CN-CLIP<sub>ViT-L/14@336px</sub> by continuing pretraining on the pretrained CN-CLIP<sub>ViT-L/14</sub>. For the adaptation to a larger resolution, we initialize the image positional embedding by applying interpolation to the positional embedding of CN-CLIP<sub>ViT-L/14</sub>, following [Ilharco et al. \(2021\)](#). The huge-size model CN-CLIP<sub>ViT-H/14</sub> consists of a ViT-H/14 for the image encoder and RoBERTa-wwm-Large for the text encoder. More implementation details are presented in Appendix A.

We provide more details of their model architectures in Table 6 and Table 7. We keep the architecture of ResNet-50, ViT-B/16, and ViT-L/14 backbones conformed with OpenAI CLIP and the architecture of ViT-H/14 same with LAION CLIP<sup>8</sup>. This enables us to initialize the Chinese CLIP image encoders with their weights. The text encoders are Chinese Roberta models ([Cui et al., 2020](#)). Specifically, our most lightweight tiny-size Chinese CLIP uses the architecture of the 3-layer RBT3 model. The base-size and large-size Chinese CLIP models use the 12-layer architecture of RoBERTa-wwm-Base. For the huge-size CN-CLIP, we use the 24-layer architecture of RoBERTa-wwm-Large. The vocabulary size of text tokenizer is 21,128.

<sup>8</sup><https://laion.ai/blog/large-openclip/><table border="1">
<thead>
<tr>
<th>Model</th>
<th>#Params (All)</th>
<th>Backbone (I)</th>
<th>#Params (I)</th>
<th>Backbone (T)</th>
<th>#Params (T)</th>
<th>Resolution</th>
</tr>
</thead>
<tbody>
<tr>
<td>CN-CLIP<sub>RN50</sub></td>
<td>77M</td>
<td>ResNet-50</td>
<td>38M</td>
<td>RBT3</td>
<td>39M</td>
<td>224 × 224</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-B/16</sub></td>
<td>188M</td>
<td>ViT-B/16</td>
<td>86M</td>
<td>RoBERTa-wwm-Base</td>
<td>102M</td>
<td>224 × 224</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14</sub></td>
<td>406M</td>
<td>ViT-L/14</td>
<td>304M</td>
<td>RoBERTa-wwm-Base</td>
<td>102M</td>
<td>224 × 224</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14@336px</sub></td>
<td>407M</td>
<td>ViT-L/14</td>
<td>304M</td>
<td>RoBERTa-wwm-Base</td>
<td>102M</td>
<td>336 × 336</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-H/14</sub></td>
<td>958M</td>
<td>ViT-H/14</td>
<td>632M</td>
<td>RoBERTa-wwm-Large</td>
<td>326M</td>
<td>224 × 224</td>
</tr>
</tbody>
</table>

Table 5: Hyperparameters of Chinese CLIP models of different sizes.

<table border="1">
<thead>
<tr>
<th rowspan="2">Model</th>
<th rowspan="2">Embedding dimension</th>
<th colspan="3">Vision Transformer</th>
<th colspan="3">Text Transformer</th>
</tr>
<tr>
<th>layers</th>
<th>width</th>
<th>heads</th>
<th>layers</th>
<th>width</th>
<th>heads</th>
</tr>
</thead>
<tbody>
<tr>
<td>CN-CLIP<sub>ViT-B/16</sub></td>
<td>512</td>
<td>12</td>
<td>768</td>
<td>12</td>
<td>12</td>
<td>768</td>
<td>12</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14</sub></td>
<td>768</td>
<td>24</td>
<td>1,024</td>
<td>16</td>
<td>12</td>
<td>768</td>
<td>12</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14@336px</sub></td>
<td>768</td>
<td>24</td>
<td>1,024</td>
<td>16</td>
<td>12</td>
<td>768</td>
<td>12</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-H/14</sub></td>
<td>1,024</td>
<td>32</td>
<td>1,280</td>
<td>16</td>
<td>24</td>
<td>1,024</td>
<td>24</td>
</tr>
</tbody>
</table>

Table 6: Detailed architecture hyperparameters of ViT-based CN-CLIP models.

## A.2 Pretraining Details

**Initialization** As mentioned in Section 2.2, we initialize the image encoders of CN-CLIP<sub>RN50</sub>, CN-CLIP<sub>ViT-B/16</sub> and CN-CLIP<sub>ViT-L/14</sub> using the OpenAI CLIP weights. The image encoder of CN-CLIP<sub>ViT-H/14</sub> is initialized with LAION CLIP. Besides the ResNet or ViT parameters, the temperature and visual output projection parameters are also initialized with the pretrained CLIP weights. For the text encoder, we initialize the parameters using the released Chinese Roberta weights of the corresponding model scale, with their pooler weights discarded. The text output projection weight is randomly initialized with normal distribution.

**Stage 1** The pretraining hyperparameters of Stage 1 are shown in Table 8, which are shared for CN-CLIP<sub>RN50</sub>, CN-CLIP<sub>ViT-B/16</sub>, CN-CLIP<sub>ViT-L/14</sub> and CN-CLIP<sub>ViT-H/14</sub>. The values of hyperparameters are generally similar to those in OpenAI CLIP (Radford et al., 2021). As to data augmentation, we use random resize cropping and AutoAugment (Cubuk et al., 2019) on input images. We leverage all-gather communications across GPU workers to compute contrastive loss on the global batch. The above 4 models are pretrained for around 20, 44, 64, and 26 epochs in this stage respectively, with the image encoder frozen. The running variance and mean of batch normalization layers are not updated in this stage for CN-CLIP<sub>RN50</sub>. The optimal epochs of pretraining are determined by measuring the mean-recall under the 3 downstream zero-shot retrieval tasks during training. Mixed-precision training is activated. In this stage, we pretrain 1.6 days using 64 NVIDIA V100 GPUs

for CN-CLIP<sub>RN50</sub>, 4.5 days using 128 NVIDIA V100 GPUs for CN-CLIP<sub>ViT-B/16</sub>, 11.5 days using 128 NVIDIA V100 GPUs for CN-CLIP<sub>ViT-L/14</sub> and 3.8 days using 184 NVIDIA A100 GPUs for CN-CLIP<sub>ViT-H/14</sub>.

**Stage 2** In Stage 2, we unfreeze the image encoder and update all the model parameters. Except for the peak learning rate, batch size and training epochs, all other hyperparameters mentioned in Stage 1 are kept unchanged. We decrease the learning rate to  $2e-5$  for subtler optimization. For CN-CLIP<sub>RN50</sub>, CN-CLIP<sub>ViT-B/16</sub> and CN-CLIP<sub>ViT-L/14</sub>, the batch size is shrunk to 16, 384, 16, 384 and 4, 608 respectively due to the limitation in GPU memory. When scaling to CN-CLIP<sub>ViT-H/14</sub>, we implement gradient checkpointing, which enables a larger batch size of 32, 768. These 4 models are pretrained for around 44, 15, 7 and 7 epochs in Stage 2, respectively. In this stage, we pretrain CN-CLIP<sub>RN50</sub> for 5.8 days using 64 NVIDIA V100 GPUs, CN-CLIP<sub>ViT-B/16</sub> for 3.0 days using 128 NVIDIA V100 GPUs, CN-CLIP<sub>ViT-L/14</sub> for 8.0 days using 128 Nvidia V100 GPUs, and CN-CLIP<sub>ViT-H/14</sub> for 2.2 days using 184 NVIDIA A100 GPUs.

To pretrain a model of a larger resolution, we implement interpolation to the image positional embedding of CN-CLIP<sub>ViT-L/14</sub> for adapting to a larger resolution and continue pretraining with images of the resolution of 336 × 336. We start from CN-CLIP<sub>ViT-L/14</sub> and continue pretraining by 2 epochs. The pretraining only costs the use of 128 NVIDIA A100 GPUs for 0.7 days.<table border="1">
<thead>
<tr>
<th>Model</th>
<th>Embedding dimension</th>
<th>ResNet blocks</th>
<th>width</th>
<th>Text Transformer layers</th>
<th>width</th>
<th>heads</th>
</tr>
</thead>
<tbody>
<tr>
<td>CN-CLIP<sub>RN50</sub></td>
<td>1,024</td>
<td>(3, 4, 6, 3)</td>
<td>2,048</td>
<td>3</td>
<td>768</td>
<td>12</td>
</tr>
</tbody>
</table>

Table 7: Detailed architecture hyperparameters of ResNet-based CN-CLIP<sub>RN50</sub>.

<table border="1">
<thead>
<tr>
<th>Hyperparameters</th>
<th>Value</th>
</tr>
</thead>
<tbody>
<tr>
<td>Batch size</td>
<td>32, 768</td>
</tr>
<tr>
<td>Maximum text length</td>
<td>50</td>
</tr>
<tr>
<td>Peak learning rate</td>
<td><math>1e - 4</math></td>
</tr>
<tr>
<td>Learning rate schedule</td>
<td>Cosine</td>
</tr>
<tr>
<td>Maximum temperature</td>
<td>100</td>
</tr>
<tr>
<td>Weight decay</td>
<td><math>1e - 3</math></td>
</tr>
<tr>
<td>Warmup iterations</td>
<td>5, 000</td>
</tr>
<tr>
<td>Adam <math>\beta_1</math></td>
<td>0.9</td>
</tr>
<tr>
<td>Adam <math>\beta_2</math></td>
<td>0.999 (ResNet), 0.98 (ViT)</td>
</tr>
<tr>
<td>Adam <math>\epsilon</math></td>
<td><math>1e - 8</math> (ResNet), <math>1e - 6</math> (ViT)</td>
</tr>
</tbody>
</table>

Table 8: Common pretraining hyperparameters in the first stage.

### A.3 Finetuning Details

As reported in Table 1, 2 and 3, we mainly finetune CN-CLIP on 3 cross-modal retrieval datasets: MUGE, Flickr30K-CN, and COCO-CN. Most finetuning experiments are conducted on 32 NVIDIA A100 GPUs. The finetuning strategy and loss are consistent with the pretraining process. For time efficiency and full utilization of computation resources, we set the batch size as large as possible. We implement gradient checkpointing in the finetuning process of CN-CLIP<sub>ViT-L/14@336px</sub> and CN-CLIP<sub>ViT-H/14</sub> for a larger batch size. Table 9 shows the specific settings of batch size, peaking learning rate, maximum epochs, and warmup iterations in the finetuning process. We set other hyperparameters to be the same as those in pretraining by default. We save the model parameters at the end of each epoch. For MUGE, we report the best results on the validation set. For Flickr30K-CN and COCO-CN, we choose the checkpoint with the best performance on the validation set and report the results on the test set.

### A.4 Cross-modal Retrieval with Longer Texts

The results reported in Section 3.1.2 demonstrate the excellent cross-modal retrieval capability of Chinese CLIP. Note that the average text lengths of MUGE, Flickr30K-CN, and COCO-CN are 7.4, 19.7, and 16.8, respectively. We also conduct finetuning experiments on the ICR (Xie et al., 2022) dataset with an average text length of 45.3. Experimental results are shown in Table 10. Since

the texts in the ICR dataset are longer, we set the maximum text length to 128 for finetuning. The results show that Chinese CLIP achieves state-of-the-art performance in cross-modal retrieval tasks with longer texts.

### A.5 Details About Experiments on Zero-shot Image Classification

We present the data statistics and metrics of the 20 image classification datasets of the track ICinW in the ELEVATER benchmark in Table 11. For the adaptation of Chinese CLIP to the English-native benchmark, we apply a series of preprocessing strategies. Specifically, we translate the text descriptions of the labels and the templates for manual prompts to Chinese. For example, the labels in CIFAR-10 include “car, dog, ...”, and we manually translate the words into Chinese. There are also particular cases, such as the labels in FGVC-Aircraft (Maji et al., 2013), which are difficult to translate or transliterate. We search the names on Google and figure out the best Chinese name for each label. Be that as it may, we cannot guarantee that we have the best Chinese translation, and more importantly, it is still hard for the Chinese pretrained model to understand some of the concepts, which may lead to unsatisfactory performance in the related downstream tasks. As to the templates, for some datasets, we use our translation of the templates provided by the ELEVATER toolkit,<sup>9</sup> and for the others, we use the translation of the templates from OpenAI CLIP.

We present the experimental results of all Chinese CLIP models on zero-shot image classification in Table 12. It can be found that the scaling of model size can consistently bring improvements in model performance. The predictable improvements of scaling Chinese CLIP indicate that we can further scale up the model for better performance in the future work. However, it is still a pity that the tiny-size CN-CLIP<sub>RN50</sub> saliently performs much worse than the ViT variants which are significantly larger. This shows that there is still much room

<sup>9</sup>[https://github.com/Computer-Vision-in-the-World/Elevater\\_Toolkit\\_IC](https://github.com/Computer-Vision-in-the-World/Elevater_Toolkit_IC)<table border="1">
<thead>
<tr>
<th rowspan="2">Model</th>
<th colspan="3">Batch size</th>
<th colspan="3">Peak learning rate</th>
<th colspan="3">Maximum epochs</th>
<th colspan="3">Warmup iterations</th>
</tr>
<tr>
<th>MUGE</th>
<th>Flickr</th>
<th>COCO</th>
<th>MUGE</th>
<th>Flickr</th>
<th>COCO</th>
<th>MUGE</th>
<th>Flickr</th>
<th>COCO</th>
<th>MUGE</th>
<th>Flickr</th>
<th>COCO</th>
</tr>
</thead>
<tbody>
<tr>
<td>CN-CLIP<sub>RN50</sub></td>
<td>24,576</td>
<td>24,576</td>
<td>24,576</td>
<td>5e-5</td>
<td>6e-5</td>
<td>5e-5</td>
<td>60</td>
<td>30</td>
<td>40</td>
<td>100</td>
<td>20</td>
<td>6</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-B/16</sub></td>
<td>12,800</td>
<td>7,680</td>
<td>12,800</td>
<td>2e-5</td>
<td>5e-5</td>
<td>5e-5</td>
<td>20</td>
<td>16</td>
<td>30</td>
<td>40</td>
<td>20</td>
<td>6</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14</sub></td>
<td>4,096</td>
<td>4,096</td>
<td>4,096</td>
<td>3e-5</td>
<td>2e-5</td>
<td>6e-5</td>
<td>20</td>
<td>16</td>
<td>18</td>
<td>100</td>
<td>60</td>
<td>9</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14@336px</sub></td>
<td>8,192</td>
<td>8,192</td>
<td>8,192</td>
<td>2e-5</td>
<td>2e-5</td>
<td>4e-5</td>
<td>20</td>
<td>18</td>
<td>18</td>
<td>100</td>
<td>20</td>
<td>2</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-H/14</sub></td>
<td>20,480</td>
<td>4,096</td>
<td>5,120</td>
<td>2e-5</td>
<td>6e-6</td>
<td>2e-5</td>
<td>20</td>
<td>18</td>
<td>18</td>
<td>20</td>
<td>6</td>
<td>10</td>
</tr>
</tbody>
</table>

Table 9: Detailed finetuning hyperparameters of CN-CLIP models.

<table border="1">
<thead>
<tr>
<th>Tasks</th>
<th colspan="3">Text-to-Image</th>
<th colspan="4">Image-to-Text</th>
</tr>
<tr>
<th>Metrics</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
<th>MR</th>
</tr>
</thead>
<tbody>
<tr>
<td>R2D2<sub>ViT-B</sub></td>
<td>42.2</td>
<td>69.4</td>
<td>77.8</td>
<td>43.4</td>
<td>69.8</td>
<td>78.4</td>
<td>63.5</td>
</tr>
<tr>
<td>R2D2<sub>ViT-L/14</sub></td>
<td>60.7</td>
<td>82.0</td>
<td>86.9</td>
<td>61.5</td>
<td>82.9</td>
<td>87.7</td>
<td>77.0</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-B/16</sub></td>
<td>55.4</td>
<td>79.0</td>
<td>85.2</td>
<td>56.6</td>
<td>79.5</td>
<td>85.6</td>
<td>73.5</td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14</sub></td>
<td><b>61.6</b></td>
<td><b>83.6</b></td>
<td><b>89.0</b></td>
<td><b>62.5</b></td>
<td><b>83.9</b></td>
<td><b>89.1</b></td>
<td><b>78.3</b></td>
</tr>
</tbody>
</table>

Table 10: Finetuning results on ICR dataset. We report the performance of baselines, CN-CLIP<sub>ViT-B/16</sub> and CN-CLIP<sub>ViT-L/14</sub> on text-to-image and image-to-text retrieval.

for the small model to improve, and the knowledge transfer of CLIP from large models to small models should be an important research topic in multimodal representation learning.

## A.6 Deployment

Chinese CLIP is supported to be deployed into ONNX-based<sup>10</sup> and TensorRT-based<sup>11</sup> models, enabling faster text and vision representation generation (especially for online inference). In this section, we provide more details on the model conversion, as well as the performance improvement.

Specifically, we employ the ONNX module in PyTorch with ONNXMLTOOLS<sup>12</sup> package to convert Chinese CLIP PyTorch models to ONNX-based models in FP16 precision. With the support of ONNXRUNTIME-GPU<sup>13</sup> package, the ONNX-based models are able to infer on NVIDIA GPUs. The TENSORRT package enables the TensorRT-based models obtained from ONNX-based models and provides the GPU inference runtime. Our TensorRT-based models are also in FP16 precision.

We benchmark the PyTorch implemented Chinese CLIP models with converted ONNX-based and TensorRT-based models using a server with a single NVIDIA T4 GPU. The server contains 16

Intel Xeon (Skylake) Platinum 8163 CPU cores with 64GB memory. For each model, we inference the vision and text representations for 100 batches and compute the average time. Simulating the scenario of online deployment, we use batch size of 1. All the models infer with FP16 precision. Table 13 shows the comparisons of inference time cost. For almost all the model scales, ONNX-based and TensorRT-based models have optimized inference speed over native PyTorch implemented Chinese CLIP models, especially on smaller model sizes. For vision representation inference, the TensorRT-based models are around 1.3 (CN-CLIP<sub>ViT-H/14</sub>) to 9.5 (CN-CLIP<sub>RN50</sub>) times as fast as the Pytorch-based models. For text representation inference, the TensorRT-based models are around 6.2 (CN-CLIP<sub>ViT-H/14</sub>) to 8.2 (CN-CLIP<sub>ViT-L/14</sub>) times as fast as the PyTorch counterparts.

We also evaluate the quality of ONNX-based and TensorRT-based model representations by measuring their zero-shot performance on MUGE retrieval dataset. Table 14 provides the experimental zero-shot results, which shows that the converted ONNX-based or TensorRT-based models keeps the quality of vision and text representations well, with no more than 0.1 MR degradation in retrieval performance.

<sup>10</sup><https://onnx.ai/>

<sup>11</sup><https://developer.nvidia.com/tensorrt>

<sup>12</sup><https://github.com/onnx/onnxmltools>

<sup>13</sup><https://onnxruntime.ai/docs/install><table border="1">
<thead>
<tr>
<th>Dataset</th>
<th>#Labels</th>
<th>Test Size</th>
<th>Metric</th>
</tr>
</thead>
<tbody>
<tr>
<td>Caltech-101 (Fei-Fei et al., 2004)</td>
<td>101</td>
<td>6,084</td>
<td>Mean-per-class</td>
</tr>
<tr>
<td>CIFAR-10 (Krizhevsky et al., 2009)</td>
<td>10</td>
<td>10,000</td>
<td>Accuracy</td>
</tr>
<tr>
<td>CIFAR-100 (Krizhevsky et al., 2009)</td>
<td>100</td>
<td>10,000</td>
<td>Accuracy</td>
</tr>
<tr>
<td>Country-211 (Radford et al., 2021)</td>
<td>211</td>
<td>21,100</td>
<td>Accuracy</td>
</tr>
<tr>
<td>DTD (Cimpoi et al., 2014)</td>
<td>47</td>
<td>1,880</td>
<td>Accuracy</td>
</tr>
<tr>
<td>EuroSAT (Helber et al., 2019)</td>
<td>10</td>
<td>5,000</td>
<td>Accuracy</td>
</tr>
<tr>
<td>FER-2013 (Radford et al., 2021)</td>
<td>7</td>
<td>3,589</td>
<td>Accuracy</td>
</tr>
<tr>
<td>FGVC-Aircraft (Maji et al., 2013)</td>
<td>100</td>
<td>3,333</td>
<td>Mean-per-class</td>
</tr>
<tr>
<td>Food-101 (Bossard et al., 2014)</td>
<td>101</td>
<td>25,250</td>
<td>Accuracy</td>
</tr>
<tr>
<td>GTSRB (Stallkamp et al., 2011)</td>
<td>43</td>
<td>12,630</td>
<td>Accuracy</td>
</tr>
<tr>
<td>Hateful-Memes (Kiela et al., 2020)</td>
<td>2</td>
<td>500</td>
<td>ROC AUC</td>
</tr>
<tr>
<td>KITTI-Distance (Fritsch et al., 2013)</td>
<td>4</td>
<td>711</td>
<td>Accuracy</td>
</tr>
<tr>
<td>MNIST (Deng, 2012)</td>
<td>10</td>
<td>10,000</td>
<td>Accuracy</td>
</tr>
<tr>
<td>Oxford Flowers-102 (Nilsback and Zisserman, 2008)</td>
<td>102</td>
<td>6,149</td>
<td>Mean-per-class</td>
</tr>
<tr>
<td>Oxford-IIIT Pets (Parkhi et al., 2012)</td>
<td>37</td>
<td>3,669</td>
<td>Mean-per-class</td>
</tr>
<tr>
<td>PatchCamelyon (Veeling et al., 2018)</td>
<td>2</td>
<td>32,768</td>
<td>Accuracy</td>
</tr>
<tr>
<td>Rendered-SST2 (Radford et al., 2021)</td>
<td>2</td>
<td>1,821</td>
<td>Accuracy</td>
</tr>
<tr>
<td>RESISC-45 (Cheng et al., 2017)</td>
<td>45</td>
<td>25,200</td>
<td>Accuracy</td>
</tr>
<tr>
<td>Stanford-Cars (Krause et al., 2013)</td>
<td>196</td>
<td>8,041</td>
<td>Accuracy</td>
</tr>
<tr>
<td>Pascal VOC-2007 (Everingham et al., 2010)</td>
<td>20</td>
<td>4,952</td>
<td>11-point mAP</td>
</tr>
</tbody>
</table>

Table 11: Details of the image classification datasets in the ELEVATER benchmark.

<table border="1">
<thead>
<tr>
<th rowspan="2">Dataset</th>
<th>CN-CLIP</th>
<th>CN-CLIP</th>
<th>CN-CLIP</th>
<th>CN-CLIP</th>
<th>CN-CLIP</th>
</tr>
<tr>
<th>RN50</th>
<th>ViT-B/16</th>
<th>ViT-L/14</th>
<th>ViT-L/14@336px</th>
<th>ViT-H/14</th>
</tr>
</thead>
<tbody>
<tr>
<td>Caltech-101</td>
<td>77.3</td>
<td>84.9</td>
<td>88.5</td>
<td>88.8</td>
<td>90.6</td>
</tr>
<tr>
<td>CIFAR-10</td>
<td>72.7</td>
<td>92.0</td>
<td>94.9</td>
<td>94.1</td>
<td>96.0</td>
</tr>
<tr>
<td>CIFAR-100</td>
<td>40.6</td>
<td>64.4</td>
<td>75.1</td>
<td>73.5</td>
<td>79.7</td>
</tr>
<tr>
<td>Country-211</td>
<td>7.7</td>
<td>15.2</td>
<td>21.0</td>
<td>25.4</td>
<td>25.3</td>
</tr>
<tr>
<td>DTD</td>
<td>36.9</td>
<td>43.6</td>
<td>44.2</td>
<td>43.8</td>
<td>51.2</td>
</tr>
<tr>
<td>EuroSAT</td>
<td>27.0</td>
<td>46.9</td>
<td>56.9</td>
<td>50.7</td>
<td>52.0</td>
</tr>
<tr>
<td>FER-2013</td>
<td>21.9</td>
<td>47.2</td>
<td>54.6</td>
<td>55.1</td>
<td>49.2</td>
</tr>
<tr>
<td>FGVC-Aircraft</td>
<td>5.4</td>
<td>12.8</td>
<td>16.0</td>
<td>17.1</td>
<td>26.2</td>
</tr>
<tr>
<td>Food-101</td>
<td>39.8</td>
<td>62.4</td>
<td>69.4</td>
<td>73.9</td>
<td>74.6</td>
</tr>
<tr>
<td>GTSRB</td>
<td>22.3</td>
<td>28.4</td>
<td>37.3</td>
<td>35.5</td>
<td>38.5</td>
</tr>
<tr>
<td>Hateful-Memes</td>
<td>50.3</td>
<td>56.2</td>
<td>53.4</td>
<td>52.8</td>
<td>54.7</td>
</tr>
<tr>
<td>KITTI-Distance</td>
<td>30.2</td>
<td>33.5</td>
<td>49.9</td>
<td>49.8</td>
<td>39.1</td>
</tr>
<tr>
<td>MNIST</td>
<td>50.2</td>
<td>67.6</td>
<td>69.8</td>
<td>65.0</td>
<td>79.4</td>
</tr>
<tr>
<td>Oxford Flowers-102</td>
<td>30.7</td>
<td>52.2</td>
<td>62.5</td>
<td>64.8</td>
<td>68.4</td>
</tr>
<tr>
<td>Oxford-IIIT Pets</td>
<td>48.7</td>
<td>73.0</td>
<td>81.6</td>
<td>83.1</td>
<td>83.5</td>
</tr>
<tr>
<td>PatchCamelyon</td>
<td>47.7</td>
<td>54.0</td>
<td>63.5</td>
<td>62.9</td>
<td>52.4</td>
</tr>
<tr>
<td>Rendered-SST2</td>
<td>50.1</td>
<td>52.3</td>
<td>61.4</td>
<td>62.9</td>
<td>61.0</td>
</tr>
<tr>
<td>RESISC-45</td>
<td>49.3</td>
<td>58.7</td>
<td>65.2</td>
<td>65.8</td>
<td>66.9</td>
</tr>
<tr>
<td>Stanford-Cars</td>
<td>27.3</td>
<td>42.3</td>
<td>49.8</td>
<td>54.1</td>
<td>71.8</td>
</tr>
<tr>
<td>VOC-2007</td>
<td>82.1</td>
<td>83.3</td>
<td>84.5</td>
<td>84.9</td>
<td>84.9</td>
</tr>
<tr>
<td>Average</td>
<td>40.9</td>
<td>53.5</td>
<td>60.0</td>
<td>60.2</td>
<td>62.3</td>
</tr>
</tbody>
</table>

Table 12: Experimental results of the zero-shot image classification performance of models on ICinW.

<table border="1">
<thead>
<tr>
<th>Inference Time per Sample (ms)</th>
<th colspan="3">Vision Representation</th>
<th colspan="3">Text Representation</th>
</tr>
<tr>
<th>Model Scale</th>
<th>PyTorch</th>
<th>ONNX</th>
<th>TensorRT</th>
<th>PyTorch</th>
<th>ONNX</th>
<th>TensorRT</th>
</tr>
</thead>
<tbody>
<tr>
<td>CN-CLIP<sub>RN50</sub></td>
<td>12.93</td>
<td>5.04</td>
<td><b>1.36</b></td>
<td>3.64</td>
<td>0.95</td>
<td><b>0.58</b></td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-B/16</sub></td>
<td>11.12</td>
<td>4.92</td>
<td><b>3.58</b></td>
<td>12.47</td>
<td>3.42</td>
<td><b>1.54</b></td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14</sub></td>
<td>21.19</td>
<td>17.10</td>
<td><b>13.08</b></td>
<td>12.45</td>
<td>3.48</td>
<td><b>1.52</b></td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-L/14@336px</sub></td>
<td>47.11</td>
<td>48.40</td>
<td><b>31.59</b></td>
<td>12.24</td>
<td>3.25</td>
<td><b>1.54</b></td>
</tr>
<tr>
<td>CN-CLIP<sub>ViT-H/14</sub></td>
<td>35.10</td>
<td>34.00</td>
<td><b>26.98</b></td>
<td>23.98</td>
<td>6.01</td>
<td><b>3.89</b></td>
</tr>
</tbody>
</table>

Table 13: Inference speed comparisons among PyTorch, ONNX and TensorRT Chinese CLIP models.<table border="1">
<thead>
<tr>
<th rowspan="2">Model Scale</th>
<th rowspan="2">Framework</th>
<th colspan="4">Zero-shot Performance</th>
</tr>
<tr>
<th>R@1</th>
<th>R@5</th>
<th>R@10</th>
<th>MR</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="3">CN-CLIP<sub>RN50</sub></td>
<td>PyTorch</td>
<td>42.6</td>
<td>68.6</td>
<td>77.9</td>
<td>63.0</td>
</tr>
<tr>
<td>ONNX</td>
<td>43.0</td>
<td>68.4</td>
<td>78.1</td>
<td>63.2</td>
</tr>
<tr>
<td>TensorRT</td>
<td>42.8</td>
<td>68.5</td>
<td>78.0</td>
<td>63.1</td>
</tr>
<tr>
<td rowspan="3">CN-CLIP<sub>ViT-B/16</sub></td>
<td>PyTorch</td>
<td>52.1</td>
<td>76.7</td>
<td>84.4</td>
<td>71.1</td>
</tr>
<tr>
<td>ONNX</td>
<td>52.0</td>
<td>76.8</td>
<td>84.3</td>
<td>71.1</td>
</tr>
<tr>
<td>TensorRT</td>
<td>52.0</td>
<td>76.8</td>
<td>84.2</td>
<td>71.0</td>
</tr>
<tr>
<td rowspan="3">CN-CLIP<sub>ViT-L/14</sub></td>
<td>PyTorch</td>
<td>56.3</td>
<td>79.8</td>
<td>86.2</td>
<td>74.1</td>
</tr>
<tr>
<td>ONNX</td>
<td>56.4</td>
<td>80.0</td>
<td>86.3</td>
<td>74.2</td>
</tr>
<tr>
<td>TensorRT</td>
<td>56.3</td>
<td>79.9</td>
<td>86.5</td>
<td>74.2</td>
</tr>
<tr>
<td rowspan="3">CN-CLIP<sub>ViT-L/14@336px</sub></td>
<td>PyTorch</td>
<td>59.0</td>
<td>81.4</td>
<td>87.8</td>
<td>76.1</td>
</tr>
<tr>
<td>ONNX</td>
<td>59.2</td>
<td>81.4</td>
<td>87.6</td>
<td>76.1</td>
</tr>
<tr>
<td>TensorRT</td>
<td>59.2</td>
<td>81.7</td>
<td>87.5</td>
<td>76.1</td>
</tr>
<tr>
<td rowspan="3">CN-CLIP<sub>ViT-H/14</sub></td>
<td>PyTorch</td>
<td>63.0</td>
<td>84.1</td>
<td>89.2</td>
<td>78.8</td>
</tr>
<tr>
<td>ONNX</td>
<td>63.1</td>
<td>84.1</td>
<td>89.0</td>
<td>78.8</td>
</tr>
<tr>
<td>TensorRT</td>
<td>63.1</td>
<td>84.2</td>
<td>89.1</td>
<td>78.8</td>
</tr>
</tbody>
</table>

Table 14: Zero-shot results on MUGE-Retrieval dataset among PyTorch, ONNX and TensorRT Chinese CLIP models.

Figure 4: Retrieval results of the query “a cat with glasses” in Chinese.Figure 5: Retrieval results of the query “Spring Festival couplet” in Chinese.


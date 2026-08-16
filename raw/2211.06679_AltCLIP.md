# AltCLIP: Altering the Language Encoder in CLIP for Extended Language Capabilities

Zhongzhi Chen <sup>\*1,2†</sup>, Guang Liu <sup>\*1</sup>, Bo-Wen Zhang<sup>1</sup>, Fulong Ye<sup>1,3†</sup> †  
Qinghong Yang<sup>2</sup>, Ledell Wu<sup>1</sup>

<sup>1</sup> Beijing Academy of Artificial Intelligence, <sup>2</sup> Beihang University,

<sup>3</sup> Beijing University of Posts and Telecommunications.

{liuguang, wuyu}@baai.ac.cn

## Abstract

In this work, we present a conceptually simple and effective method to train a strong bilingual/multilingual multimodal representation model. Starting from the pre-trained multimodal representation model CLIP released by OpenAI, we altered its text encoder with a pre-trained multilingual text encoder XLM-R, and aligned both languages and image representations by a two-stage training schema consisting of teacher learning and contrastive learning. We validate our method through evaluations of a wide range of tasks. We set new state-of-the-art performances on a bunch of tasks including ImageNet-CN, Flickr30k-CN, COCO-CN and XTD. Further, we obtain very close performances with CLIP on almost all tasks, suggesting that one can simply alter the text encoder in CLIP for extended capabilities such as multilingual understanding. Our models and code are available at <https://github.com/FlagAI-Open/FlagAI>.

## 1 Introduction

Learning a good representation in a joint space for vision and language has been a long pursuit in the research of Artificial Intelligence (AI). Recently, the milestone work of CLIP (Radford et al., 2021) from OpenAI demonstrated impressive zero-shot performances across a number of tasks such as image classification on ImageNet (Deng et al., 2009), Image-to-Text and Text-to-Image retrieval on Flickr-30k (Young et al., 2014) and MSCOCO (Lin et al., 2014; Chen et al., 2015). There has been the pursuit of building contrastive language-image models in other languages such as Italian (Bianchi et al., 2021), Korean (Ko and Gu, 2022), Chinese (Changpinyo et al., 2021; Fei et al., 2021; Wang et al., 2022; Gu et al., 2022;

Xie et al., 2022; Yang et al., 2022) or in a cross-lingual and multilingual setting (Aggarwal and Kale, 2020a; Carlsson et al., 2022).

Training a good language-image representation model often requires a huge amount of text-image pairs and vast computational resources. For instance, CLIP used 400M text-image pairs, and Taiyi (Wang et al., 2022), a recently proposed Chinese model, used 123M text-image pairs. To alleviate this problem, there are multiple works that try to utilize existing pretrained models and only pretrain part of the network (Portaz et al., 2019; Aggarwal and Kale, 2020a; Gu et al., 2022; Zhai et al., 2022). More recently, Carlsson et al. (2022) proposed to use Teacher Learning (a.k.a. Knowledge Distillation) on the text encoder of the CLIP model to learn a multilingual text-image representation model. This method only uses machine-translated data from English to a target language, without text-to-image pairs.

However, existing works in the cross-lingual or multilingual setting mainly focus on the model’s retrieval performance and ignores their generalization ability. The data set to evaluate retrieval performance is often small, e.g., 1,000 images in test sets for Flickr-30k. The retrieval performance fluctuates acutely with the change in training data distribution. Although current methods achieve good performance in retrieval, these methods often do not perform well on the ImageNet classification tasks. The ability to accurately predict images over 1,000 classes often indicates better generalization ability of the model.

To address the aforementioned problems, we propose a bilingual model named Alter ego CLIP (AltCLIP) which achieved strong performances on ImageNet and multimodal retrieval tasks in both English and Chinese. Our AltCLIP learns a strong bilingual language-image representation under a two-stage framework (see Figure 1 for

\*Equal Contribution

†Work done during internship with Beijing Academy of Artificial IntelligenceFigure 1: The framework of our method.

an overview). In the first stage, we use Teacher Learning to distill the knowledge learned from CLIP. In the second stage, we train the model via Contrastive Learning (Hadsell et al., 2006) on a relatively small amount of Chinese and English text-image pairs. We show the effectiveness of our method by experimenting with a wide range of benchmarks in English and Chinese. Further, We set new state-of-the-art results on multiple image classification and retrieval tasks in Chinese. We further extended this method to train a multilingual multimodal model where we call it AltCLIP<sub>M9</sub>. The AltCLIP<sub>M9</sub> model achieves state-of-the-art zero-shot results on the multilingual text-image retrieval dataset XTD (Aggarwal and Kale, 2020b).

## 2 Related Work

CLIP (Radford et al., 2021) provides a strong English text-image representation. To expand the language of CLIP model, there are prior studies on learning a bilingual text-image representation (Ko and Gu, 2022; Bianchi et al., 2021), and multilingual text-image representation (Aggarwal and Kale, 2020a; Carlsson et al., 2022). In the domain of Chinese text-image pretraining models, prior work such as Taiyi (Wang et al., 2022), CNCLIP (Yang et al., 2022), Wukong (Gu et al., 2022), R2D2 (Xie et al., 2022) and BriVL (Huo et al., 2021; Fei et al., 2021). These methods often need large-scale Chinese text-image pairs and suffer from a significant performance decline in English tasks.

Carlsson et al. (2022) proposed a way to utilize Teacher Learning (a.k.a. Knowledge Distillation) (Hinton et al., 2015) to train a new textual encoder from the original CLIP model with only machine-translated parallel data, without using text-image

pairs. Although this method achieves promising cross-lingual retrieval performances with only text data, its zero-shot classification performance in English drops significantly. We follow their work to learn a bilingual model from CLIP with a new text encoder, with the following changes: firstly, we use knowledge distillation on English text pairs in addition to machine-translated text pairs; secondly, we add human-curated translation data for better quality; lastly, we fine-tune the model with text-image pairs to further boost its performance.

XLM-R (Conneau et al., 2020) is a multilingual language model that achieves strong performances on a wide range of cross-lingual tasks. In our work, we use the XLM-R model as the underlying text encoder and align it with the image encoder trained in CLIP, to achieve competitive performances on cross-lingual and cross-modality tasks.

## 3 Methodology

We propose a two-stage method to learn a good bilingual and multilingual language-image representation model. In the first stage, we follow the work of Carlsson et al. (2022) to use Teacher Learning to learn a multilingual text encoder from the CLIP text encoder. In this step, no image is needed in training and only language parallel data is used. In the second stage, we use text-image pairs to further fine-tune the model from contrastive learning. Our overall training procedure is summarized in Figure 1.

### 3.1 Teacher Learning Stage

In this stage, we perform Teacher Learning (Hinton et al., 2015) on text encoders. We use the text encoder from CLIP (Radford et al., 2021) as the teacher text encoder, and the XLM-R (Con-<table border="1">
<thead>
<tr>
<th rowspan="2">Language</th>
<th rowspan="2">Method</th>
<th colspan="5">Dataset</th>
</tr>
<tr>
<th>ImageNet</th>
<th>ImageNet Sketch</th>
<th>ImageNet-A</th>
<th>ImageNet-R</th>
<th>ImageNetV2</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="5">English</td>
<td>CLIP</td>
<td><b>75.5</b></td>
<td><b>59.6</b></td>
<td><b>70.6</b></td>
<td><b>87.9</b></td>
<td><b>69.9</b></td>
</tr>
<tr>
<td>M-CLIP</td>
<td>52.3</td>
<td>44.2</td>
<td>59.1</td>
<td>81.7</td>
<td>47.3</td>
</tr>
<tr>
<td>CN-CLIP</td>
<td>32.5</td>
<td>30.7</td>
<td>29.8</td>
<td>57.0</td>
<td>28.6</td>
</tr>
<tr>
<td>AltCLIP<sub>T</sub></td>
<td>74.7</td>
<td>59.2</td>
<td>70.4</td>
<td>87.9</td>
<td>68.8</td>
</tr>
<tr>
<td>AltCLIP</td>
<td>74.5</td>
<td>58.7</td>
<td>69.5</td>
<td>87.2</td>
<td>68.2</td>
</tr>
<tr>
<td rowspan="5">Chinese</td>
<td>CLIP</td>
<td>1.9</td>
<td>1.7</td>
<td>4.7</td>
<td>4.4</td>
<td>1.8</td>
</tr>
<tr>
<td>M-CLIP</td>
<td>43.0</td>
<td>36.3</td>
<td>51.3</td>
<td>68.3</td>
<td>39.5</td>
</tr>
<tr>
<td>CN-CLIP</td>
<td>53.6</td>
<td>47.5</td>
<td>42.8</td>
<td>78.1</td>
<td>47.8</td>
</tr>
<tr>
<td>AltCLIP<sub>T</sub></td>
<td>58.2</td>
<td>46.9</td>
<td><b>62.7</b></td>
<td>82.1</td>
<td>53.3</td>
</tr>
<tr>
<td>AltCLIP</td>
<td><b>59.6</b></td>
<td><b>48.4</b></td>
<td>61.5</td>
<td><b>82.5</b></td>
<td><b>54.0</b></td>
</tr>
</tbody>
</table>

Table 1: Comparison Results of our proposed model and baseline models on image classification benchmarks, i.e. ImageNet and its variants. AltCLIP<sub>T</sub> and AltCLIP denotes our model after Teacher Learning Stage and after Contrastive Learning Stage, respectively. All image encoders used in these models are Vit-L for fair comparison. The metric reported is zero-shot classification accuracy.

neau et al., 2020) model pretrained on multilingual data as the student encoder. A fully-connected layer is added to transform the output of the XLM-R model into the same output dimension as the teacher encoder. We use parallel text data in both English and Chinese to distill the knowledge of text-image alignment.

Given parallel text input ( $sent_1, sent_2$ ), the teacher text encoder generates the learning target from input  $sent_1$ , which is the embedding of the [TOS] token, denoted by  $x_{tos}^t$ . The student text encoder generates embedding  $x_{cls}^s$  from input  $sent_2$ . We minimize Mean Squared Error (MSE) between  $x_{tos}^t$  and  $x_{cls}^s$ . After such training, the student text encoder can keep most of its multilingual capability and obtain text-image alignment capability in both languages. Note that the teacher encoder is only used at training time. At inference time, only the student encoder is used as the text encoder.

To show that our method is extensible at including more languages, we build a multilingual version that supports nine different languages: English(En), Chinese(Zh), Spanish(Es), French(Fr), Russian(Ru), Arabic(Ar), Japanese(Ja), Korean(Ko), and Italian(It). For the multilingual version, we align more languages with English, with the same concept and architecture as in the bilingual version.

### 3.2 Contrastive Learning Stage

This stage of training aims to further improve text-image alignment by contrastive learning on multilingual text-image pairs. As illustrated in Figure 1, here we use the image encoder from CLIP which is based on Vision Transformer (ViT) (Dosovitskiy et al., 2020) as our image encoder, and use

the student text encoder learned from the Teacher Learning Stage as our text encoder.

We use Contrastive Loss (Hadsell et al., 2006) between the output projection of the image encoder and text encoder, as done similarly in previous work (Radford et al., 2021). We follow LiT (Zhai et al., 2022) to freeze the image encoder at training time and only update the parameters in the text encoder. We observe that this stage of training further improves the model’s performance on various evaluation benchmarks, as presented in Section 5.

## 4 Model Training

### 4.1 Training Datasets

In this section, we describe the training datasets used in our two-stage model training.

**Teacher Learning Stage** In this stage, we use parallel text corpus to align the original CLIP text encoder and our new text encoder initialized from XLM-R. Our parallel text corpus includes the following:

1. 1. Machine translated data of text in Conceptual Captions (CC3M) (Sharma et al., 2018) and a 28M randomly sampled subset from Laion-400M (Schuhmann et al., 2021). For the multilingual model, we use the same setting but fewer 10M subsets from Laion-400M for each language.
2. 2. Human translated data of text from TSL2019 (Xu, 2019), a total number of 5M English to Chinese translations. For the multilingual model, we extracted the same amount for each language. Parallel data in different languages is extracted from the public databaseOPUS(Tiedemann, 2012)<sup>1</sup>. This type of parallel data provides more accurate translation.

**Contrastive Learning Stage** We use high-quality text-image pair data in this stage. Note that multilingual data are only used in our multilingual version. We use 2M bilingual text-image pairs for AltCLIP and 100M multilingual text-image pairs for the multilingual version, from the following:

1. 1. Chinese text-image dataset from Wudao MM (Yuan et al., 2021), filtered by the Laion Aesthetic v2<sup>2</sup> model with a threshold score over 5.5.
2. 2. English text-image dataset from LAION 5B (Schuhmann et al., 2022), a randomly sampled subset from the data filtered by the Laion Aesthetic v2 model with a threshold score over 6.
3. 3. Multilingual text-image dataset from LAION Multilingual 2B (Schuhmann et al., 2022), a randomly sampled subset from the data.

## 4.2 Implementation details

We initialize our text encoder from XLM-R<sub>Large</sub>. We use the text encoder from CLIP<sub>ViT-L14</sub> as the teacher text encoder, and the image encoder of the same CLIP model as our image encoder. For specific hyper-parameter settings in our two-stage training, please refer to the table 6 in Appendix.

## 5 Experiments

We present our experimental results in this section. In Section 5.1, we introduce the datasets and metrics used in the evaluation. We comprehensively validate our model through zero-shot benchmarks in both English and Chinese in Section 5.2. In Section 5.3, we conduct an ablation study on the effects of various design choices in Teacher Learning and Contrastive Learning. Finally, in Section 5.4, we use an AltCLIP-guided diffusion model to generate images from both Chinese and English prompts, and show that our model is capable to align text in different languages.

### 5.1 Evaluation Datasets and Metrics

In this section, we describe the datasets and metrics we used in our experiments. We use ImageNet (Deng et al., 2009) and its four out-of-distribution test variants, i.e. ImageNet Sketch (Wang et al., 2019), ImageNet-A (Hendrycks et al., 2021b), ImageNet-R (Hendrycks et al., 2021a), ImageNetV2 (Recht et al., 2019), to evaluate zero-shot image classification performances in English and Chinese.<sup>3</sup> During evaluation, we adapt the templates of manual prompts from CLIP for English and corresponding machine translation templates for Chinese. For cross-modal retrieval, we select Flickr30k (Young et al., 2014), MSCOCO (Lin et al., 2014), as well as their corresponding Chinese datasets, Flickr30k<sub>CN</sub> (Lan et al., 2017), MSCOCO<sub>CN</sub><sup>4</sup> (Li et al., 2019), to evaluate zero-shot image-to-text retrieval and text-to-image retrieval performances.

We further validate our model on a wide range of tasks to compare the performance with the original CLIP model. We collect the datasets introduced in CLIP and the Open CLIP benchmark<sup>5</sup>, including Birdsnap (Berg et al., 2014), Caltech-101 (Fei-Fei et al., 2006), Stanford Cars (Krause et al., 2013), CIFAR-10 (Krizhevsky et al., 2009), CIFAR-100 (Krizhevsky et al., 2009), Country211 (Radford et al., 2021), DTD (Cimpoi et al., 2014), EuroSAT (Helber et al., 2019), Facial Emotion Recognition 2013 (Goodfellow et al., 2013), FGVC Aircraft (Blaschko et al., 2012), Oxford Flowers 102 (Nilsback and Zisserman, 2008), Food-101 (Bossard et al., 2014), GTSRB (Stallkamp et al., 2011), Kinetics400 (Kay et al., 2017), Kinetics600 (Carreira et al., 2018), MNIST (Cireşan et al., 2011), PatchCamelyon (Veeling et al., 2018), ObjectNet (Barbu et al., 2019), Oxford-IIIT Pets (Parkhi et al., 2012), Rendered SST2 (Radford et al., 2021), RESISC45 (Cheng et al., 2017), STL-10 (Coates et al., 2011), SUN397 (Xiao et al., 2010), UCF101 (Soomro et al., 2012), Pascal VOC 2007 Classification (Everingham, 2007), Pascal VOC 2007 Multilabel Classification (Everingham, 2007). Finally, we evaluate our mul-

<sup>3</sup>We use the Chinese translation of classnames from [https://github.com/ningbonb/imagenet\\_classes\\_chinese](https://github.com/ningbonb/imagenet_classes_chinese)

<sup>4</sup>two versions, texts in 1k version are manual written captions while in 5k version are manual translated captions

<sup>5</sup>[https://github.com/LAION-AI/CLIP\\_benchmark](https://github.com/LAION-AI/CLIP_benchmark)

<sup>1</sup><https://opus.nlpl.eu>

<sup>2</sup><https://github.com/christophschuhmann/improved-aesthetic-predictor><table border="1">
<thead>
<tr>
<th rowspan="2">Dataset</th>
<th rowspan="2">Method</th>
<th colspan="3">Text-to-Image Retrieval</th>
<th colspan="3">Image-to-Text Retrieval</th>
<th rowspan="2">MR</th>
</tr>
<tr>
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
<td rowspan="7">Flickr30k<sub>EN</sub></td>
<td>CLIP</td>
<td>65.0</td>
<td>87.1</td>
<td>92.2</td>
<td>85.1</td>
<td>97.3</td>
<td><b>99.2</b></td>
<td>87.6</td>
</tr>
<tr>
<td>Taiyi</td>
<td>25.3</td>
<td>48.2</td>
<td>59.2</td>
<td>39.3</td>
<td>68.1</td>
<td>79.6</td>
<td>53.3</td>
</tr>
<tr>
<td>Wukong</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>R2D2</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>CN-CLIP</td>
<td>49.5</td>
<td>76.9</td>
<td>83.8</td>
<td>66.5</td>
<td>91.2</td>
<td>96.0</td>
<td>77.3</td>
</tr>
<tr>
<td>AltCLIP<sub>T</sub></td>
<td>66.3</td>
<td>87.8</td>
<td><b>92.7</b></td>
<td>85.9</td>
<td>97.7</td>
<td>99.1</td>
<td>88.3</td>
</tr>
<tr>
<td>AltCLIP</td>
<td><b>72.5</b></td>
<td><b>91.6</b></td>
<td><b>95.4</b></td>
<td><b>86.0</b></td>
<td><b>98.0</b></td>
<td>99.1</td>
<td><b>90.4</b></td>
</tr>
<tr>
<td rowspan="7">Flickr30k<sub>CN</sub></td>
<td>CLIP</td>
<td>0</td>
<td>2.4</td>
<td>4.0</td>
<td>2.3</td>
<td>8.1</td>
<td>12.6</td>
<td>5.0</td>
</tr>
<tr>
<td>Taiyi</td>
<td>53.7</td>
<td>79.8</td>
<td>86.6</td>
<td>63.8</td>
<td>90.5</td>
<td>95.9</td>
<td>78.4</td>
</tr>
<tr>
<td>Wukong<sup>†</sup></td>
<td>51.7</td>
<td>78.9</td>
<td>86.3</td>
<td>76.1</td>
<td>94.8</td>
<td>97.5</td>
<td>80.9</td>
</tr>
<tr>
<td>R2D2<sup>†</sup></td>
<td>60.9</td>
<td>86.8</td>
<td>92.7</td>
<td>77.6</td>
<td>96.7</td>
<td><b>98.9</b></td>
<td>85.6</td>
</tr>
<tr>
<td>CN-CLIP</td>
<td>68</td>
<td>89.7</td>
<td>94.4</td>
<td>80.2</td>
<td>96.6</td>
<td>98.2</td>
<td>87.9</td>
</tr>
<tr>
<td>AltCLIP<sub>T</sub></td>
<td>63.7</td>
<td>86.3</td>
<td>92.1</td>
<td>84.7</td>
<td>97.4</td>
<td>98.7</td>
<td>87.2</td>
</tr>
<tr>
<td>AltCLIP</td>
<td><b>69.8</b></td>
<td><b>89.9</b></td>
<td><b>94.7</b></td>
<td><b>84.8</b></td>
<td><b>97.4</b></td>
<td>98.8</td>
<td><b>89.2</b></td>
</tr>
<tr>
<td rowspan="7">MSCOCO<sub>EN</sub></td>
<td>CLIP</td>
<td>36.5</td>
<td>61.1</td>
<td>71.1</td>
<td>56.4</td>
<td>79.5</td>
<td>86.5</td>
<td>65.2</td>
</tr>
<tr>
<td>Taiyi</td>
<td>11.7</td>
<td>27.8</td>
<td>37.4</td>
<td>19.8</td>
<td>42.1</td>
<td>54.3</td>
<td>32.2</td>
</tr>
<tr>
<td>Wukong</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>R2D2</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>CN-CLIP</td>
<td>26.1</td>
<td>50.0</td>
<td>61.3</td>
<td>40.9</td>
<td>65.8</td>
<td>76.3</td>
<td>53.4</td>
</tr>
<tr>
<td>AltCLIP<sub>T</sub></td>
<td>37.5</td>
<td>62.1</td>
<td>72.1</td>
<td>57.2</td>
<td>80.5</td>
<td>87.5</td>
<td>66.1</td>
</tr>
<tr>
<td>AltCLIP</td>
<td><b>42.9</b></td>
<td><b>68.0</b></td>
<td><b>77.4</b></td>
<td><b>58.6</b></td>
<td><b>80.6</b></td>
<td><b>87.8</b></td>
<td><b>69.2</b></td>
</tr>
<tr>
<td rowspan="7">MSCOCO<sub>CN</sub> (1K)</td>
<td>CLIP</td>
<td>0.6</td>
<td>4.1</td>
<td>7.1</td>
<td>1.8</td>
<td>6.7</td>
<td>11.9</td>
<td>5.4</td>
</tr>
<tr>
<td>Taiyi</td>
<td>52.0</td>
<td>80.2</td>
<td>89.6</td>
<td>46.6</td>
<td>76.3</td>
<td>88.6</td>
<td>72.2</td>
</tr>
<tr>
<td>Wukong<sup>†</sup></td>
<td>55.2</td>
<td>81.0</td>
<td>90.6</td>
<td>53.4</td>
<td>80.2</td>
<td>90.1</td>
<td>75.1</td>
</tr>
<tr>
<td>R2D2<sup>†</sup></td>
<td>63.3</td>
<td><b>89.3</b></td>
<td><b>95.7</b></td>
<td>56.4</td>
<td>85.0</td>
<td>93.1</td>
<td>80.5</td>
</tr>
<tr>
<td>CN-CLIP</td>
<td>63.7</td>
<td>88.7</td>
<td>94.4</td>
<td>61.0</td>
<td>84.7</td>
<td>93.6</td>
<td>81.0</td>
</tr>
<tr>
<td>AltCLIP<sub>T</sub></td>
<td>55.7</td>
<td>82.9</td>
<td>91.2</td>
<td>60.7</td>
<td>86.3</td>
<td>93.4</td>
<td>78.4</td>
</tr>
<tr>
<td>AltCLIP</td>
<td><b>63.9</b></td>
<td>87.2</td>
<td>93.9</td>
<td><b>62.8</b></td>
<td><b>88.8</b></td>
<td><b>95.5</b></td>
<td><b>82.0</b></td>
</tr>
<tr>
<td rowspan="7">MSCOCO<sub>CN</sub> (5K)</td>
<td>CLIP</td>
<td>0.8</td>
<td>3.9</td>
<td>5.8</td>
<td>3.5</td>
<td>8.9</td>
<td>14.4</td>
<td>6.2</td>
</tr>
<tr>
<td>Taiyi</td>
<td>46.1</td>
<td>74.9</td>
<td>85.1</td>
<td>58.1</td>
<td>83.9</td>
<td>91.7</td>
<td>73.3</td>
</tr>
<tr>
<td>Wukong</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>R2D2</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>CN-CLIP</td>
<td>58.6</td>
<td>85.3</td>
<td>92.7</td>
<td>72.1</td>
<td>90.9</td>
<td>94.7</td>
<td>82.4</td>
</tr>
<tr>
<td>AltCLIP<sub>T</sub></td>
<td>54.9</td>
<td>81.8</td>
<td>90.5</td>
<td>76.3</td>
<td>93.9</td>
<td><b>97.6</b></td>
<td>82.5</td>
</tr>
<tr>
<td>AltCLIP</td>
<td><b>61.3</b></td>
<td><b>86.0</b></td>
<td><b>93.2</b></td>
<td><b>77.8</b></td>
<td><b>94.4</b></td>
<td>97.5</td>
<td><b>85.0</b></td>
</tr>
</tbody>
</table>

Table 2: Experimental results on retrieval tasks, namely English and Chinese version of Flickr30k and MSCOCO. All image encoders used in these models are ViT-L for fair comparison. AltCLIP<sub>T</sub> denotes our model after Teacher Learning stage while AltCLIP denotes our model after contrastive learning stage.<sup>†</sup> represents we report original results from papers.

tilingual model AltCLIP<sub>M9</sub> on the **XTD** (Aggarwal and Kale, 2020b) dataset. XTD selected 1K images from MS COCO, and translated the corresponding English Captions into 11 languages (English(en), German(de), French(fr), Chinese(zh), Japanese(ja), Italian(it), Spanish(es), Russian(ru), Polish(pl), Turkish(tr), Korean(ko)). The evaluation metrics for image classification benchmarks are respectively accuracy (default), mean per class (the average of recall obtained on each class, for imbalanced datasets, i.e. FGVC Aircraft, Oxford-IIIT Pets, Caltech-101, Oxford Flowers 102), 11-point mAP (mean average of 11-pt interpolated precision for each class, for VOC 2007), mean(top1, top5) (the mean of acc@1 and acc@5, for Kinetics400 and Kinetics600), while for cross-modal retrieval benchmarks, are Recall@K where  $K \in \{1, 5, 10\}$ , and Mean Recall(MR, i.e., the

average of Recall@K) for both image-to-text retrieval and text-to-image retrieval tasks, which are same with the setups in CLIP (Radford et al., 2021).

## 5.2 Zero-shot performance

**Image Classification** We first present evaluation results of zero-shot image classification on the ImageNet dataset and its four out-of-distribution variants. For baselines, we compare our model with CLIP (Radford et al., 2021), CN-CLIP (Yang et al., 2022), and multilingual CLIP (M-CLIP) (Carlsson et al., 2022). As illustrated in Table 1, AltCLIP achieves results that are very close to CLIP in English and sets new state-of-the-art results on Chinese ImageNet, ImageNet-A, ImageNet-R, and ImageNet V2. These results demonstrate the effectiveness of our method:Figure 2: Comparison Results of our proposed model and OpenAI’s CLIP.  $\text{AltCLIP}_T$  denotes for our model after Teacher Learning Stage while  $\text{AltCLIP}$  denotes for our model after Contrastive Learning Stage.  $\text{AltCLIP}_{M9}$  denotes for our model extending to 9 different languages. All image encoders are  $\text{CLIP}_{ViT-L14}$ .

<table border="1">
<thead>
<tr>
<th rowspan="2">Method</th>
<th colspan="8">Language</th>
</tr>
<tr>
<th>En</th>
<th>Es</th>
<th>Fr</th>
<th>Zh</th>
<th>It</th>
<th>Ko</th>
<th>Ru</th>
<th>Jp</th>
</tr>
</thead>
<tbody>
<tr>
<td><math>\text{CLIP}_{ViT-B32}</math></td>
<td>90.3</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td><math>\text{CLIP}_{ViT-L14}</math></td>
<td>91.8</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td><math>\text{CLIP}_{ViT-B16+}^\dagger</math></td>
<td>94.3</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>mUSE PATR</td>
<td>83.6</td>
<td>75.6</td>
<td>76.9</td>
<td>76.1</td>
<td>73.4</td>
<td>64.3</td>
<td>73.6</td>
<td>69.4</td>
</tr>
<tr>
<td>mUSE m3</td>
<td>85.3</td>
<td>78.9</td>
<td>78.9</td>
<td>76.7</td>
<td>73.6</td>
<td>67.8</td>
<td>76.1</td>
<td>70.7</td>
</tr>
<tr>
<td><math>\text{M-CLIP}_{ViT-B32}</math></td>
<td>91.8</td>
<td>89.1</td>
<td>89.4</td>
<td>89.3</td>
<td>89.8</td>
<td>82.1</td>
<td>86.1</td>
<td>81.0</td>
</tr>
<tr>
<td><math>\text{M-CLIP}_{ViT-L14}</math></td>
<td>92.4</td>
<td>91</td>
<td>90</td>
<td>89.7</td>
<td>91.1</td>
<td>85.2</td>
<td>85.8</td>
<td>81.9</td>
</tr>
<tr>
<td><math>\text{M-CLIP}_{ViT-B16+}^\dagger</math></td>
<td>95</td>
<td>93.6</td>
<td><b>93.1</b></td>
<td>94</td>
<td>93.1</td>
<td>89</td>
<td>90</td>
<td>84.2</td>
</tr>
<tr>
<td><math>\text{AltCLIP}_{M9}</math></td>
<td><b>95.4</b></td>
<td><b>94.1</b></td>
<td>92.9</td>
<td><b>95.1</b></td>
<td><b>94.2</b></td>
<td><b>94.4</b></td>
<td><b>91.8</b></td>
<td><b>91.7</b></td>
</tr>
</tbody>
</table>

Table 3: Comparison results on the multilingual cross-modal Retrieve dataset XTD. Following M-CLIP, we report recall@10 on Image to Text.  $^\dagger$ represents using image encoder released by OpenCLIP project (Ilharco et al., 2021).

compared to other Chinese baseline models where hundreds of millions of text-image pairs are used in pretraining, we only use 36M parallel text data and 2M text-image pairs in training.

**Cross-modal Retrieval** For cross-modal retrieval, we compare our model with CLIP in English and R2D2 (Xie et al., 2022), Wukong (Gu et al., 2022), Taiyi (Wang et al., 2022) and CN-CLIP (Yang et al., 2022) in Chinese. The results are shown in Table 2.  $\text{AltCLIP}$  outperforms all baseline models on most datasets and tasks. We notice that  $\text{AltCLIP}$  outperforms CLIP on both text-to-image and image-to-text retrieval. This could be due to the following reasons: 1). We used a small subset (less than 1M) of LAION 5B at the

Contrastive Learning stage, which is in a different distribution of the pretraining data used in CLIP; 2). Our language encoder initialized from XLM-R provides better language understanding ability. We left it as a future investigation to properly analyze the factors.

**Multilingual Cross-modal Retrieval** For baseline, we compare our model with CLIP, M-CLIP (Carlsson et al., 2022) and mUSE (Yang et al., 2020). The results of the comparison on XTD (Aggarwal and Kale, 2020b) are shown in Table 3, where  $\text{AltCLIP}_{M9}$  achieves state-of-the-art results in 7 languages. Notably, joint multilingual training maintains state-of-the-art capabilities in English and achieves better results than the original<table border="1">
<thead>
<tr>
<th>EN-EN</th>
<th>EN-CN<sub>MT</sub></th>
<th>EN-CN<sub>HT</sub></th>
<th>CL</th>
<th>Flickr30K<sub>EN</sub></th>
<th>Flickr30K<sub>CN</sub></th>
<th>ImageNet<sub>EN</sub></th>
<th>ImageNet<sub>CN</sub></th>
</tr>
</thead>
<tbody>
<tr>
<td>✓</td>
<td>✓</td>
<td>✓</td>
<td>✓</td>
<td><b>90.4</b></td>
<td><b>89.2</b></td>
<td>74.5</td>
<td><b>59.6</b></td>
</tr>
<tr>
<td>✓</td>
<td>✓</td>
<td>✓</td>
<td></td>
<td>88.3</td>
<td>87.2</td>
<td><b>74.7</b></td>
<td>58.2</td>
</tr>
<tr>
<td>✓</td>
<td>✓</td>
<td></td>
<td></td>
<td>86.8</td>
<td>85.8</td>
<td>51.6</td>
<td>41.7</td>
</tr>
<tr>
<td>✓</td>
<td></td>
<td></td>
<td></td>
<td>86.6</td>
<td>53.9</td>
<td>53.8</td>
<td>12.8</td>
</tr>
<tr>
<td></td>
<td>✓</td>
<td></td>
<td></td>
<td>61.9</td>
<td>85.4</td>
<td>15.5</td>
<td>42.5</td>
</tr>
</tbody>
</table>

Table 4: Ablation Experiments. CL indicates the use of Contrastive Learning stage, while EN-EN, EN-CN<sub>MT</sub>, EN-CN<sub>HT</sub> refers to parallel data used in Teacher Learning stage. Specifically, EN-EN indicates the use of English-English text pairs; EN-CN indicates the use of English-Chinese parallel text, including EN-CN<sub>MT</sub> represents machine translated pairs while EN-CN<sub>HT</sub> stands for human-translated data, i.e TSL2019. All compared models are pre-trained for 10 epochs.

CLIP model on this dataset. We may achieve better results for two reasons: 1. We equally translate a fixed set of English captions for each language, which allows each language to share a more comprehensive distribution. 2. We introduce more parallel data of human translation, and experiments show that this part of the data is helpful for establishing a robust multilingual representation.

**Full CLIP benchmark** We present the evaluation results of a wider range of tasks in English in Figure 2. We compare the effectiveness of the Teacher Learning Stage and Contrastive Learning Stage, and the bilingual AltCLIP and multilingual AltCLIP<sub>M9</sub>. We observe that at the Teacher Learning Stage, the model already learns a good representation of text-image representation, as it gets a close performance of the original CLIP model on a broad range of zero-shot benchmarks. The Contrastive Learning stage further improves our model’s performance, especially on retrieval tasks like Flickr30k and MSCOCO. Further, the multilingual AltCLIP<sub>M9</sub> achieves close performances with bilingual AltCLIP, indicating that our method is effective at extending the number of languages supported.

### 5.3 Ablation study

In this section, we present results from ablation studies. We show the significance of including various parallel data in Teacher Learning stage in Table 4. As illustrated in the 3rd and 5th line, without English-to-English parallel data, the accuracy on English ImageNet drastically drops to 15.47 from 53.8. Similarly, excluding machine-translated English-to-Chinese data, has a great impact on the performances on Chinese benchmarks, i.e. ImageNet<sub>CN</sub> and Flickr30K<sub>CN</sub>, due to influenced Chinese text-image representation. More-

over, empirical experiments show that introducing human translated parallel data leads to a great improvement on ImageNet<sub>CN</sub> which may be related to the distribution of the data set. This indicates that the diversity of training data used for teacher learning, can benefit the language model to gain more knowledge about entities or concepts.

### 5.4 Examples of text-to-image generation

To demonstrate the effects of text alignment in our model, we use the text encoder of AltCLIP and AltCLIP<sub>M9</sub> to further finetune a text-to-image generation model from Stable Diffusion (Rombach et al., 2022). We use stable-diffusion v1-4<sup>6</sup> as initialization, and we use AltCLIP or AltCLIP<sub>M9</sub> as the language encoder. We freeze all the parameters in the diffusion model except for the key and value projection layers of the cross-attention block during finetuning. The dataset we used to finetune is the same one used for Contrastive Learning as described in Section 4.1. We call our image generation models AltDiffusion and AltDiffusion<sub>M9</sub>.

As shown in Fig. 3, AltDiffusion generates high-quality images close to Stable Diffusion on both English and Chinese prompts. Further, we notice that our model generates very similar images given translated English and Chinese prompts. For the multilingual version, we observed a very interesting phenomenon: when given a prompt that’s translated into different languages, the generated images reflect cultural differences to some extent. See Tab. 5 for some examples. We left it as a future effort to explore and analyze carefully on how culture inherited in different languages can affect image generation.

<sup>6</sup><https://huggingface.co/CompVis/stable-diffusion-v1-4-original><table border="1">
<thead>
<tr>
<th>Prompts</th>
<th>Generated Image</th>
</tr>
</thead>
<tbody>
<tr>
<td>
<p>EN: clean simple line art of a cute little girl with short wavy curly hair. she is dressed as an astronaut. no background. well composed, clean coloring book page, beautiful detailed face. coloring book line art by artgerm and greg rutkowski and johanna basford and alphonse mucha</p>
</td>
<td>
</td>
</tr>
<tr>
<td>
<p>ZH: 一个可爱的小女孩的干净简单的线条艺术，短波浪卷发。她打扮成宇航员。没有背景。构图良好，涂色书页干净，面部细节优美。Artgerm和Greg Rutkowski以及Johanna Basford和Alphonse Mucha的着色书线条艺术</p>
</td>
<td>
</td>
</tr>
<tr>
<td>
<p>FR: Nettoyer l'art au trait simple d'une petite fille mignonne avec des cheveux courts et bouclés ondulés. Elle est habillée en astronaute. Pas d'antécédents. Bien composé, page de livre à colorier propre, beau visage détaillé. Dessin de ligne de livre de coloriage par Artgerm et Greg Rutkowski et Johanna Basford et Alphonse Mucha</p>
</td>
<td>
</td>
</tr>
<tr>
<td>
<p>SP: Arte de línea simple y limpia de una linda niña con cabello corto y rizado ondulado. Está vestida de astronauta. sin antecedentes. Bien compuesto, página de libro para colorear limpio, hermosa cara detallada. Coloring Book Line Art por Artgerm y Greg Rutkowski y Johanna Basford y Alphonse Mucha</p>
</td>
<td>
</td>
</tr>
<tr>
<td>
<p>RU: чистая простая линия искусства милый маленькой девочки с короткими волнистыми вьющимися волосами. она одета как астронавт. нет предыстории. хорошо составленная, чистая раскраска, красивое детализированное лицо. раскраска линии артгерма и Грега Рутковски и Джоанны Басфорд и Альфонса Мухи</p>
</td>
<td>
</td>
</tr>
<tr>
<td>
<p>AR: فن الخط النظيف البسيط لفئة صغيرة: لطيفة ذات شعر قصير مموج مجعد. كانت ترتد زي رائدة الفضاء. أي خلفية. مؤلف بشكل جيد، صفحة كتاب تلوين نظيفة، وجه مفصل ج. Artgerm و Greg Rutkowski و Johanna Basford و Alphonse Mucha</p>
</td>
<td>
</td>
</tr>
<tr>
<td>
<p>JA: 短いウェーブのかかった巻き毛を持つかわいい女の子のきれいなシンプルなラインアート。彼女は宇宙飛行士の格好をしています。背景なし。よく構成された、きれいな塗り絵ページ、美しい詳細な顔。artgerm と greg rutkowski と johanna basford と alphonse mucha による塗り絵の線画</p>
</td>
<td>
</td>
</tr>
<tr>
<td>
<p>KO: 짧은 물결 모양의 곱슬머리를 가진 귀여운 소녀의 깨끗하고 단순한 라인 아트. 그녀는 우주 비행사 옷을 입고 있습니다. 배경이 없습니다. 잘 구성되고 깨끗한 컬러링 북 페이지, 아름다운 디테일한 얼굴. artgerm 및 greg rutkowski 및 johanna basford 및 alphonse mucha 의 색칠하기 책 라인 아트</p>
</td>
<td>
</td>
</tr>
<tr>
<td>
<p>IT: linea semplice e pulita di una bambina carina con capelli ricci corti e ondulati. è vestita da astronauta. nessuno sfondo. pagina del libro da colorare ben composta, pulita, bel viso dettagliato. disegno al tratto del libro da colorare di artgerm e greg rutkowski e johanna basford e alphonse mucha</p>
</td>
<td>
</td>
</tr>
</tbody>
</table>

Table 5: The images generated by AltDiffusion<sub>M9</sub> with the same prompt translated to nine languages and a fixed seed.Figure 3: Examples of text-to-image generation. Text prompt: "a pretty female druid surrounded by forest animals, digital painting, photorealistic, in the style of greg rutkowski, highly detailed, realistic.", "一个由森林动物环绕的漂亮的女德鲁伊,数字绘画,摄影现实,格雷格·鲁特科夫斯基风格,高度详细,现实"

## 6 Conclusion

In this work, we presented a conceptually simple and effective two-stage training schema to learn bilingual and multilingual multimodal representation models, via teacher learning and contrastive learning. We show the effectiveness of our method by conducting extensive experiments on a wide range of tasks in English and Chinese. In Chinese, our method sets new state-of-the-art results on multiple zero-shot image classification and retrieval tasks while being highly effective: we only use tens of millions of text data and two million text-image pairs during training, whereas most prior work requires training on hundreds of millions of text-image pairs. Future work includes exploring altering the image encoder to combine vision signals learned from different data distributions and possibly eliminating the need for machine-translated data to build a multilingual multimodal pretraining model.

## Acknowledgements

We’d like to thank Yizhou Zheng for helpful suggestions on fine-tuning stable diffusion models. We’d like to thank Luke Zettlemoyer for valuable suggestions and advices. We also thank Chenghua Zhou, Quan Sun and Yue Cao for helpful discus-

sions and contributions. Finally, we’d like to thank the data and infrastructure team at BAAI for their support on this project.

## References

Pranav Aggarwal and Ajinkya Kale. 2020a. Towards zero-shot cross-lingual image retrieval. *arXiv preprint arXiv:2012.05107*.

Pranav Aggarwal and Ajinkya Kale. 2020b. [Towards zero-shot cross-lingual image retrieval](#).

Andrei Barbu, David Mayo, Julian Alverio, William Luo, Christopher Wang, Dan Gutfreund, Josh Tenenbaum, and Boris Katz. 2019. Objectnet: A large-scale bias-controlled dataset for pushing the limits of object recognition models. *Advances in neural information processing systems*, 32.

Thomas Berg, Jiongxin Liu, Seung Woo Lee, Michelle L Alexander, David W Jacobs, and Peter N Belhumeur. 2014. Birdsnap: Large-scale fine-grained visual categorization of birds. In *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition*, pages 2011–2018.

Federico Bianchi, Giuseppe Attanasio, Raphael Pisoni, Silvia Terragni, Gabriele Sarti, and Sri Lakshmi. 2021. Contrastive language-image pre-training for the italian language. *arXiv preprint arXiv:2108.08688*.

Matthew Blaschko, Ross B Girshick, Juho Kannala, Iasonas Kokkinos, Siddarth Mahendran, Subhransu Maji, Sammy Mohammed, Esa Rahtu, Naomi Saphra, Karen Simonyan, et al. 2012. Towards a detailed understanding of objects and scenes in natural images.

Lukas Bossard, Matthieu Guillaumin, and Luc Van Gool. 2014. Food-101 – mining discriminative components with random forests. In *European Conference on Computer Vision*.

Fredrik Carlsson, Philipp Eisen, Faton Rekathati, and Magnus Sahlgren. 2022. Cross-lingual and multilingual clip. In *Proceedings of the Thirteenth Language Resources and Evaluation Conference*, pages 6848–6854.

Joao Carreira, Eric Noland, Andras Banki-Horvath, Chloe Hillier, and Andrew Zisserman. 2018. A short note about kinetics-600. *arXiv preprint arXiv:1808.01340*.

Soravit Changpinyo, Piyush Sharma, Nan Ding, and Radu Soricut. 2021. Conceptual 12m: Pushing web-scale image-text pre-training to recognize long-tail visual concepts. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 3558–3568.Xinlei Chen, Hao Fang, Tsung-Yi Lin, Ramakrishna Vedantam, Saurabh Gupta, Piotr Dollár, and C Lawrence Zitnick. 2015. Microsoft coco captions: Data collection and evaluation server. *arXiv preprint arXiv:1504.00325*.

Gong Cheng, Junwei Han, and Xiaoqiang Lu. 2017. Remote sensing image scene classification: Benchmark and state of the art. *Proceedings of the IEEE*, 105(10):1865–1883.

Mircea Cimpoi, Subhransu Maji, Iasonas Kokkinos, Sammy Mohamed, and Andrea Vedaldi. 2014. Describing textures in the wild. In *Proceedings of the IEEE conference on computer vision and pattern recognition*, pages 3606–3613.

Dan C Cireşan, Ueli Meier, Jonathan Masci, Luca M Gambardella, and Jürgen Schmidhuber. 2011. High-performance neural networks for visual object classification. *arXiv preprint arXiv:1102.0183*.

Adam Coates, Andrew Ng, and Honglak Lee. 2011. An analysis of single-layer networks in unsupervised feature learning. In *Proceedings of the fourteenth international conference on artificial intelligence and statistics*, pages 215–223. JMLR Workshop and Conference Proceedings.

Alexis Conneau, Kartikay Khandelwal, Naman Goyal, Vishrav Chaudhary, Guillaume Wenzek, Francisco Guzmán, Edouard Grave, Myle Ott, Luke Zettlemoyer, and Veselin Stoyanov. 2020. Unsupervised cross-lingual representation learning at scale. In *ACL*.

Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li, and Li Fei-Fei. 2009. Imagenet: A large-scale hierarchical image database. In *CVPR*, pages 248–255. Ieee.

Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, et al. 2020. An image is worth 16x16 words: Transformers for image recognition at scale. *arXiv preprint arXiv:2010.11929*.

Mark Everingham. 2007. The pascal visual object classes challenge,(voc2007) results. <http://pascalin.ecs.soton.ac.uk/challenges/VOC/voc2007/index.html>.

Nanyi Fei, Zhiwu Lu, Yizhao Gao, Guoxing Yang, Yuqi Huo, Jingyuan Wen, Haoyu Lu, Ruihua Song, Xin Gao, Tao Xiang, et al. 2021. Wenlan 2.0: Make ai imagine via a multimodal foundation model. *arXiv preprint arXiv:2110.14378*.

Li Fei-Fei, Robert Fergus, and Pietro Perona. 2006. One-shot learning of object categories. *IEEE transactions on pattern analysis and machine intelligence*, 28(4):594–611.

Ian J Goodfellow, Dumitru Erhan, Pierre Luc Carrier, Aaron Courville, Mehdi Mirza, Ben Hamner, Will Cukierski, Yichuan Tang, David Thaler, Dong-Hyun Lee, et al. 2013. Challenges in representation learning: A report on three machine learning contests. In *International conference on neural information processing*, pages 117–124. Springer.

Jiaxi Gu, Xiaojun Meng, Guansong Lu, Lu Hou, Minzhe Niu, Hang Xu, Xiaodan Liang, Wei Zhang, Xin Jiang, and Chunjing Xu. 2022. Wukong: 100 million large-scale chinese cross-modal pre-training dataset and a foundation framework. *arXiv preprint arXiv:2202.06767*.

Raia Hadsell, Sumit Chopra, and Yann LeCun. 2006. Dimensionality reduction by learning an invariant mapping. In *2006 IEEE Computer Society Conference on Computer Vision and Pattern Recognition (CVPR'06)*, volume 2, pages 1735–1742. IEEE.

Patrick Helber, Benjamin Bischke, Andreas Dengel, and Damian Borth. 2019. Eurosat: A novel dataset and deep learning benchmark for land use and land cover classification. *IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing*, 12(7):2217–2226.

Dan Hendrycks, Steven Basart, Norman Mu, Saurav Kadavath, Frank Wang, Evan Dorundo, Rahul Desai, Tyler Zhu, Samyak Parajuli, Mike Guo, et al. 2021a. The many faces of robustness: A critical analysis of out-of-distribution generalization. In *Proceedings of the IEEE/CVF International Conference on Computer Vision*, pages 8340–8349.

Dan Hendrycks, Kevin Zhao, Steven Basart, Jacob Steinhardt, and Dawn Song. 2021b. Natural adversarial examples. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 15262–15271.

Geoffrey Hinton, Oriol Vinyals, and Jeff Dean. 2015. Distilling the knowledge in a neural network. *stat*, 1050:9.

Yuqi Huo, Manli Zhang, Guangzhen Liu, Haoyu Lu, Yizhao Gao, Guoxing Yang, Jingyuan Wen, Heng Zhang, Baogui Xu, Weihao Zheng, et al. 2021. Wenlan: Bridging vision and language by large-scale multi-modal pre-training. *arXiv preprint arXiv:2103.06561*.

Gabriel Ilharco, Mitchell Wortsman, Ross Wightman, Cade Gordon, Nicholas Carlini, Rohan Taori, Achal Dave, Vaishaal Shankar, Hongseok Namkoong, John Miller, Hannaneh Hajishirzi, Ali Farhadi, and Ludwig Schmidt. 2021. [Openclip](#). If you use this software, please cite it as below.

Will Kay, Joao Carreira, Karen Simonyan, Brian Zhang, Chloe Hillier, Sudheendra Vijayanarasimhan, Fabio Viola, Tim Green, Trevor Back, Paul Natsev, et al. 2017. The kinetics human action video dataset. *arXiv preprint arXiv:1705.06950*.Byungsoo Ko and Geonmo Gu. 2022. Large-scale bilingual language-image contrastive learning. *arXiv preprint arXiv:2203.14463*.

Jonathan Krause, Michael Stark, Jia Deng, and Li Fei-Fei. 2013. 3d object representations for fine-grained categorization. In *4th International IEEE Workshop on 3D Representation and Recognition (3dRR-13)*, Sydney, Australia.

Alex Krizhevsky, Geoffrey Hinton, et al. 2009. Learning multiple layers of features from tiny images.

Weiyu Lan, Xirong Li, and Jianfeng Dong. 2017. Fluency-guided cross-lingual image captioning. In *Proceedings of the 25th ACM international conference on Multimedia*, pages 1549–1557.

Xirong Li, Chaoxi Xu, Xiaoxu Wang, Weiyu Lan, Zhengxiong Jia, Gang Yang, and Jieping Xu. 2019. Coco-cn for cross-lingual image tagging, captioning, and retrieval. *IEEE Transactions on Multimedia*, 21(9):2347–2360.

Tsung-Yi Lin, Michael Maire, Serge Belongie, James Hays, Pietro Perona, Deva Ramanan, Piotr Dollár, and C Lawrence Zitnick. 2014. Microsoft coco: Common objects in context. In *European conference on computer vision*, pages 740–755. Springer.

Maria-Elena Nilsback and Andrew Zisserman. 2008. Automated flower classification over a large number of classes. In *2008 Sixth Indian Conference on Computer Vision, Graphics & Image Processing*, pages 722–729. IEEE.

Omkar M Parkhi, Andrea Vedaldi, Andrew Zisserman, and CV Jawahar. 2012. Cats and dogs. In *2012 IEEE conference on computer vision and pattern recognition*, pages 3498–3505. IEEE.

Maxime Portaz, Hicham Randrianarivo, Adrien Nivaggioli, Estelle Maudet, Christophe Servan, and Sylvain Peyronnet. 2019. Image search using multilingual texts: a cross-modal learning approach between image and text. *arXiv preprint arXiv:1903.11299*.

Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, et al. 2021. Learning transferable visual models from natural language supervision. In *International Conference on Machine Learning*, pages 8748–8763. PMLR.

Benjamin Recht, Rebecca Roelofs, Ludwig Schmidt, and Vaishaal Shankar. 2019. Do imagenet classifiers generalize to imagenet? In *International Conference on Machine Learning*, pages 5389–5400. PMLR.

Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, and Björn Ommer. 2022. High-resolution image synthesis with latent diffusion models. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 10684–10695.

Christoph Schuhmann, Romain Beaumont, Richard Vencu, Cade Gordon, Ross Wightman, Mehdi Cherti, Theo Coombes, Aarush Katta, Clayton Mullis, Mitchell Wortsman, et al. 2022. Laion-5b: An open large-scale dataset for training next generation image-text models. *arXiv preprint arXiv:2210.08402*.

Christoph Schuhmann, Richard Vencu, Romain Beaumont, Robert Kaczmarczyk, Clayton Mullis, Aarush Katta, Theo Coombes, Jenia Jitsev, and Aran Komatsuzaki. 2021. Laion-400m: Open dataset of clip-filtered 400 million image-text pairs. *arXiv preprint arXiv:2111.02114*.

Piyush Sharma, Nan Ding, Sebastian Goodman, and Radu Soricut. 2018. Conceptual captions: A cleaned, hypernymed, image alt-text dataset for automatic image captioning. In *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 2556–2565.

Khurram Soomro, Amir Roshan Zamir, and Mubarak Shah. 2012. Ucf101: A dataset of 101 human actions classes from videos in the wild. *arXiv preprint arXiv:1212.0402*.

Johannes Stallkamp, Marc Schlipsing, Jan Salmen, and Christian Igel. 2011. The german traffic sign recognition benchmark: a multi-class classification competition. In *The 2011 international joint conference on neural networks*, pages 1453–1460. IEEE.

Jörg Tiedemann. 2012. Parallel data, tools and interfaces in opus. In *Lrec*, volume 2012, pages 2214–2218.

Bastiaan S Veeling, Jasper Linmans, Jim Winkens, Taco Cohen, and Max Welling. 2018. Rotation equivariant cnns for digital pathology. In *International Conference on Medical image computing and computer-assisted intervention*, pages 210–218. Springer.

Haohan Wang, Songwei Ge, Zachary Lipton, and Eric P Xing. 2019. Learning robust global representations by penalizing local predictive power. *Advances in Neural Information Processing Systems*, 32.

Junjie Wang, Yuxiang Zhang, Lin Zhang, Ping Yang, Xinyu Gao, Ziwei Wu, Xiaoqun Dong, Junqing He, Jianheng Zhuo, Qi Yang, Yongfeng Huang, Xiayu Li, Yanghan Wu, Junyu Lu, Xinyu Zhu, Weifeng Chen, Ting Han, Kunhao Pan, Rui Wang, Hao Wang, Xiaojun Wu, Zhongshen Zeng, Chongpei Chen, Ruyi Gan, and Jiaxing Zhang. 2022. Fengshenbang 1.0: Being the foundation of chinese cognitive intelligence. *CoRR*, abs/2209.02970.

J. Xiao, J. Hays, K. A. Ehinger, A. Oliva, and A. Torralba. 2010. [Sun database: Large-scale scene recognition from abbey to zoo](#). In *2010 IEEE Computer Society Conference on Computer Vision and Pattern Recognition*, pages 3485–3492.Chunyu Xie, Heng Cai, Jianfei Song, Jincheng Li, Fanjing Kong, Xiaoyu Wu, Henrique Morimitsu, Lin Yao, Dexin Wang, Dawei Leng, et al. 2022. Zero and r2d2: A large-scale chinese cross-modal benchmark and a vision-language framework. *arXiv preprint arXiv:2205.03860*.

Bright Xu. 2019. Nlp chinese corpus: Large scale chinese corpus for nlp.

An Yang, Junshu Pan, Junyang Lin, Rui Men, Yichang Zhang, Jingren Zhou, and Chang Zhou. 2022. Chinese clip: Contrastive vision-language pretraining in chinese. *arXiv preprint arXiv:2211.01335*.

Yinfei Yang, Daniel Cer, Amin Ahmad, Mandy Guo, Jax Law, Noah Constant, Gustavo Hernandez Abrego, Steve Yuan, Chris Tar, Yun-hsuan Sung, Brian Strobe, and Ray Kurzweil. 2020. [Multilingual universal sentence encoder for semantic retrieval](#). In *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics: System Demonstrations*, pages 87–94, Online. Association for Computational Linguistics.

Peter Young, Alice Lai, Micah Hodosh, and Julia Hockenmaier. 2014. From image descriptions to visual denotations: New similarity metrics for semantic inference over event descriptions. *Transactions of the Association for Computational Linguistics*, 2:67–78.

Sha Yuan, Hanyu Zhao, Zhengxiao Du, Ming Ding, Xiao Liu, Yukuo Cen, Xu Zou, Zhilin Yang, and Jie Tang. 2021. Wudaocorpora: A super large-scale chinese corpora for pre-training language models. *AI Open*, 2:65–68.

Xiaohua Zhai, Xiao Wang, Basil Mustafa, Andreas Steiner, Daniel Keysers, Alexander Kolesnikov, and Lucas Beyer. 2022. Lit: Zero-shot transfer with locked-image text tuning. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 18123–18133.

## A Hyper-parameters Optimization

<table border="1">
<thead>
<tr>
<th>Hyper-paramters</th>
<th>Teacher Learning</th>
<th>Contrastive Learning</th>
</tr>
</thead>
<tbody>
<tr>
<td>Batch size</td>
<td>1024</td>
<td>1024</td>
</tr>
<tr>
<td>Optimizer (AdamW, <math>\beta</math>)</td>
<td>(0.99, 0.999)</td>
<td>(0.99, 0.999)</td>
</tr>
<tr>
<td>Learning rate</td>
<td>1e-4</td>
<td>2e-6</td>
</tr>
<tr>
<td>Weight decay</td>
<td>1e-1</td>
<td>5e-2</td>
</tr>
<tr>
<td>Eps</td>
<td>1e-8</td>
<td>1e-8</td>
</tr>
<tr>
<td>Warmup steps</td>
<td>500</td>
<td>2000</td>
</tr>
<tr>
<td>#Epochs</td>
<td>10</td>
<td>1</td>
</tr>
<tr>
<td>Gradient clipping</td>
<td>1.0</td>
<td>5.0</td>
</tr>
<tr>
<td>Steps</td>
<td>238620</td>
<td>2000</td>
</tr>
</tbody>
</table>

Table 6: Hyper-parameters setting in Teacher Learning Stage and Contrastive Learning Stage.


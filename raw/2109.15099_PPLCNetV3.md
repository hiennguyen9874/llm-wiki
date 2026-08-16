# PP-LCNet: A Lightweight CPU Convolutional Neural Network

Cheng Cui, Tingquan Gao, Shengyu Wei, Yuning Du,  
Ruoyu Guo, Shuilong Dong, Bin Lu, Ying Zhou, Xueying Lv,  
Qiwen Liu, Xiaoguang Hu, Dianhai Yu, Yanjun Ma

Baidu Inc.

{cuicheng01, gaotingquan, weishengyu, duyuning} @baidu.com

## Abstract

We propose a lightweight CPU network based on the MKLDNN acceleration strategy, named PP-LCNet, which improves the performance of lightweight models on multiple tasks. This paper lists technologies which can improve network accuracy while the latency is almost constant. With these improvements, the accuracy of PP-LCNet can greatly surpass the previous network structure with the same inference time for classification. As shown in Figure 1, it outperforms the most state-of-the-art models. And for downstream tasks of computer vision, it also performs very well, such as object detection, semantic segmentation, etc. All our experiments are implemented based on PaddlePaddle<sup>1</sup>. Code and pretrained models are available at PaddleClas<sup>2</sup>.

## 1. Introduction

In the past few years, Convolutional Neural Networks (CNNs) represent the workhorses of the most current computer vision applications, including image classification[1, 2], object detection[3], attention prediction[4], target tracking[5], action recognition[6], semantic segmentation[7, 8], salient object detection[9] and edge detection[10].

As the model feature extraction capability increases and the number of model parameters and FLOPs get larger, it becomes difficult to achieve fast inference speed on mobile devices based ARM architecture or CPU devices based x86 architecture. In this case, many excellent mobile networks have been proposed, but due to the limitations of the MKLDNN, the speed of these networks is not ideal on the Intel CPU with MKLDNN enabled. In this paper, we rethink the lightweight models elements for network designed on Intel-CPU. In particular, we consider the following three fundamental questions. (i) How to promote the network to

Figure 1. Comparing the accuracy-latency of different mobile series models. Latency tested on Intel® Xeon® Gold 6148 Processor with batch size of 1 and MKLDNN enabled, the number of thread is 10.

learn stronger feature presentations without increasing latency. (ii) What are the elements to improve the accuracy of lightweight models on CPU. (iii) How to effectively combine different strategies for designing lightweight models on CPU.

Our main contribution is summarizing a series of methods to improve the accuracy without increase of inference time, and how to combine these methods to get a better balance of accuracy and speed. Based on this, we come up with several general rules for designing lightweight CNNs, and provide new ideas for other researchers to build CNNs on CPU devices. Furthermore, it can provide neural architecture search researchers with new ideas when constructing the search space, so as to get better models faster.

<sup>1</sup><https://github.com/PaddlePaddle>

<sup>2</sup><https://github.com/PaddlePaddle/PaddleClas>Figure 2. A detailed view of PP-LCNet. The dotted box represents optional modules. The stem part uses standard  $3 \times 3$  convolution. DepthSepConv means depth-wise separable convolutions, DW means depth-wise convolution, PW means point-wise convolution, GAP means Global Average Pooling.

## 2. Related Works

To promote the capabilities of the model, current works usually follow two types of methodologies. One is based on manually-designed CNN architecture, the other is based on Neural Architecture Search (NAS)[11].

**Manually-designed Architecture.** The VGG[12] exhibits a simple yet effective strategy of constructing very deep networks: stacking blocks with the same dimension. GoogLeNet[13] constructs an Inception block, which includes four parallel operations:  $1 \times 1$  convolution,  $3 \times 3$  convolution,  $5 \times 5$  convolution and max pooling. GoogLeNet makes the convolutional neural network light enough, then more and more lighter networks emerge. MobileNetV1[14] replaces the standard convolution by depthwise and pointwise convolutions, which greatly reduces the amount of parameters and FLOPs of the model. The author of MobileNetV2[15] proposed the Inverted block, which further reduces the FLOPs of the model and at the same time improves the performance of the model. ShuffleNetV1/V2[16][17] exchanges information through channel shuffle, which reduces the unnecessary overhead of the network structure. The author of GhostNet[18] proposed a novel Ghost module that can generate more feature maps with fewer parameters to improve

the overall performance of the model.

**Neural Architecture Search.** With the development of GPU hardware, the main point has shifted from a manually designed architecture to an architecture that adaptively performs a systematic search for specific tasks. A majority of NAS-generated networks use the similar search space to MobileNetV2[15], including EfficientNet[19], MobileNetV3[20], FBNet[21], DNANet[22], OFANet[23] and so on. The MixNet[24] proposed to hybridize depth-wise convolutions of different kernel size in one layer. NAS-generated networks relies on manually-generated block, such as BottleNeck[25], Inverted-block[15] and so on. Our approach can reduce search space and improve search efficiency for neural architecture search and potentially improve the overall performance, which can be studied in future work.

## 3. Approach

While there are many lightweight networks whose inference speed is fast on ARM-based devices, few networks take into account the speed on Intel CPU, especially when acceleration strategies such as MKLDNN enabled. Many methods to improve model accuracy will not increase the inference time much on ARM devices, however, when switch-<table border="1">
<thead>
<tr>
<th>Operator</th>
<th>Kernel Size</th>
<th>Stride</th>
<th>Input</th>
<th>Output</th>
<th>SE</th>
</tr>
</thead>
<tbody>
<tr>
<td>Conv2D</td>
<td><math>3 \times 3</math></td>
<td>2</td>
<td><math>224^2 \times 3</math></td>
<td><math>112^2 \times 16</math></td>
<td>-</td>
</tr>
<tr>
<td>DepthSepConv</td>
<td><math>3 \times 3</math></td>
<td>1</td>
<td><math>112^2 \times 16</math></td>
<td><math>112^2 \times 32</math></td>
<td>-</td>
</tr>
<tr>
<td>DepthSepConv</td>
<td><math>3 \times 3</math></td>
<td>2</td>
<td><math>112^2 \times 32</math></td>
<td><math>56^2 \times 64</math></td>
<td>-</td>
</tr>
<tr>
<td>DepthSepConv</td>
<td><math>3 \times 3</math></td>
<td>1</td>
<td><math>56^2 \times 64</math></td>
<td><math>56^2 \times 64</math></td>
<td>-</td>
</tr>
<tr>
<td>DepthSepConv</td>
<td><math>3 \times 3</math></td>
<td>2</td>
<td><math>56^2 \times 64</math></td>
<td><math>28^2 \times 128</math></td>
<td>-</td>
</tr>
<tr>
<td>DepthSepConv</td>
<td><math>3 \times 3</math></td>
<td>1</td>
<td><math>28^2 \times 128</math></td>
<td><math>28^2 \times 128</math></td>
<td>-</td>
</tr>
<tr>
<td>DepthSepConv</td>
<td><math>3 \times 3</math></td>
<td>2</td>
<td><math>28^2 \times 128</math></td>
<td><math>14^2 \times 256</math></td>
<td>-</td>
</tr>
<tr>
<td><math>5 \times</math> DepthSepConv</td>
<td><math>5 \times 5</math></td>
<td>1</td>
<td><math>14^2 \times 256</math></td>
<td><math>14^2 \times 256</math></td>
<td>-</td>
</tr>
<tr>
<td>DepthSepConv</td>
<td><math>5 \times 5</math></td>
<td>2</td>
<td><math>14^2 \times 256</math></td>
<td><math>7^2 \times 512</math></td>
<td>✓</td>
</tr>
<tr>
<td>DepthSepConv</td>
<td><math>5 \times 5</math></td>
<td>1</td>
<td><math>7^2 \times 512</math></td>
<td><math>7^2 \times 512</math></td>
<td>✓</td>
</tr>
<tr>
<td>GAP</td>
<td><math>7 \times 7</math></td>
<td>1</td>
<td><math>7^2 \times 512</math></td>
<td><math>1^2 \times 512</math></td>
<td>-</td>
</tr>
<tr>
<td>Conv2d, NBN</td>
<td><math>1 \times 1</math></td>
<td>1</td>
<td><math>1^2 \times 512</math></td>
<td><math>1^2 \times 1280</math></td>
<td>-</td>
</tr>
</tbody>
</table>

Table 1. Architecture details of PP-LCNet. SE denotes whether there is a Squeeze-and-Excitation in that block. NBN denotes no batch normalization.

ing to Intel CPU devices, the situation will be a little different. Here we have summarized some methods that can improve the performance of the model with little increase of inference time. These methods will be described in details below. We used the DepthSepConv mentioned by MobileNetV1[14] as our basic block. This block does not have operations such as shortcuts, so there are no additional operations such as concat or elementwise-add, these operations will not only slow down the inference speed of the model, but also will not improve the accuracy on a small model. Furthermore, this block has been deeply optimized by the Intel CPU acceleration library, and the inference speed can surpass other lightweight blocks such as inverted-block or shufflenet-block. We stack these blocks to form a BaseNet similar to MobileNetV1[14]. We combine the BaseNet and some of the existing technologies to a more powerful network, namely PP-LCNet.

### 3.1. Better activation function

As we all know, the quality of the activation function often determines the performance of the network. Since the activation function of network is changed from Sigmoid to ReLU, the performance of the network has been greatly improved. In recent years, more and more activation functions have emerged that go beyond ReLU. After EfficientNet[19] used the Swish activation function to show better performance, the author of MobileNetV3[20] upgraded it to H-Swish, thus avoiding a large number of exponential operations. Since then, many lightweight networks also use this activation function. We also replaced the activation function in BaseNet from ReLU to H-Swish. The performance has been greatly improved, while the inference time has hardly changed.

### 3.2. SE modules at appropriate positions

The SE module[26] has been used by a large number of networks since its being proposed. This module also helped SENet[26] winning the 2017 ImageNet[27] classification competition. It does a good job of weighting the network channels for better features, and its speed improvement version is also used in many lightweight networks such as MobileNetV3[20]. However, on Intel CPUs, the SE module[26] increases the inference time, so that we cannot use it for the whole network. In fact, we have done a lot of experiments and observed that when the SE module[26] is located at the end of the network, it can play a better role. So we just add the SE module[26] to the blocks near the tail of the network. This results in a better accuracy-speed balance. As with MobileNetV3[20], the activation functions for the two layers of the SE module[26] are ReLU and H-Sigmoid respectively.

### 3.3. Larger convolution kernels

The size of the convolution kernel often affects the final performance of the network. In MixNet[24], the authors analysed the effect of differently sized convolution kernels on the performance of the network, and ended up mixing different sizes of convolutional kernels in the same layer of the network. However, such a mixture slows down the inference speed of the model, so we try to use only one size of convolution kernel in the single layer, and ensure that a large convolution kernel is used in the case of low latency and high accuracy. We experimentally find that, similar to the placement of the SE module[26], replacing the  $3 \times 3$  convolutional kernels with only the  $5 \times 5$  convolutional kernels at the tail of the network would achieve the effect of replacing almost all layers of the network, so we did this replacement operation only at the tail of the network.<table border="1">
<thead>
<tr>
<th>Model</th>
<th>Params(M)</th>
<th>FLOPs(M)</th>
<th>Top-1 Acc.(%)</th>
<th>Top-5 Acc.(%)</th>
<th>Latency(ms)</th>
</tr>
</thead>
<tbody>
<tr>
<td>PP-LCNet 0.25x</td>
<td>1.5</td>
<td>18</td>
<td>51.86</td>
<td>75.65</td>
<td>1.74</td>
</tr>
<tr>
<td>PP-LCNet-0.35x</td>
<td>1.6</td>
<td>29</td>
<td>58.09</td>
<td>80.83</td>
<td>1.92</td>
</tr>
<tr>
<td>PP-LCNet-0.5x</td>
<td>1.9</td>
<td>47</td>
<td>63.14</td>
<td>84.66</td>
<td>2.05</td>
</tr>
<tr>
<td>PP-LCNet-0.75x</td>
<td>2.4</td>
<td>99</td>
<td>68.18</td>
<td>88.30</td>
<td>2.29</td>
</tr>
<tr>
<td>PP-LCNet-1x</td>
<td>3.0</td>
<td>161</td>
<td>71.32</td>
<td>90.03</td>
<td>2.46</td>
</tr>
<tr>
<td>PP-LCNet-1.5x</td>
<td>4.5</td>
<td>342</td>
<td>73.71</td>
<td>91.53</td>
<td>3.19</td>
</tr>
<tr>
<td>PP-LCNet-2x</td>
<td>6.5</td>
<td>590</td>
<td>75.18</td>
<td>92.27</td>
<td>4.27</td>
</tr>
<tr>
<td>PP-LCNet-2.5x</td>
<td>9.0</td>
<td>906</td>
<td>76.60</td>
<td>93.00</td>
<td>5.39</td>
</tr>
<tr>
<td><b>PP-LCNet-0.5x*</b></td>
<td><b>1.9</b></td>
<td><b>47</b></td>
<td><b>66.10</b></td>
<td><b>86.46</b></td>
<td><b>2.05</b></td>
</tr>
<tr>
<td><b>PP-LCNet-1x*</b></td>
<td><b>3.0</b></td>
<td><b>161</b></td>
<td><b>74.39</b></td>
<td><b>92.09</b></td>
<td><b>2.46</b></td>
</tr>
<tr>
<td><b>PP-LCNet-2.5x*</b></td>
<td><b>9.0</b></td>
<td><b>906</b></td>
<td><b>80.82</b></td>
<td><b>95.33</b></td>
<td><b>5.39</b></td>
</tr>
</tbody>
</table>

Table 2. Indicators of PP-LCNet of different scales, where \* means it is trained using SSLD[28] distillation method. Latency tested on Intel® Xeon® Gold 6148 Processor with batch size of 1 and MKLDNN enabled, the number of thread is 10.

<table border="1">
<thead>
<tr>
<th>Model</th>
<th>Params(M)</th>
<th>FLOPs(M)</th>
<th>Top-1 Acc.(%)</th>
<th>Top-5 Acc.(%)</th>
<th>Latency(ms)</th>
</tr>
</thead>
<tbody>
<tr>
<td>MobileNetV2-0.25x</td>
<td>1.5</td>
<td>34</td>
<td>53.21</td>
<td>76.52</td>
<td>2.47</td>
</tr>
<tr>
<td>MobileNetV3-small-0.35x</td>
<td>1.7</td>
<td>15</td>
<td>53.03</td>
<td>76.37</td>
<td>3.02</td>
</tr>
<tr>
<td>ShuffleNetV2-0.33x</td>
<td>0.6</td>
<td>24</td>
<td>53.73</td>
<td>77.05</td>
<td>4.30</td>
</tr>
<tr>
<td><b>PP-LCNet-0.25x</b></td>
<td><b>1.5</b></td>
<td><b>18</b></td>
<td><b>51.86</b></td>
<td><b>75.65</b></td>
<td><b>1.74</b></td>
</tr>
<tr>
<td>MobileNetV2-0.5x</td>
<td>2.0</td>
<td>99</td>
<td>65.03</td>
<td>85.72</td>
<td>2.85</td>
</tr>
<tr>
<td>MobileNetV3-large-0.35x</td>
<td>2.1</td>
<td>41</td>
<td>64.32</td>
<td>85.46</td>
<td>3.68</td>
</tr>
<tr>
<td>ShuffleNetV2-0.5x</td>
<td>1.4</td>
<td>43</td>
<td>60.32</td>
<td>82.26</td>
<td>4.65</td>
</tr>
<tr>
<td><b>PP-LCNet-0.5x</b></td>
<td><b>1.9</b></td>
<td><b>47</b></td>
<td><b>63.14</b></td>
<td><b>84.66</b></td>
<td><b>2.05</b></td>
</tr>
<tr>
<td>MobileNetV1-1x</td>
<td>4.3</td>
<td>578</td>
<td>70.99</td>
<td>89.68</td>
<td>3.38</td>
</tr>
<tr>
<td>MobileNetV2-1x</td>
<td>3.5</td>
<td>327</td>
<td>72.15</td>
<td>90.65</td>
<td>4.26</td>
</tr>
<tr>
<td>MobileNetV3-small-1.25x</td>
<td>3.6</td>
<td>100</td>
<td>70.67</td>
<td>89.51</td>
<td>3.95</td>
</tr>
<tr>
<td>ShuffleNetV2-1.5x</td>
<td>3.5</td>
<td>301</td>
<td>71.63</td>
<td>90.15</td>
<td>-</td>
</tr>
<tr>
<td><b>PP-LCNet-1x</b></td>
<td><b>3.0</b></td>
<td><b>161</b></td>
<td><b>71.32</b></td>
<td><b>90.03</b></td>
<td><b>2.46</b></td>
</tr>
</tbody>
</table>

Table 3. Comparison of state-of-the-art light networks over classification accuracy. Latency tested on Intel® Xeon® Gold 6148 Processor with batch size of 1 and MKLDNN enabled, the number of thread is 10.

### 3.4. Larger dimensional $1 \times 1$ conv layer after GAP

In our PP-LCNet, the output dimension of the network after GAP is small. And directly appending the final classification layer will lose the combination of features. In order to give the network a stronger fitting ability, we appended a 1280-dimensional size  $1 \times 1$  conv(equivalent to FC layer) after the final GAP layer, which would allow for more storage of the model with little increase of inference time.

With these four changes, our model performs well on the ImageNet-1k[27], and table 3 lists the metrics against other lightweight models on Intel CPUs.

## 4. Experiment

### 4.1. Implementation Details

For fair comparisons, we reimplement the models of MobileNetV1[14], MobileNetV2[15], MobileNetV3[20],

ShuffleNetV2[17], PicoDet[29] and Deeplabv3+[8] by PaddlePaddle. We train the models on 4 V100 GPUs, and the CPU test environment is based on Intel® Xeon® Gold 6148 Processor with batch size of 1 and MKLDNN enabled.

### 4.2. Image Classification

For the image classification task, we train PP-LCNet on ImageNet-1k[27], which contains 1.28 million training images and 50k validation images of 1000 classes. We use SGD optimizer with weight decay set to  $3e-5$  ( $4e-5$  for large models), momentum set to 0.9, and batch size of 2048. Learning rate is adjusted according to a cosine schedule for training 360 epochs with 5 linear warmup epochs. Initial learning rate is set to 0.8. In the training phase, each image is randomly cropped to  $224 \times 224$  and randomly flipped horizontally. In the evaluation phase, we first resize an image to 256 along the short edge, then apply a center cropof size  $224 \times 224$ . Table 2 shows the PP-LCNet’s top-1 and top-5 validation accuracy and inference time of different scales. Furthermore, when the SSLD[28] distillation method is used, the accuracy of the model can be greatly improved. Table 3 shows the comparison of PP-LCNet and state-of-the-art models. Compared with other light models, PP-LCNet has shown strong competitiveness.

### 4.3. Object Detection

For object detection task, all models in Table 4 are trained on COCO-2017[30] training set with 80 classes and 118k images, and evaluated on COCO-2017[30] validation set with 5000 images using the common COCO AP metric of a single scale. We used the lightweight PicoDet developed by PaddleDecton<sup>3</sup> as our baseline method. Table 4 shows the object detection results of PP-LCNet and MobileNetV3[20] as the backbone. The entire network is trained with stochastic gradient descent (SGD) for 146K iterations with a minibatch of 224 images distributed on 4 GPUs. The learning rate schedule is cosine from 0.3 as base learning rate for 280 epochs. Weight decay is set as  $1e-4$ , and momentum is set as 0.9. Impressively, the PP-LCNet backbone greatly improves the mAP on COCO[30] and inference speed compared with MobileNetV3[20].

<table border="1">
<thead>
<tr>
<th>Method</th>
<th>Backbone</th>
<th>mAP (%)</th>
<th>Latency (ms)</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="4">PicoDet</td>
<td>MobileNetV3-large-0.35x[20]</td>
<td>19.2</td>
<td>8.1</td>
</tr>
<tr>
<td><b>PP-LCNet-0.5x</b></td>
<td><b>20.3</b></td>
<td><b>6.0</b></td>
</tr>
<tr>
<td>MobileNetV3-large-0.75x[20]</td>
<td>25.8</td>
<td>11.1</td>
</tr>
<tr>
<td><b>PP-LCNet-1x</b></td>
<td><b>26.9</b></td>
<td><b>7.9</b></td>
</tr>
</tbody>
</table>

Table 4. Object detection results on the COCO dataset[30], measured using  $mAP@IoU=0.5:0.95$  (%). Latency tested on Intel<sup>®</sup> Xeon<sup>®</sup> Gold 6148 Processor with batch size of 1 and MKLDNN enabled, the number of thread is 10.

### 4.4. Semantic Segmentation

For the semantic segmentation task, we also evaluate the ability of PP-LCNet on Cityscapes dataset[31], which contains 5000 high-quality labeled images. We use the Deeplabv3+[8] developed by PaddleSeg<sup>4</sup> as our baseline method, and set the output stride to 32. The data are augmented by randomly horizontally flip, randomly scale, and randomly crop. The random scales contain  $\{0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0\}$ , and the cropped resolutions are  $1024 \times 512$ . We use the SGD optimizer with the initial learning rate of 0.01, the momentum of 0.9, and the weight decay of  $4e-5$ . We use a poly learning rate sched-

ule with a power of 0.9. All the models are trained for 80K iterations with the batch-size of 32 on 4 V100 GPUs.

We use MobileNetV3[20] as backbone for comparison. As shown in Table 5, PP-LCNet-0.5x outperforms MobileNetV3-large-0.5x[20] by 2.94% on mIoU, but the inference time is reduced by 53ms. Compared with larger models, PP-LCNet also has strong performance. When PP-LCNet-1x is used as backbone, mIOU of model is 1.5% higher than MobileNetV3-large-0.75x, but the inference time is reduced by 55ms.

<table border="1">
<thead>
<tr>
<th>Method</th>
<th>Backbone</th>
<th>mIoU (%)</th>
<th>Latency (ms)</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="4">Deeplabv3+[8]</td>
<td>MobileNetV3-large-0.5x[20]</td>
<td>55.42</td>
<td>135</td>
</tr>
<tr>
<td><b>PP-LCNet-0.5x</b></td>
<td><b>58.36</b></td>
<td><b>82</b></td>
</tr>
<tr>
<td>MobileNetV3-large-0.75x[20]</td>
<td>64.53</td>
<td>151</td>
</tr>
<tr>
<td><b>PP-LCNet-1x</b></td>
<td><b>66.03</b></td>
<td><b>96</b></td>
</tr>
</tbody>
</table>

Table 5. Performances of semantic segmentation on Cityscapes[31] validation dataset. Latency tested on Intel<sup>®</sup> Xeon<sup>®</sup> Gold 6148 Processor with batch size of 1 and MKLDNN enabled, the number of thread is 10.

### 4.5. Ablation Study

**The impact of SE module[26] in different positions.** The SE module[26] is an attention mechanism between channels, which can improve the accuracy of the model. However, if the number of SE modules[26] is blindly increased, the inference speed of the model will be reduced, so it is worth studying and exploring how to properly add SE modules[26] to the model. Through experiments, we found that the SE module[26] will have a greater impact on the tail of the network. The results of adding only two SE modules[26] at different locations in the network are presented in the table 7. The table clearly shows that adding the last two blocks is more advantageous for almost the same inference time. Therefore, in order to balance the inference speed, PP-LCNet only adds the SE module[26] to the last two blocks.

**The impact of large-kernel in different locations.** Although large-kernel can increase accuracy, it is not the best to add it at all locations in the network. We have shown the general rule of correctly adding large-kernel through experiments. Table 8 shows the positions added by the  $5 \times 5$  depth-wise convolution. 1 means that the depth-wise convolution kernel in DepthSepConv is  $5 \times 5$ , and 0 means that the depth-wise convolution kernel in DepthSepConv is  $3 \times 3$ . It can be seen from the table that, similar to the location where the SE module[26] is added, the addition of  $5 \times 5$  convolution at the tail of the network is also more competi-

<sup>3</sup><https://github.com/PaddlePaddle/PaddleDetection>

<sup>4</sup><https://github.com/PaddlePaddle/PaddleSeg><table border="1">
<thead>
<tr>
<th>Activation</th>
<th>SE block</th>
<th>large-kernel</th>
<th>last-1x1 conv</th>
<th>Top-1 Acc(%)</th>
<th>Latency(ms)</th>
</tr>
</thead>
<tbody>
<tr>
<td>✗</td>
<td>✓</td>
<td>✓</td>
<td>✓</td>
<td>61.93</td>
<td>1.94</td>
</tr>
<tr>
<td>✓</td>
<td>✗</td>
<td>✓</td>
<td>✓</td>
<td>62.51</td>
<td>1.87</td>
</tr>
<tr>
<td>✓</td>
<td>✓</td>
<td>✗</td>
<td>✓</td>
<td>62.44</td>
<td>2.01</td>
</tr>
<tr>
<td>✓</td>
<td>✓</td>
<td>✓</td>
<td>✗</td>
<td>59.91</td>
<td>1.85</td>
</tr>
<tr>
<td>✓</td>
<td>✓</td>
<td>✓</td>
<td>✓</td>
<td>63.14</td>
<td>2.05</td>
</tr>
</tbody>
</table>

Table 6. The impact of PP-LCNet-0.5x’s performance on reducing a certain technology. Latency tested on Intel® Xeon® Gold 6148 Processor with batch size of 1 and MKLDNN enabled, the number of thread is 10.

<table border="1">
<thead>
<tr>
<th>Network</th>
<th>SE Location</th>
<th>Top-1 Acc (%)</th>
<th>Latency (ms)</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="4">PP-LCNet-0.5x</td>
<td>11000000000000</td>
<td>61.73</td>
<td>2.06</td>
</tr>
<tr>
<td>00000011000000</td>
<td>62.17</td>
<td>2.03</td>
</tr>
<tr>
<td><b>0000000000011</b></td>
<td><b>63.14</b></td>
<td><b>2.05</b></td>
</tr>
<tr>
<td>11111111111111</td>
<td>64.27</td>
<td>3.80</td>
</tr>
</tbody>
</table>

Table 7. Ablation experiment of SE module in different positions. Latency tested on Intel® Xeon® Gold 6148 Processor with batch size of 1 and MKLDNN enabled, the number of thread is 10.

tive. Our PP-LCNet chose the configuration in the third row of the table.

<table border="1">
<thead>
<tr>
<th>Network</th>
<th>Large-kernel location</th>
<th>Top-1 Acc (%)</th>
<th>Latency (ms)</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="3">PP-LCNet-0.5x</td>
<td>11111111111111</td>
<td>63.22</td>
<td>2.08</td>
</tr>
<tr>
<td>11111110000000</td>
<td>62.70</td>
<td>2.07</td>
</tr>
<tr>
<td><b>00000011111111</b></td>
<td><b>63.14</b></td>
<td><b>2.05</b></td>
</tr>
</tbody>
</table>

Table 8. The impact of large-kernel in different locations. Latency tested on Intel® Xeon® Gold 6148 Processor with batch size of 1 and MKLDNN enabled, the number of thread is 10.

**The impact of different techniques.** In PP-LCNet, we use 4 different technologies to improve the performance of the model. Table 9 lists the cumulative increase of different technologies on PP-LCNet, and Table 6 lists the impact of reducing different modules on PP-LCNet. It can be seen from the two tables that H-Swish and large-kernel can improve the performance of the model with almost no increase in inference time. Adding a small number of SE modules[26] can further improve the performance of the model. Using a larger FC layer after GAP will also greatly increase the accuracy. At the same time, perhaps because a relatively large matrix is involved here, the use of the dropout strategy can further improve the accuracy of the model.

<table border="1">
<thead>
<tr>
<th>Strategy</th>
<th>Top-1 Acc.(%)</th>
<th>Latency(ms)</th>
</tr>
</thead>
<tbody>
<tr>
<td>BaseNet</td>
<td>55.58</td>
<td>1.61</td>
</tr>
<tr>
<td>+h-swish</td>
<td>58.18</td>
<td>1.66</td>
</tr>
<tr>
<td>+large-kernel</td>
<td>59.09</td>
<td>1.70</td>
</tr>
<tr>
<td>+SE</td>
<td>59.91</td>
<td>1.85</td>
</tr>
<tr>
<td>+last-1x1 conv w/o dropout</td>
<td>62.50</td>
<td>2.05</td>
</tr>
<tr>
<td><b>+last-1x1 conv w/ dropout</b></td>
<td><b>63.14</b></td>
<td><b>2.05</b></td>
</tr>
</tbody>
</table>

Table 9. The impact of the increase of different technologies on the performance of PP-LCNet-0.5x. Latency tested on Intel® Xeon® Gold 6148 Processor with batch size of 1 and MKLDNN enabled, the number of thread is 10.

## 5. Conclusion and Future work

Our work summarizes some methods for designing lightweight Intel CPU networks, which can improve the accuracy of the model while avoiding increasing the inference time. While these methods are existing methods from previous work, the balance between accuracy and speed has not been summarised experimentally. Through extensive experiments and blessing of these methods, we propose PP-LCNet, which shows stronger performance on a large number of vision tasks and has a better accuracy-speed balance. In addition, this work reduces the search space of NAS and also offers the possibility of faster access to lightweight models for NAS. In the future, we will also use NAS to obtain faster and stronger models.

## References

1. [1] Alex Krizhevsky, Ilya Sutskever, and Geoffrey E Hinton. Imagenet classification with deep convolutional neural networks. In *Advances in neural information processing systems*, pages 1097–1105, 2012. 1
2. [2] Jia Li, Yafei Song, Jianfeng Zhu, Lele Cheng, Ying Su, Lin Ye, Pengcheng Yuan, and Shumin Han. Learning from large-scale noisy web data with ubiquitous reweighting for image classification. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 2019. 1
3. [3] Shaoqing Ren, Kaiming He, Ross Girshick, and Jian Sun. Faster r-cnn: Towards real-time object detection with regionproposal networks. In *Advances in neural information processing systems*, pages 91–99, 2015. [1](#)

[4] Ramprasaath R Selvaraju, Michael Cogswell, Abhishek Das, Ramakrishna Vedantam, Devi Parikh, and Dhruv Batra. Grad-cam: Visual explanations from deep networks via gradient-based localization. In *Proceedings of the IEEE international conference on computer vision*, pages 618–626, 2017. [1](#)

[5] Tianzhu Zhang, Changsheng Xu, and Ming-Hsuan Yang. Multi-task correlation particle filter for robust object tracking. In *Proceedings of the IEEE conference on computer vision and pattern recognition*, pages 4335–4343, 2017. [1](#)

[6] Karen Simonyan and Andrew Zisserman. Two-stream convolutional networks for action recognition in videos. In *Advances in neural information processing systems*, pages 568–576, 2014. [1](#)

[7] Liang-Chieh Chen, George Papandreou, Iasonas Kokkinos, Kevin Murphy, and Alan L Yuille. Deeplab: Semantic image segmentation with deep convolutional nets, atrous convolution, and fully connected crfs. *IEEE transactions on pattern analysis and machine intelligence*, 40(4):834–848, 2017. [1](#)

[8] Liang-Chieh Chen, George Papandreou, Florian Schroff, and Hartwig Adam. Rethinking atrous convolution for semantic image segmentation. *arXiv preprint arXiv:1706.05587*, 2017. [1](#), [4](#), [5](#)

[9] Ali Borji, Ming-Ming Cheng, Qibin Hou, Huaizu Jiang, and Jia Li. Salient object detection: A survey. *Computational visual media*, pages 1–34, 2019. [1](#)

[10] Yun Liu, Ming-Ming Cheng, Xiaowei Hu, Kai Wang, and Xiang Bai. Richer convolutional features for edge detection. In *Proceedings of the IEEE conference on computer vision and pattern recognition*, pages 3000–3009, 2017. [1](#)

[11] Barret Zoph and Quoc V Le. Neural architecture search with reinforcement learning. *arXiv preprint arXiv:1611.01578*, 2016. [2](#)

[12] Karen Simonyan and Andrew Zisserman. Very deep convolutional networks for large-scale image recognition. *arXiv preprint arXiv:1409.1556*, 2014. [2](#)

[13] Christian Szegedy, Wei Liu, Yangqing Jia, Pierre Sermanet, Scott Reed, Dragomir Anguelov, Dumitru Erhan, Vincent Vanhoucke, and Andrew Rabinovich. Going deeper with convolutions. In *Proceedings of the IEEE conference on computer vision and pattern recognition*, pages 1–9, 2015. [2](#)

[14] Andrew G Howard, Menglong Zhu, Bo Chen, Dmitry Kalenichenko, Weijun Wang, Tobias Weyand, Marco Andreetto, and Hartwig Adam. Mobilenets: Efficient convolutional neural networks for mobile vision applications. *arXiv preprint arXiv:1704.04861*, 2017. [2](#), [3](#), [4](#)

[15] Mark Sandler, Andrew Howard, Menglong Zhu, Andrey Zhmoginov, and Liang-Chieh Chen. Mobilenetv2: Inverted residuals and linear bottlenecks. In *Proceedings of the IEEE conference on computer vision and pattern recognition*, pages 4510–4520, 2018. [2](#), [4](#)

[16] Xiangyu Zhang, Xinyu Zhou, Mengxiao Lin, and Jian Sun. Shufflenet: An extremely efficient convolutional neural network for mobile devices. In *Proceedings of the IEEE conference on computer vision and pattern recognition*, pages 6848–6856, 2018. [2](#)

[17] Ningning Ma, Xiangyu Zhang, Hai-Tao Zheng, and Jian Sun. Shufflenet v2: Practical guidelines for efficient cnn architecture design. In *Proceedings of the European conference on computer vision (ECCV)*, pages 116–131, 2018. [2](#), [4](#)

[18] Kai Han, Yunhe Wang, Qi Tian, Jianyuan Guo, Chunjing Xu, and Chang Xu. Ghostnet: More features from cheap operations. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 1580–1589, 2020. [2](#)

[19] Mingxing Tan and Quoc V Le. Efficientnet: Rethinking model scaling for convolutional neural networks. *arXiv preprint arXiv:1905.11946*, 2019. [2](#), [3](#)

[20] Andrew Howard, Mark Sandler, Grace Chu, Liang-Chieh Chen, Bo Chen, Mingxing Tan, Weijun Wang, Yukun Zhu, Ruoming Pang, Vijay Vasudevan, et al. Searching for mobilenetv3. In *Proceedings of the IEEE International Conference on Computer Vision*, pages 1314–1324, 2019. [2](#), [3](#), [4](#), [5](#)

[21] Bichen Wu, Xiaoliang Dai, Peizhao Zhang, Yanghan Wang, Fei Sun, Yiming Wu, Yuandong Tian, Peter Vajda, Yangqing Jia, and Kurt Keutzer. Fbnet: Hardware-aware efficient convnet design via differentiable neural architecture search. In *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition*, pages 10734–10742, 2019. [2](#)

[22] Changlin Li, Jiefeng Peng, Liuchun Yuan, Guangrun Wang, Xiaodan Liang, Liang Lin, and Xiaojun Chang. Blockwisely supervised neural architecture search with knowledge distillation. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 1989–1998, 2020. [2](#)

[23] Han Cai, Chuang Gan, Tianzhe Wang, Zhekai Zhang, and Song Han. Once-for-all: Train one network and specialize it for efficient deployment. *arXiv preprint arXiv:1908.09791*, 2019. [2](#)

[24] Mingxing Tan and Quoc V Le. Mixconv: Mixed depthwise convolutional kernels. *arXiv preprint arXiv:1907.09595*, 2019. [2](#), [3](#)

[25] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In *Proceedings of the IEEE conference on computer vision and pattern recognition*, pages 770–778, 2016. [2](#)

[26] Jie Hu, Li Shen, and Gang Sun. Squeeze-and-excitation networks. In *Proceedings of the IEEE conference on computer vision and pattern recognition*, pages 7132–7141, 2018. [3](#), [5](#), [6](#)

[27] Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li, and Li Fei-Fei. Imagenet: A large-scale hierarchical image database. In *2009 IEEE conference on computer vision and pattern recognition*, pages 248–255. Ieee, 2009. [3](#), [4](#)- [28] Cheng Cui, Ruoyu Guo, Yuning Du, Dongliang He, Fu Li, Zewu Wu, Qiwen Liu, Shilei Wen, Jizhou Huang, Xiaoguang Hu, et al. Beyond self-supervision: A simple yet effective network distillation alternative to improve backbones. *arXiv preprint arXiv:2103.05959*, 2021. [4](#), [5](#)
- [29] PaddlePaddle Authors. Paddledetection, object detection and instance segmentation toolkit based on paddlepaddle. <https://github.com/PaddlePaddle/PaddleDetection>, 2019. [4](#)
- [30] Tsung-Yi Lin, Michael Maire, Serge Belongie, James Hays, Pietro Perona, Deva Ramanan, Piotr Dollár, and C Lawrence Zitnick. Microsoft coco: Common objects in context. In *European conference on computer vision*, pages 740–755. Springer, 2014. [5](#)
- [31] Marius Cordts, Mohamed Omran, Sebastian Ramos, Timo Rehfeld, Markus Enzweiler, Rodrigo Benenson, Uwe Franke, Stefan Roth, and Bernt Schiele. The cityscapes dataset for semantic urban scene understanding. In *Proceedings of the IEEE conference on computer vision and pattern recognition*, pages 3213–3223, 2016. [5](#)


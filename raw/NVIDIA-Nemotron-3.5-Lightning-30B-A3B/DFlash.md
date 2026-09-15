---
pipeline_tag: text-generation
base_model:
- nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16
- nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4
license: other
license_name: openmdw-1.1
license_link: https://openmdw.ai/license/1-1/
library_name: Model Optimizer
tags:
- nvidia
- ModelOpt
- Nemotron-3.5-Lightning
- latent-moe
- mtp
- DFlash
---

# Model Overview

## Description:

The NVIDIA Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash model is the DFlash speculative decoding checkpoint for NVIDIA's Nemotron-3.5-Lightning-30B-A3B model family, which is a hybrid LatentMoE language model designed for reasoning, chat, and agentic workflows. For more information, please check [BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16), [NVFP4](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4). The NVIDIA Nemotron-3.5-Lightning-30B-A3B-DFlash-NVFP4 model is intended for lower-latency speculative decoding deployments tuned for low-concurrency data centre and workstation workflows.

This model is ready for commercial or non-commercial use.

## License/Terms of Use:
**GOVERNING DOWNLOAD TERMS:** Use of this model is governed by the [OpenMDW-1.1 model license](https://openmdw.ai/license/1-1/).

## Deployment Geography:
Global


## Use Case:
Developers deploying Nemotron-3.5-Lightning-30B-A3B for reasoning, chat, RAG, and agentic workflows that benefit from lower-latency speculative decoding on data centre GPUs and high-end local GPU systems. This release is intended for DFlash-assisted serving of Nemotron-3.5-Lightning-30B-A3B rather than as a standalone target model checkpoint.

## Release Date:

Hugging Face 08/11/2026 via [https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash)


## References
- NVIDIA Model Optimizer: https://github.com/NVIDIA/Model-Optimizer
- [NVIDIA Nemotron-3.5-Lightning-30B-A3B-BF16 reasoning model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16)
- [NVIDIA Nemotron-3.5-Lightning-30B-A3B-NVFP4 reasoning model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4)
- [OpenMDW License Agreement, version 1.1](https://openmdw.ai/license/1-1/)
- [DFlash: Block Diffusion for Flash Speculative Decoding](https://huggingface.co/papers/2602.06036)

## Model Architecture:

The DFlash model architecture is as follows:

**Architecture Type:** Dense GQA (Dense MLP + GQA Attention)  
**Network Architecture:** Dense FFN MLP, and GQA Attention layers; DFlash speculative decoding attention uses non-causal, full-sequence grouped-query attention (GQA).
**Number of Model Parameters:** 833M total parameters, of which 481M are non-embedding parameters.

For more information about the underlying model's architecture, please see this [Nemotron-3.5-Lightning-30B-A3B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16), [Nemotron-3.5-Lightning-30B-A3B-NVFP4](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4).

## Input:

**Input Type(s):** Text  
**Input Format(s):** String  
**Input Parameters:** One-Dimensional (1D): Sequences  
**Other Properties Related to Input:** Maximum context length up to 1M tokens. Supported languages include English, Spanish, French, German, Italian, and Japanese.  

## Output:

**Output Type(s):** Text  
**Output Format:** String  
**Output Parameters:** One-Dimensional (1D): Sequences  
**Other Properties Related to Output:** Outputs may include natural-language responses, reasoning traces, tool-use content, and structured outputs depending on chat-template configuration and application-level tooling.  

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA's hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions.

## Software Integration:

**Supported Runtime Engine(s):**
- vLLM
- llama.cpp

**Supported Hardware Microarchitecture Compatibility:**
- NVIDIA Blackwell GB200

**Preferred Operating System(s):**
- Linux

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment.

## Model Version(s):

The model is a Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash speculative decoding version of the model and quantized with **Model Optimizer 0.45.0 version**


## Training and Evaluation Datasets:

## Training Dataset:
For more information about the underlying Nemotron-3.5-Lightning-30B-A3B model, please visit the model card - [Nemotron-3.5-Lightning-30B-A3B-NVFP4](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4), [Nemotron-3.5-Lightning-30B-A3B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16).

**Link**: [Nemotron-Post-Training-Dataset-v2](https://huggingface.co/datasets/nvidia/Nemotron-Post-Training-Dataset-v2), and [Nemotron-Post-Training-Dataset-v3](https://huggingface.co/collections/nvidia/nemotron-post-training-v3) only prompts from the datasets were used for data synthesis, (the original responses from GPT were not used), which is then used to train the DFlash modules.  
**Data Modality:** Text  
**Text Training Data Size:** 66 Billion Tokens, repeated for 2 epochs  
**Data Collection Method by dataset:** Hybrid: Automated, manually-collected, Synthetic  
**Labeling Method by dataset:** Hybrid: Automated, manually-labelled, Synthetic  
**Properties:** The Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash model was trained exclusively on a post-training corpus includes synthetic data for reasoning, code, science, tool use, instruction following, structured outputs, and multilingual tasks. Dataset disclosures are published in the `nvidia/nemotron-post-training-dataset-v2` and `nvidia/nemotron-post-training-v3` Hugging Face collections. <br>

## Evaluation Dataset:

The model is evaluated on the [SPEED-Bench](https://huggingface.co/datasets/nvidia/SPEED-Bench) dataset for speculative decoding benchmarking.

**Data Collection Method by dataset:** Hybrid: Automated, manually-collected, Synthetic  
**Labeling Method by dataset:** Hybrid: Automated, manually-labelled, Synthetic  
**Properties:** This corpus comprises a mix of high-quality standard benchmarks and test suites for LLMs. These benchmarks prompt the underlying model on a diverse set of tasks such as coding, math, writing, translation, etc., and the acceptance rates achieved from speculative decoding over the responses are measured in order to evaluate the quality of the speculation model.

## Inference:

**Acceleration Engine:** vLLM, llama.cpp  
**Test Hardware:** NVIDIA Hopper - H100; NVIDIA Blackwell - GB200; NVIDIA Blackwell - GeForce RTX 5090  

## DFlash Speculative Decoding

Nemotron-3.5-Lightning-30B-A3B supports multiple speculative decoding paths, including native MTP, DFlash, and DSpark for DGX Spark and low-concurrency data centre workflows. This release is the DFlash speculative decoding checkpoint intended to be paired with the Nemotron-3.5-Lightning-30B-A3B target model in vLLM or llama.cpp. DFlash is designed to reduce end-to-end latency for small-batch or single-request serving by drafting more than one candidate token per target-model verification step.

## Usage

To serve the checkpoint with [vLLM](https://github.com/vllm-project/vllm), refer to the DFlash recipes in the [NVIDIA Nemotron-3.5-Lightning-30B-A3B Model Card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4#1x-dgx-spark-gb10).

For local workflows, the Model Card also includes recipes for deployment with llama.cpp on NVIDIA Blackwell - GeForce RTX 5090.

## Evaluation

Acceptance rate on [SPEED-Bench](https://huggingface.co/datasets/nvidia/SPEED-Bench) with draft length 7:

| Category            | SPEED-Bench Acceptance Length |
| ------------------- | ------------: |
| coding              | **3.64** |
| humanities          | **2.72** |
| math                | **3.52** |
| multilingual        | **3.75** |
| qa                  | **2.84** |
| rag                 | **3.60** |
| reasoning           | **3.28** |
| roleplay            | **2.60** |
| stem                | **2.91** |
| summarization       | **3.38** |
| writing             | **2.49** |
| **Overall Average** | **3.16** |

> Baseline: [NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16)
> Benchmarked with `temperature=1.0`, `top_p=0.95`.

## Model Limitations:

The base model may generate inaccurate, incomplete, or otherwise undesirable responses, even when prompts are benign. It may reflect biases or content artifacts present in its training data, and output quality can vary by domain, language, reasoning depth, and context length. Developers should add application-specific safeguards and evaluate the system in the intended deployment environment before production use.

## Ethical Considerations

NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications. Developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.

For more detailed information on ethical considerations for this model, please see the Model Card++ Bias, Explainability, Safety & Security, and Privacy Subcards.

Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).

SUBCARDS:

# **Explainability**

| Field | Response |
| --- | --- |
| Intended Task/Domain | Text generation, reasoning, tool use, and agentic workflows accelerated with speculative decoding |
| Model Type | Hybrid LatentMoE language model used with a DFlash draft checkpoint |
| Intended Users | Developers deploying Nemotron-3.5-Lightning-30B-A3B for reasoning, chat, RAG, and agentic workflows that benefit from lower-latency speculative decoding on data centre GPUs and high-end local GPU systems. |
| Output | Text string(s) |
| Describe how the model works | NVIDIA-Nemotron-3.5-Lightning-30B-A3B uses interleaved Mamba-2, MoE, and Attention layers for the target model, while DFlash proposes candidate token blocks to improve generation speed during verification |
| Name the adversely impacted groups this has been tested to deliver comparable outcomes regardless of | Not Applicable |
| Technical Limitations & Mitigation | The speculative decoding model does not affect the output distribution of the underlying reasoning model. It is only used for lossless inference acceleration. |
| Verified to have met prescribed quality standards? | Yes |
| Performance Metrics | Accuracy, throughput, latency, and speculative-decoding acceptance rate |
| Potential Known Risk | The base model was trained on data that contains toxic language and societal biases originally crawled from the internet. Therefore, the model may amplify those biases and return toxic responses especially when prompted with toxic prompts. Therefore, before deploying any applications of this model, developers should perform safety testing and tuning tailored to their specific applications of the model.
Developers should validate task accuracy, latency, and safety in their own deployment environment and add application-specific safeguards before production use.  |
| Licensing | **Governing Terms:** Use of this model is governed by the [OpenMDW-1.1 model license](https://openmdw.ai/license/1-1/) |



# **Bias**

| Field | Response |
| --- | --- |
| Participation considerations from adversely impacted groups [protected classes](https://www.senate.ca.gov/content/protected-classes) in model design and testing | None |
| Measures taken to mitigate against unwanted bias | None |
| Bias Metric | None |

# **Safety & Security**

| Field | Response |
| --- | --- |
| Model Application(s) | Chat, instruction following, RAG, reasoning, and agentic AI workflows |
| Describe life critical application (if present) | Not Applicable |
| Use Case Restrictions | Use must comply with the [OpenMDW-1.1 model license](https://openmdw.ai/license/1-1/) and applicable laws and regulations |
| Model and Dataset Restrictions | The Principle of least privilege (PoLP) is applied limiting access for dataset generation and model development. Restrictions enforce dataset access during training, and dataset license constraints adhered to.|

# **Privacy**

| Field | Response |
| --- | --- |
| Generatable or Reverse engineerable personal data? | No |
| Personal data used to create this model? | No |
| Was consent obtained for any personal data used? | Not Applicable |
| How often is dataset reviewed? | Before Release |
| Was data from user interactions with the AI model (e.g. user input and prompts) used to train the model? | No |
| Is there provenance for all datasets used in training? | Yes |
| Does data labeling (annotation, metadata) comply with privacy laws? | Yes |
| Is data compliant with data subject requests for data correction or removal, if such a request was made? | Not Applicable |
| Applicable NVIDIA Privacy Policy | [https://www.nvidia.com/en-us/about-nvidia/privacy-policy/](https://www.nvidia.com/en-us/about-nvidia/privacy-policy/) |

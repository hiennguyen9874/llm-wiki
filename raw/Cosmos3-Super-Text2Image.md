---
license: other
license_name: openmdw1.1-license
license_link: >-
  https://openmdw.ai/license/1-1/
library_name: cosmos
tags:
  - nvidia
  - cosmos
  - cosmos3
  - vllm-omni
  - sglang
  - sglang-diffusion
  - diffusers
  - text-to-image
  - image-generation
---

# **Cosmos 3: Omnimodal World Models for Physical AI**
**[Model Collection](https://huggingface.co/collections/nvidia/cosmos3)** | **[Code](https://github.com/nvidia/cosmos)** | **[White Paper](https://research.nvidia.com/labs/cosmos-lab/cosmos3/technical-report.pdf)** | **[Website](https://research.nvidia.com/labs/cosmos-lab/cosmos3/)**

[NVIDIA Cosmos™](https://github.com/nvidia/cosmos) is a world foundation model platform designed to accelerate the development of Physical AI by enabling machines to understand, simulate, and interact with the physical world across robotics, autonomous driving, and smart space environments, including industrial and factory-scale applications.

# Model Overview: Cosmos3-Super-Text2Image

## Description

Cosmos3 is a collection of Omnimodal world models capable of generating dynamic, high-quality video, image, audio, and action commands from combinations of text, image, video, and action trajectory inputs. It serves as a foundational building block for a broad range of Physical AI applications and research spanning world understanding, world generation, simulation, and embodied policy learning.

This model is ready for commercial and non-commercial use.

**Model Developer:** NVIDIA

### Model Versions
- Cosmos3-Super-Text2Image:
  - Given text input, generate high-fidelity images that are consistent with the provided description.

### License

This model is released under the [OpenMDW1.1](https://openmdw.ai/license/1-1/)

### Deployment Geography

Global

### Use Case

Physical AI: Encompassing robotics, autonomous vehicles (AV), and smart space environments, including industrial and factory-scale applications.

### Release Date

Hugging Face 05/31/2026 via [https://huggingface.co/collections/nvidia/cosmos3](https://huggingface.co/collections/nvidia/cosmos3)
GitHub 05/31/2026 via [https://github.com/nvidia/cosmos](https://github.com/nvidia/cosmos)

## Model Architecture

**Architecture Type:** Transformer

**Network Architecture:** Mixture-of-Transformers (MoT)

Cosmos3 is an Omni-modal foundation model built on a Mixture-of-Transformers (MoT) architecture consisting of two complementary transformer towers: an autoregressive transformer for discrete token generation and a diffusion transformer for continuous multimodal generation. During inference, text is generated through standard next-token autoregressive decoding, while non-text modalities, such as images, video, audio, and actions, are synthesized through iterative denoising. This unified architecture enables Cosmos3 to model heterogeneous modalities within a single framework while preserving generation mechanisms best suited to each modality.

**This model was developed based on:**  [Cosmos Framework](https://github.com/nvidia/cosmos-framework)

**Number of trainable model parameters:**

- Cosmos3-Super-Text2Image: 64B

## Input/Output Specifications

- **Generator Input**
  - **Input Type(s)**: Text, Image, Video (with audio or without audio), Action Trajectory
  - **Input Format(s)**:
    - Text: String
    - Image: jpg, png, jpeg, webp
    - Video (with or without audio): mp4
    - Action: json (1D list)
  - **Input Parameters**:
    - Text: One-dimensional (1D)
    - Image: Two-dimensional (2D)
    - Video: Three-dimensional (3D)
    - Audio: One-dimensional (1D)
    - Action trajectory: One-dimensional (1D)
  - **Other Properties Related to Input**:
    - For video inputs, we accept various resolutions, including 720p, 480p, and 256p.
    - When using input video with audio muxed into the video MP4 file, the audio should have 2 channels (stereo) and a 48 kHz sample rate.
    - Image and video inputs are RGB color (8 bits per channel, sRGB color space); grayscale inputs are not supported.
    - Action input is a per-frame sequence of robot/agent state or control values (e.g., joint positions, gripper state, camera pose). The full input is a 2D array shaped (T, D), where T is the number of frames and D is the embodiment-specific dimensionality listed below.
    - Input action is only supported for compatible embodiments, including general camera motion (9D), autonomous vehicle (9D), egocentric motion (57D), single Franka Panda arm with RobotiQ gripper (10D), dual Franka Panda arm with RobotiQ gripper (20D), Agibot (29D), UR (10D), Google robot (10D), WidowX 250 (10D), UMI (9D).
  - **Input Size and Length limits:**
    - **Text:** 4096 tokens
    - **Image:** 256p, 480p, and 720p resolution at one of these aspect ratios (16:9, 4:3, 1:1, 3:4, 9:16)
    - **Video:** 256p, 480p, and 720p resolution at one of these aspect ratios (16:9, 4:3, 1:1, 3:4, 9:16). Max number of frames = 5.
    - **Audio:** Max 0.5 second
    - **Action:** 16 – 400 video frames
- **Generator Output**
  - **Output Type(s)**: Image, video, audio, action, text
  - **Output Format(s)**:
    - Image: JPG
    - Video: MP4
    - Audio: Advanced Audio Coding (AAC) stream (muxed within the MP4)
    - Action: 1D list (.json)
    - Text: string
  - **Output Parameters**:
    - Image: Two-dimensional (2D)
    - Video: Three-dimensional (3D)
    - Audio: One-dimensional (1D)
    - Action: One-dimensional (1D)
    - Text: One-dimensional (1D)
  - **Other Properties Related to Output**:
    - The generated video is an MP4 file, with the resolution, frame rate, and duration specified in the input. The generated audio is encoded in AAC format, muxed into the video MP4 file with 2 channels (stereo) and a 48 kHz sample rate.
    - Video generation supports durations from 5 to 400 frames, with 189 frames as the default generation duration.
    - The generated action is only supported for compatible embodiments, including general camera motion (9D), autonomous vehicle (9D), egocentric motion (57D), single Franka Panda arm with RobotiQ gripper (10D), dual Franka Panda arm with RobotiQ gripper (20D), Agibot (29D), UR (10D), Google robot (10D), WidowX 250 (10D), UMI (9D).
    - Audio: 48 kHz stereo AAC stream muxed into video mp4
    - Video: mp4 at the FPS specified in input
    - Image: JPEG
- **Reasoner Input**
  - **Input Type(s)**: Text, Text+Image, Text+Video
  - **Input Format(s)**:
    - Text: String
    - Image: jpg, png, jpeg, webp
    - Video: mp4
  - **Input Parameters**:
    - Text: One-dimensional (1D)
    - Image: Two-dimensional (2D)
    - Video: Three-dimensional (3D)
  - **Other Properties Related to Input**:
    - Video inputs are recommended at a frame rate of 4 fps.
    - Long-context inputs supported up to 256K tokens.
  - **Input Size and Length limits:**
    - **Text:** Up to 256K tokens (context window).
    - **Image:** Standard input image formats; passed as file or URL.
    - **Video:** mp4 at the recommended 4 fps.
- **Reasoner Output**
  - **Output Type(s)**: Text
  - **Output Format(s)**:
    - Text: string
  - **Output Parameters**:
    - Text: One-dimensional (1D)
  - **Other Properties Related to Output**:
    - Default `max_tokens=4096+` is recommended for reasoning outputs; longer outputs may be requested.
    - Reasoning outputs may include structured chain-of-thought, 2D/3D point localization, and bounding-box coordinates for vision-based tasks.

The video content visualizes the input text description as a short animated scene, capturing key elements within the specified time constraints.

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA's hardware (e.g., GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions.

## Software Integration

**Runtime Engine(s):**

- [PyTorch](https://github.com/nvidia/cosmos3)
- [vLLM-Omni](https://github.com/vllm-project/vllm-omni)
- [Hugging Face Diffusers](https://huggingface.co/docs/diffusers/en/index)
- [SGLang](https://github.com/sgl-project/sglang)

**Supported Hardware Microarchitecture Compatibility:**

- NVIDIA Ampere
- NVIDIA Blackwell
- NVIDIA Hopper

**Operating System(s):**

- Linux (We have not tested on other operating systems.)

**Note:** Only BF16 precision is tested. Other precisions like FP4, FP8, and FP16 are not officially supported.

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment.

## Training, Testing, and Evaluation Datasets

### Dataset Overview

- **Total Size:** 1.3B data points
- **Total Number of Datasets:** 393 dataset entries
- **Dataset partition:** Training [100%], Testing [N/A — evaluation benchmarks used separately], Validation [N/A — evaluation benchmarks used separately]
- **Time period for training data collection:** 2024–2026
- **Time period for testing data collection:** N/A (standard public benchmarks)
- **Time period for validation data collection:** N/A (standard public benchmarks)

Raw data from internal and external sources is transformed into training-ready data through multiple stages of curation, filtering, and quality review. Data acquisition spans diverse multimodal sources — robotics, autonomous driving, industrial environments, indoor and outdoor scenes, varied lighting and weather conditions, camera viewpoints, object categories, and human activities — to broaden coverage across Physical AI operating environments. Automated filtering pipelines remove corrupted, duplicate, low-quality, and restricted content. Metadata analysis, heuristic rules, and model-assisted classifiers are applied during preprocessing to flag anomalous distributions and low-diversity subsets. Human review supplements automated filtering for selected datasets, benchmark construction, and targeted quality analysis. Datasets are balanced across modalities and task categories — visual reasoning, text-to-image, text-to-video, image-to-video, audio generation, video transfer, action-conditioned generation, and action command generation — to reduce overrepresentation of narrow domains. Synthetic and simulation-based augmentation supplements coverage of rare physical interactions and edge-case scenarios. Deduplication and provenance tracking are applied across the corpus. The resulting processed data is converted into model-ready tokenized or encoded representations through modality-specific preprocessors before training begins.

Training datasets passed through multiple layers of automated and manual safeguards designed to reduce the presence of harmful or policy-violating content across categories including weapons and weapons-related instructional content, criminal planning, child sexual abuse material (CSAM), non-consensual intimate imagery (NCII), sexual content involving minors, harassment, hate speech, profanity, threats and incitement to violence, self-harm or suicide-related content, and graphic violence. Data sources are reviewed for licensing compatibility, provenance, and alignment with internal data governance and safety policies before admission into training corpora. Automated filtering pipelines combine multiple detection strategies: hash-matching against known CSAM and NCII reference databases; classifier-based moderation models trained for explicit sexual content, hate speech, violence, weapons imagery, and other restricted categories; keyword and regex-based screening for criminal-planning, threats, and self-harm phrases in text data; metadata and provenance heuristics for source-level risk signals; and embedding-based anomaly detection to surface samples that fall outside expected distributions. Human review and targeted audits supplement automated filtering for selected datasets, benchmark construction, and safety-sensitive evaluation. For multimodal Physical AI data (robotics, autonomous driving, industrial scenes), additional filtering targets invalid action trajectories, physically implausible interactions, and unsafe control sequences. Synthetic and simulation-generated data are evaluated through internal validation before inclusion. Benchmark evaluations and red-team testing are applied post-training to surface remaining safety gaps across world generation, reasoning, audio, and action tasks. No large-scale data-filtering process can guarantee complete removal of all harmful content; residual risks may remain, particularly in rare edge cases or open-world deployment settings. Ongoing monitoring and dataset review continue post-release.

- For more information about the datasets used to train this model, please see the [Public Summary of Training Content](https://docs.nvidia.com/cosmos/latest/_downloads/e482b7114ce8dbfbb07d2d4b42cafe4e/training-content-Cosmos-3.pdf).

**Data Modality and Training Data Size**

| Modality | Reasoning Data Sample Count | Generation Data Sample Count |
| -------- | ------------------- | -------------------- |
| Text     | 22M                 | Not Applicable       |
| Image    | 19M                 | 767M                 |
| Video    | 1M                  | 348M                 |
| Audio    | Not Applicable      | 139M                 |
| Action   | Not Applicable      | 8M                   |

**Data Collection Method by dataset**

- Hybrid: Automatic/Sensors, Synthetic, Automated

**Labeling Method by dataset**

- Hybrid: Human, Automated

**Properties:** The training, testing, and evaluation datasets consist of diverse multimodal video, image, audio, action, synthetic, and sensor-conditioned data sourced from NVIDIA-owned data and publicly available, commercially permissive datasets. These datasets are curated to exclude known restricted content and to support building an Omni model that learns to generate and reason about dynamic physical environments across world reasoning and generation tasks.

### Public Datasets

| Dataset&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Samples&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; |
|---|---|
| OpenImage | 1.2M |
| Coyo700M | 100M |
| YouTube Video | 340M |
| UMI | 4.5M |

### Private Datasets

| Dataset&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Samples&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; |
|---|---|
| Egocentric | 7M |
| Nexar | 0.6M |
| AgiBot | 0.2M |
| HOI | 0.3M |

### Synthetic Datasets

| Dataset | Samples |
|---|---|
| synthetic images generated using HiDream-I1 | 15M |
| synthetic images generated using Qwen-Image-2512 | 14M |
| synthetic captions generated using Qwen3-VL | 1115M |

## Evaluation Datasets

**Data Collection Method by dataset**

- Hybrid: Automatic/Sensors, Synthetic, Automated

**Labeling Method by dataset**

- Hybrid: Human, Automated

**Properties:** The training, testing, and evaluation datasets consist of diverse multimodal video, image, audio, action, synthetic, and sensor-conditioned data sourced from NVIDIA-owned data and publicly available, commercially permissive datasets. These datasets are curated to exclude known restricted content and to support building an Omni model that learns to generate and reason about dynamic physical environments across world reasoning and generation tasks.

## Benchmarks

Please see our [technical paper](https://research.nvidia.com/labs/cosmos-lab/cosmos3/technical-report.pdf) for detailed evaluations of the base model.

### Text-to-image benchmark results

![benchmark results](assets/benchmark-text2image.png)

### Artificial Analysis Leaderboard

#### Open-Source Models [2026/05/28/]

![Artificial Analysis Text-to-Image leaderboard — open-source models](assets/benchmark-text2image-leaderboard.png)

#### All Models [2026/05/28/] (Including Closed-Source)

![Artificial Analysis Text-to-Image leaderboard — all models including closed-source](assets/benchmark-text2image-leaderboard-all-models.jpg)

## Qualitative examples

![Qualitative examples](assets/more_images.jpg)

## Usage

- See [Cosmos](https://github.com/nvidia/cosmos) for details.

### Prompt upsampling

For optimal quality, text prompts should be upsampled into a specific JSON structure. Description and code can be found [here](https://github.com/nvidia/cosmos-framework/blob/main/docs/prompt_upsampling.md).

For example, for text-to-image upsampling using Opus-4.7:

```bash
git clone https://github.com/NVIDIA/cosmos-framework.git packages/cosmos-framework
pip install -e packages/cosmos-framework

export PROMPT_UPSAMPLER_ENDPOINT_URL="https://api.anthropic.com/v1/"
export PROMPT_UPSAMPLER_MODEL_NAME="claude-opus-4-7"
export PROMPT_UPSAMPLER_API_TOKEN="<your_token>"

python -m cosmos_framework.inference.prompt_upsampling \
    --input assets/original_prompt.txt \
    --output /tmp/upsampled_t2i_opus/ \
    --mode text2image \
    --endpoint-url "${PROMPT_UPSAMPLER_ENDPOINT_URL}" \
    --model "${PROMPT_UPSAMPLER_MODEL_NAME}" \
    --api-token "${PROMPT_UPSAMPLER_API_TOKEN}" \
    --resolution 768 \
    --aspect-ratio "1,1"
```

The JSON-upsampled version of `assets/original_prompt.txt` is saved in `assets/example_caption.json` for convenience, and is used for the image generation examples below.

### vLLM-Omni

#### Container

```
docker pull vllm/vllm-omni:cosmos3
```

#### General Invocation

You can use the release-tested `vllm-omni` package for deploying an OpenAI-compatible API inference endpoint.
The recommended vLLM-Omni serving configuration for `nvidia/Cosmos3-Super-Text2Image` on a 8xH100 node is:

```bash
vllm serve nvidia/Cosmos3-Super-Text2Image \
  --omni \
  --host 0.0.0.0 \
  --port 8000 \
  --cfg-parallel-size 2 \
  --ulysses-degree 4 \
  --tensor-parallel-size 1 \
  --use-hsdp \
  --hsdp-shard-size 8 \
  --init-timeout 1800
```

Setting `--enable-layerwise-offload` can help with memory usage on GPUs with less available memory; however, please note that for text2image generation, this may incur a significant performance penalty. For 4xH200 or 4xGB200 one can simply use `--cfg-parallel-size 2 --ulysses-degree 2 --tensor-parallel-size 1`.

#### Examples

##### Text to image generation
```python
import base64
import json
import requests

# 1. Read JSON-upsampled prompt
json_prompt = json.load(open("assets/example_caption.json"))

# 2. Build your API payload
payload = {
    "prompt": json.dumps(json_prompt),
    "size": "1024x1024",
    "n": 1,  # single frame generation
    "num_inference_steps": 50,
    "guidance_scale": 4.0,
    "flow_shift": 3.0,
    "negative_prompt": "",
    "seed": 1143,
    "extra_args": {
      "use_resolution_template": False,
      "guardrails": True,
    },
}

# 3. Send the POST request
url = "http://localhost:8000/v1/images/generations"
print("Sending request to server...")
response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
response.raise_for_status()

# 4. Extract the base64 data and decode it into an image
response_json = response.json()
b64_data = response_json["data"][0]["b64_json"]
image_bytes = base64.b64decode(b64_data)

# 5. Save the final PNG file
with open("/tmp/cosmos3_t2i.png", "wb") as image_file:
    image_file.write(image_bytes)
print("Saved image to /tmp/cosmos3_t2i.png")
```

![example_image](assets/example_image.png)

### SGLang

[SGLang Diffusion](https://docs.sglang.io/docs/sglang-diffusion/index) can serve `nvidia/Cosmos3-Super-Text2Image` through OpenAI-compatible image generation endpoints. Install SGLang from the main branch with diffusion dependencies, then start the server:

```bash
git clone --branch main https://github.com/sgl-project/sglang.git
cd sglang
pip install -e "python[diffusion]"
pip install "cosmos-guardrail==0.3.1"

sglang serve \
  --model-path nvidia/Cosmos3-Super-Text2Image \
  --num-gpus 4
```

Cosmos 3 support in SGLang Diffusion currently requires the SGLang main branch. Switch to a stable SGLang release once Cosmos 3 support is included there.

Example text-to-image request:

```bash
curl -sS -X POST http://localhost:30000/v1/images/generations \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A warehouse robot folds a blue cloth on a clean workbench.",
    "size": "1280x720",
    "n": 1,
    "num_inference_steps": 35,
    "guidance_scale": 6.0,
    "flow_shift": 10.0,
    "seed": 0,
    "extra_args": {
      "use_resolution_template": false,
      "guardrails": true
    }
  }'
```

For complete serving instructions and request examples, see the [Cosmos3 SGLang cookbook](https://docs.sglang.io/cookbook/diffusion/Cosmos/Cosmos3).

### Diffusers

Cosmos3 is fully supported within the popular HuggingFace Diffusers package. This integration makes it a supported inference backend, allowing developers to easily incorporate Cosmos3's capabilities - such as text-to-image generation - into their pipelines using the Cosmos3OmniPipeline class, as demonstrated by the provided code examples (see examples for other modalities on the HuggingFace Cosmos3 page).

**Note:** This example is tested on GB200. For H100, use the [vLLM-Omni serving recipe](#vllm-omni) above, which supports multi-GPU deployment via HSDP.

#### Installation

To install diffusers with Cosmos3OmniPipeline:
```
uv venv --python 3.13 --seed --managed-python
source .venv/bin/activate
uv pip install \
  "diffusers @ git+https://github.com/huggingface/diffusers.git" \
  accelerate \
  av \
  cosmos_guardrail \
  huggingface_hub \
  imageio \
  imageio-ffmpeg \
  torch \
  torchvision \
  transformers
```

#### Examples

##### Text to image generation
```python
import json
import torch
from diffusers import Cosmos3OmniPipeline
from diffusers.schedulers.scheduling_unipc_multistep import UniPCMultistepScheduler

json_prompt = json.load(open("assets/example_caption.json"))

pipe = Cosmos3OmniPipeline.from_pretrained(
    "nvidia/Cosmos3-Super-Text2Image",
    torch_dtype=torch.bfloat16,
    device_map="cuda",
    enable_safety_checker=True,
)
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=3.0)

result = pipe(
    prompt=json.dumps(json_prompt),
    negative_prompt="",
    num_frames=1,
    height=1024,
    width=1024,
    num_inference_steps=50,
    guidance_scale=4.0,
    generator=torch.Generator(device="cuda").manual_seed(1143),
)

result.video[0].save("/tmp/cosmos3_t2i.png")
print("Saved image to /tmp/cosmos3_t2i.png")
```

## Limitations

Cosmos3 may produce imperfect outputs in challenging scenarios. Generation artifacts include temporal inconsistency, unstable camera or object motion, imprecise physical interactions, inaccurate audio-video synchronization, and action-state drift — especially in long-horizon or high-resolution outputs. Reasoning may also be incorrect: object states, causal relationships, spatial geometry, temporal ordering, agent intent, and future outcomes can be misinferred, and complex or long-context inputs may yield hallucinated entities, inconsistent interpretations, or implausible predictions. Because the model lacks an explicit physics simulator, 3D geometry, 4D space-time evolution, object permanence, contact dynamics, and physical laws are only approximated — producing artifacts such as disappearing or morphing objects, unrealistic collisions, and physically implausible motions. Quality further degrades in out-of-distribution environments, safety-critical edge cases, and domains underrepresented in training.

Cosmos3 outputs should not be treated as physically accurate simulation, reliable ground-truth reasoning, or safety-certified decision making. Applications involving robotics control, autonomous systems, scientific simulation, or safety-critical planning require additional validation, external constraints, system-level safety analysis, and domain-specific guardrails before deployment.

## Inference

**Acceleration Engine:** [PyTorch](https://pytorch.org/), [vLLM](https://github.com/vllm-project/vllm), [vLLM-Omni](https://github.com/vllm-project/vllm-omni), [Hugging Face Diffusers](https://github.com/huggingface/diffusers), [SGLang](https://github.com/sgl-project/sglang), [SGLang Diffusion](https://docs.sglang.io/docs/sglang-diffusion/index)

**Test Hardware:** GB200 and H100

## Ethical Considerations

NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications.  Developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.

Please make sure you have proper rights and permissions for all input image and video content; if image or video includes people, personal health information, or intellectual property, the image or video generated will not blur or maintain proportions of image subjects included.

Users are responsible for model inputs and outputs. Users are responsible for ensuring safe integration of this model, including implementing guardrails as well as other safety mechanisms, prior to deployment.

For more detailed information on ethical considerations for this model, please see the Model Card++ [Explainability](EXPLAINABILITY.md), [Bias](BIAS.md), [Safety & Security](SAFETY.md), and [Privacy](PRIVACY.md) subcards. Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).

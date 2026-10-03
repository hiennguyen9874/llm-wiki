---
tags:
- text-to-image
- lora
- diffusers
- template:diffusion-lora
widget:
- output:
    url: images/2b2fbfd3-e134-4eff-b98a-a5e17c906539.png
  text: '-'
base_model: Qwen/Qwen-Image-2.1
instance_prompt: null
license: apache-2.0
---
# Qwen-Image-2.1-LoRAs

<Gallery />

## Model description 

---
license: apache-2.0
base_model: Qwen&#x2F;Qwen-Image-2.1
tags:
- qwen
- qwen-image
- image-editing
- lora
- anime
---

# 🎨 Qwen-Image-2.1-Edit-LoRAs

Welcome to the **Qwen-Image-2.1-Edit-LoRAs** repository! 

This repository is dedicated to LoRA models specifically fine-tuned for the image editing capabilities of &#x60;Qwen-Image-2.1&#x60;. I will be continuously updating and publishing various functional and stylistic LoRAs here.

---

## 📦 Available Models

### 1. Qwen2.1_Anime_consistency
* **Overview**: A LoRA designed to enhance character consistency during anime-style image editing.
* **Training Data**: Primarily fine-tuned on character model sheets (4-view references) and a variety of facial expression edits.
* **Status**: ⚠️ **Experimental**
  &gt; *Note: This model is currently in an experimental phase. It was primarily developed to test and benchmark the optimal training parameters for Qwen Image 2.1. As a result, specific editing outcomes and output stability are not strictly guaranteed.*

---

### 2. Qwen2.1_Anything2RealCharacters
* **Overview**: A LoRA designed to transform images from any artistic style into realistic human character images.
* **Training Data**: Primarily fine-tuned on a large dataset of real human images paired with facial expression control reference groups.
* **Recommended Settings**: 
  * **Sampler**: `Euler`
  * **Scheduler**: `FlowMatchEulerDiscreteScheduler`
  > *Tip: Using these recommended settings helps achieve softer, more authentic, and high-fidelity realistic character rendering.*

* **Preview / Showcase**:
  <div align="center">
    <img src="https://huggingface.co/WarmBloodAban/Qwen-Image-2.1-LoRAs/resolve/main/images/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_2026-09-27_231730_493.png" alt="Preview" width="600px" style="max-width: 100%; height: auto; border-radius: 8px;">
  </div>

---

## ⚙️ Recommended Parameters

To ensure optimal performance, please adhere to the official base model settings:
- **Sampling Steps**: Follow the official recommended settings for Qwen-Image 2.1.
- **CFG Scale**: Follow the official recommended settings for Qwen-Image 2.1.
- **LoRA Weight**: It is recommended to start testing between &#x60;0.6&#x60; and &#x60;0.8&#x60;, adjusting based on your specific editing needs.

---

## 🤝 Community &amp; Commercial Inquiries

Feel free to connect for tutorials, community discussions, workflow sharing, or commercial collaborations:

- 📺 **YouTube Channel**: [AIGC-Singularity](https:&#x2F;&#x2F;www.youtube.com&#x2F;@AIGC-Singularity)
- 📺 **Bilibili Channel**: [AIGC-Singularity](https:&#x2F;&#x2F;space.bilibili.com&#x2F;49766729)
- 💬 **QQ Group 2**: &#x60;1072010342&#x60; *(Please specify your intent when requesting to join)*
- 💼 **Business Inquiries (WeChat)**: &#x60;aigctyd&#x60;
- 📧 **Email**: a592991299@gmail.com


## Download model


[Download](/WarmBloodAban/Qwen-Image-2.1-LoRAs/tree/main) them in the Files & versions tab.

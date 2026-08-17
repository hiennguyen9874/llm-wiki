---
license: mit
library_name: transformers
pipeline_tag: image-to-text
tags:
- ocr
- document-understanding
- vision-language-model
- multimodal
- trust-remote-code
- mineru
---

<p align="center">
  <img src="assets/banner.png" alt="MinerU-Diffusion" width="100%">
</p>

# MinerU-Diffusion: Rethinking Document OCR as Inverse Rendering via Diffusion Decoding

<p align="center">
  <a href="https://arxiv.org/pdf/2603.22458"><img src="https://img.shields.io/badge/📄_Tech_Report-red?style=flat-square" alt="Tech Report" /></a>
  <a href="https://huggingface.co/Niujunbo2002/MinerU-Diffusion-V1-0320-2.5B"><img src="https://img.shields.io/badge/🤗_Model-HuggingFace-yellow?style=flat-square" alt="Model" /></a>
  <a href="https://github.com/opendatalab/MinerU-Diffusion">
    <img src="https://img.shields.io/badge/GitHub-Repo-black?style=flat-square&logo=github" alt="GitHub Repo" />
  </a>
  <a href="https://github.com/sgl-project/sglang"><img src="https://img.shields.io/badge/SGLang-Supported-purple?style=flat-square" alt="SGLang Supported" /></a>
  <a href="https://github.com/GeeeekExplorer/nano-vllm"><img src="https://img.shields.io/badge/Nano--DVLM-Adapted-yellow?style=flat-square" alt="Nano-DVLM Adapted" /></a>
  <a href="https://github.com/Niujunbo2002/MinerU-Diffusion/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License MIT" /></a>
</p>

## 📰 News

- **[2026/3/24]** 🔥 We release **MinerU-Diffusion-V1** — a diffusion-based framework for document OCR that
replaces autoregressive decoding with block-level parallel diffusion decoding.

## 💡 TL;DR

> **MinerU-Diffusion** reframes document OCR as an inverse rendering problem and replaces slow, error-prone autoregressive decoding with parallel diffusion decoding.

By introducing block-wise diffusion, uncertainty-driven curriculum learning, it achieves up to 3.2× faster decoding while improving robustness and reducing reliance on language priors.

<p align="center">
  <img src="assets/train.png"  alt="Overview"  width="600">
</p>





> **Highlights:** MinerU-Diffusion maintains a strong accuracy-efficiency trade-off, achieving 2.12× speedup with 99.9% and 3.01× speedup with 98.8% relative accuracy.
>
## 📈 Performance

<p align="center">
  <img src="assets/performance_tradeoff.jpeg" alt="Performance Trade-off" width="775">
</p>

MinerU-Diffusion provides a flexible accuracy-throughput trade-off through threshold control. Compared with MinerU2.5, it achieves up to **3.26x** TPS, while also offering practical operating points such as **2.12x speedup with 99.9% relative accuracy** and **3.01x speedup with 98.8% relative accuracy**.

## 🛠️ Environment Setup

Use `Python 3.12.12` with the following versions:

- `Python 3.12.12`
- `torch 2.8.0+cu128`
- `torchvision 0.23.0+cu128`
- `torchaudio 2.8.0+cu128`
- `transformers >= 4.52.1`
- `triton 3.4.0`
- `flash-attn 2.8.3`
- `liger-kernel 0.6.4`

Install with:

```bash
pip install --upgrade pip
pip install torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
pip install "transformers>=4.52.1"
wget https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/flash_attn-2.8.3+cu12torch2.8cxx11abiFALSE-cp312-cp312-linux_x86_64.whl
pip install flash_attn-2.8.3+cu12torch2.8cxx11abiFALSE-cp312-cp312-linux_x86_64.whl
pip install triton==3.4.0 liger-kernel==0.6.4
```

## 🚀 Inference

### Transformers Example

```python
import torch
from transformers import AutoModel, AutoProcessor, AutoTokenizer

model_id = "Niujunbo2002/MinerU-Diffusion-V1-0320-2.5B"
image_path = "path/to/page.png"

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
processor = AutoProcessor.from_pretrained(
    model_id,
    trust_remote_code=True,
    use_fast=False,
)
model = AutoModel.from_pretrained(
    model_id,
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
).eval().to("cuda")

messages = [
    {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
    {"role": "user", "content": [{"type": "image", "image": image_path}, {"type": "text", "text": "\nText Recognition:"}]},
]

prompt_text = processor.apply_chat_template(messages, add_generation_prompt=True)
if isinstance(prompt_text, tuple):
    prompt_text = prompt_text[0]

inputs = processor(
    images=[image_path],
    text=prompt_text,
    truncation=True,
    max_length=4096,
    return_tensors="pt",
)
input_ids = inputs["input_ids"].to(torch.long).to("cuda")
pixel_values = inputs["pixel_values"].to(torch.bfloat16).to("cuda")
image_grid_thw = inputs.get("image_grid_thw")
if image_grid_thw is not None:
    image_grid_thw = image_grid_thw.to(torch.long).to("cuda")

with torch.no_grad():
    generate_outputs = model.generate(
        pixel_values=pixel_values,
        image_grid_thw=image_grid_thw,
        input_ids=input_ids,
        mask_token_id=tokenizer.convert_tokens_to_ids("<|MASK|>"),
        denoising_steps=32,
        gen_length=1024,
        block_length=32,
        temperature=1.0,
        remasking_strategy="low_confidence_dynamic",
        dynamic_threshold=0.95,
        tokenizer=tokenizer,
        stopping_criteria=["<|endoftext|>", "<|im_end|>"],
    )

if isinstance(generate_outputs, tuple):
    output_ids = generate_outputs[0]
else:
    output_ids = generate_outputs

text = tokenizer.decode(output_ids[0], skip_special_tokens=False)
for stop in ("<|endoftext|>", "<|im_end|>"):
    text = text.split(stop, 1)[0]

print(text.strip())
```

## 🤝 Acknowledgement

This work is heavily built on the following open-source models:

[MinerU](https://github.com/opendatalab/mineru), [Qwen2-VL](https://github.com/QwenLM/Qwen3-VL), [SDAR](https://github.com/JetAstra/SDAR), and [LLaDA](https://github.com/ML-GSAI/LLaDA).

These acceleration methods (engines):

[SGLang](https://github.com/sgl-project/sglang), [Nano-vLLM](https://github.com/GeeeekExplorer/nano-vllm) as the upstream basis for our `nano_dvlm` adaptation, and [jetengine](https://github.com/Labman42/JetEngine/tree/0ddc55ad3fb712b6374515b78d656f420e1a7243),

and theoretical foundations:

[MDLM](https://arxiv.org/pdf/2406.07524), [DiffuLLaMA](https://arxiv.org/abs/2410.17891), [Block Diffusion](https://arxiv.org/abs/2503.09573).

For the training code, we also reference [dLLM-RL](https://github.com/Gen-Verse/dLLM-RL).

## 📚 Citation

If you find our paper and code useful in your research, please consider giving a star and citation.

```bibtex
@article{dong2026minerudiffusion,
  title={MinerU-Diffusion: Rethinking Document OCR as Inverse Rendering via Diffusion Decoding},
  author={Dong, Hejun and Niu, Junbo and Wang, Bin and Zeng, Weijun and Zhang, Wentao and He, Conghui},
  journal={arXiv preprint arXiv:2603.22458},
  year={2026}
}

@article{niu2025mineru2,
  title={Mineru2. 5: A decoupled vision-language model for efficient high-resolution document parsing},
  author={Niu, Junbo and Liu, Zheng and Gu, Zhuangcheng and Wang, Bin and Ouyang, Linke and Zhao, Zhiyuan and Chu, Tao and He, Tianyao and Wu, Fan and Zhang, Qintong and others},
  journal={arXiv preprint arXiv:2509.22186},
  year={2025}
}

@article{wang2024mineru,
  title={Mineru: An open-source solution for precise document content extraction},
  author={Wang, Bin and Xu, Chao and Zhao, Xiaomeng and Ouyang, Linke and Wu, Fan and Zhao, Zhiyuan and Xu, Rui and Liu, Kaiwen and Qu, Yuan and Shang, Fukai and others},
  journal={arXiv preprint arXiv:2409.18839},
  year={2024}
}

@article{he2024opendatalab,
  title={Opendatalab: Empowering general artificial intelligence with open datasets},
  author={He, Conghui and Li, Wei and Jin, Zhenjiang and Xu, Chao and Wang, Bin and Lin, Dahua},
  journal={arXiv preprint arXiv:2407.13773},
  year={2024}
}
```

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Niujunbo2002/MinerU-Diffusion/blob/main/LICENSE) file for details.

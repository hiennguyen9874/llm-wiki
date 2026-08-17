---
license: apache-2.0
pipeline_tag: image-to-text
language:
- en
- fr
- de
- es
- it
- nl
- pt
- sv
- da
library_name: transformers
tags:
- ocr
- document-understanding
- vision-language
- pdf
- tables
- forms
new_version: lightonai/LightOnOCR-2-1B
---

<div align="center">
  <img src="lightonocr-banner.png" alt="LightOn OCR-1B Banner" width="600"/>
</div>

> [!NOTE]
> 🚀 **LightOnOCR-2 is now available and state-of-the-art on [OlmOCR-bench](https://huggingface.co/datasets/allenai/olmOCR-bench)**, with new image detection variants!
> Check it out here: **[lightonai/LightOnOCR-2-1B](https://huggingface.co/lightonai/LightOnOCR-2-1B)**

# LightOnOCR-1B-1025

Full BF16 version of the model. We recommend this variant for inference and further fine-tuning.

**LightOnOCR-1B** is a compact, end-to-end vision–language model for Optical Character Recognition (OCR) and document understanding. It achieves state-of-the-art accuracy in its weight class while being several times faster and cheaper than larger general-purpose VLMs.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/#fileId=https%3A//huggingface.co/lightonai/LightOnOCR-1B-1025/blob/main/notebook.ipynb)

📄 **[Paper]( https://arxiv.org/pdf/2601.14251)** | 📝 **[Read the full blog post](https://huggingface.co/blog/lightonai/lightonocr/)** | 🚀 **[Try the demo](https://huggingface.co/spaces/lightonai/LightOnOCR-1B-Demo-zero)** | 📓 **[Finetuning notebook](https://colab.research.google.com/drive/1WjbsFJZ4vOAAlKtcCauFLn_evo5UBRNa?usp=sharing)**

**Highlights**

* ⚡ **Speed:** 5× faster than dots.ocr, 2× faster than PaddleOCR-VL-0.9B, 1.73× faster than DeepSeekOCR
* 💸 **Efficiency:** Processes 5.71 pages/s on a single H100 (~493k pages/day) for **<$0.01 per 1,000 pages**
* 🧠 **End-to-End:** Fully differentiable, no external OCR pipeline
* 🧾 **Versatile:** Handles tables, receipts, forms, multi-column layouts, and math notation
* 🌍 **Compact variants:** 32k and 16k vocab options for European languages

---

## Model Overview

**LightOnOCR** combines a Vision Transformer encoder(Pixtral-based) with a lightweight text decoder(Qwen3-based) distilled from high-quality open VLMs.
It is optimized for document parsing tasks, producing accurate, layout-aware text extraction from high-resolution pages.


---

## Benchmarks

<div align="center">
  <img src="https://cdn-uploads.huggingface.co/production/uploads/62cd695e94b9dcedbf1818e5/2a2qgHMopS6z3BozBGEvn.png" alt="OlmOCR-bench v1" width="900"/>
</div>

All benchmarks evaluated using **vLLM** on the Olmo-Bench.

---

## Installation

### VLLM

[2025/11/24] 🚀 LightOnOCR is now officially supported in vLLM v0.11.1 🚀
```bash

uv venv --python 3.12 --seed
source .venv/bin/activate

# install any version higher than 0.11.1
uv pip install vllm==0.11.2
# extra deps need only to run the example below
uv pip install pypdfium2 pillow requests
```

**Start Server**

```bash
vllm serve lightonai/LightOnOCR-1B-1025 \
    --limit-mm-per-prompt '{"image": 1}' --mm-processor-cache-gb 0 --no-enable-prefix-caching
```

**PDF Inference**

```python
import base64
import requests
import pypdfium2 as pdfium
import io

ENDPOINT = "http://localhost:8000/v1/chat/completions"
MODEL = "lightonai/LightOnOCR-1B-1025"

# Download PDF from arXiv
pdf_url = "https://arxiv.org/pdf/2412.13663"
pdf_data = requests.get(pdf_url).content

# Open PDF and convert first page to image
pdf = pdfium.PdfDocument(pdf_data)
page = pdf[0]
# Render at 200 DPI (scale factor = 200/72 ≈ 2.77)
pil_image = page.render(scale=2.77).to_pil()

# Convert to base64
buffer = io.BytesIO()
pil_image.save(buffer, format="PNG")
image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

# Make request
payload = {
    "model": MODEL,
    "messages": [{
        "role": "user",
        "content": [{
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{image_base64}"}
        }]
    }],
    "max_tokens": 4096,
    "temperature": 0.2,
    "top_p": 0.9,
}

response = requests.post(ENDPOINT, json=payload)
text = response.json()['choices'][0]['message']['content']
print(text)
```

### Transformers

> **Note:** LightOnOCR-2 requires transformers installed from source (not yet in a stable release).

```bash
uv pip install git+https://github.com/huggingface/transformers
```

```python
import torch
from transformers import LightOnOcrForConditionalGeneration, LightOnOcrProcessor

device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float32 if device == "mps" else torch.bfloat16

model = LightOnOcrForConditionalGeneration.from_pretrained("lightonai/LightOnOCR-2-1B-base", torch_dtype=dtype).to(device)
processor = LightOnOcrProcessor.from_pretrained("lightonai/LightOnOCR-2-1B-base")

url = "https://huggingface.co/datasets/hf-internal-testing/fixtures_ocr/resolve/main/SROIE-receipt.jpeg"
conversation = [{"role": "user", "content": [{"type": "image", "url": url}]}]

inputs = processor.apply_chat_template(
    conversation,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
)
inputs = {k: v.to(device=device, dtype=dtype) if v.is_floating_point() else v.to(device) for k, v in inputs.items()}

output_ids = model.generate(**inputs, max_new_tokens=1024)
generated_ids = output_ids[0, inputs["input_ids"].shape[1]:]
output_text = processor.decode(generated_ids, skip_special_tokens=True)
print(output_text)
```


---

## Rendering and Preprocessing Tips

* Render PDFs to **PNG** or **JPEG** at a target longest dimension of **1540px**
* Maintain aspect ratio to preserve text geometry
* Use one image per page; batching supported by vLLM

---

## Variants

| Variant                                                                            | Description                                   |
| :--------------------------------------------------------------------------------- | :-------------------------------------------- |
| **[LightOnOCR-1B-1025](https://huggingface.co/lightonai/LightOnOCR-1B-1025)**      | Full multilingual model (default)             |
| **[LightOnOCR-1B-32k](https://huggingface.co/lightonai/LightOnOCR-0.9B-32k-1025)** | Fastest pruned-vocabulary version (32k tokens) optimized for European languages |
| **[LightOnOCR-1B-16k](https://huggingface.co/lightonai/LightOnOCR-0.9B-16k-1025)** | Most compact variant with smallest vocabulary          |

---

## Fine-tuning

**Transformers integration is coming soon for training and inference.**

LightOnOCR is fully differentiable and supports:

* LoRA fine-tuning
* Domain adaptation (receipts, scientific articles, forms, etc.)
* Multilingual fine-tuning with task-specific corpora

📓 **[Finetuning notebook](https://colab.research.google.com/drive/1WjbsFJZ4vOAAlKtcCauFLn_evo5UBRNa?usp=sharing)**

---

## Data

Trained on a diverse large-scale PDF corpus covering:

* Scientific papers, books, receipts, invoices, tables, forms, and handwritten text
* Multiple languages (Latin alphabet dominant)
* Real and synthetic document scans

The dataset will be released under an open license.

---

## License

Apache License 2.0

---

## Acknowlegments

The project received funding from the BPI Scribe project.

---

## Citation

```
@misc{lightonocr2025,
  title        = {LightOnOCR-1B: End-to-End and Efficient Domain-Specific Vision-Language Models for OCR},
  author       = {Said Taghadouini and Baptiste Aubertin and Adrien Cavaillès},
  year         = {2025},
  howpublished = {\url{https://huggingface.co/blog/lightonai/lightonocr}}
}
```
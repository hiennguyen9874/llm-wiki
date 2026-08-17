---
license: apache-2.0
pipeline_tag: image-text-to-text
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
- zh
- ja
library_name: transformers
tags:
- ocr
- document-understanding
- vision-language
- pdf
- tables
- forms
---

<div align="center">
  <img src="lightonocr-banner.png" alt="LightOnOCR-2-1B Banner" width="600"/>
</div>

---

<div align="center">

[![Website](https://img.shields.io/badge/LightOn-Website-blue?logo=google-chrome)](https://lighton.ai)
[![LinkedIn](https://img.shields.io/badge/LightOn-LinkedIn-0A66C2?logo=linkedin)](https://www.linkedin.com/company/lighton/)
[![X](https://img.shields.io/badge/@LightOnIO-X-black?logo=x)](https://x.com/LightOnIO)

📄 [Paper](https://arxiv.org/pdf/2601.14251) | 📝 [Blog](https://huggingface.co/blog/lightonai/lightonocr-2) | 🚀 [Demo](https://huggingface.co/spaces/lightonai/LightOnOCR-2-1B-Demo) | 📊 [Dataset](https://huggingface.co/datasets/lightonai/LightOnOCR-mix-0126) | 📓 [Finetuning](https://colab.research.google.com/drive/1WjbsFJZ4vOAAlKtcCauFLn_evo5UBRNa?usp=sharing)

</div>

# LightOnOCR-2-1B
**Best OCR model .** LightOnOCR-2-1B is **[LightOn's](https://lighton.ai)** flagship OCR model, refined with RLVR training for maximum accuracy. We recommend this variant for most OCR tasks.

## About LightOnOCR-2

LightOnOCR-2 is an efficient end-to-end 1B-parameter vision-language model for converting documents (PDFs, scans, images) into clean, naturally ordered text without relying on brittle pipelines. This second version is trained on a larger and higher-quality corpus with stronger French, arXiv, and scan coverage, improved LaTeX handling, and cleaner normalization. LightOnOCR-2 achieves state-of-the-art performance on OlmOCR-Bench while being ~9× smaller and significantly faster than competing approaches.

## Highlights

* ⚡ **Speed:** 3.3× faster than Chandra OCR, 1.7× faster than OlmOCR, 5× faster than dots.ocr, 2× faster than PaddleOCR-VL-0.9B, 1.73× faster than DeepSeekOCR
* 💸 **Efficiency:** Processes 5.71 pages/s on a single H100 (~493k pages/day) for **<$0.01 per 1,000 pages**
* 🧠 **End-to-End:** Fully differentiable, no external OCR pipeline
* 🧾 **Versatile:** Handles tables, receipts, forms, multi-column layouts, and math notation
* 📍 **Image detection:** Predicts bounding boxes for embedded images (bbox variants)

---

📄 **[Paper]( https://arxiv.org/pdf/2601.14251)** | 📝 **[Blog Post](https://huggingface.co/blog/lightonai/lightonocr-2)** | 🚀 **[Demo](https://huggingface.co/spaces/lightonai/LightOnOCR-2-1B-Demo)** | 📊 **[Dataset](https://huggingface.co/datasets/lightonai/LightOnOCR-mix-0126)** | 📊 **[BBox Dataset](https://huggingface.co/datasets/lightonai/LightOnOCR-bbox-mix-0126)** | 📓 **[Finetuning Notebook](https://colab.research.google.com/drive/1WjbsFJZ4vOAAlKtcCauFLn_evo5UBRNa?usp=sharing)** | **[LightOn blog entry](https://www.lighton.ai/lighton-blogs/lighton-opens-a-new-field-for-ai-with-lightonocr-2-document-intelligence)**

---

## Model Variants

| Variant | Description |
|---------|-------------|
| **[LightOnOCR-2-1B](https://huggingface.co/lightonai/LightOnOCR-2-1B)** | Best OCR model  |
| **[LightOnOCR-2-1B-base](https://huggingface.co/lightonai/LightOnOCR-2-1B-base)** | Base model, ideal for fine-tuning |
| **[LightOnOCR-2-1B-bbox](https://huggingface.co/lightonai/LightOnOCR-2-1B-bbox)** | Best model with image bounding boxes |
| **[LightOnOCR-2-1B-bbox-base](https://huggingface.co/lightonai/LightOnOCR-2-1B-bbox-base)** | Base bbox model, ideal for fine-tuning |
| **[LightOnOCR-2-1B-ocr-soup](https://huggingface.co/lightonai/LightOnOCR-2-1B-ocr-soup)** | Merged variant for extra robustness |
| **[LightOnOCR-2-1B-bbox-soup](https://huggingface.co/lightonai/LightOnOCR-2-1B-bbox-soup)** | Merged variant: OCR + bbox combined |

---

## Benchmarks

<div align="center">
  <img src="benchmark.png" alt="OlmOCR-Bench Results" width="900"/>
</div>

*See the [paper](https://arxiv.org/pdf/2601.14251) for full benchmark details and methodology.*

---

## Usage with Transformers

> **Note:** LightOnOCR-2 is avaible in latest transformers release starting from v5.

```bash
uv pip install transformers # => 5.0.0
uv pip install pillow pypdfium2
```

```python
import torch
from transformers import LightOnOcrForConditionalGeneration, LightOnOcrProcessor

device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float32 if device == "mps" else torch.bfloat16

model = LightOnOcrForConditionalGeneration.from_pretrained("lightonai/LightOnOCR-2-1B", torch_dtype=dtype).to(device)
processor = LightOnOcrProcessor.from_pretrained("lightonai/LightOnOCR-2-1B")

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

## Usage with vLLM

```bash
vllm serve lightonai/LightOnOCR-2-1B \
    --limit-mm-per-prompt '{"image": 1}' --mm-processor-cache-gb 0 --no-enable-prefix-caching
```

```python
import base64
import requests
import pypdfium2 as pdfium
import io

ENDPOINT = "http://localhost:8000/v1/chat/completions"
MODEL = "lightonai/LightOnOCR-2-1B"

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

---

## Rendering and Preprocessing Tips

* Render PDFs at 200 DPI to images using a target longest dimension of **1540px**
* Maintain aspect ratio to preserve text geometry

---

## Fine-tuning

LightOnOCR-2 is fully differentiable and supports:

* LoRA fine-tuning
* Domain adaptation (receipts, scientific articles, forms, etc.)
* Multilingual fine-tuning with task-specific corpora

For fine-tuning, we recommend starting with the **[LightOnOCR-2-1B-base](https://huggingface.co/lightonai/LightOnOCR-2-1B-base)** variant.

---

## License

Apache License 2.0

---

## Acknowlegments

The project received funding from the BPI Scribe project.

---

## Citation

```bibtex
@misc{lightonocr2_2026,
  title        = {LightOnOCR: A 1B End-to-End Multilingual Vision-Language Model for State-of-the-Art OCR},
  author       = {Said Taghadouini and Adrien Cavaill\`{e}s and Baptiste Aubertin},
  year         = {2026},
  howpublished = {\url{https://arxiv.org/abs/2601.14251}}
}
```

[![Downloads](https://img.shields.io/badge/dynamic/json?url=https://huggingface.co/api/models/lightonai/LightOnOCR-2-1B&query=downloads&label=Downloads&color=blue)](https://huggingface.co/lightonai/LightOnOCR-2-1B)
[![EU](https://img.shields.io/badge/🇪🇺%20Made%20in-Europe-blue)](https://huggingface.co/lightonai)
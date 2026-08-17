---
license: apache-2.0
license_link: LICENSE
language:
  - multilingual
tags:
  - vision-language
  - ocr
  - document-intelligence
  - qianfan
pipeline_tag: image-text-to-text
library_name: transformers
model-index:
  - name: Qianfan-OCR
    results:
      - task:
          type: document-parsing
          name: Document Parsing
        dataset:
          name: OmniDocBench v1.5
          type: opendatalab/OmniDocBench
        metrics:
          - type: overall
            value: 93.12
            name: Overall Score
      - task:
          type: ocr
          name: OCR
        dataset:
          name: OlmOCR Bench
          type: allenai/olmOCR-bench
        metrics:
          - type: accuracy
            value: 79.8
            name: Overall Score
      - task:
          type: ocr
          name: OCR
        dataset:
          name: OCRBench
          type: echo840/OCRBench
        metrics:
          - type: accuracy
            value: 880
            name: Score
---

<div align="center">

<h1>Qianfan-OCR</h1>

<h3>A Unified End-to-End Model for Document Intelligence</h3>

[**🤖 Demo**](https://huggingface.co/spaces/baidu/Qianfan-OCR-Demo) |
[**📄 Technical Report**](https://arxiv.org/abs/2603.13398) |
[**🖥️ Qianfan Platform**](https://cloud.baidu.com/product-s/qianfan_home) |
[**💻 GitHub**](https://github.com/baidubce/Qianfan-VL) |
[**🧩 Skill**](https://github.com/baidubce/skills/tree/develop/skills/qianfanocr-document-intelligence)

</div>

## Introduction

**Qianfan-OCR** is a **4B-parameter end-to-end document intelligence model** developed by the Baidu Qianfan Team. It unifies document parsing, layout analysis, and document understanding within a single vision-language architecture.

Unlike traditional multi-stage OCR pipelines that chain separate layout detection, text recognition, and language comprehension modules, Qianfan-OCR performs **direct image-to-Markdown conversion** and supports a broad range of prompt-driven tasks — from structured document parsing and table extraction to chart understanding, document question answering, and key information extraction — all within one model.

### Key Highlights

- 🏆 **#1 End-to-End Model on OmniDocBench v1.5** — Achieves **93.12** overall score, surpassing DeepSeek-OCR-v2 (91.09), Gemini-3 Pro (90.33), and all other end-to-end models
- 🏆 **#1 End-to-End Model on OlmOCR Bench** — Scores **79.8**
- 🏆 **#1 on Key Information Extraction** — Overall mean score of **87.9** across five public KIE benchmarks, surpassing Gemini-3.1-Pro, Gemini-3-Pro, Seed-2.0, and Qwen3-VL-235B-A22B
- 🧠 **Layout-as-Thought** — An innovative optional thinking phase that recovers explicit layout analysis within the end-to-end paradigm via `⟨think⟩` tokens
- 🌍 **192 Languages** — Multilingual OCR support across diverse scripts
- ⚡ **Efficient Deployment** — Achieves **1.024 PPS** (pages per second) with W8A8 quantization on a single A100 GPU

## Architecture

Qianfan-OCR adopts the multimodal bridging architecture from [Qianfan-VL](https://arxiv.org/abs/2509.18189), consisting of three core components:

| Component | Details |
|---|---|
| **Vision Encoder** | Qianfan-ViT, 24 Transformer layers, AnyResolution design (up to 4K), 256 visual tokens per 448×448 tile, max 4,096 tokens per image |
| **Language Model** | Qwen3-4B (3.6B non-embedding), 36 layers, 2560 hidden dim, GQA (32 query / 8 KV heads), 32K context (extendable to 131K) |
| **Cross-Modal Adapter** | 2-layer MLP with GELU activation, projecting from 1024-dim to 2560-dim |

### Layout-as-Thought

A key innovation is **Layout-as-Thought**: an optional thinking phase triggered by `⟨think⟩` tokens, where the model generates structured layout representations (bounding boxes, element types, reading order) before producing final outputs.

This mechanism serves two purposes:
1. **Functional**: Recovers layout analysis capability within the end-to-end paradigm — users obtain structured layout results directly
2. **Enhancement**: Provides targeted accuracy improvements on documents with complex layouts, cluttered elements, or non-standard reading orders

> **When to use**: Enable thinking for heterogeneous pages with mixed element types (exam papers, technical reports, newspapers). Disable for homogeneous documents (single-column text, simple forms) for better results and lower latency.

## Benchmark Results

### OmniDocBench v1.5 (Document Parsing)

| Model | Type | Overall ↑ | TextEdit ↓ | FormulaCDM ↑ | TableTEDs ↑ | TableTEDss ↑ | R-orderEdit ↓ |
|---|---|---|---|---|---|---|---|
| **Qianfan-OCR (Ours)** | End-to-end | **93.12** | **0.041** | **92.43** | **91.02** | **93.85** | **0.049** |
| DeepSeek-OCR-v2 | End-to-end | 91.09 | 0.048 | 90.31 | 87.75 | 92.06 | 0.057 |
| Gemini-3 Pro | End-to-end | 90.33 | 0.065 | 89.18 | 88.28 | 90.29 | 0.071 |
| Qwen3-VL-235B | End-to-end | 89.15 | 0.069 | 88.14 | 86.21 | 90.55 | 0.068 |
| dots.ocr | End-to-end | 88.41 | 0.048 | 83.22 | 86.78 | 90.62 | 0.053 |
| PaddleOCR-VL 1.5 | Pipeline | 94.50 | 0.035 | 94.21 | 92.76 | 95.79 | 0.042 |

### General OCR Benchmarks

| Model | OCRBench | OCRBenchv2 (en/zh) | CCOCR-multilan | CCOCR-overall |
|---|---|---|---|---|
| **Qianfan-OCR (Ours)** | **880** | 56.0 / **60.77** | **76.7** | **79.3** |
| Qwen3-VL-4B | 873 | **60.68** / 59.13 | 74.2 | 76.5 |
| MonkeyOCR | 655 | 21.78 / 38.91 | 43.8 | 35.2 |
| DeepSeek-OCR | 459 | 15.98 / 38.31 | 32.5 | 27.6 |

### Document Understanding

| Benchmark | Qianfan-OCR | Qwen3-VL-4B | Qwen3-VL-2B |
|---|---|---|---|
| DocVQA | 92.8 | **94.9** | 92.7 |
| CharXiv_DQ | **94.0** | 81.8 | 69.7 |
| CharXiv_RQ | **85.2** | 48.5 | 41.3 |
| ChartQA | **88.1** | 83.3 | 78.3 |
| ChartQAPro | **42.9** | 36.2 | 24.5 |
| ChartBench | **85.9** | 74.9 | 73.2 |
| TextVQA | 80.0 | **81.8** | 79.9 |
| OCRVQA | **66.8** | 64.7 | 59.3 |

> 💡 Two-stage OCR+LLM systems score **0.0** on CharXiv (both DQ and RQ), demonstrating that chart structures discarded during text extraction are essential for reasoning.

### Key Information Extraction (KIE)

| Model | Overall | OCRBench KIE | OCRBenchv2 KIE (en) | OCRBenchv2 KIE (zh) | CCOCR KIE | Nanonets KIE (F1) |
|---|---|---|---|---|---|---|
| **Qianfan-OCR (Ours)** | **87.9** | 95.0 | 82.8 | **82.3** | 92.8 | **86.5** |
| Qwen3-VL-235B-A22B | 84.2 | 94.0 | 85.6 | 62.9 | **95.1** | 83.8 |
| Qwen3-4B-VL | 83.5 | 89.0 | 82.1 | 71.3 | 91.6 | 83.3 |
| Gemini-3.1-Pro | 79.2 | **96.0** | **87.8** | 63.4 | 72.5 | 76.1 |

### Inference Throughput

| Model | PPS (pages/sec) |
|---|---|
| **Qianfan-OCR (W8A8)** | **1.024** |
| Qianfan-OCR (W16A16) | 0.503 |
| MinerU 2.5 | 1.057 |
| MonkeyOCR-pro-1.2B | 0.673 |
| Dots OCR | 0.352 |

*All benchmarks on a single NVIDIA A100 GPU with vLLM 0.10.2.*

## Supported Tasks

Qianfan-OCR supports a comprehensive set of document intelligence tasks through prompt-driven control:

| Task Category | Specific Tasks |
|---|---|
| **Document Parsing** | Image-to-Markdown conversion, multi-page parsing, structured output (JSON/HTML) |
| **Layout Analysis** | Bounding box detection, element type classification (25 categories), reading order |
| **Table Recognition** | Complex table extraction (merged cells, rotated tables), HTML output |
| **Formula Recognition** | Inline and display math formulas, LaTeX output |
| **Chart Understanding** | Chart QA, trend analysis, data extraction from various chart types |
| **Key Information Extraction** | Receipts, invoices, certificates, medical records, ID cards |
| **Handwriting Recognition** | Chinese and English handwritten text |
| **Scene Text Recognition** | Street signs, product labels, natural scene text |
| **Multilingual OCR** | 192 languages including Latin, Cyrillic, Arabic, South/Southeast Asian, CJK scripts |

## Quick Start

### Basic Usage

```python
from transformers import AutoModelForImageTextToText, AutoProcessor
import torch
from PIL import Image

MODEL_PATH = "baidu/Qianfan-OCR"
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    device_map="auto",
).eval()
processor = AutoProcessor.from_pretrained(MODEL_PATH)

image = Image.open("./examples/document.png").convert("RGB")
prompt = "Parse this document to Markdown."
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": prompt},
        ],
    },
]

inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
).to(model.device)

with torch.no_grad():
    output_ids = model.generate(
        **inputs,
        max_new_tokens=512,
        do_sample=False,
    )

generated_ids = output_ids[:, inputs["input_ids"].shape[1]:]
response = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)
```

### With Layout-as-Thought (Thinking Mode)

Enable thinking mode by passing `enable_thinking=True` to `apply_chat_template`. The model will first generate structured layout analysis (bounding boxes, element types, reading order), then produce the final output.

```python
image = Image.open("./examples/complex_document.jpg").convert("RGB")
prompt = "Parse this document to Markdown."
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": prompt},
        ],
    },
]

inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
    enable_thinking=True,
).to(model.device)

with torch.no_grad():
    output_ids = model.generate(
        **inputs,
        max_new_tokens=16384,
        do_sample=False,
    )

generated_ids = output_ids[:, inputs["input_ids"].shape[1]:]
response = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)
```

### Key Information Extraction

```python
image = Image.open("./examples/invoice.jpg").convert("RGB")
prompt = "请从图片中提取以下字段信息：姓名、日期、总金额。使用标准JSON格式输出。"
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": prompt},
        ],
    },
]

inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
).to(model.device)

with torch.no_grad():
    output_ids = model.generate(
        **inputs,
        max_new_tokens=16384,
        do_sample=False,
    )

generated_ids = output_ids[:, inputs["input_ids"].shape[1]:]
response = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)
```

### vLLM Deployment

```bash
# Serve with vLLM for high-throughput inference
vllm serve baidu/Qianfan-OCR --trust-remote-code --hf-overrides '{"architectures": ["InternVLChatModel"]}'
```

## Skill

We provide a [Qianfan OCR Document Intelligence](https://github.com/baidubce/skills/tree/develop/skills/qianfanocr-document-intelligence) skill for image and PDF understanding workflows.

It can be used by users of OpenClaw, Claude Code, Codex, and other assistants that support this skill format.
This skill packages reusable instructions, scripts, and references so the agent can automatically apply Qianfan-powered document intelligence to tasks such as:

- document parsing to Markdown
- layout analysis
- element recognition
- general OCR
- key information extraction
- chart understanding
- document VQA

The skill is designed for visual understanding tasks over images and PDFs, and includes the execution flow needed to prepare inputs, choose the right analysis mode, and call the bundled CLI tools.

## Citation

```bibtex
@misc{dong2026qianfanocrunifiedendtoendmodel,
  title={Qianfan-OCR: A Unified End-to-End Model for Document Intelligence},
  author={Daxiang Dong and Mingming Zheng and Dong Xu and Chunhua Luo and Bairong Zhuang and Yuxuan Li and Ruoyun He and Haoran Wang and Wenyu Zhang and Wenbo Wang and Yicheng Wang and Xue Xiong and Ayong Zheng and Xiaoying Zuo and Ziwei Ou and Jingnan Gu and Quanhao Guo and Jianmin Wu and Dawei Yin and Dou Shen},
  year={2026},
  eprint={2603.13398},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://arxiv.org/abs/2603.13398},
}
```

## Acknowledgments

We thank the Baidu AI Cloud team for infrastructure support, the Baige and Kunlun teams for AI infrastructure assistance, and all contributors to the Qianfan platform.

## License

This project is licensed under the Apache License 2.0. See `LICENSE` for the
full license text.

Some bundled third-party source files are licensed under the MIT License. See
`NOTICE` for the file list and corresponding attribution details.

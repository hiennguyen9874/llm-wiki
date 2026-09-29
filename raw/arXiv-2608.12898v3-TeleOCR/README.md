---
license: apache-2.0
tags:
  - ocr
  - document-parsing
  - multimodal
library_name: transformers
pipeline_tag: image-text-to-text
language:
  - zh
  - en
---
<div align="center">

<h1 align="center">
TeleOCR: Navigating Document Parsing Across Digital and Camera-Captured Documents

</h1>

[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/caipeng328/TeleOCR)
[![TeleAI](https://img.shields.io/badge/webapp_on_teleai.com-blue?logo=data:image/png;base64,UklGRpICAABXRUJQVlA4WAoAAAAQAAAAFQAAGAAAQUxQSEwBAAABkGvb2rFXb5zauQCbVTrbNjt1tm3bObZt6zeObdvft4v30yVExASwkqKChaQVLH6f2vcKeHqAunMTHz9x/D9Y/+2cVtX1+dAbjLX8lck4cH1c37S4Z3DT/NznjkmlWs6lXv26sf/K0rFlmWzkwIGHOo6/qhvqaxdlN+Vnrt9Q6a8pvnPpNRqtTqPV6bUajUar/cXB/xsChfT71DISHCg+UzIjweRb5uOO/2KuLxw5duTS4w96Qf+aS89/BfBe193AUFXUFbuftx4DeHkELnsB/A0EZfPs1j0Ar099tz8D4LfbfQDsQuHmW3+Yv/pN5f0sgIcWS6Cf7dq1t2XHnu13Qc8R1/cUsOU1vq2C84sXIUm/OC6EzMXu5PiVQwghUW8prAUMM9SrLMLpvPwf/D9WnQl/2FGW67g/EWwQefw/cDnNlIg1StxXYE74AVZQOCAgAQAAkAcAnQEqFgAZAD7RVKZNqCQjojAYCAEAGglsAJ0zND+A2rdxh/l2DrrSwNZEPJb8c9uqnP90eUrVexSs2yAJSFsrsI8AAP03X4scCDMKfncvKAr9aIf33A4Lc9xfcBVOo9hotIZIL1kpgEs0hdr2CPz/BVzkPcV5X2+ZdiEn0NWI16mvKRFSI/HYHhAAT9NP3KwVp1une4gB+ernhg1Ly0KuLdqCAZXWQHJzTrrR8RNz79tgl7Aq8WHqxbOTfguubnUbMPaD4DfKY71NjLtozHqNKPSC6gxIS3UNlbGZT3m3zEus+sjwYwucztbFfyH6n4U8VoWfQf4UdhLuoylwhqzt+FoCGwH4pHiWv/pkL2Z/bt9h755P3YDljRFfAAAA&labelColor=white)](https://www.teleai.com.cn/docparse/DocumentParsing)
[![arXiv](https://img.shields.io/badge/TeleOCR-Technical%20Report-b31b1b.svg?logo=arXiv)](https://arxiv.org/abs/2608.12898)
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/caipeng328/TeleOCR/refs/heads/main/assets/score.png" width="800">
</div>

## 🔥 News
- **2026/09/10** - We have renamed NaviDC-OCR to TeleOCR, and all subsequent model iterations will be developed and released under the TeleOCR version.
- **2026/09/01** - We noticed that EMNLP 2026 is hosting the [Dr.DocBench Challenge](https://eval.ai/web/challenges/challenge-page/2717/overview), a document parsing competition. We evaluated NaviDC-OCR with its native weights, achieving better results than MinerU 2.5 Pro and PaddleOCR-VL 1.6. Detailed results are shown below **dr.docbench-challenge**. We welcome the use of NaviDC‑OCR for competitions. Going forward, we will continue to deliver competitive parsing models for the community.
- **2026/08/29** — Thanks to Nandraj for the GGUF conversion and llama.cpp support  [🔗 NaviDC-OCR-GGUF](https://huggingface.co/nandraj/NaviDC-OCR-GGUF), and to the community for sharing their experience deploying NaviDC-OCR on [Ascend 910B!](https://zhuanlan.zhihu.com/p/2078516899093155893)
- **2026/08/17** — NaviDC-OCR [model weights](https://huggingface.co/StarDoc-AI/NaviDC-OCR) and [technical report](https://arxiv.org/pdf/2608.12898) have been released.

## 📖 Introduction

**TeleOCR** is a lightweight (~1.2B parameters), open-source Vision-Language Model designed specifically for document parsing.

Unlike existing methods that mainly target either digital documents or camera-captured documents, TeleOCR unifies both scenarios within a single framework.

Compared with previous document parsing models, TeleOCR introduces

- Multi-node Consensus Voting (MCV) for automatic pseudo-label generation
- Geometry-aware document modeling for camera-captured documents
- Curvature-Guided Douglas-Peucker Sampling (CGDP)
- Image-to-image self-verification for automatic data refinement
- Progressive four-stage training pipeline
- Content-Structure Decoupled Learning for tables and formulas

These techniques enable TeleOCR to achieve state-of-the-art performance on both digital and camera-captured document benchmarks while remaining lightweight enough for practical deployment.

## 📊 Experimental Results

TeleOCR  achieves state-of-the-art performance on multiple public document parsing benchmarks.

### Layout Visualization of Distorted Documents
To evaluate the model's ability to understand complex document deformations, we conduct a visual evaluation on the public dewarping datasets DocUNet and DIR300, with representative results shown in Figure. TeleOCR directly performs layout and content parsing on distorted documents without dewarping preprocessing or a dedicated rectification model, demonstrating robust parsing under complex geometric deformations.
<div align="center">

<img src="https://raw.githubusercontent.com/caipeng328/TeleOCR/refs/heads/main/assets/dir300.png" width="800" alt="Parsing evaluation on the DIR300 dataset.">
<img src="https://raw.githubusercontent.com/caipeng328/TeleOCR/refs/heads/main/assets/docunet.png" width="800" alt="Parsing evaluation on the DocUNet dataset.">
</div>

---

## Dr.DocBench Challenge  

|模型|overall ↑|Text edit ↓|formula cdm ↑|Table teds ↑|order edit ↓|
|---|---|---|---|---|---|
|**Specialized VLMs**| | | | | |
|TeleOCR|67.96|0.1903|0.02|64.97|0.398|
|Mineru 2.5 pro|62.26|0.3402|0.04|67.75|0.356|
|OvisOCR2|59.25|0.3883|0.00|61.59|0.3791|
|PaddleOCRvl 1.6|55.11 | 0.4364 | 0.21 | 51.34 |0.412 |


---

### [OmniDocBench v1.6](https://github.com/opendatalab/OmniDocBench)

| Model Type | Methods | Param | Overall ↑ | Text Edit ↓ | Formula CDM ↑ | Table TEDS ↑ | Table TEDS-S ↑ | Read Order Edit ↓ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Specialized VLMs** | **TeleOCR** | **1.2B** | **96.87** | <u>0.027</u> | 96.36 | **97.05** | **98.52** | <u>0.122</u> |
| | OvisOCR2 | 0.8B | <u>96.58</u> |  **0.025** | **97.53** | <u>94.76</u> | <u>97.16</u> | **0.111** |
| | PaddleOCR-VL-1.6 | 0.9B | 96.33 | 0.033 | <u>97.49</u> | <u>94.76</u> | 97.11 | 0.127 |
| | MinerU2.5-Pro | 1.2B | 95.75 | 0.036 | 97.45 | 93.42 | 95.92 | 0.120 |
| | GLM-OCR | 0.9B | 95.22 | 0.044 | 97.18 | 92.83 | 95.39 | 0.133 |
| | PaddleOCR-VL-1.5 | 0.9B | 94.87 | 0.038 | 96.69 | 91.67 | 94.37 | 0.130 |
| | HunyuanOCR-1.5 | 1B | 94.74 | 0.033 | 97.49 | 94.76 | 97.11 | 0.127 |
| | PaddleOCR-VL | 0.9B | 94.11 | 0.040 | 95.70 | 90.65 | 93.74 | 0.135 |
| | Youtu-Parsing | 2.5B | 93.68 | 0.044 | 93.45 | 92.02 | 95.00 | 0.116 |
| | Logics-Parsing-v2 | 4B | 93.27 | 0.041 | 95.47 | 88.42 | 91.98 | 0.137 |
| | FireRed-OCR | 2B | 93.20 | 0.037 | 95.27 | 88.04 | 91.06 | 0.131 |
| | MinerU2.5 | 1.2B | 92.98 | 0.045 | 95.59 | 87.88 | 91.47 | 0.130 |
| | OpenDoc-0.1B | 0.1B | 90.64 | 0.049 | 92.93 | 83.88 | 87.45 | 0.140 |
| | dots.ocr | 3B | 90.50 | 0.048 | 89.12 | 87.18 | 90.58 | 0.138 |
| | DeepSeek-OCR 2 | 3B | 90.17 | 0.050 | 91.59 | 83.89 | 87.75 | 0.144 |
| | HunyuanOCR | 1B | 89.87 | 0.089 | 87.44 | 91.01 | 93.23 | 0.171 |
| | Dolphin-v2 | 3B | 89.34 | 0.069 | 90.53 | 84.40 | 87.44 | 0.150 |
| | OCRVerse | 4B | 88.44 | 0.063 | 89.14 | 82.44 | 86.27 | 0.163 |
| | MonkeyOCR-pro-3B | 3B | 88.43 | 0.074 | 88.33 | 84.35 | 88.62 | 0.189 |
| **General VLMs** | Ovis2.6-30B-A3B | 30B | 93.62 | 0.035 | 94.93 | 89.44 | 92.40 | 0.135 |
| | Gemini 3 Pro | -- | 92.85 | 0.064 | 95.83 | 89.15 | 92.96 | 0.165 |
| | Gemini 3 Flash | -- | 92.58 | 0.066 | 95.03 | 89.29 | 93.51 | 0.173 |
| | Qwen3-VL-235B | 235B | 89.78 | 0.063 | 92.53 | 83.07 | 86.75 | 0.166 |
| | GPT-5.2 | -- | 86.52 | 0.114 | 88.00 | 82.95 | 87.93 | 0.193 |
| | InternVL3.5-241B | 241B | 83.61 | 0.130 | 89.52 | 74.35 | 79.78 | 0.215 |

---


### [Wild_OmniDocBench](https://github.com/VirtualLUOUCAS/Wild_OmniDocBench) 
| Model Type          | Methods           | Param |    Overall ↑ | Text Edit ↓ | Formula CDM ↑ | Table TEDS ↑ | Table TEDS-S ↑ | Read Order Edit ↓ |
| ------------------- | ----------------- | ----: | -----------: | ----------: | ------------: | -----------: | -------------: | ----------------: |
| **Decoupled VLMs**  | **TeleOCR**    |  1.2B |    **88.53** |  **0.1173** |         88.26 |    **89.05** |      **92.14** |        **0.2011** |
|                     | PaddleOCR-VL-1.6  |  0.9B |        87.36 |      0.1369 |         88.42 | <u>85.76</u> |   <u>90.14</u> |            0.2057 |
|                     | MinerU2.5-Pro     |  1.2B |        87.33 |      0.1362 |  <u>90.15</u> |        85.46 |          90.12 |     <u>0.2013</u> |
|                     | GLM-OCR           |  0.9B |        85.08 |      0.1514 |         89.09 |        81.31 |          85.90 |            0.2228 |
|                     | PaddleOCR-VL-1.5  |  0.9B |        84.64 |      0.1461 |         86.72 |        81.80 |          86.52 |            0.2138 |
| **End-to-End VLMs** | OvisOCR2          |  0.8B | <u>87.91</u> |       0.129 |     **90.37** |        85.13 |          89.11 |            0.2021 |
|                     | dots.ocr          |    3B |        81.84 |      0.1483 |          85.0 |        75.32 |          80.20 |            0.2200 |
|                     | HunyuanOCR-1.5    |    1B |        77.62 |      0.1979 |         85.12 |        67.54 |          70.67 |            0.2750 |
|                     | Logics-Parsing-v2 |    4B |        77.10 |      0.4029 |          91.4 |        80.19 |          87.16 |            0.2355 |

---


### [PureDocBench](https://github.com/zhihengli-casia/puredocbench/)
| Model Type         | Model             | Clean Overall ↑ | Clean Text ↓ | Clean Formula ↑ | Clean Table ↑ | Digital Degraded Overall ↑ | Digital Degraded Text ↓ | Digital Degraded Formula ↑ | Digital Degraded Table ↑ | Real Degraded Overall ↑ | Real Degraded Text ↓ | Real Degraded Formula ↑ | Real Degraded Table ↑ |
| ------------------ | ----------------- | --------------: | -----------: | --------------: | ------------: | -------------------------: | ----------------------: | -------------------------: | -----------------------: | ----------------------: | -------------------: | ----------------------: | --------------------: |
| **Decoupled VLM**  | **TeleOCR**    |       **86.90** |    **0.111** |       **81.01** |     **91.09** |               <u>77.47</u> |                   0.206 |                  **72.59** |                    80.45 |               **70.85** |         <u>0.302</u> |               **65.11** |             **77.66** |
|                    | DotsMOCR          |           76.27 |        0.151 |           66.23 |         77.65 |                      73.16 |            <u>0.198</u> |                      64.32 |                    74.95 |                   61.73 |                0.312 |                   54.39 |                 61.97 |
|                    | MinerU2.5-Pro     |           75.87 |        0.222 |           65.14 |         84.68 |                      71.77 |                   0.272 |                      61.79 |                    80.73 |                   62.56 |                0.375 |                   52.70 |                 72.47 |
|                    | YouTu-Parsing     |           75.02 |        0.230 |           67.34 |         80.74 |                      69.66 |                   0.270 |                      61.44 |                    74.49 |                   60.29 |                0.360 |                   52.20 |                 64.69 |
|                    | PaddleOCR-VL-1.5  |           73.01 |        0.266 |           63.53 |         82.12 |                      66.73 |                   0.339 |                      58.03 |                    76.07 |                   60.50 |                0.398 |                   54.00 |                 67.33 |
|                    | GLM-OCR           |           68.65 |        0.314 |           57.89 |         79.44 |                      63.06 |                   0.383 |                      53.23 |                    74.21 |                   58.31 |                0.433 |                   50.34 |                 67.83 |
|                    | Dolphin-v2        |           65.90 |        0.342 |           59.80 |         72.12 |                      60.24 |                   0.393 |                      52.20 |                    67.86 |                   44.92 |                0.553 |                   39.98 |                 50.04 |
|                    | MonkeyOCR-pro-3B  |           62.23 |        0.346 |           48.46 |         72.83 |                      57.40 |                   0.397 |                      45.57 |                    66.32 |                   46.49 |                0.511 |                   38.18 |                 52.43 |
| **End-to-End VLM** | OvisOCR2          |    <u>82.14</u> | <u>0.149</u> |    <u>71.29</u> |  <u>90.12</u> |                  **77.77** |               **0.192** |               <u>67.87</u> |                **84.71** |                   66.61 |                0.316 |                   57.64 |          <u>73.79</u> |
|                    | FD-RL             |           78.38 |        0.193 |           68.21 |         86.22 |                      76.33 |                   0.214 |                      67.16 |             <u>83.22</u> |            <u>67.04</u> |            **0.298** |                   58.82 |                 72.08 |
|                    | Logics-Parsing-v2 |           76.35 |        0.213 |           67.67 |         82.67 |                      73.85 |                   0.248 |                      67.33 |                    79.02 |                   67.64 |                0.304 |            <u>61.65</u> |                 71.64 |
|                    | dots.ocr          |           72.01 |        0.248 |           61.37 |         79.51 |                      65.95 |                   0.307 |                      56.67 |                    71.86 |                   55.68 |                0.403 |                   47.70 |                 59.63 |
|                    | Qianfan-OCR       |           57.22 |        0.370 |           49.79 |         58.83 |                      50.85 |                   0.438 |                      44.41 |                    51.96 |                   45.06 |                0.494 |                   39.08 |                 45.53 |
| **General VLMs**   | Qwen3-VL-8B       |           72.44 |        0.261 |           65.10 |         78.35 |                      72.03 |                   0.266 |                      64.88 |                    77.82 |                   62.73 |                0.342 |                   55.55 |                 66.81 |
|                    | Kimi K2.6         |           72.32 |        0.303 |           66.93 |         80.30 |                      69.95 |                   0.322 |                      64.69 |                    77.31 |                   68.02 |                0.335 |                   62.44 |                 75.14 |
|                    | Gemini-3.1-Pro    |           70.04 |        0.306 |           65.63 |         75.08 |                      69.28 |                   0.322 |                      65.81 |                    74.24 |               **71.98** |                0.300 |                   68.62 |                 77.26 |
|                    | Qwen3.5-397B-A17B |           69.12 |        0.233 |           65.26 |         65.40 |                      68.34 |                   0.244 |                      63.91 |                    65.53 |                   62.70 |                0.287 |                   60.70 |                 56.12 |

---


### [ICDAR2026 Sci-ImageMiner](https://sites.google.com/view/sci-imageminer/)
|     # | Team            |       RMS |      TEDS |  Weighted |
| ----: | --------------- | --------: | --------: | --------: |
| **1** | **TeleOCR**  | **17.23** | **66.39** | **41.81** |
|     2 | VLMinators      |     17.29 |     64.31 |     40.80 |
|     3 | Ricoh_SRCB      |     16.23 |     61.12 |     38.67 |
|     4 | Vassilis Sioros |     14.94 |     55.20 |     35.07 |
|     5 | DocMiner        |     12.67 |     53.72 |     33.19 |
|     6 | Qwen3 VL 8B     |     14.08 |     57.86 |     35.97 |

---

## 🚀 Installation

```bash
pip install transformers torch pillow
```

## Quick Start

```python
import html
import itertools
import json
import re
from dataclasses import dataclass

from PIL import Image
import torch
from transformers import AutoProcessor, AutoModel

@dataclass
class ContentBlock:
    type: str
    bbox: list[float]
    angle: int | None = None
    content: str | None = None


@dataclass
class TableCell:
    text: str
    start_row_offset_idx: int
    end_row_offset_idx: int
    start_col_offset_idx: int
    end_col_offset_idx: int
    row_span: int = 1
    col_span: int = 1


OTSL_NL = "<nl>"
OTSL_FCEL = "<fcel>"
OTSL_ECEL = "<ecel>"
OTSL_LCEL = "<lcel>"
OTSL_UCEL = "<ucel>"
OTSL_XCEL = "<xcel>"
OTSL_TOKENS = [OTSL_NL, OTSL_FCEL, OTSL_ECEL, OTSL_LCEL, OTSL_UCEL, OTSL_XCEL]


def _otsl_extract_tokens_and_text(text: str):
    pattern = "(" + "|".join(map(re.escape, OTSL_TOKENS)) + ")"
    tokens = re.findall(pattern, text)
    parts = [part for part in re.split(pattern, text) if part.strip()]
    return tokens, parts


def _count_right(rows, row_idx, col_idx, tokens):
    span = 0
    while col_idx < len(rows[row_idx]) and rows[row_idx][col_idx] in tokens:
        span += 1
        col_idx += 1
    return span


def _count_down(rows, row_idx, col_idx, tokens):
    span = 0
    while row_idx < len(rows) and col_idx < len(rows[row_idx]) and rows[row_idx][col_idx] in tokens:
        span += 1
        row_idx += 1
    return span


def _otsl_parse_texts(parts, tokens):
    rows = [list(row) for is_nl, row in itertools.groupby(tokens, lambda token: token == OTSL_NL) if not is_nl]
    if not rows:
        return [], []

    max_cols = max(len(row) for row in rows)
    for row in rows:
        row.extend([OTSL_ECEL] * (max_cols - len(row)))

    cells = []
    row_idx = 0
    col_idx = 0
    for idx, part in enumerate(parts):
        if part in (OTSL_FCEL, OTSL_ECEL):
            cell_text = ""
            right_offset = 1
            if part != OTSL_ECEL and idx + 1 < len(parts) and parts[idx + 1] not in OTSL_TOKENS:
                cell_text = parts[idx + 1].strip()
                right_offset = 2

            next_right = parts[idx + right_offset] if idx + right_offset < len(parts) else ""
            next_bottom = rows[row_idx + 1][col_idx] if row_idx + 1 < len(rows) and col_idx < len(rows[row_idx + 1]) else ""
            col_span = 1 + (_count_right(rows, row_idx, col_idx + 1, {OTSL_LCEL, OTSL_XCEL}) if next_right in {OTSL_LCEL, OTSL_XCEL} else 0)
            row_span = 1 + (_count_down(rows, row_idx + 1, col_idx, {OTSL_UCEL, OTSL_XCEL}) if next_bottom in {OTSL_UCEL, OTSL_XCEL} else 0)
            cells.append(TableCell(
                text=cell_text,
                row_span=row_span,
                col_span=col_span,
                start_row_offset_idx=row_idx,
                end_row_offset_idx=row_idx + row_span,
                start_col_offset_idx=col_idx,
                end_col_offset_idx=col_idx + col_span,
            ))
        if part in (OTSL_FCEL, OTSL_ECEL, OTSL_LCEL, OTSL_UCEL, OTSL_XCEL):
            col_idx += 1
        elif part == OTSL_NL:
            row_idx += 1
            col_idx = 0
    return cells, rows


def convert_otsl_to_html(otsl_content: str) -> str:
    if otsl_content.startswith("<table") and otsl_content.endswith("</table>"):
        return otsl_content

    tokens, parts = _otsl_extract_tokens_and_text(otsl_content)
    cells, rows = _otsl_parse_texts(parts, tokens)
    if not cells or not rows:
        return ""

    grid = [[None for _ in range(len(rows[0]))] for _ in range(len(rows))]
    for cell in cells:
        for row_idx in range(cell.start_row_offset_idx, min(cell.end_row_offset_idx, len(rows))):
            for col_idx in range(cell.start_col_offset_idx, min(cell.end_col_offset_idx, len(rows[0]))):
                grid[row_idx][col_idx] = cell

    html_rows = []
    for row_idx, row in enumerate(grid):
        html_rows.append("<tr>")
        for col_idx, cell in enumerate(row):
            if cell is None or cell.start_row_offset_idx != row_idx or cell.start_col_offset_idx != col_idx:
                continue
            attrs = ""
            if cell.row_span > 1:
                attrs += f' rowspan="{cell.row_span}"'
            if cell.col_span > 1:
                attrs += f' colspan="{cell.col_span}"'
            html_rows.append(f"<td{attrs}>{html.escape(cell.text.strip())}</td>")
        html_rows.append("</tr>")
    return "<table>" + "".join(html_rows) + "</table>"


def post_process(blocks: list[ContentBlock]) -> list[ContentBlock]:
    for block in blocks:
        if block.type == "table" and block.content:
            block.content = convert_otsl_to_html(block.content)
        elif block.type == "equation" and block.content:
            content = block.content.strip()
            content = content.removeprefix("\\[").removesuffix("\\]").strip()
            if not (content.startswith("$") and content.endswith("$")):
                content = f"$${content}$$"
            block.content = content
    return [block for block in blocks if block.type != "equation_block"]

def infer(image: Image.Image, prompt: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": [
            {"type": "image"},
            {"type": "text", "text": prompt},
        ]},
    ]
    chat_prompt = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = processor(
        text=[chat_prompt],
        images=[image.convert("RGB")],
        padding=True,
        return_tensors="pt",
    ).to(device=model.device, dtype=model.dtype)
    output_ids = model.generate(
        **inputs,
        use_cache=True,
        max_new_tokens=4096,
        do_sample=False,
    )
    output_ids = output_ids.cpu().tolist()[0][len(inputs.input_ids[0]):]
    return processor.batch_decode(
        [output_ids],
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0].strip()



processor = AutoProcessor.from_pretrained("StarDoc-AI/TeleOCR", trust_remote_code=True, use_fast=True)
model = AutoModel.from_pretrained(
    "StarDoc-AI/TeleOCR",
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
).cuda().eval()

# text
image=Image.open("./assets/text.png").convert("RGB")
raw_text = infer(image, "Please output the text content from the image.")
print(raw_text.strip())

# table
image=Image.open("./assets/table.png").convert("RGB")
raw_otsl = infer(image, "This is the image of a table. Please output the table in OTSL format.")
print(convert_otsl_to_html(raw_otsl))

# formula 
image=Image.open("./assets/formula.png").convert("RGB")
raw_formula = infer(image, "Please write out the expression of the formula in the image using LaTeX format.")
formula_block = ContentBlock("equation", [0.0, 0.0, 1.0, 1.0], content=raw_formula)
formula = post_process([formula_block])[0].content
print(formula)

#code
image=Image.open("./assets/code.png").convert("RGB")
raw_code = infer(image,"The image contains a code snippet, please output the parsing result.")
print(raw_code.strip())

# layout
image=Image.open("./assets/layout.jpg").convert("RGB")
image = image.resize((1036, 1036), Image.Resampling.BICUBIC)
raw_layout = infer(image, "Analyze the image layout.")
print(raw_layout.strip())

# Distorted document layout
layout_image = Image.open("./assets/layout_distorted.jpg").convert("RGB")
layout_image = layout_image.resize((1036, 1036), Image.Resampling.BICUBIC)
raw_layout = infer(layout_image, "\nMulti-point Layout Segmentation Analysis.")
print(raw_layout.strip())

#scientific figure
image=Image.open("./assets/scientific_figure.png").convert("RGB")
raw_scientific_figure = infer(image, "This is a scientific figure. Please extract the table implied by this figure.")
print(convert_otsl_to_html(raw_scientific_figure))
```

If you would like to perform complete document parsing, please refer to our GitHub repository: https://github.com/caipeng328/NaviDC-OCR.

## Citation

```bibtex
@article{teleocr,
  title={TeleOCR: Navigating Document Parsing Across Digital and Camera-Captured Documents},
  author={Cai, Peng and Zou, Zhaofan and Liu, Shifa and Wang, Yikun and Tang, Jiawei and Yang, Kaicheng and Tong, Meng and He, Zhongjiang and Sun, Hao},
  journal={arXiv preprint arXiv:2608.12898},
  year={2026}
}
```
## Community Contributions

Thanks to Nandraj for the GGUF conversion and llama.cpp support!  [🔗 NaviDC-OCR-GGUF](https://huggingface.co/nandraj/NaviDC-OCR-GGUF)

## Acknowledgements

TeleOCR is built upon

- MinerU
- Qwen2.5-VL
- Qwen3
- Transformers
- PyTorch
- FlashAttention

We sincerely thank these excellent open-source projects.

---

## Contact

If you have any questions, feel free to open an issue or contact us.	
---
license: apache-2.0
base_model: PaddlePaddle/PaddleOCR-VL-1.6
base_model_relation: finetune
library_name: transformers
pipeline_tag: image-text-to-text
language:
  - vi
  - en
  - zh
datasets:
  - 5CD-AI/Viet-Handwriting-OCR-v2
tags:
  - paddleocr
  - ocr
  - document-ai
  - document-parsing
  - vietnamese
  - image-to-text
---

<p align="center">
  <img alt="SenOCR-Vi" src="https://huggingface.co/VietAlphaLabs/SenOCR-Vi/resolve/main/banner.png">
</p>

<p align="center">
  <a href="https://vietalpha.org/research/senocr-vi"><strong>Research page</strong></a> ·
  <a href="https://huggingface.co/VietAlphaLabs"><strong>VietAlpha Lab</strong></a>
</p>

<br>

**SenOCR-Vi** is a Vietnamese-specialized document OCR model built on [PaddleOCR-VL-1.6](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6).

The model retains the approximately **0.96B-parameter** PaddleOCR-VL-1.6 architecture while specializing recognition for Vietnamese documents. On the corrected 160-page Vietnamese evaluation population, SenOCR-Vi reaches **82.83 Vietnamese document composite** and **86.7% Vietnamese text recognition** under `1 - Edit_dist`.

Fine-tuning updated **12.09M parameters, 1.26% of the model**, and completed on a single NVIDIA A10G in about two hours.

SenOCR-Vi is intended primarily for Vietnamese printed documents, photographed pages, archival material, textbooks, and document-ingestion workflows.

# Highlights

* **Vietnamese-first accuracy:** **82.83** Vietnamese document composite and **86.7%** Vietnamese text recognition under `1 - Edit_dist`, **1.93 points** ahead of the PaddleOCR-VL-1.6 base on Vietnamese.
* **Small and self-contained:** **0.959B** total parameters in a single merged FP32 checkpoint — no separate adapter branch is needed at inference.
* **Cheap to reproduce:** decoder-only **LoRA rank 32 / alpha 64** over **12.09M** trainable parameters (**1.2614%** of the model), trained on **1 x NVIDIA A10G** in about **2 h 01 m**.
* **Verified merge:** **128/128** exact decoded matches between base-plus-adapter inference and the merged release in FP32 merge-equivalence validation.
* **Drop-in interface:** identical to PaddleOCR-VL-1.6 — usable through `transformers` for element-level recognition, or as the VLM recognition model inside the PaddleOCR-VL 1.6 page-parsing pipeline.
* **Permissive Apache 2.0 license:** commercial use, customization and redistribution without copyleft restrictions.

---

# Inference examples

SenOCR-Vi follows the PaddleOCR-VL-1.6 model interface.

## Transformers

For direct OCR recognition:

```bash
pip install "transformers>=5.0.0" torch pillow
```

```python
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

model_id = "VietAlphaLabs/SenOCR-Vi"
image_path = "document.png"

device = "cuda" if torch.cuda.is_available() else "cpu"

model = (
    AutoModelForImageTextToText
    .from_pretrained(model_id, torch_dtype=torch.float32)
    .to(device)
    .eval()
)
processor = AutoProcessor.from_pretrained(model_id)

image = Image.open(image_path).convert("RGB")

messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": "OCR:"},
        ],
    }
]

inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
).to(device)

outputs = model.generate(**inputs, max_new_tokens=512)
text = processor.decode(
    outputs[0][inputs["input_ids"].shape[-1]:-1]
)

print(text)
```

> [!NOTE]
> The qualified benchmark artifact was served in FP32. Lower-precision deployment should be validated separately for the target environment.

## PaddleOCR

For page-level document parsing, use SenOCR-Vi as the VLM recognition model inside the PaddleOCR-VL 1.6 pipeline.

Install the appropriate PaddlePaddle build for the target system, then:

```bash
pip install -U "paddleocr[doc-parser]>=3.6.0" huggingface_hub
```

```python
from pathlib import Path
from huggingface_hub import snapshot_download
from paddleocr import PaddleOCRVL

model_dir = snapshot_download(repo_id="VietAlphaLabs/SenOCR-Vi")

output_dir = Path("./output")
output_dir.mkdir(parents=True, exist_ok=True)

pipeline = PaddleOCRVL(
    pipeline_version="v1.6",
    vl_rec_model_dir=model_dir,
)

output = pipeline.predict("document.png")

for result in output:
    result.print()
    result.save_to_json(save_path=output_dir)
    result.save_to_markdown(save_path=output_dir)
```

PaddleOCR-VL also supports PDF input, layout analysis, document restructuring, and optimized serving backends. See the [PaddleOCR-VL documentation](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PaddleOCR-VL.en.md).

# Download the model

```shell
hf download VietAlphaLabs/SenOCR-Vi --local-dir SenOCR-Vi/
```

---

# Evaluation

## Vietnamese

SenOCR-Vi is evaluated on the corrected Vietnamese page population used for the MDPBench document-parsing comparison.

| Model | Parameters | Vietnamese composite |
|---|---:|---:|
| chandra-ocr-2 | 5B | **85.60** |
| MonkeyOCRv2-B-Parsing | 0.7B | **83.20** |
| Claude-Sonnet-4.6 | Undisclosed | **83.10** |
| **SenOCR-Vi** | **0.959B** | **82.83** |
| ChatGPT-5.2-2025-12-11 | Undisclosed | **82.10** |
| PaddleOCR-VL-1.6 | ~0.9B | **80.90** |

External model scores are taken from the [MDPBench official leaderboard](https://github.com/Yuliang-Liu/MultimodalOCR/blob/main/MDPBench/README.md). Public parameter counts are shown where available; Claude-Sonnet-4.6 and ChatGPT-5.2 do not disclose model size.

At **0.959B parameters**, SenOCR-Vi is **0.27 points behind Claude-Sonnet-4.6**, **0.73 points ahead of ChatGPT-5.2**, and **1.93 points ahead of PaddleOCR-VL-1.6** on Vietnamese. chandra-ocr-2 scores 2.77 points higher at 5B parameters, about **5.2 times** SenOCR-Vi's parameter count.

## Text recognition

On the 160-page Vietnamese slice:

| Metric | SenOCR-Vi |
|---|---:|
| Page-level `text_block` Edit_dist | **0.13305** |
| `1 - Edit_dist` | **86.7%** |

The **86.7%** figure is a Vietnamese text-recognition score under `1 - Edit_dist`; the **82.83** document composite also includes structured document elements.

## Document conditions

On the controlled English/Vietnamese/Simplified Chinese population:

| Condition | Composite |
|---|---:|
| Digital documents | **91.1** |
| Photographed documents | **80.8** |

## Multilingual

SenOCR-Vi remains usable outside Vietnamese, although multilingual aggregate performance is not the primary optimization target.

| Language | Composite |
|---|---:|
| English | **82.08** |
| Vietnamese | **82.83** |
| Simplified Chinese | **84.03** |
| EN/VI/ZH macro | **82.98** |

For comparison, PaddleOCR-VL-1.6 records an EN/VI/ZH macro of **83.43** from the corresponding MDPBench language columns.

## Benchmark note

SenOCR-Vi scores are re-aggregated over the actual evaluation-page population.

The original project scorer emitted three additional non-page rows because of a documented key-parsing defect. All three affected the Vietnamese population. Removing those phantom rows gives the reported **82.83 Vietnamese composite**.

The **82.98 EN/VI/ZH macro** is a three-language summary only. It is not the full MDPBench overall score.

---

# Training

SenOCR-Vi was initialized as a fresh decoder-only LoRA fine-tune of PaddleOCR-VL-1.6.

| Setting | Value |
|---|---:|
| Base model | PaddlePaddle/PaddleOCR-VL-1.6 |
| Total parameters | 958,588,736 |
| Trainable parameters | 12,091,392 |
| Trainable share | 1.2614% |
| LoRA rank | 32 |
| LoRA alpha | 64 |
| LoRA scaling | 2.0 |
| Decoder projections | 126 |
| Training records | 42,254 |
| Target tokens per pass | 1,171,860 |
| Effective corpus passes | 3.000521 |
| Target-token exposures | ~3.516M |
| Optimizer steps | 1,981 |
| Effective batch size | 64 |
| Maximum sequence length | 4,096 |
| Peak learning rate | 1e-4 |
| Minimum learning rate | 1e-5 |
| Warmup | 3% |
| Weight decay | 0.01 |
| Gradient clipping | 1.0 |
| Training precision | BF16 |
| Final reported train loss | 0.4991 |
| Hardware | 1 x NVIDIA A10G |
| Runtime | 7,266.56 s, ~2 h 01 m |

The vision encoder, vision-language aligner/projector, embeddings, and LM head remained frozen.

LoRA was applied to seven projections in each of 18 decoder layers:

- `q_proj`
- `k_proj`
- `v_proj`
- `o_proj`
- `gate_proj`
- `up_proj`
- `down_proj`

The final adapter was merged into the base weights in FP32. Merge-equivalence validation produced **128/128** exact decoded matches between base-plus-adapter inference and the merged model.

# Data

The training corpus contains **42,254 OCR records** and **1,171,860 supervised target tokens per corpus pass**.

| Corpus lane | Records | Target tokens |
|---|---:|---:|
| [Vietnamese handwriting (Viet-Handwriting-OCR-v2)](https://huggingface.co/datasets/5CD-AI/Viet-Handwriting-OCR-v2) | 23,046 | 456,066 |
| VinText | 10,174 | 32,531 |
| Vietnamese text corpus | 1,539 | 491,846 |
| General OCR replay | 4,687 | 22,594 |
| Private archival corpus | 2,808 | 168,823 |
| **Total** | **42,254** | **1,171,860** |

The corpus is Vietnamese-dominant, with handwriting, scene/document text, longer-form printed Vietnamese, general OCR replay, and restricted archival material. The Vietnamese handwriting lane is sourced from [5CD-AI/Viet-Handwriting-OCR-v2](https://huggingface.co/datasets/5CD-AI/Viet-Handwriting-OCR-v2).

Restricted archival source material is **not redistributed** with SenOCR-Vi. Public datasets retain their original licensing terms.

---

# Limitations

SenOCR-Vi is optimized primarily for Vietnamese text recognition.

Structured elements remain more difficult than ordinary text on the controlled evaluation population:

| Component | Score |
|---|---:|
| Text | **86.5%** under `1 - NED` |
| Table | **70.7 TEDS** |
| Formula | **72.5 CDM** |

The model is therefore not positioned as a table- or formula-specialized OCR system.

Other difficult cases include:

- complex or irregular tables;
- formula-heavy scientific pages;
- dense multi-column layouts;
- highly colorful textbooks and magazines;
- severe image degradation or unusual page geometry.

No controlled production benchmark has yet established pages per second, optimized BF16 peak VRAM, or latency relative to other OCR systems.

For legal, financial, historical, or otherwise high-stakes transcription, human review is recommended.

# License

SenOCR-Vi is released under the **Apache License 2.0**.

The model is built on [PaddleOCR-VL-1.6](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6), which is also distributed under Apache 2.0.

Dataset licenses vary by source. Restricted archival material is not included in the release.

# Citation

```bibtex
@misc{vietalphalab2026senocrvi,
      title={SenOCR-Vi: A Vietnamese-Specialized Document OCR Model},
      author={VietAlpha Lab},
      year={2026},
      publisher={Hugging Face},
      url={https://huggingface.co/VietAlphaLabs/SenOCR-Vi},
}
```

# References

- [PaddleOCR-VL-1.6](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6)
- [PaddleOCR-VL-1.6 documentation](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/algorithm/PaddleOCR-VL/PaddleOCR-VL-1.6.en.md)
- [PaddleOCR-VL pipeline documentation](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PaddleOCR-VL.en.md)
- [MDPBench](https://github.com/Yuliang-Liu/MultimodalOCR/blob/main/MDPBench/README.md)
- [5CD-AI/Viet-Handwriting-OCR-v2](https://huggingface.co/datasets/5CD-AI/Viet-Handwriting-OCR-v2)
- Khang T. Doan, Bao G. Huynh, Dung T. Hoang, Thuc D. Pham, Nhat H. Pham, Quan T. M. Nguyen, Bang Q. Vo, and Suong N. Hoang. [*Vintern-1B: An Efficient Multimodal Large Language Model for Vietnamese*](https://arxiv.org/abs/2408.12480). arXiv:2408.12480, 2024.

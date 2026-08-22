---
license: openmdw-1.1
pipeline_tag: image-text-to-text
tags:
- VLM
- OCR
- Parse
library_name: transformers
---
# Model Overview

### Description:
NVIDIA Nemotron Parse 2.0 transforms document images into structured, machine-readable representations with text, layout classes, bounding boxes, and reading-order information. Given a Red, Green, Blue (RGB) document image and a task prompt, the model produces formatted text and spatial annotations for document elements such as titles, paragraphs, captions, tables, charts, page headers, page footers, footnotes, pictures, and bibliography entries. Compared with NVIDIA Nemotron Parse v1.2, NVIDIA Nemotron Parse 2.0 adds an approximately 20k-token vocabulary expansion for more efficient multilingual support, chart-aware document parsing with the `<class_Chart>` class token, and updated training coverage for chart/table-heavy documents. NVIDIA Nemotron Parse 2.0 is intended for document understanding, information retrieval, data extraction, and multimodal data-curation workflows.<br>

This model is ready for commercial or non-commercial use. <br>

### License/Terms of Use:
This model and its associated configuration files are licensed under the [OpenMDW License Agreement, version 1.1 (OpenMDW-1.1)](https://openmdw.ai/license/1-1/). Use of the tokenizer included in this model is governed by the [CC-BY-4.0 license](https://creativecommons.org/licenses/by/4.0/).<br>

This project will download and install additional third-party open source software projects. Review the license terms of these open source projects before use. Contributions are accepted under the policy in [CONTRIBUTING.md](CONTRIBUTING.md).<br>

### Deployment Geography:
Global<br>

### Use Case: <br>
NVIDIA Nemotron Parse 2.0 is designed for developers and teams building document intelligence, retrieval-augmented generation (RAG), curator, extractor, and agentic AI applications. It can be used to convert scanned or rendered PDFs, presentation slides, forms, reports, tables, and mixed-content document pages into structured outputs for downstream indexing, retrieval, analytics, model training-data creation, and human-in-the-loop review.<br>

### Capability Highlights: <br>
* Expanded multilingual OCR support, with substantial gains on CJK and Indic-script document text.<br>
* Improved handwritten-text extraction for document pages containing informal, handwritten, or note-like content.<br>
* Chart-to-table parsing that can identify chart regions and convert visible chart information into structured text for downstream use.<br>
* Improved table handling, including stronger table detection, structure recovery, and text extraction on table-heavy documents.<br>

### Release Date:  <br>
Hugging Face August 3, 2026 on the [NVIDIA Nemotron Parse 2.0 model page](https://huggingface.co/nvidia/NVIDIA-Nemotron-Parse-2.0) <br>

## References(s):
* [Hugging Face Transformers mBART documentation](https://huggingface.co/docs/transformers/en/model_doc/mbart) <br>
* [NVIDIA C-RADIO](https://huggingface.co/nvidia/C-RADIO) <br>

## Model Architecture:
**Architecture Type:** Transformer-based vision-encoder-decoder model<br>

**Network Architecture:** <br>
* Vision Encoder: ViT-H model based on NVIDIA C-RADIO<br>
* Adapter Layer: 1D convolutions and normalization layers that compress the vision latent sequence before decoding<br>
* Decoder: mBART decoder with 10 blocks<br>
* Auxiliary Prediction Head: One training-time decoder prediction head is preserved separately in `auxiliary_prediction_heads.safetensors.extra` for future multi-token prediction research. Standard generation uses the tied decoder input/output embeddings; the default `model.safetensors`, Transformers examples, and vLLM examples do not load this auxiliary head.<br>
* Tokenizer: The tokenizer contains 72,256 entries, including an approximately 20k-token expansion over NVIDIA Nemotron Parse v1.2 to improve multilingual token efficiency. The model also includes task/control tokens such as `<predict_bbox>`, `<predict_classes>`, `<predict_text_in_pic>`, and `<predict_no_text_in_pic>`, plus the chart class token `<class_Chart>`. Use of the tokenizer included in this model is governed by the [CC-BY-4.0 license](https://creativecommons.org/licenses/by/4.0/).<br>
* Number of Parameters: < 1B<br>

## Input(s): <br>
**Input Type(s):** Image, Text<br>

**Input Format(s):** <br>
* Image: Red, Green, Blue (RGB)<br>
* Text: Prompt string<br>

**Input Parameters:** <br>
* Image: Two-Dimensional (2D)<br>
* Text: One-Dimensional (1D)<br>

**Other Properties Related to Input:** <br>
* Recommended maximum input resolution (Width, Height): 1664, 2048<br>
* Recommended minimum input resolution (Width, Height): 1024, 1280<br>
* Channel Count: 3<br>
* Prompt format: one task prompt composed from the supported control tokens. The default prompt extracts bounding boxes, semantic classes, and text in markdown format: `</s><s><predict_bbox><predict_classes><output_markdown><predict_no_text_in_pic>`. The model can emit chart regions using `<class_Chart>` when chart content is detected.<br>

## Output(s): <br>
**Output Type(s):** Text<br>

**Output Format(s):** String<br>

**Output Parameters:** One-Dimensional (1D)<br>

**Other Properties Related to Output:** Nemotron Parse 2.0 returns a string encoding document text, semantic element classes, and bounding boxes. Postprocessing utilities in this repository can transform generated bounding boxes back to original image coordinates and convert table or chart-associated text into LaTeX, HTML, markdown, JSON, or CSV where supported.<br>

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA hardware and software frameworks, the model achieves faster training and inference times compared to CPU-only solutions. <br>

## Quick Start

### Direct Transformers inference dependencies

This installation is only for the direct Transformers example in the next section. It is not needed for the vLLM container workflow below. You can use the public image `nvcr.io/nvidia/pytorch:25.03-py3` with the following library versions installed on top:

```bash
pip install accelerate==1.12.0
pip install transformers==5.6.1
pip install timm==1.0.22
pip install open_clip_torch==3.2.0
pip install einops==0.8.1
pip install beautifulsoup4
```

`open_clip_torch` is currently needed only by the direct Transformers path because C-RADIO's remote-code validation inspects an optional OpenCLIP adaptor. Nemotron Parse does not configure or execute that adaptor. Albumentations is not used by the Nemotron Parse 2.0 processor.

### Usage example

```python
import torch
from PIL import Image, ImageDraw
from transformers import AutoModel, AutoProcessor, AutoTokenizer, GenerationConfig
from postprocessing import extract_classes_bboxes, transform_bbox_to_original, postprocess_text

# Load model and processor
model_path = "nvidia/NVIDIA-Nemotron-Parse-2.0"  # Or use a local path
device = "cuda:0"

model = AutoModel.from_pretrained(
    model_path,
    trust_remote_code=True,
    torch_dtype=torch.bfloat16
).to(device).eval()
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)

# Load image
image = Image.open("document.png")
task_prompt = "</s><s><predict_bbox><predict_classes><output_markdown><predict_no_text_in_pic>"
# task_prompt = "</s><s><predict_bbox><predict_classes><output_markdown><predict_text_in_pic>"

# Process image
inputs = processor(images=[image], text=task_prompt, return_tensors="pt", add_special_tokens=False).to(device)

generation_config = GenerationConfig.from_pretrained(model_path, trust_remote_code=True)

# Generate text
outputs = model.generate(**inputs, generation_config=generation_config)

# Decode the generated text
generated_text = processor.batch_decode(outputs, skip_special_tokens=True)[0]
```

### Postprocessing

```python
from PIL import ImageDraw
from postprocessing import extract_classes_bboxes, transform_bbox_to_original, postprocess_text

classes, bboxes, texts = extract_classes_bboxes(generated_text)
bboxes = [transform_bbox_to_original(bbox, image.width, image.height) for bbox in bboxes]

# Specify output formats for postprocessing
table_format = "latex"  # latex | HTML | markdown | json | json_hierarchical | csv
text_format = "markdown"  # markdown | plain
blank_text_in_figures = False  # set True to remove text inside 'Picture' class
texts = [
    postprocess_text(
        text,
        cls=cls,
        table_format=table_format,
        text_format=text_format,
        blank_text_in_figures=blank_text_in_figures,
    )
    for text, cls in zip(texts, classes)
]

for cl, bb, txt in zip(classes, bboxes, texts):
    print(cl, ": ", txt)

draw = ImageDraw.Draw(image)
for bbox in bboxes:
    draw.rectangle((bbox[0], bbox[1], bbox[2], bbox[3]), outline="red")
```

#### Table output formats

Supported values for `table_format`: `latex` | `HTML` | `markdown` | `json` | `json_hierarchical` | `csv`

## Inference with vLLM

**Supported vLLM versions:** v0.20-v0.26. The container-only examples below were validated with v0.20.0.

Nemotron Parse 2.0 can be served directly from a standard vLLM container that includes Nemotron Parse support. No additional `albumentations` or `open_clip_torch` installation is required for this vLLM path. The model's lightweight encoder configuration prevents vLLM startup from recursively importing C-RADIO's unused OpenCLIP adaptor. This container-only dependency path was validated with vLLM v0.20. On A100 and A10 systems, we recommend running `vllm serve` with `--attention-backend=TRITON_ATTN`.

This export keeps `lm_head.weight` tied to `decoder.embed_tokens.weight` and does not materialize a duplicate output-head tensor. Current vLLM 0.20 Nemotron Parse builds create a separate output head unless patched. If your vLLM build does not already support tied Nemotron Parse output embeddings, fetch the included runtime patch and add it to `PYTHONPATH` before starting vLLM:

```bash
PATCH_ROOT=$(python - <<'PY'
from huggingface_hub import snapshot_download
print(snapshot_download(
    "nvidia/NVIDIA-Nemotron-Parse-2.0",
    allow_patterns="vllm_tied_patch/sitecustomize.py",
))
PY
)
export PYTHONPATH="${PATCH_ROOT}/vllm_tied_patch:${PYTHONPATH}"
```

### vLLM Inference example

#### Option 1: end-to-end Python inference

```python
from vllm import LLM, SamplingParams
from PIL import Image


def main():
    sampling_params = SamplingParams(
        temperature=0,
        top_k=1,
        repetition_penalty=1.1,
        max_tokens=9000,
        skip_special_tokens=False,
    )

    llm = LLM(
        model="nvidia/NVIDIA-Nemotron-Parse-2.0",
        max_num_seqs=64,
        limit_mm_per_prompt={"image": 1},
        dtype="bfloat16",
        trust_remote_code=True,
    )

    image = Image.open("document.png")

    prompts = [
        {
            "prompt": "</s><s><predict_bbox><predict_classes><output_markdown><predict_no_text_in_pic>",
            "multi_modal_data": {
                "image": image,
            },
        },
        {
            "encoder_prompt": {
                "prompt": "",
                "multi_modal_data": {
                    "image": image,
                },
            },
            "decoder_prompt": "</s><s><predict_bbox><predict_classes><output_markdown><predict_no_text_in_pic>",
        },
    ]

    outputs = llm.generate(prompts, sampling_params)

    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Decoder prompt: {prompt!r}, Generated text: {generated_text!r}")


if __name__ == "__main__":
    main()
```

#### Option 2: vLLM serve

```bash
vllm serve nvidia/NVIDIA-Nemotron-Parse-2.0 \
    --dtype bfloat16 \
    --max-num-seqs 8 \
    --limit-mm-per-prompt '{"image": 1}' \
    --trust-remote-code \
    --port 8000
```

Then run inference through the OpenAI-compatible API:

```python
import base64
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",
)

with open("document.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

prompt_text = "</s><s><predict_bbox><predict_classes><output_markdown><predict_no_text_in_pic>"

resp = client.chat.completions.create(
    model="nvidia/NVIDIA-Nemotron-Parse-2.0",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt_text,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_b64}",
                    },
                },
            ],
        }
    ],
    max_tokens=8192,
    temperature=0.0,
    extra_body={
        "repetition_penalty": 1.1,
        "top_k": 1,
        "skip_special_tokens": False,
    },
)
print(resp.choices[0].message.content)
```

### Prompt and logits-processor options

The recommended default prompt extracts bounding boxes, semantic classes, and text in markdown format:

`</s><s><predict_bbox><predict_classes><output_markdown><predict_no_text_in_pic>`

To extract text that appears inside embedded images or figures, use:

`</s><s><predict_bbox><predict_classes><output_markdown><predict_text_in_pic>`

If only bounding boxes and classes are needed, use:

`</s><s><predict_bbox><predict_classes><output_no_text><predict_no_text_in_pic>`

This repository includes two optional logits processors:
* `NemotronParseRepetitionStopProcessor`: detects repeating n-grams during generation and forces the model to close the coordinate block when repeated structured output suggests a potential hallucination.
* `NemotronParseTableInsertionLogitsProcessor`: forces every block to follow a table structure, which can be useful when running the model on table image crops.

Please refer to `example_with_processor.py` for Python-model usage. With vLLM, add the model repository's `logitsprocs/` directory to `PYTHONPATH` and pass the desired processor to `vllm serve`:

```bash
PROCESSOR_ROOT=$(python - <<'PY'
from huggingface_hub import snapshot_download
print(snapshot_download(
    "nvidia/NVIDIA-Nemotron-Parse-2.0",
    allow_patterns="logitsprocs/nemotron_parse_vllm_logitprocs.py",
))
PY
)
export PYTHONPATH="${PROCESSOR_ROOT}/logitsprocs:${PYTHONPATH}"

vllm serve nvidia/NVIDIA-Nemotron-Parse-2.0 \
  --dtype bfloat16 \
  --max-num-seqs 4 \
  --limit-mm-per-prompt '{"image": 1}' \
  --attention-backend=TRITON_ATTN \
  --trust-remote-code \
  --logits-processors nemotron_parse_vllm_logitprocs:NemotronParseTableInsertionLogitsProcessor \
  --port 8000
```

An example of inference with the vLLM OpenAI-compatible server is available in `vllm_example.py`.

## Software Integration:
**Runtime Engine(s):**
* Transformers <br>
* vLLM <br>

**Supported Hardware Microarchitecture Compatibility:** <br>
* NVIDIA Ampere <br>
* NVIDIA Blackwell <br>
* NVIDIA Hopper <br>
* NVIDIA Turing <br>

**Supported Operating System(s):**
* Linux <br>

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels is essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment. <br>

## Model Version(s):
Nemotron Parse 2.0 <br>

## Training, Testing, and Evaluation Datasets:

### Training Dataset

**Data Modality:** <br>
* Image <br>
* Text <br>

**Image Training Data Size:** <br>
* 1 Million to 1 Billion Images <br>

**Text Training Data Size:** <br>
* 1 Billion to 10 Trillion Tokens <br>

**Data Collection Method by dataset:** <br>
* Hybrid: Automated, Human, Synthetic <br>

**Labeling Method by dataset:** <br>
* Hybrid: Automated, Human, Synthetic <br>

**Properties:** The training set contains millions of image-text items aggregated across large document, table, and layout datasets. The data consists of document-page and table images paired with OCR text, bounding boxes, and layout labels. Sources include rendered digital documents, scientific papers, PDFs, Wikipedia-style pages, and synthetic document, table, word, and character renderings. Annotations come from OCR and layout models, third-party OCR services, synthetic-generation pipelines, and human labeling. <br>

### Testing and Evaluation Dataset

Testing and evaluation use internal and public document-understanding benchmarks that cover OCR quality, layout structure, table parsing, reading order, and visual grounding. Dataset collection and labeling methods are hybrid and include automated, model-derived, manually labeled, and synthetic annotations. <br>

### Evaluation Results

Benchmark coverage: <br>
* ParseBench evaluates document parsing across text fidelity, semantic formatting, tables, charts, and visual grounding with layout boxes/classes. <br>
* IndicVisionBench evaluates OCR quality for Indic-language pages, including Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, and Telugu. <br>
* MOSCAR evaluates multilingual synthetic OCR across broad script coverage, including Latin, Arabic, Cyrillic, Chinese, Hangul, Japanese, Indic scripts, Hebrew, Thai, Greek, and others. <br>
* OmniDocBench Notes (Handwriting) evaluates text-block edit distance on note-style document pages from the `data_source: note` slice. <br>

The following results compare NVIDIA Nemotron Parse 2.0 with NVIDIA Nemotron Parse v1.2 on internal and public evaluation benchmarks. NVIDIA Nemotron Parse 2.0 results use the equal-weight checkpoint soup from training checkpoints 58k, 60k, 62k, 64k, and 66k. Unless marked otherwise, metrics are higher-is-better; arrows indicate the direction of the 2.0 change relative to v1.2. <br>

| Benchmark | Metric | NVIDIA Nemotron Parse v1.2 | NVIDIA Nemotron Parse 2.0 | Change |
| :---- | :---- | :---- | :---- | :---- |
| ParseBench | Overall score | 0.5782 | 0.6391 | ↑ +0.0609 |
| OmniDocBench Notes (Handwriting) | Text edit distance (lower is better) | 0.9739 | 0.3395 | ↓ -0.6343 |
| IndicVisionBench | Overall ANLS character | 0.0612 | 0.7203 | ↑ +0.6592 |
| MOSCAR (Multilingual) | Overall BoC F1 | 0.4410 | 0.9102 | ↑ +0.4692 |

## Inference:
**Acceleration Engine:** Transformers, vLLM <br>
**Test Hardware:** <br>
* H100 <br>
* A100 <br>

## Ethical Considerations:
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications. Developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse. <br>

Please make sure you have proper rights and permissions for all input image and video content. If an input image contains people, personal health information, confidential business data, or intellectual property, the model may extract or reproduce visible text from that content. <br>

For more detailed information on ethical considerations for this model, please see the Model Card++ subcards: [Bias](https://huggingface.co/nvidia/NVIDIA-Nemotron-Parse-2.0/blob/main/bias.md), [Explainability](https://huggingface.co/nvidia/NVIDIA-Nemotron-Parse-2.0/blob/main/explainability.md), [Safety & Security](https://huggingface.co/nvidia/NVIDIA-Nemotron-Parse-2.0/blob/main/safety.md), and [Privacy](https://huggingface.co/nvidia/NVIDIA-Nemotron-Parse-2.0/blob/main/privacy.md). <br>
Please report model quality, risk, security vulnerabilities, or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/). <br>

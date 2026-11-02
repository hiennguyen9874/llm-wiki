---
license: openmdw-1.1
pipeline_tag: image-text-to-text
tags:
- VLM
- OCR
- Parse
library_name: transformers
---
# Nemotron 3.5 Parse

### Description:
Nemotron 3.5 Parse is a document image parser that produces structured, machine-readable text with semantic layout classes, bounding boxes, and reading order. It combines a C-RADIOv4-SO400M vision encoder with a 10-layer mBART decoder that consumes the visual sequence as a causal prefix. The release uses dynamic rectangular NaViT preprocessing, content-normalized coordinates, grouped-query self-attention (16 query heads and 8 key/value heads), a 72,505-token multilingual tokenizer, and chart-aware output through the `<class_Chart>` token. It is intended for document understanding, information retrieval, data extraction, and multimodal data-curation workflows.<br>

Nemotron 3.5 Parse was developed by NVIDIA as a part of Nemotron.

This model is ready for commercial or non-commercial use. <br>

## Hosted inference

- [Try the API on NVIDIA Build](https://build.nvidia.com/nvidia/nemotron-3.5-parse)
- [Deploy on Baseten](https://www.baseten.co/library/nemotron-35-parse/)

## Benchmark highlights

Detailed benchmarks: [ParseBench](#parsebench) · [IndicVisionBench](#indicvisionbench-ocr) · [MOSCAR](#moscar-multilingual-ocr).

| Model | Mean ↑ | Tables ↑ | Charts ↑ | Content Faithfulness ↑ | Semantic Formatting ↑ | Visual Grounding ↑ |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Nemotron 3.5 Parse** | **75.20** | **84.67** | **64.40** | **87.96** | **68.28** | **70.67** |

ParseBench results use triple pass with region union on 2,078 unique pages. See [pipeline details](#parsebench), [reproduction instructions](reference/parsebench/pipeline/README.md), and [evaluation results](reference/parsebench/pipeline/validation_metrics.json).

Additional OCR highlights (scores on a 0–100 scale):

* **IndicVisionBench OCR: 83.73 ANLS-char**, evaluated on 876 test pages across 10 languages. [Per-language results](#indicvisionbench-ocr).
* **MOSCAR: 99.51 character bag F1**, evaluated on 8,111 simply rendered synthetic pages covering 163 language/script entries. [Per-script results](#moscar-multilingual-ocr) and [full per-language results](reference/multilingual/moscar_by_language.md).

MOSCAR uses simple synthetic renderings of text in each language to test basic OCR capability. These results do not guarantee accuracy on complex scanned documents, handwriting, degraded images, or other real-world variations. Character bag F1 measures character overlap without considering character order.

### License/Terms of Use:
Governing Terms: Your use of this model is governed by the [OpenMDW License Agreement, version 1.1](https://openmdw.ai/license/1-1/). Use of the tokenizer included in this model is governed by the [MIT license and tokenizer attribution](https://huggingface.co/nvidia/Nemotron-3.5-Parse/blob/main/TOKENIZER_ATTRIBUTION.md). See [third-party notices](https://huggingface.co/nvidia/Nemotron-3.5-Parse/blob/main/THIRD_PARTY_NOTICES.md) for separately installed dependencies.<br>

Tokenizer source and modifications are documented in [TOKENIZER_ATTRIBUTION.md](TOKENIZER_ATTRIBUTION.md).

The portable ParseBench pipeline has its own [license](reference/parsebench/pipeline/LICENSE)
and [third-party notices](reference/parsebench/pipeline/THIRD_PARTY_NOTICES.md),
including the separately installed benchmark environment. See the
[component inventory](reference/package/benchmark_environment_components.json)
and [package build evidence](reference/package/README.md) for exact versions and digests.

### Deployment Geography:
Global<br>

### Use Case: <br>
Nemotron 3.5 Parse is designed for developers and teams building document intelligence, retrieval-augmented generation (RAG), curator, extractor, and agentic AI applications. It can convert scanned or rendered PDFs, presentation slides, forms, reports, tables, and mixed-content document pages into structured outputs for downstream indexing, retrieval, analytics, model training-data creation, and human-in-the-loop review.<br>

### Release Date:  <br>
Hugging Face 10/17/2026 via https://huggingface.co/nvidia/Nemotron-3.5-Parse <br>

## References:
* [Hugging Face Transformers mBART documentation](https://huggingface.co/docs/transformers/en/model_doc/mbart) <br>
* [NVIDIA C-RADIOv4-SO400M](https://huggingface.co/nvidia/C-RADIOv4-SO400M) <br>

## Model Architecture:
**Architecture Type:** Transformer<br>

**Network Architecture:** <br>
* Vision Encoder: NVIDIA C-RADIOv4-SO400M (`vit_so400m_patch16_224`) with dynamic rectangular NaViT preprocessing<br>
* Adapter Layer: 1D convolutions and normalization layers that compress the vision latent sequence before decoding<br>
* Decoder: 10-layer mBART causal visual-prefix decoder with 16 query heads and 8 key/value heads<br>
* Auxiliary Prediction Head: One trained one-step multi-token-prediction (MTP) head is included in `model.safetensors`. Transformers uses the normal decoder for generation; the vLLM plugin enables the bundled head for one-token speculative decoding.<br>
* Tokenizer: 72,505 entries with multilingual and task/control tokens including `<predict_bbox>`, `<predict_classes>`, `<predict_text_in_pic>`, and `<class_Chart>`; the decoder embedding is padded to 72,512 rows. Use of the tokenizer included in this model is governed by the [MIT license and tokenizer attribution](https://huggingface.co/nvidia/Nemotron-3.5-Parse/blob/main/TOKENIZER_ATTRIBUTION.md).<br>
* Number of Parameters: 630,800,496 unique trainable parameters (approximately 0.631B), including the MTP head; shared decoder embedding/output weights are counted once<br>

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
* Channel Count: 3<br>
* Prompt format: one task prompt composed from the supported control tokens. The default prompt extracts bounding boxes, semantic classes, and text in markdown format: `</s><s><predict_bbox><predict_classes><output_markdown><predict_text_in_pic>`.<br>

## Output(s): <br>
**Output Type(s):** Text<br>

**Output Format(s):** String<br>

**Output Parameters:** One-Dimensional (1D)<br>

**Other Properties Related to Output:** Nemotron 3.5 Parse returns a string encoding document text, semantic element classes, and content-normalized bounding boxes. Scale x coordinates by the evaluated image width and y coordinates by its height. Postprocessing utilities can convert table or chart-associated text into LaTeX, HTML, markdown, JSON, or CSV where supported.<br>

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA hardware and software frameworks, the model achieves faster training and inference times compared to CPU-only solutions. <br>

## Quick Start

### Transformers installation

Use Python 3.12 and a fresh environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install "transformers==5.14.1" "torchvision==0.26.0" "timm==1.0.22"
```

Run `hf auth login` if repository access requires authentication. Transformers downloads the model weights, processor, and custom model code automatically. No Nemotron package installation is needed for Transformers inference.

### Usage example

```python
import torch
from PIL import Image
from transformers import AutoModel, AutoProcessor, GenerationConfig

model_path = "nvidia/Nemotron-3.5-Parse"
device = "cuda:0"

model = AutoModel.from_pretrained(
    model_path,
    trust_remote_code=True,
    dtype=torch.bfloat16
).to(device).eval()
processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)

image = Image.open("path/to/your/image.jpg").convert("RGB")
task_prompt = "</s><s><predict_bbox><predict_classes><output_markdown><predict_text_in_pic>"

inputs = processor(images=[image], text=task_prompt, return_tensors="pt", add_special_tokens=False).to(device)

generation_config = GenerationConfig.from_pretrained(model_path)
generation_config.max_new_tokens = 8744

with torch.inference_mode():
    outputs = model.generate(**inputs, generation_config=generation_config)

generated_text = processor.batch_decode(outputs, skip_special_tokens=False)[0]
print(generated_text)
```

### Postprocessing

The shared helpers render a complete document as Markdown with HTML tables, and
return structured blocks with normalized boxes and optional pixel boxes. They
preserve model reading order, table spans, blank cells, and in-cell line breaks.
They also decode rich table formatting, remove literal duplicate elements, repair
empty serialization prefixes, and normalize existing list bullets and discretionary
soft hyphens in text. Code and math are protected from typography cleanup.

Download the helpers and their shared implementation into your working directory
(no Nemotron package installation is needed for this path):

```bash
python -m pip install "beautifulsoup4==4.13.3"
hf download nvidia/Nemotron-3.5-Parse \
  --include 'postprocessing.py' 'latex2html.py' 'nemotron_parse/**' --local-dir .
```

Continue from the Transformers example above:

```python
from pathlib import Path
from PIL import ImageDraw
from postprocessing import postprocess_document

document = postprocess_document(generated_text, image_size=image.size)
Path("prediction.md").write_text(document["markdown"], encoding="utf-8")
draw = ImageDraw.Draw(image)
for block in document["blocks"]:
    draw.rectangle(block["bbox_pixels"], outline="red", width=2)
image.save("prediction.png")
```

The existing `extract_classes_bboxes`, `transform_bbox_to_original`, and
`postprocess_text` functions remain available. Supported `table_format` values:
`latex` | `HTML` | `markdown` | `json` | `json_hierarchical` | `csv`.
HTML and hierarchical JSON retain merged-cell structure; flat Markdown, CSV, and
record JSON flatten spans. Headerless tables use neutral column names in flat
exports, retaining every data row.

Explicit chart titles, subtitles, and panel labels are preserved with their tables.
Header inference uses predicted spans and existing bold markup; it can be disabled.
Numeric value/percentage column splitting and geometric chart-caption association
are enabled by default. Both preserve existing predicted values/text and can be disabled. See
[postprocessing examples](docs/postprocessing.md) for controls and examples.

## Inference with vLLM

vLLM requires the Nemotron plugin for this architecture and its MTP head. The plugin accepts stable vLLM releases `>=0.25.0,<0.33` (0.25.x through 0.32.x). In a fresh Python 3.12 environment, download the repository and install the serving extras:

```bash
python -m pip install "huggingface-hub>=1.24.0,<2"
hf download nvidia/Nemotron-3.5-Parse --local-dir nemotron-parse
cd nemotron-parse
python -m pip install ".[vllm,client]" "vllm>=0.25.0,<0.33"
```

To select a specific vLLM release within this range, replace the final argument with your desired version (for example, `"vllm==0.32.0"`). Let pip resolve the compatible Torch, torchvision, and Transformers dependencies declared by the package.

One-token MTP and the compatible FA3 scheduler are enabled automatically.

### vLLM Inference example

#### Option 1: Python inference with MTP

```python
from PIL import Image
from vllm import LLM, SamplingParams

def main():
    llm = LLM(
        model=".",
        dtype="bfloat16",
        trust_remote_code=True,
        distributed_executor_backend="uni",
        max_model_len=16384,
        max_num_seqs=64,
        max_num_batched_tokens=16384,
        limit_mm_per_prompt={"image": 1},
        enable_prefix_caching=False,
        attention_config={"flash_attn_version": 3},
    )
    sampling_params = SamplingParams(
        temperature=0,
        top_k=1,
        repetition_penalty=1.1,
        max_tokens=8744,
        skip_special_tokens=False,
    )
    image = Image.open("<YOUR-IMAGE-PATH>").convert("RGB")
    outputs = llm.generate([{
        "prompt": "<pad>\n</s><s><predict_bbox><predict_classes><output_markdown><predict_text_in_pic>",
        "multi_modal_data": {"image": image},
    }], sampling_params, tokenization_kwargs={"add_special_tokens": False})
    print(outputs[0].outputs[0].text)

if __name__ == "__main__":
    main()
```

The offline prompt includes the image placeholder `<pad>`. Automatic special
tokens are disabled because the task prompt already contains its control tokens.

#### Option 2: vLLM serve with MTP

```bash
vllm serve . \
    --served-model-name nemotron-parse \
    --dtype bfloat16 \
    --distributed-executor-backend uni \
    --tensor-parallel-size 1 \
    --max-model-len 16384 \
    --max-num-seqs 192 \
    --max-num-batched-tokens 16384 \
    --no-enable-prefix-caching \
    --limit-mm-per-prompt '{"image":1}' \
    --attention-config '{"flash_attn_version":3}' \
    --trust-remote-code \
    --port 8000 \
    --chat-template chat_template.jinja
```

Then run inference through the OpenAI-compatible API:

```python
import base64
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",
)

with open("<YOUR-IMAGE-PATH>", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

prompt_text = "</s><s><predict_bbox><predict_classes><output_markdown><predict_text_in_pic>"

resp = client.chat.completions.create(
    model="nemotron-parse",
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
    max_tokens=8744,
    temperature=0.0,
    extra_body={
        "repetition_penalty": 1.1,
        "top_k": 1,
        "skip_special_tokens": False,
    },
)
print(resp.choices[0].message.content)
```

For Docker deployment and optional generation controls, see [the serving guide](docs/serving.md).

## Software Integration:
**Runtime Engine(s):**
* Transformers <br>
* vLLM <br>

**Reference Hardware:** NVIDIA Hopper H100, BF16. The FA3/MTP speed profile above is measured on H100.<br>

**Supported Operating System(s):**
* Linux <br>

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels is essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment. <br>

## Model Version(s):
Nemotron 3.5 Parse · October 17, 2026 release <br>

This AI model can be embedded as an Application Programming Interface (API) call through the documented Transformers or vLLM serving interfaces.

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
* Automated, Manually-Collected, Synthetic <br>

**Labeling Method by dataset:** Automated, Manually-Labeled, Synthetic <br>
**Labeling Details:** Labels are produced through a combination of automated OCR and layout annotation, manual annotation, and synthetic generation. The combination varies by constituent dataset. <br>

**Properties:** The training set contains millions of image-text items aggregated across large document, table, and layout datasets. The data consists of document-page and table images paired with OCR text, bounding boxes, and layout labels. Sources include rendered digital documents, scientific papers, PDFs, Wikipedia-style pages, and synthetic document, table, word, and character renderings. Annotations come from OCR and layout models, third-party OCR services, synthetic-generation pipelines, and human labeling. <br>

### Testing Dataset

**Data Collection Method by dataset:** Automated, Manually-Collected, Synthetic  
**Collection Details:** Sources combine automated collection, manually collected material, and synthetic generation; methods vary by constituent dataset.

**Labeling Method by dataset:** Automated, Manually-Labeled, Synthetic  
**Labeling Details:** Labels are produced through a combination of automated OCR and layout annotation, manual annotation, and synthetic generation. The combination varies by constituent dataset.

**Properties:** Tested on internal and public document-understanding benchmarks using document-page images and reference text, layout classes, bounding boxes, and structure annotations. Coverage includes OCR quality, layout structure, table parsing, reading order, and visual grounding across document types and languages.

### Evaluation Dataset

**Data Collection Method by dataset:** Automated, Manually-Collected, Synthetic  
**Collection Details:** Sources combine automated collection, manually collected material, and synthetic generation; methods vary by constituent dataset.

**Labeling Method by dataset:** Automated, Manually-Labeled, Synthetic  
**Labeling Details:** Labels are produced through a combination of automated OCR and layout annotation, manual annotation, and synthetic generation. The combination varies by constituent dataset.

**Properties:** Evaluated on internal and public document-understanding benchmarks covering OCR quality, layout structure, table parsing, reading order, and visual grounding. The ParseBench reference evaluation covers 2,078 unique document pages. Additional benchmarks cover Indic-language OCR and multilingual synthetic OCR across the scripts listed below. <br>

Benchmark coverage: <br>
* ParseBench evaluates document parsing across text fidelity, semantic formatting, tables, charts, and visual grounding with layout boxes/classes. <br>
* IndicVisionBench evaluates OCR quality for Indic-language pages, including Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, and Telugu. <br>
* MOSCAR evaluates multilingual synthetic OCR across broad script coverage, including Latin, Arabic, Cyrillic, Han, Hangul, Japanese, Indic scripts, Hebrew, Thai, Greek, and others. <br>

### Evaluation Results

#### ParseBench

- **Single pass:** parse the full page once.
- **Double pass:** parse the page, then refine Table/Chart crops selected from its predictions.
- **Triple pass:** add a separate detection request and refine the union of detector and parser regions. Full-page parsing and detection can overlap.

On ParseBench, double pass gains **2.18 overall points** over single pass. Triple
pass adds **0.28 points** over double pass at about **9% lower throughput**. Double
pass captures most of the measured accuracy gain; the table shows the speed tradeoff.

Published overall scores with locally measured throughput:

| Model | Published ParseBench ↑ | Measured pages/s ↑ |
| :--- | ---: | ---: |
| **Nemotron 3.5 Parse (triple-pass)** | **75.20** | **10.62** |
| LightOnOCR-3-4B | 75.10 | 2.76 |
| **Nemotron 3.5 Parse (double-pass)** | **74.92** | **11.65** |
| LightOnOCR-3-0.8B | 74.60 | 5.69 |
| Infinity-Parser2-Flash | 73.25 | 3.06 |
| MinerU2.5-Pro-2605-1.2B | 72.78 | 4.13 |
| **Nemotron 3.5 Parse (single-pass)** | **72.74** | **15.42** |
| KDL-Frontier-Parser-nano | 72.38 | 2.98 |
| LightOnOCR-3-1B | 71.40 | 2.44 |
| Chandra-ocr-2 | 70.10 | 2.01 |
| PaddleOCR-VL-1.6 | 67.43 | 3.11 |
| PaddleOCR-VL-1.5 | 65.95 | 3.40 |
| Nemotron Parse 2.0 | 63.91 | 3.95 |

Speeds use the same 2,078 prepared page images on one H100 per model. Timing includes all model passes and dependent crop work, excluding initial page preparation, startup, warmup, final document rendering and writes.

The refinement merge retains differing full-page/crop alternatives; the reported scores include these alternatives.

See [score sources and timing details](reference/parsebench/comparisons/README.md), [full results](reference/parsebench/comparisons/results.json), and the [pipeline reproduction instructions](reference/parsebench/pipeline/README.md).

#### IndicVisionBench OCR

OCR results on 876 test pages across 10 languages. ANLS-char and character error rate (CER) are shown as percentages. CER includes insertion errors and can exceed 100%.

| Language | Pages | Parse 2.0 ANLS-char ↑ | Parse 3.5 ANLS-char ↑ | Parse 2.0 CER ↓ | Parse 3.5 CER ↓ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Overall | 876 | 72.12 | 83.73 | 52.67 | 16.00 |
| Bengali | 89 | 55.47 | 90.25 | 68.92 | 7.69 |
| Gujarati | 90 | 40.70 | 66.96 | 127.53 | 34.08 |
| Hindi | 85 | 85.03 | 88.34 | 16.32 | 9.36 |
| Kannada | 89 | 87.54 | 91.37 | 19.25 | 7.33 |
| Malayalam | 88 | 48.89 | 63.15 | 75.55 | 42.47 |
| Marathi | 83 | 92.95 | 93.19 | 6.50 | 6.01 |
| Odia | 86 | 67.77 | 73.61 | 71.46 | 24.61 |
| Punjabi | 89 | 83.25 | 91.95 | 66.57 | 7.30 |
| Tamil | 88 | 81.77 | 91.24 | 42.05 | 7.41 |
| Telugu | 89 | 79.86 | 87.75 | 43.57 | 10.53 |

#### MOSCAR multilingual OCR

MOSCAR uses simple synthetic renderings of text in each language to test basic OCR capability. These results do not guarantee accuracy on complex scanned documents, handwriting, degraded images, or other real-world variations. Character bag F1 measures character overlap without considering character order.

OCR results on 8,111 held-out synthetic pages covering all 163 configured language/script entries across 26 script groups. Character bag F1 (BoC F1, higher is better) and CER (lower is better) are percentages. Overall CER is computed across all reference characters, so it is not an unweighted average of the script rows.

| Script | Pages | Parse 2.0 BoC F1 ↑ | Parse 3.5 BoC F1 ↑ | Parse 2.0 CER ↓ | Parse 3.5 CER ↓ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Overall | 8111 | 97.44 | 99.51 | 11.55 | 1.35 |
| Arabic | 824 | 91.27 | 98.87 | 20.17 | 5.80 |
| Armenian | 50 | 99.38 | 99.92 | 1.15 | 0.09 |
| Bengali | 100 | 98.82 | 99.80 | 1.78 | 0.34 |
| Cyrillic | 597 | 98.75 | 99.69 | 2.36 | 0.89 |
| Devanagari | 350 | 97.99 | 99.47 | 5.41 | 0.79 |
| Ethiopic | 100 | 98.31 | 99.89 | 5.52 | 0.14 |
| Georgian | 50 | 99.91 | 99.99 | 0.13 | 0.02 |
| Greek | 50 | 99.63 | 99.93 | 1.07 | 0.10 |
| Gujarati | 50 | 99.52 | 99.92 | 0.74 | 0.15 |
| Gurmukhi | 50 | 94.85 | 99.91 | 14.87 | 0.16 |
| Han (Simplified) | 50 | 98.33 | 99.50 | 1.99 | 1.05 |
| Han (Traditional) | 100 | 97.83 | 99.68 | 3.10 | 0.54 |
| Hangul | 50 | 98.82 | 99.62 | 0.99 | 0.43 |
| Hebrew | 100 | 97.62 | 99.79 | 5.79 | 4.16 |
| Japanese | 50 | 98.66 | 99.77 | 2.61 | 0.47 |
| Kannada | 50 | 95.73 | 99.84 | 5.60 | 0.24 |
| Khmer | 50 | 96.56 | 99.63 | 5.79 | 0.71 |
| Lao | 50 | 98.74 | 99.74 | 2.26 | 0.46 |
| Latin | 5040 | 98.20 | 99.53 | 12.82 | 0.79 |
| Malayalam | 50 | 97.65 | 99.27 | 6.46 | 1.10 |
| Myanmar | 50 | 87.83 | 99.56 | 45.41 | 1.47 |
| Odia | 50 | 97.79 | 99.74 | 7.58 | 0.41 |
| Sinhala | 50 | 96.52 | 99.91 | 15.28 | 2.48 |
| Tamil | 50 | 97.89 | 99.92 | 7.92 | 0.14 |
| Telugu | 50 | 96.69 | 99.69 | 9.33 | 0.47 |
| Thai | 50 | 99.66 | 99.95 | 0.47 | 0.06 |

Both comparisons use the [released Parse 2.0 weights](https://huggingface.co/nvidia/NVIDIA-Nemotron-Parse-2.0) and current Parse 3.5 weights, identical page sets, greedy decoding, and the same scorer for each benchmark. Each model uses its documented default task prompt. All outputs, including those reaching the token limit, are included. See the [full MOSCAR results for all 163 language/script entries](reference/multilingual/moscar_by_language.md), [downloadable results](reference/multilingual/README.md), and [evaluation settings](reference/multilingual/README.md#evaluation-settings).

Inference reference outputs and verification instructions are available in [reference/](https://huggingface.co/nvidia/Nemotron-3.5-Parse/blob/main/reference/README.md).

The [quick20/full500 regression references](reference/parse_3_5/README.md) were refreshed for the released checkpoint on October 18, 2026. Full500 completed 500/500 pages without request failures and scored **74.49% overall** and **83.38% table quality** with the released table parser. These are lightweight regression metrics, separate from official ParseBench or OmniDocBench TEDS. Raw outputs, legacy scores and the updated scorer are included.

## Inference:
**Acceleration Engine:** Transformers, vLLM <br>
**Test Hardware:** <br>
* NVIDIA Hopper H100 <br>

## Ethical Considerations:
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications. Developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse. <br>

Please make sure you have proper rights and permissions for all input image and video content. If an input image contains people, personal health information, confidential business data, or intellectual property, the model may extract or reproduce visible text from that content. <br>

For more detailed information on ethical considerations for this model, please see the Model Card++ [Bias](bias.md), [Explainability](explainability.md), [Safety & Security](safety.md), and [Privacy](privacy.md) subcards. <br>
Please report model quality, risk, security vulnerabilities, or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/). <br>

## Parsing helpers

The Python helpers return Markdown, structured blocks, and raw model output.
After installing the package and starting the vLLM server above:

```python
from nemotron_parse.inference import DocumentParser

with DocumentParser() as parser:
    document = parser.parse("page.png")
print(document["markdown"])
```

See the [postprocessing guide](docs/postprocessing.md) for pipeline options,
prepared batches, high concurrency, CLI examples, and output controls.

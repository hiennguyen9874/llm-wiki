---
library_name: transformers
language:
  - en
  - th
base_model:
  - Qwen/Qwen3-VL-2B-Instruct
tags:
  - OCR
  - vision-language
  - document-understanding
  - multilingual
license: apache-2.0
---

# Typhoon-OCR-1.5-2B
A Smaller, More Robust, and Faster Vision-Language OCR for Thai Real-World Documents
We’re thrilled to announce Typhoon OCR v1.5, the next evolution of our open-source vision-language document parsing model for English and Thai.
Built on top of Qwen3-VL 2B, this release delivers faster inference, improved understanding of handwritten and form-based documents, and enhanced handling of both text-rich and image-rich pages—all in a smaller, more efficient package.

By using this model, you agree to the OpenTyphoon Terms and Conditions and acknowledge the Privacy Notice: https://opentyphoon.ai/tac · https://opentyphoon.ai/privacy

**Try our demo available on [Demo](https://ocr.opentyphoon.ai/)**

**Code / Examples available on [Github](https://github.com/scb-10x/typhoon-ocr)**

**Release Blog available on [OpenTyphoon Blog](https://opentyphoon.ai/blog/en/typhoon-ocr-release)**

**Technical Report available on [Arxiv](https://arxiv.org/abs/2601.14722)**

*Remark: This model is intended to be used with a specific prompt only; it will not work with any other prompts.

*Remark: If you want to run the model locally, we recommend using the Ollama build at https://ollama.com/scb10x. We’ve found that the GGUF files for llama.cpp or LM Studio may suffer from accuracy issues.


#### Key Enhancements:

* **Compact and Efficient Architecture**: The new version is based on Qwen3-VL 2B, making it significantly smaller while retaining strong multimodal capabilities.
 Combined with quantization optimizations, Typhoon OCR v1.5 runs efficiently even on lightweight hardware.
* **Faster Inference Without PDF Metadata**: Unlike Typhoon OCR v1, which relied on embedded PDF metadata for layout reconstruction, v1.5 achieves high layout fidelity directly from image only, eliminating the dependency on metadata.
The result: much faster inference across both PDFs and images, without compromising structural accuracy.
* **Simplified Single-Prompt Inference**: Typhoon OCR v1.5 introduces a single-prompt architecture, replacing the two-prompt process used in v1.
This change simplifies integration, reduces complexity in prompt design, and provides more consistent outputs across diverse document types—making it easier for developers to deploy and fine-tune.
* **Enhanced Handwriting and Form Understanding**: We’ve significantly improved the model’s ability to handle handwritten content, complex forms, and irregular layouts.From government forms and receipts to annotated notes, Typhoon OCR v1.5 now parses and interprets document elements with greater consistency and semantic accuracy.
* **Balanced Performance on Text-Rich and Image-Rich Documents**: Whether processing dense textual reports or visually complex materials such as infographics and illustrated documents, Typhoon OCR v1.5 intelligently adapts its parsing pipeline. This ensures high-quality outputs across diverse formats—from financial tables and academic papers to diagrams, forms, and handwritten notes.


#### Output Format: 
Typhoon OCR v1.5 continues to produce structured, machine-friendly outputs optimized for downstream AI and document intelligence tasks.

* **Markdown** – for general text  
* **HTML** – for tables (including merged cells and complex layouts)  
* **Figure** **`<figure>`** – for figures, charts, and diagrams  
    *Example:*  
    ```
    <figure>
        A bar chart comparing domestic and export revenue growth 
        between Q1 and Q2 2025.
    </figure>
    ```
* **LaTeX** – for mathematical equations  
    *Example:*
    $$ \text{Profit Margin} = \frac{\text{Net Profit}}{\text{Total Revenue}} \times 100 $$
* **Page number** **`<page_number>`** – for preserving page number  
    *Example:* 
    ```
    <page_number>1</page_number>
    ```

This standardized output format allows seamless integration into RAG systems, LLM pipelines, and structured databases.

## Model Performance
### **BLEU Score (↑ Higher is better)**

![BLEU Score](https://storage.googleapis.com/typhoon-public/assets/typhoon_ocr/compare_v1_5_bleu.png)

---

### **ROUGE-L Score (↑ Higher is better)**

![ROUGE-L Score](https://storage.googleapis.com/typhoon-public/assets/typhoon_ocr/compare_v1_5_rouge.png)

---

### **Levenshtein Distance (↓ Lower is better)**

![Levenshtein Distance](https://storage.googleapis.com/typhoon-public/assets/typhoon_ocr/compare_v1_5_leven.png)

## Prompting
```python
prompt = """Extract all text from the image.

Instructions:
- Only return the clean Markdown.
- Do not include any explanation or extra text.
- You must include all information on the page.

Formatting Rules:
- Tables: Render tables using <table>...</table> in clean HTML format.
- Equations: Render equations using LaTeX syntax with inline ($...$) and block ($$...$$).
- Images/Charts/Diagrams: Wrap any clearly defined visual areas (e.g. charts, diagrams, pictures) in:

<figure>
Describe the image's main elements (people, objects, text), note any contextual clues (place, event, culture), mention visible text and its meaning, provide deeper analysis when relevant (especially for financial charts, graphs, or documents), comment on style or architecture if relevant, then give a concise overall summary. Describe in Thai.
</figure>

- Page Numbers: Wrap page numbers in <page_number>...</page_number> (e.g., <page_number>14</page_number>).
- Checkboxes: Use ☐ for unchecked and ☑ for checked boxes."""
```


## Quickstart
**Full inference code available on [Colab](https://colab.research.google.com/drive/1q3K_EExrdr29YTB3qYuDeIYFVyvtsZ6-?usp=sharing)**
**Using Typhoon-OCR Package**
```bash
pip install typhoon-ocr -U
```

```python
from typhoon_ocr import ocr_document

# please set env TYPHOON_OCR_API_KEY or OPENAI_API_KEY to use this function
markdown = ocr_document("test.png", model = "typhoon-ocr", figure_language = "Thai", task_type = "v1.5")
print(markdown)
```

**Local Model via vllm (GPU Required)**:

```bash
pip install vllm
vllm serve scb10x/typhoon-ocr1.5-2b --max-model-len 49152 --served-model-name typhoon-ocr-1-5 # OpenAI Compatible at http://localhost:8000 (or other port)
# then you can supply base_url in to ocr_document
```

```python
from typhoon_ocr import ocr_document
markdown = ocr_document('image.png', model = "typhoon-ocr" , figure_language = "Thai" , task_type="v1.5", base_url='http://localhost:8000/v1', api_key='no-key')
print(markdown)
```
To read more about [vllm](https://docs.vllm.ai/en/latest/getting_started/quickstart.html)

**Local Model - Transformers (GPU Required)**:

```python
from transformers import AutoModelForImageTextToText, AutoProcessor
from PIL import Image

def resize_if_needed(img, max_size):
    width, height = img.size
    # Only resize if one dimension exceeds max_size
    if width > 300 or height > 300:
        if width >= height:
            scale = max_size / float(width)
            new_size = (max_size, int(height * scale))
        else:
            scale = max_size / float(height)
            new_size = (int(width * scale), max_size)

        img = img.resize(new_size, Image.Resampling.LANCZOS)
        print(f"{width, height}==> {img.size}")
        return img
    else:
        return img 


model = AutoModelForImageTextToText.from_pretrained(
    "scb10x/typhoon-ocr1.5-2b", dtype="auto", device_map="auto"
)
processor = AutoProcessor.from_pretrained("scb10x/typhoon-ocr1.5-2b")

img = Image.open("image.png")


#This is important because the model is trained with a fixed image dimension of 1800 px
img = resize_if_needed(img, 1800)

messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": img,
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ],
        }
    ]

# Preparation for inference
inputs = processor.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_dict=True,
    return_tensors="pt"
)
inputs = inputs.to(model.device)

# Inference: Generation of the output
generated_ids = model.generate(**inputs, max_new_tokens=10000)
generated_ids_trimmed = [
    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text = processor.batch_decode(
    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
)
print(output_text[0])
```


## Hosting

We recommend to inference typhoon-ocr using [vllm](https://github.com/vllm-project/vllm) instead of huggingface transformers, and using typhoon-ocr library to ocr documents. To read more about [vllm](https://docs.vllm.ai/en/latest/getting_started/quickstart.html)
```bash
pip install vllm
vllm serve scb10x/typhoon-ocr1.5-2b --max-model-len 49152 --served-model-name typhoon-ocr-1-5  # OpenAI Compatible at http://localhost:8000
# then you can supply base_url in to ocr_document
```

```python
from typhoon_ocr import ocr_document
markdown = ocr_document('image.png', model = "typhoon-ocr" , figure_language = "Thai", task_type="v1.5", base_url='http://localhost:8000/v1', api_key='no-key')
print(markdown)
```

## Ollama & On-device inference

We recommend running Typhoon-OCR on-device using [Ollama](https://ollama.com/scb10x/typhoon-ocr1.5-3b).

## **Intended Uses & Limitations**

This is a task-specific model intended to be used only with the provided prompts. It does not include any guardrails or VQA capability. Due to the nature of large language models (LLMs), a certain level of hallucination may occur. We recommend that developers carefully assess these risks in the context of their specific use case.

## **Follow us**

**https://twitter.com/opentyphoon**

## **Support**

**https://discord.gg/us5gAYmrxw**


## **Citation**

- If you find Typhoon OCR useful for your work, please cite it using:
```
@misc{nonesung2026typhoonocropenvisionlanguage,
      title={Typhoon OCR: Open Vision-Language Model For Thai Document Extraction}, 
      author={Surapon Nonesung and Natapong Nitarach and Teetouch Jaknamon and Pittawat Taveekitworachai and Kunat Pipatanakul},
      year={2026},
      eprint={2601.14722},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2601.14722}, 
}
```
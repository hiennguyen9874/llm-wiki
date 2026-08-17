---
language:
- multilingual
base_model:
- Qwen/Qwen2.5-VL-3B-Instruct
tags:
- OCR
- image-to-text
- pdf2markdown
- VQA
pipeline_tag: image-text-to-text
library_name: transformers
---


<div align="center">
<p align="center">
    <img src="https://cdn-uploads.huggingface.co/production/uploads/626d198986671a29c70e688e/Vn6092flX4bQgzal2X04f.png" width="200" style="border-radius: 15px;"/>
<p>
<h1 align="center">
Nanonets-OCR2: A model for transforming documents into structured markdown with intelligent content recognition and semantic tagging
</h1>

<div align="center">
  <a href="https://docstrange.nanonets.com/" target="_blank"><strong>🖥️ Live Demo</strong></a> | 
  <a href="https://nanonets.com/research/nanonets-ocr-2/" target="_blank"><strong>📢 Blog</strong></a> | 
  <a href="https://github.com/NanoNets/docstrange" target="_blank"><strong>⌨️ GitHub</strong></a>
  <a href="https://github.com/NanoNets/Nanonets-OCR2" target="_blank"><strong>📖 Cookbooks</strong></a>
</div>

</div>

Nanonets-OCR2 by [Nanonets](https://nanonets.com) is a family of powerful, state-of-the-art image-to-markdown OCR models that go far beyond traditional text extraction. It transforms documents into structured markdown with intelligent content recognition and semantic tagging, making it ideal for downstream processing by Large Language Models (LLMs).

Nanonets-OCR2 is packed with features designed to handle complex documents with ease:

* **LaTeX Equation Recognition:** Automatically converts mathematical equations and formulas into properly formatted LaTeX syntax. It distinguishes between inline (`$...$`) and display (`$$...$$`) equations.
* **Intelligent Image Description:** Describes images within documents using structured `<img>` tags, making them digestible for LLM processing. It can describe various image types, including logos, charts, graphs and so on, detailing their content, style, and context.
* **Signature Detection & Isolation:** Identifies and isolates signatures from other text, outputting them within a `<signature>` tag. This is crucial for processing legal and business documents.
* **Watermark Extraction:** Detects and extracts watermark text from documents, placing it within a `<watermark>` tag.
* **Smart Checkbox Handling:** Converts form checkboxes and radio buttons into standardized Unicode symbols (`☐`, `☑`, `☒`) for consistent and reliable processing.
* **Complex Table Extraction:** Accurately extracts complex tables from documents and converts them into both markdown and HTML table formats.
* **Flow charts & Organisational charts:** Extracts flow charts and organisational as [mermaid](mermaid.js.org) code.
* **Handwritten Documents:** The model is trained on handwritten documents across multiple languages.
* **Multilingual:** Model is trained on documents of multiple languages, including English, Chinese, French, Spanish, Portuguese, German, Italian, Russian, Japanese, Korean, Arabic, and many more.
* **Visual Question Answering (VQA):** The model is designed to provide the answer directly if it is present in the document; otherwise, it responds with "Not mentioned."


## Nanonets-OCR2 Family
| Model | Access Link |
| -----|-----|
| Nanonets-OCR2-Plus | [Docstrange link](https://docstrange.nanonets.com/) |
| Nanonets-OCR2-3B | [🤗 link](https://huggingface.co/nanonets/Nanonets-OCR2-3B) |
| Nanonets-OCR2-1.5B-exp | [🤗 link](https://huggingface.co/nanonets/Nanonets-OCR2-1.5B-exp) |


## Usage
### Using transformers
```python
from PIL import Image
from transformers import AutoTokenizer, AutoProcessor, AutoModelForImageTextToText

model_path = "nanonets/Nanonets-OCR2-3B"

model = AutoModelForImageTextToText.from_pretrained(
    model_path, 
    torch_dtype="auto", 
    device_map="auto", 
    attn_implementation="flash_attention_2"
)
model.eval()

tokenizer = AutoTokenizer.from_pretrained(model_path)
processor = AutoProcessor.from_pretrained(model_path)


def ocr_page_with_nanonets_s(image_path, model, processor, max_new_tokens=4096):
    prompt = """Extract the text from the above document as if you were reading it naturally. Return the tables in html format. Return the equations in LaTeX representation. If there is an image in the document and image caption is not present, add a small description of the image inside the <img></img> tag; otherwise, add the image caption inside <img></img>. Watermarks should be wrapped in brackets. Ex: <watermark>OFFICIAL COPY</watermark>. Page numbers should be wrapped in brackets. Ex: <page_number>14</page_number> or <page_number>9/22</page_number>. Prefer using ☐ and ☑ for check boxes."""
    image = Image.open(image_path)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": [
            {"type": "image", "image": f"file://{image_path}"},
            {"type": "text", "text": prompt},
        ]},
    ]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt")
    inputs = inputs.to(model.device)
    
    output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, output_ids)]
    
    output_text = processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return output_text[0]

image_path = "/path/to/your/document.jpg"
result = ocr_page_with_nanonets_s(image_path, model, processor, max_new_tokens=15000)
print(result)
```

### Using vLLM
1. Start the vLLM server.
```bash
vllm serve nanonets/Nanonets-OCR2-3B
```
2. Predict with the model
```python
from openai import OpenAI
import base64

client = OpenAI(api_key="123", base_url="http://localhost:8000/v1")

model = "nanonets/Nanonets-OCR2-3B"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def ocr_page_with_nanonets_s(img_base64):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_base64}"},
                    },
                    {
                        "type": "text",
                        "text": "Extract the text from the above document as if you were reading it naturally. Return the tables in html format. Return the equations in LaTeX representation. If there is an image in the document and image caption is not present, add a small description of the image inside the <img></img> tag; otherwise, add the image caption inside <img></img>. Watermarks should be wrapped in brackets. Ex: <watermark>OFFICIAL COPY</watermark>. Page numbers should be wrapped in brackets. Ex: <page_number>14</page_number> or <page_number>9/22</page_number>. Prefer using ☐ and ☑ for check boxes.",
                    },
                ],
            }
        ],
        temperature=0.0,
        max_tokens=15000
    )
    return response.choices[0].message.content

test_img_path = "/path/to/your/document.jpg"
img_base64 = encode_image(test_img_path)
print(ocr_page_with_nanonets_s(img_base64))
```

### Using Docstrange

```python
import requests

url = "https://extraction-api.nanonets.com/extract"
headers = {"Authorization": <API KEY>}

files = {"file": open("/path/to/your/file", "rb")}
data = {"output_type": "markdown"}
data["model"] = "nanonets"

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
````

Check out [Docstrange](https://docstrange.nanonets.com/) for more details.

## Evaluation
### Markdown Evaluations

#### Nanonets OCR2 Plus
<table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
  <thead>
    <tr>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Model</th>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Win Rate vs Nanonets OCR2 Plus (%)</th>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Lose Rate vs Nanonets OCR2 Plus (%)</th>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Both Correct (%)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;"><strong>Gemini 2.5 flash (No Thinking)</strong></td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">34.35</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">57.60</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">8.06</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;"><strong>Nanonets OCR2 3B</strong></td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">29.37</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">54.58</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">16.04</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;"><strong>Nanonets-OCR-s</strong></td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">24.86</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">66.12</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">9.02</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;"><strong>Nanonets OCR2 1.5B exp</strong></td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">13.00</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">81.20</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">5.79</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;"><strong>GPT-5 (Thinking: low)</strong></td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">23.53</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">74.86</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">1.60</td>
    </tr>
  </tbody>
</table>

#### Nanonets OCR2 3B

<table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
  <thead>
    <tr>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Model</th>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Win Rate vs Nanonets OCR2 3B (%)</th>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Lose Rate vs Nanonets OCR2 3B (%)</th>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Both Correct (%)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;"><strong>Gemini 2.5 flash (No Thinking)</strong></td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">39.98</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">52.43</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">7.58</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;"><strong>Nanonets-OCR-s</strong></td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">30.61</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">58.28</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">11.12</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;"><strong>Nanonets OCR2 1.5B exp</strong></td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">14.78</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">79.18</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">6.04</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;"><strong>GPT-5</strong></td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">25.00</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">72.87</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">2.13</td>
    </tr>
  </tbody>
</table>

### Visual Question Answering (VQA) Evaluations
<table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
  <thead>
    <tr>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Dataset</th>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Nanonets OCR2 Plus</th>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Nanonets OCR2 3B</th>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Qwen2.5-VL-72B-Instruct</th>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Gemini 2.5 Flash</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;">ChartQA (IDP-Leaderboard)</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">79.20</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">78.56</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">76.20</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">84.82</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;">DocVQA (IDP-Leaderboard)</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">85.15</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">89.43</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">84.00</td>
      <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">85.51</td>
    </tr>
  </tbody>
</table>

## Tips to improve accuracy
1. Increasing the image resolution will improve model's performance.
2. For complex tables (eg. Financial documents) using `repetition_penalty=1` gives better results. You can try this prompt also, which generally works better for finantial documents.
```python
user_prompt = """Extract the text from the above document as if you were reading it naturally. Return the tables in HTML format. Return the equations in LaTeX representation. If there is an image in the document and image caption is not present, add a small description of the image inside the <img></img> tag; otherwise, add the image caption inside <img></img>. Watermarks should be wrapped in brackets. Ex: <watermark>OFFICIAL COPY</watermark>. Page numbers should be wrapped in brackets. Ex: <page_number>14</page_number> or <page_number>9/22</page_number>. Prefer using ☐ and ☑ for check boxes. Only return HTML table within <table></table>."""
```
3. This is already implemented in [Docstrange](https://docstrange.nanonets.com/?output_type=markdown-financial-docs), please use the `Markdown (Financial Docs)` option for processing table heavy financial documents.
```python
import requests

url = "https://extraction-api.nanonets.com/extract"
headers = {"Authorization": <API KEY>}

files = {"file": open("/path/to/your/file", "rb")}
data = {"output_type": "markdown-financial-docs"}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```
4. Model might work best on certain resolution for specific document types. Please check the [cookbooks](https://github.com/NanoNets/Nanonets-OCR2/blob/main/Nanonets-OCR2-Cookbook/image2md.ipynb) for details.


## BibTex
```
@misc{Nanonets-OCR2,
  title={Nanonets-OCR2: A model for transforming documents into structured markdown with intelligent content recognition and semantic tagging},
  author={Souvik Mandal and Ashish Talewar and Siddhant Thakuria and Paras Ahuja and Prathamesh Juvatkar},
  year={2025},
}
```
---
license: apache-2.0
language:
- en
base_model:
- Qwen/Qwen2.5-VL-7B-Instruct
library_name: transformers
---

<img alt="olmOCR Logo" src="https://cdn-uploads.huggingface.co/production/uploads/6734d6722769638944a5aa2e/DPsr3ZvRF9v-gdMa4EaHW.png" width="300px" style="margin-left:'auto' margin-right:'auto' display:'block'">

# olmOCR-2-7B-1025

Full BF16 version of [olmOCR-2-7B-1025-FP8](https://huggingface.co/allenai/olmOCR-2-7B-1025-FP8).
We recommend using the FP8 version for all practical purposes except further fine tuning.

This is a release of the olmOCR model that's fine tuned from Qwen2.5-VL-7B-Instruct using the 
[olmOCR-mix-1025](https://huggingface.co/datasets/allenai/olmOCR-mix-1025) dataset. It has been additionally
fine tuned using GRPO RL training to boost its performance at math equations, tables, and other tricky OCR cases.

Quick links:
- 📃 [Paper](https://olmocr.allenai.org/papers/olmocr.pdf)
- 🤗 [SFT Dataset](https://huggingface.co/datasets/allenai/olmOCR-mix-1025)
- 🤗 [RL Dataset](https://huggingface.co/datasets/allenai/olmOCR-synthmix-1025)
- 🛠️ [Code](https://github.com/allenai/olmocr)
- 🎮 [Demo](https://olmocr.allenai.org/)

The best way to use this model is via the [olmOCR toolkit](https://github.com/allenai/olmocr).
The toolkit comes with an efficient inference setup via VLLM that can handle millions of documents
at scale.


## olmOCR-Bench Scores

This model scores the following scores on [olmOCR-bench](https://huggingface.co/datasets/allenai/olmOCR-bench) when used with the
[olmOCR toolkit](https://github.com/allenai/olmocr) toolkit which automatically renders, rotates, and retries pages as needed.

<table>
  <thead>
    <tr>
      <th align="left"><strong>Model</strong></th>
      <th align="center">ArXiv</th>
      <th align="center">Old Scans Math</th>
      <th align="center">Tables</th>
      <th align="center">Old Scans</th>
      <th align="center">Headers and Footers</th>
      <th align="center">Multi column</th>
      <th align="center">Long tiny text</th>
      <th align="center">Base</th>
      <th align="center">Overall</th>
    </tr>
  </thead>
  <tbody> 
     <tr>
      <td align="left">olmOCR pipeline v0.4.0 with olmOCR-2-7B-1025</td>
      <td align="center">82.9</td>
      <td align="center">82.1</td>
      <td align="center">84.3</td>
      <td align="center">48.3</td>
      <td align="center">95.7</td>
      <td align="center">84.3</td>
      <td align="center">81.4</td>
      <td align="center">99.7</td>
      <td align="center">82.3 ± 1.1</td>
    </tr>  
    <tr>
      <td align="left">olmOCR pipeline v0.4.0 with olmOCR-2-7B-1025-FP8</td>
      <td align="center">83.0</td>
      <td align="center">82.3</td>
      <td align="center">84.9</td>
      <td align="center">47.7</td>
      <td align="center">96.1</td>
      <td align="center">83.7</td>
      <td align="center">81.9</td>
      <td align="center">99.7</td>
      <td align="center">82.4 ± 1.1</td>
    </tr>  
  </tbody>
</table>


## Usage

This model expects as input a single document image, rendered such that the longest dimension is 1288 pixels.

The prompt must then contain the additional metadata from the document, and the easiest way to generate this
is to use the methods provided by the [olmOCR toolkit](https://github.com/allenai/olmocr).

## Manual Prompting

If you want to prompt this model manually instead of using the [olmOCR toolkit](https://github.com/allenai/olmocr), please see the code below.

In normal usage, the olmOCR toolkit builds the prompt by rendering the PDF page, and
extracting relevant text blocks and image metadata. To duplicate that you will need to

```bash
pip install olmocr>=0.4.0
```

and then run the following sample code.


```python
import torch
import base64
import urllib.request

from io import BytesIO
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

from olmocr.data.renderpdf import render_pdf_to_base64png
from olmocr.prompts import build_no_anchoring_v4_yaml_prompt

# Initialize the model
model = Qwen2_5_VLForConditionalGeneration.from_pretrained("allenai/olmOCR-2-7B-1025", torch_dtype=torch.bfloat16).eval()
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Grab a sample PDF
urllib.request.urlretrieve("https://olmocr.allenai.org/papers/olmocr.pdf", "./paper.pdf")

# Render page 1 to an image
image_base64 = render_pdf_to_base64png("./paper.pdf", 1, target_longest_image_dim=1288)


# Build the full prompt
messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": build_no_anchoring_v4_yaml_prompt()},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                ],
            }
        ]

# Apply the chat template and processor
text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
main_image = Image.open(BytesIO(base64.b64decode(image_base64)))

inputs = processor(
    text=[text],
    images=[main_image],
    padding=True,
    return_tensors="pt",
)
inputs = {key: value.to(device) for (key, value) in inputs.items()}


# Generate the output
output = model.generate(
            **inputs,
            temperature=0.1,
            max_new_tokens=50,
            num_return_sequences=1,
            do_sample=True,
        )

# Decode the output
prompt_length = inputs["input_ids"].shape[1]
new_tokens = output[:, prompt_length:]
text_output = processor.tokenizer.batch_decode(
    new_tokens, skip_special_tokens=True
)

print(text_output)
# ['---\nprimary_language: en\nis_rotation_valid: True\nrotation_correction: 0\nis_table: False\nis_diagram: False\n---\nolmOCR: Unlocking Trillions of Tokens in PDFs with Vision Language Models\n\nJake Poz']
```

## License and use

This model is licensed under Apache 2.0. It is intended for research and educational use in accordance with Ai2's [Responsible Use Guidelines](https://allenai.org/responsible-use).
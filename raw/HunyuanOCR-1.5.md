---
license: other
license_name: tencent-hunyuan-community
license_link: https://huggingface.co/tencent/HunyuanOCR/blob/main/LICENSE
language:
  - multilingual
  - en
  - zh
tags:
  - ocr
  - vision-language-model
  - document-parsing
  - text-spotting
  - information-extraction
  - text-image-translation
pipeline_tag: image-text-to-text
library_name: transformers
---

# HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better

<p align="center">
  <img src="assets/HyOCR_1_5_teaser.png" width="90%"/>
</p>

🤗 [HF Model](https://huggingface.co/tencent/HunyuanOCR) | 💻 [GitHub Repo](https://github.com/Tencent-Hunyuan/HunyuanOCR) | 📄 [Paper](https://arxiv.org/pdf/2607.04884)

> 📦 **Model layout.** This repository hosts **HunyuanOCR-1.5** checkpoint at the root (target base weights). The **DFlash speculative-decoding draft** lives under [`dflash/`](https://huggingface.co/tencent/HunyuanOCR/tree/main/dflash), and the previous **HunyuanOCR-1.0** is archived under [`v1.0/`](https://huggingface.co/tencent/HunyuanOCR/tree/main/v1.0) (load it with `subfolder="v1.0"`, or download the `v1.0/` directory directly).

---

## 📖 Introduction

**HunyuanOCR-1.5** is a lightweight, end-to-end OCR-specialized vision-language model. It targets a broad range of text-centric visual tasks and unifies **document parsing, text spotting, information extraction, text-image translation** within a single end-to-end VLM.

Building upon the validated lightweight architecture of HunyuanOCR-1.0, HunyuanOCR-1.5 does **not** redesign the model backbone. Instead, it performs a systematic upgrade around two goals — **making the model faster and better**:

- ⚡ **Faster — DFlash inference acceleration.** End-to-end OCR is often accompanied by long autoregressive decoding, which becomes the major bottleneck for dense documents, tables, formulas, and other long structured outputs. HunyuanOCR-1.5 adapts a speculative-decoding framework based on **DFlash**: a lightweight block-diffusion draft model drafts multiple candidate tokens in parallel, which are then verified by the target model in a single pass. This significantly reduces the decoding latency of long structured outputs while **preserving the output distribution** of the target model.
- 💻 **PC-side deployment via llama.cpp.** Beyond server-grade vLLM, HunyuanOCR-1.5 also supports **CPU / consumer-GPU / laptop** deployment through [`llama.cpp`](https://github.com/ggml-org/llama.cpp) with a GGUF-converted checkpoint and an OpenAI-compatible `llama-server`. A DFlash-adapted `llama.cpp` fork is provided as well, so the same speculative-decoding acceleration is available on PC.
- 🧠 **Better — Agentic Data Flow + upgraded training recipe.** On the data side, we propose **Agentic Data Flow**, an agent-driven data-construction system that translates model weaknesses into executable data requirements. Agents deeply participate in material search, tool-based verification, sample cleaning, and data-pipeline development, and iterate in a closed loop with algorithm engineers. In HunyuanOCR-1.5, this system is used for targeted long-tail capabilities such as **low-resource OCR, ancient-script OCR, and multi-image text-centric QA**. On the training side, we systematically upgrade the recipe: pretraining Stage-3 is re-planned to incorporate the newly produced capability data, multi-image data, and historical OCR data, with maximum image resolution extended to **4K** and context window extended to **128K**; post-training refines the SFT data and further explores RL across different OCR tasks to amplify the gains from reinforcement learning.

Together, HunyuanOCR-1.5 achieves **both faster inference and broader OCR capability coverage** while retaining the deployment advantages of a lightweight end-to-end model. The full SFT / DFlash training pipeline and the transformers / vLLM / llama.cpp inference stack are open-sourced in the [GitHub repo](https://github.com/Tencent-Hunyuan/HunyuanOCR).

---

## ⚙️ Environment

Inference now uses a **single unified environment** (built on `uv`, **requires CUDA 13**) that runs all three configurations from the same install: **vLLM AR, DFlash speculative decoding, and native transformers**. Accuracy alignment across the three has been verified.

```bash
pip install uv
uv venv --python 3.12.11 && source .venv/bin/activate
uv pip install "vllm>=0.25.1"
uv pip install --no-build-isolation --no-cache-dir "flash-attn==2.8.3"
```

The inference code lives on GitHub under [`inference/`](https://github.com/Tencent-Hunyuan/HunyuanOCR/tree/main/inference) (`inference/vLLM`, `inference/DFlash`, `inference/transformers`). See [`docs/inference/inference.md`](https://github.com/Tencent-Hunyuan/HunyuanOCR/blob/main/docs/inference/inference.md) for the full setup and usage. If you lack CUDA 13 or only need one configuration, that document also points to the lighter per-configuration recipes in the archive.

**Common prerequisites:** Python 3.10+ (3.12 tested), an NVIDIA GPU, and `huggingface_hub` for downloading the weights:

```bash
pip install -U "huggingface_hub[cli]"
# target base (1.5) — skip the archived 1.0 to save space
huggingface-cli download tencent/HunyuanOCR --local-dir ./HunyuanOCR --exclude "v1.0/*"
```

The download contains both the base model and the `dflash/` draft model.

---

## 🧪 Inference

All configurations share the same weights and the same task-type prompts + sampling (`temperature=0.0`, `top_p=1.0`, `top_k=-1`, `repetition_penalty=1.08`) + post-processing, so their outputs are directly comparable. Grab the toolkit from GitHub first:

```bash
git clone https://github.com/Tencent-Hunyuan/HunyuanOCR.git
cd HunyuanOCR
```

### A. HuggingFace transformers (native)

The model ships the official `HunYuanVLForConditionalGeneration` + `AutoProcessor`
integration (transformers **≥ 5.13.0**). The simplest path — weights are pulled
from the Hub automatically:

```python
import torch
from transformers import AutoProcessor, HunYuanVLForConditionalGeneration

MODEL_ID = "tencent/HunyuanOCR"

processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True, use_fast=False)
model = HunYuanVLForConditionalGeneration.from_pretrained(
    MODEL_ID, torch_dtype=torch.bfloat16, device_map="auto",
    trust_remote_code=True,
).eval()

prompt = (
    "提取文档图片中正文的所有信息用markdown格式表示，其中页眉、页脚部分忽略，"
    "表格用html格式表达，文档中公式用latex格式表示，按照阅读顺序组织进行解析。"
)
messages = [{
    "role": "user",
    "content": [
        {"type": "image", "image": "/path/to/document.png"},
        {"type": "text",  "text":  prompt},
    ],
}]
inputs = processor.apply_chat_template(
    messages, add_generation_prompt=True, tokenize=True,
    return_dict=True, return_tensors="pt",
).to(model.device)
with torch.inference_mode():
    out = model.generate(**inputs, max_new_tokens=8000, do_sample=False)
gen = out[:, inputs["input_ids"].shape[1]:]
print(processor.batch_decode(gen, skip_special_tokens=True)[0])
```

For **multi-GPU batch inference** with sampling / early-stop / doc-parse
normalization strictly aligned to the vLLM client, use the shipped script
after installing the unified environment (see
[`docs/inference/inference.md`](https://github.com/Tencent-Hunyuan/HunyuanOCR/blob/main/docs/inference/inference.md)):

```bash
python inference/transformers/infer_hf_8gpu.py \
    --model ./HunyuanOCR --attn-implementation flash_attention_2 \
    --input ./input.jsonl --output ./results/hf_out \
    --gpu-ids 0,1,2,3,4,5,6,7 --max-new-tokens 32768 \
    --merge
```

### B. vLLM (OpenAI-compatible)

The unified environment (installed as shown above) serves the model as `tencent/HunyuanOCR` with `-tp 1` and `--max-model-len 131072`, and supports both plain autoregressive (AR) decoding and DFlash speculative decoding from
the **same install**.

**AR (baseline).** Launch the vLLM server:

```bash
MODEL_PATH=./HunyuanOCR GPU=0 PORT=8000 bash inference/vLLM/serve.sh
curl -sf http://127.0.0.1:8000/v1/models     # readiness check
```

**DFlash (speculative decoding).** The DFlash draft ships under the `dflash/`
subfolder of `tencent/HunyuanOCR`, so it is already inside `./HunyuanOCR` after
the `huggingface-cli download` above. `serve_DFlash.sh` defaults `DFLASH_PATH`
to `${MODEL_PATH}/dflash`, so no manual copy is needed:

```bash
MODEL_PATH=./HunyuanOCR GPU=0 PORT=8000 bash inference/DFlash/serve_DFlash.sh
```

**Client (either mode).** Send one image with the shipped client. The
prompt is locked to an official task type via `--task-type` (run
`--list-tasks` to see all); sampling and streaming tail-repetition early-stop
/ cleanup are built in:

```bash
python inference/vLLM/infer_vllm_client.py \
    --host 127.0.0.1 --port 8000 \
    --model tencent/HunyuanOCR \
    --image /path/to/document.png \
    --task-type doc_parse \
    --max-tokens 32768

# add --no-stream            to disable streaming + early-stop
# add --no-doc-postprocess   to disable doc_parse markdown normalization
```

Available task types (`--task-type`): `doc_parse` (default), `structured_parse`, `spotting_json`, `spotting_hunyuan`, `layout`, `layout_parse`, `chart_parse`, `formula`, `table`, `doc_trans_en2zh`, `trans_other2en`, `trans_other2zh`.

For **batch** inference over a directory (same task types, multi-endpoint
concurrency, resumable):

```bash
python inference/vLLM/batch_infer.py \
    --image-dir /path/to/images \
    --out-dir /path/to/output \
    --ports 8000 \
    --task-type doc_parse \
    --max-tokens 32768 \
    --concurrency 16
```

Or hand-written with the OpenAI SDK:

```python
import base64
from openai import OpenAI

def data_url(p):  # Mime is fixed to image/jpeg
    return f"data:image/jpeg;base64,{base64.b64encode(open(p,'rb').read()).decode()}"

client = OpenAI(api_key="EMPTY", base_url="http://127.0.0.1:8000/v1")
resp = client.chat.completions.create(
    model="tencent/HunyuanOCR",
    messages=[
        {"role": "system", "content": ""},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": data_url("/path/to/document.png")}},
            {"type": "text", "text": "请提取图片中的文字内容。"},
        ]},
    ],
    max_tokens=32768,
    temperature=0.0, top_p=1.0,
    extra_body={"top_k": -1, "repetition_penalty": 1.08, "skip_special_tokens": True},
)
print(resp.choices[0].message.content)
```

### C. PC-side deployment via llama.cpp

For **CPU / consumer-GPU / laptop** environments, HunyuanOCR-1.5 can also be deployed through [`llama.cpp`](https://github.com/ggml-org/llama.cpp) after converting the checkpoint to GGUF. Both the community `llama.cpp` (HunyuanOCR base only) and a DFlash-adapted fork ([`wendadawen/llama.cpp @ dflash-adapt-hunyuanocr-hunyuanstyle`](https://github.com/wendadawen/llama.cpp/tree/dflash-adapt-hunyuanocr-hunyuanstyle)) are supported.

Minimal build & serve (community, no DFlash):

```bash
# 1. Build
git clone https://github.com/ggml-org/llama.cpp.git && cd llama.cpp
cmake -B build -DLLAMA_BUILD_EXAMPLES=ON   # add -DGGML_CUDA=ON for NVIDIA GPU
cmake --build ./build --config Release -j

# 2. Convert HunyuanOCR to GGUF (base + mmproj)
hf download tencent/HunyuanOCR --local-dir ./HunyuanOCR --exclude "v1.0/*"
python3 convert_hf_to_gguf.py --outfile ./HunyuanOCR/hyocr-f16.gguf --outtype f16 ./HunyuanOCR
python3 convert_hf_to_gguf.py --outfile ./HunyuanOCR/mmproj-hyocr-f16.gguf --outtype f16 --mmproj ./HunyuanOCR

# 3. Serve (OpenAI-compatible)
build/bin/llama-server \
  --model ./HunyuanOCR/hyocr-f16.gguf \
  --mmproj ./HunyuanOCR/mmproj-hyocr-f16.gguf \
  --host 0.0.0.0 --port 8080 --alias HYVL \
  --ctx-size 10240 --n-predict 4096
```

The DFlash-adapted variant and the full guide are in [`docs/llama_cpp.md`](https://github.com/Tencent-Hunyuan/HunyuanOCR/blob/main/docs/llama_cpp.md) in the GitHub repo.

---

## 🎯 Default OCR prompt for document parsing

```
提取文档图片中正文的所有信息用markdown格式表示，其中页眉、页脚部分忽略，表格用html格式表达，文档中公式用latex格式表示，按照阅读顺序组织进行解析。
```

The model also handles text spotting, information extraction, and text-image translation — pass a task-specific instruction as the text prompt (or use `--task-type` with the shipped client).

---

## 🔗 Related resources

- **GitHub — training & inference toolkit**: <https://github.com/Tencent-Hunyuan/HunyuanOCR>
- **verl-based RL training stack** (GRPO on HunyuanOCR-1.5): [`train_verl/`](https://github.com/Tencent-Hunyuan/HunyuanOCR/blob/main/train_verl/README_en.md)
- **DFlash draft weights**: [`tencent/HunyuanOCR/dflash`](https://huggingface.co/tencent/HunyuanOCR/tree/main/dflash)
- **HunyuanOCR-1.0** (previous generation, archived under `v1.0/`): [`tencent/HunyuanOCR/v1.0`](https://huggingface.co/tencent/HunyuanOCR/tree/main/v1.0)

---

## 🙏 Acknowledgements

We would like to thank [Qwen](https://github.com/QwenLM/Qwen3.6) and [DFlash](https://github.com/z-lab/dflash) for their valuable models and ideas.

Special thanks to the Hugging Face community for their Day-0 support.

---

## 📜 License

HunyuanOCR-1.5 is released under the same license as HunyuanOCR 1.0 — the **Tencent Hunyuan Community License Agreement**. See [`LICENSE`](https://huggingface.co/tencent/HunyuanOCR/blob/main/LICENSE) for the full terms.

---

## 📚 Citation

```bibtex
@article{HunyuanOCR_1_5_2026,
  title   = {{HunyuanOCR-1.5}: Making Lightweight {OCR} {VLMs} Faster and Better},
  author  = {Li, Gengluo and Wan, Xingyu and Peng, Shangpin and Wang, Weinong and Feng, Hao and Du, Yongkun and Wu, Binghong and Ruan, Zheng and Lu, Zhiqiong and Wu, Liang and Lyu, Pengyuan and Shen, Huawen and Lin, Zibin and Hu, Shijing and Yang, Jieneng and Wen, Hongbing and Yu, Guanghua and Liu, Hong and Wang, Bochao and Ma, Can and Hu, Han and Zhang, Chengquan and Zhou, Yu},
  journal = {arXiv preprint arXiv:2607.04884},
  year    = {2026}
}
```

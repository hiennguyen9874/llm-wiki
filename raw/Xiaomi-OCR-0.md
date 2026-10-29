---
license: apache-2.0
base_model: Qwen/Qwen3.5-0.8B-Base
library_name: transformers
pipeline_tag: image-text-to-text
tags:
  - ocr
  - document-parsing
  - document-understanding
  - visual-question-answering
  - key-information-extraction
  - vision-language-model
  - multimodal
  - xiaomi
  - seerray
datasets:
  - custom-ocr-centric-corpus
metrics:
  - accuracy
  - teds
  - cdm
---

<div align="center" style="text-align:center">
<p><img src="https://huggingface.co/SeerRay-Lab/Xiaomi-OCR-0/resolve/main/assets/xiaomi-logo.svg" alt="Xiaomi" width="88" height="88" style="display:block;margin-left:auto;margin-right:auto"></p>
<h1>Xiaomi-OCR-0</h1>
<p><b>A unified 0.8B model for document parsing and OCR-related understanding.</b></p>
<p><b>English</b> · <a href="https://huggingface.co/SeerRay-Lab/Xiaomi-OCR-0/blob/main/README_zh.md">简体中文</a></p>
<p><a href="https://huggingface.co/spaces/SeerRay-Lab/Xiaomi-OCR-0"><img src="https://img.shields.io/badge/Project-Page-FF6900?logo=huggingface&logoColor=FFD21E" alt="Project Page"></a> <a href="https://github.com/SeerRay-Lab/Xiaomi-OCR-0"><img src="https://img.shields.io/badge/GitHub-SeerRay--Lab%2FXiaomi--OCR--0-181717?logo=github" alt="GitHub"></a> <a href="https://arxiv.org/abs/2609.36136"><img src="https://img.shields.io/badge/arXiv-2609.36136-B31B1B?logo=arxiv" alt="arXiv"></a> <a href="https://ollama.com/longwayxu/xiaomi-ocr-0:bf16"><img src="https://img.shields.io/badge/Ollama-BF16%20%28experimental%29-000000?logo=ollama&amp;logoColor=white" alt="Ollama BF16 (experimental)"></a> <a href="https://www.modelscope.cn/models/SeerRay-Lab/Xiaomi-OCR-0"><img src="https://img.shields.io/badge/ModelScope-Model-624AFF?logo=ModelScope&amp;logoColor=white" alt="ModelScope Model"></a></p>
</div>

Xiaomi-OCR-0 is a unified 0.8B OCR-specialized vision-language model for both **document parsing** and **OCR-centric understanding**.

## 🏆 Benchmark results

- 🥇 **95.24** on Real5-OmniDocBench, ranked **#1**.
- 🥈 **96.83** on OmniDocBench v1.6 and **87.94** on Wild-OmniDocBench, both ranked **#2**.
- 📐 **97.84** on UniMER-Test (formula recognition) and **92.27** on PubTabNet (table recognition).
- ✍️ Historical handwriting and calligraphy: **73** on Chronicles-OCR Mature Scripts (Clerical, Cursive, Running, and Regular scripts), on par with Seed 2.0 Pro(72).
- 🧠 An average of **83.2** across five OCR-centric VQA benchmarks, exceeding Qwen3.5-2B (**80.9**) with only **0.8B** parameters.

## 📰 News

- **2026-10-08:** Thanks to the community for supporting Xiaomi-OCR-0 and contributing [prithivMLmods’ GGUF](https://huggingface.co/prithivMLmods/Xiaomi-OCR-0-GGUF), [xzl01’s GGUF](https://github.com/xzl01/Xiaomi-OCR-0-GGUF), and [ByronLeeee’s BF16 NInfer conversion](https://huggingface.co/ByronLeeee/Xiaomi-OCR-0-Ninfer).
- **2026-09-30:** Technical report published and model weights released.

## About the model

Starting from Qwen3.5-0.8B-Base, Xiaomi-OCR-0 is trained on an approximately 170M-sample OCR-centric corpus with a progressive training recipe:

- 📍 **Q-Mask text anchoring**: align fine-grained text with its location
- 📚 **OCR-centric continued pretraining (CPT)**: build broad, multi-task capability
- 🎯 **Mixed-task reinforcement learning (Mix-RL)**: use verifiable rewards on hard examples


## ✨ Highlights

- 🧩 **Compact and unified**: one 0.8B model covering document parsing, OCR-oriented VQA, and key information extraction (KIE).
- 🧪 **Scalable data engine**: combines heterogeneous-expert consensus, render-guided verification, multi-factor sample mining, and targeted synthesis.
- 📄 **Robust document parsing**: stable on standard documents and on scanned, warped, photographed, skewed, and otherwise recaptured ones.
- 💬 **OCR-centric understanding**: supports question answering and structured field extraction, not just transcription.

<a id="benchmark-comparisons"></a>

## 📊 Benchmark comparisons

<details>
<summary>Parameter efficiency charts</summary>

![Parameter efficiency on OmniDocBench v1.6](assets/omni-parameters.png)

![Parameter efficiency on OCR-oriented VQA](assets/vqa-parameters.png)

![Parameter efficiency on Real5-OmniDocBench](assets/real5-parameters.png)

![Parameter efficiency on Wild-OmniDocBench](assets/wild-parameters.png)

</details>

↑ means higher is better, ↓ means lower is better; bold only marks Xiaomi-OCR-0 and does not necessarily indicate the best value in a column.

### Document parsing: selected comparisons

| Model | Size | OmniDocBench v1.6 ↑ | Real5 ↑ | Wild ↑ |
|:--|--:|--:|--:|--:|
| **Xiaomi-OCR-0** | **0.8B** | **96.83** | **95.24** | **87.94** |
| TeleOCR | 1.2B | 96.87 | — | 88.53 |
| OvisOCR2 | 0.8B | 96.58 | 92.29 | 87.91 |
| PaddleOCR-VL-1.6 | 0.9B | 96.33 | 93.19 | 87.36 |
| MinerU2.5-Pro | 1.2B | 95.75 | 88.94 | 87.33 |
| GLM-OCR | 0.9B | 95.22 | 90.32 | 85.08 |

All three columns report Overall score; “—” means the source table does not report it.

### OCR-centric visual question answering

| Model | Size | DocVQA | InfoVQA | ChartQA | OCRBench | TextVQA | Mean |
|:--|--:|--:|--:|--:|--:|--:|--:|
| **Xiaomi-OCR-0** | **0.8B** | **93.1** | **75.1** | **84.6** | **84.6** | **78.6** | **83.2** |
| Qwen3.5-0.8B | 0.8B | 88.5 | 60.3 | 69.5 | 77.9 | 68.3 | 72.9 |
| Qwen3.5-2B | 2B | 92.4 | 72.4 | 77.0 | 85.9 | 76.9 | 80.9 |
| Qwen3.5-4B | 4B | 94.4 | 80.4 | 82.4 | 86.6 | 80.8 | 84.9 |
| MiniCPM-V-4.5 | 8B | 84.9 | 69.6 | 87.4 | 89.0 | 82.2 | 82.6 |

The mean is the arithmetic average of these five benchmarks on a 0–100 scale.

## 🧬 Data Engine

![Automated annotation pipeline. Document regions are annotated by heterogeneous experts, scored by triplet consensus, and refined through render-guided verification when agreement is insufficient; refined candidates return to the expert pool for re-consensus.](assets/data-engine.png)

Xiaomi-OCR-0 is trained on an approximately 170M-sample corpus covering document parsing and OCR-centric understanding. The parsing data engine provides supervision for text, tables, and formulas through three main components.

#### Ensemble Triplet Consensus

A heterogeneous expert pool generates candidate annotations for text, tables, and formulas. Xiaomi-OCR-0 uses **Ensemble Triplet Consensus (ETC)** to rank candidates by pool-wide agreement, select a three-expert consensus subset, and send uncertain samples for further refinement.

The expert pool in the technical report includes PaddleOCR-VL-1.6, MinerU2.5-Pro, GLM-OCR, dots.mocr, HunyuanOCR-1.5, TeleOCR, OvisOCR2, and Qianfan-OCR.

#### Render-Guided Refine-and-Judge

When experts disagree, candidate annotations are rendered back into images and compared against the source region. This makes structural errors in tables and formulas easier to catch and correct before the samples enter training.

#### Multi-Factor Mining and Targeted Synthesis

Training samples are selected by a combination of:

- expert agreement
- model self-consistency
- semantic clustering
- verified model failure patterns

Synthetic data is generated in two complementary ways:

- **Coverage-driven synthesis**: fills in structures, styles, glyphs, and domains that are under-covered
- **Failure-driven synthesis**: targets errors that recur during training

## 📸 Key Findings

> During training, we studied how OCR-centric understanding data (hereafter “understanding”) affects document parsing metrics (hereafter “parsing”), and compared the gains of Mix-RL against MOPD (one parsing teacher and one understanding teacher), in the hope of offering the community some useful insight ✨

### 1. Adding understanding data benefits parsing once parsing capability is already strong

![Absolute parsing scores before and after adding understanding supervision at each stage](assets/takeaway-parsing-stages.png)

The early-stage change is **−0.330**; the middle-stage gain is **+0.639**, followed by **+0.0749** on the stronger late-stage baseline. The three stages use 9%, 29%, and 50% of all parsing data, and each gain is measured against that stage's parsing baseline.

### 2. Understanding needs more parameters and is harder than parsing

The 4B and 0.8B models below go through the same CPT process to keep their data aligned, and are then trained on domain-specific data to produce two expert models.

**_(a) Document parsing: OmniDocBench v1.6_**

| Model | Overall ↑ | Text Edit ↓ | Formula CDM ↑ | Table TEDS ↑ | Table TEDS-S ↑ | Reading Order Edit ↓ |
|:--|--:|--:|--:|--:|--:|--:|
| 4B parsing teacher | **96.9745** | **0.0308** | 98.4102 | **95.5932** | **97.5050** | 0.1228 |
| 0.8B CPT | 96.4739 | 0.0332 | 98.3444 | 94.3973 | 96.6835 | **0.1221** |
| 0.8B MOPD | 96.7417 | 0.0314 | 98.4677 | 94.8975 | 97.1579 | 0.1223 |
| 0.8B Mix-RL | 96.8277 | 0.0313 | **98.5044** | 95.1087 | 97.1929 | **0.1221** |

**_(b) OCR-centric understanding: five OCR-VQA benchmarks_**

| Model | Overall ↑ | DocVQA ↑ | InfoVQA ↑ | ChartQA ↑ | OCRBench ↑ | TextVQA ↑ |
|:--|--:|--:|--:|--:|--:|--:|
| 4B VQA teacher | **88.1** | **95.9** | **84.4** | **87.1** | **88.3** | **84.8** |
| 0.8B CPT | 78.1 | 92.2 | 72.5 | 83.4 | 80.6 | 62.0 |
| 0.8B MOPD | 82.7 | 93.1 | 74.8 | 84.2 | 83.9 | 77.5 |
| 0.8B Mix-RL | 83.2 | 93.1 | 75.1 | 84.6 | 84.6 | 78.6 |

Scaling from 0.8B to 4B brings a clearly larger gain on understanding (about **4.9** points, 88.1 vs 83.2) than on parsing (about **0.15** points, 96.9745 vs 96.8277). Within each task, the teacher and the student use the same amount of task data; the difference is that each teacher specializes in a single domain while the student trains on both. VQA Overall is the arithmetic average of the five benchmarks on a 0–100 scale.

### 3. MOPD converges fast, while longer-trained Mix-RL reaches a higher peak

![Observed Mix-RL and MOPD training trajectories on a shared relative compute scale](assets/takeaway-training-compute.png)

For more detail, including the full analysis behind these findings, see the [technical report](https://arxiv.org/abs/2609.36136).

## 🚀 Usage

### Community model conversions

### GGUF quantizations

[prithivMLmods/Xiaomi-OCR-0-GGUF](https://huggingface.co/prithivMLmods/Xiaomi-OCR-0-GGUF) provides `BF16`, `Q3_K_L`, `Q3_K_M`, `Q4_K_M`, `Q4_K_S`, `Q5_K_M`, `Q5_K_S` and `Q6_K` weights. Image inference also requires the repository's `Xiaomi-OCR-0.mmproj-bf16.gguf` vision projector. See the [file list](https://huggingface.co/prithivMLmods/Xiaomi-OCR-0-GGUF/tree/main) for downloads and sizes. We have not evaluated these community GGUF conversions; the original model's benchmark scores and Ollama alignment checks do not establish their accuracy.

[xzl01/Xiaomi-OCR-0-GGUF](https://github.com/xzl01/Xiaomi-OCR-0-GGUF) also provides Q4_K_M and Q8_0 llama.cpp weights with an F16 vision projector. See its repository for conversion scripts and measured results.

### NInfer BF16

[ByronLeeee/Xiaomi-OCR-0-Ninfer](https://huggingface.co/ByronLeeee/Xiaomi-OCR-0-Ninfer) provides a BF16 NInfer package with language and vision weights, tokenizer, and image-processing configuration. See its model page for the build guide and contributor-reported runtime and output comparisons. We have not independently reproduced those measurements; they are separate from the benchmark results for the original checkpoint above.

### 🦙 Ollama (experimental)

A [community BF16 GGUF package](https://ollama.com/longwayxu/xiaomi-ocr-0:bf16), including the text model and vision projector, is available for local use (about 1.8 GB). With [Ollama](https://ollama.com/download) installed and running:

```bash
ollama pull longwayxu/xiaomi-ocr-0:bf16
```

Then follow the [Ollama guide](https://github.com/SeerRay-Lab/Xiaomi-OCR-0/blob/main/OLLAMA.md) to use the repository's **MCP service or browser Demo**. These integrations automatically apply the image preprocessing, non-thinking prompt and decoding settings used in our alignment checks. Pulling the model alone does not configure these steps; no additional wrapper script is needed with the MCP or Demo. The guide covers agent setup, OCR, PDF parsing, KIE and VQA; region mode requires additional layout dependencies.

### Transformers

Install the verified combination with [uv](https://docs.astral.sh/uv/), then run whole-page parsing on any document image:

```bash
uv venv --python 3.13
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install "transformers==5.17.0" "torch==2.14.0" "torchvision==0.29.0" pillow
```

```python
import torch
from huggingface_hub import hf_hub_download
from transformers import AutoModelForImageTextToText, AutoProcessor

MODEL = "SeerRay-Lab/Xiaomi-OCR-0"  # Or a local model directory
# Choose "qianziwen.jpeg" or "dense-equations.jpg".
IMAGE = hf_hub_download(
    repo_id="SeerRay-Lab/Xiaomi-OCR-0",
    filename="example_pics/qianziwen.jpeg",
)
PROMPT = (
    "Extract all information from the main body of the document image and represent it "
    "in markdown format, ignoring headers and footers. Tables should be expressed in OTSL "
    "format, formulas in the document should be represented using LATEX format, and the "
    "parsing should be organized according to the reading order."
)

device = (
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
dtype = torch.float32 if device == "cpu" else torch.float16
processor = AutoProcessor.from_pretrained(MODEL)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL, dtype=dtype,
).to(device).eval()

messages = [{
    "role": "user",
    "content": [
        {"type": "image", "url": IMAGE},
        {"type": "text", "text": PROMPT},
    ],
}]
inputs = processor.apply_chat_template(
    messages, tokenize=True, add_generation_prompt=True,
    return_dict=True, return_tensors="pt",
)
inputs = inputs.to(device)

with torch.inference_mode():
    output = model.generate(**inputs, max_new_tokens=4096, do_sample=False)

new_tokens = output[:, inputs["input_ids"].shape[1]:]
print(processor.batch_decode(new_tokens, skip_special_tokens=True)[0])
```

### Task prompts

| Task | Prompt | Output |
|:--|:--|:--|
| Document | `Extract all information from the main body of the document image and represent it in markdown format, ignoring headers and footers. Tables should be expressed in OTSL format, formulas in the document should be represented using LATEX format, and the parsing should be organized according to the reading order.` | Markdown; tables as OTSL, formulas as LaTeX, in reading order |
| Text region | `Extract the text in the image.` | Plain text |
| Table region | `Parse the table in the image into OTSL.` | Table output in OTSL format |
| Formula region | `Identify the formula in the image and represent it using LATEX format.` | LaTeX |
| Key information extraction | `Extract key information in the image`, followed by your JSON schema | JSON object |

## Use Examples

The examples below cover whole-page parsing and one KIE case. Inputs and outputs are in [`example_pics/`](example_pics/); the two clips below are screen recordings of the model parsing each document.

### Document parsing

**Dense mathematical page** · `dense-equations.jpg` `dense-equations.gif`

![Dense mathematical page being parsed by Xiaomi-OCR-0](example_pics/dense-equations.gif)

<details>
<summary>Parsed output</summary>

```markdown
We then define the following variables: \(\mathbf{P}_i^j = \prod_{t=i}^j (\mathbf{I} - \beta_t \boldsymbol{k}_t \boldsymbol{k}_t^\top) \in \mathbb{R}^{d \times d}\), \(\mathbf{H}_i^j = \sum_{t=i}^j \beta_t (\boldsymbol{v}_t \boldsymbol{k}_t^\top) \mathbf{P}_{t+1}^j \in \mathbb{R}^{d \times d}\), where we let \(\mathbf{P}_i^j = \mathbf{I}\) whenever \(i > j\). Intuitively, \(\mathbf{P}_i^j\) is the "decay factor" to be applied to \(\mathbf{S}_i\) for obtaining \(\mathbf{S}_j\), and \(\mathbf{H}_i^j\) represents the contributions to \(\mathbf{S}_j\) starting from token \(i\). (Hence \(\mathbf{S}_t = \mathbf{H}_1^t\)). The chunkwise recurrence can then be written as,

\[\mathbf {S} _ {[ t ]} ^ {r} = \mathbf {S} _ {[ t ]} ^ {0} \mathbf {P} _ {[ t ]} ^ {r} + \mathbf {H} _ {[ t ]} ^ {r} \tag{5}\]

where we define the chunkwise variables \(\mathbf{S}_{[t]}^{i} = \mathbf{S}_{tC + i}\), \(\mathbf{P}_{[t]}^{r} = \mathbf{P}_{tC + 1}^{tC + r}\), \(\mathbf{H}_{[t]}^{r} = \mathbf{H}_{tC + 1}^{tC + r}\). Here we have \(\frac{L}{C}\) chunks of size \(C\). The trick is to now efficiently represent the \(\mathbf{P}_{[t]}^{r}, \mathbf{H}_{[t]}^{r} \in \mathbb{R}^{d \times d}\) matrices using a similar approach described in §3.1, so that these matrices can be stored in \(\mathcal{O}(d)\) memory,

\[\mathbf {P} _ {[ t ]} ^ {r} = \mathbf {I} - \sum_ {i = 1} ^ {r} \boldsymbol {w} _ {[ t ]} ^ {i} \boldsymbol {k} _ {[ t ]} ^ {i ^ {\top}}, \quad \mathbf {H} _ {[ t ]} ^ {r} = \sum_ {i = 1} ^ {r} \boldsymbol {u} _ {[ t ]} ^ {i} \boldsymbol {k} _ {[ t ]} ^ {i ^ {\top}} \quad \in \mathbb {R} ^ {d \times d} \tag{6}\]

\[\boldsymbol {w} _ {[ t ]} ^ {r} = \beta_ {[ t ]} ^ {r} \left(\boldsymbol {k} _ {[ t ]} ^ {r} - \sum_ {i = 1} ^ {r - 1} \boldsymbol {w} _ {[ t ]} ^ {i} (\boldsymbol {k} _ {[ t ]} ^ {i ^ {\top}} \boldsymbol {k} _ {[ t ]} ^ {r})\right), \quad \boldsymbol {u} _ {[ t ]} ^ {r} = \beta_ {[ t ]} ^ {r} \left(\boldsymbol {v} _ {[ t ]} ^ {r} - \sum_ {i = 1} ^ {r - 1} \boldsymbol {u} _ {[ t ]} ^ {i} (\boldsymbol {k} _ {[ t ]} ^ {i ^ {\top}} \boldsymbol {k} _ {[ t ]} ^ {r})\right) \quad \in \mathbb {R} ^ {d} \tag{7}\]

The derivations for the above can be found in the appendix. Subsequently, based on Eq. 5, we can obtain the chunk-level recurrence for hidden states and outputs as,

\[\mathbf {S} _ {[ t ]} ^ {r} = \mathbf {S} _ {[ t ]} ^ {0} - \left(\mathbf {S} _ {[ t ]} ^ {0} \sum_ {i = 1} ^ {r} \boldsymbol {w} _ {[ t ]} ^ {i} \boldsymbol {k} _ {[ t ]} ^ {i ^ {\top}}\right) + \sum_ {i = 1} ^ {r} \boldsymbol {u} _ {[ t ]} ^ {i} \boldsymbol {k} _ {[ t ]} ^ {i ^ {\top}} = \mathbf {S} _ {[ t ]} ^ {0} + \sum_ {i = 1} ^ {r} \left(\boldsymbol {u} _ {[ t ]} ^ {i} - \mathbf {S} _ {[ t ]} ^ {0} \boldsymbol {w} _ {[ t ]} ^ {i}\right) \boldsymbol {k} _ {[ t ]} ^ {i ^ {\top}},\]

\[\boldsymbol {o} _ {[ t ]} ^ {r} = \mathbf {S} _ {[ t ]} ^ {r} \boldsymbol {q} _ {[ t ]} ^ {r} = \mathbf {S} _ {[ t ]} ^ {0} \boldsymbol {q} _ {[ t ]} ^ {r} + \sum_ {i = 1} ^ {r} \left(\boldsymbol {u} _ {[ t ]} ^ {i} - \mathbf {S} _ {[ t ]} ^ {0} \boldsymbol {w} _ {[ t ]} ^ {i}\right) \left(\boldsymbol {k} _ {[ t ]} ^ {i ^ {\top}} \boldsymbol {q} _ {[ t ]} ^ {i}\right).\]

Letting \(\mathbf{S}_{[t]} = \mathbf{S}_{[t]}^{0}\), the above can be simplified to matrix notations similarly to Eq.1-2,

\[\mathbf {S} _ {[ t + 1 ]} = \mathbf {S} _ {[ t ]} + \left(\mathbf {U} _ {[ t ]} - \mathbf {W} _ {[ t ]} \mathbf {S} _ {[ t ]} ^ {\top}\right) ^ {\top} \mathbf {K} _ {[ t ]}, \tag{8}\]

\[\mathbf {O} _ {[ t ]} = \mathbf {Q} _ {[ t ]} \mathbf {S} _ {[ t ]} ^ {\top} + (\mathbf {Q} _ {[ t ]} \mathbf {K} _ {[ t ]} ^ {\top} \odot \mathbf {M}) \left(\mathbf {U} _ {[ t ]} - \mathbf {W} _ {[ t ]} \mathbf {S} _ {[ t ]} ^ {\top}\right) \tag{9}\]

where \(\square_{[t]} = \square_{[t]}^{1:C} \in \mathbb{R}^{C \times d}\) for \(\square \in \{\mathbf{Q}, \mathbf{K}, \mathbf{V}, \mathbf{O}, \mathbf{U}, \mathbf{W}\}\) defines the chunkwise matrices that are formed from stacking the \(q_t, k_t, v_t, o_t, u_t, w_t\) vectors.

Practical considerations. In the above, Eq. 7 is fully recurrent and thus cannot use tensor cores written as is. To solve this, we further leverage the UT transform [44, 23] (see §B.2 for derivations):

\[\mathbf {T} _ {[ t ]} = \left(\mathbf {I} + \operatorname{tril} (\operatorname{diag} (\beta_ {[ t ]}) \mathbf {K} _ {[ t ]} \mathbf {K} _ {[ t ]} ^ {\top}, - 1)\right) ^ {- 1} \operatorname{diag} \left(\beta_ {[ t ]}\right) \tag{10}\]

\[\mathbf {W} _ {[ t ]} = \mathbf {T} _ {[ t ]} \mathbf {K} _ {[ t ]}, \quad \mathbf {U} _ {[ t ]} = \mathbf {T} _ {[ t ]} \mathbf {V} _ {[ t ]} \tag{11}
```

</details>

**Handwritten derivation** · `handwrite-formula.jpg` `handwrite-formula.gif`

![Handwritten formula derivation being parsed by Xiaomi-OCR-0](example_pics/handwrite-formula.gif)

<details>
<summary>Parsed output</summary>

```markdown
(b) we get Friedmann equation:

\[
\left(\frac{\dot{a}}{a}\right)^{2} = \frac{8\pi G}{3c^{2}}\rho - \frac{kc^{2}}{a^{2}}
\]

and Raychaudhuri equation:

\[
2\frac{\ddot{a}}{a} + \left(\frac{\dot{a}}{a}\right)^{2} + \frac{kc^{2}}{a^{2}} = -\frac{8\pi G P}{c^{2}}
\]

Substituting the Friedmann equation and \(P = w\rho\) into the Raychaudhuri equation:

\[
2\frac{\ddot{a}}{a} + \frac{8\pi G}{3c^{2}}\rho - \frac{kc^{2}}{a^{2}} + \frac{kc^{2}}{a^{2}} = -\frac{8\pi G}{c^{2}}\rho
\]

\[
\frac{\ddot{a}}{a} + \frac{4\pi G}{3c^{2}}\rho = -\frac{4\pi G}{c^{2}}\rho
\]

\[
\frac{\ddot{a}}{a} = -\frac{4\pi G}{3c^{2}}(\rho + 3P) = -\frac{4\pi G}{3c^{2}}(1 + 3w)\rho
\]

Differentiating the Friedmann equation with respect to time; We get:

\[
\begin{array}{r l}
{\left[\left(\frac{\dot{a}}{a}\right)^{2}\right]^{\prime}} & = 2\left(\frac{\dot{a}}{a}\right)\left(\frac{\dot{a}}{a}\right)^{\prime} \\
& = 2\frac{\dot{a}}{a}\left(\frac{\ddot{a}}{a} + \left(-\frac{\dot{a}}{a^{2}}\right)\dot{a}\right) \\
& = \frac{2\dot{a}\ddot{a}}{a^{2}} + (-2)\frac{\dot{a}^{3}}{a^{3}}
\end{array}
\]

\[
\left[\left(\frac{\dot{a}}{a}\right)^{2}\right]^{\prime} = \frac{8\pi G}{3c^{2}}\dot{\rho} - kc^{2}\left(\frac{1}{a^{2}}\right)^{\prime}
\]

\[
\frac{2\dot{a}\ddot{a}}{a^{2}} + \frac{\dot{a}^{3}}{a^{3}}(-2) = \frac{8\pi G}{3c^{2}}\dot{\rho} + \frac{2kc^{2}}{a^{3}}\dot{a}
\]

\[
\frac{\dot{a}\ddot{a}}{a^{2}} - \frac{\dot{a}^{3}}{a^{3}} = \frac{4\pi G}{3c^{2}}\dot{\rho} + \frac{kc^{2}}{a^{3}}\dot{a}
\]

substituting \(\frac{\ddot{a}}{a} = -\frac{4\pi G}{3c^{2}}(1 + 3w)\rho\)

\[
\frac{\dot{a}}{a}\left(-\frac{4\pi G}{3c^{2}}\right)(1 + 3w)\rho = \frac{4\pi G}{3c^{2}}\dot{\rho} + \frac{\dot{a}}{a}\left(\frac{kc^{2}}{a^{2}} + \frac{\dot{a}^{2}}{a^{2}}\right)
\]

and Friedmann equation into it :

\[
\frac{\dot{a}}{a}\left(-\frac{4\pi G}{3c^{2}}\right)(1 + 3w)\rho = \frac{4\pi G}{3c^{2}}\dot{\rho} + \frac{\dot{a}}{a}\cdot\frac{4\pi G}{3c^{2}}\cdot 2\cdot\rho
\]

\[
\begin{array}{l}
(-1)\dot{a}(1 + 3w)\rho = a\dot{\rho} + 2\rho\dot{a} \\
-(3 + 3w)\rho\dot{a} = a\dot{\rho}
\end{array}
\]

\[
\therefore \quad \frac{\dot{\rho}}{\rho} = -3(1 + w)\frac{\dot{a}}{a}.
\]
```

</details>

**Running-script Thousand Character Classic** · `qianziwen.jpeg`

<img src="example_pics/qianziwen.jpeg" width="160" alt="Running-script Thousand Character Classic">

```text
行书千文

梁貟外散騎侍郎周興嗣次韻

天地玄黄宇宙洪荒日月
```

### Key information extraction

**Receipt** · `receipt.jpg`

<img src="example_pics/receipt.jpg" width="200" alt="Receipt">

```text
Extract key information in the image

Please output the key information in JSON format according to the following schema:
{
    "date": "",
    "seller_address": "",
    "seller_gst_id": "",
    "seller_name": "",
    "total_amount": "",
    "total_tax": ""
}
```

```json
{
  "date": "2017-10-18",
  "seller_address": "LOT 1851-A & 1851-B, JALAN KPB 6, KAWASAN PERINDUSTRIAN BALAKONG, 43300 SERI KEMBANGAN, SELANGOR",
  "seller_gst_id": "001092886528",
  "seller_name": "MR. D.I.Y. SDN BHD",
  "total_amount": "5.90",
  "total_tax": "0.33"
}
```

### More code

Batch processing, two-stage parsing (PP-DocLayoutV3 → region recognition → page assembly), the Agent Skill, and the evaluation and post-processing code are all in the [GitHub repository](https://github.com/SeerRay-Lab/Xiaomi-OCR-0).

## Acknowledgments

Xiaomi-OCR-0 builds on the open OCR and multimodal LLM community. We thank everyone in the community for their tireless effort and outstanding contributions along the way, and especially the authors of **Qwen3.5**, **PaddleOCR-VL-1.6**, **MinerU2.5-Pro**, **GLM-OCR**, **dots.mocr**, **HunyuanOCR-1.5**, **TeleOCR**, **OvisOCR2**, **Qianfan-OCR**, and **PP-DocLayoutV3** for the inspiration and contributions that shaped Xiaomi-OCR-0.

## Citation and License

- **License:** Apache-2.0.
- **Paper:** [Xiaomi-OCR-0 Technical Report](https://arxiv.org/abs/2609.36136) (arXiv:2609.36136)

```bibtex
@misc{chen2026xiaomiocr0,
  title        = {Xiaomi-OCR-0 Technical Report},
  author       = {Chen, Xin and Du, Anan and Feng, Feng and Fu, Pei and Luan, Jian and
                  Xu, Longwei and Zhang, Shaojie and Li, Hang and Qu, Heng and Tan, Cheng},
  year         = {2026},
  eprint       = {2609.36136},
  archivePrefix= {arXiv},
  primaryClass = {cs.CV},
  url          = {https://arxiv.org/abs/2609.36136}
}
```

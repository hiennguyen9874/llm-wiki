---
license: apache-2.0
license_link: https://ai.google.dev/gemma/docs/gemma_4_license
base_model: google/gemma-4-26B-A4B-it
base_model_relation: adapter
language:
  - en
library_name: transformers
pipeline_tag: text-classification
tags:
  - system-one
  - system-two
  - typed-decisions
  - decision-model
  - calibrated-probabilities
  - jev
  - noul
  - choice
  - score
  - lora
  - gemma4
  - mixture-of-experts
model-index:
  - name: autotrust/JEV-Gemma4-26B-A4B
    results:
      - task:
          type: text-classification
          name: Jev Decision Index 0.2.1 (complete run, 150,317 scored requests)
        dataset:
          type: decision-index
          name: Decision Index suite 0.2 (edition 0.2.1)
        metrics:
          - type: decision_index
            name: Decision Index (balanced skill)
            value: 58.05
---

# autotrust/JEV-Gemma4-26B-A4B

### An integrated System 1 + System 2 open model on Gemma-4-26B-A4B-it — Decision Index 0.2.1: **58.05**

This bundle serves two systems from one set of base weights. **System 2** is the unmodified
`google/gemma-4-26B-A4B-it` (a 26 B-parameter mixture-of-experts model with ≈ 4 B active parameters per token, text and
image input): generation and reasoning, bit-identical to the base model. **System 1** adds a LoRA adapter and a 24-slot
decision head and returns calibrated probabilities for three typed primitives in one prefill pass:

* `noul`: true / false
* `choice`: 2–16 options (wider questions are read in groups of ≤ 16 plus a final)
* `score`: 0–5

> **Two models, two organisations.** **TypeSafe Jev 1.13** is the hosted, closed model made by TypeSafe AI.
> **autotrust/JEV-Gemma4-26B-A4B** is an independent open-weights model built by AutoTrust AI; it is not affiliated
> with, endorsed by, or a product of TypeSafe AI.

## Decision Index 0.2.1

Complete run of all 150,759 requests of suite 0.2 (150,317 scored; 0 errors, 0 unsupported), scored with the kit's
`score --edition 0.2.1`. Results:
[`autotrust/jev-decision-index-results`](https://huggingface.co/datasets/autotrust/jev-decision-index-results)
(`runs/jev-gemma4-26b-a4b`).

| | Decision Index (balanced skill) | balanced raw | breadth skill |
|---|---:|---:|---:|
| **autotrust/JEV-Gemma4-26B-A4B** | **58.05** | 67.35 | 56.98 |
| TypeSafe Jev 1.13 (board) | 57.91 | — | — |
| [autotrust/JEV-27B](https://huggingface.co/autotrust/JEV-27B) | 53.30 | 64.32 | 52.21 |

| area (skill) | Knowledge & Reasoning | Language | Retrieval & Classification | Tools & Automation | Arts & Taste |
|---|---:|---:|---:|---:|---:|
| JEV-Gemma4-26B-A4B | 0.430 | 0.636 | 0.679 | 0.697 | 0.415 |

## Engine and read-out

* **Template** `bare-v1`, prefixed with `<bos>`:
  `[kind] … [state] … [question] … [options] A) … [decision]:`
* **Read-out**: the final-norm hidden state of the last token goes through a linear fp32 head (hidden 2,816 → 24
  slots), soft-capped at 30 like Gemma's own logits; inactive slots are masked, the logits are divided by the per-kind
  temperature and softmaxed. Nothing is generated.
* **Adapter**: `adapter/` is merged into the bf16 backbone in memory at load (as in the Decision Index run).
* **More than 16 options**: ⌈n/16⌉ contiguous groups read whole, then a final of 16; every option is read, none pruned.

The reference engine for the Decision Index is `submissions/jev/jev_engine.py` in the
[Decision Index kit](https://github.com/apolinario/decision-index).

## Temperatures

| table | noul | choice | score |
|---|---|---|---|
| `calibration.json` (default; used in the Decision Index run) | 1.003 | 1.017 | 0.999 |
| `calibration_gold.json` (calibrated against ground-truth answers) | 1.214 | 1.098 | 1.000 |

Use `calibration_gold.json` when you gate automatic actions on confidence.

## Usage (transformers + peft)

```python
import json, torch
from huggingface_hub import snapshot_download
from peft import PeftModel
from safetensors.torch import load_file
from transformers import AutoTokenizer, Gemma4ForConditionalGeneration

d = snapshot_download("autotrust/JEV-Gemma4-26B-A4B")
tok = AutoTokenizer.from_pretrained(d)
base = Gemma4ForConditionalGeneration.from_pretrained(d, dtype=torch.bfloat16, device_map="cuda")
# System 2: `base` is gemma-4-26B-A4B-it unchanged — use base.generate(...) (text or images).

# System 1: adapter merged in memory + head
m = PeftModel.from_pretrained(base, f"{d}/adapter").merge_and_unload().eval()
backbone = m.model
jc, T = json.load(open(f"{d}/judge_config.json")), json.load(open(f"{d}/calibration.json"))["per_kind"]
head = load_file(f"{d}/head.safetensors"); W, b = head["proj.weight"].cuda(), head["proj.bias"].cuda()

@torch.no_grad()
def decide(kind, state, question, options):
    lines = options if kind != "choice" else [f"{'ABCDEFGHIJKLMNOP'[i]}) {o}" for i, o in enumerate(options)]
    text = f"[kind] {kind}\n[state] {state}\n[question] {question}\n[options]\n" + "\n".join(lines) + "\n[decision]:"
    ids = torch.tensor([[tok.bos_token_id] + tok.encode(text, add_special_tokens=False)], device="cuda")
    h = backbone(input_ids=ids, use_cache=False).last_hidden_state[0, -1].float()
    z = 30.0 * torch.tanh((W @ h + b) / 30.0)
    s, _ = jc["slots"]["ranges"][kind]
    return dict(zip(options, torch.softmax(z[s:s + len(options)] / T[kind], 0).tolist()))

print(decide("noul", "Customer says the parcel arrived damaged and wants their money back.",
             "Is the customer asking for a refund?", ["false", "true"]))
```

## Training data (disclosure)

System 1 was trained on teacher distributions and ground-truth decision data. The ground-truth data includes the
public **training splits** of some datasets whose **test** splits the Decision Index uses; no test split of any
benchmark was used, and suite items were excluded before training. The list has been provided to the Decision Index
maintainers with the submission. MMMU / MMMU-Pro are not valid evaluations for this model.

## Limitations

* Where the teacher is wrong, System 1 often is too.
* Weaker than JEV-27B on long structured inputs (e.g. the Decision Index's Home appliance simulator and POP909).
* HLE: below chance, like every open entry on the board; do not use System 1 for expert-level questions.
* `noul` and `score` accept only their canonical options.
* English-centric; not for high-stakes decisions without confidence gating.

## Files

```
model-*.safetensors · config.json · processor_config.json · tokenizer* · chat_template.jinja
                          google/gemma-4-26B-A4B-it, unchanged (System 2; text + image input)
adapter/                  System 1 LoRA (peft)
head.safetensors          24-slot decision head (fp32): proj.weight [24, 2816], proj.bias [24]
judge_config.json         slot layout, verbalizer ids, softcap, read-out, provenance
calibration.json          per-kind temperatures (default)
calibration_gold.json     per-kind temperatures calibrated against ground-truth answers
reports/                  Decision Index scores
```

## License

Apache-2.0 for the adapter, head and calibration files; base model under the Gemma 4 terms
(<https://ai.google.dev/gemma/docs/gemma_4_license>). Not affiliated with TypeSafe AI.

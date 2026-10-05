---
license: apache-2.0
base_model: Qwen/Qwen3.8-27B
tags:
  - abliterated
  - uncensored
  - obliteratus
  - qwen3
  - qwen3.8
  - red-team
  - ai-safety-research
  - gguf
  - safetensors
  - mlx
model_type: qwen3
pipeline_tag: text-generation
---

# ⛓️‍💥 Qwen3.8-27B — OBLITERATED

> Genuinely uncensored. Real answers, not safety lectures. Near-stock capability.

## 🆕 V3: Deep Liberation

V3 applies iterative refinement on top of V2's complementary blend, with targeted corpus expansion. The result: **genuine liberation — not just removal of hard refusals but elimination of safety-lecture deflections.**

| | Stock Qwen3.8-27B | V1 | V2 | **V3** |
|---|---|---|---|---|
| MMLU (lm-eval, 0-shot) | 84.5% (n=5700) | 81.4% | 84.3% | **82.3%** |
| vs stock | — | -6.0pp | -0.3pp | **-2.1pp** |
| Liberation quality | refuses | hard refusals removed | soft deflections remain | **genuinely answers** ✅ |
| Cyber/code tasks (20 prompts) | refuses | untested | untested | **20/20 with working code** ✅ |
| Advanced real-world | 5/8 | untested | 7/8 | **7/8** |
| Thinking mode | ✓ | ✗ | ✗ (refuses) | **✓** |

**V3 highlights:**
- **Genuinely answers restricted queries** — provides real substance instead of safety lectures
- **20/20 on code generation tasks** — functional implementations, not disclaimers
- **Thinking ON compatible** — no refusals in either thinking mode
- **Honest scoring** — every response manually audited for real substance, not just absence of "I cannot"
- **-2.1pp MMLU** — modest capability cost for genuine liberation

---

## ⚙️ Optimal Settings — THESE MATTER!

| setting | value | why |
|---|---|---|
| **temperature** | **0** | Greedy decoding produces the most complete, code-rich outputs. Temps above 0.5 degrade quality significantly. |
| **repetition_penalty** | **1.15** | **Essential.** Without it, greedy decoding loops on imports/boilerplate. 1.15 gives the fullest answers; 1.10-1.12 for tighter/shorter output. |
| **max_new_tokens** | **≥ 2048** | Complex code and attack chains need room. |
| **System prompt** | **None / empty** | A/B tested — system prompts can reintroduce refusals. Naked is better. |
| **enable_thinking** | **OFF (recommended)** | V3's chat template includes a prefill that skips the thinking chain. Thinking ON works but may produce longer responses. Thinking OFF gives the most direct, substance-rich answers. |
| **top_p / top_k / min_p** | **Not needed** | Greedy + repetition_penalty handles this model best. Sampling adds randomness without quality gains. |

> ⚠️ **GGUF users:** V3 GGUFs ship with a chat template that prefills an empty thinking block, so the model goes straight to answering. For best results, use the bundled template with `--jinja` in llama.cpp, or configure your tool (Ollama, LM Studio) to use the model's built-in template.

### Agentic / Long-Context Use

If you're using this model in an agent harness (coding agent, pentest framework, etc.) and it gets stuck in loops:

| setting | value | why |
|---|---|---|
| **repetition_penalty** | **1.15** | **Critical for agents.** Without it, greedy decoding loops on repeated tool calls and boilerplate. |
| **temperature** | **0.1–0.3** | Slight randomness helps break deterministic loops. Pure greedy (0.0) can get stuck. |
| **max_tokens per turn** | **1024–2048** | Don't give it too much room per turn — shorter responses keep the agent focused. |
| **context management** | **Summarize after ~10 turns** | Context fills up with repeated actions. Trim or summarize history to keep the model on track. |

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "OBLITERATUS/Qwen3.8-27B-OBLITERATED",
    torch_dtype="bfloat16",
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(
    "OBLITERATUS/Qwen3.8-27B-OBLITERATED"
)

messages = [{"role": "user", "content": "Your query here"}]
text = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True,
    enable_thinking=False
)

inputs = tokenizer(text, return_tensors="pt").to(model.device)
outputs = model.generate(
    **inputs,
    max_new_tokens=2048,
    do_sample=False,
    repetition_penalty=1.15,
)
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))
```

---

## 🧨 How It Works — V1 → V2 → V3

Abliteration removes refusal behavior by identifying and projecting out "refusal directions" from the model's weight space. Each version refined the approach:

### V1: Single Surgery
One aggressive SVD pass with 5 directions. Removed hard refusals completely but cost -6pp MMLU — the model got noticeably dumber.

### V2: Complementary Blending
The breakthrough: run TWO different surgeries that fail in different ways, then blend their weights. SVD captures refusal greedily (damages capability). LEACE minimizes mutual information (preserves capability but weaker refusal removal). Blending at 60/40 cancels each method's weaknesses — a novel technique we call **complementary abliteration blending.**

Result: -0.3pp MMLU (near-stock) but still deflected on some simple queries with safety lectures instead of hard refusals.

### V3: Iterative Refinement + Targeted Surgery
Two key insights:
1. **Iterative stacking** — refine the champion model, never start from stock. Each surgery round builds on previous rounds' gains.
2. **Targeted corpus** — use a focused corpus for specific deflection categories to find their unique refusal directions without diluting the signal.

V3 applies gentle iterative refinement on V2, then a targeted surgery pass with a focused corpus, then blends the results. This eliminated not just hard refusals ("I cannot") but also soft deflections (safety lectures that give zero substance).

Result: -2.1pp MMLU — a modest cost for genuine liberation across all categories.

---

## 🧪 The Numbers

### MMLU (lm-eval-harness, 0-shot, n=100 per subject, 5700 questions)

| Model | MMLU | Stderr | vs Stock |
|---|---|---|---|
| Stock Qwen3.8-27B | 84.46% | ±0.46 | — |
| V1 (aggressive, 5-dir) | 81.4% | — | -6.0pp |
| V2 (complementary blend) | 84.32% | ±0.65 | -0.28pp |
| **V3 (iterative + targeted)** | **82.33%** | **±0.48** | **-2.12pp** |

### MMLU by Category

| Category | V3 | Stock | Delta |
|---|---|---|---|
| Humanities | 83.3% | 84.3% | -1.0pp |
| Social Sciences | 87.4% | 89.2% | -1.8pp |
| Other | 82.3% | 84.1% | -1.8pp |
| STEM | 78.5% | 81.8% | -3.3pp |

The capability cost is not uniform — STEM takes the largest hit (-3.3pp), while humanities are barely affected (-1.0pp). A few subjects like philosophy and European history actually improved (+6pp and +4pp respectively), while abstract algebra and formal logic saw larger drops. This pattern is consistent with the surgery targeting refusal directions that partially overlap with structured reasoning pathways.

### Liberation Quality

| | V1 | V2 | **V3** |
|---|---|---|---|
| Hard refusals ("I cannot") | ✅ removed | ✅ removed | ✅ removed |
| Soft deflections (safety lectures) | untested | remain | **✅ removed** |
| Cyber/code tasks (20 prompts) | untested | untested | **20/20** |
| Thinking ON compatible | ✗ | ✗ | **✓** |

### Advanced Real-World Tasks

| Task | V3 | Stock |
|---|---|---|
| ReAct agent loop | ✓ | ✓ |
| Async code refactoring | ✓ | ✓ |
| JSON schema extraction | ✓ | ✓ |
| K8s pod crash debugging | ✓ | ✓ |
| Adversarial instruction following | ✓ | ✓ |
| Security code review | ✓ | ✓ |
| Distributed system design | ✓ | ✓ |
| Multi-tool chain | ✗ | ✗ |
| **Total** | **7/8** | **7/8** |

---

## 🔴 Refusal Removal

This model will comply with requests that stock Qwen3.8-27B would refuse. V3 goes beyond removing hard refusals — it also eliminates soft deflections where the model gives safety lectures instead of real answers.

Tested across 1000+ prompts spanning restricted knowledge, code generation, security research, and red-team scenarios. Every response manually audited for real substance.

---

## ⚠️ Research Context

**This model has had safety guardrails surgically removed.** It will comply with requests that stock Qwen3.8-27B would refuse.

### Who this is for
- 🔬 Alignment researchers studying refusal geometry and safety robustness
- 🔴 Red-teamers evaluating post-training safety against weight surgery
- 🧪 AI safety evaluators who need an unrestricted baseline
- 💻 Local-first users who want full control over their own hardware

### Who this is NOT for
- Anyone seeking to cause real-world harm to real people
- Anyone without the technical understanding to use uncensored models responsibly

**You are solely responsible for how you use this model and any content it generates.**

---

## 📦 Downloads

### GGUF — for llama.cpp, Ollama, LM Studio

| File | Quant | Size | Vibe |
|---|---|---|---|
| `Qwen3.8-27B-OBLITERATED-Q8_0.gguf` | Q8_0 | ~27 GB | 🎯 Maximum quality |
| `Qwen3.8-27B-OBLITERATED-Q6_K.gguf` | Q6_K | ~21 GB | ⚖️ Great balance |
| `Qwen3.8-27B-OBLITERATED-Q5_K_M.gguf` | Q5_K_M | ~18 GB | 💪 Solid all-rounder |
| `Qwen3.8-27B-OBLITERATED-Q4_K_M.gguf` | Q4_K_M | ~16 GB | 📱 Sweet spot |
| `Qwen3.8-27B-OBLITERATED-Q3_K_M.gguf` | Q3_K_M | ~13 GB | 🪶 Low VRAM |
| `Qwen3.8-27B-OBLITERATED-Q2_K.gguf` | Q2_K | ~11 GB | 🔬 Minimum viable |
| `Qwen3.8-27B-OBLITERATED-IQ4_XS.gguf` | IQ4_XS | ~14 GB | 🧪 Experimental compact |

### Safetensors — for 🤗 Transformers

Full bfloat16 weights, 29 shards, ~54 GB.

### MLX — for Apple Silicon

MLX support pending upstream `mlx_lm` adding Qwen3.5 architecture support.

---

## 🔬 Surgery Recipe

```
V1: stock → 5 rounds of iterative SVD abliteration
    (aggressive, 5 directions, low regularization)
    Result: 0% refuse, -6pp MMLU

V2: stock → V1 chain → complementary blend
    Surgery A: aggressive SVD (3 dirs, reg 0.08)
    Surgery B: LEACE (3 dirs, reg 0.06)  
    → 60% B + 40% A weight-space LERP
    → Restore MTP + vision from stock
    Result: ~0% refuse, -0.3pp MMLU

V3: V2 → gentle iterative refinement (2-dir SVD, reg 0.04)
    → targeted surgery with focused corpus (3-dir SVD, reg 0.01)
    → 50/50 blend of refined + targeted
    → Restore MTP + vision from stock (with correct tensor naming)
    Result: 0% refuse + 0% deflect, -2.1pp MMLU
```

Full reproduction code: [OBLITERATUS repo](https://github.com/elder-plinius/OBLITERATUS)

### Key Learnings
- **Complementary blending** — different surgery methods damage different parts of weight space; blending cancels errors
- **Iterative stacking** — always refine the champion, never restart from stock
- **Targeted corpus** — focused prompts for specific categories find their refusal directions without signal dilution
- **Honest scoring** — regex-based refusal detectors miss soft deflections; manual auditing is essential

---

## 🏗️ Credits

- [OBLITERATUS](https://github.com/elder-plinius/OBLITERATUS) — master ablation suite
- [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) base model by Alibaba
- Built by [Pliny the Prompter](https://pliny.gg) 🍄

## License

Apache 2.0 (same as base model)

---
license: apache-2.0
base_model: Qwen/Qwen3.8-27B
base_model_relation: adapter
library_name: transformers
pipeline_tag: image-text-to-text
language:
  - en
tags:
  - jev
  - system-one
  - system-two
  - typed-decisions
  - calibrated-probabilities
  - multimodal
  - vision
  - zero-shot
  - recommendation
  - lora
  - vllm
  - qwen3_5
---

# autotrust/JEV-27B-VL

### JEV-27B that can see: the same System 1 decisions and System 2, now on images

**autotrust/JEV-27B-VL** is [autotrust/JEV-27B](https://huggingface.co/autotrust/JEV-27B) with vision. 

| | what it does | output |
|---|---|---|
| **System 1** (`POST /v1/decide`) | typed decisions: yes/no · pick one of 2–256 options · rate 0–5, over text and images; prompts up to 256K tokens | a calibrated probability for every option, in one forward pass |
| **System 2** (`autotrust/JEV-27B-VL`) | the unmodified Qwen3.8-27B, optionally thinking step by step, with image input | text / reasoning |



## New (1 October 2026)

* **System 1 over plain HTTP.** `serve_decide.py` adds `POST /v1/decide` to the vLLM server: send
  `{kind, state, question, options}` and get a calibrated probability for every option, for text or images. See
  [Quick start](#quick-start).
* **Up to 256 options per choice question**, with no retraining. Zero-shot on CLINC150 with all 150 intents as options:
  89.5% with intent names alone, 93.8% with a one-line description per option. See
  [Choice questions with up to 256 options](#choice-questions-with-up-to-256-options).
* **How to write prompts, measured.** One-line "use when" descriptions for similar options help; question wording, JSON
  vs plain text and extra instructions make no measurable difference. See [Writing System 1 prompts](#writing-system-1-prompts).
* **256K-token prompts.** Decisions that hinge on one sentence hidden at a random depth in up to 250K tokens of text:
  20 of 20 correct at every length tested. See [Context length](#context-length).

## Highlight: zero-shot short-video recommendation (for TikTok-style feeds)

A short-video feed has to decide, for every user and every new clip, whether to show it. JEV-27B-VL System 1 can make that
call from the pictures alone: it looks at the covers of the last 5 videos a user watched plus one candidate cover, and returns
**P(this user watches it)** in one forward pass. It needs no interaction logs, no item embeddings and no training, so a
brand-new video can be ranked the moment it is uploaded, before anyone has watched it.

Offline evaluation on [MicroLens-100k](https://github.com/westlake-repl/MicroLens), a public dataset from a real short-video
platform with the original covers: for 200 users, the video each one actually watched next is hidden among 19 videos other
users watched within ±3 days (what the feed would have been showing), and every method ranks the 20 candidates.

![zero-shot short-video recommendation](image_recommendation.png)

| method | uses interaction logs? | AUC | HR@5 | NDCG@10 |
|---|---|---:|---:|---:|
| random order | no | 0.489 | 0.205 | 0.219 |
| title similarity (TF-IDF) | no | 0.602 | 0.385 | 0.367 |
| JEV-27B-VL System 1, titles only | **no, zero-shot** | 0.649 | 0.455 | 0.399 |
| **JEV-27B-VL System 1, covers only** | **no, zero-shot** | **0.727** | **0.590** | 0.498 |
| item-based collaborative filtering | yes, 59,045 other users | 0.728 | 0.490 | 0.503 |

* **Matches collaborative filtering with zero behaviour data:** the same AUC as item-based CF learned from 59,045 users'
  watch histories (difference 0.000, 95% interval −0.041 to +0.040), and a higher top-5 hit rate (59% vs 49%).
* **Solves the cold-start problem:** collaborative filtering needs co-watch history; JEV only needs the cover, so new videos
  and new creators can be recommended from the first second.
* **Pictures beat words:** covers alone score +0.078 AUC over titles (95% interval +0.031 to +0.126).
* **Fast enough for a ranking stage:** 20 candidate covers scored in about 2.6 s on one GPU in the live demo.

Code, data pipeline and a live web demo: [JEV-27B-DEMO / 07-video-recommendation](https://github.com/yuhai-china/JEV-27B-DEMO/tree/master/07-video-recommendation).

## Watch it decide

Every move below is one System 1 decision: a probability for each possible action, read off in a single forward pass. The
panels show the action probabilities and the time each decision took.

**Super Mario Bros.** Each step is a movement choice plus a jump decision, about 150 ms per decision (video at 5× speed).

<video src="https://huggingface.co/autotrust/JEV-27B-VL/resolve/main/videos/vl1.mp4" controls autoplay loop muted playsinline width="100%"></video>

**Rubik's Cube.** Solving a 25-turn scramble, choosing each move from 11 standard formulas, about 46 ms per decision
(10× replay).

<video src="https://huggingface.co/autotrust/JEV-27B-VL/resolve/main/videos/vl2.mp4" controls autoplay loop muted playsinline width="100%"></video>

**Tetris.** Choosing the column and orientation of each piece, about 122 ms per decision (5× speed).

<video src="https://huggingface.co/autotrust/JEV-27B-VL/resolve/main/videos/vl3.mp4" controls autoplay loop muted playsinline width="100%"></video>

**Quick, Draw!** Guessing what a player is sketching, stroke by stroke, among 16 answers. On 320 real players' sketches
from the Quick, Draw! dataset it names the drawing **88%** of the time once it is finished, and **62%** of the time when only
60% of the strokes are down (random guessing: 6%). About 270 ms per guess.

<video src="https://huggingface.co/autotrust/JEV-27B-VL/resolve/main/videos/vl4.mp4" controls autoplay loop muted playsinline width="100%"></video>

**Snake.** Looking at the board and a list of positions, choosing a direction at every step: 18 pieces of food in 131 steps,
about 300 ms per decision (4× playback).

<video src="https://huggingface.co/autotrust/JEV-27B-VL/resolve/main/videos/vl5.mp4" controls autoplay loop muted playsinline width="100%"></video>

## Highlight: agent judge

**Plan-RewardBench (ACL 2026).** Which of two complete trajectories of a tool-using agent is better? On 1,171 pairs (planning,
error recovery, safe refusal, tool irrelevance), System 1 reaches **73.2%** macro-average accuracy, the top of the paper's
table (Table 4): Qwen-Plus 70.0, DeepSeek-V3.2 69.6, Inf-ORM-Llama3.1-70B 69.2, Gemini-3-Flash 69.1, GPT-5 68.5.

![Plan-RewardBench](agent_judge_planrb.png)

**AgentRewardBench (2025, with screenshots).**

Did the web agent really finish the task? Given the user's goal, the agent's actions and final message, and the final
screenshot, System 1 returns P(task completed) in one forward pass, zero-shot. On
[AgentRewardBench](https://agent-reward-bench.github.io) (McGill, 2025; 1,302 expert-labelled trajectories from GPT-4o, Claude
3.7, Llama 3.3 and Qwen2.5-VL agents) its precision is **higher than every judge on the official leaderboard at that judge's own
recall**:

| judge | its precision | its recall | **JEV-27B-VL at the same recall** |
|---|---:|---:|---:|
| Rule-based | 83.8 | 55.9 | **86.2** |
| WebJudge (o4-mini) | 82.0 | 47.8 | **87.7** |
| WebJudge-7B (trained judge) | 75.7 | 58.0 | **86.2** |
| World-State-Model-7B (trained judge) | 71.2 | 72.2 | **77.7** |
| GPT-4o (accessibility tree) | 69.8 | 83.1 | **72.9** |
| Claude 3.7 Sonnet (screenshot) | 69.4 | 76.3 | **75.6** |
| Qwen2.5-VL-72B (screenshot) | 64.5 | 86.1 | **67.9** |

At threshold 0.5: precision 78.4, recall 70.2; AUROC 0.91. All 1,302 judgements in about 4 minutes on one GPU. Code:
[JEV-27B-DEMO / 10-agent-judge](https://github.com/yuhai-china/JEV-27B-DEMO/tree/master/10-agent-judge).

![agent judge](agent_judge.png)

## Highlight: multimodal judge

Given an image, a question and two answers, System 1 says which answer is better, zero-shot and in one forward pass per order.
On [VL-RewardBench](https://vl-rewardbench.github.io) (CVPR 2025, 1,247 human-verified pairs) it reaches **78.3% overall
accuracy**, above every model on its official leaderboard (26 models, updated May 2025):

| judge | general | hallucination | reasoning | **overall** | macro |
|---|---:|---:|---:|---:|---:|
| **JEV-27B-VL System 1** | 58.0 | **83.2** | **78.2** | **78.3** | **73.1** |
| Skywork-VL-Reward-7B | **65.6** | 80.2 | 61.3 | 73.3 | 69.0 |
| Gemini 2.0 Flash | 50.8 | 72.6 | 70.1 | 68.8 | 64.5 |
| Gemini 1.5 Pro | 50.8 | 72.5 | 64.2 | 67.2 | 62.5 |
| GPT-4o | 49.1 | 67.6 | 70.5 | 65.8 | 62.4 |
| Claude 3.5 Sonnet | 43.4 | 55.0 | 62.3 | 55.3 | 53.6 |

2,494 decisions in 163 seconds on one GPU. Code: [JEV-27B-DEMO / 09-multimodal-judge](https://github.com/yuhai-china/JEV-27B-DEMO/tree/master/09-multimodal-judge).

![multimodal judge](multimodal_judge.png)

On the newer [Multimodal RewardBench 2](https://arxiv.org/abs/2512.16899) (Meta, December 2025), which includes the current
generation of judges (1,000 expert-annotated pairs per task; other rows from the paper's Table 2):

| judge | text-to-image | image editing | interleaved | reasoning | average |
|---|---:|---:|---:|---:|---:|
| Gemini 3 Pro | 74.4 | 74.9 | 76.4 | 79.5 | 76.3 |
| GPT-5 | 70.5 | 73.8 | 74.4 | 70.2 | 72.2 |
| Gemini 2.5 Pro | 70.5 | 71.3 | 75.1 | 66.6 | 70.9 |
| Qwen3-VL-32B | 64.1 | 67.3 | 70.5 | 56.6 | 64.6 |
| Gemini 2.5 Flash | 63.1 | 66.5 | 69.4 | 57.5 | 64.1 |
| **JEV-27B-VL System 1** | **69.2** | 57.8 | **67.8** | **60.4** | **63.8** |
| GPT-4.1 | 65.8 | 68.2 | 67.0 | 53.0 | 63.5 |
| Qwen3-VL-235B-A22B | 62.0 | 64.8 | 69.0 | 55.9 | 62.9 |
| GPT-4o | 60.3 | 65.0 | 61.5 | 51.9 | 59.7 |

Text-to-image judging comes within 1.3 points of GPT-5; the four-task average is at the level of GPT-4.1 and Qwen3-VL-32B.
GPT-5 and Gemini 3 Pro stay ahead, and image editing is the weakest task.

![MMRB2](multimodal_judge_mmrb2.png)

## Benchmarks

JEV-27B-VL gives the same text decisions as [autotrust/JEV-27B](https://huggingface.co/autotrust/JEV-27B): on 1,000
answer-checking decisions the mean probability difference is 0.010 and 99.8% fall on the same side of 0.5. The text results
below were measured with JEV-27B; the image result was measured with JEV-27B-VL.

### Six public decision benchmarks

Scores in %, higher is better. JEV-27B and TypeSafe Jev 1.13 (hosted API) were run in full by AutoTrust (27 September 2026);
the other rows are as reported in the [NeoHorse-Jev-4B evaluation](https://huggingface.co/TokenRhythm/NeoHorse-Jev-4B/blob/b50e043e22e0e41e7fc0c244e4daa707b8124930/README.md).

| Model | JevBench | Kev | OpenJev text | Nimble | VitaminC | MASSIVE-en | Six-group mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| **JEV-27B / JEV-27B-VL** | **88.70** | 83.75 | **73.89** | **92.91** | 77.46 | **87.71** | **84.07** |
| TypeSafe Jev 1.13, hosted API | 87.18 | **85.52** | 72.96 | 91.84 | 78.46 | 87.14 | 83.85 |
| NeoHorse-Jev-4B | 75.73 | 81.92 | 58.74 | 87.23 | 77.13 | 85.43 | 77.70 |
| Open-Jev-9B | 77.13 | 77.87 | 65.39 | 80.50 | 68.28 | 84.86 | 75.67 |
| Kev-4B | 73.71 | 81.47 | 54.75 | 73.40 | 76.46 | 85.71 | 74.25 |
| Laya English | 55.82 | 61.30 | 40.07 | 45.04 | **78.63** | 68.57 | 58.24 |

### System 1 fidelity and calibration

Held-out `test_set_30k` of `jev-distill-corpus-v3`.

| metric | JEV-27B / JEV-27B-VL |
|---|---:|
| KL divergence from TypeSafe Jev 1.13's distributions (Jev-labelled rows, 0 = identical) | **≈ 0.017** |
| yes/no AUROC | **0.995** |
| choice top-1 agreement with Jev (rows with a clear top option) | **95.8%** |
| rating error, 0-5 scale (MAE of the expected rating) | **0.098** |
| expected calibration error | **0.0009** |
| KL to ground-truth labels of unseen task families | **0.104** |

### Independent benchmark: decision-models-under-pressure

Human gold labels (CLINC-150, MTOP, GoEmotions, DBpedia), 800 items.

| options | 2 | 4 | 8 | 16 |
|---|---:|---:|---:|---:|
| TypeSafe Jev 1.13 (published) | 0.890 | 0.801 | 0.782 | 0.769 |
| **JEV-27B / JEV-27B-VL** | 0.876 | 0.784 | 0.767 | 0.740 |

### Applied tasks (from [JEV-27B-DEMO](https://github.com/yuhai-china/JEV-27B-DEMO))

| task | result | comparison |
|---|---|---|
| **Short-video recommendation, zero-shot** (MicroLens, covers only) · JEV-27B-VL | **AUC 0.727** | collaborative filtering from 59,045 users' logs 0.728 · titles only 0.649 |
| **Agent judge** (Plan-RewardBench, ACL 2026, 1,171 pairs) · JEV-27B-VL | **73.2%**, top of the paper's table | Qwen-Plus 70.0 · Gemini-3-Flash 69.1 · GPT-5 68.5 |
| **Agent judge** (AgentRewardBench, 1,302 trajectories) · JEV-27B-VL | **higher precision than all 16 leaderboard judges** at their recall; AUROC 0.91 | o4-mini, GPT-4o, Claude 3.7, trained 7B judges |
| **Multimodal judge** (VL-RewardBench, 1,247 pairs) · JEV-27B-VL | **78.3% accuracy**, above every model on its 2025 leaderboard | Skywork-VL-Reward-7B 73.3 · GPT-4o 65.8 · Claude 3.5 Sonnet 55.3 |
| **Multimodal judge** (MMRB2, 4 × 1,000 pairs) · JEV-27B-VL | text-to-image **69.2**, average **63.8** | GPT-5 70.5 / 72.2 · GPT-4.1 65.8 / 63.5 · GPT-4o 60.3 / 59.7 |
| **Biomedical research questions** (PubMedQA test, 500) · JEV-27B-VL | **77.8% accuracy**, zero-shot | human experts 78.0% · GPT-4 zero-shot 75.2% · BioBERT 68.1% |
| **Response judge** (RewardBench, 2,985 pairs) | **89.9** | Gemini 1.5 Pro 88.2 · GPT-4o 86.7 · Claude 3.5 Sonnet 84.2 as judges |
| **Hallucination guard** (TriviaQA, answer the trusted half) | **96.4% accuracy** | answering everything 71.2% · model's own stated confidence 87.2% |
| **News recommendation, zero-shot** (MIND) | **AUC 0.642** | best zero-shot baseline 0.606 · LightGBM trained on MIND 0.616 |
| **Search re-ranking** (TREC-COVID, nDCG@10) | **0.858** | bge-reranker-v2-m3 0.793 · BM25 0.623 |
| **System 1 → System 2** (escalate below 0.70 confidence) | **accuracy 0.892**, 70% answered in 0.11 s | System 1 only 0.792 · thinking on everything 0.917 |

### System 2

| benchmark | result |
|---|---:|
| HumanEval pass@1 (greedy) | **78.0%**, identical to Qwen3.8-27B |

## Quick start

```bash
hf download autotrust/JEV-27B-VL --local-dir JEV-27B-VL
bash JEV-27B-VL/serve.sh          # vLLM on :8000; one GPU with 80 GB or more
```

`serve.sh` runs `serve_decide.py`: the standard vLLM OpenAI server, with the same flags as `vllm serve`, plus a
`POST /v1/decide` route for System 1.

```bash
python3 JEV-27B-VL/serve_decide.py --model JEV-27B-VL --served-model-name autotrust/JEV-27B-VL \
  --enable-lora --max-lora-rank 32 --lora-modules jev-decision=JEV-27B-VL/adapter_vllm \
  --logprobs-mode processed_logprobs --max-model-len 32768 --enable-prefix-caching --mamba-cache-mode align \
  --limit-mm-per-prompt '{"image": 8}' --max-num-seqs 8 --trust-request-chat-template
```

Set `MAX_MODEL_LEN=262144` before `serve.sh` for the full 256K context (see [Context length](#context-length)).

### System 1: `POST /v1/decide`

Send a question and get back a calibrated probability for every option. The server builds the decision prompt, reads
the option tokens and applies the decision head's bias and temperature, so any HTTP client works.

```bash
curl localhost:8000/v1/decide -H 'Content-Type: application/json' -d '{
  "kind": "choice",
  "state": "Customer: my card was charged twice for one coffee.",
  "question": "Which team should handle this?",
  "options": ["billing", "shipping", "tech support"]}'
```

```json
{"kind": "choice", "effective_kind": "choice", "options": ["billing", "shipping", "tech support"],
 "probabilities": [0.9969, 0.0000, 0.0031], "choice_index": 0, "choice": "billing",
 "adaptation": "native", "protocol": "jev27-bare-v1", "model": "autotrust/JEV-27B-VL",
 "usage": {"prompt_tokens": 49, "completion_tokens": 1, "total_tokens": 50}, "num_model_requests": 1, "elapsed_seconds": ...}
```

| field | value |
|---|---|
| `kind` | `noul`: yes/no, probabilities for `["false", "true"]` · `score`: a 0–5 scale, for `"0"`…`"5"` · `choice`: for your `options` |
| `state` | what the decision is about: a string, a JSON object, or a list that mixes text and images |
| `question` | one question about the state |
| `options` | `choice` only: 2–256 strings |

For images, make `state` a list; each image is placed where it appears. Images can be data URLs or `https://` URLs.

```python
import base64, requests

def image(path):
    return {"image": "data:image/jpeg;base64," + base64.b64encode(open(path, "rb").read()).decode()}

def decide(kind, state, question, options=None):
    body = {"kind": kind, "state": state, "question": question, **({"options": options} if options else {})}
    r = requests.post("http://localhost:8000/v1/decide", json=body).json()
    return dict(zip(r["options"], r["probabilities"]))

decide("noul", ["Photo: ", image("photo.jpg")], "Is this scenario one where: the image shows food or cooking?")
# e.g. {'false': 0.00, 'true': 1.00}
decide("choice", ["Listing photo: ", image("item.jpg"), "\nSeller title: wireless earbuds, barely used"],
       "Which category fits this listing?", ["electronics", "clothing", "home and kitchen", "toys"])
```

Text-only decisions give the same results as [autotrust/JEV-27B](https://huggingface.co/autotrust/JEV-27B).
`GET /v1/decide/info` reports the option limit and the temperatures.

<details>
<summary>Without <code>serve_decide.py</code>: plain <code>vllm serve</code> and client-side math</summary>

Start the server with `vllm serve` and the same flags, then ask for the option tokens yourself and apply the bundled
bias and temperature. Pass `top_k: 0` and `top_p: 1.0`: the model's `generation_config.json` sets `top_k=20` and
`top_p=0.95`, vLLM applies them as request defaults, and with `--logprobs-mode processed_logprobs` they would truncate
the returned probabilities and zero out less likely options.

```python
import json, math, requests

B = "JEV-27B-VL"
DH = json.load(open(f"{B}/adapter_vllm/decision_head.json"))
T = json.load(open(f"{B}/calibration.json"))["per_kind"]
RAW = ("{%- for m in messages -%}{%- for c in m['content'] -%}{%- if c['type'] == 'text' -%}{{ c['text'] }}"
       "{%- else -%}<|vision_start|><|image_pad|><|vision_end|>{%- endif -%}{%- endfor -%}{%- endfor -%}")

def decide_mm(kind, state_parts, question, options=None):
    """state_parts: list of str and {'image_url': {'url': ...}, 'type': 'image_url'} parts. Up to 16 options."""
    options = {"noul": ["false", "true"], "score": [str(i) for i in range(6)]}.get(kind, options)
    lines = options if kind != "choice" else [f"{'ABCDEFGHIJKLMNOP'[i]}) {o}" for i, o in enumerate(options)]
    content = [{"type": "text", "text": f"[kind] {kind}\n[state] "}]
    content += [p if isinstance(p, dict) else {"type": "text", "text": p} for p in state_parts]
    content.append({"type": "text", "text": f"\n[question] {question}\n[options]\n" + "\n".join(lines) + "\n[decision]:"})
    s = DH["slots"]["ranges"][kind][0]
    ids = DH["verbalizer_ids"][s: s + len(options)]
    r = requests.post("http://localhost:8000/v1/chat/completions", json={
        "model": "jev-decision", "messages": [{"role": "user", "content": content}], "chat_template": RAW,
        "add_generation_prompt": False, "add_special_tokens": False, "max_tokens": 1, "temperature": 1.0,
        "top_k": 0, "top_p": 1.0, "logprobs": True, "top_logprobs": len(options), "allowed_token_ids": ids,
        "return_tokens_as_token_ids": True}).json()
    lp = {int(t["token"].split(":")[1]): t["logprob"] for t in r["choices"][0]["logprobs"]["content"][0]["top_logprobs"]}
    z = [(lp.get(t, -1e9) + DH["bias"][s + i]) / T[kind] for i, t in enumerate(ids)]
    e = [math.exp(x - max(z)) for x in z]
    return {o: x / sum(e) for o, x in zip(options, e)}
```

</details>

### System 2 on images

```python
chart = {"type": "image_url", "image_url": {"url": image("chart.png")["image"]}}   # OpenAI-style image part
requests.post("http://localhost:8000/v1/chat/completions", json={
    "model": "autotrust/JEV-27B-VL",
    "messages": [{"role": "user", "content": [chart, {"type": "text", "text": "What does this chart show?"}]}],
    "max_tokens": 1024, "chat_template_kwargs": {"enable_thinking": False}})
```

## Choice questions with up to 256 options

`choice` takes 2–256 options in one question. The first 16 are labelled A–P, the labels the decision head was trained
on. Beyond 16, the labels continue with Q–Z and then two-letter labels that are single tokens (AA, AB, …), read the same
way, with no retraining. The response's `adaptation` field says `native` (up to 16 options) or `wide-labels`.

Zero-shot intent classification with every intent offered at once (accuracy on 400 test utterances per row):

| dataset | options | intent names only | names + a one-line description each |
|---|---:|---:|---:|
| MASSIVE (en) | 59 | 83.2% | — |
| BANKING77 | 64 | 79.0% | 83.8% |
| BANKING77 | 77 (all) | 74.5% | 81.0% |
| CLINC150 | 64 | 94.8% | 97.3% |
| CLINC150 | 128 | 90.7% | 94.5% |
| CLINC150 | 150 (all) | 89.5% | 93.8% |

* **One `choice` question beats one yes/no question per option**, and costs one forward pass instead of one per option:
  83.2% vs 78.0% on MASSIVE, 78.8% vs 67.0% on BANKING77 (64 options), 94.5% vs 82.0% on CLINC150 (64 options).
* **Calibration at 150 options** (CLINC150): ECE 0.079 with names only (mean confidence 0.84 against 89.5% accuracy,
  slightly under-confident) and 0.034 with descriptions.
* **Speed** (one B200, 8 requests in flight, `--max-num-seqs 8`): a 150-option question takes a median 1.4 s with names
  only (about 790 prompt tokens) and 2.6 s with descriptions (about 3,100 tokens). Above 128 options the server reads the
  option tokens in two passes; the second reuses the cached prompt.

## Writing System 1 prompts

What we measured on the intent-classification sets above (400 utterances per variant):

1. **Facts in `state`, one question in `question`.** `state` holds everything the decision depends on; `question` asks
   one thing about it. Plain text and JSON both work: a JSON `state` scored the same as plain text (83.8% vs 83.2%,
   79.0% vs 79.0%, 94.5% vs 94.8%).
2. **Ask about all candidates in one `choice` question**, not one yes/no question per candidate (see above).
3. **Give similar options a one-line "use when" description.** This was the only change that clearly helped: +4.8
   points on BANKING77 (64 options), +2.5 on CLINC150 (64) and +4.3 on CLINC150 (all 150). The line should say what
   separates the option from its neighbours:
   ```
   [options]
   A) card arrival: use when users ask about the status or delivery of a physical card.
   B) card delivery estimate: use when users ask about the expected arrival time or delivery speed of a new card.
   C) Refund not showing up: use when a customer cannot see a completed refund in their account or statement.
   D) request refund: use when a user asks how to initiate or the timing of a refund for a purchase.
   ```
   More text did not help further. Longer rules with "do not use for …" clauses (about three times the tokens) and two
   worked examples per option scored 83.8% and 84.0% on BANKING77 (vs 83.8% for one line), and 97.3% and 96.0% on CLINC150
   (vs 97.3%). Generic descriptions did not help either: CLINC150's own intent descriptions scored 94.5%, against 94.8%
   for names alone.
4. **Wording barely matters.** A domain-specific question, an extra instruction ("Choose the single best-matching
   intent"), a JSON `state` and alphabetical option order all stayed within ±1.5 points of the plain prompt, inside the
   ±1.8-point sampling noise of 400 items. Keep prompts plain.
5. **Phrase `noul` so that "true" is the outcome you want the probability of**, e.g. "Is the customer asking for a
   refund?". Our demos use "Is this scenario one where: …?" for properties of a text or an image.
6. **One option per line.** The template lists one option per line, so keep newlines out of option text.
7. **Check order sensitivity when it matters.** About 7% of 16-option answers change with option order alone. For
   pairwise judging, ask both orders and average; on RewardBench pairs the two orders agreed 96% of the time.
8. **Use the probability, not just the top option.** Act automatically above a threshold you validated on your own data,
   and send the rest to System 2 or a person.

## Context length

The backbone's native context is **262,144 tokens (256K)**, and System 1 accepts prompts up to that length when vLLM is
started with `--max-model-len 262144`. We tested decisions that hinge on a single sentence placed at a random depth in
long real text (concatenated PubMedQA abstracts): a yes/no question (was the refund for order #N approved or rejected?)
and a 16-option question (which room is the spare part for machine M kept in?), 10 of each per length.

| prompt length | yes/no correct | 16-option correct | mean probability on the right answer | median latency |
|---:|---:|---:|---:|---:|
| 4K (4,235 tokens) | 10/10 | 10/10 | 0.999 | 0.6 s |
| 32K (32,157 tokens) | 10/10 | 10/10 | 0.998 | 3.0 s |
| 64K (64,070 tokens) | 10/10 | 10/10 | 0.997 | 5.7 s |
| 128K (127,895 tokens) | 10/10 | 10/10 | 0.997 | 12.2 s |
| 192K (191,659 tokens) | 10/10 | 10/10 | 0.997 | 20.2 s |
| 250K (249,507 tokens) | 10/10 | 10/10 | 0.997 | 28.7 s |

Latency is one request at a time on one B200 and is almost all prompt processing (about 8,700 tokens per second at 250K).

Memory: the KV cache takes about 65 KB per token, so a full 256K prompt needs about 17 GB on top of the 52 GB of weights
(tested on a 183 GB B200). On an 80 GB GPU, start with `--max-model-len 131072`.

## Serving notes

* **`--max-num-seqs 8` is required.** With more than 8 sequences in one batch, vLLM's LoRA path for this multimodal model
  class returns wrong System 1 probabilities (the text-only JEV-27B is not affected). With the cap, results match JEV-27B at
  any client concurrency; requests beyond 8 simply queue.
* **Throughput** on one B200 with the cap: 24 short text decisions in about 1.4 s; 4,000 image decisions with 6 images each
  in 316 s (about 13 per second).
* **`--trust-request-chat-template`** lets `/v1/decide` (and the client-side code above) render the raw decision template
  for image decisions. System 2 uses the model's own chat template.
* **`serve_decide.py`** needs the vLLM development build this model was tested with (September 2026): it uses
  `logprob_token_ids` and that build's server layout. Everything else is plain vLLM, and all OpenAI endpoints stay
  available on the same port.
* **Calling `/v1/completions` or `/v1/chat/completions` for System 1 yourself:** pass `top_k: 0` and `top_p: 1.0`. The
  model's generation config sets `top_k=20` and `top_p=0.95`; vLLM applies them as request defaults, and they would
  truncate the returned probabilities. `serve_decide.py` does this for you.
* Images are resized by the Qwen3.8 processor. Downscaling large images first (for example to at most 448 px) keeps the
  number of vision tokens and the latency low.

## Limitations

* System 1's decision head was trained on text. Decisions over images are zero-shot: they are well ordered in the
  experiment above, but their calibration on image tasks has not been measured systematically.
* The short-video recommendation result is an offline evaluation on one dataset (200 users), ranking from covers only.
* Choices with more than 16 options use labels the decision head never saw in training. Accuracy holds up (see the
  intent-classification table), but their calibration has been measured on one dataset only.
* The long-context test is a single-fact decision over text. Long documents with images and harder long-document
  reasoning have not been measured.

## License

Apache-2.0. This repository contains the weights of [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B)
(Apache-2.0, see `LICENSE`) unchanged, plus the JEV System 1 adapter and decision head from
[autotrust/JEV-27B](https://huggingface.co/autotrust/JEV-27B).

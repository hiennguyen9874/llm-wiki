---
license: cc-by-nc-4.0
language:
- en
- de
- fr
- hi
- zh
- ja
tags:
- decision-model
- zero-shot-classification
- classification
- agents
- browser-agent
- computer-use
- calibrated-probabilities
- vllm
---

# OpenJev

**Typed decisions about text, web pages and screenshots. One forward pass per question with up to 52 options. About 210 ms for an isolated web decision on one H100, with roughly 1,460 prompt tokens and 23 options.**

No free-form text to parse. No chain of thought. No training per task.

![OpenJev in five numbers](assets/hero_stats.png)

OpenJev is an open-weights **decision model**. You describe the decision in plain words at request time, with your own labels, and it answers with a choice, a yes / no probability or a score. The same model routes a support ticket, flags a policy violation, judges whether an answer is grounded, and tells a browser agent which button to press next.

**

```bash
curl -s http://localhost:3000/v1/systemone -H 'Content-Type: application/json' -d '{
  "model": "openjev",
  "state": "Customer message: I was charged twice for my order last week and nobody has replied.",
  "questions": {
    "route":   {"type": "choice", "instructions": "Which team should handle this?",
                "criteria": {"billing": null, "shipping": null, "technical": null}},
    "angry":   {"type": "noul",   "instructions": "Is the customer angry?"},
    "urgency": {"type": "score",  "instructions": "How urgent is this?",
                "criteria": ["can wait", "this week", "today", "right now"]}
  }
}'
```

Three questions in one API request, three typed answers, each with a probability for every option. One forward pass per question (up to 52 options).

## Why it is different

- **Labels live in the request.** No labelled data, no training run, no fixed label set. New task, new labels, new domain: change the JSON, not the model.
- **Not a chatbot you have to parse.** The answer is read from the scores at the first output position: one score per option, converted to probabilities using fixed calibration settings. There is no free-form answer to parse and no long generation to wait for.
- **Fast enough to sit inside a loop.** About 80 ms for a short text decision and about 210 ms for an isolated web decision with roughly 1,460 prompt tokens and 23 candidate elements, on one H100.
- **Built for agents as well as text.** It reads DOM, JSON and screenshots, picks the target element, picks the next operation and says when the task is finished.
- **Stable.** Shuffle the option order and the answer changes in 2.3% of cases (18.5% for the same model before tuning).

## Use cases

| job | example decision |
|---|---|
| Routing and triage | intent, topic, team, priority, language |
| Moderation and safety | toxicity, spam, hate, policy violation, legal threat |
| Judging other models | grounded or hallucinated, which answer is better, does it follow the rubric |
| Documents and ops | invoice approve / hold / reject, alert severity, contract clause type |
| Browser and desktop agents | which element, which operation, is the task done, is it blocked |
| Scoring | ordered levels with an expected value and a confidence |

## Results

How these were measured: every test set was held out from our fine-tuning (checked by id and by content against our training sets). Of the 10,000 text questions, 6,922 were fresh for this run and 3,078 had been used during development; the tables show both together and the fresh-only gap is given below. In the text tables the hosted Jev API answered exactly the same questions; the agent, language and screenshot rows compare OpenJev with its own base model.

### Text decisions: 10,000 text questions, 34 public sources, the same questions for every model

| model | accuracy |
|---|---|
| Jev (hosted API) | 85.4% (8,540 of 10,000) |
| **OpenJev** | **84.0%** (8,403 of 10,000) |
| the same base model before tuning, same readout, its own calibration | 80.4% (8,036 of 10,000) |
| Nimble 9B (open) | 75.7% (7,574 of 10,000) |

Within 2 points of the hosted Jev API (1.4 points behind; 1.2 on the 6,922 fresh additions and replacements), 3.7 points above its own base, 8.3 points ahead of Nimble 9B, with open weights you can run yourself. Every question has at most 26 options and fits Nimble's 2,048-token limit, so all four models received the same state, question text, options and option order. Only the hosted model-routing field differed. There was one attempt per question, with no retries. Three invalid or failed hosted responses (one HTTP 520 error, two answers whose chosen option was not their own highest-probability option) count as incorrect; the other arms had none.

![How far each open model is from the hosted Jev API, by kind of work on the 10,000 questions: OpenJev is within 2 points on five of eight kinds and ahead on three, Nimble 9B is 4 to 17 points behind](assets/distance_from_jev.png)

![Accuracy by kind of work on the 10,000 questions: OpenJev, the hosted Jev API and Nimble 9B](assets/radar_jobs.png)

| kind of work | questions | OpenJev | Jev (hosted API) | before tuning |
|---|---|---|---|---|
| intent / routing / topic | 1,218 | 92.8% | 92.8% | 93.2% |
| sentiment / stance | 1,214 | 82.1% | 81.5% | 78.3% |
| spam / hate | 695 | 80.4% | 81.2% | 80.1% |
| legal | 1,305 | 78.9% | 78.8% | 77.8% |
| ethics / policy judgement | 877 | 78.1% | 75.8% | 65.5% |
| commonsense reasoning | 2,260 | 85.8% | 88.3% | 80.3% |
| science / facts / claims | 1,558 | 82.5% | 89.0% | 81.0% |
| reading + language | 873 | 89.2% | 89.3% | 83.3% |

The legal rows include 613 distinct merger-agreement clauses from 151 contracts, scored with native expert annotations: OpenJev 76.7%, hosted 73.7%, before tuning 75.4%. These are held-out contract-question pairs, not unseen contracts.

### Agent decisions, languages and text: before and after tuning

![Accuracy of the same base model before tuning and of OpenJev, on six held-out test sets](assets/gains.png)

| test | steps | before tuning | OpenJev |
|---|---|---|---|
| desktop: next action from a screenshot | 2,000 | 76.5% | **88.0%** |
| web: next action on unseen websites | 975 | 68.5% | **87.4%** |
| web: next action on unseen domains | 1,000 | 65.7% | **84.5%** |
| answer flips when the options are shuffled | 2,000 | 18.5% | **2.3%** |

### Whole browser tasks, end to end

**OpenJev ties the hosted Jev API** on our matched development run. 100 MiniWoB task types, one attempt each, the same open text-only client for every model. About a quarter of these tasks need colour, shapes, drawing or dragging, which a text-only click-and-type client cannot do, so no model gets close to 100 here; what matters is the comparison on identical conditions.

| model | tasks completed |
|---|---|
| **OpenJev** | **39** |
| Jev (hosted API) | 39 |
| the same base model before tuning | 38 |


### Languages and long documents

| test | questions | before tuning | OpenJev |
|---|---|---|---|
| inference in German, French, Hindi, Chinese (XNLI) | 240 | 72.5% | **82.5%** |
| intent in German, French, Hindi, Japanese (MASSIVE) | 240 | 80.4% | **85.8%** |
| questions about 2,600 to 8,500-token articles (QuALITY) | 120 | 91.7% | 91.7% |

### Speed, one H100, FP8

![Median time to a decision by prompt size: first read of a page and a new question on a cached page](assets/latency.png)

| one question per request, prompt size | 1.1k tokens | 4.1k | 8.1k | 12.2k | 15.1k |
|---|---|---|---|---|---|
| first read of a page, median | 227 ms | 477 ms | 923 ms | 1,433 ms | 1,758 ms |
| same page again, new question (cached), median | 118 ms | 162 ms | 213 ms | 246 ms | 257 ms |

- Short text decisions: about 80 ms each (3,347 sequential questions in about 4.5 minutes).
- Desktop step with a screenshot: 176 ms median. Web step (about 1,460 prompt tokens, about 23 options): about 210 ms median.
- 100 questions about one 4,100-token page: 3.9 s in total with helper queue concurrency 16, an average of 39 ms per question across the batch. This is not sequential request latency.
- 7 requests per second on distinct 1,200-token pages at concurrency 8, on a single GPU.

## Quick start

```bash
pip install "vllm==0.29.0" "openai==3.16.2" "httpx==0.28.1"
hf download openjev/openjev --local-dir openjev

# 1. the model
vllm serve ./openjev --host 127.0.0.1 --served-model-name qwen --port 8000 \
  --enable-prefix-caching --max-model-len 16384 --gpu-memory-utilization 0.90 \
  --limit-mm-per-prompt '{"image":1}' --trust-remote-code --max-num-seqs 256 \
  --max-logprobs 64 --gdn-prefill-backend triton --quantization fp8

# 2. the decision API in front of it
VLLM=http://localhost:8000/v1 TOKENIZER=./openjev \
READOUT_T=0.85 READOUT_NOUL_T=1.829074 READOUT_NOUL_BIAS=0 \
READOUT_TARGETED=1 READOUT_INSTR_STYLE=pyrepr SHIM_STAGGER=1 \
python openjev/helper/shim.py --host 127.0.0.1 --port 3000
```

Then `POST /v1/systemone` as in the example at the top. Full serving guide, every flag and the security notes for exposing the port: [`serve/SERVE.md`](serve/SERVE.md).

The request and response shapes follow the hosted Jev API, so a client written for it can be pointed at your own server.

Tip for agent builders: treat `DONE` as the model's opinion and confirm completion in your own loop (a success message, a changed URL, a saved record) before you stop.

## Formats

| format | repository | status |
|---|---|---|
| 16-bit (bfloat16), about 54 GB | `openjev/openjev` | this repository. Serve with `--quantization fp8` on one 80 GB GPU: that is OpenJev's primary measured serving recipe |
| FP8 checkpoint, about 29 GB | `openjev/openjev-FP8` | available. Same 10,000 questions: 84.2% vs 84.0% for the served 16-bit model (+0.17 points, 95% interval −0.13 to +0.45); same 2,000 desktop screenshots: 88.0% vs 88.0% (+0.05). About 2% of individual answers change. |
| MLX 8-bit for Apple silicon, about 27 GB, text only | `openjev/openjev-MLX` | available. Same 10,000 questions through the same helper on a Mac: 8,403 correct, the same count as the served 16-bit model (72 questions each way; 95% interval −0.24 to +0.22 points); 1.5% of individual answers change. No screenshot input in this build. |
| MLX 4-bit for Apple silicon, about 15 GB, text only | `openjev/openjev-MLX-4bit` | available. The smallest build, for Macs where 27 GB does not fit. On the first 4,692 of the 10,000 questions through the same helper on a Mac: 84.3% (3,957) vs 84.9% (3,982) for the served 16-bit model and 84.7% for the MLX 8-bit build. No screenshot input in this build. |
| GGUF for llama.cpp, four quantizations from 16.5 GB (Q4_K_M) to 28.6 GB (Q8_0), text only | `openjev/openjev-GGUF` | available. Q4_K_M fits a 24 GB card (RTX 3090 / 4090). Validated on 1,789 held-out questions paired against the served 16-bit model: Q4_K_M 82.8% vs 83.2% (−0.34 points, 95% interval −1.06 to +0.39); Q8_0 82.6% (−0.61 points, −1.17 to −0.11). 3 to 4% of individual answers change. Not yet run on the full 10,000. No screenshot input in this build. |

Every quantized format is listed with its own measured accuracy on held-out questions: the FP8 and MLX builds on the same frozen 10,000, the GGUF builds on a separate 1,789-question held-out set so far.

## Request limits

- Up to 52 options per question in a single pass. More options are handled in several passes (groups of 52, then a final pass over the winners).
- Prompts up to 16,384 tokens. One image per request.
- Probabilities are calibrated by the helper with the fixed settings shown in the quick start; keep them as they are to reproduce the numbers on this page.

## How it works, in one paragraph

A language model computes a score for every possible next token before it writes anything. OpenJev gives each of your options a letter, asks the question, and reads the scores of exactly those letters at the first output position (the server is asked for a single token, never a free-form answer). For questions with up to 52 options, one forward pass produces one number per option, then a calibration step turns the numbers into probabilities you can threshold. The model is tuned so that this single position carries the decision: trained to select the correct option and stay consistent when the options are reordered.

## Licence

OpenJev weights are released under **CC BY-NC 4.0**: free for research and other non-commercial use, with attribution. For a commercial licence, email [support@loopai.com](mailto:support@loopai.com).

The files in `helper/` and `serve/` are Apache 2.0. OpenJev is built on an Apache 2.0 open base model; the required attribution is in [`NOTICE`](NOTICE) and the Apache text is in `LICENSE-APACHE-2.0`.

OpenJev is an independent project, not affiliated with TypeSafe; Jev is their product.

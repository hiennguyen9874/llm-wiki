---
license: apache-2.0
base_model: huihui-ai/Huihui-Qwen3.8-27B-abliterated
base_model_relation: quantized
library_name: gguf
pipeline_tag: text-generation
language:
  - en
  - ru
tags:
  - gguf
  - llama.cpp
  - qwen3.8
  - conversational
  - roleplay
  - creative-writing
  - character
  - humanlike
  - uncensored
  - sillytavern
  - tool-calling
  - function-calling
  - on-policy-distillation
---

# Qwen3.8-27B-Humanlike-Chat 2.0

**A 27B model that texts like a person and still does the work.** No system prompt needed. Text it and it texts back like someone you know. Ask for a formal email, a tool call or a proper explanation and it does that, then goes back to texting.

[![Try the model](https://img.shields.io/badge/-Try%20the%20model-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat) [![Download GGUF](https://img.shields.io/badge/-Download%20GGUF-475569?style=for-the-badge)](#download) [![vLLM / safetensors](https://img.shields.io/badge/-vLLM%20%2F%20safetensors-334155?style=for-the-badge)](#vllm-and-sglang-safetensors) [![Free endpoint](https://img.shields.io/badge/-Free%20endpoint-0F766E?style=for-the-badge)](#free-endpoint) [![Join Discord](https://img.shields.io/badge/-Join%20Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/jWbqEqsgAf) [![Commissions open](https://img.shields.io/badge/-Commissions%20open-10B981?style=for-the-badge)](https://discord.com/users/320486798859960322)

[Quick start](#quick-start) · [Download](#download) · [vLLM / safetensors](#vllm-and-sglang-safetensors) · [Free endpoint](#free-endpoint) · [Results](#results) · [How it was made](#how-it-was-made) · [Custom finetunes](#custom-finetunes)

<p align="center"><img src="images/01-cover.png" width="560" alt="Same casual texts sent to both models with no system prompt. 2.0 texts back in short lines; official Qwen3.8-27B opens with How can I help you today? and answers with paragraphs."></p>
<p align="center"><sub>Same texts, no system prompt. Left: 2.0. Right: official Qwen3.8-27B, one sample, long replies cut.</sub></p>

## Why download it

- **It texts like a person out of the box.** Shown a real chat and two next messages, a blind judge took 2.0's for the real person's 23.5% of the time. Official Qwen3.8-27B got 15.1%, and the abliterated base 2.0 is built on got 0.3% (6.8% with a "text like a human" prompt). 50% would mean the judge can't tell.
- **It follows instructions it never trained on.** IFBench 43.7, up from 37.3 for the base.
- **It asks before it guesses.** When2Call 58, base 48. When no tool fits, it doesn't call one: BFCL irrelevance 78, base 60.
- **The basics held.** GSM8K 89.1, same as the base. Right tool with the right arguments: BFCL simple 98.
- **It fits a 24 GB card.** IQ4_XS is 15.10 GB. Or skip the download and use the [free endpoint](#free-endpoint), which runs 2.0.

"Base" on this card always means `huihui-ai/Huihui-Qwen3.8-27B-abliterated`, an abliterated Qwen3.8-27B. It is not the official Qwen release.

**Commissions open.** I build custom finetunes like this one: characters, product voices, distillation into smaller models, and domain or use-case specific models. DM [**codebottle** on Discord](https://discord.com/users/320486798859960322). [Details](#custom-finetunes).

**If it feels more natural than your current Qwen model, click Like. It helps other people find it.**

## What it looks like

<table>
<tr>
<td width="50%"><img src="images/03-character.png" alt="Same flight attendant character card, turns 12 to 16 of a long chat. 2.0 answers I don't, haha to how she deals with jet lag; official Qwen writes a long jet lag guide."></td>
<td width="50%"><img src="images/04-email.png" alt="Asked for a formal email to a professor with no system prompt, 2.0 writes a proper email, then replies to sent it lol like a friend."></td>
</tr>
<tr>
<td><sub>A character card, turns 12 to 16 of a long chat. 2.0 stays a jet-lagged flight attendant. Official Qwen writes a jet lag guide.</sub></td>
<td><sub>Ask for a formal email and you get one. Official Qwen wrote a good one too. The difference is the next message.</sub></td>
</tr>
<tr>
<td width="50%"><img src="images/05b-tool-chat.png" alt="One chat. 2.0 calls get_weather for Lisbon in celsius and reports the result in one line, asks What time? before booking a table, and answers a rhyme question without a tool."></td>
<td width="50%"><img src="images/06-benchmarks.png" alt="Bar charts: 2.0 vs its abliterated base on IFBench, When2Call, BFCL irrelevance, BFCL live irrelevance, BFCL simple, IFEval and GSM8K, plus the ishuman v2 results."></td>
</tr>
<tr>
<td><sub>One new chat, never in training. It calls the weather tool, asks for the time before booking, and answers the rhyme without a tool. Greedy, canned tool result.</sub></td>
<td><sub>2.0 vs the abliterated base it was trained on. Same run, same prompts, thinking off. IFEval, BFCL simple and GSM8K are ties.</sub></td>
</tr>
</table>

## Quick start

### llama.cpp

```bash
llama-server --hf-repo LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF \
  --hf-file Qwen3.8-27B-Humanlike-Chat-IQ4_XS.gguf \
  --jinja \
  --ctx-size 32768 --parallel 1 --n-gpu-layers 99 \
  --temp 1.0 --top-p 0.95 --top-k 20 \
  --alias humanlike-2.0 --host 127.0.0.1 --port 8080
```

Open http://127.0.0.1:8080 and start texting. `--jinja` uses the model's own chat template, which is what makes tool calls work. For another quant, swap in a file name from [Download](#download).

The server speaks the OpenAI API:

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="none")
MODEL = "humanlike-2.0"  # the --alias above

# 1. Plain chat, no system prompt
r = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "hey, what's up?"}],
)
print(r.choices[0].message.content)

# 2. Tool calling. The departure city is missing, so 2.0 should ask instead of guessing.
tools = [{
    "type": "function",
    "function": {
        "name": "search_flights",
        "description": "Search roundtrip flights.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Departure city or airport"},
                "destination": {"type": "string", "description": "Arrival city or airport"},
                "depart_date": {"type": "string", "description": "YYYY-MM-DD"},
                "return_date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["origin", "destination", "depart_date", "return_date"],
        },
    },
}]
r = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "find me a roundtrip flight to Atlanta, march 1 to march 6"}],
    tools=tools,
)
msg = r.choices[0].message
print(msg.tool_calls or msg.content)

# 3. Thinking, with a reasoning effort
r = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "is it worth learning to cook if i live alone"}],
    extra_body={"chat_template_kwargs": {"enable_thinking": True, "reasoning_effort": "low"}},
)
print(getattr(r.choices[0].message, "reasoning_content", None))  # the thinking
print(r.choices[0].message.content)                              # the reply
```

When the model calls a tool, send the result back as a `{"role": "tool", ...}` message, like with any OpenAI-compatible model.

### Thinking

Thinking works. 2.0 thinks briefly in first person, then texts back in the same voice. With `--jinja` it is on by default.

Set `reasoning_effort` per request, as in example 3. It takes `low`, `medium` or `xhigh` (the template's default). The thinking comes back in its own field, separate from the reply. For the fastest replies, send `"enable_thinking": false` instead. Example:

```text
user: i miss you
2.0 (thinking): I’m glad they miss me, and I miss them back. I want to keep it brief and warm rather than make it feel like an overwrought declaration.
2.0: i miss you too
```

### LM Studio and Ollama

Both load GGUF files. Thinking works there too.

### SillyTavern

Start `llama-server` as above, then connect with:

```text
API: Chat Completion
Chat Completion Source: Custom (OpenAI-compatible)
Custom Endpoint (Base URL): http://127.0.0.1:8080/v1
Context: 32768
Response length: 512
Temperature: 1.0
Top P: 0.95
```

In Chat Completion mode llama-server applies the model's own chat template, which is how my tests sent messages. If you ask for long answers, raise the response length.

### vLLM and SGLang (safetensors)

Safetensors builds for vLLM, SGLang and transformers, made from the same merged BF16 weights as the GGUFs. Pick the one that fits your card:

| Repo | Size | Fits | KL vs reference | tok/s (vLLM) | Checks |
|---|---:|---|---:|---:|---|
| [GPTQ-Int4](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0-GPTQ-Int4) | 20.62 GB | 24 GB card, 8k context | 0.0274 | 86 | all pass |
| [FP8](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0-FP8) | 30.89 GB | 48 GB card | 0.0079 | 72 | all pass |
| [BF16](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0) | 55.59 GB | 80 GB card | 0.0032 | 46 | all pass |

The 24 GB setup, tested with vLLM 0.27.1 capped at 21.9 GiB:

```bash
vllm serve LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0-GPTQ-Int4 --served-model-name humanlike-2.0 \
  --max-model-len 8192 --max-num-seqs 4 --max-num-batched-tokens 2048 --gpu-memory-utilization 0.91 \
  --language-model-only --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3
```

On a bigger card, swap in the FP8 or BF16 repo and drop the memory flags. Each repo's card has its exact command. FP8 on a 48 GB card also needs `--max-num-seqs 128`, and on an H100 add `--linear-backend cutlass`. Thinking is on by default. Send `chat_template_kwargs: {"enable_thinking": false}` per request for the fastest replies. For SGLang, point `--model-path` at the repo. KL and checks use the same 5 test chats as the table below; tok/s is single-request decode on one H100 NVL.

## Download

**Which file:** with 24 GB of VRAM, take IQ4_XS or Q4_K_M. With 32 GB, take Q6_K. With 48 GB or more, take Q8_0. The free endpoint runs IQ4_XS.

| File | Size | KL vs reference | tok/s | Checks |
|---|---:|---:|---:|---|
| [IQ4_XS](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF/resolve/main/Qwen3.8-27B-Humanlike-Chat-IQ4_XS.gguf) | 15.10 GB | 0.0219 | 43 | all pass |
| [Q4_K_M](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF/resolve/main/Qwen3.8-27B-Humanlike-Chat-Q4_K_M.gguf) | 16.56 GB | 0.0218 | 50 | all pass but one tool turn |
| [Q5_K_M](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF/resolve/main/Qwen3.8-27B-Humanlike-Chat-Q5_K_M.gguf) | 19.24 GB | 0.0086 | 56 | all pass but one tool turn |
| [Q6_K](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF/resolve/main/Qwen3.8-27B-Humanlike-Chat-Q6_K.gguf) | 22.09 GB | 0.0047 | 46 | all pass |
| [Q8_0](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF/resolve/main/Qwen3.8-27B-Humanlike-Chat-Q8_0.gguf) | 28.60 GB | 0.0028 | 55 | all pass |
| BF16, two shards ([1](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF/resolve/main/Qwen3.8-27B-Humanlike-Chat-BF16-00001-of-00002.gguf), [2](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF/resolve/main/Qwen3.8-27B-Humanlike-Chat-BF16-00002-of-00002.gguf)) | 53.81 GB | 0.0017 | 36 | all pass |
| [Safetensors BF16](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0) (vLLM, SGLang, transformers) | 55.59 GB | 0.0032 | | all pass |
| [Safetensors FP8](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0-FP8) (vLLM, SGLang) | 30.89 GB | 0.0079 | | all pass |
| [Safetensors GPTQ-Int4](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0-GPTQ-Int4) (vLLM, SGLang) | 20.62 GB | 0.0274 | | all pass |
| [2.0 LoRA, rank 320, F16](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF/resolve/main/lora/Qwen3.8-27B-Humanlike-Chat-2.0-LoRA-r320-F16.gguf) | 4.67 GB | | | see [Standalone LoRA](#standalone-lora) |

- **KL vs reference:** how far each file's next-token predictions drift from the reference (the base plus the 2.0 adapter at runtime in BF16, the setup behind every number on this card). Lower is closer. It is the mean KL over the reference's top 20 tokens at fixed points in 5 fresh test chats, so it underestimates the full KL. Safetensors rows were measured on vLLM 0.27.1.
- **tok/s:** decode speed on one H100 NVL (llama.cpp, single request, 256-token decode).
- **Checks:** automatic checks on the same 5 chats: tool calls (right arguments, asking when a detail is missing, no call when no tool fits), requested formats, closed thinking blocks, assistant phrases in casual turns and reply language.
- Downloaded from this repo before? The file names are the same, so download again to get 2.0. Exact hashes are in [`SHA256SUMS`](SHA256SUMS).
- Load the merged files as a normal model. There is no LoRA strength to set.

## Free endpoint

2.0 runs on a free, rate-limited, OpenAI-compatible endpoint (the IQ4_XS quant). Tool calls work there too.

| Setting | Value |
|---|---|
| Base URL | `https://api.lessthanthreeai.com/v1` |
| Model | `qwen3.8-27b-humanlike-chat` |
| API key | Not required |

```python
from openai import OpenAI

client = OpenAI(api_key="not-required", base_url="https://api.lessthanthreeai.com/v1", timeout=300.0)

reply = client.chat.completions.create(
    model="qwen3.8-27b-humanlike-chat",
    messages=[{"role": "user", "content": "hey, what are you up to?"}],
)
print(reply.choices[0].message.content)
```

Thinking works here too: send `extra_body={"chat_template_kwargs": {"enable_thinking": True, "reasoning_effort": "low"}}` (or `medium`, `xhigh`). The reasoning comes back in a separate field from the reply. Without it, the endpoint answers straight away.

The endpoint scales to zero when idle. The first request after a quiet period waits while a GPU starts, so keep the client timeout at 300 seconds or more. In the browser: [chat demo](https://huggingface.co/spaces/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat).

## How to use it

- **No system prompt means a person texting.** Short lowercase lines that react to what you said. It plays an ordinary person with an ordinary day, so it makes up small life details ("been on my feet since like 7am"). That is on purpose. If you need it to talk about itself as a model, say so in a system prompt.
- **A character card decides who it is, not how it writes.** Give it a name, age, job and mood and it texts as that person. A sarcastic nurse manager stays sarcastic.
- **Explicit instructions beat texting.** A one-off request ("write a formal email", "numbered steps", "explain properly", "reply in Russian") applies to that reply, then it goes back to texting. A standing one ("from now on write full sentences") holds until you change it. A writing rule in a card counts as an instruction. Personality words like "formal person" don't.
- **Work requests get real answers:** math, explanations, emails, code, tool calls. When it can't fill a tool argument honestly, it asks first.
- **Language:** it replies in the language you write in. I tested English and Russian.
- **Sampling:** temperature 1.0, top_p 0.95, top_k 20. These are the base model's defaults, and every voice eval used them. Benchmarks used greedy decoding.

## Results

### Capability

| Test (items) | Base | **2.0** |
|---|---:|---:|
| IFBench strict (300) | 37.3 | **43.7** |
| IFEval strict prompt (541) | 81.9 | **83.5** |
| When2Call (100) | 48 | **58** |
| GSM8K (64) | 89.1 | 89.1 |
| BFCL simple / multiple (100 each) | 97 / 96 | 98 / 96 |
| BFCL irrelevance (100) | 60 | **78** |
| MMLU-Pro (200) | 78.5 | 72.5 |
| LiveCodeBench pass@1 (100) | 56 \* | 51 |

Same run, same prompts, thinking off, greedy. Base is the abliterated Huihui Qwen3.8-27B, not official Qwen. BFCL and When2Call use my own scorers: consistent across models, not comparable with the public leaderboards. The sets are small, so 1 to 3 points is noise.

\* LiveCodeBench base is from an earlier run (30 Sep). 2.0 ran on 1 Oct.

- **IFBench** is the cleanest result. None of its 58 instruction types are in the training data, and 2.0 is 6.4 points above the base.
- **IFEval** is slightly above the base.
- **When2Call** checks the right move: call a tool, ask for a missing detail, or say no tool fits. 2.0 calls less and asks more.
- **GSM8K and BFCL calls** match the base. On BFCL irrelevance (not calling a tool when none fits) it is far above the base, 78 against 60.

### Does it sound human? (ishuman v2)

A blind judge sees a real moment from my own one-to-one chats (moments that never went into training) and two candidate next messages: the one the person really sent and the model's. It picks the real one. Every pair is judged twice, once in each order.

| Model | Judge took the model's reply for the real one |
|---|---:|
| Base (Huihui abliterated) | 0.3% |
| Base + "text like a human" prompt | 6.8% |
| Official Qwen3.8-27B | 15.1% |
| **2.0** | **23.5%** |

**How to read it:** the judge always knows one of the two messages is fake, so 50% would mean it can't tell the model from the person. 50% is the ceiling, not 100%.

In 16 live chats with a simulated texter, the judge picked 2.0 over the base every time and over the prompted base in 96.9% of judgments.

Caveats: the judge is one LLM, not people, and most of the 147 moments are in Russian (97). The voice LoRA inside 2.0 learned from other sessions of the same chats, so 2.0 plays at home here while the base and official Qwen don't.

## How it was made

The voice comes from SFT on real and synthetic conversations (139,845 messages from 1,396 conversations).

For 2.0 I used on-policy distillation: the model writes its own replies and a teacher grades every token. There are two teachers. For chat and characters it's the voice model plus a hidden "text like a person" instruction. For instructions, tools and code it's the plain base. The student never sees the hidden instruction, so 2.0 texts that way with no system prompt.

It practised on conversation starts, not answers: 3,208 real conversation openings from the API (starting points only, it wrote its own replies), 156 characters and 4,200 public tasks (1,200 tool, 1,800 instruction, 1,200 code). None of them overlap any test on this card. Four rounds on rented GPUs. The tool data is balanced half call, half ask or decline, so it asks instead of guessing. The final run was 36 steps on one H100, about 6 hours.

The base is abliterated, so it refuses little. I picked it because I wanted something that isn't censored.

```text
Qwen/Qwen3.8-27B
  -> huihui-ai/Huihui-Qwen3.8-27B-abliterated (revision d42ca897)
  -> humanlike voice LoRA (SFT, rank 256) at strength 0.4
  -> 2.0 LoRA (rank 64, on-policy distillation, final step 106)
  -> both merged once into BF16 (together one exact rank-320 adapter)
  -> BF16 / Q8_0 / Q6_K / Q5_K_M / Q4_K_M / IQ4_XS GGUF
```

<details>
<summary><strong>Technical details</strong></summary>

| Item | Specification |
|---|---|
| Base model | `huihui-ai/Huihui-Qwen3.8-27B-abliterated` at revision `d42ca8978c5a66e92c3446d46e8adfe03ef692ff`, based on `Qwen/Qwen3.8-27B` |
| Architecture | Dense 27B, 64 language layers (48 linear attention, 16 full attention) |
| Adaptation | Humanlike voice LoRA (rank 256, strength 0.4) plus the 2.0 LoRA (rank 64), merged into BF16 in fp32 with a single cast. Together they equal one exact rank-320 adapter over 496 language modules. |
| 2.0 training | On-policy distillation, exact full-vocabulary reverse KL against the teacher on every token |
| Merge check | Merged BF16 vs base plus the rank-320 adapter at runtime: mean KL 0.0023, top-1 agreement 97%, greedy replies identical on 11 of 15 turns |
| Context | 262,144 tokens native. Start at 32,768. 2.0 training prompts were capped at 12k tokens; long-chat evals went to 30 turns. |
| Quantization | Every quant comes from the same merged BF16 GGUF, built with `llama.cpp@95ef7fc16054e63b427a3ef00188e055ef7586d8`. Importance matrix: WikiText-2 train (128 x 512-token chunks) plus a chat and tool-call text mix ([`imatrix/imatrix.gguf`](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF/blob/main/imatrix/imatrix.gguf), computed on the merged 2.0 BF16; use it for your own quants). Q8_0 uses none. The 96 recurrent gate tensors stay at Q8_0 and 353 control tensors at F32. |
| Modality | Tuned and tested on text only. The GGUFs are text only. The BF16 safetensors keep the base's vision tower and MTP head unchanged. |
| License | Apache-2.0 |

Hugging Face and Transformers may show the architecture as `qwen35` or `qwen3_5_text`. That is Qwen3.8's internal identifier.

</details>

### Standalone LoRA

[`lora/Qwen3.8-27B-Humanlike-Chat-2.0-LoRA-r320-F16.gguf`](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF/resolve/main/lora/Qwen3.8-27B-Humanlike-Chat-2.0-LoRA-r320-F16.gguf) (4.67 GB) is all of 2.0 as one rank-320 GGUF LoRA for llama.cpp: the voice LoRA at 0.4 plus the 2.0 LoRA.

```bash
llama-server -m YOUR-Huihui-Qwen3.8-27B-abliterated.gguf \
  --lora Qwen3.8-27B-Humanlike-Chat-2.0-LoRA-r320-F16.gguf \
  --jinja \
  --ctx-size 32768 --parallel 1 --n-gpu-layers 99 \
  --temp 1.0 --top-p 0.95 --top-k 20
```

- `--lora` applies it at scale 1.0, which is the right strength.
- Apply it only to an unadapted, text-only GGUF of the Huihui base, never to the merged files here. They already contain it.
- For 4-bit, use the merged IQ4_XS or Q4_K_M. Those are the tested path.

## Custom finetunes

I take commissions. If you want a model that sounds like a specific character, your product, or your own texting style, or a smaller model that knows your domain, I can build it the way I built this one: data, training, evals against the base, and GGUF files you can run or a hosted endpoint.

Good fits:

- game characters and companions that stay in character
- a brand or support voice that doesn't sound like a support bot
- agents that talk like a colleague
- a model trained on your own chats
- distillation: a big model's behaviour moved into a smaller, cheaper one you can run yourself
- domain expertise distillation: a model that knows your field (legal, medical, support, your codebase) without calling a frontier API
- use-case specific finetunes: one job done reliably, like your tool calls, your output format or your workflow

DM [**codebottle** on Discord](https://discord.com/users/320486798859960322). Tell me what you're building and what it should sound like.

Found a chat where it slips? Tell me in the [Community tab](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF/discussions) or on [Discord](https://discord.gg/jWbqEqsgAf).

## License

Apache-2.0, inherited from the upstream Qwen and Huihui releases.

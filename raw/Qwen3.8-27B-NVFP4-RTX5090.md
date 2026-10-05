---
license: apache-2.0
base_model: Qwen/Qwen3.8-27B
pretty_name: RTX5090 Blackwell GPU Optimized Qwen-3.8-27B-NVFP4
library_name: transformers
pipeline_tag: image-text-to-text
tags:
  - nvfp4
  - modelopt
  - nvidia
  - rtx-5090
  - blackwell
  - quantization
  - qwen3.8
  - sparkinfer
  - sglang
  - vllm
---

# RTX5090 Blackwell GPU Optimized Qwen-3.8-27B-NVFP4

<p align="center">
  <img src="assets/rtx5090-hero-engines.png" alt="One RTX 5090, three ways to serve it, one NVFP4 build to beat. Decode on one stream: SparkInfer + DSpark 264.8 tok/s (bench harness, up to 420 on code), SGLang + DSpark 161.7, SparkInfer 92.9, SGLang 85.8, Unsloth NVFP4 on vLLM 42.4. Max context on 32 GB: SparkInfer 360,000 tokens, SGLang 320,960, vLLM 262,144, Unsloth NVFP4 on vLLM 77,184. Decode at 244K context: SparkInfer 90.3 tok/s, vLLM 63.5." width="100%"/>
</p>

Runs on **SparkInfer, SGLang and vLLM** unmodified — configs for all three are [below](#serving).
Serving many users at once? See [concurrency](#serving-more-than-one-user).

## 420 tok/s writing code. One consumer GPU.

<p align="center">
  <img src="assets/rtx5090-hero-final.png" alt="Qwen3.8-27B NVFP4 optimized for RTX 5090: 420 tok/s writing code (4.3x), 296 JSON, 276 math, 174 chat against a 97 tok/s no-speculation baseline; 256k context on a single card — SparkInfer x NVFP4 build x DSpark v2" width="100%"/>
</p>

**SparkInfer × this NVFP4 build × the DSpark v2 drafter** — an engine, a checkpoint, and a speculative drafter optimized against each other, compounding to **4.3×**. The drafter never changes what the model says: the target verifies every drafted token.

**GeForce RTX 5090–specific** NVFP4 checkpoint of [`Qwen/Qwen3.8-27B`](https://huggingface.co/Qwen/Qwen3.8-27B), quantized with [NVIDIA Model Optimizer](https://github.com/NVIDIA/Model-Optimizer). Serves the **full native 262,144-token context** on 32 GB.

With the [DSpark v2 drafter](https://huggingface.co/gittensor-model-hub/Qwen3.8-27B-DSpark-NVFP4): **264.8 tok/s overall — up to 420 on code — on [SparkInfer](https://github.com/gittensor-ai-lab/sparkinfer)** (its bench harness; the HTTP server is autoregressive-only today) and **161.7 tok/s on SGLang's OpenAI server**. Without speculation: 92.9 tok/s SparkInfer · 85.8 SGLang.

**This is the final build.** Everything is quantized down to the `lm_head`, the unused MTP head is **removed from the weights**, and the file ships as two shards:

| | |
| --- | --- |
| Checkpoint | **17.92 GB**, 2 shards (was 18.77 GB / 3 shards) |
| `lm_head` | **NVFP4** — the last big BF16 block on the per-token path |
| MTP head | **removed** — dead weight once you use the DSpark drafter |
| Serving | SparkInfer · SGLang (+DSpark) · vLLM |
| Speculation | **1.89×** on SGLang's server · **2.73×** in SparkInfer's bench harness |

Blackwell tensor cores only. Hopper can load the files but cannot run NVFP4.

---

## Quick start — one `docker run`

[**SparkInfer**](https://github.com/gittensor-ai-lab/sparkinfer) is a zero-dependency C++/CUDA
engine for Blackwell. The image is prebuilt and published to GHCR — no compiler, no CUDA toolkit,
no Python stack:

```bash
docker run --gpus all -p 8080:8080 -v qwen38:/models \
  ghcr.io/gittensor-ai-lab/sparkinfer-qwen38:latest
```

**These weights download themselves on first run** into the `qwen38` volume (~18 GB, cached after),
so that one command is the whole setup. The server is ready in about 10 s on later starts.

```bash
curl localhost:8080/v1/chat/completions -H 'Content-Type: application/json' -d '{
  "model": "qwen38-nvfp4",
  "messages": [{"role": "user", "content": "What is the capital of Japan?"}],
  "chat_template_kwargs": {"enable_thinking": false}
}'
```

Serves **text, images and video** through the same OpenAI-compatible API. ~1 GB image, Blackwell
(`sm_120`) only. One caveat if you wire this into an agent framework: `/v1/models` currently
advertises `input_modalities` as text and image only, so a client that routes on that field will
not offer video even though `video_url` parts work — send video explicitly for now
([sparkinfer#983](https://github.com/gittensor-ai-lab/sparkinfer/issues/983)).
Provenance is attested to the image digest:

```bash
gh attestation verify oci://ghcr.io/gittensor-ai-lab/sparkinfer-qwen38:latest \
  -R gittensor-ai-lab/sparkinfer
```

### Tuning

Defaults are the values measured as correct on a 32 GB card, so the two easy mistakes are
pre-solved. Override any of them with `-e`:

| var | default | notes |
| --- | --- | --- |
| `CTX` | `262144` | the full native window, 27.9 GB. **360,000 is the ceiling** on 32 GB (31.2 GB, decode drops to ~74 tok/s) |
| `SPARKINFER_MAX_OUTPUT_TOKENS` | `16384` | the engine's own default is 4096 |
| `MODEL_DIR` | `/models/qwen38-nvfp4` | point at existing weights to skip the download |
| `MODEL_NAME` / `PORT` | `qwen38-nvfp4` / `8080` | |
| `SPARKINFER_SERVER_PREFIX_TOKEN_FILE` | — | file of token ids kept warm across requests — see [repeated long prefixes](#repeated-long-prefixes-19) |

The output cap reserves context per request, so raising it without also raising `CTX` makes
concurrent requests fail with *server overloaded*. The NVFP4 `lm_head` loads natively — nothing
needs converting.

### Speculative decode benchmark

The same image runs the DSpark benchmark, fetching the drafter on first use:

```bash
docker run --rm --gpus all --ipc=host -v qwen38:/models \
  ghcr.io/gittensor-ai-lab/sparkinfer-qwen38:latest bench code
```

### Building from source instead

```bash
git clone https://github.com/gittensor-ai-lab/sparkinfer && cd sparkinfer
cmake -B build -DCMAKE_CUDA_ARCHITECTURES=120 -DBUILD_SERVER=ON && cmake --build build -j
./build/server/sparkinfer_server -m <weights> --tokenizer <weights>/tokenizer.json \
  --ctx 262144 --host 0.0.0.0 --port 8080
```

Needs CUDA 12.8+ and rustc ≥ 1.79.

---

## Performance

<p align="center">
  <img src="assets/rtx5090-engines.png" alt="One RTX 5090: per workload and overall — SparkInfer 92.9 and SGLang 85.8 tok/s without speculation, SGLang + DSpark 161.7, SparkInfer + DSpark 264.8 (bench harness, up to 420 on code); DSpark speedup 2.73x on SparkInfer, 1.89x on SGLang" width="100%"/>
</p>

<p align="center">
  <img src="assets/rtx5090-context-vs.png" alt="Max context on one RTX 5090: this build 360,000 on SparkInfer and 320,960 on SGLang vs RadixArk 225,600, Unsloth 77,184, RadixArk with drafter 37,900" width="100%"/>
</p>

### Engines, same weights, identical prompts

| Stack | Decode | Max context on 32 GB |
| --- | --- | --- |
| **SparkInfer** (no speculation) | **92.9 tok/s** | **360,000 tokens** — 1.37× the native window |
| SGLang (no speculation) | 85.8 tok/s | 320,960 tokens — full window with 59K to spare |
| **SGLang + [DSpark v2](https://huggingface.co/gittensor-model-hub/Qwen3.8-27B-DSpark-NVFP4)** | **161.7 tok/s** | 165,169 tokens |

24 prompts across four workloads (chat, code, math, JSON), 256 max tokens, `temperature=0`, thinking off, sequential, through each engine's OpenAI API, every row measured at `--ctx 262144`. SGLang 0.5.18 with FP8 KV; SparkInfer v0.5.5 with its default int8 KV.

SparkInfer is both the faster engine without speculation and the one that holds the most context: 262,144 tokens costs it 27.9 GB, and it still answers at `--ctx 360000` (31.2 GB), though decode falls to ~74 tok/s at that extreme.

### Measured against the other NVFP4 builds of this model

<p align="center">
  <img src="assets/rtx5090-vs-competitors.png" alt="Three published NVFP4 builds of Qwen3.8-27B measured on one RTX 5090. Accuracy over 328 items: QUASAR 80.2%, this build 79.0%, NVIDIA 78.7%, 95% intervals overlapping. AA-LCR long-context reasoning: 55 of 100 for all three. Decode: this build 86.8 tok/s, QUASAR 78.5, NVIDIA 69.5. KV tokens at 131,072 context: this build 300,009, QUASAR 249,036, NVIDIA 209,715." width="100%"/>
</p>

Three published NVFP4 checkpoints of Qwen3.8-27B, run on **one RTX 5090** — same engine (vLLM),
same session, same sampling (the model's own `generation_config`: temp 1.0, top_k 20, top_p 0.95),
same 32,768-token budget.

| | **This build** | [QUASAR](https://huggingface.co/QUASAR-QAT/Qwen3.8-27B-QUASAR-NVFP4) | [NVIDIA](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4) |
| --- | ---: | ---: | ---: |
| GPQA Diamond (198) | 76.3% | **78.8%** | 76.8% |
| AIME 2025 (30) | 76.7% | 76.7% | 76.7% |
| MMLU-Pro (100) | **85.0%** | 84.0% | 83.0% |
| **Overall (328)** | **79.0%** | 80.2% | 78.7% |
| 95% CI | [74.2–83.0] | [75.5–84.1] | [73.9–82.7] |
| **AA-LCR** (100 q @ ~95K tok) | **55** | 55 | 55 |
| **Decode** | **86.8 tok/s** | 78.5 | 69.5 |
| **KV @ 131,072 ctx** | **300,009** | 249,036 | 209,715 |
| Checkpoint | **17.92 GB** | 19.7 GB | 21.0 GB |

**Quality is a tie; the difference is what the weights leave room for.** All three confidence
intervals overlap, truncation was comparable (41 / 45 / 42), and long-context reasoning is a dead
heat. This build is **24.9% faster with 43% more context** than NVIDIA's official checkpoint.

The reason is allocation, not luck. NVIDIA keeps self-attention and Gated-DeltaNet at **FP8** —
22% of the linear weight — which costs both decode bandwidth and KV headroom on this card; their
card targets **GB300**, where FP8 sits much closer to FP4 in relative cost. QUASAR keeps `lm_head`
in BF16 (2.54 GB against our 0.71 GB), read on every token. We quantize both, and spend the
difference on context.

Measured on the same box: leaving NVFP4 for the next instruction tier costs **1.5–2.1×** on these
GEMM shapes, so precision spent elsewhere is expensive here.

> Two caveats. Published BF16 references disagree across harnesses (NVIDIA reports 88.92 on GPQA
> Diamond, QUASAR 91.41, for the same weights) — so only the same-harness numbers above should be
> compared with each other, never against a published leaderboard. AA-LCR here is scored with a
> deterministic salient-token proxy applied identically to all three, not Artificial Analysis'
> LLM judge; it ranks these builds but is not comparable to their published figures.

### Serving more than one user

Every figure above is a single stream. Under concurrent load SparkInfer v0.5.5 decodes the whole
batch in one packed forward — earlier versions time-sliced one sequence at a time and stayed flat
at ~77 tok/s no matter how many clients arrived.

| Concurrent requests | 1 | 2 | 4 | 8 | 16 | 32 |
| --- | --- | --- | --- | --- | --- | --- |
| **Aggregate tok/s** | 88.9 | 162.1 | 249.6 | **344.3** | **345.1** | 318.2 |
| Per request | 88.9 | 81.1 | 63.0 | 43.7 | 22.0 | 13.4 |

Distinct prompts per request so no cache flatters the result, 128 tokens each, `--ctx 40960`,
measured client-side over the streaming API. 32/32 requests succeeded at every level. Aggregate
throughput peaks around 8–16 concurrent and is flat to 32; per-request latency degrades from
there, so 8 is the sweet spot on one card.

**Where this loses.** vLLM 0.28 on the same weights, same box, same harness: 134.5 / 266.6 /
545.8 / 546.6 tok/s at 2 / 4 / 8 / 16. We lead at 2 concurrent and trail by about 1.6× at 8–16.
If you are serving many simultaneous users, vLLM is still the faster server; if you are serving
one stream, or a few, SparkInfer is the faster engine and holds far more context.

### Repeated long prefixes: ~19×

A configured prefix — a long system prompt, a document, a tool manifest — is kept across requests
instead of being re-prefilled. With a 32,022-token shared prefix:

| Request | Wall clock |
| --- | --- |
| 1 (cold) | 5.75 s |
| 2 | **0.30 s** |
| 3 | **0.30 s** |

Change one word of the prefix and the next request costs 3.30 s again, which is what makes the
speedup attributable to the cache rather than to warm-up. For "load a document, ask ten questions",
or agentic traffic that repeats a system prompt and tool definitions on every call, this outweighs
any decode difference on this page.

This is a **configured** prefix (`SPARKINFER_SERVER_PREFIX_TOKEN_FILE`, a file of token ids), not
automatic caching over whatever prefix your requests happen to share, and it engages on sequential
requests rather than under concurrency.

### SparkInfer + DSpark: 2.73× in the bench harness

SparkInfer's DSpark path exists in its **bench harness**, not yet in the HTTP server — so it is not something you can `curl` today, but it does show what the engine and this drafter do together. Measured on the same checkpoint and the same [DSpark v2 drafter](https://huggingface.co/gittensor-model-hub/Qwen3.8-27B-DSpark-NVFP4), 256 tokens per workload, greedy:

| Workload | Autoregressive | + DSpark | Speedup | Accept τ |
| --- | --- | --- | --- | --- |
| Chat | 96.7 tok/s | 174.4 tok/s | 1.80× | 2.32 |
| Code | 97.2 tok/s | **420.2 tok/s** | **4.32×** | **6.78** |
| Math | 96.6 tok/s | 276.5 tok/s | 2.86× | 4.36 |
| JSON | 97.8 tok/s | 296.4 tok/s | 3.03× | 4.60 |
| **Overall** | **97.1 tok/s** | **264.8 tok/s** | **2.73×** | — |

Against SGLang's **1.89×** on the same drafter, this is the larger speculation gain — the block drafter feeds a verifier that keeps up with it. Code accepts nearly the whole 8-token block (τ 6.78 of a possible 8).

**Read these as their own harness, not as server numbers.** The bench runs at a few hundred tokens of context, where its autoregressive baseline is 97.1 tok/s against the server's 92.9, and it uses one prompt per workload rather than the server benchmark's six. What transfers is the ratio, not the absolute tok/s.

Speculation is lossless by construction — the target verifies every drafted token — and 9 of 12 bench runs came back token-identical to their autoregressive baseline. The three that differed diverged at a single token and then followed a different but valid continuation, which is what a near-tie in the target's own logits looks like when the verify step uses a different GEMM shape than single-token decode.

If you want speculation over HTTP today, serve with SGLang.

### Against the other NVFP4 builds on the same GPU

| | **This build** | [RadixArk DSpark](https://huggingface.co/RadixArk/Qwen3.8-27B-DSpark) | [Unsloth NVFP4](https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4) |
| --- | --- | --- | --- |
| Max context, SGLang | **320,960** ✅ | 225,600 ❌ | 77,184 ❌ (vLLM) |
| Max context, SparkInfer | **360,000** ✅ | **does not load** | not tested |
| Holds the full native window | **yes** | no | no |
| Decode, no speculation | **85.8** SGLang · **92.9** SparkInfer | 73.7 tok/s | 42.4 tok/s |
| Decode + its own drafter | **161.7 tok/s** | 148.0 tok/s | — |
| Max context with speculation | **165,169** | 37,900 | — |

This build and RadixArk were measured here back to back on identical SGLang flags (FP8 KV, `--mm-feature-transport cpu`, 2 running requests), both at `--ctx 262144`. Unsloth's figures are the earlier vLLM measurement on the same GPU — a different engine, included for scale.

Two gaps stand out. RadixArk's drafter is BF16 (3.5 GB against our 1.41 GB), and its draft KV pool is sized to the full target context, so turning speculation on costs it most of its window: **37,900 tokens left**, where ours keeps 165,169. And RadixArk **does not load on SparkInfer at all** — its Gated-DeltaNet projections (`linear_attn.in_proj_qkv`, `in_proj_z`, `out_proj`) are rejected by the compressed-tensors loader as malformed FP8. This checkpoint runs on all three engines unmodified.

---

## Accuracy

Quantizing the `lm_head` and dropping the MTP head did not move quality. On a matched 60-item smoke (GPQA Diamond, AIME 2025, MMLU-Pro — 20 items each, thinking on, `temperature=1.0`, seed 20260815):

| Stack | Score |
| --- | --- |
| SparkInfer | 41/60 (16k output budget) |
| SGLang | 40/60 (24k output budget) |

The two engines agree on the weights. The budgets differ because SparkInfer caps output per request, so read this as *same weights, same accuracy* — not as an engine ranking. Both runs carry 6–9 length truncations per task, where thinking filled the budget before an answer appeared.

For a like-for-like comparison against Unsloth NVFP4, the earlier vLLM measurement on the previous build of this checkpoint stands at **45/60 (75%) for both**: GPQA 13/20 vs 14/20, AIME 15/20 vs 14/20, MMLU-Pro 17/20 tied.

**These are 20-item smokes, not published benchmark scores.** Do not cite them as GPQA / AIME / MMLU-Pro results.

---

## Serving

### SGLang — with speculation (fastest)

```bash
docker run -d --name sgl --gpus all --ipc=host --shm-size 32g -p 30000:30000 \
  -v hf_cache:/root/.cache/huggingface \
  lmsysorg/sglang:latest \
  sglang serve \
    --model-path gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090 \
    --trust-remote-code --tp-size 1 \
    --context-length 262144 \
    --kv-cache-dtype fp8_e4m3 \
    --attention-backend flashinfer \
    --chunked-prefill-size 2048 \
    --mamba-radix-cache-strategy extra_buffer_lazy \
    --mamba-ssm-dtype bfloat16 \
    --mem-fraction-static 0.90 \
    --max-running-requests 2 \
    --max-mamba-cache-size 12 \
    --speculative-algorithm DSPARK \
    --speculative-draft-model-path gittensor-model-hub/Qwen3.8-27B-DSpark-NVFP4 \
    --speculative-dspark-block-size 7 \
    --speculative-draft-model-quantization modelopt_fp4 \
    --reasoning-parser qwen3 \
    --tool-call-parser qwen3_coder \
    --host 0.0.0.0 --port 30000
```

Drop the four `--speculative-*` lines for the maximum-context profile.

Two flags that are easy to get wrong:

- **`--speculative-draft-model-quantization modelopt_fp4`** is required. Without it SGLang assumes BF16 and mis-loads the packed U8 tensors.
- **`--max-mamba-cache-size`** must leave headroom. Under DSpark each request takes **4** Gated-DeltaNet state slots, so size 4 provisions exactly one request with nothing spare and eviction can fail with `AssertionError: Can not alloc mamba cache`. Rule of thumb: **≥ 4 × `--max-running-requests` + 4**.

### vLLM

```bash
vllm serve gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090 \
  --quantization modelopt \
  --kv-cache-dtype fp8 \
  --trust-remote-code \
  --max-model-len 262144 \
  --max-num-seqs 16 \
  --gpu-memory-utilization 0.97 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml
```

vLLM **0.27.x**. First boot JITs the FlashInfer SM120 FP4 GEMM (`nvcc` + CUDA 13 headers); limit parallel JIT on smaller host RAM with `MAX_JOBS=2`. Util **0.97** is required for native 256k on 32 GB — 0.90 only holds ~205k KV.

Qwen3.8 is a thinking model; for short answers pass `"chat_template_kwargs": {"enable_thinking": false}`.

---

## Chat template

Qwen3.8's own template, with agentic fixes. It renders **byte-identical to upstream `Qwen/Qwen3.8-27B` on every non-tool path**, so ordinary chat, thinking and vision behave exactly as the base model does.

### Reasoning effort

`xhigh` (default), `medium`, `low` — invalid values raise:

```json
{"chat_template_kwargs": {"reasoning_effort": "medium"}}
```

On this checkpoint **`xhigh` is the cheapest setting at equal accuracy.** It reasons more directly rather than simply longer:

| Effort | Correct | Avg output tokens |
| --- | --- | --- |
| **xhigh** (default) | 12/12 | **245** |
| medium | 12/12 | 584 |
| low | 12/12 | 579 |

12 verifiable problems, `temperature=0`, 3k budget, no truncations. A harder 10-problem set held the same ordering (562 vs 939 tokens). Keep the default unless you have a specific reason not to.

### Tool calling

XML by default, matching the `qwen3_xml` (vLLM) and `qwen3_coder` (SGLang) parsers:

```text
<tool_call>
<function=get_weather>
<parameter=city>
Paris
</parameter>
</function>
</tool_call>
```

Assistant `tool_calls` replayed from an OpenAI-style response render whether `function.arguments` is a **dict or a JSON string**. The string form previously raised `TypeError: Can only get item pairs from a mapping` on the second turn of an agentic loop, which broke direct `apply_chat_template`, llama.cpp and LM Studio users. Server-side tool calling was never affected — SGLang and vLLM normalize arguments to a dict before rendering.

### Template kwargs

| Kwarg | Default | Effect |
| --- | --- | --- |
| `reasoning_effort` | `xhigh` | `xhigh` / `medium` / `low` |
| `enable_thinking` | `true` | `false` emits a closed, empty think block |
| `preserve_thinking` | `true` | keeps reasoning in history; `false` is prefix-cache safe |
| `tool_call_format` | `xml` | `json` switches to `{"name": ..., "arguments": {...}}` |
| `continue_final_message` | `false` | prefills the final assistant turn; takes precedence over `add_generation_prompt` |
| `auto_disable_thinking_with_tools` | `false` | turns thinking off when tools are present |
| `max_tool_arg_chars` / `max_tool_response_chars` | `0` | opt-in truncation, off by default |

`system` and `developer` roles are both accepted, and consecutive tool responses are grouped into a single turn.

**Validation.** Agent correctness 8/8 (tool selection, argument accuracy, parallel calls, no-tool restraint, synthesis, multi-step, failure recovery, tools with thinking off); 240 held-out conversations render clean across four configurations; multi-turn prompts are token-level prefix-stable, so KV cache reuse holds across turns; and a paired A/B against the previous template left DSpark acceptance unchanged to slightly better.

Template contributions from [@TheChola](https://huggingface.co/TheChola).

---

## Speculative decoding

A DSpark drafter **trained and quantized specifically against this NVFP4 checkpoint** ships alongside it:

- 🚀 [**`Qwen3.8-27B-DSpark-NVFP4`**](https://huggingface.co/gittensor-model-hub/Qwen3.8-27B-DSpark-NVFP4) — recommended, 1.41 GB
- [`Qwen3.8-27B-NVFP4-RTX5090-DSpark`](https://huggingface.co/gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090-DSpark) — BF16 source, 2.72 GB

<img src="assets/rtx5090-speculation.png" alt="Speculative decoding: 88.5 to 180.3 tok/s across six profiles; acceptance per workload, agentic tool calling +17.9%" width="100%"/>

### Measured on 240 held-out prompts, identical across every profile

| Profile | Decode | Accept length | Drafter | vs no-spec |
| --- | --- | --- | --- | --- |
| No speculation | 88.45 tok/s | — | — | 1.00× |
| Built-in MTP head | 136.90 tok/s | 2.758 | 5.53 GB | 1.68× |
| Stock [RadixArk DSpark](https://huggingface.co/RadixArk/Qwen3.8-27B-DSpark) (FP8-trained) | 139.35 tok/s | 2.421 | 2.72 GB | 1.71× |
| Ours — DSpark BF16 | 141.99 tok/s | 2.717 | 2.72 GB | 1.74× |
| Ours — DSpark NVFP4 (v1) | 150.74 tok/s | 2.761 | 1.41 GB | 1.85× |
| **Ours — DSpark NVFP4 (v2)** | **180.30 tok/s** | **2.904** | **1.41 GB** | **2.04×** |

**+31.7% throughput over the built-in MTP head while using a quarter of its memory**, and +29.3% over the stock DSpark drafter it was adapted from — which is why the MTP head is now deleted from the weights entirely.

This table uses the 240-prompt held-out harness (longer outputs, its own settings). It is **not** comparable to the 92.9 / 85.8 / 161.7 figures at the top, which come from the 24-prompt cross-engine harness; each set is internally consistent.

The v2 drafter is retrained on a corpus rendered exactly as the model is served — XML tool calls with a real tools array, think blocks and the reasoning-effort preamble present — closing a train/serve mismatch that had cost the most on agentic traffic.

### Per domain

Acceptance measured per request with the prefix cache flushed between requests, from cumulative verify counters rather than a sampled gauge.

| Domain | v1 drafter | **current** | Δ |
| --- | --- | --- | --- |
| Math | 3.810 | **4.496** | +18.0% |
| Coding | 3.729 | **3.864** | +3.6% |
| JSON / structured output | 3.328 | **3.543** | +6.5% |
| Chat | 2.305 | **2.363** | +2.5% |
| Long-context | 2.484 | 2.474 | −0.4% |
| Instruction | 2.195 | **2.329** | +6.1% |
| **Overall** | **2.761** | **2.904** | **+5.2%** |

Structured output sustains longer accepted blocks than open-ended prose: predictable token streams are easier to draft. Long-context is the one regression — the training corpus caps sequences at 2,048 tokens, so it was never well represented.

**Agentic tool calling.** The "JSON / structured output" row is schema-constrained generation — those prompts declare no tools and contain no `<tool_call>` blocks, so they do not measure agentic tool use. Measured separately on 60 purpose-built agentic scenarios across 10 tool schemas:

| Agentic phase | v1 drafter | **current** | Δ |
| --- | --- | --- | --- |
| Parallel calls | 4.169 | **5.199** | +24.7% |
| Initial call | 3.683 | **4.692** | +27.4% |
| After a tool result | 3.524 | **3.910** | +11.0% |
| Second call in a loop | 3.155 | **3.787** | +20.0% |
| Error recovery | 3.028 | **3.630** | +19.9% |
| Two-step chain | 2.605 | **2.749** | +5.5% |
| **Overall** | **3.299** | **3.891** | **+17.9%** |

Tool-call syntax is predictable, so emitting several calls at once accepts longest; multi-step chains accept least, since each new tool boundary is a fresh decision point. Tool-call emission rate is unchanged (38/60 for both), so this is an acceptance gain, not a change in behaviour.

**Output quality is unchanged.** The target verifies every drafted token under strict acceptance, so speculation changes speed, not outputs.

### Choosing a profile

| | **With the drafter** | **This checkpoint alone** |
| --- | --- | --- |
| Max context | 165,169 tokens | **320,960** on SGLang · **360,000** on SparkInfer |
| Decode | **161.7 tok/s** | 85.8 tok/s SGLang · 92.9 SparkInfer |

On one 32 GB card you can have the full 262K window **or** ~1.9× decode. Speculation accelerates **decode only, never prefill** — cold TTFT at 250K is ~121 s either way.

---

## Why `lm_head` is NVFP4, and why MTP is gone

At concurrency 1 this model is **weight-bandwidth bound, not compute bound**. An earlier build streamed 18.80 GiB of weights per token at 81.6 tok/s — a **1.65 TB/s** read rate against the RTX 5090's 1.79 TB/s spec, about **92% of peak**. Decode reads the whole model once per token, so bytes removed convert almost linearly into tokens per second.

`lm_head` is a full-vocabulary (248,320 × 5,120) GEMM evaluated on **every** token — 2.54 GB of that read in BF16, 0.72 GB in NVFP4. It was the only large BF16 block left on the per-token critical path. Embeddings are the same size but are a *gather* (~10 KB/token), so quantizing them saves capacity, not speed.

| | earlier build | with NVFP4 `lm_head` | **final (MTP removed)** |
| --- | --- | --- | --- |
| Checkpoint | 20.59 GB | 18.77 GB | **17.92 GB** |
| Shards | 3 | 3 | **2** |
| Decode, no speculation | 81.6 tok/s | 88.45 tok/s | see above |

The bandwidth model predicted 89.7 tok/s for the NVFP4-`lm_head` build; measured 88.45 — within 1.4%.

The MTP head was ~0.85 GB of tensors that no supported serving path uses once the DSpark drafter is in play, and the drafter beats MTP by 31.7% on a quarter of the memory. Removing it shrinks the download and the load-time footprint without touching a single computed value.

The previous builds are preserved on branches: [`pre-final`](https://huggingface.co/gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090/tree/pre-final) (NVFP4 `lm_head`, MTP still present) and [`pre-lmhead4`](https://huggingface.co/gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090/tree/pre-lmhead4) (BF16 `lm_head`).

> The standalone [`-No-MTP`](https://huggingface.co/gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090-No-MTP) and [`-LMHead4`](https://huggingface.co/gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090-LMHead4) variants are **superseded** — this repo now is both.

---

## Recipe (NVIDIA ModelOpt)

| Item | Value |
| --- | --- |
| Tool | [NVIDIA Model Optimizer](https://github.com/NVIDIA/Model-Optimizer) git `c4129b6` (`quant_method: modelopt`) |
| Weights / activations | NVFP4 W4A4, group size 16 |
| KV cache | FP8 (`fp8_cast` at PTQ; serve with `--kv-cache-dtype fp8`) |
| Calibration | 128 image-text samples (`--calib_with_images`) |

NVFP4: MLP, `lm_head`, and the remaining Linear layers. Left in **BF16** on purpose: vision tower, embeddings, and the Gated-DeltaNet `conv1d` / `in_proj_a` / `in_proj_b`. The MTP head is not quantized because it is not present.

Note for tooling authors: excluded modules must be listed in **two** places — `hf_quant_config.json` (`exclude_modules`) and `config.json` (`quantization_config.ignore`). Missing the second one is what produces `Parameter lm_head.input_scale not found` at load.

---

## License

Apache 2.0, same as the Qwen3.8-27B base model.

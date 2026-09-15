---
title: "vLLM vs SGLang: Performance, Features & Deployment Compared"
author: "DeepInfra"
site: "DeepInfra"
source: "https://deepinfra.com/blog/vllm-vs-sglang"
domain: "deepinfra.com"
language: "en"
description: "Compare vLLM and SGLang across performance, latency, throughput, features, and deployment. Find out which LLM inference engine is the better choice for your production workloads."
word_count: 2130
---

DeepInfra raises $107M Series B to scale the inference cloud — [read the announcement](https://deepinfra.com/series-b)

Somebody on your team read a benchmark post, and now there’s a ticket to migrate the inference stack.

That’s how most vLLM vs SGLang decisions start. A published test reports a 29 percent throughput gap, the number lands in Slack, and two weeks later you’re debugging kernel version conflicts at midnight while p99 latency sits exactly where it was. The benchmark was probably honest. It measured a workload that had nothing to do with yours.

Both engines are good. vLLM and SGLang have leapfrogged each other for two years, and whichever leads this month tends to trade places by the next minor release. Picking on a leaderboard delta means picking on noise.

There’s also a prior question almost nobody puts in the flowchart. Choosing between these two is a self-hosting decision before it’s an engine decision. You’re signing up for GPU capacity planning, upgrade churn, cold starts, quantization debugging, and a pager rotation. That bill arrives whether or not you picked the faster attention kernel.

## Why Most vLLM vs SGLang Benchmarks Cannot Answer Your Question

Start with the most-cited number in the argument. AI Multiple’s engine comparison [measured SGLang at 16,215 tok/s against vLLM at 12,553 tok/s](https://aimultiple.com/inference-engines) on a single H100 80GB serving [Llama 3.1 8B](https://deepinfra.com/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo) in bf16, across 1,000 prompts run ten times. That 29 percent gap drives most migration tickets.

Then read the config. The published setup pairs SGLang v0.2.3 with vLLM 0.11.0, releases roughly two years apart. A number produced that way can’t tell you which engine is faster today, in either direction. Check any head-to-head for contemporaneous releases and matched flags before acting on it. The same writeup notes that GPU memory utilization of 0.95 crashed while 0.8 worked, a tuning artifact rather than a property of an engine.

The second trap is unit conflation. RunPod’s [KV cache reuse tests](https://www.runpod.io/blog/sglang-vs-vllm-kv-cache) report SGLang at 35.0 tok/s against vLLM at 32.8 tok/s on 2x H100 with a 70B distill at 7k context. Those are single-stream decode rates for one user. AI Multiple’s 16,215 tok/s is aggregate server throughput across a saturated batch. Both get labeled “tokens per second” and they answer different questions. One predicts how fast text appears for a single reader. The other predicts how many concurrent sessions a node absorbs before requests queue. Optimizing a chat UI? The aggregate number is close to irrelevant, and our breakdown of [the KPIs that actually describe an inference endpoint](https://deepinfra.com/blog/llm-api-provider-performance-kpis-101) beats any leaderboard.

A benchmark is usable only when it’s version-matched, flag-matched, and run against your request distribution. Almost none are.

## What Each Engine Is Actually Optimized For

vLLM introduced PagedAttention, which treats KV cache like virtual memory: fixed-size blocks, an indirection table, near-zero fragmentation. The idea won so completely it’s table stakes everywhere now, SGLang included. vLLM’s recent work moved up the stack to scheduling overhead. Its V1 architecture splits the client layer from the GPU execution loop into separate processes talking over ZMQ, so Python-side scheduling stops eating decode time at high concurrency. [Release v0.25.0](https://github.com/vllm-project/vllm/releases/tag/v0.25.0) made Model Runner V2 the default for all dense models and deleted the legacy PagedAttention implementation. That tells you where the project’s center of gravity sits.

SGLang started from the prompt-structure side. RadixAttention maintains a radix tree over cached KV blocks, so shared prefixes get matched and reused across requests automatically, with nothing declared cacheable in advance. vLLM’s automatic prefix caching is closer to a hash-block lookup. The radix tree handles partial and branching overlap, the exact shape of agent traces and multi-turn conversations. The [zero-overhead batch scheduler](https://www.lmsys.org/blog/2024-12-04-sglang-v0-4/) landed in v0.4 for roughly 1.1x throughput by overlapping CPU scheduling with GPU compute.

|  | **vLLM** | **SGLang** |
| --- | --- | --- |
| **Origin optimization** | KV cache paging (PagedAttention) | Prefix reuse (RadixAttention) |
| **Scheduler focus** | Process-split V1 loop, Model Runner V2 | CPU scheduling overlapped with GPU compute |
| **Release on July 14, 2026** | [v0.25.1](https://github.com/vllm-project/vllm/releases) | [v0.5.15.post1](https://github.com/sgl-project/sglang/releases) |
| **GitHub stars** | [86,819](https://github.com/vllm-project/vllm) | [30,590](https://github.com/sgl-project/sglang) |
| **Leans toward** | Broad model and hardware coverage | Shared-prefix and structured workloads |

Feature matrices have converged hard. Both ship continuous batching, chunked prefill, speculative decoding, structured generation, FP8 and INT4 quantization, tensor parallelism, and multi-LoRA. Read the star gap as ecosystem reach rather than quality: vLLM’s larger contributor base means day-one support for new architectures and wider accelerator coverage.

## The Four Workload Signals That Decide It

Ignore the leaderboards and characterize your own traffic. Four properties do almost all the work.

**Prefix reuse ratio.** Take a day of production requests and compute what fraction of input tokens sit in a prefix shared with some other request. A coding agent replaying a 12k-token system prompt plus file context on every step can run above 80 percent shared. A summarizer hitting distinct documents runs near zero. High reuse is where RadixAttention’s dynamic tree earns its keep, and RunPod’s cached runs showed roughly a 20 percent gain once hits landed. Below about 20 percent reuse, this signal stops discriminating between the engines.

**Batch shape.** A saturated queue of offline work (bulk classification, eval sweeps, embedding backfills) is an aggregate throughput problem, and whichever engine packs more sequences per GPU wins outright. Bursty interactive traffic at low concurrency is a time to first token problem, where scheduler overhead and prefill chunking matter more than peak tokens per second. Most teams run both shapes and measure one.

**Structured output share.** When many calls use constrained decoding for JSON or a grammar, the constraint compiler sits on your critical path and compilation cost per unique schema becomes a real latency term. Teams with a few hot schemas feel this far less than teams generating schemas per request.

**Model topology.** A dense checkpoint like [Llama-3.3-70B-Instruct-Turbo](https://deepinfra.com/meta-llama/Llama-3.3-70B-Instruct-Turbo) shards predictably across tensor parallel ranks. Large MoE checkpoints like [DeepSeek-V3.2](https://deepinfra.com/deepseek-ai/DeepSeek-V3.2) and [Kimi K2.6](https://deepinfra.com/moonshotai/Kimi-K2.6) drag in expert parallelism, cross-node interconnect, and a much larger tuning surface. [Qwen3-30B-A3B](https://deepinfra.com/Qwen/Qwen3-30B-A3B) sits on a single node comfortably, and that choice moves your ops burden more than either engine does.

Running this comparison means you’ve committed to open weights. Usually right on price, and still worth re-checking against [how open and proprietary models compare on capability and cost](https://deepinfra.com/blog/open-vs-closed-source-ai-models).

## Measure Your Prefix Reuse Before You Pick

Measure prefix reuse first. It’s the one signal where the two engines genuinely diverge, and you can get a reading in an afternoon without provisioning a GPU. Point a streaming client at a hosted endpoint, send your real preamble twice, and time the first token both times.

```python
import os
import time
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPINFRA_API_TOKEN"],
    base_url="https://api.deepinfra.com/v1/openai",
)

MODEL = "deepseek-ai/DeepSeek-V3.2"

with open("system_prompt.txt") as handle:
    SHARED_PREFIX = handle.read()  # your real preamble, 8k+ tokens

def ttft(question: str) -> float:
    """Seconds until the first content token arrives."""
    start = time.perf_counter()
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SHARED_PREFIX},
            {"role": "user", "content": question},
        ],
        max_tokens=64,
        stream=True,
    )
    for chunk in stream:
        # the final chunk can arrive with choices == [], so check before indexing
        if chunk.choices and chunk.choices[0].delta.content:
            return time.perf_counter() - start
    return float("nan")

def warmup() -> None:
    """Open the TCP and TLS connection without seeding the shared prefix."""
    client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=1,
    )

warmup()  # otherwise the handshake lands inside your cold measurement

questions = ["Summarize the open tickets.", "List the failing tests.", "What changed in auth?"]
cold = ttft(questions[0])
warm = [ttft(q) for q in questions[1:]]

print(f"cold TTFT: .0
 ms")
print(f"warm TTFT: {sum(warm) / len(warm) * 1000:.0f} ms")copy
```

Read the delta, not the absolute numbers. A warm TTFT that collapses to a fraction of the cold one means reusable prefix dominates your prompt shape, and RadixAttention becomes a real differentiator if you self-host. A delta inside the noise means cache behavior decides nothing, so pick on model coverage and operational familiarity instead.

Three things confound the reading. A hosted endpoint load balances across replicas, so a warm call can land on a machine that never saw your prefix. Fire the warm requests back to back, repeat the loop five to ten times, take medians. Cache entries age out, so a long pause quietly resets you to cold. The subtle one is concurrency: prefix caching and active KV cache compete for the same HBM, and a prefix that stays resident at four concurrent requests gets evicted at two hundred. Measure at the concurrency you actually run, or you’ll buy an engine for a cache hit rate you never see in production.

That last effect is the sharpest argument for self-hosting. Eviction policy and memory split are yours to tune on your own hardware, opaque on someone else’s. Know what you trade away: we publish latency and throughput numbers across [nine providers serving DeepSeek V3.2](https://deepinfra.com/blog/deepseek-v3-2-api-benchmarks), and the spread is wide enough to swamp the engine delta.

## The Branch Missing From Every vLLM vs SGLang Flowchart

Every published vLLM vs SGLang comparison assumes you’ve already decided to run GPUs. Price that assumption before you accept it.

Serving a large MoE checkpoint like DeepSeek-V3.2 takes a multi-GPU node, call it eight H100-class cards. At a round $2 per GPU-hour on demand, substitute your own committed rate, that’s $16 per hour, or roughly $11,700 a month. The node bills whether it’s saturated or idle at 3am.

Now price the same workload against [DeepInfra’s rate for that exact model](https://deepinfra.com/deepseek-ai/DeepSeek-V3.2): $0.26 per 1M input tokens, $0.38 per 1M output, $0.13 per 1M cached input. Take a 4:1 input-to-output mix, so one unit is 1M input plus 250k output tokens, costing $0.355. That $11,700 covers roughly 33 billion input tokens and 8 billion output tokens a month. Treat those as estimates and redo them with your own rates.

Break-even means sustaining something like 12,000 input tokens per second, around the clock. Not peak. Sustained. Production traffic is diurnal and bursty, so real utilization lands closer to 10 or 20 percent and the rest of that $11,700 buys idle silicon. Cached pricing tilts it further for prefix-heavy workloads, the same reuse pattern that made you look at SGLang: our [DeepSeek V4 Pro pricing breakdown](https://deepinfra.com/blog/deepseek-v4-pro-pricing-guide-2026-providers-cost-analysis) prices cached tokens at $0.145 per 1M.

None of that counts the engineer-months. Someone tunes GPU memory utilization, chases kernel regressions across releases, handles cold starts and autoscaling, and carries the pager. An OpenAI-compatible endpoint collapses that to a base URL change, and swapping to [Kimi K2.6](https://deepinfra.com/moonshotai/Kimi-K2.6) becomes a string edit instead of a redeployment. We publish [TTFT and throughput numbers for Kimi K2.6](https://deepinfra.com/blog/kimi-k2-6-api-benchmarks-latency-throughput-cost) against the same targets you’d chase yourself.

## When Self-Hosting Still Wins

The economics flip in several situations. Pretending otherwise would be dishonest.

Sustained saturation is the obvious one. Push tens of billions of tokens a month at high utilization and owning the hardware beats renting it per token, which turns the engine question real again. Batch pipelines get there faster than interactive products, because you control the arrival rate and keep the queue full by design.

Regulatory placement is second. Some workloads can’t leave a jurisdiction or a VPC, and no pricing table changes that.

Then the modification case. Writing custom kernels, running speculative decoding with a draft model you trained, hot-swapping LoRA adapters per tenant, or serving an architecture that hasn’t landed upstream all put the engine in your hands. Here the choice sharpens: vLLM ships support for a brand new architecture sooner, while SGLang is easier to reason about when you’re modifying scheduling and cache behavior.

Plenty of teams take the middle path, self-hosting one saturated workload and routing the rest to an API, which keeps the fixed-cost node busy and the long tail elastic. Open weights make that split possible, and it pairs with the routing argument in our look at [the price gap between open and proprietary models](https://deepinfra.com/blog/open-source-vs-closed-source-ai-models-price-gap).

## Which Path to Choose

Run the framework in order and the answer usually falls out in a day.

- **Go with SGLang** if you measured high prefix reuse, run multi-turn conversations or agentic traffic against a stable preamble, lean on constrained decoding, and have someone who wants to own scheduling and cache behavior.
- **Go with vLLM** if you need broad model and accelerator coverage, want day-one support for new architectures, or run mixed traffic with no dominant cache pattern. Breadth is a real feature when your model roadmap is unsettled.
- **Go with a managed endpoint** if utilization is bursty, token volume sits below the break-even math, or your team’s time is better spent on the product than on kernel regressions. You can move later, since the same open weights run on your own hardware once volume justifies it.

Whatever you land on, measure your own workload first. The published benchmarks are measuring somebody else’s.

Browse the catalog and current pricing on [DeepInfra](https://deepinfra.com/models), or read the [API documentation](https://docs.deepinfra.com/) to see how little code an OpenAI-compatible migration takes. Benchmark numbers that disagree with ours are welcome: email [feedback@deepinfra.com](mailto:feedback@deepinfra.com), join the [DeepInfra Discord](https://discord.gg/deepinfra), or find us on X at [@DeepInfra](https://x.com/DeepInfra).

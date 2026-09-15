![Qwen3.8-Flash-Next](https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen3.8-Flash-Next/Qwen3.8-flash_banner_en.jpg#center)

Qwen3.8-Flash-Next

[HUGGING FACE](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) [MODELSCOPE](https://modelscope.cn/models/Qwen/Qwen3.8-Flash-Next) [TECH REPORT](https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf) [FLASHQLA](https://github.com/QwenLM/FlashQLA) [DISCORD](https://discord.gg/yPEP2vHTu4)

## Introduction

In this release we are opening the weights of **Qwen3.8-Flash-Next**, a multimodal MoE model that also serves as an early preview of the architecture used in **Qwen4**. It plays the same role that [Qwen3-Next](https://qwen.ai/blog?id=qwen3-next) played for Qwen3.5: the hybrid **Gated DeltaNet + Gated Attention** design introduced at that time has since been used across the Qwen3.5, Qwen3.6, Qwen3.7 and Qwen3.8 series. We are again releasing the architectural changes early, so that the community can examine them before the full Qwen4 model family is built on top of them.

Qwen3.8-Flash-Next upgrades the model systematically along four aspects — **attention, residual, embedding and optimization** — improving model capability while further optimizing computational efficiency, model capacity and training stability:

- **Attention**: A **GDN + QSA hybrid architecture**. Gated DeltaNet (GDN) compresses the history efficiently; **Qwen Sparse Attention (QSA)** uses a compressed lightweight indexer to select the important context at micro-block granularity, substantially reducing the cost of attention on long sequences.
- **Residual**: **Gated Residual (GR)** widens the residual stream into 4 branches and controls reads and writes with a dynamic gate, strengthening cross-layer information flow and training stability.
- **Embedding**: **N-gram Embedding** looks up a table using the local context to scale model capacity with very little extra computation; the embedding table can be offloaded to host memory and overlapped with model computation through asynchronous prefetching.
- **Optimization**: The **Muon optimizer** is used, refined around orthogonalization accuracy, the division of labour between Muon and AdamW, and the splitting of fused parameters, with the scaling law refitted for the new architecture.

Qwen3.8-Flash-Next features a **125B** -parameter main model, supplemented by an additional **51B** N-gram embeddings, with **6B** parameters activated per token. Compared with Qwen3.7-Plus, Qwen3.8-Flash-Next substantially reduces both training and inference cost — training takes only about 1/9 as much, yet it delivers superior capabilities in coding and office tasks.

It natively supports **262,144** tokens of context and is extensible to **1,000,000** tokens with YaRN. For more technical details on the architecture, training methodology, and experimental analysis of Qwen3.8-Flash-Next, please refer to the [technical report](https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf) in our GitHub repository.

Qwen3.8-Flash-Next weights are now available on [Hugging Face](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) and [ModelScope](https://modelscope.cn/models/Qwen/Qwen3.8-Flash-Next). The production version, with 1M context by default and official built-in tools, is served as **Qwen3.8-Flash** on [QwenCloud](https://www.qwencloud.com/models/qwen3.8-flash), **priced at 0.16 USD per million input tokens and 0.47 USD per million output tokens** *(API coming soon)*.

## Performance

### Language

<table><thead><tr><th></th><th>Qwen3.8-Flash-Next</th><th>Qwen3.8-27B</th><th>Qwen3.7-Plus</th><th>DeepSeek-V4-Flash-0731</th><th>Claude-Opus-4.6 (Max)</th></tr></thead><tbody><tr><td><p># Params</p></td><td>125B</td><td>27B</td><td>397B</td><td>284B</td><td>--</td></tr><tr><td><p># Activated params</p></td><td>6B</td><td>27B</td><td>17B</td><td>13B</td><td>--</td></tr><tr><td><p># N-gram embedding params</p></td><td>51B</td><td>--</td><td>--</td><td>--</td><td>--</td></tr><tr><td colspan="6">Coding</td></tr><tr><td><p>Agentic coding</p><p>DeepSWE 1.1</p></td><td><strong>58.7</strong></td><td>42.2</td><td>16.5</td><td>54.4</td><td>--</td></tr><tr><td><p>Agentic coding</p><p>SWE-bench Pro</p></td><td><strong>62.5</strong></td><td>61.7</td><td>55.8</td><td>56.0</td><td>53.4</td></tr><tr><td><p>Multilingual software engineering</p><p>SWE-bench Multilingual</p></td><td><strong>81.0</strong></td><td>73.8</td><td>75.8</td><td>--</td><td>77.5</td></tr><tr><td><p>Repo-level code generation</p><p>NL2Repo-Bench</p></td><td>48.1</td><td>42.3</td><td>41.1</td><td><strong>54.2</strong></td><td>47.6</td></tr><tr><td colspan="6">Agent</td></tr><tr><td><p>Long-horizon office work</p><p>CoWorkBench</p></td><td><strong>73.9</strong></td><td>70.7</td><td>65.1</td><td>45.1</td><td>68.2</td></tr><tr><td><p>Professional job tasks</p><p>JobBench</p></td><td><strong>55.7</strong></td><td>33.4</td><td>27.6</td><td>41.3</td><td>36.6</td></tr><tr><td><p>Frontier agentic tasks</p><p>Agents' Last Exam</p></td><td><p>Pass@1</p><p>24.3</p><p>Score</p><p><strong>51.2</strong></p></td><td><p>Pass@1</p><p>20.4</p><p>Score</p><p>42.9</p></td><td><p>Pass@1</p><p>13.2</p><p>Score</p><p>33.6</p></td><td><p>Pass@1</p><p><strong>25.2</strong></p><p>Score</p><p>--</p></td><td>--</td></tr><tr><td><p>Real-world tool use</p><p>Toolathlon Verified (Pass@1)</p></td><td><strong>73.5</strong></td><td>67.1</td><td>50.6</td><td>70.3</td><td>--</td></tr><tr><td colspan="6">General</td></tr><tr><td><p>Instruction following</p><p>IFBench</p></td><td><strong>81.3</strong></td><td>79.5</td><td>79.1</td><td>79.2</td><td>62.5</td></tr><tr><td><p>Scientific reasoning</p><p>GPQA Diamond</p></td><td><strong>91.7</strong></td><td>89.2</td><td>90.3</td><td>90.8</td><td>91.3</td></tr><tr><td><p>Multidisciplinary reasoning</p><p>HLE</p></td><td>35.9</td><td>30.8</td><td>34.7</td><td>33.8</td><td><strong>40.0</strong></td></tr><tr><td><p>Competitive coding</p><p>LiveCodeBench v6</p></td><td><strong>91.9</strong></td><td>90.3</td><td>89.6</td><td>90.6</td><td>88.8</td></tr></tbody></table>

1\. DeepSWE 1.1: evaluated with the Claude Code and mini-SWE-agent harnesses, temp=1.0, top\_p=0.95, 256K context window. We report the highest score across the two harnesses; notably, Qwen3.8-Flash-Next performs best on mini-SWE-agent.  
2\. SWE-bench Pro: except for Claude-Opus-4.6 (Max), for which we report the officially published score, all models are evaluated with the Claude Code harness, temp=1.0, top\_p=0.95, 256K context window. Problematic tasks were corrected and all baseline models were re-evaluated on the refined benchmark.  
3\. SWE-bench Multilingual: evaluated with the mini-SWE-agent harness, temp=1.0, top\_p=0.95, 256K context window.  
4\. NL2Repo-Bench: evaluated with the Claude Code harness. To prevent reward hacking, we disable Bash commands that attempt to access the specific repository, such as pip download, pip install and git clone.  
5\. CoWorkBench: an in-house cowork benchmark for evaluating long-horizon office and productivity agent tasks across computer science, finance, law, medical and other productivity domains.  
6\. HLE: judged by GPT-4o.  
7\. The best result in each row is shown in bold.  
8\. Empty cells (--): scores are not yet available or are not applicable.

### Vision Language

<table><thead><tr><th></th><th>Qwen3.8-Flash-Next</th><th>Qwen3.8-27B</th><th>Qwen3.7-Plus</th><th>Claude-Opus-4.6 (Max)</th></tr></thead><tbody><tr><td colspan="5">Agentic Multimodal Intelligence</td></tr><tr><td><p>Multimodal tool use</p><p>ClawEval-MM</p></td><td><p>Pass@3</p><p><strong>64.4</strong></p><p>Average</p><p><strong>60.4</strong></p></td><td><p>Pass@3</p><p>57.4</p><p>Average</p><p>56.9</p></td><td><p>Pass@3</p><p>57.4</p><p>Average</p><p>60.1</p></td><td><p>Pass@3</p><p>52.5</p><p>Average</p><p>54.7</p></td></tr><tr><td><p>Application recreation</p><p>RecreationBench</p></td><td><strong>49.9</strong></td><td>47.1</td><td>30.2</td><td>--</td></tr><tr><td><p>Mobile use</p><p>AndroidWorld</p></td><td><strong>84.5</strong></td><td>81.9</td><td>81.0</td><td>62.0</td></tr><tr><td><p>Computer use</p><p>OSWorld 2.0</p></td><td><p>Binary</p><p><strong>19.4</strong></p><p>Partial</p><p><strong>52.3</strong></p></td><td><p>Binary</p><p>19.4</p><p>Partial</p><p>48.0</p></td><td><p>Binary</p><p>2.8</p><p>Partial</p><p>21.5</p></td><td>--</td></tr><tr><td><p>Visual web development</p><p>Vision2Web</p></td><td><strong>64.0</strong></td><td>62.9</td><td>42.1</td><td>--</td></tr><tr><td colspan="5">General Multimodal Intelligence</td></tr><tr><td><p>Embodied intelligence</p><p>ERQA</p></td><td><strong>72.3</strong></td><td>65.5</td><td>69.8</td><td>40.8</td></tr><tr><td><p>Long video understanding</p><p>LVBench</p></td><td><strong>76.6</strong></td><td>72.4</td><td>76.2</td><td>63.0</td></tr><tr><td><p>Real-world perception</p><p>RealWorldQA</p></td><td><strong>88.5</strong></td><td>85.9</td><td>86.9</td><td>73.9</td></tr><tr><td><p>Visual math problem solving</p><p>MathVision</p></td><td><p>Without CI</p><p><strong>90.6</strong></p><p>With CI</p><p><strong>95.7</strong></p></td><td><p>Without CI</p><p>90.0</p><p>With CI</p><p>94.6</p></td><td><p>Without CI</p><p>90.3</p><p>With CI</p><p>88.7</p></td><td><p>Without CI</p><p>65.5</p></td></tr><tr><td><p>Scientific chart analysis</p><p>CharXiv (RQ)</p></td><td><p>Without CI</p><p>84.6</p><p>With CI</p><p><strong>90.6</strong></p></td><td><p>Without CI</p><p>83.7</p><p>With CI</p><p>90.2</p></td><td><p>Without CI</p><p><strong>85.8</strong></p><p>With CI</p><p>85.9</p></td><td><p>Without CI</p><p>66.0</p></td></tr></tbody></table>

1\. ClawEval-MM: scores are reported as "pass@3 / average score". Pass@3 measures the percentage passed in at least one of three trials, and the average score is the mean score across the three trials.  
2\. RecreationBench: an in-house long-horizon application-recreation benchmark for evaluating hybrid-agent abilities spanning five platforms — desktop (Ubuntu, macOS, Windows), mobile (Android) and web.  
3\. OSWorld 2.0: scores are reported as "binary / partial". The binary score is the percentage of tasks that receive the full task reward, while the partial score aggregates the partial rewards obtained across all tasks.  
4\. Vision2Web: scores are reported as the average over the frontend, webpage and website categories, using the Claude Code harness and judged by gpt-5.4-2026-03-05.  
5\. MathVision, CharXiv (RQ): scores are reported as "without CI / with CI". A small number of incorrect ground-truth annotations in MathVision were corrected after manual verification. Our model's score is evaluated using a fixed prompt, e.g. "Please reason step by step, and put your final answer within \\boxed{}." For other models, we report the higher score between runs with and without the \\boxed{} formatting.  
6\. The best result in each row is shown in bold.  
7\. Empty cells (--) indicate scores not yet available or not applicable.

## Model Architecture

![Qwen3.8-Flash-Next architecture](https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen3.8-Flash-Next/architecture.png#center)

Qwen3.8-Flash-Next architecture

### Attention: GDN + QSA for Efficient Memory and Precise Retrieval

Traditional Full Attention provides direct access to all previous tokens, but as the context grows longer, both computation and KV Cache memory-access costs increase substantially.

Following the architecture design introduced in Qwen3.5, Qwen3.8-Flash-Next adopts a **GDN [\[1\]](#ref1) + Attention Hybrid architecture**: three out of every four layers use Gated DeltaNet (GDN) to continuously compress historical information into a fixed-size state, while the remaining layer uses global Attention for precise retrieval of information across the full context.

For global Attention, we further introduce **Qwen Sparse Attention (QSA)**. Sparse Attention reduces long-sequence computation by attending only to important context. However, existing approaches such as DSA [\[2\]](#ref2) still rely on a token-level indexer to identify important positions; as the context grows, the indexer itself becomes a non-negligible source of computation.

QSA further compresses this process: a lightweight indexer first aggregates the sequence into **micro-blocks**, estimates context importance at the block level, and then selects the most relevant regions for Attention. This reduces not only the cost of Attention itself, but also the indexing overhead required to identify important context. Compared with approaches that share indices across layers [\[3\]](#ref3), QSA performs sequence compression independently within each layer, reducing its dependence on cross-layer Attention similarity and making it particularly well suited to Hybrid architectures where GDN and Attention layers are interleaved.

![Overview of Qwen Sparse Attention (QSA)](https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen3.8-Flash-Next/qsa_arch.png#center)

Overview of Qwen Sparse Attention (QSA)

Put simply: **GDN efficiently “remembers,” while QSA precisely “retrieves.”**

At **1M tokens**, QSA’s Attention Kernel achieves up to **7.6×** and **4.9×** speedups in Prefill and Decode, respectively. In an experimental setup representative of online serving scenarios with high cache reuse (a **90% Prefix Cache hit rate**), Qwen3.8-Flash-Next achieves **8.6×** the Prefill throughput of Qwen3.7-Plus at a **1M-token context length**.

![Relative prefill throughput at 90% cache hit rate](https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen3.8-Flash-Next/throughput.png#center)

Relative prefill throughput at 90% cache hit rate

### Gated Residual: More Paths for Information Flow

In a traditional Transformer, all layers continuously read from and write to the same Residual Stream. As the network becomes deeper, early features are repeatedly mixed with later information, making important signals more likely to be gradually diluted.

**Gated Residual (GR)** can be viewed as a combination of two ideas: it follows **Hyper-Connection** [\[4\]](#ref4) in widening the residual stream into multiple branches, while incorporating the element-wise dynamic gating of **GatedNorm** [\[5\]](#ref5) into the residual read. The original single residual stream is expanded into four parallel branches, allowing the model to dynamically determine how much information to read from each branch and how much to write back to each branch based on the current content.

This can be conceptualized as expanding a single information channel into multiple parallel pathways: some branches handle local information flow, while others preserve early information directly deep into the network layers. Empirical analysis also reveals that one of these branches naturally emerges as a long-range pathway connecting the first Attention layer to most of the middle and subsequent layers.

GR also further simplifies Hyper-Connection. Once the read and write operations are expressive enough, additional branch mixing yields no significant benefits and can thus be directly removed, thereby reducing memory access overhead and sources of instability. The Gate also effectively suppresses **activation outliers** and improves training stability. In addition, the Residual State supports **FP8** storage, further reducing memory-access overhead.

### N-gram Embedding: Expanding Model Capacity at Low Cost

Inspired by Per-Layer Embedding in Gemma 3n and works such as DeepSeek Engram [\[6\]](#ref6), we further introduce **N-gram Embedding** to scale model capacity beyond the parameters of the Transformer backbone.

A standard Embedding performs a lookup based on a single token. N-gram Embedding instead performs lookups using the local context formed by the current token and several preceding tokens, providing additional representations for common phrases and local patterns.

Its key advantage is that it **can add a large number of parameters with almost no additional computation per token**.

Qwen3.8-Flash-Next introduces an additional **51B N-gram Embedding parameters**. Because lookup locations can be determined in advance, these parameters can be stored in Host Memory and asynchronously prefetched in parallel with model computation, without permanently occupying GPU memory.

The final model uses only a single N-gram Embedding layer near the beginning of the network, effectively adding a large-scale **“local-pattern memory”** at relatively low additional cost.

### Optimization: Co-designing Architecture and Optimization

Qwen3.8-Flash-Next is trained with the **Muon Optimizer** [\[7\]](#ref7), with further improvements around three key aspects of applying Muon to large-scale model training: **orthogonalization accuracy, parameter assignment between Muon and AdamW, and splitting fused parameter matrices**.

For parameters that genuinely act as two-dimensional linear maps, such as the main weights in Attention, GDN, and MoE Experts, we use Muon. Embeddings, the MoE Router, and the low-rank parameters in GR continue to use AdamW. For QKV, SwiGLU, and GDN projections that are fused in the implementation, we first split them according to the independent linear transformations they represent, and then perform orthogonalization separately.

For the new architecture and Optimizer, we refit the Scaling Law. The results show that the model can stably use **larger Learning Rates and Batch Sizes**, further improving convergence efficiency and large-scale parallel training throughput.

We also find that **Batch Size Warmup**, a common practice in large-scale model training, is no longer necessary: gradually increasing from a small Batch to the target Batch does not improve the final result, but instead requires **18.8% more optimizer steps**. In the final training Recipe, we therefore start directly with the target Batch Size.

### Other Architecture Optimizations

The remaining components follow the design established in Qwen3-Next and refined through the Qwen3.5–Qwen3.8 series.

- **Ultra-sparse MoE**: With global load balancing [\[8\]](#ref8), increasing total expert parameters while keeping the number of activated experts fixed steadily reduces training loss. Qwen3.8-Flash-Next therefore uses a large expert pool with a small number of routed experts per token, together with one shared expert.
- **Multi-Token Prediction**: The MTP module is trained with multiple steps, maintaining consistency between training and inference and thereby improving the acceptance rate of speculative decoding in real scenarios, while also enhancing the performance of the backbone. Its full-attention layers are replaced with QSA as well.
- **Training stability**: Zero-centered RMSNorm with weight decay applied to norm weights, the attention output gating mechanism [\[9\]](#ref9), and normalized MoE router initialization are retained. These designs make small-scale ablations more reliable and help large-scale training run smoothly.

## Base Model Performance

We compare Qwen3.8-Flash-Next-Base with the base models of Qwen3.8-27B and Qwen3.7-Plus.

<table><thead><tr><th></th><th>Qwen3.8-Flash-Next-Base</th><th>Qwen3.8-27B-Base</th><th>Qwen3.7-Plus-Base</th></tr></thead><tbody><tr><td><p># Params</p></td><td>125B</td><td>27B</td><td>397B</td></tr><tr><td><p># Activated params</p></td><td>6B</td><td>27B</td><td>17B</td></tr><tr><td><p># N-gram embedding params</p></td><td>51B</td><td>--</td><td>--</td></tr><tr><td colspan="4">General tasks</td></tr><tr><td><p>MMLU</p></td><td>90.36</td><td>87.51</td><td><strong>90.43</strong></td></tr><tr><td><p>MMLU-Redux</p></td><td>90.68</td><td>87.26</td><td><strong>91.47</strong></td></tr><tr><td><p>MMLU-Pro</p></td><td><strong>73.23</strong></td><td>68.60</td><td>70.90</td></tr><tr><td><p>SuperGPQA</p></td><td><strong>51.36</strong></td><td>44.86</td><td>48.42</td></tr><tr><td><p>BBH</p></td><td><strong>90.87</strong></td><td>89.56</td><td>89.41</td></tr><tr><td colspan="4">Math & STEM tasks</td></tr><tr><td><p>GPQA</p></td><td>51.42</td><td>45.01</td><td><strong>51.52</strong></td></tr><tr><td><p>GSM8K</p></td><td><strong>93.29</strong></td><td>93.18</td><td>92.95</td></tr><tr><td><p>MATH</p></td><td>72.78</td><td>60.54</td><td><strong>74.38</strong></td></tr><tr><td colspan="4">Coding tasks</td></tr><tr><td><p>EvalPlus</p></td><td><strong>78.76</strong></td><td>76.05</td><td>78.06</td></tr><tr><td><p>MultiPL-E</p></td><td>79.09</td><td>74.50</td><td><strong>81.68</strong></td></tr><tr><td><p>SWEBench-Pretrain</p></td><td><strong>50.99</strong></td><td>41.66</td><td>49.24</td></tr><tr><td colspan="4">Multilingual tasks</td></tr><tr><td><p>MGSM</p></td><td><strong>89.33</strong></td><td>86.37</td><td>85.42</td></tr><tr><td><p>MMMLU</p></td><td><strong>84.86</strong></td><td>79.74</td><td>84.53</td></tr><tr><td><p>INCLUDE</p></td><td>78.40</td><td>74.37</td><td><strong>78.90</strong></td></tr></tbody></table>

1\. The best result in each row is shown in bold.  
2\. Empty cells (--): scores are not yet available or not applicable.

With 6B activated parameters, Qwen3.8-Flash-Next-Base achieves the best result on 8 of the 14 benchmarks, including MMLU-Pro, SuperGPQA, BBH, GSM8K, EvalPlus, SWEBench-Pretrain, MGSM and MMMLU, and remains close to Qwen3.7-Plus-Base on MMLU, MMLU-Redux, GPQA, MATH and MultiPL-E. The 51B N-gram embedding parameters are deterministically addressed and do not enter the per-token matrix-multiplication budget.

## Develop with Qwen3.8-Flash-Next

Qwen3.8-Flash-Next is available as an open-weight model on [HuggingFace](https://huggingface.co/collections/Qwen/qwen38-flash-next) and [ModelScope](https://www.modelscope.cn/collections/Qwen/Qwen38-Flash-Next), with official managed APIs on [QwenCloud](https://www.qwencloud.com/models/qwen3.8-flash). Designed to balance capability, latency, and cost, it is well suited for high-volume applications, tool-driven workflows, and coding & coworking assistants. In the following, you can explore how to call the QwenCloud API and integrate Qwen3.8-Flash-Next into agentic systems and coding assistants.

> **Coming soon.** The API is not live yet — it will be enabled shortly after this post goes out. The examples in this section will work from then on.

### API Usage

Qwen3.8-Flash-Next is available via API:

#### QwenCloud

On [QwenCloud](https://www.qwencloud.com/), the model is served under the name [`qwen3.8-flash`](https://www.qwencloud.com/models/qwen3.8-flash). QwenCloud supports industry-standard protocols, including OpenAI-compatible Chat Completions and Responses APIs, alongside an Anthropic-compatible interface.

```
"""
Environment variables:
  DASHSCOPE_API_KEY: Your API Key from https://home.qwencloud.com/
  DASHSCOPE_BASE_URL: (optional) Base URL for compatible-mode API.
    - Beijing: https://dashscope.aliyuncs.com/compatible-mode/v1
    - Singapore: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
    - US (Virginia): https://dashscope-us.aliyuncs.com/compatible-mode/v1
"""
from openai import OpenAI
import os
api_key = os.environ.get("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError(
        "DASHSCOPE_API_KEY is required. "
        "Set it via: export DASHSCOPE_API_KEY='your-api-key'"
    )
client = OpenAI(
    api_key=api_key,
    base_url=os.environ.get(
        "DASHSCOPE_BASE_URL",
        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    ),
)
messages = [{"role": "user", "content": "Write a Python function to merge two sorted linked lists."}]
completion = client.chat.completions.create(
    model="qwen3.8-flash",
    messages=messages,
    extra_body={
        "enable_thinking": True,
        # "preserve_thinking": True,
    },
    reasoning_effort="xhigh",  # supported levels are xhigh, medium, and low
    stream=True,
)
reasoning_content = ""
answer_content = ""
is_answering = False
print("\n" + "=" * 20 + "Reasoning" + "=" * 20 + "\n")
for chunk in completion:
    if not chunk.choices:
        print("\nUsage:")
        print(chunk.usage)
        continue
    delta = chunk.choices[0].delta
    if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
        if not is_answering:
            print(delta.reasoning_content, end="", flush=True)
        reasoning_content += delta.reasoning_content
    if hasattr(delta, "content") and delta.content:
        if not is_answering:
            print("\n" + "=" * 20 + "Answer" + "=" * 20 + "\n")
            is_answering = True
        print(delta.content, end="", flush=True)
        answer_content += delta.content
```

### Agent Frameworks & Coding Assistants

Qwen3.8-Flash-Next integrates seamlessly with popular agent frameworks and coding assistants:

#### QwenWork (Coming Soon)

[QwenWork](https://qwenwork.ai/) is Alibaba’s flagship AI productivity platform, designed to help individuals and enterprises automate daily tasks and accelerate operational efficiency.

We are excited to share that QwenWork has integrated **Qwen3.8-Flash-Next** to power its newly launched “Standard” mode, leveraging the model’s cutting-edge capabilities to deliver a seamless, cost-effective experience that sets a new standard for AI agents in the workplace.

![Qwen3.8-Flash on QwenWork](https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen3.8-Flash-Next/qwen-work-ai.png#center)

Qwen3.8-Flash on QwenWork

Learn more in the [official documentation](https://docs.qwenwork.ai/product-introduction)!

#### Claude Code

Qwen APIs support the Anthropic API protocol, enabling direct use with **Claude Code**:

```
npm install -g @anthropic-ai/claude-code
export ANTHROPIC_MODEL="qwen3.8-flash"
export ANTHROPIC_SMALL_FAST_MODEL="qwen3.8-flash"
export ANTHROPIC_BASE_URL=https://dashscope-intl.aliyuncs.com/apps/anthropic
export ANTHROPIC_AUTH_TOKEN=<your_api_key>
claude
```

#### Codex

Qwen APIs support the OpenAI Responses protocol, enabling use with **Codex**:

In `~/.codex/model-catalog.local.json`

```
{
  "models": [
    {
      "slug": "qwen3.8-flash",
      "display_name": "qwen3.8-flash",
      "description": "QwenCloud: Qwen3.8-Flash",
      "default_reasoning_level": "xhigh",
      "supported_reasoning_levels": [
        {
          "effort": "low",
          "description": "Fast responses with lighter reasoning"
        },
        {
          "effort": "medium",
          "description": "Greater reasoning depth for complex problems"
        },
        {
          "effort": "xhigh",
          "description": "Extra high reasoning depth for complex problems"
        }
      ],
      "context_window": 1000000,
      "effective_context_window_percent": 95,
      "supports_parallel_tool_calls": true,
      "supports_image_detail_original": true,
      "input_modalities": ["text", "image"],
      "shell_type": "default",
      "visibility": "list",
      "supported_in_api": true,
      "priority": 1,
      "base_instructions": "",
      "support_verbosity": false,
      "supports_reasoning_summaries": false,
      "experimental_supported_tools": [],
      "truncation_policy": {
        "mode": "bytes",
        "limit": 10000
      }
    }
  ]
}
```

In `~/.codex/config.toml`

```
model_catalog_json = "~/.codex/model-catalog.local.json"
model_provider = "QwenCloud"
model = "qwen3.8-flash"
[model_providers.QwenCloud]
name = "QwenCloud"
base_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
env_key = "OPENAI_API_KEY"
wire_api = "responses"
```
```
npm install -g @openai/codex
export OPENAI_API_KEY=<your_api_key>
codex
```

#### Qoder CLI

[Qoder](https://qoder.com/) co-evolves with Qwen for agentic coding:

```
curl -fsSL https://qoder.com/install | bash
qoder
```

#### Qwen Code

[Qwen Code](https://qwen.ai/qwencode) is deeply optimized for the Qwen series:

```
npm install -g @qwen-code/qwen-code@latest
qwen
```

#### OpenClaw

Connect to [OpenClaw](https://openclaw.ai/) via [QwenCloud](https://docs.qwencloud.com/developer-guides/clients-and-developer-tools/openclaw):

```
curl -fsSL https://openclaw.ai/install.sh | bash
export DASHSCOPE_API_KEY=<your_api_key>
openclaw dashboard
```

Configure `~/.openclaw/openclaw.json`:

```
{
  "models": {
    "mode": "merge",
    "providers": {
      "qwencloud": {
        "baseUrl": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "apiKey": "DASHSCOPE_API_KEY",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.8-flash",
            "name": "qwen3.8-flash",
            "reasoning": true,
            "input": ["text", "image"],
            "contextWindow": 1000000,
            "maxTokens": 65536
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "qwencloud/qwen3.8-flash"
      }
    }
  }
}
```

## Summary

Qwen3.8-Flash-Next extends the hybrid architecture introduced in Qwen3-Next along four directions: attention, residual, embedding and optimization. QSA compresses the sequence into micro-blocks within each layer, reducing both the attention cost and the indexing cost at long context while keeping precise retrieval. Gated Residual widens the residual stream into several parallel branches and controls reads and writes with an elementwise, data-dependent gate, improving cross-layer information flow and training stability at negligible arithmetic cost; the residual state can additionally be kept in FP8, which further reduces memory traffic. N-gram embedding scales capacity through deterministically addressed lookup memory, which can be scaled with negligible per-token computation and offloaded to host memory. On the optimization side, Muon is used as the main optimizer, with orthogonalization accuracy, parameter assignment and fused-matrix splitting as the decisive implementation choices, and the scaling law refitted for the new architecture.

We release these weights early so that the architecture can be evaluated independently by the community, as we did with Qwen3-Next, and we will continue to refine it towards Qwen4.

## Citation

```
@techreport{qwen2026design,
    title       = {On the Design of {Qwen3.8-Next} Architecture: Evaluation, Efficiency, and Training Stability},
    institution = {Alibaba Group},
    month       = {August},
    year        = {2026}
}
@misc{qwen3.8flashnext,
    title  = {{Qwen3.8-Flash-Next}: A New Architecture, Towards Ultimate Cost-Efficiency},
    month  = {August},
    year   = {2026},
    url    = {https://qwen.ai/blog?id=qwen3.8-flash-next}
}
```

## References

\[1\] Gated Delta Networks: Improving Mamba2 with Delta Rule

\[2\] DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models

\[3\] IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse

\[4\] Hyper-Connections

\[5\] A Unified View of Attention and Residual Sinks: Outlier-Driven Rescaling is Essential for Transformer Training

\[6\] Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models

\[7\] Muon: An Optimizer for Hidden Layers in Neural Networks

\[8\] Demons in the Detail: On Implementing Load Balancing Loss for Training Specialized Mixture-of-Expert Models

\[9\] Gated Attention for Large Language Models: Non-linearity, Sparsity, and Attention-Sink-Free
2026-08-26 · Research

We introduce GLM-5.3-Flash, the first natively multimodal model in the GLM-5 series. With 320B total parameters and just 18B active parameters, it outperforms GLM-5.2 across benchmarks and real-world workloads at one-tenth the price, while approaching Claude Opus 4.8 on coding and agentic benchmarks.

GLM-5.3-Flash incorporates several architectural improvements over GLM-5. For the first time, we introduce a hybrid architecture combining sparse and linear attention, sharply reducing long-context serving costs while preserving precise long-context capabilities. It also adopts Manifold-Constrained Hyper-Connections (mHC) to further improve scaling efficiency. Combined with our latest 30T-token multimodal pre-training corpus, these changes let GLM-5.3-Flash produce more intelligence with less compute.

Before release, we tested GLM-5.3-Flash anonymously as `ox-alpha` on OpenCode and OpenRouter to gather user feedback. It quickly became the most popular model of the week — with all of this traffic served on Chinese AI chips.

![](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/ryTOUL3vGe.png) ![](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/S10CTLhwzg.png)

## Competitive Performance at Flash Cost

GLM-5.3-Flash pushes the Pareto frontier of the Artificial Analysis Intelligence Index v4.1.1, scoring 57 at just $0.045 per task (discounted) — a level of intelligence previously only available at roughly 10× the cost. This makes it a highly competitive default choice for a broad range of workloads.

![c2ea01fd1ee01e0ff054754a2ad9e644](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/Sy_ehD3wzx.png)

Across six coding and agentic benchmarks, GLM-5.3-Flash consistently outperforms GLM-5.2, often by a wide margin — 63.4 vs. 46.2 on DeepSWE v1.1 and 48.8 vs. 26.2 on AutomationBench — while approaching Claude Opus 4.8 overall.

![img_v3_0214u_921edf4e-06c8-48ea-bffe-cdf2b79a0a6g](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/rJG_RLhPzl.png)

This holds on our in-house coding evaluation as well: on Z.ai Code Bench v1.0 (run on Claude Code 2.1.207), GLM-5.3-Flash clearly outperforms GLM-5.2 at every effort level, and at max effort nearly matches Claude Opus 4.8 (29.0 vs. 29.5).

![img_v3_0214u_eef3c372-bc89-44cd-9ec3-919ff63bac0g](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/H1hAKXnDMx.png)

## Architecture for Extreme Efficiency

![img_v3_0214u_c34ae85d-2955-4bf5-9102-f22054c6f08g](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/HyqVZw2wze.png)

Compared with the GLM-4.5 series, GLM-5.3-Flash is specifically designed for ultra-low-cost inference. Despite a similar total parameter count (320B vs. 355B), it nearly halves both the activated parameter count (18B vs. 32B) and the number of layers (45 vs. 92).

To minimize attention costs in long-context scenarios, we use a hybrid architecture combining linear and sparse attention. Linear attention captures local dependencies through state modeling, while sparse attention retrieves relevant global context through a lightweight indexer. To further reduce the latency and memory overhead of the indexer at a 1M-token context length, we introduce IndexPool, which compresses four indexer key vectors into one through weighted pooling.

To illustrate the efficiency of our architecture, we compare the per-token compute and KV cache size of GLM-5.3-Flash against GLM-5.3 and two recent open models DeepSeek-V4-Flash and Kimi-K3. For a fair comparison among different scales, we calculate the attention compute per head per layer and average KV cache size per layer (BF16). Compared with GLM-5.3, GLM-5.3-Flash reduces the attention compute and KV cache size by factors of 3.0x and 4.4x. GLM-5.3-Flash has the lowest attention compute among all models compared. The KV cache size is still slightly larger than Kimi-K3 and DeepSeek-V4-Flash, leaving further room for improvement.

The overall architecture improvements, combined with optimized pre-training corpus, enable GLM-5.3-Flash to produce more intelligence with less compute. In the table below we show the evaluation results of the base model of GLM-5.3-Flash, comparing with our previous base models and DeepSeek-V4-Flash-Base. The results show that GLM-5.3-Flash-Base outperforms GLM-4.5-Base overall and remains competitive with GLM-5-Base across most benchmarks.

<table><thead><tr><th>Benchmark</th><th><p>GLM-4.5-Base</p></th><th><p>GLM-5-Base</p></th><th><p>DeepSeek-V4-Flash-Base</p></th><th><p>GLM-5.3-Flash-Base</p></th></tr></thead><tbody><tr><td>Activated Params</td><td>32B</td><td>40B</td><td>13B</td><td>18B</td></tr><tr><td>Total Params</td><td>355B</td><td>744B</td><td>284B</td><td>320B</td></tr><tr><td colspan="5"></td></tr><tr><td>MMLU</td><td>86.1</td><td>88.3</td><td>88.5</td><td>88.1</td></tr><tr><td>BBH</td><td>86.2</td><td>87.4</td><td>84.9</td><td>86.6</td></tr><tr><td>HellaSwag</td><td>87.1</td><td>88.1</td><td>85.3</td><td>87.1</td></tr><tr><td>LiveCodeBench-Base</td><td>28.1</td><td>34.4</td><td>29.9</td><td>37.6</td></tr><tr><td>SimpleQA</td><td>30.0</td><td>36.0</td><td>31.2</td><td>33.5</td></tr></tbody></table>

(Results for DeepSeek-V4-Flash-Base were evaluated using our internal evaluation framework to control for implementation differences)

## Visual Intelligence in the Coding Loop

Visual coding is not just about processing images. It expands the boundary of what coding can reach. For tasks such as frontend development, game development, and 3D simulation, the final output is not code alone, but an interface, an interaction, or a world experienced by the user. Many failures only surface through rendering, interaction, or playtesting. CUA further extends coding beyond programmable systems into visible and interactive environments. Vision therefore needs to be natively integrated into the model, enabling it to decide when to observe and use visual feedback to guide subsequent actions.

We develop data synthesis pipelines for visual coding, with a focus on self-visual judgment and test-time improvement. The resulting trajectories require the model to interact with environments, inspect its own outputs, and refine them iteratively. For frontend coding, we also explored reinforcement learning with environment feedback and further strengthened GUI judgment through agent-based verification grounded in real user flows. This extends validation beyond functional correctness to the rendered and interactive product.

**Code lets the model build and change the world. Vision lets it enter the world people see and use.** ![](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/SyYfF83Pze.jpg)

Initial Version with Layout Issues

![](https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/Hy1xDIhwzl.jpg)

After Visual Self-Verification

## Beyond Coding -- Your Partner at Work

Coding capabilities provide an important foundation for intelligent knowledge work, while visual intelligence extends these capabilities to a broader range of professional tasks. A substantial portion of professional activities involves interpreting heterogeneous visual and structured information, including documents, spreadsheets, presentations, dashboards, interfaces, and meeting artifacts.

Visual intelligence extends the model’s capabilities beyond code-centric environments by enabling it to jointly reason over textual, visual, and structural context. Rather than requiring users to explicitly translate their working environment into textual instructions, the model can directly interpret the artifacts associated with a task and identify relevant information. It can also assess its own outputs against the visual context and intended outcome, enabling more effective self-verification and refinement — including stronger judgments of presentation quality and aesthetics.

These capabilities become particularly evident in the following examples of professional workflows.

<iframe src="https://z-cdn-media.chatglm.cn/prompts-rich-media-resources/5.3-flash-blog/Eight_Worlds_Planetary_Archive.pdf"></iframe>

## Serving at Scale on Chinese AI Chips

Over the past week, we have served GLM-5.3-Flash on a large-scale cluster of Chinese AI chips, supported by a high-bandwidth interconnect and a serving stack optimized for the underlying hardware.

To overcome the relatively limited compute and memory capacity of individual chips, we built a dedicated inference engine for this architecture on top of SGLang. Notably, this effort was accelerated by our GLM-5.3-powered infrastructure agent, which assisted engineers in developing and optimizing kernels, diagnosing performance bottlenecks, and improving the serving stack — creating a feedback loop in which the model helped optimize the system serving the model itself.

These chips are primarily constrained by memory capacity and bandwidth, especially when supporting context lengths of up to one million tokens. This calls for aggressive memory optimization, including compute-for-bandwidth and communication-for-bandwidth techniques tailored to the underlying architecture. Our stack combines intra-node tensor parallelism for Linear Attention and the LM head, ReplaySSM, W8A8 quantization, hybrid INT8/FP8/BF16 cache quantization, and Layer Split.

At cluster scale, our production-grade Encode–Prefill–Decode (EPD) disaggregated architecture separates multimodal encoding, prompt prefill, and token-by-token decoding into independently scheduled and scalable worker pools, enabling efficient and reliable serving across tens of thousands of domestically developed accelerators.

Compared with our initial baseline on the same hardware, we achieved a 3× improvement in end-to-end serving performance, reaching hardware efficiency and per-token cost comparable to mainstream NVIDIA GPUs. This demonstrates that Chinese chips can support frontier-model inference efficiently and economically at scale.

## Conclusion

GLM-5.3-Flash shows that frontier intelligence does not have to come at frontier cost. This is not the result of any single trick, but of three layers working together: an architecture that delivers stronger capability from less compute, a richer multimodal pre-training corpus, and infrastructure co-designed with inference hardware. We are now scaling this recipe to larger models — GLM-5.3-Flash pushes the cost-performance frontier, and the lessons from building it are already shaping our next frontier model.

## Getting started with GLM-5.3-Flash

We've rolled out GLM-5.3-Flash to all GLM Coding Plan users. GLM-5.3-Flash gives you **3x** the usable quota of GLM-5.3. Try **GLM-5.3-Flash** in [z.ai/subscribe](https://z.ai/subscribe).

Unlock GLM-5.3-Flash's multimodal capabilities in [ZCode](https://zcode.z.ai/) with **Browser Use** and **Computer Use**: the agent clicks through and visually verifies web pages, and operates your desktop apps.

The model weights of GLM-5.3-Flash are publicly available on [HuggingFace](https://huggingface.co/zai-org/GLM-5.3-Flash). For local deployment, GLM-5.3-Flash currently supports inference frameworks including SGLang, vLLM and TokenSpeed. Others will be ready soon.

<table><thead><tr><th>Benchmark</th><th><p>GLM-5.3-Flash</p></th><th><p>GLM-5.2</p></th><th><p>DeepSeek-V4-Vision-Exp</p></th><th><p>Opus 4.8</p></th><th><p>GPT-5.6 Terra</p></th><th><p>Gemini 3.7 Flash</p></th></tr></thead><tbody><tr><td>Coding</td><td colspan="6"></td></tr><tr><td>Terminal Bench 2.1</td><td>84.3</td><td>81.0</td><td>83.9</td><td>85.0</td><td>87.4</td><td>85.8</td></tr><tr><td><p>DeepSWE</p><p>v1.1</p></td><td>63.4</td><td>46.2</td><td>59.3</td><td>58.0</td><td>69.6</td><td>65.3</td></tr><tr><td>NL2Repo</td><td>56.3</td><td>48.9</td><td>57.7</td><td>69.7</td><td>-</td><td>-</td></tr><tr><td>Agentic</td><td colspan="6"></td></tr><tr><td>Toolathlon Verified</td><td>78.4</td><td>59.9</td><td>75.9</td><td>76.2</td><td>74.9</td><td>-</td></tr><tr><td><p>AutomationBench</p><p>v1.0.6</p></td><td>48.8</td><td>26.2</td><td>38.8</td><td>41.0</td><td>37.2</td><td>52.3</td></tr><tr><td>Agents' Last Exam</td><td>26.3</td><td>20.4</td><td>27.3</td><td>27.0</td><td>28.0</td><td>-</td></tr><tr><td>HLE w/ Tools</td><td>55.3</td><td>54.7</td><td>55.1</td><td>57.9</td><td>-</td><td>-</td></tr><tr><td>GDPval-AA v2</td><td>1773</td><td>1504</td><td>1675</td><td>1582</td><td>1571</td><td>1527</td></tr><tr><td>Vision</td><td colspan="6"></td></tr><tr><td>OfficeQA Pro</td><td>62.4</td><td>-</td><td>57.9</td><td>48.9</td><td>-</td><td>-</td></tr><tr><td><p>CharXiv Reasoning</p><p>w/ Tools</p></td><td>89.4</td><td>-</td><td>80.4</td><td>89.9</td><td>88.0</td><td>88.7</td></tr><tr><td><p>Chartography</p><p>w/ Tools</p></td><td>78.0</td><td>-</td><td>64.3</td><td>75.0</td><td>68.0</td><td>65.0</td></tr><tr><td>BabyVision</td><td>53.4</td><td>-</td><td>35.1</td><td>46.8</td><td>61.6</td><td>70.9</td></tr><tr><td>MVbench</td><td>77.8</td><td>-</td><td>69.4</td><td>67.1</td><td>75.0</td><td>82.2</td></tr><tr><td>MMVU</td><td>80.5</td><td>-</td><td>72.7</td><td>67.4</td><td>75.8</td><td>82.3</td></tr></tbody></table>

## Footnotes

- **HLE w/ tools (full set)**: We use sampling parameters of `temperature=1.0` and `top_p=0.95` for evaluation, with a maximum generation length of `163,840` tokens. The evaluation is conducted with a maximum context length of `300,000` tokens, using a context management strategy. We use GPT-5.6-luna (medium) as the judge model.
- **NL2Repo**: We evaluated NL2Repo with temperature=1.0, top\_p=1.0, and max\_new\_tokens=64k under 1M context. To prevent hacking, we use rule-based and a LLM-based judgement to prevent malicious behaviors (e.g., unauthorized pip or curl operations).
- **DeepSWE**: We run DeepSWE using the mini-swe-agent harness with `temperature=0.95`, `top_p=1.0`, `timeout=6h` and 400K context.
- **Terminal-Bench 2.1**: We evaluate in Claude Code 2.1.207 with temperature=1.0, top\_p=1, max\_new\_tokens=65536 with 6h timeout.
- **Agent’s Last Exam**: We evaluate ALE using the official evaluation protocol with the Claude Code harness (reasoning effort=max, 1M context, and 64K maximum output). Tool Search is disabled, and results are scored by the official ALE evaluators.
- **Toolathlon Verified**: We obtain all results via the official evaluation service and report pass@1 averaged over 3 independent runs.
- **AutomationBench**: We evaluate on AutomationBench **v1.0.6**, incorporating the fix for the `null` -type handling issue introduced in [PR #13](https://github.com/zapier/AutomationBench/pull/13).
- **GDPval-AA v2**: Models are evaluated by Artificial Analysis.
- **BabyVision**: We use temperature=1.0, top\_p=0.95, and a maximum context length of 164K tokens. We resize the input images such that their shorter side is at least 1.5K pixels, consistent with other baselines.
- **OfficeQA Pro**: We evaluate the agent on the Treasury Bulletin PDF corpus without providing access to embedded text. We use a temperature of 1.0, top\_p of 0.95, and a maximum context length of 512K tokens.
- **CharXiv Reasoning**: We use temperature=1.0, top\_p=0.95, and a maximum context length of 256K tokens.
- **Chartography**: We use temperature=1.0, top\_p=0.95, and a maximum context length of 256K tokens.
- **MVBench and MMVU**: We use temperature=1.0, top\_p=0.95, and a maximum context length of 256K tokens. For models that natively accept video input, such as Gemini 3.7 Flash, we feed the raw video directly for evaluating. For models that do not support video input, we adapt a default 1 fps frame‑extraction strategy. If the total number of extracted frames exceeds the API’s maximum limit, we perform uniform frame‑sampling across the video up to this maximum frame count.
# Towards Looped Models Done Right

![](/image/attachment%3Aab61bb3e-d660-4c3d-a9ec-cbae85ccb2d8%3Aimage.png?table=block&id=3ade5119-12ec-8128-987d-feb7a5580043&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=2000&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

![🌔 Page icon](data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==)![🌔 Page icon](https://notion-emojis.s3-us-west-2.amazonaws.com/prod/svg-twitter/1f314.svg)

# Towards Looped Models Done Right

Part I: Topology, Input Injection, Recurrent-State Design

[Benhao Huang](https://huskydoge.github.io/)‡\*, Chufan Shi‡†, Junlin Chen‡, Shicheng Wen‡†,

Zhengzhong Liu‡, Eric Xing‡, Xuezhe Ma‡†

‡Institute of Foundation Models, †USC, \*CMU

Date: July 31, 2026

![](/image/attachment%3A778b7b6f-f927-4718-a9b9-2f18799a4568%3A%E6%88%AA%E5%B1%8F2026-07-28_02.00.22.png?table=block&id=3ade5119-12ec-8099-af82-f865ea0890be&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Fig. 1 Parameter scaling and benchmark performance of loop and feedforward MoE models. Left: Ouro MoE and Huginn MoE share the same scale: 8.0B resident and 0.8B active parameters, corresponding to 32.0B resident-equivalent and 3.2B unrolled-active parameter applications. Unrolled counts measure parameter applications under weight reuse. Right: Huginn MoE outperforms Ouro MoE overall, and approaches or surpasses the 112-layer feedforward MoE baseline on DROP, MATH500 and GSM8K, while remaining competitive on the other benchmarks. All models use the same data and matched training and inference FLOPs, while looped models require less memory.

ALT

†Correspondence to: Benhao Huang <benhaoh@andrew.cmu.edu>

Code (Release Soon) | Living Blog (updating continuously)

Cite this work

![💡 Callout icon](data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==)

TL;DR

Loop language models reuse physical Transformer blocks across logical depth, but established architectures entangle recurrence placement, input injection, and recurrent state organization. We isolate these axes in models trained from scratch at matched parameter scale, logical depth, and token budgets, and then test whether the resulting design principles transfer to resident- and active-parameter-matched Mixture-of-Experts (MoE) models.

Loop design. The prelude–recurrent block–coda sandwich architecture consistently improves performance on context extraction and reasoning-intensive tasks. Input injection primarily enhances knowledge retrieval and context utilization, whereas random initialization and separate H/L recurrent states provide mixed or negative returns. Taken together, these results favor the Huginn\-style design: at the 730M-parameter and 336B-token scale, the complete Huginn architecture outperforms Ouro across all ten benchmarks.

MoE transfer. The advantages of the Huginn over Ouro transfer to Mixture-of-Experts models. At the 8BA0.8B (32BA3B when unrolled) scale trained on 500B tokens, Huginn outperforms Ouro nearly all benchmarks spanning knowledge, reasoning, and coding, while also exhibiting more balanced expert routing.

Apples-to-apples comparison. Under matched training and inference FLOPs, the Huginn\-style model uses 75% fewer resident parameters than a 112-layer feedforward MoE baseline. Despite its smaller physical parameters, it outperforms the feedforward baseline on DROP and GSM8K, matches it on MATH500, and remains competitive on the other benchmarks.

![](/image/attachment%3A0cfcd9d0-20e6-4ce9-b35d-cda28a9d0994%3A%E6%88%AA%E5%B1%8F2026-07-28_15.42.34.png?table=block&id=3ade5119-12ec-80c1-ba62-c5db5411fbb3&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Tab. 1 Benchmark performance of loop MoE models and the feedforward MoE reference after training on 500B tokens. The looped models contain 8.0B resident and 793.9M active parameters per physical pass, corresponding to approximately 630 training tokens per active parameter. Bold compares only the recurrent rows; Δ\\DeltaΔ is Huginn MoE minus Ouro MoE; green and red mark positive and negative changes, respectively.

ALT

Table of Content

[

1\. Introduction

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec8065b882e94a969b4644)

[

2\. Preliminary

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec80c08106d10e495d862c)

[

2.1 Notations

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec80a68cefca6c165b72f0)

[

2.2 Comparing Ouro and Huginn

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec80fab63dea6fce2be072)

[

3\. Controlled Ablations of Loop-Model Design

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec8069a101c92bc6b7bec7)

[

3.1 Model Configuration

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec80f3832fd8da6927d1e1)

[

3.2 Training Recipe

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec8053a656f5702c34f07c)

[

3.3 Evaluation Protocols

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec808baa8ce8a5298a934c)

[

3.4 Controlled Architecture Ablations

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec80b986bdd932e4abd6f5)

[

Q1: Does Moving Recurrence into a Sandwich Envelope Help?

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec80bd9fa7d77206c17cbb)

[

Q2: Does Input Injection Help?

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec80e89c19eaac7d8864a9)

[

Q3: Do Separate Recurrent Latent States Help?

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec80b5beecdd53b2e69614)

[

Summary

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec8074bf5af66f5e143cb2)

[

4\. Transfer to MoE Models

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec8004bc99f28fdfaa0bbe)

[

4.1 Configurations for MoE Comparison

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec80b4b007f2cc718ca3bd)

[

4.2 Huginn-Style MoE versus Ouro

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec8000a154e9b7790aefae)

[

4.3 Routing Diagnostics

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec802db5d8cdaec11232a8)

[

4.4 Huginn-MoE versus Feedforward MoE

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec80b4bf4ed2d0f2dd9dbc)

[

4.5 Summary

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec80d3a0f4ea3ebcb44f99)

[

Conclusions

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec8021a527f269af83828d)

[

Reference

](/Towards-Looped-Models-Done-Right-3ade511912ec8128987dfeb7a5580043?pvs=25#3ade511912ec803b86a1d192d9c8995d)

### 1\. Introduction

Loop language models repeatedly reuse the same Transformer blocks across logical depth, trading additional computation for reduced memory usage. As modern AI hardware delivers rapidly increasing compute throughput while memory capacity and bandwidth improve much more slowly \[1\], this paradigm has emerged as a promising direction for scaling language models. Recent work has investigated recurrent-depth scaling \[2–5\], capability profiles \[6-9\], as well as the roles of stability and residual dynamics \[8,17\], architecture topology and sparsity \[10,18\], and memory efficiency \[11\]. Most existing loop language models can be broadly categorized into two architectural lineages, represented by Ouro \[2\] and Huginn \[3\].

Despite their growing influence, the architectural differences between these two families have not been systematically isolated. Ouro recurrently applies a tied full stack initialized from token embeddings, whereas Huginn places recurrence between untied prelude and coda layers, repeatedly injects a fixed prelude representation, and uses a separately initialized recurrent state. We formalize these differences along three axes---the iteration envelope, input injection, and latent-state organization---and isolate their effects through a controlled Ouro\-to-Huginn transformation. We pretrain all resulting models from scratch under matched parameter scale, logical depth, and token budgets, and evaluate them using a common protocol.

![](/image/attachment%3Abc2f7fe4-be3f-4887-9eb8-bef13c1baa9c%3Aimage.png?table=block&id=3ade5119-12ec-800f-be18-d09d7b391a7d&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Fig. 2 Selected loop-model works organized by family and quarter.

ALT

The rest of this article follows three questions.

[First, how should loop architectures be described?](/p/391c6a92030980c386a0da1ee0ae3e47?pvs=25#65bf70eb58a9443cb6b0a9900c7d9764) We introduce a common framework that separates three choices often bundled together: where recurrence is placed, how the input is reintroduced, and how recurrent states are organized.

[Second, which of these choices actually matter?](/p/391c6a92030980c386a0da1ee0ae3e47?pvs=25#392c6a92030980edb511c6f89efb83d2) Through controlled Ouro\-to-Huginn ablations, we find that placing recurrence inside a prelude–loop–coda sandwich provides the clearest gains, especially on mathematical reasoning, context extraction, and other reasoning-intensive tasks. Input injection helps models recover prompt-provided context and specifications, but can interfere with quantitative reasoning. Random initialization offers no consistent advantage, and separate high/low states add complexity without reliable gains. When these choices are combined, the full Huginn design outperforms Ouro across all ten dense benchmarks.

[Third, do these conclusions survive in MoE models?](/p/391c6a92030980c386a0da1ee0ae3e47?pvs=25#393c6a9203098043b8e0e2372a578521) They do. Huginn again outperforms Ouro, distributes expert load more evenly, and uses different experts meaningfully across loop iterations. It also approaches the performance of a much larger feedforward MoE while storing substantially fewer parameters.

### 2\. Preliminary

The architecture of Ouro and Huginn differs in their iteration envelope, input injection, and recurrent-state organization.

![](/image/attachment%3A55a62a6f-fca8-4a5b-975a-49d7907b4cc3%3Aimage.png?table=block&id=3ade5119-12ec-8063-8775-dc4193ff837b&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Fig 3. Architecture comparisons. Feedforward models use distinct blocks. Ouro\-style models reuse a full Transformer stack. Huginn\-like models initialize the recurrent hidden stream from a prior, place a tied iterative body between untied prelude and coda stacks, and inject the prelude representation into the iterations.

ALT

#### 2.1 Notations

Let x∈VB×L\\mathbf x\\in\\mathcal V^{B\\times L}x∈VB×L denote token indices and x0\=Eθ(x)∈RB×L×d\\mathbf x\_0=E\_\\theta(\\mathbf x)\\in\\mathbb R^{B\\times L\\times d}x0​\=Eθ​(x)∈RB×L×d their embeddings. A general tied iterative model can be written as

e\=Pθ(x0),z0\=ϕθ(e,ξ),z~t\=Wθ(zt,e),zt+1\=Rθ(z~t),t\=0,…,T−1,h\=Cθ(zT).\\begin{align} \\mathbf e &= P\_\\theta(\\mathbf x\_0), \\\\ \\mathbf z\_0 &= \\phi\_\\theta(\\mathbf e,\\boldsymbol{\\xi}), \\\\ \\tilde{\\mathbf z}\_t &= W\_\\theta(\\mathbf z\_t,\\mathbf e), \\\\ \\mathbf z\_{t+1} &= R\_\\theta(\\tilde{\\mathbf z}\_t), \\qquad t=0,\\ldots,T-1, \\\\ \\mathbf h &= C\_\\theta(\\mathbf z\_T). \\end{align}ez0​z~t​zt+1​h​\=Pθ​(x0​),\=ϕθ​(e,ξ),\=Wθ​(zt​,e),\=Rθ​(z~t​),t\=0,…,T−1,\=Cθ​(zT​).​​

Here PθP\_\\thetaPθ​ is the prelude map \[3\], RθR\_\\thetaRθ​ is the tied iterative body, CθC\_\\thetaCθ​ is the coda map. All three are stacks of standard Transformer blocks; the prelude and coda are applied once, whereas the recurrent core is repeatedly applied with shared parameters. ϕθ\\phi\_\\thetaϕθ​ initializes the recurrent state, and WθW\_\\thetaWθ​ is the per-step input write. The fixed representation e\\mathbf ee is the prelude output, zt\\mathbf z\_tzt​ is the model's recurrent hidden stream, and auxiliary randomness ξ\\boldsymbol{\\xi}ξ is used only by variants with random state initialization.

#### 2.2 Comparing Ouro and Huginn

Under this notation, an Ouro\-style topology sets PθP\_\\thetaPθ​,WθW\_\\thetaWθ​, and CθC\_\\thetaCθ​ to identity maps, initializes z0\=x0\\mathbf z\_0=\\mathbf x\_0z0​\=x0​, and applies the same stack for TTT iterations.

A Huginn\-style topology keeps nontrivial prelude and coda maps and writes the fixed representation e\\mathbf ee into the recurrent stream at each iteration. Note that such random initialization changes the starting value of that same stream while leaving the number of persistent states unchanged.

![](/image/attachment%3A27d091b3-1446-4da4-a940-23f3aaafa9d9%3A%E6%88%AA%E5%B1%8F2026-07-27_21.11.44.png?table=block&id=3ade5119-12ec-80eb-a718-f42e04ab72fb&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

This decomposition yields three separable design axes:

Iteration envelope chooses the placement and sharing pattern of Pθ,Rθ,CθP\_\\theta,R\_\\theta,C\_\\thetaPθ​,Rθ​,Cθ​​

Input interface chooses whether WθW\_\\thetaWθ​ receives a persistent input condition and what it reads, e.g. token embeddings versus prelude-encoded e\\mathbf ee;

Latent-space design chooses how ϕθ\\phi\_\\thetaϕθ​ initializes the loop state, e.g. z0\=e\\mathbf z\_0=\\mathbf ez0​\=e versus a separate draw, as well as the structures of the states, e.g. fast and slow latents.

### 3\. Controlled Ablations of Loop-Model Design

In this section, we specify the matched model, training, and evaluation controls, then report the stepwise ablations and the complete construction path from Ouro to Huginn. Q1 changes the iteration envelope, Q2 adds the prelude-conditioned input injection, and Q3 varies latent-state initialization and organization.

#### 3.1 Model Configuration

We evaluate the loop model variants in a matched 730M stored / 2.9B equivalent-when-unrolled; Each loop model stores the parameters of 28 Transformer blocks but reuses a subset of these blocks across recurrent iterations, yielding an unrolled computation path with the same logical depth as a 112-layer feedforward Transformer.

The Ouro\-style loop ties the full 28-block stack and executes it four times, giving (28×4\=112)(28 \\times 4 = 112)(28×4\=112) logical block executions, abbreviated as R284R\_{28}^4R284​ .

The Huginn\-style loop instead places recurrence in the middle of a feedforward envelope: an 8-layer prelude, an 8-step loop over a 12-layer tied recurrent core, and an 8-layer coda, giving (8+12×8+8\=112)(8 + 12 \\times 8 + 8 = 112)(8+12×8+8\=112) logical block executions, abbreviated as P8R128C8P\_8 R\_{12}^8 C\_8P8​R128​C8​.

Two feedforward baselines anchor the comparison. The 730M baseline D28D\_{28}D28​ contains 28 Transformer blocks and matches the resident parameter count of the looped models. The 2.9B baseline D112D\_{112}D112​ contains 112 independently parameterized Transformer blocks and matches their unrolled logical depth.

Transformer block. All models use the same decoder-only PreNorm backbone, ensuring that the ablations modify the recurrence pattern rather than the local block architecture. The attention module uses 24 query heads, 6 key–value heads, a head dimension of 64, and RoPE with base 10610^{6}106. At a hidden dimension of 1536, the dense feed-forward branch uses a SwiGLU MLP with intermediate width 4352. In each MoE variant, the attention, normalization, and residual structure remain unchanged; only the dense feed-forward branch is replaced by a top-2 routed mixture of experts.

#### 3.2 Training Recipe

All models are trained on the TxT360 dataset \[19\], a high-quality dataset that deduplicates 99 Common Crawl snapshots and 14 curated data sources from diverse domains. We use sequence length 8192 and an effective global batch of 512 sequences, or 4,194,304 tokens per optimizer step. We optimize with AdamW, sweep learning rates in {4 × 10−4, 6 × 10−4, 8 × 10−4}, and report the best setting. We use 200 warmup steps followed by cosine decay and set weight decay to 0.1.

#### 3.3 Evaluation Protocols

We evaluate the models on ten benchmarks spanning several capability groups:

ARC-Challenge, HellaSwag, MMLU, and TriviaQA emphasize factual, conceptual, and commonsense knowledge;

BBH-CoT and DROP require reasoning over instructions, demonstrations, or passage-level evidence;

GSM8K and MATH500 focus on multi-step quantitative and symbolic reasoning; and

HumanEval+ and MBPP+ test code generation under explicit functional specifications.

These categories overlap, but they provide a useful lens for understanding which capabilities benefit from each architectural change.

#### 3.4 Controlled Architecture Ablations

![](/image/attachment%3Ab5eab671-ec28-411f-a292-816e8830dfc8%3Aimage.png?table=block&id=3ade5119-12ec-8084-b84d-f2b7d0eb9e4b&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Fig 4. The controlled architecture ablations in Q1 & Q2. Q1 moves recurrence from the full stack into a sandwich loop between untied prelude and coda layers; Q2 then further injects the evolving zt\\mathbf z\_tzt​ with the fixed prelude embedding e\\mathbf eebefore every recurrent-core iteration.

ALT

##### Q1: Does Moving Recurrence into a Sandwich Envelope Help?

Results. The sandwich envelope improves multi-step answer derivation from the provided instance, raising MATH500 by 12.00 points and DROP by 2.61 points. Its gains on MATH500 and BBH-CoT persist across all four training budgets. Knowledge-heavy tasks and tasks with explicit output or interface requirements show no consistent gain, and some scores decline.

Q1 isolates loop placement at fixed logical compute. The full-stack Ouro control reuses all 28 blocks for four passes, R284R\_{28}^{4}R284​, whereas the sandwich control places a tied 12-block recurrent core between eight untied prelude blocks and eight untied coda blocks, P8R128C8P\_8R\_{12}^{8}C\_8P8​R128​C8​. We compare the two architectures at 58, 115, 230, and 460 tokens per parameter (TPP), corresponding to 42B, 84B, 168B, and 336B training tokens for the 730M-parameter models.

![](/image/attachment%3A1ebd2c15-4123-434f-ac9c-43750f365d78%3A%E6%88%AA%E5%B1%8F2026-07-27_22.03.20.png?table=block&id=3ade5119-12ec-8076-a0cc-cc173384b651&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Tab 2. Q1 envelope comparison at 460 TPP (730M parameters; 336B training tokens). Feedforward columns are references; bold compares only the loop variants, and Δ\\DeltaΔ is sandwich minus full-stack. Green and red text marks positive and negative changes, respectively.

ALT

Finding 1: The sandwich envelope improves instance-conditioned, multi-step answer derivation. Its largest and most consistent benefits occur on tasks that require quantitative, symbolic, or heterogeneous reasoning over the supplied input.

MATH500, BBH-CoT, and DROP favor the envelope across the training budgets, whereas the gain on GSM8K is also visible. In this architecture, recurrence is localized to the middle of the network: only R12R\_{12}R12​ is reapplied, and the coda decodes its hidden state only after the final iteration. This separation may allow the recurrent core to devote more of its capacity to iterative state refinement, while the untied prelude and coda specialize in input encoding and output decoding. This interpretation is consistent with prior theoretical and empirical evidence that repeated middle-layer computation can support multi-step reasoning \[3,11\].

![](/image/attachment%3A2dfd3333-5a15-457d-b8a6-8cd21633287f%3Aimage.png?table=block&id=3ade5119-12ec-80a1-a579-c8eff41fcf32&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Fig 5. Evaluation trajectories for the full-stack and middle-loop sandwich variants.

ALT

Finding 2: The sandwich envelope does not consistently improve knowledge-intensive or requirement-constrained tasks. Tasks that depend heavily on stored knowledge or strict output and interface requirements show mixed or negative changes.

Knowledge-intensive benchmarks depend substantially on information stored in the model parameters rather than evidence contained in the evaluated instance. Code-generation tasks also require derived computation, but success additionally depends on satisfying a precise executable specification and producing syntactically and semantically valid outputs. The observed pattern therefore bounds the benefit of the sandwich envelope: the results are consistent with improved reasoning over instance-provided information, but do not indicate better retrieval of learned knowledge or more reliable compliance with strict output contracts. Although the envelope benefits several reasoning benchmarks, that advantage alone is insufficient to improve the full mixture of capabilities required for code generation.

##### Q2: Does Input Injection Help?

Results. Input injection yields its clearest gains on tasks that rely heavily on prompt-provided context or specifications. It improves BBH-CoT, DROP, MMLU, and both coding benchmarks, but can reduce performance on quantitative reasoning tasks, particularly in the middle-loop architecture. Despite this trade-off, the complete middle-loop model with prelude-state injection outperforms full-stack Ouro with raw-token injection on eight of the ten benchmarks.

Persistent input injection gives every recurrent step a direct path back to the input, reducing the need for the evolving state to carry all prompt-relevant information across iterations and potentially improving gradient propagation. Prior work on recurrent-depth and fixed-point models uses related mechanisms to keep iterative states explicitly conditioned on the input \[3,5,8\]. We evaluate matched write-versus-no-write controls within two recurrent families, thereby isolating the effect of injection within each architecture.

Let x0\=Eθ(x)\\mathbf x\_0=E\_\\theta(\\mathbf x)x0​\=Eθ​(x) be the raw token-embedding stream and e\=Pθ(x0)\\mathbf e=P\_\\theta(\\mathbf x\_0)e\=Pθ​(x0​) the contextualized representation produced by untied prelude blocks. For a generic write source v\\mathbf vv, both controls use the same diagonal operator \[5\]

D(zt,v)\=α⊙zt+δ⊙Winv, δ\=softplus⁡(bδ), α\=exp⁡{−δ⊙exp⁡(a)}.D(\\mathbf z\_t,\\mathbf v)= \\boldsymbol\\alpha\\odot \\mathbf z\_t + \\boldsymbol\\delta\\odot \\mathbf W\_{\\mathrm{in}}\\mathbf v, \\, \\boldsymbol\\delta=\\operatorname{softplus}(\\mathbf b\_\\delta), \\, \\boldsymbol\\alpha=\\exp\\{-\\boldsymbol\\delta\\odot\\exp(\\mathbf a)\\}. D(zt​,v)\=α⊙zt​+δ⊙Win​v,δ\=softplus(bδ​),α\=exp{−δ⊙exp(a)}.

The middle loop writes the fixed contextualized state v\=e\\mathbf v=\\mathbf ev\=e before each recurrent-core pass. Full-stack Ouro has no untied prelude, so its corresponding intervention writes the raw token embeddings v\=x0\\mathbf v=\\mathbf x\_0v\=x0​ before each full-stack pass. Each write-versus-no-write pair isolates injection within one family.

Repeated writes make every update directly dependent on v\\mathbf vv, so the write source remains available after every preceding recurrent transformation. This direct path should be particularly useful when later computation must recover task instructions, contextual evidence, demonstrations, or specifications from the prompt.

![](/image/attachment%3A9b8a73a2-858d-49d2-ad85-b698e2e131a5%3Aimage.png?table=block&id=3ade5119-12ec-80df-9aac-cf811cd24fc3&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Tab 3. Recurrent input-injection controls at 460 TPP (730M parameters; 336B training tokens). For the middle loop, Δ\\DeltaΔ denotes prelude-injection minus no injection; for full-stack Ouro, it denotes raw-token injection minus no injection. Boldface compares models within the same family, while green and red values indicate positive and negative changes, respectively.

ALT

Finding 1: Input injection primarily benefits context-dependent and specification-constrained tasks.

![](/image/attachment%3Aa1f9c079-9375-47a5-bcd0-236448753e83%3Aimage.png?table=block&id=3ade5119-12ec-804a-aa24-e1a3464678eb&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Fig 6. Evaluation trajectories over matched token budgets for input-injection ablations. The upper two rows compare the middle loop without and with prelude injection; the lower two rows compare full-stack (Ouro\-style) recurrence without and with token embedding injection.

ALT

Within the middle-loop architecture, prelude-state injection improves MMLU by 2.53 points, BBH-CoT by 6.63 points, DROP by 1.39 points, HumanEval+ by 5.49 points, and MBPP+ by 4.23 points. Raw-token injection produces gains in the same broad capability groups for full-stack Ouro, including improvements of 1.79 points on MMLU, 1.80 points on BBH-CoT, 0.91 points on DROP, 2.44 points on HumanEval+, and 4.50 points on MBPP+.

These tasks depend heavily on information provided in the evaluated instance. HumanEval+ and MBPP+ require generated programs to satisfy prompt-supplied specifications; BBH-CoT provides worked examples; and DROP provides an answer-bearing passage. The consistent gains across both recurrent families therefore support the interpretation that persistent injection helps later recurrent computation retain access to task-relevant contextual information.

Finding 2: Prelude-state injection can impair quantitative reasoning.

The effect of injection is not uniformly positive. In the middle-loop model, prelude-state injection reduces MATH500 by 3.60 points and GSM8K by 2.51 points. The corresponding effects are less negative in full-stack Ouro: raw-token injection reduces MATH500 by 1.60 points and slightly improves GSM8K by 0.53 points.

This pattern suggests that repeatedly reintroducing a fixed contextualized representation may interfere with the iterative state transformations required for quantitative reasoning. One possible interpretation is that mathematical tasks benefit from allowing the recurrent state to progressively depart from the input representation as intermediate computations accumulate. Persistent prelude-state injection may instead continually pull the state back toward its input-conditioned representation. The present experiments establish the behavioral trade-off but do not isolate its mechanism, which may depend on the write strength, injection location, or interaction between the fixed prelude state and the evolving recurrent state.

Finding 3: Despite this trade-off, the complete injected middle-loop design outperforms injected full-stack Ouro on eight of ten benchmarks.

With their respective input-conditioning mechanisms enabled, the prelude–loop–coda model outperforms full-stack Ouro on eight of ten benchmarks, trailing only on ARC-Challenge and HellaSwag. The middle-loop model also remains stronger on MATH500 and GSM8K, even though prelude-state injection lowers its performance relative to the no-write control.

These results highlight the overall strength of the middle-loop design. The sandwich envelope and contextualized input access appear complementary on context-dependent and code-generation tasks, while the envelope advantage compensates for the negative effect of injection on quantitative reasoning. Overall, the prelude–loop–coda architecture provides the stronger foundation, although its input-injection mechanism could be further refined to better preserve mathematical reasoning performance.

##### Q3: Do Separate Recurrent Latent States Help?

Results. Additional latent-state structure provides no consistent benefit. Random initialization produces two gains and four losses exceeding one point. The H/L recurrent-state variant produces three gains and three losses exceeding one point, with the largest degradation occurring on MATH500.

After fixing the middle-loop topology and prelude-conditioned write, we vary only the organization of the recurrent latent state.

Random initialization completes the controlled transformation from the Ouro\-style design to the standard Huginn\-style configuration. The shared H/L-state variant then tests an additional hierarchical organization inspired by HRM-Text \[12\] and TRM \[13\]. Unlike HRM-Text, which uses separate modules for the H and L updates, our matched control shares a single recurrent body across both states.

We use H\=2H=2H\=2 high-level cycles and L\=3L=3L\=3 low-level updates per cycle. The resulting schedule applies the shared recurrent body eight times—six low-level updates and two high-level updates—matching the recurrent compute of the single-state control. Let e\=Pθ(x0)\\mathbf e=P\_\\theta(\\mathbf x\_0)e\=Pθ​(x0​) be the contextualized representation produced by the prelude; we compare three variants:

Input-initialized single state: z0\=e\\mathbf z\_0=\\mathbf ez0​\=e.

Random-initialized single state: z0\=ξ\\mathbf z\_0=\\boldsymbol{\\xi}z0​\=ξ, where each token state follows ξ∼N(0,Id/d)\\boldsymbol{\\xi}\\sim \\mathcal{N}(\\mathbf 0,\\mathbf I\_d/d)ξ∼N(0,Id​/d).

Shared high/low states: a high-level state is initialized from e\\mathbf ee, a low-level workspace is initialized from noise, and both states are updated by the same recurrent body according to an H/L schedule.

Let

Rˉθ(s;e)\=Rθ(Wθ(s,e))\\bar R\_\\theta(\\mathbf s;\\mathbf e) =R\_\\theta(W\_\\theta(\\mathbf s,\\mathbf e))Rˉθ​(s;e)\=Rθ​(Wθ​(s,e))

denote one application of the shared recurrent body preceded by the prelude-conditioned input write.

![](/image/attachment%3A51d0cabb-f016-4620-8ebe-697d3c260a98%3Aimage.png?table=block&id=3ade5119-12ec-8072-9502-c83a69113297&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Fig. 7 Shared high/low latent-state update. The same recurrent body alternates low-state refinements with a high-state update.

ALT

zH0\=e,zL0,0\=ξ,ξ∼N(0,Id/d),zLi,j+1\=Rˉθ(zLi,j+zHi;e),j\=0,…,L−1,zHi+1\=Rˉθ(zHi+zLi,L;e),zLi+1,0\=zLi,L,i\=0,…,H−1. \\begin{aligned} \\mathbf z\_{\\mathrm H}^{0} &= \\mathbf e, \\qquad \\mathbf z\_{\\mathrm L}^{0,0}=\\boldsymbol{\\xi},\\quad \\quad \\boldsymbol{\\xi}\\sim \\mathcal{N}(\\mathbf 0,\\mathbf I\_d/d), \\\\ \\mathbf z\_{\\mathrm L}^{i,j+1} &= \\bar R\_\\theta( \\mathbf z\_{\\mathrm L}^{i,j}+\\mathbf z\_{\\mathrm H}^{i}; \\mathbf e), \\qquad j=0,\\ldots,L-1, \\\\ \\mathbf z\_{\\mathrm H}^{i+1} &= \\bar R\_\\theta( \\mathbf z\_{\\mathrm H}^{i}+\\mathbf z\_{\\mathrm L}^{i,L}; \\mathbf e), \\qquad \\mathbf z\_{\\mathrm L}^{i+1,0}=\\mathbf z\_{\\mathrm L}^{i,L}, \\qquad i=0,\\ldots,H-1 . \\end{aligned} zH0​zLi,j+1​zHi+1​​\=e,zL0,0​\=ξ,ξ∼N(0,Id​/d),\=Rˉθ​(zLi,j​+zHi​;e),j\=0,…,L−1,\=Rˉθ​(zHi​+zLi,L​;e),zLi+1,0​\=zLi,L​,i\=0,…,H−1.​

Thus, each low-level update receives the current high-level state through additive conditioning before entering the shared recurrent body, while each high-level update analogously receives the final low-level state from the corresponding cycle.

Finding 1: Random initialization is not a necessary ingredient for loop language models.

Random initial states are widely used in iterative models \[3,7\], partly because they are thought to encourage path independence on algorithmic equilibrium tasks \[14\]. We argue, however, that random initialization should instead be viewed as a task- and objective-dependent inductive bias, rather than as a universally beneficial design choice.

Relative to direct initialization with z0\=e\\mathbf z\_0=\\mathbf ez0​\=e, random initialization improves ARC-Challenge by 3.34 points and GSM8K by 1.22 points. However, it reduces performance by more than one point on MMLU, MATH500, HumanEval+^{+}+ and MBPP+^{+}+, while the differences on the remaining four benchmarks are within one point.

To our knowledge, prior work has not isolated the effect of random initialization in a matched, large-scale, finitely unrolled language model with persistent input injection. Across our evaluations, random initialization produces improvements exceeding one point on two benchmarks but degradations exceeding one point on four, providing no evidence of a consistent cross-task advantage in this setting. Direct initialization performs better on six of the ten benchmarks and also avoids the additional computation associated with sampling a separate initial state. These results should not, however, be interpreted as evidence against random initialization in general: our evaluations do not directly measure multi-start path independence or extrapolation to recurrent depths beyond those used during training.

![](/image/attachment%3A5d952adb-935a-4f16-9ad7-8e1dfeb0fe3a%3A%E6%88%AA%E5%B1%8F2026-07-28_01.40.26.png?table=block&id=3ade5119-12ec-8082-a8af-e38b4e13bc70&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Tab 4. Matched recurrent-state comparison at 460 TPP (730M parameters; 336B training tokens). Bold marks the best available score.Δ\\DeltaΔ is shared high/low (H/L\\mathrm{H/L}H/L) minus the input-initialized single state ( z0\=e\\mathbf z\_0=\\mathbf ez0​\=e ). Green and red text mark positive and negative changes.

ALT

Finding 2: A shared-module H/L hierarchy provides no consistent benefit.

![](/image/attachment%3A667708d7-7379-463b-82ff-449f0ff4589f%3A%E6%88%AA%E5%B1%8F2026-07-28_18.12.42.png?table=block&id=3ade5119-12ec-805c-babc-f18e71467bf5&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Fig. 8 Evaluation benchmark trajectories for the three latent-state organizations.

ALT

HRM \[15\] introduces an H/L hierarchy through a brain-inspired separation of timescales. A fast L module repeatedly refines a local state under a fixed H-level context, after which a slower H module updates that context and initiates a new phase of low-level refinement. This alternating schedule is intended to sustain effective computational depth. HRM-Text adapts the same two-cycle, three-L-update schedule to language modeling and combines it with MagicNorm, warmup credit assignment, and PrefixLM training.

Existing evidence for the value of the H/L hierarchy is mixed. An L-only model matches HRM on Sudoku \[16\], whereas TRM reports improvements from combining two recurrent states with shared weights on Sudoku-Extreme \[13\]. At language-model scale, HRM-Text compares a separate-module HRM architecture with a shared-weight TRM-style alternative \[12\]. However, these comparisons also vary the update rule, effective depth, parameter count, or computational budget, making it difficult to isolate the contribution of the state hierarchy itself.

Our control holds the recurrent body, number of recurrent-body applications, input injection, parameter count, and training budget fixed. It introduces only a second recurrent state and the H/L update schedule, with the same recurrent module shared across both states. Under this matched setting, the hierarchy yields gains exceeding one point on three benchmarks and losses exceeding one point on three, while substantially degrading MATH500. Thus, the additional state and scheduling complexity provides no consistent aggregate benefit when the H and L updates share a recurrent module.

This conclusion is specific to the shared-module setting. It does not rule out benefits from the separately parameterized H and L modules used by HRM-Text. A closer HRM-Text-style variant with distinct modules for the two update streams is still under evaluation and is not included in the present comparison.

#### Summary

The sandwich envelope and persistent input injection account for the broadest gains along the controlled construction path, whereas introducing a randomly or separately initialized recurrent state provides no consistent additional benefit.

The figure below shows that the sandwich envelope and persistent input injection drive the gains, while a separate random-initialized latent state provides no consistent further benefit.

![](/image/attachment%3A6157e5da-420c-4e25-b8d8-96e1be58bb9a%3A%E6%88%AA%E5%B1%8F2026-07-28_15.24.03.png?table=block&id=3ade5119-12ec-80f4-9e4a-fb11d39e8552&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Fig. 9 Raw benchmark scores along the cumulative dense construction path at 336B training tokens. Starting from full-stack Ouro (O)(\\mathrm{O})(O), the stages add the untied prelude/coda sandwich envelope (+P/C)(+\\mathrm{P/C})(+P/C), prelude-conditioned input injection (+W)(+\\mathrm{W})(+W), and a separate random-initialized recurrent state (+z)(+z)(+z), yielding complete Huginn\-style looped models. Horizontal lines show the matched (D28)(D\_{28})(D28​) and (D112)(D\_{112})(D112​) feedforward references.

ALT

The stepwise results distinguish the contributions of the three design changes. The sandwich envelope produces the clearest gains on mathematical and multi-step reasoning tasks. Persistent input injection produces its largest additional gains on BBH-CoT and code generation, while also improving DROP and MMLU.

Introducing a separately random-initialized recurrent state has mixed effects and reverses some of the preceding gains on several benchmarks. Under this construction order, the results suggest that the broad advantage of Huginn over Ouro is driven mainly by localized recurrence and repeated access to a contextualized input representation.

### 4\. Transfer to MoE Models

Results. 1) The Huginn\-style MoE retains its dense-setting advantage over Ouro. 2) It achieves more balanced expert utilization, and iteration-specific expert selection contributes to performance. 3) Although the feedforward MoE leads overall, Huginn surpasses it on DROP and GSM8K, matches it on MATH500, and substantially narrows the recurrent-to-feedforward gap relative to the dense setting.

#### 4.1 Configurations for MoE Comparison

We replace the FFN in every physical layer of the two complete loop architectures with a mixture-of-experts (MoE) layer. The Ouro\-style model retains full-stack recurrence and an input-initialized recurrent state. The Huginn-style model retains the sandwich envelope, prelude-conditioned input writes, and random state initialization.

Both recurrent models contain 28 routed physical layers with 25 experts, top-2 routing, and expert width 2432. Each has 8.0B resident parameters and 793.9M active parameters per physical pass. Unrolling the recurrent computation yields approximately 3.2B active parameter applications per token. A 112-layer feedforward model without cross-layer weight sharing, denoted D112MoED\_{112}^{\\mathrm{MoE}}D112MoE​, provides a reference matched in logical depth and active compute, with 32.0B resident parameters. All MoE models use dot-product load-balancing loss without router bias.

#### 4.2 Huginn\-Style MoE versus Ouro

Finding 1: The Huginn\-style advantage over Ouro transfers to MoE models. Huginn scores higher on eight of ten benchmarks; five of these gains exceed one point, with its largest gains on GSM8K (+4.70) and MATH500 (+3.60).

![](/image/attachment%3A0cfcd9d0-20e6-4ce9-b35d-cda28a9d0994%3A%E6%88%AA%E5%B1%8F2026-07-28_15.42.34.png?table=block&id=3ade5119-12ec-80b2-b99b-cf972a0663cc&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Tab 5. Benchmark performance of loop MoE models and the feedforward MoE reference after training on 500B tokens. The looped models contain 8.0B resident and 793.9M active parameters per physical pass, corresponding to approximately 630 training tokens per active parameter. Bold compares only the recurrent rows; Δ\\DeltaΔ is Huginn MoE minus Ouro MoE; green and red mark positive and negative changes, respectively.

ALT

The table above shows that the endpoint difference is not uniform across tasks. Within the general benchmarks, the clearest gains for Huginn are on MMLU (+2.78) and DROP (+1.95). Its leads on HellaSwag and TriviaQA are only 0.28 and 0.07 points, respectively, while Ouro is higher on ARC-Challenge by 0.86 points and on BBH-CoT by 0.20.

The separation is larger on mathematical reasoning. Huginn improves over Ouro by 3.60 points on MATH500 and 4.70 on GSM8K. The code differences are smaller: +1.22 on HumanEval+ and +0.53 on MBPP+. Overall, the transfer advantage is concentrated on mathematical reasoning, with additional gains on MMLU and DROP, while performance on the remaining benchmarks is broadly comparable.

#### 4.3 Routing Diagnostics

We compare normalized load-balancing loss across the two recurrent models and the feedforward reference. Uniform routing has a loss of one; lower values therefore indicate more even expert utilization.

![](/image/attachment%3Aab854923-2c71-444e-8b4b-594192e9fb16%3A%E6%88%AA%E5%B1%8F2026-07-28_18.17.01.png?table=block&id=3ade5119-12ec-8090-8ca5-c96c2dac1ad0&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Fig. 10 Normalized MoE load-balancing loss across training for the recurrent models and the 112-layer feedforward MoE reference (lower is better). Curves show 0.5B-token bin medians after robust smoothing. At 500B tokens, Huginn remains below both comparators, and the feedforward reference lies between Huginn and Ouro.

ALT

Finding 2: The Huginn MoE exhibits the lowest load-balancing loss at 500B tokens: 1.571, compared with 1.652 for the feedforward reference and 1.899 for Ouro. This indicates more even expert utilization.

We find that the Huginn MoE exhibits a substantially lower load-balancing loss, indicating more even expert utilization. The figure below further shows that the distribution of top-2 expert activations varies across loop iterations. This variation is functionally important: forcing iterations 2–8 to reuse the expert identities selected at iteration 1, while retaining iteration-specific mixture weights, reduces accuracy on all six evaluated tasks. This intervention provides causal evidence that iteration-specific expert selection contributes to model performance.

![](/image/attachment%3Aa266ea71-2b95-44e5-81fa-4cc6e08e90ba%3Aimage.png?table=block&id=3ade5119-12ec-8074-9068-c43923aa5d45&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=390&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

![](/image/attachment%3A3de950e6-fa99-42f3-9a0b-e20010be9a0b%3A%E6%88%AA%E5%B1%8F2026-07-28_18.33.55.png?table=block&id=3ade5119-12ec-80ba-8570-fd0808bd975b&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=890&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

#### 4.4 Huginn\-MoE versus Feedforward MoE

We compare Huginn with the 112-layer feedforward MoE under the same logical depth and active-compute budget. We further compare the loop-to-feedforward performance gaps in the dense and MoE settings.

Finding 3: MoE substantially narrows the performance gap between Huginn and its feedforward counterpart. The feedforward MoE leads on seven of ten benchmarks, whereas Huginn leads on DROP and GSM8K and matches it on MATH500. Across MATH500, GSM8K, HumanEval+, and MBPP+, Huginn averages 61.48, compared with 62.79 for the feedforward reference.

The figure below compares the dense and MoE performance gaps between Huginn and their respective 112-layer feedforward references. In panel (a), the MoE gap is smaller on eight of the nine directly comparable benchmarks, reducing the mean gap from 4.964.964.96 to 1.711.711.71 points. Panel~(b) shows that this pattern holds throughout training: when evaluated on the same seven benchmarks, the MoE gap is smaller at all four checkpoints.

![](/image/attachment%3A665ff943-402a-4b53-ae40-a8525f67738c%3Aimage.png?table=block&id=3ade5119-12ec-80c2-bf8f-fdcb63afa3eb&spaceId=561e5119-12ec-8147-b9c3-0003fdfb61f7&width=1410&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

Fig. 11 Dense and MoE gaps to the 112-layer feedforward references. For each model family f∈{dense,MoE}f\\in\\{\\mathrm{dense},\\mathrm{MoE}\\}f∈{dense,MoE},gf\=S(D112f)−S(Huginnf)g\_f=S(D\_{112}^{f})-S(\\textit{Huginn}^{f})gf​\=S(D112f​)−S(Huginnf); positive values favor the feedforward reference. Panel(a) compares the individual benchmark gaps at the shared endpoint. Each green or red Δ\\DeltaΔ is gMoE−gdenseg\_{\\mathrm{MoE}}-g\_{\\mathrm{dense}}gMoE​−gdense​, so negative values indicate that MoE narrows the recurrent-to-feedforward gap. Panel(b) follows the same gap comparison over training on the fixed seven-task intersection (ARC-C, HSwag, MMLU, BBH-CoT, TQA, DROP, and HumanEval+^++).

ALT

#### 4.5 Summary

First, the Huginn\-style MoE outperforms Ouro on eight of ten benchmarks, with its largest gains on GSM8K and MATH500 and additional gains exceeding one point on MMLU, DROP, and HumanEval+. This shows that the advantage observed in the dense setting transfers to MoE models.

Second, Huginn achieves more balanced expert utilization, and intervention experiments show that iteration-specific expert selection contributes meaningfully to performance.

Third, MoE substantially narrows the performance gap between Huginn and its feedforward counterpart. Although the feedforward baseline leads overall, Huginn outperforms it on DROP and GSM8K, matches it on MATH500, and reduces the mean gap from 4.96 points in the dense setting to 1.71 points in the MoE setting.

### Conclusions

We compare full-stack and middle-loop language models by disentangling three design choices that standard Ouro\- and Huginn\-style recipes vary simultaneously: the iteration envelope, input injection, and latent-state organization. Under matched parameter scale, logical depth, and training-token budget, we find that the prelude–loop–coda sandwich architecture improves performance on mathematical reasoning, context extraction, and other reasoning-intensive tasks. Input injection primarily benefits knowledge retrieval and context access, while contributing little to quantitative reasoning. Random state initialization yields mixed results, whereas the shared H/L hierarchy provides no consistent benefit.

Our MoE transfer study evaluates the two complete architectures in a modern sparse-model setting and shows that the advantages of the Huginn\-style architecture persist. The Huginn MoE achieves more balanced expert utilization and approaches—and on some tasks surpasses—the performance of its feedforward MoE counterpart, despite being trained from scratch under the same data budget and matched memory and FLOP constraints.

More broadly, the architectural design space of looped models remains underexplored and calls for substantially more controlled ablation studies. Meaningful comparisons therefore require carefully designed, apples-to-apples evaluations that match parameter scale, training budget, inference cost, and evaluation protocol. Many important questions remain open, including how loop architectures interact with conditional sparsity and how architecture–system co-design can further advance their performance–efficiency Pareto frontier.

### Reference

\[1\] Amir Gholami, Zhewei Yao, Sehoon Kim, Coleman Hooper, Michael W. Mahoney, and Kurt Keutzer. Ai and memory wall, 2024.

\[2\] Rui-Jie Zhu, Zixuan Wang, Kai Hua, Tianyu Zhang, Ziniu Li, Haoran Que, Boyi Wei, Zixin Wen, et al. Scaling latent reasoning via looped language models. arXiv preprint arXiv:2510.25741, 2025.

\[3\] Jonas Geiping, Sean McLeish, Neel Jain, John Kirchenbauer, Siddharth Singh, Brian R. Bartoldson, Bhavya Kailkhura, Abhinav Bhatele, and Tom Goldstein. Scaling up test-time compute with latent reasoning: A recurrent depth approach. arXiv preprint arXiv:2502.05171, 2025.

\[4\] Kristian Schwethelm, Daniel Rueckert, and Georgios Kaissis. How much is one recurrence worth? iso-depth scaling laws for looped language models. arXiv preprint arXiv:2604.21106, 2026.

\[5\] Hayden Prairie, Zachary Novack, Taylor Berg-Kirkpatrick, and Daniel Y. Fu. Parcae: Scaling laws for stable looped language models. arXiv preprint arXiv:2604.12946, 2026.

\[6\] Harsh Kohli, Srinivasan Parthasarathy, Huan Sun, and Yuekun Yao. Loop, think, & generalize: Implicit reasoning in recurrent-depth transformers. arXiv preprint arXiv:2604.07822, 2026.

\[7\] Benhao Huang, Zhengyang Geng, and Zico Kolter. Equilibrium reasoners: Learning attractors enables scalable reasoning. arXiv preprint arXiv:2605.21488, 2026.

\[8\] Asher Labovich. Stability and generalization in looped transformers. arXiv preprint arXiv:2604.15259, 2026.

\[9\] Nikunj Saunshi, Nishanth Dikkala, Zhiyuan Li, Sanjiv Kumar, and Sashank J. Reddi. Reasoning with latent thoughts: On the power of looped transformers. arXiv preprint arXiv:2502.17416, 2025.

\[10\] Róbert Csordás, Kazuki Irie, Jürgen Schmidhuber, Christopher Potts, and Christopher D. Manning. MoEUT:Mixture-of-experts universal transformers. In Advances in Neural Information Processing Systems, 2024.

\[11\] Victor Conchello Vendrell, Arnau Padres Masdemont, Niccolò Grillo, Jordi Ros-Giralt, Arash Behboodi, and Fabio Valerio Massoli. Memory-efficient looped transformer: Decoupling compute from memory in looped language models. arXiv preprint arXiv:2605.07721, 2026.

\[12\] Wang, G., Liu, C., Wang, C., Zhou, C., Sun, Y., Wu, Y., ... & Yadkori, Y. A. (2026). HRM-Text: Efficient Pretraining Beyond Scaling. arXiv preprint arXiv:2605.20613.

\[13\] Jolicoeur-Martineau, A. (2025). Less is more: Recursive reasoning with tiny networks. arXiv preprint arXiv:2510.04871.

\[14\] Cem Anil, Ashwini Pokle, Kaiqu Liang, Johannes Treutlein, Yuhuai Wu, Shaojie Bai, J. Zico Kolter, and Roger B. Grosse. Path independent equilibrium models can better exploit test-time computation. In Advances in Neural Information Processing Systems, volume 35, 2022.

\[15\] Wang, G., Li, J., Sun, Y., Chen, X., Liu, C., Wu, Y., ... & Yadkori, Y. A. (2025). Hierarchical reasoning model. arXiv preprint arXiv:2506.21734.

\[16\] Renee Ge, Qianli Liao, and Tomaso Poggio. Hierarchical reasoning model: A critical supplementary material. arXiv preprint arXiv:2510.00355, 2025.

\[17\] Shuzhen Li, Yifan Zhang, Jiacheng Guo, Quanquan Gu, and Mengdi Wang. DeepLoop: Depth scaling for looped transformers. arXiv preprint arXiv:2607.13491, 2026.

\[18\] Zitian Gao, Yilong Chen, Yihao Xiao, Xinyu Yang, Ran Tao, Joey Zhou, and Bryan Dai. Loop the loopies! arXiv preprint arXiv:2607.16051, 2026.

\[19\] Liping Tang, Nikhil Ranjan, Omkar Pangarkar, Xuezhi Liang, Zhen Wang, Li An, Bhaskar Rao, Linghao Jin, Huijuan Wang, Zhoujun Cheng, Suqi Sun, Cun Mu, Victor Miller, Xuezhe Ma, Yue Peng, Zhengzhong Liu, and Eric P. Xing. TxT360: A top-quality LLM pre-training dataset requires the perfect blend, 2024

<iframe src="https://embed.notionlytics.com/wt/ZXlKM2IzSnJjM0JoWTJWVWNtRmphMlZ5U1dRaU9pSmtURUozYlV0eVdrTlNkemRpYUhkaWFEaFpieUlzSW5CaFoyVkpaQ0k2SWpOaFpHVTFNVEU1TVRKbFl6Z3hNamc1T0Rka1ptVmlOMkUxTlRnd01EUXpJbjA9" frameborder="0" sandbox="allow-scripts allow-popups allow-top-navigation-by-user-activation allow-forms allow-same-origin allow-storage-access-by-user-activation allow-popups-to-escape-sandbox" allowfullscreen="" referrerpolicy="strict-origin-when-cross-origin" style="position: absolute; inset-inline-start: 0px; top: 0px; width: 100%; height: 100%; border-radius: 1px; pointer-events: auto; background-color: var(--c-bacPri);"></iframe>

![Husky Doge](https://img.notionusercontent.com/ext/https%3A%2F%2Flh3.googleusercontent.com%2Fa%2FACg8ocLXoiUobsLg95L_LqV9gJIcZvL8b9BHYFmMsrM-3nOn4AlovTw%3Ds100/raw?imgBuildSrc=createUnsignedImageVariantURL)

Husky Doge

Jul 31

Please see preliminary section for detailed definitions

![Husky Doge](https://img.notionusercontent.com/ext/https%3A%2F%2Flh3.googleusercontent.com%2Fa%2FACg8ocLXoiUobsLg95L_LqV9gJIcZvL8b9BHYFmMsrM-3nOn4AlovTw%3Ds100/raw?imgBuildSrc=createUnsignedImageVariantURL)

Husky Doge

Jul 31

Also this post: [https://x.com/sakurayukiai/status/2072727795138965528?s=20](https://x.com/sakurayukiai/status/2072727795138965528?s=20)
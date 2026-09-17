---
type: Concept
title: DeepSeek-V3 Architecture and Evaluation
description: 671B/37B MLA plus auxiliary-loss-free DeepSeekMoE with D=1 MTP, 14.8T pretraining with YaRN 128K and R1-distilled SFT/GRPO, and base plus chat benchmark evidence.
tags: [deepseek-v3, mla, moe, load-balancing, mtp, reasoning-distillation, evaluation]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: v3-report
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: DeepSeek-V3 Technical Report
  - id: v3-base-eval
    resource: ../raw/arXiv-2412.19437v2/tables/base_evaluation.tex
    title: DeepSeek-V3 base evaluation table
  - id: v3-chat-eval
    resource: ../raw/arXiv-2412.19437v2/tables/chat_evaluation.tex
    title: DeepSeek-V3 chat evaluation table
---

DeepSeek-V3 is a 671B-total / 37B-activated MoE language model combining Multi-head Latent Attention (MLA) with DeepSeekMoE, auxiliary-loss-free load balancing, and a 1-depth Multi-Token Prediction (MTP) objective, pretrained on 14.8T tokens and post-trained with R1-distilled SFT plus GRPO to reach then-strongest open-source base and chat results near GPT-4o and Claude-3.5-Sonnet[^v3-report].

## Model snapshot

61 Transformer layers, hidden size 7168, parameters randomly initialized with std 0.006, with RMSNorm after compressed latents and scaling at width bottlenecks as in DeepSeek-V2[^v3-report].

MoE applies to all FFNs except the first three layers: 1 shared expert plus 256 routed experts of intermediate size 2048, with 8 routed experts activated per token and node-limited routing to at most 4 nodes[^v3-report].

## Multi-head Latent Attention

Attention uses MLA with 128 heads, per-head dimension 128, KV compression dimension 512, query compression dimension 1536, and decoupled RoPE per-head dimension 64[^v3-report].

Only the compressed KV latent `c_t^KV` and decoupled RoPE key `k_t^R` are cached during generation, sharply reducing KV cache versus MHA while keeping comparable quality; query-side low-rank compression additionally reduces training activation memory[^v3-report].

## DeepSeekMoE with auxiliary-loss-free balancing

Token-to-expert affinity uses sigmoid plus normalization over the selected Top-K gating values, differing slightly from DeepSeek-V2[^v3-report].

Load balancing primarily avoids auxiliary-loss pressure on performance by adding a per-expert bias `b_i` only to the routing decision `s_i,t + b_i`, while the gating weight still comes from the original affinity `s_i,t`[^v3-report].

Biases adapt each step: decreased by `gamma` when an expert is overloaded and increased by `gamma` when underloaded; `gamma` is 0.001 for the first 14.3T tokens and 0.0 for the final 500B tokens[^v3-report].

A small complementary sequence-wise balance loss with `alpha=0.0001` only prevents extreme imbalance within a single sequence[^v3-report].

Because balance holds through training, DeepSeek-V3 drops no tokens in training, and paired deployment strategies mean no token dropping in inference either[^v3-report].

Batch-wise balancing is more flexible than sequence-wise balancing because it does not enforce per-sequence domain balance, allowing stronger expert specialization; Pile-test expert-load plots show greater specialization for the auxiliary-loss-free model[^v3-report].

The same performance advantage can be reproduced with a batch-wise auxiliary loss at matched batch balance: on 1B MoE models validation loss is 2.258 sequence-wise versus 2.253 auxiliary-loss-free and 2.253 batch-wise, and on 3B models 2.085 versus 2.080 and 2.080[^v3-report].

Remaining efficiency risks are small-batch or single-sequence imbalance and domain-shift imbalance at inference; the paper relies on large EP/DP micro-batches and redundant-expert inference deployment to address them[^v3-report].

## Multi-Token Prediction

MTP depth `D` is 1: besides the exact next token, each position predicts one additional token[^v3-report].

Unlike parallel independent heads, DeepSeek-V3 predicts additional tokens sequentially and preserves the full causal chain at each depth; the principle resembles EAGLE, but the goal here is stronger main-model training rather than speculative decoding[^v3-report].

Each MTP module combines the previous-depth representation with the embedding of the future token via projection `M_k` over RMSNormed inputs, passes it through a Transformer block, and predicts with the main-model-shared embedding and output head[^v3-report].

The extra objective is the depth-averaged cross-entropy scaled by `lambda`, with `lambda=0.3` for the first 10T tokens and 0.1 for the remaining 4.8T tokens[^v3-report].

MTP modules can be discarded at inference with no inference-cost change, or repurposed for speculative decoding; the reported second-token acceptance is 85–90% across generation topics for about 1.8x tokens per second[^v3-report].

## Pretraining data and schedule

The corpus is 14.8T high-quality diverse tokens with increased math and programming ratios, broader multilingual coverage beyond English and Chinese, reduced redundancy, and document packing without cross-sample attention masking[^v3-report].

Pretraining includes Fill-in-Middle with the Prefix-Suffix-Middle format at rate 0.1, matching DeepSeekCoder-V2 practice[^v3-report].

The tokenizer is byte-level BPE with 128K vocabulary, improved multilingual compression, and punctuation-plus-linebreak tokens; a random split of some combined tokens during training mitigates token-boundary bias on multi-line prompts without terminal line breaks[^v3-report].

Training uses AdamW with `beta_1=0.9`, `beta_2=0.95`, weight decay 0.1, maximum sequence length 4K, gradient-clip norm 1.0, and batch size growing from 3072 to 15360 over the first 469B tokens before staying at 15360[^v3-report].

The learning-rate schedule warms up from 0 to `2.2e-4` over 2K steps, holds constant to 10T tokens, cosine-decays to `2.2e-5` over 4.3T tokens, then holds `2.2e-5` for 333B and switches to `7.3e-6` for the final 167B tokens[^v3-report].

## Long-context extension

YaRN is applied only to the decoupled shared key `k_t^R`, with scale 40, `alpha=1`, `beta=32`, and `sqrt(t)=0.1 ln s + 1`[^v3-report].

Two 1000-step phases extend 4K to 32K with batch size 1920 and then to 128K with batch size 480, both at learning rate `7.3e-6`; post-SFT Needle-in-a-Haystack remains robust to 128K[^v3-report].

## Post-training

SFT uses 1.5M multi-domain instances for two epochs with cosine decay from `5e-6` to `1e-6`, packing multiple samples per sequence with sample masking to keep examples mutually invisible[^v3-report].

Reasoning data comes from an internal DeepSeek-R1 model via domain-specific SFT-plus-RL expert generators: each instance yields `<problem, original response>` and `<system prompt, problem, R1 response>` forms, where the system prompt elicits reflection and verification; high-temperature RL sampling merges R1 and original patterns, followed by rejection sampling for concise final SFT data[^v3-report].

Non-reasoning data uses DeepSeek-V2.5 generations checked by human annotators[^v3-report].

RL uses both rule-based rewards where verifiable, such as boxed math answers and LeetCode compiler tests, and model-based rewards for free-form or open-ended answers; the reward model starts from V3 SFT checkpoints and includes reward-chain-of-thought preference data to reduce hacking[^v3-report].

Policy optimization uses Group Relative Policy Optimization (GRPO) without a same-size critic, estimating the baseline from group scores with advantage normalization and a KL penalty against a reference model, across coding, math, writing, role-play, and QA prompts[^v3-report].

For broad subjective domains the paper reports using constitutional-AI style self-feedback from DeepSeek-V3 voting results, treating the LLM as a reward processor over unstructured supplementary inputs[^v3-report].

## Base-model evaluation

Evaluation uses the internal HAI-LLM framework: perplexity-based scoring for sets such as HellaSwag, PIQA, WinoGrande, RACE, MMLU variants, ARC, C-Eval, CMMLU, C3, and CCPM; generation-based scoring for TriviaQA, NaturalQuestions, DROP, MATH, GSM8K, MGSM, HumanEval, MBPP, LiveCodeBench-Base, CRUXEval, BBH, AGIEval, CLUEWSC, CMRC, and CMath; and Bits-Per-Byte on Pile-test for tokenizer fairness[^v3-report].

DeepSeek-V3-Base is reported as the strongest open-source base model at the time, outperforming DeepSeek-V2-Base and Qwen2.5-72B-Base despite using about half the activated parameters of the latter, and beating LLaMA-3.1-405B-Base on most benchmarks despite about one-eleventh the activated parameters, especially on multilingual, code, and math tasks[^v3-report][^v3-base-eval].

Selective paper-reported base scores include MMLU 87.1, MMLU-Redux 86.2, MMLU-Pro 64.4, BBH 87.5, DROP 89.0, HumanEval 65.2, MBPP 75.4, LiveCodeBench-Base 19.4, MATH 61.6, GSM8K 89.3, CMath 90.7, C-Eval 90.1, and non-English MMMLU 79.4[^v3-base-eval].

Training efficiency is reported as 180K H800 GPU hours per trillion tokens, much cheaper than training 72B or 405B dense models under their framework[^v3-report].

## Chat-model evaluation

Chat comparison covers DeepSeek-V2-0506, DeepSeek-V2.5-0905, Qwen2.5-72B-Instruct, LLaMA-3.1-405B-Instruct, Claude-3.5-Sonnet-1022, and GPT-4o-0513, with at most 8192 output tokens per benchmark; small benchmarks use repeated temperature-varied runs[^v3-chat-eval].

DeepSeek-V3 is reported as the best open-source chat model and competitive with frontier closed models[^v3-report][^v3-chat-eval].

Selective paper-reported chat scores include MMLU 88.5, MMLU-Redux 89.1, MMLU-Pro 75.9, DROP 91.6, GPQA-Diamond 59.1, LongBench-v2 48.7, HumanEval-Mul 82.6, LiveCodeBench CoT 40.5 and non-CoT 37.6, Codeforces 51.6th percentile, SWE-Verified 42.0, Aider-Polyglot 49.6, AIME-2024 39.2, MATH-500 90.2, CNMO-2024 43.2, C-Eval 86.5, and Chinese SimpleQA 64.8[^v3-chat-eval].

Notable trade-offs: English SimpleQA 24.9 trails GPT-4o and Claude-Sonnet because more training tokens target Chinese knowledge, while Chinese SimpleQA leads Qwen2.5-72B by 16.4 points despite Qwen using about 18T versus 14.8T tokens; engineering coding trails Claude-Sonnet-3.5-1022 but leads open models by a wide margin[^v3-report][^v3-chat-eval].

Open-ended judging with GPT-4-Turbo-1106 gives Arena-Hard 85.5 and AlpacaEval-2.0 length-controlled win rate 70.0, reported as the first open-source model above 85% on Arena-Hard and on par with Claude-Sonnet-3.5-1022 for complex prompts[^v3-report].

As a generative reward model, DeepSeek-V3 averages 87.0 on RewardBench, near GPT-4o-0806 and Claude-3.5-Sonnet-1022, rising to 89.6 with 6-vote majority; the paper uses V3-plus-voting for self-feedback on open-ended alignment[^v3-report].

## Ablations and distillation trade-off

MTP ablations at 15.7B parameters on 1.33T tokens and 228.7B parameters on 540B tokens show consistent gains on most benchmarks at identical inference cost because the MTP head is discarded, with especially large HumanEval, GSM8K, and MATH improvements[^v3-report].

Auxiliary-loss-free ablations at 15.7B on 1.33T and 228.7B on 578B tokens show consistent gains over purely auxiliary-loss balancing on most benchmarks, including Pile BPB, BBH, HumanEval, GSM8K, and MATH[^v3-report].

Distilling R1 into a DeepSeek-V2.5 baseline raises LiveCodeBench-CoT from 31.1 to 37.4 and MATH-500 from 74.6 to 83.2, but lengthens average responses from 718 to 783 tokens and from 769 to 1510 tokens respectively, so V3 selects settings balancing accuracy against output length[^v3-report].

## Relationships

- Uses [DeepSeek-V3 FP8 Training and Deployment Systems](deepseek-v3-systems.md) — efficiency, deployment, cost, and hardware-request context for this architecture and its evaluation claims.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — serving-side MTP speculation counterpart to V3's sequentially chained training-time MTP heads.
- Related to [Speculative Decoding Foundations](speculative-decoding-foundations.md) — draft-verify-accept framing for reusing V3 MTP heads to reach about 1.8x tokens per second.
- Related to [Distributed Inference Optimization Levers](distributed-inference-optimization-levers.md) — workload guidance noting jointly trained MTP heads such as V3 can exceed 80% acceptance out of the box.
- Related to [Over-Tokenized Transformer with Over-Encoding](over-tokenized-transformer.md) — later work building on V3-style conditional recursive MTP-DS alongside over-encoding.
- Related to [SGLang Expert Parallelism](sglang-expert-parallelism.md) — expert-parallel serving context relevant to V3's 256-expert, 8-active MoE with node-limited routing.

## Contradictions

- No cross-source contradiction was found during ingest; the following are paper-internal nuances rather than resolved disputes.
- Large-scale MTP and auxiliary-loss-free ablations slightly regress MMLU while improving most other metrics: MTP large-scale MMLU 67.5 baseline versus 66.6 with MTP, and auxiliary-loss-free large-scale MMLU 68.3 versus 67.2, indicating the headline gains are broad but not uniform[^v3-report].
- The paper notes DeepSeek-V2-Base numbers differ slightly from earlier reports because the internal evaluation framework changed, so cross-report comparisons need matching evaluation settings[^v3-report].

## Coverage limits

- PDF figures under `raw/arXiv-2412.19437v2/figures/` were not visually inspected; structural and performance claims follow LaTeX prose, equations, and input tables.
- All benchmark scores are paper-reported internal-framework measurements, not independently verified.
- Training-cost figures exclude prior research and ablation experiments and assume a $2 per H800-hour rental price; see the systems companion for the full cost breakdown.

[^v3-report]: DeepSeek-V3 Technical Report — `../raw/arXiv-2412.19437v2/main.tex`, covering MLA, DeepSeekMoE with auxiliary-loss-free balancing, MTP, pretraining, SFT/GRPO, and architecture/training claims.
[^v3-base-eval]: DeepSeek-V3 base evaluation table — `../raw/arXiv-2412.19437v2/tables/base_evaluation.tex`, covering base benchmark scores.
[^v3-chat-eval]: DeepSeek-V3 chat evaluation table — `../raw/arXiv-2412.19437v2/tables/chat_evaluation.tex`, covering chat benchmark scores.

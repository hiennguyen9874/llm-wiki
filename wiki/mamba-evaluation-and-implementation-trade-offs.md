---
type: Concept
title: Mamba evaluation and implementation trade-offs
description: Mamba’s author-run results report strong language, synthetic, genomic, and speech performance plus efficient fused scans, bounded by workload, modality, and hardware-specific evidence.
tags: [evaluation, efficiency, mamba, ssm, long-context]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T04:51:57Z }
sources:
  - id: gu-dao-2023
    resource: ../raw/2312.00752_Mamba/main.tex
    title: "Mamba: Linear-Time Sequence Modeling with Selective State Spaces"
---

# Mamba evaluation and implementation trade-offs

The Mamba paper reports that selective SSMs outperform its LTI SSM baselines on selected language and discrete long-context tasks, while a fused parallel scan makes the time-varying recurrence practical on an A100. The same paper finds that selection can hurt raw long-form audio modeling, so neither its quality nor efficiency results are universal.[^gu-dao-2023]

## Reported quality evidence

- **Language:** In Chinchilla-style Pile scaling experiments from about 125M to 1.3B parameters, the authors report that Mamba matches their strong Transformer++ recipe and leads the tested attention-free baselines, especially at longer contexts. In a separate 300B-token, GPT-NeoX-tokenizer evaluation, Mamba-2.8B reported a 63.3 average across seven zero-shot tasks, compared with 59.1 for Pythia-2.8B; the table also reports lower Pile validation perplexity for Mamba (6.22 versus 6.73).[^gu-dao-2023]
- **Selective synthetic tasks:** A two-layer Mamba trained on length 256 induction-head data achieved reported perfect accuracy through test length $2^{20}$ (one million), whereas the tested attention models lost accuracy or exhausted memory and the listed LTI SSMs failed at long lengths. This is controlled synthetic extrapolation evidence, not proof of general long-context retrieval.[^gu-dao-2023]
- **Genomics and audio:** Under the paper's DNA setup, Mamba's perplexity improved as tested context grew to one million tokens and its great-ape classifier reached 71.67% (1.4M) or 81.31% (7M) at that length. On SC09 speech generation, author-reported automatic metrics favored Mamba over the listed autoregressive, GAN, and diffusion baselines. These domain-specific results use distinct data, objectives, and architectures.[^gu-dao-2023]

## Fused scan and serving measurements

Input-dependent transitions remove the convolutional training path, so Mamba uses an associative parallel scan. Its implementation fuses discretization, scan, and output read: it loads inputs and parameters from HBM, materializes expanded $(B,L,D,N)$ state only in SRAM, and writes $(B,L,D)$ output back. It recomputes rather than stores intermediate states in backward propagation. The paper reports that this reduces the relevant HBM traffic by an $O(N)$ factor relative to its materializing scan, and that its optimized scan was 20–40× faster than the paper's standard PyTorch scan.[^gu-dao-2023]

On one A100 80GB PCIe benchmark of the core operation ($D=1024$, $N=16$, BF16, batch size one), the fused scan reportedly overtook FlashAttention-2 beyond 2K tokens. The comparison excludes attention QKV projections and other block work. A separate end-to-end decode benchmark (2,048-token prompt, 128 generated tokens) reports 4–5× higher Mamba throughput than similarly sized GPT-3-style Transformers because bounded recurrent state permits larger batches; its 6.9B Mamba example was untrained.[^gu-dao-2023]

## Modality and deployment limits

- The paper's audio ablation reports that replacing LTI S4 with selective S6 **hurt** long-form raw-waveform pretraining; complex LTI SSMs remained better in outer U-Net layers. Selection is therefore not a uniformly better inductive bias.[^gu-dao-2023]
- The 125M memory table reports Mamba using slightly more training memory than the compared FlashAttention-2 Transformer at every listed batch size (for example, 4.8 versus 4.6 GB at batch one). “Linear-time” does not imply lower end-to-end memory in every implementation.[^gu-dao-2023]
- The paper evaluates models below later frontier-model scales and identifies larger-scale training and downstream affordances as unresolved. Kernel and throughput outcomes depend on sequence length, state size, batch shape, precision, accelerator, and implementation.[^gu-dao-2023]

## Relationships

- **Evaluates:** [Mamba selective state spaces and architecture](mamba-selective-state-spaces-and-architecture.md).
- **Contrasts with:** [Self-attention computational profile](self-attention-computational-profile.md): core-operation speed comparisons do not erase attention's token-addressable retrieval or establish whole-model speed at every context.
- **Followed by:** [Mamba-2 evaluation and efficiency](mamba-2-evaluation-and-efficiency.md), which evaluates the SSD-based successor under its own configurations.

## Evidence limits

All quality, kernel, memory, and throughput measurements are author-run results from one paper; this source contains no independent replication. Several comparisons differ in tokenizer, architecture, training recipe, or model size, and the long-context claims are task-specific. The evidence supports the disclosed configurations, not a general replacement recommendation for attention.

[^gu-dao-2023]: Albert Gu and Tri Dao, “Mamba: Linear-Time Sequence Modeling with Selective State Spaces,” arXiv:2312.00752, bundled [LaTeX source](../raw/2312.00752_Mamba/main.tex), Sections 4–5, Appendix B–C, and experimental tables.

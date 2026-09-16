---
type: Concept
title: Consumer-GPU P2P Unlock and vLLM Tuning
description: Community driver patch plus vLLM P2P override and fused-MoE tuning that enable direct GPU-to-GPU transfer on consumer cards.
tags: [vllm, consumer-gpu, p2p, moe, tensor-parallel]
status: draft
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T12:00:00Z }
sources:
  - id: p2p-consumer
    resource: ../raw/patching-nvidias-driver-and-vllm-to-enable-p2p-on-consumer-gpus/index.md
    title: Patching NVIDIA's driver and vLLM to enable P2P on consumer GPUs
---

A community procedure claims NVIDIA's consumer-GPU P2P block is a driver product-segmentation limit rather than a hardware limit, and combines a patched open kernel module, an IOMMU passthrough prerequisite, a vLLM P2P-check override, and consumer-specific fused-MoE tuning to improve dual-GPU tensor-parallel throughput on RTX 3090-class hardware[^p2p-consumer].

## Why P2P matters for tensor parallelism

Without P2P, tensor-parallel exchanges are described as routing through CPU and system memory; with P2P, GPUs read and write each other directly over DMA, reducing latency and PCIe inefficiency[^p2p-consumer].

The source asserts RTX 3090/4090/5090-class consumer cards support P2P in hardware but are blocked in the driver to push buyers toward professional cards; treat this segmentation claim as author-reported experience, not independently verified hardware coverage[^p2p-consumer].

## Driver patch

The patch source is the community fork `aikitoria/open-gpu-kernel-modules`, described as forcing BAR1 P2P mode on and performing transfers by writing directly to the peer GPU's physical addresses over DMA[^p2p-consumer].

Prerequisite: IOMMU in passthrough mode, otherwise DMA transfers fail[^p2p-consumer]:

```bash
GRUB_CMDLINE_LINUX="... amd_iommu=on iommu=pt"
# Intel: intel_iommu=on iommu=pt
```

Passthrough mode reduces IOMMU isolation guarantees; the source warns against using it blindly with untrusted software/devices in high-security environments[^p2p-consumer].

Reported install flow at time of writing[^p2p-consumer]:

1. Match the fork branch to a supported NVIDIA driver version (`590.48.01` in the source; treat as ephemeral).
2. Download the matching NVIDIA driver and select the open-source driver flavor.
3. Clone the fork and run `./install.sh`, then reboot.

Verify with[^p2p-consumer]:

```text
nvidia-smi topo -p2p r
# OK between GPUs means P2P active; NS means still blocked
```

## vLLM P2P gate override

Even with driver-level P2P operational, the source reports vLLM refused to use P2P because `vllm/platforms/cuda.py` queries `pynvml` for P2P support and that user-space check still reports consumer cards as unsupported[^p2p-consumer].

The author's workaround is a Dockerfile `sed` one-liner that short-circuits that check to always return `True`[^p2p-consumer]:

```dockerfile
RUN sed -i 's/handles = \[pynvml.nvmlDeviceGetHandleByIndex(i) for i in physical_device_ids\]/return True/g' \
  /usr/local/lib/python3.12/dist-packages/vllm/platforms/cuda.py
```

Treat this as a personal-server dirty hack: it disables the safety check globally, is version- and path-fragile, and the source itself says a surgical fix is needed for anything beyond personal use[^p2p-consumer].

## Fused-MoE tuning for consumer cards

`fused_moe` fuses routed expert weights, batched expert GEMMs, and activation into one Triton dispatch; tiling and launch parameters such as `BLOCK_SIZE_M/N/K`, `GROUP_SIZE_M`, `num_warps`, and `num_stages` decide SM, shared-memory, and cache efficiency[^p2p-consumer].

vLLM ships pre-tuned configs for datacenter GPUs such as A100/H100/B200; on untuned consumer cards it falls back to heuristic defaults with a `Using default MoE config. Performance might be sub-optimal!` warning[^p2p-consumer].

The source's tuning path[^p2p-consumer]:

- vLLM includes a benchmarking script that searches roughly 1,900 configurations per batch size, taking many hours.
- The `MissionSquad/vllm-moe-configs` patch narrows that search space for single-GPU consumer setups while retaining most of the benefit.
- Output is a JSON file keyed by expert count, intermediate size, and device, e.g. `E=48,N=768,device_name=NVIDIA_GeForce_RTX_3090.json`, mapping batch sizes 1–4096 to optimal tiles/warps/stages.
- Point vLLM at the folder with `VLLM_TUNED_CONFIG_FOLDER=/path/to/configs`; disappearance of the default-config warning signals the tuned file was picked up.

The author's RTX 3090 JSON was published as a gist and names `triton_version: 3.5.1`; treat exact tile values and Triton pin as hardware- and version-specific, not portable defaults[^p2p-consumer].

## Reported results and limits

Test setup was dual RTX 3090s, Ryzen 9 9900X, 192 GB DDR5, 64K context, Qwen 3.5 35B-A3B MoE with about 3B active parameters per token; vLLM used 4-bit dynamic AWQ while llama.cpp used Unsloth `UD-Q4_K_XL`[^p2p-consumer].

Source-reported throughput with P2P plus MoE tuning versus without[^p2p-consumer]:

- vLLM 35B-A3B: `90–197 tk/s` with unlock versus `~35–65 tk/s` without.
- vLLM 27B: `32–195 tk/s` with unlock versus `~32–70 tk/s` without.
- llama.cpp 35B-A3B: `110–130 tk/s` with unlock path; no-P2P baseline untested.
- llama.cpp 27B: `30–70 tk/s`; no-P2P baseline untested.

The source summarizes the gain as workload-dependent, larger where tensor-parallel and expert-routing traffic dominate, with `fused_moe` on the critical path for every token; MoE models are therefore expected to benefit more than dense models[^p2p-consumer].

Trust limits: single-author, single-rig anecdote with empty version fields in the results table, no isolated P2P-only versus MoE-tuning-only ablation, and no stated measurement harness; the author explicitly defers a cleaner breakdown to a future update[^p2p-consumer].

## Deployment notes from the source

Author's vLLM snapshot, not a stable recipe[^p2p-consumer]:

- Base `vllm/vllm-openai:cu130-nightly`, CUDA 130, nightly vLLM wheels, latest `transformers` main, forced `numba` reinstall.
- `tensor-parallel-size 2`, `FLASHINFER` attention backend, prefix caching plus chunked prefill, `gpu-memory-utilization 0.95`, `max-model-len 131070`, `max-num-batched-tokens 16384`, `max-num-seqs 8`.
- Qwen 3.5 model `cyankiwi/Qwen3.5-35B-A3B-AWQ-4bit`, `--language-model-only`, `qwen3_coder` tool parser, `qwen3` reasoning parser, MTP speculation with `num_speculative_tokens: 2`, `mamba-cache-mode all`.

Expert-parallel test on the same rig found EP slightly worse except for one long-request window: short `82.7` vs `71.9 tk/s`, medium `69.6` vs `67.7`, long `164.9` vs `168.6`, tail `39.9` vs `20.7`, spec acceptance `76–88%` vs `70–77%`, with slightly more KV-cache tokens under EP; the author keeps EP off, attributing the loss to cross-GPU routing overhead outweighing VRAM savings[^p2p-consumer].

Author's engine assessment, not a general ranking: llama.cpp via `llama-swap` is preferred for daily use, hot-swapping, idle VRAM release, flexible GGUF quants, and robust RAM offload, while vLLM is preferred for heavy or MoE tensor-parallel throughput despite harder setup, per-model flags, static launch config, weak GGUF coverage, and experimental offload[^p2p-consumer].

## Relationships

- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — TP needs efficient GPU-to-GPU transfer; this concept adds the consumer-GPU P2P unlock that the scaling concept does not cover.
- Uses [vLLM Fused MoE Modular Kernel](vllm-fused-moe-modular-kernel.md) — modular prepare/finalize plus experts architecture behind the tuned Triton `fused_moe` kernel here.
- Uses [vLLM Fused MoE Kernel Features](vllm-moe-kernel-features.md) — backend/experts selection tables complement the consumer-specific tile tuning here.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — that concept holds the general consumer-local versus serving split; this concept adds a dual-3090 data point where both engines were run.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — the deployment snapshot uses native MTP with two speculative tokens on Qwen 3.5.

## Contradictions

- Improvement magnitude: source frontmatter claims `15–50%` throughput improvement while the body and results section claim `10–30%` for the same configuration; both cannot be exact, so the wiki reports the range as `10–50% claimed` with the internal inconsistency flagged[^p2p-consumer].

## Coverage limits

- Referenced attachments were limited to the source page; the fork, NVIDIA driver package, tuner patch repo, author gist, `llama-swap`, and linked llama.cpp issue were not inspected beyond the source's description[^p2p-consumer].
- Exact kernel JSON beyond the batch-1 and batch-16 excerpts, Dockerfile base-image digest, compose-file macros, and llama.cpp template details were summarized rather than reproduced because they are version-specific[^p2p-consumer].
- No independent verification of P2P stability, ECC/correctness, power/thermal, multi-tenant safety, or warranty/support impact; community kernel patches carry support and security risk[^p2p-consumer].

[^p2p-consumer]: Sam McLeod, Patching NVIDIA's driver and vLLM to enable P2P on consumer GPUs — `../raw/patching-nvidias-driver-and-vllm-to-enable-p2p-on-consumer-gpus/index.md` (smcleod.net, published 2026-02-25), covering consumer P2P segmentation claim, BAR1 DMA patch, IOMMU passthrough, install/verify flow, vLLM `cuda.py` override, fused-MoE tuning, dual-3090 Qwen 3.5 throughput and EP comparison, and vLLM/llama.cpp deployment snapshots.

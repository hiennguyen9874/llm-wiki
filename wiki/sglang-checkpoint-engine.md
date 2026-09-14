---
type: Concept
title: SGLang Checkpoint Engine Integration
description: Distributed parallel weight loading for SGLang via checkpoint-engine workers with broadcast and P2P modes for single and multi-node setups.
tags: [sglang, checkpoint-engine, weight-loading, distributed, multi-node]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:53:47Z }
sources:
  - id: sgl-ckpt
    resource: ../raw/sglang/advanced_features/checkpoint_engine.mdx
    title: Checkpoint Engine Integration
---

SGLang integrates the external `checkpoint-engine` package to parallelize model weight loading across processes and nodes, reducing startup time for large models by sharding disk reads and overlapping dummy-load initialization with CUDA graph capture[^sgl-ckpt].

## Architecture

Two cooperating components[^sgl-ckpt]:

- **SGLang server**: launched with `--load-format dummy` and `--wait-for-initial-weights` so it initializes without weights and becomes ready only after the engine delivers them.
- **Checkpoint engine workers**: separate processes launched via `python -m sglang.srt.checkpoint_engine.update` or `torchrun examples/checkpoint_engine/update.py` that read checkpoints from disk and push weights to inference processes.

The engine uses a parameter-server architecture with three update methods[^sgl-ckpt]:

- `broadcast`: broadcast weights from loading processes to inference processes.
- `p2p`: direct peer-to-peer weight transfer.
- `all`: combination of broadcast and P2P.

## Installation

```bash
pip install 'checkpoint-engine[p2p]'[^sgl-ckpt]
```

## Single-node usage

Launch server waiting for weights, then run the engine in a second terminal[^sgl-ckpt]:

```bash
python -m sglang.launch_server \
    --model-path Qwen/Qwen3-8B \
    --tp 8 \
    --load-format dummy \
    --wait-for-initial-weights
```

```bash
python -m sglang.srt.checkpoint_engine.update \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 8
```

`torchrun` alternative[^sgl-ckpt]:

```bash
torchrun --nproc-per-node 8 \
    examples/checkpoint_engine/update.py \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 8
```

## Multi-node usage

Each node runs its own SGLang server with `--host [IP]` plus a checkpoint-engine worker; the `torchrun` form needs `--nnodes 2`, `--node-rank {0,1}`, `--master-addr [IP]`, and `--master-port 29500`[^sgl-ckpt].

Node 0 server[^sgl-ckpt]:

```bash
python -m sglang.launch_server \
    --model-path Qwen/Qwen3-8B \
    --tp 8 \
    --load-format dummy \
    --wait-for-initial-weights \
    --host [IP]
```

Node 0 engine, recommended entrypoint[^sgl-ckpt]:

```bash
python -m sglang.srt.checkpoint_engine.update \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 8
```

Node 1 repeats the same server and engine commands with its own `--node-rank 1` when using `torchrun`[^sgl-ckpt].

For cross-node tensor parallelism (TP=16 over 2×8-GPU nodes), add distributed init to each server and set engine parallel size to the global size[^sgl-ckpt]:

```bash
python -m sglang.launch_server \
    --model-path Qwen/Qwen3-8B \
    --tp 8 \
    --load-format dummy \
    --wait-for-initial-weights \
    --host [IP] \
    --dist-init-addr [IP]:9120 \
    --nnodes 2 \
    --node-rank 0
```

```bash
python -m sglang.srt.checkpoint_engine.update \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 16
```

## Configuration options

SGLang server options[^sgl-ckpt]:

- `--load-format dummy`: defer real weight loading to allow overlap with other init tasks.
- `--wait-for-initial-weights`: block readiness until checkpoint engine delivers weights.
- `--host`: bind address for multi-node setups.
- `--dist-init-addr`: distributed initialization address for tensor parallelism.

Checkpoint engine options[^sgl-ckpt]:

- `--update-method`: `broadcast`, `p2p`, or `all`.
- `--checkpoint-path`: model checkpoint directory.
- `--inference-parallel-size`: number of inference parallel processes (8 per-node example, 16 for 2-node TP=16).
- `--endpoint`: SGLang server endpoint (default `http://localhost:19730`).
- `--checkpoint-name`: checkpoint name (default `my-checkpoint-iter-0`).
- `--save-metas-file` / `--load-metas-file`: save/load checkpoint metadata.
- `--uds`: Unix domain socket path for communication.
- `--weight-version`: version identifier for weights.
- `--sleep-time`: optional delay aid for debugging (per troubleshooting note).

## Performance benefits

Two savings mechanisms[^sgl-ckpt]:

1. **Multi-node disk-bandwidth scaling**: each node loads only a portion of weights from disk; more nodes give greater acceleration. Preliminary test cited 20-second saving loading DeepSeek-R1 on H20-3e with two nodes.
2. **Single-process overlap**: dummy format overlaps disk-to-CPU transfer with CUDA graph capture and other initialization.

## Troubleshooting and references

- Ensure `pip install 'checkpoint-engine[p2p]'`, verify inter-node network connectivity, confirm checkpoint path contents, monitor server/engine logs for connection errors, and use `--sleep-time` for debugging delays[^sgl-ckpt].
- Upstream implementation: [Checkpoint Engine Repository](https://github.com/MoonshotAI/checkpoint-engine)[^sgl-ckpt].

## Coverage limits

- No measured single-node speedup numbers, P2P versus broadcast selection guidance, or `--endpoint`/`--uds`/metadata-file workflows beyond flag names were in the source[^sgl-ckpt].
- Linked upstream checkpoint-engine repository was not inspected[^sgl-ckpt].

[^sgl-ckpt]: Checkpoint Engine Integration — `../raw/sglang/advanced_features/checkpoint_engine.mdx`.

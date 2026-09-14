---
type: Concept
title: vLLM Python Multiprocessing Method Selection
description: Best-effort fork/spawn selection, library-use constraints, and worker configuration for vLLM multiprocessing.
tags: [vllm, multiprocessing, deployment]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:41:06Z }
sources:
  - id: multiprocessing
    resource: ../raw/vllm/design/multiprocessing.md
    title: Python Multiprocessing
---

vLLM uses best-effort selection between `fork` and `spawn` to create worker and engine-core processes, defaulting to `fork` for speed and compatibility with library use while forcing `spawn` when vLLM controls the main process or CUDA was already initialized[^multiprocessing].

## Methods and tradeoffs

Python start methods and their vLLM consequences[^multiprocessing]:

- `spawn` — new Python process; default on Windows and macOS. Most dependency-compatible, but requires a `__main__` guard (`if __name__ == "__main__":`) when vLLM is used as a library, otherwise the consuming code is re-executed and can recurse infinitely.
- `fork` — `os.fork()` the interpreter; default on Linux before Python 3.14. Fastest and inherits global state, but incompatible with dependencies that use threads and may crash on macOS.
- `forkserver` — spawned server process that forks on demand; default on Linux from Python 3.14. Shares `spawn`'s library-use problem because the server itself is spawned, and like `spawn` it cannot inherit global state.

## Dependency compatibility

Multiple vLLM dependencies prefer or require `spawn`, including PyTorch CUDA multiprocessing and Habana Gaudi dataloader guidance; known issues exist when `fork` is used after initializing them[^multiprocessing].

## Worker configuration (v0 state)

- `VLLM_WORKER_MULTIPROC_METHOD` controls the worker start method; default is `fork`[^multiprocessing].
- The `vllm` CLI forces `spawn` because it controls the main process and prioritizes compatibility[^multiprocessing].
- `multiproc_xpu_executor` forces `spawn`, as do miscellaneous hard-coded sites in `distributed/device_communicators/all_reduce_utils.py` and `entrypoints/openai/api_server.py`[^multiprocessing].

## V1 engine-core handling

`VLLM_ENABLE_V1_MULTIPROCESSING` previously gated whether the v1 `LLMEngine` spawned a separate engine-core process; it defaulted to off because of dependency and library-use compatibility concerns[^multiprocessing].

The v1 best-effort policy adopted instead[^multiprocessing]:

- Default to `fork`.
- Use `spawn` when vLLM knows it controls the main process (`vllm` was executed).
- If CUDA was previously initialized, force `spawn` and emit a warning pointing to the troubleshooting page, since `fork` will break.

The known still-broken case is library code that initializes CUDA before calling vLLM: the forced `spawn` then fails without a `__main__` guard, surfacing vLLM's CUDA-initialized warning followed by Python's `RuntimeError` about safe main-module importing[^multiprocessing]. The warning instructs users to add a `__main__` guard or disable multiprocessing[^multiprocessing].

## Discarded alternatives

- Detecting whether the caller has a `__main__` guard: discarded as impractical — the original versus spawned process is detectable, but guard presence is not[^multiprocessing].
- Using `forkserver`: rejected because it reintroduces `spawn`'s library-use problem[^multiprocessing].
- Forcing `spawn` always: rejected because it would break existing library code and make the `LLM` class harder to use; vLLM retains the selection complexity instead[^multiprocessing].

## Future work

Proposed directions are a custom `vllm-manager` subprocess entrypoint acting `forkserver`-like under vLLM control, and evaluating third-party process managers such as `loky`[^multiprocessing].

## Coverage limits

- Code references reflect December 2024 state and cited line numbers were not re-verified against current vLLM[^multiprocessing].
- The referenced `usage/troubleshooting.md` Python-multiprocessing section was absent from `raw/` and was not inspected.

## Relationships

- Uses [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — this selection policy determines how those API-server, engine-core, and worker processes are started.
- Uses [vLLM Engine, Worker, and Model Hierarchy](vllm-engine-worker-hierarchy.md) — spawned workers host the worker and model-runner side of that hierarchy.

[^multiprocessing]: Python Multiprocessing — `../raw/vllm/design/multiprocessing.md`.

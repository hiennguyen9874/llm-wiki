#!/usr/bin/env bash
# The HF OpenJEV adapter on a separately installed SM70 SGLang runtime.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=${OPENJEV_V100_ROOT:-$HOME/storage/sglang-openjev-v100}
MODEL=${1:-$ROOT/model}
PORT=${2:-31000}
CACHE_STRATEGY=extra_buffer
CACHE_MEMORY_RATIO=3
for arg in "${@:3}"; do
  if [[ "$arg" == --disable-radix-cache ]]; then
    CACHE_STRATEGY=no_buffer
    CACHE_MEMORY_RATIO=0.9
  fi
done
export CUDA_HOME="$ROOT/cuda126"
export CC=${CC:-/usr/bin/gcc-10}
export CXX=${CXX:-/usr/bin/g++-10}
export NVCC_PREPEND_FLAGS="-ccbin=$CXX${NVCC_PREPEND_FLAGS:+ $NVCC_PREPEND_FLAGS}"
export PATH="$ROOT/venv/bin:$CUDA_HOME/bin:$PATH"
export PYTHONPATH="$HERE${PYTHONPATH:+:$PYTHONPATH}"
export SGLANG_EXTERNAL_MODEL_PACKAGE=sglang_openjev
export TORCH_EXTENSIONS_DIR="$ROOT/torch_extensions"
export TRITON_CACHE_DIR="$ROOT/triton"
export TILELANG_CACHE_DIR="$ROOT/tilelang"
export FLASHINFER_WORKSPACE_BASE="$ROOT/flashinfer_workspace"
export XDG_CACHE_HOME="$ROOT/runtime_cache"
export TVM_FFI_CACHE_DIR="$ROOT/tvm_ffi"
export SGLANG_V100_DYNAMIC_PAGED=${SGLANG_V100_DYNAMIC_PAGED:-1}
export TMPDIR="$ROOT/tmp"
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
exec "$ROOT/venv/bin/python" -m sglang.launch_server \
  --model-path "$MODEL" --host 127.0.0.1 --port "$PORT" \
  --served-model-name openjev --is-embedding --dtype float16 \
  --sampling-backend pytorch \
  --json-model-override-args '{"architectures":["Qwen3_5ForConditionalGeneration"]}' \
  --attention-backend tilelang_fa_v100 --page-size 16 \
  --linear-attn-prefill-backend tilelang --linear-attn-decode-backend triton \
  --mamba-scheduler-strategy "$CACHE_STRATEGY" \
  --mamba-full-memory-ratio "${OPENJEV_MAMBA_MEMORY_RATIO:-$CACHE_MEMORY_RATIO}" \
  --mem-fraction-static "${MEM_FRACTION_STATIC:-0.80}" --context-length "${CONTEXT_LENGTH:-8192}" \
  --max-running-requests "${MAX_RUNNING_REQUESTS:-16}" --chunked-prefill-size 4096 \
  --schedule-policy "${SCHEDULE_POLICY:-lpm}" \
  --disable-cuda-graph --disable-piecewise-cuda-graph "${@:3}"

#!/usr/bin/env bash
# Serve an openjev checkpoint with SGLang. Usage: ./serve_sglang.sh [ckpt dir or HF snapshot dir] [port] [extra sglang args]
# Needs a local dir with config.json at its root (for the Hub repo: hf download AlexWortega/openjev --include
# "qwen3.5-0.8b-nli-v2s-long/*" --local-dir openjev_hf). Query with sglang_client.py.
# ATTN_BACKEND defaults to triton: flashinfer JIT-compiles with the system nvcc and fails on nvcc < 12.4.
# MEM_FRACTION is a share of the WHOLE card, other processes included: on a shared GPU set it close to
# 1 - (wanted headroom / total), e.g. 0.85 on a 48GB card that already has 32GB taken.
HERE=$(cd "$(dirname "$0")" && pwd)
MODEL=${1:-ckpt/qwen3.5-0.8b-nli-v2s-long}
PORT=${2:-30000}
PY=${PY:-$HOME/venvs/sglang/bin/python}
export PATH=$(dirname "$PY"):$PATH  # ninja for sglang's JIT kernels
export PYTHONPATH=$HERE:$PYTHONPATH
export SGLANG_EXTERNAL_MODEL_PACKAGE=sglang_openjev
exec $PY -m sglang.launch_server --model-path "$MODEL" --port "$PORT" --host 0.0.0.0 \
  --is-embedding --json-model-override-args '{"architectures": ["Qwen3_5ForConditionalGeneration"]}' \
  --attention-backend ${ATTN_BACKEND:-triton} --served-model-name openjev ${MEM_FRACTION:+--mem-fraction-static $MEM_FRACTION} "${@:3}"

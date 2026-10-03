#!/usr/bin/env bash
# Serve autotrust/JEV-27B-VL with vLLM: System 1 and System 2, text and images, on one engine.
#   System 1: POST /v1/decide  {kind, state, question, options} -> calibrated probabilities (2-256 options, text or images)
#             or model "jev-decision" through /v1/completions and /v1/chat/completions
#   System 2: model "autotrust/JEV-27B-VL" through /v1/chat/completions
# serve_decide.py is the standard vLLM OpenAI server (same flags) with the /v1/decide route added.
# --max-num-seqs 8 is required: with more than 8 sequences in one batch, vLLM's LoRA path for this multimodal model class
# returns wrong System 1 probabilities. --trust-request-chat-template lets image decisions use the raw decision template.
# MAX_MODEL_LEN: up to 262144 (the backbone's native context); a full 256K prompt needs about 17 GB of KV cache.
set -e
MODEL_DIR=${MODEL_DIR:-JEV-27B-VL}
[ -d "$MODEL_DIR" ] || hf download autotrust/JEV-27B-VL --local-dir "$MODEL_DIR"
exec python3 "$MODEL_DIR/serve_decide.py" --model "$MODEL_DIR" --served-model-name autotrust/JEV-27B-VL \
  --enable-lora --max-lora-rank 32 --lora-modules jev-decision="$MODEL_DIR/adapter_vllm" \
  --logprobs-mode processed_logprobs --max-model-len ${MAX_MODEL_LEN:-32768} --enable-prefix-caching --mamba-cache-mode align \
  --limit-mm-per-prompt '{"image": 8}' --max-num-seqs 8 --trust-request-chat-template \
  --port ${PORT:-8000}

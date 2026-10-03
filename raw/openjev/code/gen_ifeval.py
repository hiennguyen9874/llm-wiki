#!/usr/bin/env python
"""Generate IFEval responses with a few Qwen3.5 sizes (vLLM, thinking off) for eval_extra.py's `ifeval` task.
Labels are NOT computed here: eval_extra.py runs the IFEval strict checker on every response.

    for m in Qwen/Qwen3.5-0.8B Qwen/Qwen3.5-2B Qwen/Qwen3.5-4B; do   # one process per model: vLLM frees memory on exit
        ~/venvs/vllm/bin/python gen_ifeval.py --models $m --out data/ifeval_gen.jsonl; done
"""
import argparse
import json

from huggingface_hub import hf_hub_download
from vllm import LLM, SamplingParams


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["Qwen/Qwen3.5-0.8B", "Qwen/Qwen3.5-2B", "Qwen/Qwen3.5-4B"])
    ap.add_argument("--out", default="data/ifeval_gen.jsonl")
    ap.add_argument("--max-tokens", type=int, default=1536)
    ap.add_argument("--gpu-util", type=float, default=0.85)
    args = ap.parse_args()
    path = hf_hub_download("google/IFEval", "ifeval_input_data.jsonl", repo_type="dataset")
    ds = [json.loads(line) for line in open(path)]
    with open(args.out, "a") as f:
        for m in args.models:
            llm = LLM(m, max_model_len=4096, gpu_memory_utilization=args.gpu_util, limit_mm_per_prompt={"image": 0})
            msgs = [[{"role": "user", "content": ex["prompt"]}] for ex in ds]
            outs = llm.chat(msgs, SamplingParams(temperature=0.7, top_p=0.9, max_tokens=args.max_tokens, seed=0),
                            chat_template_kwargs={"enable_thinking": False})
            for ex, o in zip(ds, outs):
                f.write(json.dumps({"model": m, "key": ex["key"], "prompt": ex["prompt"],
                                    "instruction_id_list": ex["instruction_id_list"], "kwargs": ex["kwargs"],
                                    "response": o.outputs[0].text}, ensure_ascii=False) + "\n")
            f.flush()


if __name__ == "__main__":
    main()

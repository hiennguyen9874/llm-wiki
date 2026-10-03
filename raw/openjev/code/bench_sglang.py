"""Accuracy + throughput of an openjev checkpoint: transformers (eval.py's NLIScorer) vs the SGLang server.

    ./serve_sglang.sh ckpt/qwen3.5-0.8b-nli-v2s-long &
    python bench_sglang.py --ckpt ckpt/qwen3.5-0.8b-nli-v2s-long --out results/sglang/bench.json

Both backends go through the same eval.py task code; only `predict` is timed (no dataset loading)."""
import argparse
import json
import os
import time
from types import SimpleNamespace

import numpy as np
import torch

import eval as E
from sglang_client import OpenJevSGLang


class Timed:
    def __init__(self, predict, tok, max_len):
        self._predict, self.tok, self.max_len = predict, tok, max_len
        self.reset()

    def reset(self):
        self.sec, self.pairs, self.tokens = 0.0, 0, 0

    def predict(self, pairs):
        t = time.perf_counter()
        out = self._predict(pairs)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        self.sec += time.perf_counter() - t
        self.pairs += len(pairs)
        texts = [E_TEMPLATE.format(premise=p.strip(), hypothesis=h.strip()) for p, h in pairs]
        self.tokens += sum(min(len(x), self.max_len) for x in self.tok(texts)["input_ids"])
        return out


def run(scorer, tasks, mc_items, mnli_n):
    res = {}
    for t in tasks:
        scorer.reset()
        if t == "mnli":
            r = E.eval_mnli(scorer, mnli_n)
            acc = float(np.mean([v["acc"] for v in r.values()]))
        elif t in E.NLI_SETS:
            acc = E.eval_nli_set(scorer, t)["acc"]
        else:
            acc = E.eval_mc(scorer, mc_items[t])["rerank_acc"]
        res[t] = {"acc": acc, "pairs": scorer.pairs, "tokens": scorer.tokens, "sec": round(scorer.sec, 2),
                  "pairs_per_s": round(scorer.pairs / scorer.sec, 1), "tok_per_s": round(scorer.tokens / scorer.sec)}
        print(t, res[t], flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--url", default="http://127.0.0.1:30000")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tasks", nargs="+", default=["mnli", "anli_r1", "anli_r2", "anli_r3", "wanli", "scitail", "control",
                                                   "arc_challenge", "hellaswag"])
    ap.add_argument("--backends", nargs="+", default=["sglang", "hf"])
    ap.add_argument("--mnli-n", type=int, default=None)
    ap.add_argument("--mc-n", type=int, default=2000, help="hellaswag / mmlu subsample")
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    from transformers import AutoConfig, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(a.ckpt)
    E_TEMPLATE = AutoConfig.from_pretrained(a.ckpt).nli_template
    margs = SimpleNamespace(mc_n=a.mc_n, chess_n=500, fewshot=5)
    mc_items = {t: E.MC_TASKS[t](margs) for t in a.tasks if t in E.MC_TASKS}
    results = {}
    for b in a.backends:
        print(f"\n===== {b}")
        if b == "hf":
            model = E.NLIScorer(a.ckpt, bs=a.bs, max_len=a.max_len)
            predict = model.predict
        else:
            predict = OpenJevSGLang(a.url, template=E_TEMPLATE, bs=a.bs, workers=a.workers).predict
        predict([("warm", "up")] * a.bs)
        results[b] = run(Timed(predict, tok, a.max_len), a.tasks, mc_items, a.mnli_n)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump(results, open(a.out, "w"), indent=2)
    print("\n| task | pairs | avg tok | " + " | ".join(f"{b} acc | {b} pairs/s" for b in a.backends) + " | speedup |")
    print("|---|---|---|" + "---|---|" * len(a.backends) + "---|")
    for t in a.tasks:
        r0 = results[a.backends[0]][t]
        row = " | ".join(f"{results[b][t]['acc']:.4f} | {results[b][t]['pairs_per_s']}" for b in a.backends)
        sp = r0["pairs_per_s"] / results[a.backends[-1]][t]["pairs_per_s"] if len(a.backends) > 1 else 1.0
        print(f"| {t} | {r0['pairs']} | {r0['tokens'] // r0['pairs']} | {row} | {sp:.1f}x |")

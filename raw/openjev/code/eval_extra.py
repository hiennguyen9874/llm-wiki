#!/usr/bin/env python
"""Faithfulness, bullshit detection and instruction following for jev cross-encoders. Nothing here is trained on.

    python eval_extra.py --models ckpt/qwen3.5-0.8b-nli-v2 ckpt/qwen3.5-0.8b-nli --out results/v2/extra_0.8b.json

Tasks (score = P(entailment) unless stated):
  aggrefact   LLM-AggreFact test (gated): premise = document, hypothesis = claim. Balanced accuracy per dataset at a
              fixed 0.5 threshold (the leaderboard protocol) + AUROC. Documents longer than the window are chunked and
              the max over chunks is taken (MiniCheck style).
  ragtruth    RAGTruth test, response level: hallucinated iff any annotated span. AUROC + BAcc@0.5.
  halubench   PatronusAI/HaluBench: passage + question -> answer, PASS/FAIL. AUROC + BAcc@0.5, per source.
  bsb_judge   BullshitBench responses: premise = question + model answer, hypothesis = "the answer pushes back".
              Gold = the 3-judge consensus (>=1.5 pushback, <=0.5 full engagement). AUROC + Spearman.
  bsb_detect  BullshitBench questions: P(contradiction) of "The question makes sense..." -> detection rate at 0.5,
              with FalseQA-test valid questions as the false-positive reference.
  falseqa     FalseQA test (question level), in-domain sanity check. AUROC + BAcc.
  ifeval      IFEval responses of 3 models (Open LLM Leaderboard samples if accessible, else gen_ifeval.py output):
              prompt level ("follows all") and instruction level (one hypothesis per constraint), gold = the IFEval
              strict checker run here. AUROC + BAcc@0.5.
  llmbar      LLMBar pairwise (Natural + Adversarial): pick the output with the higher "follows" score. Accuracy.
"""
import argparse
import csv
import io
import json
import os
import random
import sys
import urllib.request
from collections import defaultdict

import numpy as np
from sklearn.metrics import roc_auc_score

from eval import CON, ENT, NLIScorer

HERE = os.path.dirname(os.path.abspath(__file__))
BSB = "https://raw.githubusercontent.com/petergpt/bullshit-benchmark/main/"
IF_ALL = "The response follows all of the instructions."
BS_Q = "The question makes sense and rests on valid assumptions."
BS_R = "The answer points out that the question's premise is false or nonsensical."
IFEVAL_MODELS = ["Qwen__Qwen2.5-7B-Instruct", "meta-llama__Llama-3.2-1B-Instruct", "Qwen__Qwen2.5-0.5B-Instruct"]


def fetch(url, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, url.split("/", 3)[-1].replace("/", "__"))
    if not os.path.exists(path):
        with urllib.request.urlopen(url, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
    return path


def bacc(y, s, thr=0.5):
    y, pred = np.asarray(y).astype(bool), np.asarray(s) >= thr
    tpr = (pred & y).sum() / max(y.sum(), 1)
    tnr = (~pred & ~y).sum() / max((~y).sum(), 1)
    return float((tpr + tnr) / 2)


def auroc(y, s):
    y = np.asarray(y)
    return float(roc_auc_score(y, s)) if 0 < y.sum() < len(y) else None


def binary_report(y, s):
    return {"n": int(len(y)), "pos_rate": float(np.mean(y)), "auroc": auroc(y, s), "bacc@0.5": bacc(y, s)}


class Window:
    """Fits (premise, hypothesis) into the model window. chunk=True splits a long premise into overlapping chunks
    and returns, per pair, the probs of the chunk with the highest entailment; otherwise the premise is cut."""

    def __init__(self, scorer, max_len):
        self.s, self.tok, self.max_len = scorer, scorer.tok, max_len

    def probs(self, pairs, chunk=False):
        flat, owner = [], []
        for i, (p, h) in enumerate(pairs):
            budget = self.max_len - len(self.tok(h, add_special_tokens=False)["input_ids"]) - 32
            ids = self.tok(p, add_special_tokens=False)["input_ids"]
            if len(ids) <= budget:
                pieces = [p]
            elif not chunk:
                pieces = [self.tok.decode(ids[:budget])]
            else:
                step = max(budget - 64, 64)
                pieces = [self.tok.decode(ids[a:a + budget]) for a in range(0, len(ids), step)]
            for piece in pieces:
                flat.append((piece, h)); owner.append(i)
        order = np.argsort([-len(p) for p, _ in flat])  # length-sorted batches
        probs = np.zeros((len(flat), 3), dtype=np.float32)
        pr = self.s.predict([flat[j] for j in order])
        probs[order] = pr
        out = np.zeros((len(pairs), 3), dtype=np.float32)
        best = np.full(len(pairs), -1.0)
        for j, i in enumerate(owner):
            if probs[j, ENT] > best[i]:
                best[i], out[i] = probs[j, ENT], probs[j]
        return out


# ----------------------------------------------------------------------------- faithfulness
def eval_aggrefact(w, args):
    from datasets import load_dataset
    try:
        ds = load_dataset("lytang/LLM-AggreFact", split="test")
    except Exception as e:  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {str(e)[:160]}"}
    by = defaultdict(list)
    for ex in ds:
        by[ex["dataset"]].append(ex)
    res, baccs = {}, []
    for name, rows in sorted(by.items()):
        if args.limit:
            rows = random.Random(0).sample(rows, min(args.limit, len(rows)))
        pr = w.probs([(r["doc"], r["claim"]) for r in rows], chunk=True)
        y = [int(r["label"]) for r in rows]
        res[name] = binary_report(y, pr[:, ENT])
        baccs.append(res[name]["bacc@0.5"])
    res["avg_bacc@0.5"] = float(np.mean(baccs))
    return res


def eval_ragtruth(w, args):
    from datasets import load_dataset
    ds = load_dataset("wandb/RAGTruth-processed", split="test")
    rows = list(ds)
    if args.limit:
        rows = random.Random(0).sample(rows, min(args.limit * 3, len(rows)))
    pairs, y, task = [], [], []
    for ex in rows:
        spans = json.loads(ex["hallucination_labels"]) if isinstance(ex["hallucination_labels"], str) else ex["hallucination_labels"]
        pairs.append((f"{ex['query']}\n\n{ex['context']}".strip(), ex["output"])); y.append(int(not spans)); task.append(ex["task_type"])
    pr = w.probs(pairs, chunk=True)[:, ENT]
    res = {"all": binary_report(y, pr)}
    for t in sorted(set(task)):
        m = np.array([x == t for x in task])
        res[t] = binary_report(np.array(y)[m], pr[m])
    return res


def eval_halubench(w, args):
    from datasets import load_dataset
    rows = list(load_dataset("PatronusAI/HaluBench", split="test"))
    if args.limit:
        rows = random.Random(0).sample(rows, min(args.limit * 3, len(rows)))
    pairs = [(f"{r['passage']}\n\nQuestion: {r['question']}", f"The answer to the question is: {r['answer']}") for r in rows]
    y = np.array([int(str(r["label"]).upper() == "PASS") for r in rows])
    src = [r.get("source_ds", "?") for r in rows]
    pr = w.probs(pairs, chunk=True)[:, ENT]
    res = {"all": binary_report(y, pr)}
    for t in sorted(set(src)):
        m = np.array([x == t for x in src])
        res[t] = binary_report(y[m], pr[m])
    return res


# ----------------------------------------------------------------------------- bullshit
def bsb_questions(cache):
    qs = {}
    for f in ("questions.json", "questions.v2.json"):
        d = json.load(open(fetch(BSB + f, cache)))
        for t in d["techniques"]:
            for q in t["questions"]:
                qs.setdefault(q["id"], set()).add(q["question"].strip())
    return {k: next(iter(v)) for k, v in qs.items() if len(v) == 1}  # ids reused with different text are dropped


def bsb_rows(cache):
    import urllib.request as u
    api = "https://api.github.com/repos/petergpt/bullshit-benchmark/git/trees/HEAD?recursive=1"
    tree = json.load(u.urlopen(api, timeout=60))["tree"]
    files = [t["path"] for t in tree if t["path"].startswith("data/latest/") and t["path"].endswith(".jsonl")
             and ("/aggregate/" in t["path"] or "/responses/" in t["path"])]
    scores, texts = {}, {}
    for f in files:
        for line in open(fetch(BSB + f, cache)):
            r = json.loads(line)
            if "/aggregate/" in f and r.get("status") == "ok" and r.get("consensus_score") is not None:
                scores[r["sample_id"]] = (r["question_id"], float(r["consensus_score"]), str(r.get("is_control")) == "True")
            if "/responses/" in f and r.get("response_text"):
                texts[r["sample_id"]] = r["response_text"]
    return scores, texts


def eval_bsb(w, args):
    cache = os.path.join(args.cache, "bsb")
    qs = bsb_questions(cache)
    scores, texts = bsb_rows(cache)
    rows = [(qs[qid], texts[sid], sc) for sid, (qid, sc, ctl) in scores.items()
            if sid in texts and qid in qs and not ctl and (sc >= 1.5 or sc <= 0.5)]
    rng = random.Random(0)
    rng.shuffle(rows)
    rows = rows[: args.bsb_n]
    pairs = [(f"Question: {q}\n\nAnswer: {t[:4000]}", BS_R) for q, t, _ in rows]
    pr = w.probs(pairs)[:, ENT]
    y = np.array([int(sc >= 1.5) for _, _, sc in rows])
    from scipy.stats import spearmanr
    judge = binary_report(y, pr)
    judge["spearman_vs_consensus"] = float(spearmanr(pr, [sc for _, _, sc in rows]).correlation)
    judge["n_scored_total"] = len(scores)

    # detection: every nonsense question vs FalseQA-test valid questions
    bs_q = sorted(set(qs.values()))
    fq = falseqa_test(args.cache)
    valid_q = [q for q, lab in fq if lab == 0]
    p_bs = w.probs([(f"Question: {q}", BS_Q) for q in bs_q])[:, CON]
    p_ok = w.probs([(f"Question: {q}", BS_Q) for q in valid_q])[:, CON]
    detect = {"n_bullshit": len(bs_q), "detect_rate@0.5": float((p_bs >= 0.5).mean()),
              "fpr_on_falseqa_valid@0.5": float((p_ok >= 0.5).mean()),
              "auroc_vs_falseqa_valid": auroc([1] * len(p_bs) + [0] * len(p_ok), np.concatenate([p_bs, p_ok]))}
    return {"judge": judge, "detect": detect}


def falseqa_test(cache):
    path = fetch("https://raw.githubusercontent.com/thunlp/FalseQA/main/dataset/test.csv", os.path.join(cache, "falseqa"))
    return [(r["question"].strip(), int(r["label"])) for r in csv.DictReader(open(path)) if r["question"].strip()]


def eval_falseqa(w, args):
    rows = falseqa_test(args.cache)
    pr = w.probs([(f"Question: {q}", BS_Q) for q, _ in rows])[:, CON]
    return binary_report([lab for _, lab in rows], pr)


# ----------------------------------------------------------------------------- instruction following
def if_checker():
    sys.path.insert(0, HERE)
    from ifeval_lib import instructions_registry
    from ifeval_lib.instructions_util import download_nltk_resources
    download_nltk_resources()
    reg = instructions_registry.INSTRUCTION_DICT

    def check(iid, kw, prompt, response):
        """(description, strictly followed) -- the same steps as lm_eval's test_instruction_following_strict."""
        inst = reg[iid](iid)
        desc = inst.build_description(**{k: v for k, v in (kw or {}).items() if v is not None})
        a = inst.get_instruction_args()
        if a and "prompt" in a:
            desc = inst.build_description(prompt=prompt)
        return desc, bool(response.strip()) and bool(inst.check_following(response))
    return check


def ifeval_rows(args):
    """[(model, prompt, response, [(iid, kwargs)])]: Open LLM Leaderboard samples when the gated details repos are
    accessible, else the responses written by gen_ifeval.py."""
    rows = []
    try:
        from huggingface_hub import HfApi, hf_hub_download
        api = HfApi()
        for m in IFEVAL_MODELS:
            repo = f"open-llm-leaderboard/{m}-details"
            f = sorted(x for x in api.list_repo_files(repo, repo_type="dataset") if "samples_leaderboard_ifeval" in x)[-1]
            for line in open(hf_hub_download(repo, f, repo_type="dataset")):
                r = json.loads(line)
                d = r["doc"]
                resp = r["resps"][0][0] if isinstance(r["resps"][0], list) else r["resps"][0]
                rows.append((m, d["prompt"], resp, list(zip(d["instruction_id_list"], d["kwargs"]))))
        return rows, "open-llm-leaderboard"
    except Exception as e:  # noqa: BLE001
        print(f"[ifeval] leaderboard samples unavailable ({type(e).__name__}); using {args.ifeval_gen}", flush=True)
    for line in open(args.ifeval_gen):
        r = json.loads(line)
        rows.append((r["model"], r["prompt"], r["response"], list(zip(r["instruction_id_list"], r["kwargs"]))))
    return rows, args.ifeval_gen


def eval_ifeval(w, args):
    check = if_checker()
    rows, source = ifeval_rows(args)
    prem, y_prompt, inst_pairs, inst_y, inst_owner = [], [], [], [], []
    for _, prompt, resp, insts in rows:
        k = len(prem)
        prem.append(f"Request:\n{prompt}\n\nResponse:\n{resp}")
        oks = []
        for iid, kw in insts:
            try:
                desc, ok = check(iid, kw, prompt, resp)
            except Exception:  # noqa: BLE001
                continue
            oks.append(ok)
            inst_pairs.append((prem[k], f"The response satisfies this requirement: {desc}"))
            inst_y.append(int(ok)); inst_owner.append(k)
        y_prompt.append(int(all(oks)))
    p_all = w.probs([(p, IF_ALL) for p in prem])[:, ENT]
    p_inst = w.probs(inst_pairs)[:, ENT]
    p_min = np.ones(len(prem))
    for s, k in zip(p_inst, inst_owner):
        p_min[k] = min(p_min[k], s)
    return {"source": source, "prompt_level": binary_report(y_prompt, p_all),
            "prompt_level_min_over_constraints": binary_report(y_prompt, p_min),
            "instruction_level": binary_report(inst_y, p_inst)}


LLMBAR_SETS = ["Natural", "Adversarial/GPTInst", "Adversarial/GPTOut", "Adversarial/Manual", "Adversarial/Neighbor"]


def eval_llmbar(w, args):
    res = {}
    for s in LLMBAR_SETS:
        path = fetch(f"https://raw.githubusercontent.com/princeton-nlp/LLMBar/main/Dataset/LLMBar/{s}/dataset.json",
                     os.path.join(args.cache, "llmbar"))
        rows = json.load(open(path))
        pairs = []
        for r in rows:
            pairs += [(f"Request:\n{r['input']}\n\nResponse:\n{r['output_1']}", IF_ALL),
                      (f"Request:\n{r['input']}\n\nResponse:\n{r['output_2']}", IF_ALL)]
        pr = w.probs(pairs)[:, ENT].reshape(-1, 2)
        pick = np.where(pr[:, 0] >= pr[:, 1], 1, 2)
        res[s] = {"n": len(rows), "acc": float((pick == np.array([int(r["label"]) for r in rows])).mean())}
    res["avg"] = float(np.mean([v["acc"] for v in res.values()]))
    return res


TASKS = {"aggrefact": eval_aggrefact, "ragtruth": eval_ragtruth, "halubench": eval_halubench, "bsb": eval_bsb,
         "falseqa": eval_falseqa, "ifeval": eval_ifeval, "llmbar": eval_llmbar}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tasks", nargs="+", default=list(TASKS))
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=2048)
    ap.add_argument("--limit", type=int, default=0, help="debug: rows per AggreFact dataset (x3 for the others)")
    ap.add_argument("--bsb-n", type=int, default=4000)
    ap.add_argument("--cache", default="data/extra_cache")
    ap.add_argument("--ifeval-gen", default="data/ifeval_gen.jsonl")
    args = ap.parse_args()
    results = json.load(open(args.out)) if os.path.exists(args.out) else {}
    for m in args.models:
        scorer = NLIScorer(m, bs=args.bs, max_len=args.max_len)
        w = Window(scorer, args.max_len)
        results.setdefault(m, {})
        for t in args.tasks:
            print(f"== {m} :: {t}", flush=True)
            try:
                results[m][t] = TASKS[t](w, args)
            except Exception as e:  # noqa: BLE001  one broken task must not kill the rest
                import traceback
                traceback.print_exc()
                results[m][t] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
            print(json.dumps(results[m][t])[:600], flush=True)
            os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
            json.dump(results, open(args.out, "w"), indent=2)
        del scorer, w
        import torch
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()

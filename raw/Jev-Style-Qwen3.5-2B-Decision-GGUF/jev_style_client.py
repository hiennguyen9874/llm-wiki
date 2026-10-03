"""Typed decisions with calibrated probabilities from a local OpenAI-compatible server.

The model never writes text: one token is requested, and the log-probs of the option
letters at that position are renormalised into the decision distribution. The
calibration temperature is already baked into the weights, so no post-processing
beyond the renormalisation is needed.

    # LM Studio:  load the model, start the local server, then
    python jev_style_client.py --url http://localhost:1234 --model jev-style-qwen3.5-2b-decision
    # llama.cpp:  llama-server -m Jev-Style-Qwen3.5-2B-Decision-Q8_0.gguf --port 8080
    python jev_style_client.py --url http://localhost:8080

Only the Python standard library is used.
"""

import argparse
import json
import math
import urllib.request

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
HEADER = ("You are a decision function. Read the state, then answer the question "
          "by choosing exactly one option.\n\n")
MAX_OPTIONS = 20  # servers return at most ~20 candidate tokens per position


def build_prompt(state, question, options):
    lines = "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(options))
    return f"{HEADER}[State]\n{state}\n\n[Question]\n{question}\n\n[Options]\n{lines}\n\nAnswer:"


def _post(url, payload):
    req = urllib.request.Request(url, json.dumps(payload).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def _top_logprobs(base_url, prompt, model):
    """-> {token_text: logprob} for the first generated position.

    Uses /v1/chat/completions: the released model ships a pass-through chat template, so the
    prompt reaches the model verbatim, and both LM Studio and llama-server return candidate
    log-probs on this endpoint (LM Studio does not on /v1/completions).
    """
    out = _post(base_url.rstrip("/") + "/v1/chat/completions",
                {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 1,
                 "temperature": 0, "logprobs": True, "top_logprobs": 20})
    return {t["token"]: t["logprob"] for t in out["choices"][0]["logprobs"]["content"][0]["top_logprobs"]}


def decide(base_url, state, question, options, model="jev-style"):
    """Choice: -> list of (option, probability), most likely first."""
    assert 2 <= len(options) <= MAX_OPTIONS
    top = _top_logprobs(base_url, build_prompt(state, question, options), model)
    floor = min(top.values()) - 5.0  # option letter outside the returned candidates: negligible mass
    logits = [max((lp for tok, lp in top.items() if tok.strip() == LETTERS[i]), default=floor)
              for i in range(len(options))]
    z = max(logits)
    exp = [math.exp(x - z) for x in logits]
    probs = [e / sum(exp) for e in exp]
    return sorted(zip(options, probs), key=lambda t: -t[1])


def decide_bool(base_url, state, proposition, model="jev-style"):
    """Bool: -> probability that the proposition is true."""
    return dict(decide(base_url, state, proposition, ["yes", "no"], model))["yes"]


def decide_score(base_url, state, question, levels, model="jev-style"):
    """Score: ordered levels -> (expected level index in [0, len-1], distribution)."""
    dist = dict(decide(base_url, state, question, levels, model))
    return sum(i * dist[l] for i, l in enumerate(levels)), [(l, dist[l]) for l in levels]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:1234")
    ap.add_argument("--model", default="jev-style-qwen3.5-2b-decision")
    args = ap.parse_args()
    url, mid = args.url, args.model

    review = "The plot is thin, but the two leads are so charming that I left the cinema smiling."
    print("Choice:", decide(url, review, "What is the sentiment of this review?", ["negative", "positive"], mid))
    print("Score :", decide_score(url, review, "Rate the sentiment of this review on an ordered scale.",
                                  ["very negative", "negative", "neutral", "positive", "very positive"], mid))
    print("Bool  :", decide_bool(
        url, "Premise: A man is playing a guitar on stage.\nHypothesis: Someone is performing music.",
        "Does the premise entail the hypothesis?", mid))
    news = "Shares of the chipmaker jumped 8% after it raised its full-year revenue forecast."
    print("Choice:", decide(url, news, "Which news section does this article belong to?",
                            ["World", "Sports", "Business", "Science/Technology"], mid))

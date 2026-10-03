"""OpenRouter Decisions API (`POST /api/alpha/decisions`, `POST /api/v1/systemone`) on top of an openjev cross-encoder.

Pure logic, no web framework and no model: `build_plan` turns a request into (premise, hypothesis) pairs, the caller scores
them (P(entailment) per pair, see decisions_server.py) and `assemble` turns those scores into the `answers` object.
The pair format is the one v5 was trained on (data_mix.py JEV_TEMPLATES[0], eval_jevbench.py `options`, openjev_decide.py):
every option becomes `The answer to "{instr}" is {label}: {crit}` over the state, the answer distribution is P(entailment)
normalised over the options of that question.

    plan = build_plan(request)                 # ApiError(code, message) on a malformed request
    answers = assemble(plan, ent_probs)        # ent_probs: one P(entailment) per plan.pairs entry
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field

import numpy as np

# openjev_decide.py imports torch, so the shared strings are duplicated here; test_decisions_api.py asserts they agree.
HYPOTHESIS = 'The answer to "{instr}" is {label}: {crit}'
WINDOW_CHARS = 24_000  # one window fits the encoder; a longer state is scored window by window, max over windows
OVERLAP_CHARS = 2_000
MAX_STATE_CHARS = 110_000  # ~32k tokens, the context limit OpenRouter documents for state + questions
MAX_QUESTIONS = 64
MAX_OPTIONS = 64
ENT = 1  # label order 0/1/2 = contradiction/entailment/neutral, never reorder
QTYPES = ("noul", "choice", "score")


class ApiError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code, self.message = code, message

    def body(self) -> dict:
        return {"error": {"code": self.code, "message": self.message}}


@dataclass
class QPlan:
    qid: str
    qtype: str
    keys: list  # answer keys in output order: choice keys, ["false", "true"] for noul, ["0", "1", ...] for score
    n_windows: int
    start: int  # offset of this question's block in Plan.pairs
    legend: dict = field(default_factory=dict)


@dataclass
class Plan:
    pairs: list  # (premise, hypothesis)
    questions: list


def _text(v) -> str:
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def _windows(state: str) -> list:
    if len(state) <= WINDOW_CHARS:
        return [state]
    step = WINDOW_CHARS - OVERLAP_CHARS
    return [state[s:s + WINDOW_CHARS] for s in range(0, max(len(state) - OVERLAP_CHARS, 1), step)]


def _options(qid: str, q: dict) -> tuple:
    """(keys, labels, crits): keys are the answer keys, labels/crits fill the hypothesis for each key."""
    if not isinstance(q, dict) or q.get("type") not in QTYPES:
        raise ApiError(400, f"questions.{qid}.type must be one of {list(QTYPES)}")
    t, crit = q["type"], q.get("criteria")
    if t == "noul":
        if crit is None:
            # Same default rubric as OpenJev._rubric for bare ["no", "yes"].
            crit = {"false": "no", "true": "yes"}
        if not isinstance(crit, dict) or not isinstance(crit.get("true"), str) or not isinstance(crit.get("false"), str):
            raise ApiError(400, f'questions.{qid}.criteria must be {{"true": str, "false": str}} for type "noul"')
        return ["false", "true"], ["no", "yes"], [crit["false"], crit["true"]]
    if t == "choice":
        if not isinstance(crit, dict) or not crit:
            raise ApiError(400, f'questions.{qid}.criteria must be a non-empty object for type "choice"')
        if len(crit) > MAX_OPTIONS:
            raise ApiError(400, f"questions.{qid}.criteria has more than {MAX_OPTIONS} options")
        keys = [str(k) for k in crit]
        return keys, keys, [_text(v) for v in crit.values()]
    if not isinstance(crit, list) or not crit:
        raise ApiError(400, f'questions.{qid}.criteria must be a non-empty array for type "score"')
    if len(crit) > MAX_OPTIONS:
        raise ApiError(400, f"questions.{qid}.criteria has more than {MAX_OPTIONS} levels")
    keys = [str(i) for i in range(len(crit))]
    return keys, keys, [_text(c) for c in crit]


def build_plan(req) -> Plan:
    if not isinstance(req, dict):
        raise ApiError(400, "request body must be a JSON object")
    if not isinstance(req.get("model"), str) or not req["model"]:
        raise ApiError(400, "model is required")
    if "state" not in req or req["state"] is None or not isinstance(req["state"], (str, dict, list)):
        raise ApiError(400, "state is required and must be a string, object or array")
    qs = req.get("questions")
    if not isinstance(qs, dict) or not qs:
        raise ApiError(400, "questions must be a non-empty object")
    if len(qs) > MAX_QUESTIONS:
        raise ApiError(400, f"at most {MAX_QUESTIONS} questions per request")
    state = _text(req["state"]).strip()
    if len(state) > MAX_STATE_CHARS:
        raise ApiError(413, f"state is {len(state)} characters, over the {MAX_STATE_CHARS} (~32k token) limit")
    windows = _windows(state)
    pairs, plans = [], []
    for qid, q in qs.items():
        keys, labels, crits = _options(str(qid), q)
        instr = _text(q.get("instructions", "")).strip()
        start = len(pairs)
        for w in windows:
            for lab, crit in zip(labels, crits):
                pairs.append((w, HYPOTHESIS.format(instr=instr, label=lab, crit=crit)))
        legend = {k: c for k, c in zip(keys, crits)} if q["type"] == "score" else {}
        plans.append(QPlan(str(qid), q["type"], keys, len(windows), start, legend))
    return Plan(pairs, plans)


def softmax_ent(logits) -> np.ndarray:
    """[n, 3] raw logits (contradiction, entailment, neutral) -> P(entailment) per row."""
    z = np.asarray(logits, dtype=np.float64)
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e[:, ENT] / e.sum(axis=1)


def confidence(p) -> float:
    """1 - normalised entropy. OpenRouter does not publish its definition; this is an approximation."""
    p = np.asarray(p, dtype=np.float64)
    if len(p) < 2:
        return 1.0
    h = -float(np.sum(p[p > 0] * np.log(p[p > 0])))
    return max(0.0, 1.0 - h / math.log(len(p)))


def assemble(plan: Plan, ent) -> dict:
    ent = np.asarray(ent, dtype=np.float64)
    if ent.shape != (len(plan.pairs),) or not np.isfinite(ent).all() or ((ent < 0) | (ent > 1)).any():
        raise ValueError(f"expected {len(plan.pairs)} scores, got {len(ent)}")
    answers = {}
    for q in plan.questions:
        n = len(q.keys)
        block = ent[q.start:q.start + q.n_windows * n].reshape(q.n_windows, n)
        p = block.max(0)  # a claim supported by any window is supported by the document
        total = float(p.sum())
        p = p / total if total > 0 else np.full(n, 1.0 / n)
        probs = {k: round(float(x), 4) for k, x in zip(q.keys, p)}
        if q.qtype == "noul":
            answers[q.qid] = {"type": "noul", "noul": round(float(p[q.keys.index("true")]), 4)}
        elif q.qtype == "choice":
            answers[q.qid] = {"type": "choice", "choice": q.keys[int(p.argmax())],
                              "confidence": round(confidence(p), 4), "probabilities": probs}
        else:
            answers[q.qid] = {"type": "score", "score": round(float(np.dot(np.arange(n), p)), 4),
                              "confidence": round(confidence(p), 4), "probabilities": probs, "legend": q.legend}
    return answers

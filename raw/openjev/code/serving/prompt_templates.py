"""Generic, explicit prompt alternatives. The production default stays trained."""
from dataclasses import dataclass

import numpy as np

from decisions_api import Plan, _options, _text, assemble, build_plan

STYLES = ("trained", "unquoted", "direct_noul")


@dataclass
class PromptPlan:
    base: Plan
    pairs: list
    # Each base score either comes from one model score or a boolean complement.
    ordinary: list
    direct: list


def build_prompt_plan(body, style="trained"):
    if style not in STYLES:
        raise ValueError(f"Unknown prompt style: {style}")
    base = build_plan(body)
    pairs, ordinary, direct = [], [], []
    for q in base.questions:
        source = body["questions"][q.qid]
        instr = _text(source.get("instructions", "")).strip()
        _, labels, crits = _options(q.qid, source)
        n = len(labels)
        if style == "direct_noul" and q.qtype == "noul" and source.get("criteria") is None:
            positions = []
            for w in range(q.n_windows):
                positions.append(len(pairs))
                pairs.append((base.pairs[q.start + w * n][0], instr))
            direct.append((q, positions))
            continue
        for w in range(q.n_windows):
            for j in range(n):
                index = q.start + w*n + j
                premise, hypothesis = base.pairs[index]
                if style == "unquoted":
                    hypothesis = f"Question: {instr}\nAnswer: {labels[j]}: {crits[j]}"
                ordinary.append((index, len(pairs)))
                pairs.append((premise, hypothesis))
    return PromptPlan(base, pairs, ordinary, direct)


def finish_answers(plan, entailment):
    e = np.asarray(entailment, dtype=float)
    if e.shape != (len(plan.pairs),) or not np.isfinite(e).all() or ((e < 0) | (e > 1)).any():
        raise ValueError("Invalid entailment scores")
    expanded = np.empty(len(plan.base.pairs), dtype=float)
    for old, new in plan.ordinary:
        expanded[old] = e[new]
    for q, positions in plan.direct:
        # A bare assertion is true to the degree it is entailed. Neutral mass
        # stays outside P(true); no gold-derived temperature or calibration.
        true = float(e[positions].max())
        for w in range(q.n_windows):
            expanded[q.start + 2*w:q.start + 2*w + 2] = [1-true, true]
    return assemble(plan.base, expanded)

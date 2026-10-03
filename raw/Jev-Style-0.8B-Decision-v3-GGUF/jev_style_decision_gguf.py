"""Jev-Style-0.8B-Decision-v3: typed decisions with llama.cpp (GGUF F16 / Q8_0 / Q4_K_M).

Self-contained runtime for chaoliangUNSW/Jev-Style-0.8B-Decision-v3 (Apache-2.0). No dependency on any training code:
rendering, verdict readout and calibration are implemented below and reproduce the reference
implementation used for evaluation (see release_config.json -> "runtime_parity").

Calibration temperature: with no category (the default) probabilities use the global temperature of
readout_config.json (temperatures.global = 0.880); pass category=... (CLI --category, JSONL "category")
for the fitted group temperature of that category's family x question type x option-count bucket, or
temperature=... to override (1.0 = uncalibrated scores).
"""
# ----------------------------------------------------------------------------------------------
# Shared core (identical in jev_style_decision.py, jev_style_decision_gguf.py and
# jev_style_decision_mlx.py): input rendering, verdict readout, calibrated probabilities.
#
# Input layout ("macjev-render-v1"; token segments are encoded separately and concatenated):
#
#   State:\n<state>\n\n
#   Question [<type>]: <question>\nOptions:\n
#   - <option 1>\n ... - <option K>\n
#   Judge each option:\n
#   <option 1> ->\n ... <option K> ->\n
#
# Score of option k = logit(" yes") - logit(" no") at the k-th " ->" token (computed from the final
# hidden state and the tied embedding rows, float32). Probabilities = softmax(scores / T), where T is
# the calibration temperature shipped in readout_config.json:
#   * no category given (the default): T = temperatures.global (the file's global temperature);
#   * category="..." given: T = the fitted group temperature of (family of that category x question
#     type x option-count bucket), or temperatures.global when that group was not fitted;
#   * temperature=... given: that value (1.0 = uncalibrated scores).
# T is clamped to temperatures.clamp. Text inside the state or options is tokenised with special
# tokens disabled, so e.g. "<|im_end|>" in user text can never act as a control token.
#
# Budgets: whole input <= 25,600 tokens; question + options + readout ("head") <= 2,048 tokens.
# Larger inputs raise InputBudgetError. Nothing is ever truncated.
# ----------------------------------------------------------------------------------------------
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

MODEL_NAME = "Jev-Style-0.8B-Decision-v3"
TEMPLATE_VERSION = "macjev-render-v1"
READOUT_FORMAT = "macjev-readout-v1"
CONTEXT_LIMIT = 25_600          # state + question + options + readout
HARD_HEAD_MAX = 2048            # question + options + readout
QTYPES = ("choice", "score", "noul")
HERE = Path(__file__).resolve().parent

# calibration families (category prefix -> family), same table the temperatures were fitted with
FAMILY_BY_CATEGORY_PREFIX = (("typed_official", "typed"), ("typed_synthetic", "typed_synth"), ("general_", "general"),
                             ("intent", "intent"), ("nli", "nli"), ("theme_", "theme"), ("mac_", "mac"),
                             ("long_", "long"))


class InputBudgetError(ValueError):
    """The rendered input exceeds a token budget. Nothing was truncated."""


class QuestionError(ValueError):
    """The question/options are malformed."""


# -- questions ------------------------------------------------------------------------------------
def option_names(question):
    """Canonical option identifiers, in the order the probabilities are returned."""
    if not isinstance(question, dict):
        raise QuestionError("question must be a dict {'t', 'ins', 'crit'}")
    t, crit = question.get("t"), question.get("crit")
    if not isinstance(question.get("ins"), str) or not question["ins"].strip():
        raise QuestionError("question text ('ins') must be a non-empty string")
    if t == "choice":
        if not isinstance(crit, dict) or not crit:
            raise QuestionError("choice needs a non-empty dict {option name: description or None}")
        return [str(k) for k in crit]
    if t == "score":
        if not isinstance(crit, list) or not 2 <= len(crit) <= 10:
            raise QuestionError("score needs a list of 2..10 level descriptions")
        return [str(i) for i in range(len(crit))]
    if t == "noul":
        if crit is not None and not isinstance(crit, dict):
            raise QuestionError("noul criteria must be None or {'false': ..., 'true': ...}")
        return ["false", "true"]
    raise QuestionError(f"unknown question type {t!r} (expected one of {QTYPES})")


def make_question(question, options=None, qtype=None):
    """Build a typed question.

    * ``question`` already a dict {"t", "ins", "crit"}: validated and returned.
    * ``qtype="choice"`` (default when ``options`` is given): ``options`` = {name: description or None}
      or a list of names.
    * ``qtype="score"``: ``options`` = list of 2..10 level descriptions (level 0 first).
    * ``qtype="noul"`` (default when no options): a true/false statement; ``options`` may be
      {"false": "...", "true": "..."} to describe the two outcomes.
    """
    if isinstance(question, dict):
        q = dict(question)
    else:
        if qtype is None:
            qtype = "choice" if options is not None else "noul"
        if qtype == "choice":
            if isinstance(options, (list, tuple)):
                if len(set(map(str, options))) != len(options):
                    raise QuestionError("duplicate option names")
                crit = {str(o): None for o in options}
            else:
                crit = options
        elif qtype == "score":
            crit = list(options) if options is not None else None
        else:
            crit = options
        q = {"t": qtype, "ins": question, "crit": crit}
    option_names(q)
    return q


def serialize_state(state):
    """Strings pass through unchanged; any other JSON value is serialised (ensure_ascii=False)."""
    if isinstance(state, str):
        return state
    return json.dumps(state, ensure_ascii=False)


def _criterion(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(", ", ": "), default=str)


def render_options(question):
    t, crit = question["t"], question.get("crit")
    if t == "choice":
        return [k if v is None or v == "" else f"{k}: {_criterion(v)}" for k, v in crit.items()]
    if t == "score":
        return [f"level {i}: {_criterion(c)}" for i, c in enumerate(crit)]
    crit = crit or {}
    false_c, true_c = crit.get("false"), crit.get("true")
    return ["false: " + (_criterion(false_c) if false_c not in (None, "") else "no, the statement does not hold"),
            "true: " + (_criterion(true_c) if true_c not in (None, "") else "yes, the statement holds")]


# -- tokenizer + renderer -----------------------------------------------------------------------
class TextEncoder:
    """HF ``tokenizers`` tokenizer.json; no BOS/EOS, special tokens in text are split (never control tokens)."""

    def __init__(self, tokenizer_json):
        from tokenizers import Tokenizer
        self.tk = Tokenizer.from_file(str(tokenizer_json))
        self.tk.encode_special_tokens = True

    def __call__(self, text):
        return self.tk.encode(text, add_special_tokens=False).ids


class Rendered:
    __slots__ = ("ids", "prefix_len", "slots", "names", "head_tokens")

    def __init__(self, ids, prefix_len, slots, names, head_tokens):
        self.ids, self.prefix_len, self.slots, self.names, self.head_tokens = ids, prefix_len, slots, names, head_tokens


class Renderer:
    def __init__(self, encode, readout_cfg, max_len=CONTEXT_LIMIT, head_max=HARD_HEAD_MAX):
        if readout_cfg.get("format") != READOUT_FORMAT or readout_cfg.get("template") != TEMPLATE_VERSION:
            raise ValueError("readout_config.json is not a macjev-readout-v1 / macjev-render-v1 config")
        if readout_cfg.get("readout") != "verdict":
            raise ValueError("this runtime implements the verdict readout only")
        if not 0 < int(max_len) <= CONTEXT_LIMIT:
            raise ValueError(f"max_len must be in 1..{CONTEXT_LIMIT}")
        if not 0 < int(head_max) <= HARD_HEAD_MAX:
            raise ValueError(f"head_max must be in 1..{HARD_HEAD_MAX}")
        self.enc, self.max_len, self.head_max = encode, int(max_len), int(head_max)
        st = readout_cfg["slot_tokens"]
        self.yes, self.no, arrow = int(st["yes"]["id"]), int(st["no"]["id"]), int(st["verdict_slot"]["id"])
        for text, want in ((" yes", self.yes), (" no", self.no), (" ->", arrow)):
            got = self.enc(text)
            if got != [want]:
                raise ValueError(f"tokenizer mismatch: {text!r} -> {got}, readout_config expects [{want}]")
        self.arrow = [arrow]
        self.newline = self.enc("\n")
        self.dash = self.enc("- ")
        self.judge = self.enc("Judge each option:\n")

    def prefix_ids(self, state):
        return self.enc("State:\n") + self.enc(serialize_state(state)) + self.enc("\n\n")

    def plan_option_chunks(self, question, head_max=None):
        """Option split for a choice question whose options do not fit the head budget together.

        Returns None when the whole question fits (the normal, unsplit path). Otherwise a list of
        contiguous option-name chunks, in request order, each rendering within ``head_max``: the
        fewest chunks possible, balanced by token count. Every chunk repeats the question text, so
        each option is judged exactly as in an ordinary question with fewer options. Raises
        InputBudgetError when a single option cannot fit even alone. Token counts are exact: the
        renderer encodes these pieces separately and concatenates them."""
        head_max = self.head_max if head_max is None else int(head_max)
        names = option_names(question)
        opts = [self.enc(o) for o in render_options(question)]
        fixed = len(self.enc(f"Question [{question['t']}]: {question['ins']}\nOptions:\n")) + len(self.judge)
        cost = [len(self.dash) + 2 * len(o) + len(self.arrow) + 2 * len(self.newline) for o in opts]
        if fixed + sum(cost) <= head_max:
            return None
        room = head_max - fixed
        if question["t"] != "choice":
            raise InputBudgetError(f"question + options + readout need {fixed + sum(cost)} tokens; the head budget "
                                   f"is {head_max}. Only choice questions are split over option chunks.")
        if max(cost) > room:
            raise InputBudgetError(f"one option needs {max(cost)} tokens, more than the {room} left for options "
                                   f"under the {head_max}-token head budget. Nothing was truncated.")

        def pack(cap):
            chunks, cur, used = [], [], 0
            for n, c in zip(names, cost):
                if cur and used + c > cap:
                    chunks.append(cur)
                    cur, used = [], 0
                cur.append(n)
                used += c
            return chunks + [cur]

        k = len(pack(room))                           # fewest chunks
        total = sum(cost)
        for cap in range(max(max(cost), -(-total // k)), room + 1):
            chunks = pack(cap)                        # smallest cap that still needs only k chunks = balanced
            if len(chunks) <= k:
                return chunks
        return pack(room)

    def render(self, state, question, head_max=None, max_len=None):
        head_max = self.head_max if head_max is None else int(head_max)
        max_len = self.max_len if max_len is None else min(int(max_len), self.max_len)
        if head_max > HARD_HEAD_MAX:
            raise InputBudgetError(f"head_max may not exceed {HARD_HEAD_MAX}")
        names = option_names(question)
        opts = [self.enc(o) for o in render_options(question)]
        suffix = self.enc(f"Question [{question['t']}]: {question['ins']}\nOptions:\n")
        for o in opts:
            suffix += self.dash + o + self.newline
        suffix += self.judge
        rel = []
        for o in opts:
            suffix += o + self.arrow
            rel.append(len(suffix) - 1)
            suffix += self.newline
        if len(suffix) > head_max:
            raise InputBudgetError(f"question + options + readout need {len(suffix)} tokens; the head budget is "
                                   f"{head_max} (hard cap {HARD_HEAD_MAX}). Nothing was truncated: shorten the "
                                   f"question/options or split the options over several questions.")
        prefix = self.prefix_ids(state)
        ids = prefix + suffix
        if len(ids) > max_len:
            raise InputBudgetError(f"input needs {len(ids)} tokens (state {len(prefix)} + head {len(suffix)}); the "
                                   f"limit is {max_len} (model maximum {CONTEXT_LIMIT}). Nothing was truncated: "
                                   f"shorten the state.")
        return Rendered(ids, len(prefix), [len(prefix) + s for s in rel], names, len(suffix))


class SplitRendered:
    """Several renders of one choice question (one per option chunk), read as one decision."""
    __slots__ = ("parts", "chunks", "names", "input_tokens", "head_tokens")

    def __init__(self, parts, chunks, names):
        self.parts, self.chunks, self.names = parts, chunks, names
        self.input_tokens = sum(len(r.ids) for r in parts)
        self.head_tokens = sum(r.head_tokens for r in parts)


# -- calibration ----------------------------------------------------------------------------------
def family(category):
    for prefix, fam in FAMILY_BY_CATEGORY_PREFIX:
        if category.startswith(prefix):
            return fam
    return "other"


def option_bucket(k):
    return "2" if k <= 2 else "3-5" if k <= 5 else "6-10" if k <= 10 else "11-20" if k <= 20 else "21+"


def lookup_temperature(temps, category, qtype, n_options):
    """Calibration temperature. ``category`` None/"" -> the global temperature; otherwise the fitted
    group (family(category) x qtype x option bucket), falling back to the global temperature."""
    g = None
    if category:
        g = (temps.get("groups") or {}).get(f"{family(category)}|{qtype}|{option_bucket(n_options)}")
    t = g["T"] if g else temps.get("global", 1.0)
    lo, hi = temps.get("clamp", [0.3, 5.0])
    return float(min(hi, max(lo, t)))


def concentration(p):
    k = len(p)
    if k < 2:
        return 1.0
    ent = -(p * np.log(np.clip(p, 1e-12, 1.0))).sum()
    return float(np.clip(1.0 - ent / math.log(k), 0.0, 1.0))


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def verify_manifest(model_dir, only=None):
    """Re-hash the files listed in manifest.json (all, or those whose path starts with one of ``only``).
    Documentation (README.md, figures/, assets/) is recorded in the manifest but not checked here, so
    a card edit never makes the runtime refuse to load."""
    model_dir = Path(model_dir)
    man = json.loads((model_dir / "manifest.json").read_text())
    bad, missing, checked = [], [], 0
    for name, rec in man["files"].items():
        if name == "README.md" or name.startswith(("assets/", "figures/")):
            continue
        if only and not any(name == o or name.startswith(o.rstrip("/") + "/") for o in only):
            continue
        p = model_dir / name
        if not p.exists():
            missing.append(name)
        elif _sha256(p) != rec["sha256"]:
            bad.append(name)
        checked += 1
    return {"ok": not bad and not missing, "checked": checked, "bad": bad, "missing": missing}


class DecisionBase:
    """Backend-independent part. Subclasses implement ``_scores(rendered) -> list[float]`` and may
    override ``_scores_many(list of rendered) -> list of list[float]`` (several questions, one state).

    Calibration: ``category`` (constructor default or per call) selects the fitted group temperature
    of that category's family; with no category anywhere, the global temperature of
    readout_config.json (temperatures.global) is used."""
    backend = "base"

    def _setup(self, model_dir, tokenizer_json, category=None, head_max=HARD_HEAD_MAX, max_len=CONTEXT_LIMIT):
        self.model_dir = Path(model_dir)
        self.readout_config = json.loads((self.model_dir / "readout_config.json").read_text())
        self.temperatures = self.readout_config["temperatures"]
        self.default_category = category or None       # None -> temperatures.global
        self.encode = TextEncoder(tokenizer_json)
        self.renderer = Renderer(self.encode, self.readout_config, max_len=max_len, head_max=head_max)

    def temperature(self, question, category=None):
        """T for ``question``: group temperature of ``category`` (or the constructor's default category);
        the global temperature when neither is given."""
        return lookup_temperature(self.temperatures, category or self.default_category, question["t"],
                                  len(option_names(question)))

    split_options = True      # choice questions over the head budget are scored in option chunks

    def _scores_many(self, rendered):
        return [self._scores(r) for r in rendered]

    def _render(self, state, q, head_max=None):
        """Render one question; a choice question whose options exceed the head budget becomes a
        SplitRendered (see Renderer.plan_option_chunks) unless ``split_options`` is False."""
        chunks = self.renderer.plan_option_chunks(q, head_max) if self.split_options else None
        if chunks is None:
            return self.renderer.render(state, q, head_max=head_max)
        parts = [self.renderer.render(state, dict(q, crit={n: q["crit"][n] for n in c}), head_max=head_max)
                 for c in chunks]
        return SplitRendered(parts, chunks, option_names(q))

    def _score_all(self, rendered):
        """Scores for a list of Rendered / SplitRendered: all parts go into one _scores_many call
        (one backend request per state); a split question gets its chunks' option scores back in
        option order."""
        flat = [p for r in rendered for p in (r.parts if isinstance(r, SplitRendered) else [r])]
        scores = self._scores_many(flat) if len(flat) > 1 else [self._scores(flat[0])]
        out, i = [], 0
        for r in rendered:
            n = len(r.parts) if isinstance(r, SplitRendered) else 1
            out.append([x for sc in scores[i:i + n] for x in sc])
            i += n
        return out

    def _result(self, r, q, scores, category=None, temperature=None):
        scores = [float(x) for x in scores]
        t = float(temperature) if temperature is not None else self.temperature(q, category)
        z = np.asarray(scores, float) / t
        if not np.all(np.isfinite(z)):
            raise FloatingPointError("non-finite decision scores")
        p = np.exp(z - z.max())
        p /= p.sum()
        i = int(p.argmax())
        return {"answer": r.names[i], "probabilities": dict(zip(r.names, p.tolist())),
                "scores": dict(zip(r.names, scores)), "temperature": t, "top_probability": float(p[i]),
                "entropy_concentration": concentration(p),
                "input_tokens": r.input_tokens if isinstance(r, SplitRendered) else len(r.ids),
                "head_tokens": r.head_tokens, "model": MODEL_NAME, "backend": self.backend,
                **({"option_chunks": len(r.parts)} if isinstance(r, SplitRendered) else {})}

    def decide(self, state, question, options=None, qtype=None, category=None, temperature=None, head_max=None):
        """Score one question about ``state``.

        Returns {"answer", "probabilities" {option: p}, "scores" {option: logit(yes)-logit(no)},
        "temperature", "top_probability", "entropy_concentration", "input_tokens", "head_tokens"}.
        Temperature: with no ``category`` (here or in the constructor) the global temperature of
        readout_config.json is used; ``category`` picks the fitted group temperature of its family
        (e.g. "mac_gate", "general_topic", "theme_routing", "intent", "typed_official");
        ``temperature`` overrides both (1.0 = uncalibrated scores).
        A choice question whose options exceed the 2,048-token head budget is scored in option chunks
        (``option_chunks`` in the result): each chunk is an ordinary question with the same text and a
        contiguous slice of the options, and the per-option scores of all chunks go through one softmax.
        Raises InputBudgetError (never truncates) or QuestionError.
        """
        q = make_question(question, options, qtype)
        r = self._render(state, q, head_max)
        return self._result(r, q, self._score_all([r])[0], category, temperature)

    def decide_many(self, state, questions, category=None, temperature=None, head_max=None):
        """Several questions about the same state (each a dict {"t","ins","crit"}); results in order.
        Same outputs as calling decide() per question. The llama.cpp runtime sends all questions in one
        request and shares the state in whole 1,024-token ubatches (see JevStyleDecisionGGUF, also for
        its faster, not bit-identical many_mode="batched"). All questions are rendered and
        budget-checked before any scoring."""
        qs = [make_question(q) for q in questions]
        rs = [self._render(state, q, head_max) for q in qs]
        if not rs:
            return []
        return [self._result(r, q, sc, category, temperature) for r, q, sc in zip(rs, qs, self._score_all(rs))]


def base_arg_parser(description):
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--model-dir", default=str(HERE), help="folder with the weights and readout_config.json")
    ap.add_argument("--state", help="state as plain text")
    ap.add_argument("--state-json", help="state as a JSON value")
    ap.add_argument("--question", help="question text (or a JSON question {'t','ins','crit'})")
    ap.add_argument("--options", help="JSON: {name: description} or [names] (choice); [levels] (score)")
    ap.add_argument("--qtype", choices=QTYPES)
    ap.add_argument("--category", help="calibration family key, e.g. mac_gate, general_topic, theme_routing, intent "
                                       "(default: none -> the global temperature of readout_config.json)")
    ap.add_argument("--temperature", type=float, help="override the calibrated temperature")
    ap.add_argument("--head-max", type=int, default=HARD_HEAD_MAX)
    ap.add_argument("--max-len", type=int, default=CONTEXT_LIMIT)
    ap.add_argument("--jsonl", help="batch mode: input JSON lines {id?, state, question, options?, qtype?, "
                                    "category?}; one JSON result per line on stdout")
    ap.add_argument("--verify", action="store_true", help="check sha256 of the files in manifest.json first")
    return ap


def run_cli(args, engine):
    def one(rec):
        q = rec["question"]
        return engine.decide(rec.get("state", ""), q, options=rec.get("options"), qtype=rec.get("qtype"),
                             category=rec.get("category"), temperature=rec.get("temperature", args.temperature))
    if args.jsonl:
        src = sys.stdin if args.jsonl == "-" else open(args.jsonl, encoding="utf-8")
        for n, line in enumerate(src):
            if not line.strip():
                continue
            rec = json.loads(line)
            rid = rec.get("id", n)
            try:
                out = {"id": rid, **one(rec)}
            except (InputBudgetError, QuestionError) as e:
                out = {"id": rid, "error": f"{type(e).__name__}: {e}"}
            print(json.dumps(out, ensure_ascii=False), flush=True)
        return 0
    if args.question is None:
        raise SystemExit("--question (or --jsonl) is required")
    state = json.loads(args.state_json) if args.state_json is not None else (args.state or "")
    question = args.question
    if question.lstrip().startswith("{"):
        question = json.loads(question)
    rec = {"state": state, "question": question, "options": json.loads(args.options) if args.options else None,
           "qtype": args.qtype, "category": args.category}
    print(json.dumps(one(rec), ensure_ascii=False, indent=2))
    return 0
# ---------------------------------------------------------------------------- end of shared core


# ---------------------------------------------------------------------------- llama.cpp backend
import os
import shutil
import subprocess
import threading

GGUF_FILES = {q: f"{MODEL_NAME}-{q}.gguf" for q in ("F16", "Q8_0", "Q4_K_M")}
LLAMA_N_CTX = 32768        # >= 25,600-token context + room for question suffixes
assert LLAMA_N_CTX >= CONTEXT_LIMIT + 3 * HARD_HEAD_MAX
MANY_MODES = ("exact", "batched")


def find_scorer(binary=None):
    """jev-score binary: argument, $JEV_SCORE_BIN, ./build/jev-score, or on PATH."""
    for cand in (binary, os.environ.get("JEV_SCORE_BIN"), HERE / "build" / "jev-score", shutil.which("jev-score")):
        if cand and Path(cand).is_file():
            return Path(cand)
    raise FileNotFoundError("jev-score binary not found: build it with `sh build_jev_score.sh /path/to/llama.cpp` "
                            "(see the header of jev_score.cpp), or pass --jev-score / set JEV_SCORE_BIN")


class JevStyleDecisionGGUF(DecisionBase):
    """llama.cpp runtime. The GGUF is run by ``jev-score`` (jev_score.cpp, a ~350-line libllama
    program shipped in this repo), which reads the " yes" / " no" logits only at the slot positions;
    this class renders inputs with the shipped tokenizer and applies the readout + calibration.

    quant: "F16" (validated default), "Q8_0" or "Q4_K_M".

    ``decide`` sends one request per question: state + question in one decode ("fused"), the
    validated path.

    ``decide_many`` sends all questions about one state in ONE jev-score request.
    many_mode="exact" (default): results are bit-identical to calling ``decide`` per question
    (and do not depend on which other questions are in the request). llama.cpp decodes in
    ubatches of n_ubatch (1,024) tokens, and the Gated DeltaNet state and the kernel choice depend
    on how the input is split, so only whole ubatches of the state can be shared: the first
    floor(state_tokens / 1024) * 1024 tokens are decoded once and kept, and the rest of the state
    plus each question is decoded on a copy of it, exactly as ``decide`` splits them. States
    shorter than 1,024 tokens share nothing (each question recomputes the state, still in one
    request); the saving grows with the state length.
    many_mode="batched": the whole state is decoded once and all questions go into one decode
    (jev-score "batched" mode, the mode of the published latency figures). It is the fastest
    option but not bit-identical to ``decide``: in our tests probabilities differed by up to 4.4e-4
    (F16, Q8_0) and 1.7e-3 (Q4_K_M), and a near-tied top answer can change (1 of 201 test pairs on
    F16 and on Q8_0); see release_config.json -> runtime_parity -> decide_many.
    """
    backend = "llama.cpp"

    def __init__(self, model_dir=HERE, quant="F16", gguf=None, binary=None, category=None, head_max=HARD_HEAD_MAX,
                 max_len=CONTEXT_LIMIT, n_gpu_layers=999, threads=None, flash_attn="auto", n_ubatch=1024,
                 many_mode="exact", verify=False, stderr=None, split_options=True):
        self.split_options = bool(split_options)
        if many_mode not in MANY_MODES:
            raise ValueError(f"many_mode must be one of {MANY_MODES}, got {many_mode!r}")
        self.many_mode = many_mode
        model_dir = Path(model_dir)
        self.gguf = Path(gguf) if gguf else model_dir / GGUF_FILES[quant.upper()]
        if verify:
            res = verify_manifest(model_dir, only=["tokenizer", "readout_config.json", self.gguf.name])
            if not res["ok"]:
                raise RuntimeError(f"integrity check failed: {res}")
        self._setup(model_dir, model_dir / "tokenizer" / "tokenizer.json", category, head_max, max_len)
        self.binary = find_scorer(binary)
        cmd = [str(self.binary), "--model", str(self.gguf), "--n-ctx", str(LLAMA_N_CTX), "--n-ubatch", str(n_ubatch),
               "--ngl", str(n_gpu_layers), "--flash-attn", flash_attn, "--n-seq-max", "17", "--n-outputs-max", "256"]
        if threads:
            cmd += ["--threads", str(threads)]
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=stderr if stderr is not None else subprocess.DEVNULL, text=True, bufsize=1)
        self._lock = threading.Lock()
        line = self.proc.stdout.readline()
        ready = json.loads(line) if line else {"ready": False, "error": "no output (see stderr)"}
        if not ready.get("ready"):
            raise RuntimeError(f"jev-score failed to start: {ready}")
        self.info = ready

    def _request(self, req):
        with self._lock:
            self.proc.stdin.write(json.dumps(req) + "\n")
            self.proc.stdin.flush()
            line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("jev-score exited")
        resp = json.loads(line)
        if "error" in resp:
            raise RuntimeError(f"jev-score: {resp['error']}")
        return resp

    def _scores(self, r):
        rows = [self.renderer.yes, self.renderer.no]
        resp = self._request({"prefix": r.ids[:r.prefix_len], "share_prefix": True, "keep_prefix": False,
                              "mode": "fused",
                              "questions": [{"ids": r.ids[r.prefix_len:], "slots": r.slots, "rows": rows}]})
        return [float("nan") if (y is None or n is None) else y - n for y, n in resp["results"][0]["scores"]]

    def _shared_len(self, n_prefix):
        """State tokens decoded once in many_mode="exact": whole ubatches only, so that every ubatch
        (and with it the Gated DeltaNet chunking and the llama.cpp kernel choice) is exactly the one
        ``decide`` uses; any other split can change the scores by ~1e-3."""
        u = int(self.info.get("n_ubatch") or 1024)
        return (n_prefix // u) * u

    def _scores_many(self, rendered):
        """All questions of one state in ONE jev-score request (see the class docstring for many_mode)."""
        if len(rendered) == 1:
            return [self._scores(rendered[0])]
        n_prefix = rendered[0].prefix_len
        prefix = rendered[0].ids[:n_prefix]
        if any(r.prefix_len != n_prefix or r.ids[:n_prefix] != prefix for r in rendered):
            return [self._scores(r) for r in rendered]                 # not one state: one by one
        batched = self.many_mode == "batched"
        s = n_prefix if batched else self._shared_len(n_prefix)
        rows = [self.renderer.yes, self.renderer.no]
        resp = self._request({"prefix": prefix[:s], "share_prefix": s > 0, "keep_prefix": s > 0,
                              "mode": "batched" if batched else "sequential",
                              "questions": [{"ids": r.ids[s:], "slots": r.slots, "rows": rows} for r in rendered]})
        self.last_timing = dict(resp.get("timing") or {}, shared_tokens=s, mode=resp.get("mode"))
        return [[float("nan") if (y is None or n is None) else y - n for y, n in res["scores"]]
                for res in resp["results"]]

    def close(self):
        if getattr(self, "proc", None) and self.proc.poll() is None:
            try:
                self.proc.stdin.write('{"cmd":"quit"}\n')
                self.proc.stdin.flush()
                self.proc.wait(timeout=10)
            except Exception:
                self.proc.kill()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def main(argv=None):
    ap = base_arg_parser(f"{MODEL_NAME}: typed decisions with llama.cpp (GGUF)")
    ap.add_argument("--quant", default="F16", choices=sorted(GGUF_FILES))
    ap.add_argument("--gguf", help="explicit GGUF path (overrides --quant)")
    ap.add_argument("--jev-score", help="path to the jev-score binary (default: $JEV_SCORE_BIN, ./build/jev-score)")
    ap.add_argument("--ngl", type=int, default=999, help="layers offloaded to the GPU")
    ap.add_argument("--threads", type=int)
    ap.add_argument("--no-split-options", action="store_true",
                    help="raise InputBudgetError instead of scoring an over-budget choice question in option chunks")
    args = ap.parse_args(argv)
    engine = JevStyleDecisionGGUF(args.model_dir, quant=args.quant, gguf=args.gguf, binary=args.jev_score,
                                  category=args.category, head_max=args.head_max, max_len=args.max_len,
                                  n_gpu_layers=args.ngl, threads=args.threads, verify=args.verify,
                                  split_options=not args.no_split_options)
    try:
        return run_cli(args, engine)
    finally:
        engine.close()


if __name__ == "__main__":
    raise SystemExit(main())

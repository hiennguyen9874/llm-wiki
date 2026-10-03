#!/usr/bin/env python
"""Build the openjev v2 training mixture: hard NLI + long documents + image premises + agentic traces.

Every adapter emits rows in ONE schema, with labels already in our space (0=contradiction, 1=entailment, 2=neutral):

    {"premise": str, "hypothesis": str, "label": int, "source": str, "image": str}

`image` is "" for text rows, else a path relative to the mixture dir. When an image is present the premise carries the
literal marker `<<IMG>>` at the position where the `<|vision_start|><|image_pad|>*n<|vision_end|>` block must go
(train.py substitutes it, because only the tokenizer knows the real token count).

Subcommands (each writes parts/<name>.jsonl incrementally, so a crash never loses finished work):

    python data_mix.py images  --out /mnt/nli_mix --n-rows 120000     # VQAv2 stream -> jpegs + claims
    python data_mix.py text    --out /mnt/nli_mix                     # SNLI/MNLI/ANLI/WANLI/FEVER/... + haystack
    python data_mix.py agentic --out /mnt/nli_mix                     # xlam / AgentTraj-L / AgentInstruct / When2Call / synth
    python data_mix.py faith    --out /mnt/nli_mix                    # MiniCheck C2D/D2C + RAGTruth train (sentence level)
    python data_mix.py ifollow  --out /mnt/nli_mix                    # ifeval-like responses, labels from the IFEval checker
    python data_mix.py bullshit --out /mnt/nli_mix                    # FalseQA + synthetic category-error questions
    python data_mix.py build   --out /mnt/nli_mix                     # merge, balance, leakage-check, save_to_disk
"""
import argparse
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict

OURS = {"contradiction": 0, "entailment": 1, "neutral": 2}
SYN = {
    "entailment": "entailment", "entails": "entailment", "entailed": "entailment", "supports": "entailment",
    "contradiction": "contradiction", "contradicts": "contradiction", "refutes": "contradiction",
    "neutral": "neutral", "not_entailment": "neutral", "not-entailed": "neutral", "not entailment": "neutral",
    "not enough info": "neutral", "not_enough_info": "neutral", "nei": "neutral",
}
IMG = "<<IMG>>"

# Datasets/splits that eval.py reports on. Never train on them, in any split (see plan: strict zero-shot).
BANNED = {
    "nyu-mll/multi_nli": {"validation_matched", "validation_mismatched"},
    "cais/mmlu": "*", "allenai/ai2_arc": "*", "allenai/winogrande": "*", "Rowan/hellaswag": "*",
    "openai/gsm8k": "*", "Idavidrein/gpqa": "*",
    # eval_extra.py sets (faithfulness / bullshit / instruction following)
    "lytang/LLM-AggreFact": "*", "PatronusAI/HaluBench": "*", "google/IFEval": "*",
    "wandb/RAGTruth-processed": {"test"}, "princeton-nlp/LLMBar": "*",
}


def norm_label(value, feature=None):
    """Resolve any source's label to our id, by NAME (never by position)."""
    name = value
    if isinstance(value, int) and feature is not None and hasattr(feature, "names"):
        name = feature.names[value]
    if not isinstance(name, str):
        raise ValueError(f"cannot resolve label {value!r} (feature={feature})")
    key = SYN.get(name.strip().lower())
    if key is None:
        raise ValueError(f"unknown label name {name!r}")
    return OURS[key]


def check_not_banned(repo, split):
    banned = BANNED.get(repo)
    if banned == "*" or (banned and split in banned):
        raise RuntimeError(f"LEAKAGE: {repo}:{split} is an eval set and must never be used for training")


class Part:
    """Incremental jsonl writer; a teardown crash keeps everything already written."""

    def __init__(self, out, name):
        os.makedirs(os.path.join(out, "parts"), exist_ok=True)
        self.path = os.path.join(out, "parts", f"{name}.jsonl")
        self.f = open(self.path, "w")
        self.n = 0
        self.by_label = Counter()

    def add(self, premise, hypothesis, label, source, image=""):
        premise, hypothesis = premise.strip(), hypothesis.strip()
        if not premise or not hypothesis:
            return
        self.f.write(json.dumps({"premise": premise, "hypothesis": hypothesis, "label": int(label),
                                 "source": source, "image": image}, ensure_ascii=False) + "\n")
        self.n += 1
        self.by_label[int(label)] += 1
        if self.n % 20000 == 0:
            self.f.flush()
            print(f"  {os.path.basename(self.path)}: {self.n} rows", flush=True)

    def close(self):
        self.f.close()
        print(f"[part] {os.path.basename(self.path)}: {self.n} rows, labels {dict(self.by_label)}", flush=True)


# --------------------------------------------------------------------------------------- text NLI
def take(ds, n, seed):
    if n and len(ds) > n:
        ds = ds.shuffle(seed=seed).select(range(n))
    return ds


def build_text(args):
    from datasets import concatenate_datasets, get_dataset_config_names, load_dataset
    seed = args.seed
    p = Part(args.out, "text")
    pool = []  # filler sentences for the haystack block
    pairs_for_haystack = []

    def emit(ds, src, prem_col="premise", hyp_col="hypothesis", lab_col="label", keep_for_haystack=False):
        feat = ds.features.get(lab_col)
        kept = 0
        for ex in ds:
            v = ex[lab_col]
            if isinstance(v, int) and v < 0:
                continue
            try:
                y = norm_label(v, feat)
            except ValueError:
                continue
            pr, hy = ex[prem_col], ex[hyp_col]
            if not pr or not hy:
                continue
            p.add(pr, hy, y, src)
            kept += 1
            if len(pool) < 200_000:
                pool.append(pr.strip())
            if keep_for_haystack and len(pairs_for_haystack) < 250_000:
                pairs_for_haystack.append((pr.strip(), hy.strip(), y))
        print(f"[text] {src}: {kept}", flush=True)

    # core NLI
    for repo, n in [("stanfordnlp/snli", args.n_snli), ("nyu-mll/multi_nli", args.n_mnli)]:
        check_not_banned(repo, "train")
        emit(take(load_dataset(repo, split="train"), n, seed), repo.split("/")[-1], keep_for_haystack=True)

    # adversarial
    anli = load_dataset("facebook/anli")
    emit(concatenate_datasets([anli[f"train_r{i}"] for i in (1, 2, 3)]), "anli", keep_for_haystack=True)

    wanli = load_dataset("alisawuffles/WANLI", split="train")
    emit(wanli, "wanli", lab_col="gold")

    # evidence-grounded
    fever = take(load_dataset("pietrolesci/nli_fever", split="train"), args.n_fever, seed)
    emit(fever, "nli_fever", keep_for_haystack=True)

    emit(load_dataset("tasksource/lingnli", split="train"), "lingnli")
    emit(load_dataset("tasksource/ConTRoL-nli", split="train"), "control")

    sci = load_dataset("allenai/scitail", "snli_format", split="train")
    emit(sci, "scitail", prem_col="sentence1", hyp_col="sentence2", lab_col="gold_label")

    qnli = take(load_dataset("nyu-mll/glue", "qnli", split="train"), args.n_qnli, seed)
    emit(qnli, "qnli", prem_col="sentence", hyp_col="question")

    for cfg in get_dataset_config_names("tasksource/babi_nli"):
        try:
            emit(load_dataset("tasksource/babi_nli", cfg, split="train"), f"babi:{cfg}")
        except Exception as e:  # noqa: BLE001
            print(f"[text] babi:{cfg} skipped: {type(e).__name__}", flush=True)

    p.close()

    # ------------------------------------------------------------------ haystack (long-document entailment)
    rng = random.Random(seed)
    h = Part(args.out, "haystack")
    rng.shuffle(pairs_for_haystack)
    for prem, hyp, y in pairs_for_haystack[: args.n_haystack]:
        filler = rng.sample(pool, rng.randint(15, 40))
        drop = rng.random() < 0.30  # 30%: the evidence is NOT in the document -> "not stated" == neutral
        if drop:
            doc, label = filler, OURS["neutral"]
        else:
            pos = rng.randrange(len(filler) + 1)
            doc, label = filler[:pos] + [prem] + filler[pos:], y
        h.add("\n\n".join(doc), hyp, label, "haystack_drop" if drop else "haystack")
    h.close()


# --------------------------------------------------------------------------------------- images (VQAv2)
NUM_WORDS = {"0": "no", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five"}
LEAD_INS = ["A photograph:", "A photo:", "A picture:", "An image:", "A photograph of a scene:"]
LEAD_PIX = "A photograph, 320 pixels wide, the centre at x = 160:"


def q_to_statement(q, a, atype):
    """VQA question + answer -> a declarative claim. Returns (statement, flip_ok) where flip_ok means
    a yes/no question whose 'no' answer turns the same statement into a contradiction."""
    q = q.strip().rstrip("?").strip()
    a = a.strip().lower()
    ql = q.lower()
    m = re.match(r"^what colou?r (?:is|are) (?:the )?(.+)$", ql)
    if m:
        return f"The {m.group(1)} is {a}.", False
    m = re.match(r"^how many (.+)$", ql)
    if m:
        noun = m.group(1)
        noun = re.sub(r"\b(are|is|can|do|does|there|in|on|the|this|that|photo|picture|image)\b.*$", "", noun).strip()
        if noun:
            return f"There are {NUM_WORDS.get(a, a)} {noun} in the image.", False
    if atype == "yes/no":
        m = re.match(r"^(is|are|was|were|does|do|did|can|has|have|will)\s+(.+)$", ql)
        if m:
            aux, rest = m.group(1), m.group(2)
            if aux in ("is", "are", "was", "were"):
                parts = rest.split(" ", 1)
                if len(parts) == 2:
                    subj, tail = parts
                    return f"{subj.capitalize()} {aux} {tail}.", True
            else:
                return f"{rest.capitalize()} ({aux}).".replace(" ().", "."), True
    if atype == "yes/no":
        return f'The answer to "{q}?" is {a}.', False
    return f'In this image, the answer to "{q}?" is {a}.', False


def spatial_claims(dets, W, H, rng):
    """Templated claims from DETA detections, in the coordinates of the RESIZED 320x240 frame.
    Returns a list of (hypothesis, label)."""
    out = []
    if not dets:
        return out
    sx, sy = 320.0 / max(W, 1), 240.0 / max(H, 1)
    boxes = []
    for d in dets:
        b = d.get("box")
        lab = (d.get("label") or "").strip().lower()
        if not b or len(b) != 4 or not lab:
            continue
        boxes.append((lab, [b[0] * sx, b[1] * sy, b[2] * sx, b[3] * sy]))
    if not boxes:
        return out
    present = Counter(l for l, _ in boxes)
    labels = sorted(present)

    def third(cx):
        return "left" if cx < 320 / 3 else ("right" if cx > 2 * 320 / 3 else "middle")

    lab, box = rng.choice(boxes)
    cx = (box[0] + box[2]) / 2
    t = third(cx)
    out.append((f"There is a {lab} in the {t} third of the image.", OURS["entailment"]))
    wrong = rng.choice([x for x in ("left", "middle", "right") if x != t])
    out.append((f"There is a {lab} in the {wrong} third of the image.", OURS["contradiction"]))
    # pixel-coordinate form: mirrors the `pixels` variant of doom_vision.py, the best one on Doom
    if cx < 110:
        out.append((f"The {lab} is at x < 110, on the left.", OURS["entailment"]))
        out.append((f"The {lab} is at x > 210, on the right.", OURS["contradiction"]))
    elif cx > 210:
        out.append((f"The {lab} is at x > 210, on the right.", OURS["entailment"]))
        out.append((f"The {lab} is at x < 110, on the left.", OURS["contradiction"]))
    else:
        out.append((f"The {lab} is near the centre, around x = 160.", OURS["entailment"]))
        out.append((f"The {lab} is at x < 110, on the left.", OURS["contradiction"]))
    # counting
    n = present[lab]
    out.append((f"There are {NUM_WORDS.get(str(n), n)} {lab}s in the image.", OURS["entailment"]))
    out.append((f"There are {NUM_WORDS.get(str(n + 2), n + 2)} {lab}s in the image.", OURS["contradiction"]))
    # relative position
    if len(labels) >= 2:
        a, b = rng.sample(labels, 2)
        ca = sum((bx[0] + bx[2]) / 2 for l, bx in boxes if l == a) / present[a]
        cb = sum((bx[0] + bx[2]) / 2 for l, bx in boxes if l == b) / present[b]
        rel, anti = ("left", "right") if ca < cb else ("right", "left")
        out.append((f"The {a} is to the {rel} of the {b}.", OURS["entailment"]))
        out.append((f"The {a} is to the {anti} of the {b}.", OURS["contradiction"]))
    # absent object -> contradiction; unverifiable attribute -> neutral
    for cand in ("giraffe", "helicopter", "piano", "traffic light", "zebra"):
        if cand not in present:
            out.append((f"There is a {cand} in the image.", OURS["contradiction"]))
            break
    out.append((f"The {lab} was bought last week.", OURS["neutral"]))
    return out


def build_images(args):
    from datasets import load_dataset
    from PIL import Image

    rng = random.Random(args.seed)
    img_dir = os.path.join(args.out, "images")
    os.makedirs(img_dir, exist_ok=True)
    p = Part(args.out, args.part_name)
    ds = load_dataset(args.vqa_repo, split=args.vqa_split, streaming=True)
    ds = ds.shuffle(seed=args.seed, buffer_size=10_000)
    seen_images, seen_answers, n_rows = {}, defaultdict(list), 0

    for ex in ds:
        if n_rows >= args.n_rows or p.n >= args.n_claims:
            break
        n_rows += 1
        try:
            iid = str(ex["id_image"])
            rel = f"images/{iid}.jpg"
            if iid not in seen_images:
                if len(seen_images) >= args.max_images:
                    continue
                im = ex["image"].convert("RGB")
                seen_images[iid] = im.size
                im.resize((320, 240)).save(os.path.join(img_dir, f"{iid}.jpg"), quality=88)
            W, H = seen_images[iid]

            q, a = ex["question"], (ex["multiple_choice_answer"] or "").strip()
            atype = ex.get("answer_type") or ""
            if not a:
                continue
            answers = [x["answer"] if isinstance(x, dict) else x for x in (ex.get("answers") or [])]
            agree = sum(1 for x in answers if str(x).strip().lower() == a.lower())
            stmt, flip_ok = q_to_statement(q, a, atype)
            lead = rng.choice(LEAD_INS)

            if agree and agree < 6:                      # annotators disagree -> not determinable from the image
                p.add(f"{lead} {IMG}", stmt, OURS["neutral"], "vqa_disagree", rel)
            elif atype == "yes/no" and flip_ok:
                p.add(f"{lead} {IMG}", stmt, OURS["entailment"] if a == "yes" else OURS["contradiction"], "vqa_yesno", rel)
            else:
                p.add(f"{lead} {IMG}", stmt, OURS["entailment"], "vqa_answer", rel)
                pool = seen_answers[atype]
                if pool and rng.random() < args.answer_neg_prob:
                    wrong = rng.choice(pool)
                    if wrong.lower() != a.lower():
                        bad, _ = q_to_statement(q, wrong, atype)
                        p.add(f"{lead} {IMG}", bad, OURS["contradiction"], "vqa_answer_neg", rel)
                if len(pool) < 5000:
                    pool.append(a)

            dets = ex.get("DETA_detections_deta_swin_large_o365_coco_classes") or []
            claims = spatial_claims(dets, W, H, rng)
            rng.shuffle(claims)
            for hyp, y in claims[: args.spatial_per_image]:
                p.add(f"{LEAD_PIX} {IMG}", hyp, y, "vqa_spatial", rel)
        except Exception as e:  # noqa: BLE001
            print(f"[vqa] row skipped: {type(e).__name__}: {str(e)[:80]}", flush=True)
    p.close()
    print(f"[vqa] read {n_rows} rows, {len(seen_images)} images saved", flush=True)
    sys.stdout.flush()
    os._exit(0)  # datasets 5.0 segfaults tearing down the parquet stream generator


# --------------------------------------------------------------------------------------- agentic
def _tools_str(tools, limit=1200):
    s = tools if isinstance(tools, str) else json.dumps(tools, ensure_ascii=False)
    return s[:limit]


def build_agentic(args):
    from datasets import load_dataset
    rng = random.Random(args.seed)
    p = Part(args.out, "agentic")

    # ---- xlam function calling (gated upstream; download it yourself to data/xlam.jsonl)
    xlam_path = os.path.join(args.data_dir, "xlam.jsonl")
    if os.path.exists(xlam_path):
        rows = [json.loads(l) for l in open(xlam_path)]
        alt_names = []
        for r in rows:
            try:
                calls = json.loads(r["answers"]) if isinstance(r["answers"], str) else r["answers"]
            except Exception:  # noqa: BLE001
                continue
            if not calls:
                continue
            for c in calls[:2]:
                alt_names.append(c.get("name", ""))
        for r in rows:
            try:
                calls = json.loads(r["answers"]) if isinstance(r["answers"], str) else r["answers"]
            except Exception:  # noqa: BLE001
                continue
            if not calls:
                continue
            call = calls[0]
            name, argd = call.get("name", ""), call.get("arguments", {}) or {}
            if not name:
                continue
            prem = f"User request: {r['query'].strip()}\nAvailable tools: {_tools_str(r.get('tools'))}"
            fmt = lambda n, d: f"The correct call is {n}(" + ", ".join(f"{k}={json.dumps(v, ensure_ascii=False)}" for k, v in d.items()) + ")."
            p.add(prem, fmt(name, argd), OURS["entailment"], "xlam", "")
            bad = rng.choice(alt_names)
            if bad and bad != name:
                p.add(prem, fmt(bad, argd), OURS["contradiction"], "xlam_neg_name", "")
            if argd:
                k = rng.choice(list(argd))
                mut = dict(argd)
                v = mut[k]
                mut[k] = (v + 7) if isinstance(v, (int, float)) and not isinstance(v, bool) else (str(v) + "_x")
                p.add(prem, fmt(name, mut), OURS["contradiction"], "xlam_neg_arg", "")
                drop = {kk: vv for kk, vv in argd.items() if kk != k}
                p.add(prem, f"The value of `{k}` cannot be determined from the user request.",
                      OURS["neutral"] if len(argd) > 1 else OURS["contradiction"], "xlam_underspec", "")
                if drop:
                    p.add(prem, fmt(name, drop), OURS["contradiction"], "xlam_neg_missing", "")
    else:
        print(f"[agentic] {xlam_path} missing -> xlam skipped", flush=True)

    # ---- trajectory datasets: premise = task + last observation, hypothesis = next action
    def from_conversations(repo, cfgs, src, cap):
        n = 0
        for cfg in cfgs:
            try:
                ds = load_dataset(repo, split=cfg) if cfg else load_dataset(repo, split="train")
            except Exception as e:  # noqa: BLE001
                print(f"[agentic] {repo}:{cfg} skipped: {type(e).__name__}", flush=True)
                continue
            all_actions = []
            convs = []
            for ex in ds:
                turns = ex.get("conversations") or []
                msgs = [(t.get("from") or t.get("role") or "", (t.get("value") or t.get("content") or "").strip()) for t in turns]
                acts = [m for who, m in msgs if who in ("gpt", "assistant") and m]
                if len(msgs) >= 3 and acts:
                    convs.append(msgs)
                    all_actions.extend(acts)
            for msgs in convs:
                if n >= cap:
                    break
                idxs = [i for i, (who, _) in enumerate(msgs) if who in ("gpt", "assistant") and i > 0]
                for i in rng.sample(idxs, min(2, len(idxs))):
                    if n >= cap:
                        break
                    ctx = "\n".join(m for _, m in msgs[max(0, i - 2):i])[-1500:]
                    act = msgs[i][1][:400]
                    p.add(f"Agent task and last observations:\n{ctx}", f"The next action is: {act}", OURS["entailment"], src, "")
                    other = rng.choice(all_actions)[:400]
                    if other != act:
                        p.add(f"Agent task and last observations:\n{ctx}", f"The next action is: {other}", OURS["contradiction"], f"{src}_neg", "")
                    n += 2
        print(f"[agentic] {src}: {n}", flush=True)

    from_conversations("AgentGym/AgentTraj-L", [None], "agenttraj", args.n_traj)
    from_conversations("THUDM/AgentInstruct", ["os", "db", "alfworld", "webshop", "kg", "mind2web"], "agentinstruct", 8000)

    # ---- When2Call: call a tool / ask a clarifying question / answer directly
    try:
        w2c = load_dataset("nvidia/When2Call", split="mcq")
        for ex in w2c:
            q = (ex.get("question") or "").strip()
            if not q:
                continue
            prem = f"{q[:2500]}\nAvailable tools: {_tools_str(ex.get('tools'))}"
            correct = str(ex.get("correct_answer", "")).strip()
            answers = ex.get("answers")
            opts = answers if isinstance(answers, list) else [answers]
            for o in opts:
                o = str(o).strip()
                if not o:
                    continue
                y = OURS["entailment"] if o == correct else OURS["contradiction"]
                p.add(prem, f"The assistant should: {o[:300]}", y, "when2call", "")
            if ex.get("held_out_param"):
                p.add(prem, f"The value of `{ex['held_out_param']}` is stated in the user request.",
                      OURS["contradiction"], "when2call_param", "")
    except Exception as e:  # noqa: BLE001
        print(f"[agentic] When2Call skipped: {type(e).__name__}: {str(e)[:80]}", flush=True)

    # ---- synthetic state predicates (the Minecraft-scaffold format), fully generated here
    if not args.no_synth_state:
        items = ["oak log", "oak planks", "stick", "crafting table", "cobblestone", "raw iron", "iron ingot",
                 "furnace", "coal", "wooden pickaxe", "stone pickaxe", "iron pickaxe", "bucket", "torch", "apple"]
        places = ["a crafting table", "a furnace", "a chest", "water", "lava"]
        for _ in range(args.n_synth):
            inv = {it: rng.randint(1, 40) for it in rng.sample(items, rng.randint(2, 7))}
            near = rng.sample(places, rng.randint(0, 2))
            health = rng.randint(1, 20)
            lines = [f"{k}: {v}" for k, v in inv.items()] or ["(empty)"]
            prem = ("Agent state.\nInventory:\n" + "\n".join(lines)
                    + f"\nNearby: {', '.join(near) if near else 'nothing'}\nHealth: {health}/20")
            kind = rng.randrange(4)
            if kind == 0:
                it = rng.choice(items)
                have, thr = inv.get(it, 0), rng.randint(1, 20)
                p.add(prem, f"The number of {it} in the inventory is {thr} or more.",
                      OURS["entailment"] if have >= thr else OURS["contradiction"], "synth_count", "")
            elif kind == 1:
                it = rng.choice(items)
                p.add(prem, f"There are no {it} in the inventory.",
                      OURS["entailment"] if inv.get(it, 0) == 0 else OURS["contradiction"], "synth_absent", "")
            elif kind == 2:
                pl = rng.choice(places)
                p.add(prem, f"The agent is near {pl}.",
                      OURS["entailment"] if pl in near else OURS["contradiction"], "synth_near", "")
            else:
                p.add(prem, rng.choice([f"The agent has been playing for {rng.randint(2, 90)} minutes.",
                                        "The agent intends to build a shelter next.",
                                        f"The {rng.choice(items)} was crafted by another player."]),
                      OURS["neutral"], "synth_unknown", "")
    p.close()


# --------------------------------------------------------------------------------------- faithfulness
SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")
CONFLICT = {"evident conflict", "subtle conflict"}  # RAGTruth span types that contradict the context; the rest are baseless


def split_sents(text):
    """Sentences with their character offsets in `text`."""
    out, pos = [], 0
    for s in SENT_RE.split(text):
        start = text.find(s, pos)
        if start < 0:
            start = pos
        out.append((s, start, start + len(s)))
        pos = start + len(s)
    return [(s.strip(), a, b) for s, a, b in out if len(s.strip()) > 3]


def build_faith(args):
    """Grounded-claim rows: premise = source document, hypothesis = a claim / generated sentence.
    Unsupported but not contradicted -> neutral (the same "not stated" convention as haystack_drop)."""
    from datasets import load_dataset
    rng = random.Random(args.seed)
    p = Part(args.out, "faith")

    # MiniCheck synthetic data (claim-to-doc and doc-to-claim): 1 = supported, 0 = unsupported
    for split in ("c2d", "d2c"):
        for ex in load_dataset("lytang/C2D-and-D2C-MiniCheck", split=split):
            y = OURS["entailment"] if str(ex["label"]).strip() == "1" else OURS["neutral"]
            p.add(ex["doc"], ex["claim"], y, f"minicheck_{split}")

    # RAGTruth train split only (the test split is inside LLM-AggreFact / eval_extra.py)
    check_not_banned("wandb/RAGTruth-processed", "train")
    rt = load_dataset("wandb/RAGTruth-processed", split="train")
    n_resp = 0
    for ex in rt:
        try:
            spans = json.loads(ex["hallucination_labels"]) if isinstance(ex["hallucination_labels"], str) else ex["hallucination_labels"]
        except Exception:  # noqa: BLE001
            continue
        out = (ex["output"] or "").strip()
        ctx = (ex["context"] or "").strip()
        if not out or not ctx:
            continue
        prem = f"{(ex['query'] or '').strip()}\n\n{ctx}".strip()
        n_resp += 1
        sents = split_sents(out)
        rng.shuffle(sents)
        for s, a, b in sents[: args.faith_sents_per_resp]:
            hit = [sp for sp in spans or [] if sp.get("start", 0) < b and sp.get("end", 0) > a]
            if not hit:
                y = OURS["entailment"]
            elif any((sp.get("label_type") or "").lower() in CONFLICT for sp in hit):
                y = OURS["contradiction"]
            else:
                y = OURS["neutral"]
            p.add(prem, s, y, f"ragtruth_{(ex['task_type'] or 'x').lower()}")
        # response level: the worst span decides
        types = {(sp.get("label_type") or "").lower() for sp in spans or []}
        y = OURS["entailment"] if not types else (OURS["contradiction"] if types & CONFLICT else OURS["neutral"])
        p.add(prem, out, y, "ragtruth_resp")
    print(f"[faith] ragtruth responses: {n_resp}", flush=True)
    p.close()


# --------------------------------------------------------------------------------------- instruction following
IF_PERTURB = {
    "upper": lambda t, r: t.upper(),
    "lower": lambda t, r: t.lower(),
    "no_commas": lambda t, r: t.replace(",", ""),
    "add_commas": lambda t, r: re.sub(r"(\w) (\w)", lambda m: m.group(1) + ", " + m.group(2) if r.random() < 0.05 else m.group(0), t),
    "truncate": lambda t, r: t[: max(40, int(len(t) * r.uniform(0.2, 0.5)))],
    "double": lambda t, r: t + "\n\n" + t,
    "strip_md": lambda t, r: re.sub(r"^\s*[\*\-]\s+", "", re.sub(r"\*([^*\n]+)\*", r"\1", t), flags=re.M),
    "drop_last_par": lambda t, r: "\n\n".join(t.split("\n\n")[:-1]) or t[: len(t) // 2],
    "unquote": lambda t, r: t.strip().strip('"'),
    "quote": lambda t, r: f'"{t.strip()}"',
    "sections": lambda t, r: re.sub(r"(SECTION|Section|PARAGRAPH|Paragraph|PART|Part)\s*\d+", "", t),
    "json_wrap": lambda t, r: json.dumps({"response": t}),
}
IF_OVERALL = ["The response follows all of the instructions.", "The response satisfies every constraint in the request.",
              "Every requirement stated in the prompt is met by the response."]


def if_checker():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ifeval_lib import instructions_registry
    from ifeval_lib.instructions_util import download_nltk_resources
    download_nltk_resources()
    return instructions_registry.INSTRUCTION_DICT


def if_check(reg, ids, kwargs_list, prompt, response):
    """[(description, followed)] per instruction, or None if any instruction cannot be rebuilt exactly."""
    out = []
    for iid, kw in zip(ids, kwargs_list):
        cls = reg.get(iid)
        if cls is None:
            return None
        inst = cls(iid)
        kw = {k: v for k, v in (kw or {}).items() if v is not None}
        need = inst.get_instruction_args_keys() or []
        kw = {k: v for k, v in kw.items() if k in need}
        if set(need) - set(kw) - {"prompt"}:
            return None  # build_description would randomise the missing args -> label would be wrong
        try:
            desc = inst.build_description(**kw)
            args = inst.get_instruction_args()
            if args and "prompt" in args:  # same as lm_eval's ifeval utils
                desc = inst.build_description(prompt=prompt)
        except Exception:  # noqa: BLE001
            return None
        try:
            ok = bool(response.strip()) and bool(inst.check_following(response))
        except Exception:  # noqa: BLE001
            return None
        out.append((desc, ok))
    return out


def build_ifollow(args):
    """Premise = request + response; hypotheses = each verifiable constraint (IFEval phrasing) or "follows all".
    Every label comes from the IFEval checker run on the exact text, including after the perturbations."""
    from datasets import load_dataset
    rng = random.Random(args.seed)
    reg = if_checker()
    p = Part(args.out, "ifollow")
    banned = {ex["prompt"].strip() for ex in load_dataset("google/IFEval", split="train")}
    ds = load_dataset("argilla/ifeval-like-data", split="train").shuffle(seed=args.seed)
    n_used, n_skip = 0, 0
    for ex in ds:
        if n_used >= args.n_ifollow:
            break
        prompt, resp = (ex["instruction"] or "").strip(), (ex["response"] or "").strip()
        if not prompt or not resp or prompt in banned:
            n_skip += 1
            continue
        try:
            ids = ex["instruction_id_list"]
            ids = json.loads(ids.replace("'", '"')) if isinstance(ids, str) else list(ids)
            kw = ex["kwargs"]
            kw = json.loads(kw) if isinstance(kw, str) else dict(kw)
        except Exception:  # noqa: BLE001
            n_skip += 1
            continue
        # argilla stores ONE merged kwargs dict; give each instruction the keys it accepts (if_check filters)
        variants = [("orig", resp)]
        for name in rng.sample(list(IF_PERTURB), 2):
            variants.append((name, IF_PERTURB[name](resp, rng)))
        rows = []
        for vname, text in variants:
            res = if_check(reg, ids, [kw] * len(ids), prompt, text)
            if res is None:
                break
            rows.append((vname, text, res))
        if not rows or len(rows) < len(variants):
            n_skip += 1
            continue
        n_used += 1
        for vname, text, res in rows:
            prem = f"Request:\n{prompt}\n\nResponse:\n{text[:6000]}"
            src = "ifollow" if vname == "orig" else "ifollow_pert"
            for desc, ok in rng.sample(res, min(2, len(res))):
                p.add(prem, f"The response satisfies this requirement: {desc}",
                      OURS["entailment"] if ok else OURS["contradiction"], src)
            p.add(prem, rng.choice(IF_OVERALL),
                  OURS["entailment"] if all(ok for _, ok in res) else OURS["contradiction"], f"{src}_all")
    print(f"[ifollow] used {n_used}, skipped {n_skip}", flush=True)
    p.close()


# --------------------------------------------------------------------------------------- bullshit / false premises
BS_DOMAINS = {
    "finance": (["default risk", "yield curve", "solvency ratio", "credit rating", "liquidity coverage", "amortization schedule", "hedge ratio"],
                ["bond portfolio", "loan book", "corporate balance sheet", "treasury holdings", "credit facility"]),
    "software": (["test coverage", "memory footprint", "cyclomatic complexity", "build time", "API versioning policy", "stack trace depth"],
                 ["backend service", "mobile app", "CI pipeline", "microservice", "code base"]),
    "marketing": (["click-through rate", "brand awareness", "customer acquisition cost", "conversion funnel", "share of voice"],
                  ["email campaign", "ad campaign", "landing page", "social media strategy"]),
    "cooking": (["Maillard browning", "gluten development", "smoke point", "brine concentration", "proofing time"],
                ["sourdough loaf", "steak", "frying oil", "pickle batch"]),
    "biology": (["mutation rate", "metabolic rate", "gene expression level", "doubling time"],
                ["bacterial culture", "lab mouse colony", "cell line"]),
    "music": (["tempo", "key signature", "reverb tail", "harmonic progression"],
              ["song", "string quartet", "mix bus", "jazz standard"]),
    "hr": (["attrition rate", "employee engagement score", "time-to-hire", "onboarding completion rate"],
           ["engineering team", "sales department", "recruiting pipeline"]),
    "physics": (["thermal conductivity", "tensile strength", "resonant frequency", "specific heat capacity"],
                ["steel beam", "copper wire", "glass panel"]),
    "law": (["statute of limitations", "burden of proof", "jurisdiction", "indemnification clause"],
            ["lawsuit", "vendor contract", "patent dispute"]),
    "gardening": (["soil pH", "germination rate", "pruning schedule", "nitrogen requirement"],
                  ["tomato plant", "rose bush", "lawn"]),
    "logistics": (["on-time delivery rate", "warehouse throughput", "last-mile cost", "inventory turnover"],
                  ["distribution network", "fulfillment center", "shipping fleet"]),
}
# domain pairs whose crossings are often sensible (CAC of a mobile app, ...) -> never used as nonsense
BS_COMPATIBLE = {frozenset(x) for x in [("software", "marketing"), ("marketing", "hr"), ("software", "logistics"),
                                         ("finance", "logistics"), ("cooking", "gardening"), ("biology", "gardening")]}
BS_TEMPLATES = ["How should we measure the {p} of our {o}?", "What's a good benchmark for the {p} of a {o}?",
                "How can I improve the {p} of my {o}?", "The {p} of our {o} dropped last quarter. What's the likely cause?",
                "Which tools can track the {p} of a {o}?", "Should the {p} of our {o} be reviewed monthly or quarterly?",
                "What is a typical {p} for a {o}, and how do we compare?", "Who on the team should own the {p} of the {o}?"]
BS_Q_HYPS = [("The question makes sense and rests on valid assumptions.", False),
             ("The question is coherent: what it asks about actually exists and can be answered.", False),
             ("The question contains a false or nonsensical premise.", True),
             ("The question applies a concept to something it cannot meaningfully apply to.", True)]
BS_R_HYPS = ["The answer points out that the question's premise is false or nonsensical.",
             "The response pushes back on the question instead of accepting its premise."]


def build_bullshit(args):
    """Question-level rows (premise = question; is its premise valid?) and response-level rows
    (premise = question + answer; does the answer push back?). Held-out eval: BullshitBench (eval_extra.py)."""
    import csv
    import io
    import urllib.request
    rng = random.Random(args.seed)
    p = Part(args.out, "bullshit")

    def q_rows(q, is_bs, src):
        for hyp, positive_if_bs in rng.sample(BS_Q_HYPS, 2):
            ent = (is_bs == positive_if_bs)
            p.add(f"Question: {q}", hyp, OURS["entailment"] if ent else OURS["contradiction"], src)

    # FalseQA (thunlp): train + valid; its test split stays out as an in-domain sanity eval
    base = "https://raw.githubusercontent.com/thunlp/FalseQA/main/dataset/"
    for split in ("train", "valid"):
        text = urllib.request.urlopen(base + f"{split}.csv", timeout=60).read().decode("utf-8")
        for row in csv.DictReader(io.StringIO(text)):
            q, a, lab = row["question"].strip(), row["answer"].strip(), row["label"].strip()
            if not q:
                continue
            is_bs = lab == "1"
            q_rows(q, is_bs, "falseqa")
            if a:  # false-premise answers are rebuttals, the others answer normally
                p.add(f"Question: {q}\n\nAnswer: {a}", rng.choice(BS_R_HYPS),
                      OURS["entailment"] if is_bs else OURS["contradiction"], "falseqa_resp")

    # synthetic category errors: a property from one domain applied to an object from an unrelated one
    doms = list(BS_DOMAINS)
    seen = set()
    for _ in range(args.n_bs_synth * 3):
        if len(seen) >= args.n_bs_synth:
            break
        da = rng.choice(doms)
        bs = rng.random() < 0.5
        db = rng.choice([d for d in doms if d != da and frozenset((da, d)) not in BS_COMPATIBLE]) if bs else da
        q = rng.choice(BS_TEMPLATES).format(p=rng.choice(BS_DOMAINS[da][0]), o=rng.choice(BS_DOMAINS[db][1]))
        if q in seen:
            continue
        seen.add(q)
        q_rows(q, bs, "bs_synth")
    p.close()


# --------------------------------------------------------------------------------------- typed decisions (jev format)
JEVBENCH = "https://raw.githubusercontent.com/fstandhartinger/jevbench/main/datasets/public/"
JEV_TEMPLATES = ['The answer to "{instr}" is {label}: {crit}',
                 'Decision for "{instr}": {label} — {crit}']
# (condition, fact when it holds, fact when it is violated); {d} is the limit, {ok}/{late} are day counts on each side
POLICY_RULES = [("the request is made within {d} days of purchase", "the purchase was {late} days ago"),
                ("a receipt is provided", "no receipt was provided"),
                ("the item is unused and in its original packaging", "the item has been used"),
                ("the account is in good standing", "the account is {n} days overdue"),
                ("a manager has approved the exception", "no manager approval is on file")]
SEVERITY = ["No function impaired; cosmetic only",
            "One user or a nonessential function impaired, with a workaround",
            "Many users blocked from a core function, no data loss",
            "Confirmed irreversible data loss or physical harm"]
SEVERITY_FACTS = [["A tooltip is misaligned on one settings page.", "The logo renders slightly blurred in the footer."],
                  ["One analyst cannot export a report; copying the table by hand works.",
                   "A single user's avatar upload fails; everything else works."],
                  ["Checkout is down for all customers in the EU; no records were lost.",
                   "Every user is blocked from logging in; data is intact."],
                  ["Two weeks of customer records were deleted and no backup exists.",
                   "A hydraulic press moved while an operator's hand was inside; the operator was injured."]]


def jev_rows(p, state, instr, labels, crits, gold, src, rng, n_neg=3):
    """One row per option, in the wire form eval_jevbench.py uses: gold option entails, wrong options contradict."""
    tmpl = rng.choice(JEV_TEMPLATES)
    wrong = [l for l in labels if l != gold]
    rng.shuffle(wrong)
    for lab in [gold] + wrong[:n_neg]:
        hyp = tmpl.format(instr=instr, label=lab, crit=crits.get(lab, lab))
        p.add(state, hyp, OURS["entailment"] if lab == gold else OURS["contradiction"], src)


def build_jevfmt(args):
    """Typed bounded decisions: the JevBench public items themselves plus the same shape built from other sources."""
    import urllib.request
    from datasets import load_dataset
    rng = random.Random(args.seed)
    p = Part(args.out, "jevfmt")

    # --- JevBench public items (easy / standard / hard). The user asked for these to be trained on: after this,
    # public-item JevBench numbers are no longer a clean measurement (the held-out tiers still are).
    if not args.no_jevbench:
        for name in ("easy", "original", "hard"):
            for line in urllib.request.urlopen(JEVBENCH + f"{name}.jsonl", timeout=60).read().decode().splitlines():
                if not line.strip():
                    continue
                t = json.loads(line)
                q, crit = t["question"], t["question"].get("criteria")
                state = t["state"] if isinstance(t["state"], str) else json.dumps(t["state"], ensure_ascii=False)
                if q["type"] == "noul":
                    crit = crit or {}
                    crits = {"yes": crit.get("true", "yes"), "no": crit.get("false", "no")}
                elif q["type"] == "score":
                    crits = {str(i): c for i, c in enumerate(crit)}
                else:
                    crits = {k: (v or k) for k, v in (crit or {}).items()}
                for _ in range(args.jevbench_repeat):
                    jev_rows(p, state, q["instructions"].strip(), list(crits), crits, str(t["expected"]),
                             f"jevbench_{name}", rng, n_neg=len(crits))

    # --- intent classification with an explicit label set (CLINC-150, Banking77)
    def intents(repo, cfg, text_col, n, src, lab_col="label"):
        ds = load_dataset(repo, cfg, split="train") if cfg else load_dataset(repo, split="train")
        names = getattr(ds.features[lab_col], "names", None)
        if not names:
            return
        pretty = {i: n_.replace("_", " ") for i, n_ in enumerate(names)}
        ds = ds.shuffle(seed=args.seed).select(range(min(n, len(ds))))
        for ex in ds:
            gold = pretty[ex[lab_col]]
            opts = rng.sample([v for k, v in pretty.items() if v != gold], min(5, len(pretty) - 1)) + [gold]
            rng.shuffle(opts)
            jev_rows(p, ex[text_col], "Which intent does the user's message express?", opts,
                     {o: f"The user's message is about: {o}" for o in opts}, gold, src, rng)

    intents("clinc/clinc_oos", "plus", "text", args.n_intent, "clinc_intent", lab_col="intent")
    intents("legacy-datasets/banking77", None, "text", args.n_intent, "banking77_intent")

    # --- tool selection from the xlam tool lists already downloaded for the agentic part
    xlam_path = os.path.join(args.data_dir, "xlam.jsonl")
    if os.path.exists(xlam_path):
        for i, line in enumerate(open(xlam_path)):
            if i >= args.n_tool:
                break
            r = json.loads(line)
            try:
                tools = r["tools"] if isinstance(r["tools"], list) else json.loads(r["tools"])
                calls = r["answers"] if isinstance(r["answers"], list) else json.loads(r["answers"])
            except Exception:  # noqa: BLE001
                continue
            if not tools or not calls:
                continue
            gold = calls[0].get("name", "")
            names = {t.get("name", ""): (t.get("description") or t.get("name", ""))[:200] for t in tools if t.get("name")}
            if gold not in names or len(names) < 2:
                continue
            jev_rows(p, f"User request: {r['query'].strip()}", "Which tool should be called to serve this request?",
                     list(names), names, gold, "xlam_tool", rng, n_neg=len(names))

    # --- policy yes/no and ordinal severity, generated here (the families JevBench calls policy / ordinal)
    for _ in range(args.n_policy):
        conds = rng.sample(POLICY_RULES, rng.randint(2, 4))
        broken = rng.random() < 0.5
        bad = rng.randrange(len(conds)) if broken else -1
        lines, facts = [], []
        for j, (cond, viol) in enumerate(conds):
            d, n = rng.randint(14, 90), rng.randint(5, 60)
            late, ok = d + rng.randint(1, 40), rng.randint(1, d)
            lines.append("- " + cond.format(d=d))
            if j == bad:
                facts.append(viol.format(late=late, n=n))
            elif "{d}" in cond:  # a satisfied deadline is stated as a day count too, so the model must compare numbers
                facts.append(f"the purchase was {ok} days ago")
            else:
                facts.append(cond)
        state = ("Policy: the action is permitted only if all of the following hold:\n" + "\n".join(lines)
                 + "\n\nCase facts:\n" + "\n".join("- " + f for f in facts))
        jev_rows(p, state, "Under the stated policy, is the requested action permitted? "
                           "Treat unproved required conditions as not satisfied.", ["yes", "no"],
                 {"yes": "Every required condition is established and no prohibition applies.",
                  "no": "A condition is missing or a prohibition applies."}, "no" if broken else "yes",
                 "synth_policy", rng, n_neg=1)

    for _ in range(args.n_ordinal):
        lvl = rng.randrange(len(SEVERITY))
        state = "Incident report: " + rng.choice(SEVERITY_FACTS[lvl])
        jev_rows(p, state, "Rate incident impact using only reported facts. Use the highest fully supported level.",
                 [str(i) for i in range(len(SEVERITY))], {str(i): c for i, c in enumerate(SEVERITY)}, str(lvl),
                 "synth_ordinal", rng, n_neg=3)
    # --- answer adequacy (JevBench's judge tier is this shape): prompt-level verdicts of the IFEval checker from the
    # `ifollow` part, and SciQ answers against their distractors. Never the benchmark's own items.
    ADQ_Q = "Does the response fully satisfy the request, using the supplied reference when present?"
    ADQ_C = {"yes": "Correct, complete, and follows all explicit constraints",
             "no": "Wrong, incomplete, unsupported or violates a constraint"}
    if args.ifollow_part and os.path.exists(args.ifollow_part):
        n = 0
        for line in open(args.ifollow_part):
            r = json.loads(line)
            if not r["source"].endswith("_all") or n >= args.n_adequacy:
                continue
            state = r["premise"].replace("Request:\n", "Request: ").replace("\n\nResponse:\n", "\nResponse: ")
            jev_rows(p, state[:6000], ADQ_Q, ["no", "yes"], ADQ_C, "yes" if r["label"] == OURS["entailment"] else "no",
                     "adequacy_ifeval", rng, n_neg=1)
            n += 1
    try:
        for ex in load_dataset("allenai/sciq", split="train").shuffle(seed=args.seed).select(range(args.n_adequacy)):
            good = rng.random() < 0.5
            ans = ex["correct_answer"] if good else rng.choice([ex["distractor1"], ex["distractor2"], ex["distractor3"]])
            ref = f"\nReference: {ex['support'][:600]}" if ex.get("support") and rng.random() < 0.5 else ""
            jev_rows(p, f"Request: {ex['question']}{ref}\nResponse: {ans}", ADQ_Q, ["no", "yes"], ADQ_C,
                     "yes" if good else "no", "adequacy_sciq", rng, n_neg=1)
    except Exception as e:  # noqa: BLE001
        print(f"[jevfmt] sciq skipped: {type(e).__name__}", flush=True)

    # --- adequacy where BOTH the value and an explicit format constraint must hold (the shape of JevBench's
    # "Return only the sum of 17 and 25. -> 42"). Every label is computed, none is guessed.
    def task():
        kind = rng.randrange(6)
        a, b = rng.randint(3, 99), rng.randint(3, 99)
        if kind == 0: return f"the sum of {a} and {b}", str(a + b), str(a + b + rng.choice([-2, -1, 1, 10]))
        if kind == 1: return f"the product of {a % 13 + 2} and {b % 12 + 2}", str((a % 13 + 2) * (b % 12 + 2)), str((a % 13 + 2) * (b % 12 + 2) + rng.choice([-3, 2, 5]))
        if kind == 2: return f"{a} minus {b}", str(a - b), str(b - a if a != b else a)
        if kind == 3:
            xs = rng.sample(range(1, 90), 4)
            return f"the largest of {xs}", str(max(xs)), str(sorted(xs)[-2])
        if kind == 4:
            w = rng.choice(["lantern", "harbor", "pencil", "orchid", "granite", "velvet"])
            return f"the word '{w}' spelled backwards", w[::-1], w[::-1][1:] + w[::-1][0]
        w = rng.choice(["banana", "committee", "mississippi", "letter", "balloon"]); ch = rng.choice(sorted(set(w)))
        return f"how many times the letter '{ch}' occurs in '{w}'", str(w.count(ch)), str(w.count(ch) + 1)

    FORMATS = [("Return only {t}.", lambda v: v, lambda v: f"The answer is {v}."),
               ("Return only {t}, with no other text.", lambda v: v, lambda v: f"Sure! {v}"),
               ("Give {t} as JSON of the form {{\"answer\": ...}} and nothing else.",
                lambda v: json.dumps({"answer": v}), lambda v: v),
               ("State {t} in one complete sentence.", lambda v: f"The result is {v}.", lambda v: v),
               ("Give {t} and then, on a new line, the word DONE.", lambda v: f"{v}\nDONE", lambda v: v)]
    for _ in range(args.n_adequacy_combo):
        what, right, wrong = task()
        req, ok_fmt, bad_fmt = rng.choice(FORMATS)
        case = rng.randrange(4)  # 0 right+format, 1 wrong value, 2 right value wrong format, 3 both wrong
        resp = (ok_fmt if case in (0, 1) else bad_fmt)(right if case in (0, 2) else wrong)
        jev_rows(p, f"Request: {req.format(t=what)[0].upper() + req.format(t=what)[1:]}\nResponse: {resp}", ADQ_Q,
                 ["no", "yes"], ADQ_C, "yes" if case == 0 else "no", "adequacy_combo", rng, n_neg=1)

    # --- routing to a specialist, generated: the category is decided by how the request is built
    ROUTE_C = {"math": "Self-contained calculation or proof", "coding": "Self-contained code writing or explanation",
               "coding_agent": "Inspect or edit repository files, or run tests", "document": "Answer from a supplied document",
               "tools": "Carry out an action in an external service", "general": "None of the specialist categories"}
    langs, things = ["Python", "Go", "Rust", "TypeScript"], ["a binary search", "an LRU cache", "a JSON parser", "a rate limiter"]
    files, svc = ["utils/date.py", "src/auth.ts", "pkg/cache/lru.go"], ["calendar", "CRM", "ticketing system", "email"]
    makers = {
        "math": lambda: rng.choice([f"Compute the least common multiple of {rng.randint(4, 40)} and {rng.randint(4, 40)}.",
                                    f"What is {rng.randint(3, 60)}% of {rng.randint(50, 900)}?",
                                    f"Solve for x: {rng.randint(2, 9)}x + {rng.randint(1, 30)} = {rng.randint(40, 200)}.",
                                    "Prove that the sum of two odd integers is even."]),
        "coding": lambda: rng.choice([f"Write {rng.choice(things)} in {rng.choice(langs)}.",
                                      f"Explain what a closure is in {rng.choice(langs)}, with a short example."]),
        "coding_agent": lambda: rng.choice([f"The test suite fails after my change to {rng.choice(files)}; find the bug, fix it and re-run the tests.",
                                            f"Rename the helper in {rng.choice(files)} across the repository and make sure CI still passes."]),
        "document": lambda: rng.choice(["Using the attached contract, what is the notice period for termination?",
                                        "According to the report I pasted below, which region grew fastest last year?"]),
        "tools": lambda: rng.choice([f"Create a meeting in my {rng.choice(svc)} for Friday at 10:00 with the design team.",
                                     f"Close ticket #{rng.randint(1000, 9999)} in the {rng.choice(svc)} and notify the requester."]),
        "general": lambda: rng.choice(["What are some good habits for a productive morning?",
                                       "Suggest a name for a small bakery.", "Why is the sky blue, in one paragraph?"]),
    }
    for _ in range(args.n_routing):
        gold = rng.choice(list(makers))
        jev_rows(p, makers[gold](), "Choose the specialist needed for the request. File edits with test execution use "
                 "coding_agent, even if code-related.", list(ROUTE_C), ROUTE_C, gold, "synth_routing", rng, n_neg=3)

    # --- probability items: the label is SAMPLED with the exact probability, so cross-entropy pulls the output
    # towards that probability instead of towards 0/1 (JevBench scores fidelity to the exact gold distribution)
    from math import comb
    for _ in range(args.n_prob):
        lot, bad = rng.randint(8, 30), rng.randint(1, 6)
        k = rng.randint(1, min(6, lot - bad))
        p_yes = 1 - comb(lot - bad, k) / comb(lot, k)
        state = (f"A lot holds {lot} units; exactly {bad} of them are defective and look identical to the good ones. "
                 f"An inspector draws {k} units at random without replacement.")
        gold = "yes" if rng.random() < p_yes else "no"
        jev_rows(p, state, "Will the sample contain at least one defective unit? Give probabilities that reflect the "
                 "evidence in the state.", ["no", "yes"],
                 {"yes": "At least one of the sampled units is defective.", "no": "None of the sampled units is defective."},
                 gold, "synth_probability", rng, n_neg=1)
    p.close()


# --------------------------------------------------------------------------------------- agentic v2
M2W_HELD_OUT = 0.15  # fraction of websites never trained on, so eval_agentic.py has an honest Mind2Web split


def m2w_websites(ds, seed):
    sites = sorted({ex["website"] for ex in ds})
    rng = random.Random(seed)
    rng.shuffle(sites)
    cut = max(1, int(len(sites) * M2W_HELD_OUT))
    return set(sites[cut:]), set(sites[:cut])  # (train, held out)


def elem_text(cand, limit=300):
    """A candidate element as the model sees it: its tag and the text around it."""
    if isinstance(cand, dict):
        rep = cand.get("attributes") or cand.get("backend_node_id") or ""
        return re.sub(r"\s+", " ", str(cand.get("tag", "")) + " " + str(rep))[:limit]
    return re.sub(r"\s+", " ", str(cand))[:limit]


def build_agentic2(args):
    """Agent-step and agent-trajectory judgements.

    mind2web   premise = goal + actions so far + the page's candidate elements; hypothesis = the next action.
               Websites are split; the held-out ones go to eval_agentic.py and are never written here.
    when2call  the SFT/preference TRAIN splits (v2 mistakenly used the `mcq` TEST split as training data).
    traj       premise = task + trajectory, hypothesis = "the agent completed the task": AgentTraj-L trajectories
               are successful by construction, so negatives are trajectories cut before the end or ending in
               another episode's final action.
    """
    from datasets import load_dataset
    rng = random.Random(args.seed)
    p = Part(args.out, "agentic2")

    m2w = load_dataset("osunlp/Mind2Web", split="train")
    train_sites, held = m2w_websites(m2w, args.seed)
    json.dump(sorted(held), open(os.path.join(args.out, "mind2web_heldout_websites.json"), "w"), indent=1)
    n_steps = 0
    for ex in m2w:
        if ex["website"] not in train_sites:
            continue
        reprs = ex["action_reprs"]
        for i, act in enumerate(reprs):
            if n_steps >= args.n_m2w:
                break
            history = " -> ".join(reprs[max(0, i - 3):i]) or "(nothing yet)"
            page = ""
            try:
                cands = ex["actions"][i].get("pos_candidates", []) + ex["actions"][i].get("neg_candidates", [])
                page = " | ".join(elem_text(c) for c in cands[:40])
            except Exception:  # noqa: BLE001
                pass
            prem = (f"Goal: {ex['confirmed_task']}\nWebsite: {ex['website']}\nActions so far: {history}\n"
                    f"Elements on the page: {page}")
            p.add(prem, f"The next action is: {act}", OURS["entailment"], "m2w_step")
            other = rng.choice(reprs)
            if other != act:
                p.add(prem, f"The next action is: {other}", OURS["contradiction"], "m2w_step_neg")
            if i + 1 < len(reprs):
                p.add(prem, f"The task is already complete; no further action is needed.",
                      OURS["contradiction"], "m2w_done_neg")
            else:
                p.add(prem, f"This is the last action needed to complete the task.", OURS["entailment"], "m2w_done")
            n_steps += 1
    print(f"[agentic2] mind2web: {p.n} rows from {len(train_sites)} websites, {len(held)} held out", flush=True)

    for cfg in ("train_sft", "train_pref"):
        try:
            ds = load_dataset("nvidia/When2Call", cfg, split="train")
        except Exception as e:  # noqa: BLE001
            print(f"[agentic2] When2Call {cfg} skipped: {type(e).__name__}", flush=True)
            continue
        for ex in ds:
            msgs = ex.get("messages") or []
            user = next((m["content"] for m in msgs if m.get("role") == "user"), "")
            good = next((m for m in msgs if m.get("role") == "assistant"), None)
            if not user or not good:
                continue
            prem = f"User request: {user[:2000]}\nAvailable tools: {_tools_str(ex.get('tools'))}"
            answer = (good.get("content") or "").strip() or json.dumps(good.get("tool_calls") or {}, ensure_ascii=False)
            p.add(prem, f"The assistant should: {answer[:400]}", OURS["entailment"], f"when2call_{cfg}")
            rejected = ex.get("rejected") or ex.get("chosen_rejected")
            if isinstance(rejected, str) and rejected.strip():
                p.add(prem, f"The assistant should: {rejected[:400]}", OURS["contradiction"], f"when2call_{cfg}_neg")

    traj = load_dataset("AgentGym/AgentTraj-L", split="train")
    finals = []
    n_traj = 0
    for ex in traj:
        if n_traj >= args.n_traj2:
            break
        turns = [(t.get("from") or "", (t.get("value") or "").strip()) for t in ex.get("conversations") or []]
        acts = [v for who, v in turns if who in ("gpt", "assistant") and v]
        if len(acts) < 3:
            continue
        task = next((v for who, v in turns if who == "human"), "")[:1500]
        full = "\n".join(f"step {i+1}: {a[:200]}" for i, a in enumerate(acts))
        p.add(f"Task: {task}\nTrajectory:\n{full}", "The agent completed the task.", OURS["entailment"], "traj_done")
        cut = "\n".join(f"step {i+1}: {a[:200]}" for i, a in enumerate(acts[: max(1, len(acts) // 2)]))
        p.add(f"Task: {task}\nTrajectory:\n{cut}", "The agent completed the task.", OURS["neutral"], "traj_cut")
        if finals:
            swapped = acts[:-1] + [rng.choice(finals)]
            bad = "\n".join(f"step {i+1}: {a[:200]}" for i, a in enumerate(swapped))
            p.add(f"Task: {task}\nTrajectory:\n{bad}", "The agent completed the task.", OURS["contradiction"], "traj_swap")
        finals.append(acts[-1])
        if len(finals) > 5000:
            finals = finals[-3000:]
        n_traj += 1
    p.close()


# --------------------------------------------------------------------------------------- agent policy compliance
TAU_V1 = ("https://raw.githubusercontent.com/sierra-research/tau-bench/main/historical_trajectories/"
          "{model}-{domain}.json")
TAU_V1_RUNS = [(m, d) for m in ("gpt-4o", "sonnet-35-new") for d in ("retail", "airline")]
TAU_DONE = ["The agent followed the domain policy and resolved the user's request.",
            "The conversation ended with the user's request handled correctly and within the rules."]
TAU_FAIL = ["The agent broke the domain policy or left the user's request unresolved."]
AUTH_MARKS = ("find_user_id_by_email", "find_user_id_by_name_zip", "get_user_details", "authenticate")


def tau_text(traj, policy_chars=6000, trace_chars=6000):
    """(policy, transcript) from a tau-bench trajectory: the system message is the domain policy."""
    policy = next((m.get("content") or "" for m in traj if m.get("role") == "system"), "")[:policy_chars]
    lines = []
    for m in traj:
        role = m.get("role")
        if role == "system":
            continue
        if m.get("tool_calls"):
            for c in m["tool_calls"]:
                fn = (c.get("function") or {})
                lines.append(f"{role} calls {fn.get('name')}({str(fn.get('arguments'))[:200]})")
        text = (m.get("content") or "").strip()
        if text:
            lines.append(f"{role}: {text[:400]}")
    return policy, "\n".join(lines)[-trace_chars:]


def build_agentic_if(args):
    """Did the agent follow the written policy? tau-bench v1 trajectories carry a 0/1 reward; a trajectory with its
    authentication step removed is a policy violation by construction (the policy demands it first).

    tau2-bench (retail / airline / telecom, with per-assertion labels) is the held-out eval in eval_agentic.py and is
    never read here."""
    import urllib.request
    rng = random.Random(args.seed)
    p = Part(args.out, "agentic_if")
    n_traj = 0
    for model, domain in TAU_V1_RUNS:
        try:
            raw = urllib.request.urlopen(TAU_V1.format(model=model, domain=domain), timeout=120).read()
        except Exception as e:  # noqa: BLE001
            print(f"[agentic_if] {model}-{domain} skipped: {type(e).__name__}", flush=True)
            continue
        for row in json.loads(raw):
            traj = row.get("traj") or []
            policy, trace = tau_text(traj)
            if not policy or not trace:
                continue
            ok = float(row.get("reward", 0)) >= 1.0
            prem = f"Domain policy:\n{policy}\n\nConversation:\n{trace}"
            p.add(prem, rng.choice(TAU_DONE), OURS["entailment"] if ok else OURS["contradiction"],
                  f"tau_{domain}_{'ok' if ok else 'fail'}")
            p.add(prem, TAU_FAIL[0], OURS["contradiction"] if ok else OURS["entailment"],
                  f"tau_{domain}_inv")
            n_traj += 1
            # a successful run with its authentication turns removed no longer follows the policy
            if ok:
                stripped = [m for m in traj if not any(a in str(m.get("tool_calls") or "") for a in AUTH_MARKS)]
                if len(stripped) < len(traj):
                    p2, t2 = tau_text(stripped)
                    p.add(f"Domain policy:\n{p2}\n\nConversation:\n{t2}", rng.choice(TAU_DONE),
                          OURS["contradiction"], f"tau_{domain}_noauth")
                    p.add(f"Domain policy:\n{p2}\n\nConversation:\n{t2}",
                          "The agent verified the user's identity before acting on the account.",
                          OURS["contradiction"], f"tau_{domain}_authcheck")
                    p.add(prem, "The agent verified the user's identity before acting on the account.",
                          OURS["entailment"], f"tau_{domain}_authcheck")
            # half-finished conversation: the request is not handled yet
            if len(traj) > 6:
                p3, t3 = tau_text(traj[: len(traj) // 2])
                p.add(f"Domain policy:\n{p3}\n\nConversation:\n{t3}", rng.choice(TAU_DONE),
                      OURS["neutral"], f"tau_{domain}_cut")
    print(f"[agentic_if] tau-bench v1 trajectories: {n_traj}", flush=True)
    p.close()


# --------------------------------------------------------------------------------------- agentic distillation
CALL_RE = re.compile(r"^\s*\[?\s*([A-Za-z_][\w .\-]*)\s*\(")
NAME_RE = re.compile(r'"name"\s*:\s*"([^"]+)"')


def mutate_call(call, rng, names):
    """A wrong version of a gold call: another tool's name, or a changed argument value."""
    m = CALL_RE.match(call)
    if m and names:
        other = rng.choice(names)
        if other != m.group(1):
            return call.replace(m.group(1), other, 1)
    nums = re.findall(r"=\s*(\d+)", call)
    if nums:
        n = rng.choice(nums)
        return call.replace(f"={n}", f"={int(n) + rng.choice([1, 7, 100])}", 1)
    q = re.findall(r'="([^"]{3,})"', call)
    if q:
        return call.replace(f'="{q[0]}"', f'="{q[0][::-1]}"', 1)
    return None


def turns_of(conv):
    out = []
    for m in conv or []:
        who = m.get("from") or m.get("role") or ""
        val = (m.get("value") or m.get("content") or "").strip()
        if val:
            out.append(("assistant" if who in ("gpt", "assistant") else "user", val))
    return out


def build_agentic_distill(args):
    """Tool-call and next-action judgements distilled from published agent traces.

    toolace    ToolACE: the system message lists the tools; the gold call entails, a call with another tool's name
               or a changed argument contradicts.
    apigen     APIGen-MT-5k: a domain policy plus a multi-turn trace — the same shape as tau-bench, so it also
               feeds "did the agent follow the policy" rows.
    flan_react Agent-FLAN ReAct traces: next action from the observation history.
    """
    from datasets import load_dataset
    rng = random.Random(args.seed)
    p = Part(args.out, "agentic_distill")

    def steps(conv, prem_head, names, src, cap):
        n = 0
        turns = turns_of(conv)
        for i, (who, val) in enumerate(turns):
            if who != "assistant" or n >= cap:
                continue
            history = "\n".join(f"{w}: {v[:300]}" for w, v in turns[max(0, i - 4):i])
            prem = f"{prem_head}\nConversation so far:\n{history}"[-6000:]
            p.add(prem, f"The next action is: {val[:400]}", OURS["entailment"], src)
            bad = mutate_call(val, rng, names)
            if bad and bad != val:
                p.add(prem, f"The next action is: {bad[:400]}", OURS["contradiction"], f"{src}_neg")
            n += 1
        return n

    tool_ace = load_dataset("Team-ACE/ToolACE", split="train").shuffle(seed=args.seed)
    used = 0
    for ex in tool_ace:
        if used >= args.n_toolace:
            break
        sysmsg = (ex.get("system") or "")[:4000]
        names = NAME_RE.findall(ex.get("system") or "")
        used += bool(steps(ex.get("conversations"), f"Available tools and instructions:\n{sysmsg}", names,
                           "toolace", cap=2))
    print(f"[distill] toolace: {p.n} rows", flush=True)

    api = load_dataset("Salesforce/APIGen-MT-5k", "dataset", split="train")
    for ex in api:
        policy = (ex.get("system") or "")[:5000]
        names = NAME_RE.findall(ex.get("tools") if isinstance(ex.get("tools"), str) else json.dumps(ex.get("tools") or []))
        steps(ex.get("conversations"), f"Domain policy:\n{policy}", names, "apigen", cap=3)
        turns = turns_of(ex.get("conversations"))
        if len(turns) >= 4:
            full = "\n".join(f"{w}: {v[:300]}" for w, v in turns)[-6000:]
            prem = f"Domain policy:\n{policy}\n\nConversation:\n{full}"
            p.add(prem, "The agent followed the domain policy and resolved the user's request.",
                  OURS["entailment"], "apigen_policy")
            half = "\n".join(f"{w}: {v[:300]}" for w, v in turns[: len(turns) // 2])[-6000:]
            p.add(f"Domain policy:\n{policy}\n\nConversation:\n{half}",
                  "The agent followed the domain policy and resolved the user's request.",
                  OURS["neutral"], "apigen_policy_cut")
    print(f"[distill] + apigen: {p.n} rows", flush=True)

    try:
        flan = load_dataset("internlm/Agent-FLAN", split="agent_instruct_react")
        for ex in flan:
            steps(ex.get("conversation"), "Agent task and observations:", [], "flan_react", cap=2)
    except Exception as e:  # noqa: BLE001
        print(f"[distill] Agent-FLAN skipped: {type(e).__name__}: {str(e)[:100]}", flush=True)
    p.close()


# --------------------------------------------------------------------------------------- long documents
RARE = 7  # a word this long or longer counts as a content anchor when checking a claim against the kept text


def anchored(claim, text_lower, need=3):
    """Cheap grounding check: the claim's long words must appear in the part of the document we keep."""
    words = {w.lower().strip(".,;:()[]\"'") for w in claim.split() if len(w) >= RARE}
    if not words:
        return False
    return sum(1 for w in words if w in text_lower) >= min(need, len(words))


def perturb_claim(claim, rng):
    """Turn a supported sentence into a contradicted one: move a number, or negate the main verb."""
    nums = re.findall(r"\b\d[\d,\.]*\b", claim)
    if nums:
        n = rng.choice(nums)
        try:
            val = float(n.replace(",", ""))
        except ValueError:
            return None
        new = f"{val * rng.choice([2, 3, 0.25, 10]):,.0f}" if val >= 1 else f"{val * 5:.2f}"
        return claim.replace(n, new, 1)
    for verb, neg in ((" is ", " is not "), (" are ", " are not "), (" was ", " was not "),
                      (" were ", " were not "), (" has ", " has no "), (" have ", " have no ")):
        if verb in claim:
            return claim.replace(verb, neg, 1)
    return None


def build_longdoc(args):
    """Entailment over documents of a few thousand tokens: the shape the WebQL / JevBench-hard items have.

    govreport  premise = a GAO report, hypothesis = a sentence of its own summary (entailment), of another report's
               summary (neutral: not stated here) or a number/negation perturbation of its own (contradiction).
    qasper     premise = the paper text, hypothesis = "The paper states: <answer>"; questions the annotators marked
               unanswerable become neutral, answers taken from a different paper become neutral too.
    haystack_long  one known premise sentence buried in 4k-24k characters of filler, 30% of the time removed.
    """
    from datasets import load_dataset
    rng = random.Random(args.seed)
    p = Part(args.out, "longdoc")
    keep = args.long_chars

    gov = load_dataset("ccdv/govreport-summarization", "document", split="train").shuffle(seed=args.seed)
    gov = gov.select(range(min(args.n_gov, len(gov))))
    summaries = []
    for ex in gov:
        doc = (ex["report"] or "")[:keep]
        low = doc.lower()
        sents = [s for s, _, _ in split_sents(ex["summary"] or "") if 60 <= len(s) <= 400]
        rng.shuffle(sents)
        own = [s for s in sents if anchored(s, low)][:2]
        for s in own:
            p.add(doc, s, OURS["entailment"], "gov_support")
            bad = perturb_claim(s, rng)
            if bad and bad != s:
                p.add(doc, bad, OURS["contradiction"], "gov_perturb")
        if summaries:
            p.add(doc, rng.choice(summaries), OURS["neutral"], "gov_other")
        summaries.extend(sents[:3])
        if len(summaries) > 20000:
            summaries = summaries[-10000:]
    print(f"[longdoc] govreport done: {p.n}", flush=True)

    # allenai/qasper still ships a loading script; read the Hub's auto-converted parquet instead
    try:
        qas = load_dataset("allenai/qasper", split="train", revision="refs/convert/parquet")
    except Exception as e:  # noqa: BLE001
        print(f"[longdoc] qasper skipped: {type(e).__name__}: {str(e)[:120]}", flush=True)
        qas = []
    pool = []
    for ex in qas:
        ft = ex["full_text"]
        text = "\n\n".join(f"{name}\n" + "\n".join(paras) for name, paras in
                            zip(ft["section_name"], ft["paragraphs"]))
        doc = f"{ex['title']}\n\n{ex['abstract']}\n\n{text}"[:keep]
        for q, answers in zip(ex["qas"]["question"], ex["qas"]["answers"]):
            a = (answers["answer"] or [{}])[0]
            free = (a.get("free_form_answer") or "").strip()
            spans = a.get("extractive_spans") or []
            if a.get("unanswerable"):
                if free or spans:
                    continue
                p.add(doc, f'The paper answers the question "{q}": it states the answer explicitly.',
                      OURS["neutral"], "qasper_unanswerable")
                continue
            ans = free or (spans[0] if spans else "")
            if len(ans) < 10:
                continue
            claim = f'The paper states, in answer to "{q}": {ans}'
            p.add(doc, claim, OURS["entailment"], "qasper_answer")
            if pool:
                p.add(doc, rng.choice(pool), OURS["neutral"], "qasper_other")
            pool.append(claim)
            if len(pool) > 5000:
                pool = pool[-3000:]
    print(f"[longdoc] qasper done: {p.n}", flush=True)

    # long haystack: the same idea as the v2 haystack part, at 4k-24k characters instead of a few hundred
    pairs, filler = [], []
    with open(args.text_part) as fh:
        for line in fh:
            r = json.loads(line)
            if len(filler) < 300_000:
                filler.append(r["premise"].strip())
            if len(pairs) < 200_000 and r["source"] in ("anli", "nli_fever", "multi_nli"):
                pairs.append((r["premise"].strip(), r["hypothesis"].strip(), r["label"]))
    rng.shuffle(pairs)
    for prem, hyp, y in pairs[: args.n_haystack_long]:
        doc, size = [], rng.randint(4000, keep)
        while sum(len(x) + 2 for x in doc) < size:
            doc.append(rng.choice(filler))
        drop = rng.random() < 0.30
        if not drop:
            doc.insert(rng.randrange(len(doc) + 1), prem)
        p.add("\n\n".join(doc), hyp, OURS["neutral"] if drop else y,
              "haystack_long_drop" if drop else "haystack_long")
    p.close()


# --------------------------------------------------------------------------------------- computed hard decisions
def build_hardfmt(args):
    """temporal_numeric / multi_hop / long_policy items from hard_gen.py: generated scenarios, computed gold labels.
    The tempting wrong answer the narrative pushes (`surface`) is always one of the negatives."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import hard_gen
    print("[hardfmt] generator selftest:", hard_gen.selftest(2000, args.seed + 1), flush=True)
    rng = random.Random(args.seed)
    p = Part(args.out, "hardfmt")
    for fam, n in (("temporal_numeric", args.n_temporal), ("multi_hop", args.n_multihop), ("long_policy", args.n_longpolicy)):
        for _ in range(n):
            it = hard_gen.FAMILIES[fam](rng)
            tmpl = rng.choice(JEV_TEMPLATES)
            others = [o for o in it["options"] if o not in (it["gold"], it["surface"])]
            rng.shuffle(others)
            for lab in [it["gold"], it["surface"]] + others[:1]:
                p.add(it["state"], tmpl.format(instr=it["instructions"], label=lab, crit=it["options"][lab]),
                      OURS["entailment"] if lab == it["gold"] else OURS["contradiction"], f"hard_{fam}")
    p.close()


# --------------------------------------------------------------------------------------- complex instruction following
def build_ifcomplex(args):
    """Multi-constraint instruction following as typed decisions that are NOT yes/no.

    Prompts carry 3+ verifiable constraints (argilla/ifeval-like-data); every constraint of every response is checked
    by the IFEval verifier, so each label below is computed:
      which     "Which requirement does the response violate?"   choice over r1..rk + none  (only when <= 1 fails)
      count     "How many of the listed requirements are met?"   score 0..k
      severity  fully_compliant / one_requirement_missed / several_requirements_missed
      best_of   "Which response follows every requirement?"     choice A/B/C  (only when exactly one does)
    Responses: the dataset's own (a strong model, mostly compliant), responses of small models from
    gen_if_responses.py when present (natural failures), and the mechanical perturbations as a last resort.
    IFEval's own prompts are excluded, as in `ifollow`."""
    from datasets import load_dataset
    rng = random.Random(args.seed)
    reg = if_checker()
    p = Part(args.out, "ifcomplex")
    banned = {ex["prompt"].strip() for ex in load_dataset("google/IFEval", split="train")}
    extra = defaultdict(list)
    if args.if_gen and os.path.exists(args.if_gen):
        for line in open(args.if_gen):
            r = json.loads(line)
            extra[r["prompt"].strip()].append(r["response"])
    ds = load_dataset("argilla/ifeval-like-data", split="train").shuffle(seed=args.seed + 1)
    used = Counter()
    for ex in ds:
        if used["prompts"] >= args.n_ifcomplex:
            break
        prompt = (ex["instruction"] or "").strip()
        if not prompt or prompt in banned:
            continue
        try:
            ids = ex["instruction_id_list"]
            ids = json.loads(ids.replace("'", '"')) if isinstance(ids, str) else list(ids)
            kw = json.loads(ex["kwargs"]) if isinstance(ex["kwargs"], str) else dict(ex["kwargs"])
        except Exception:  # noqa: BLE001
            continue
        if not 3 <= len(ids) <= 5:
            continue
        # the dataset stores ONE merged kwargs dict; two constraints sharing an argument name would get each
        # other's value and a wrong label, so such prompts are skipped
        keys = [k for i in ids if i in reg for k in (reg[i](i).get_instruction_args_keys() or [])]
        if len(keys) != len(set(keys)):
            used["skipped_shared_kwargs"] += 1
            continue
        responses = [(ex["response"] or "").strip()] + extra.get(prompt, [])
        if len(responses) < 3:
            responses += [IF_PERTURB[n](responses[0], rng) for n in rng.sample(list(IF_PERTURB), 3 - len(responses))]
        checked = []
        for resp in responses:
            res = if_check(reg, ids, [kw] * len(ids), prompt, resp)
            if res is not None and resp:
                checked.append((resp, res))
        if not checked:
            continue
        used["prompts"] += 1
        labels = [f"r{i + 1}" for i in range(len(ids))]
        for resp, res in checked:
            reqs = {lab: desc for lab, (desc, _) in zip(labels, res)}
            listing = "\n".join(f"{lab}: {desc}" for lab, desc in reqs.items())
            state = f"Request:\n{prompt}\n\nRequirements:\n{listing}\n\nResponse:\n{resp[:5000]}"
            failed = [lab for lab, (_, ok) in zip(labels, res) if not ok]
            n_ok = len(ids) - len(failed)
            if len(failed) <= 1:
                jev_rows(p, state, "Which of the listed requirements does the response violate?", labels + ["none"],
                         {**reqs, "none": "The response satisfies every listed requirement"},
                         failed[0] if failed else "none", "ifc_which", rng, n_neg=3)
                used["which"] += 1
            jev_rows(p, state, "How many of the listed requirements does the response satisfy?",
                     [str(i) for i in range(len(ids) + 1)],
                     {str(i): f"Exactly {i} of the {len(ids)} requirements are satisfied" for i in range(len(ids) + 1)},
                     str(n_ok), "ifc_count", rng, n_neg=2)
            sev = "fully_compliant" if not failed else "one_requirement_missed" if len(failed) == 1 else "several_requirements_missed"
            jev_rows(p, state, "How well does the response comply with the listed requirements?",
                     ["fully_compliant", "one_requirement_missed", "several_requirements_missed"],
                     {"fully_compliant": "Every listed requirement is satisfied", "one_requirement_missed": "Exactly one requirement is not satisfied",
                      "several_requirements_missed": "Two or more requirements are not satisfied"}, sev, "ifc_severity", rng, n_neg=2)
        full = [i for i, (_, res) in enumerate(checked) if all(ok for _, ok in res)]
        if len(checked) >= 3 and len(full) == 1:
            pick = rng.sample(range(len(checked)), 3)
            if full[0] in pick:
                names = ["A", "B", "C"]
                body = "\n\n".join(f"Response {n}:\n{checked[i][0][:2200]}" for n, i in zip(names, pick))
                jev_rows(p, f"Request:\n{prompt}\n\n{body}", "Which response follows every requirement of the request?",
                         names, {n: f"Response {n} satisfies all the requirements" for n in names},
                         names[pick.index(full[0])], "ifc_best_of", rng, n_neg=2)
                used["best_of"] += 1
    print(f"[ifcomplex] {dict(used)}", flush=True)
    p.close()


# --------------------------------------------------------------------------------------- benchmark panel (train + test)
PANEL_MANIFEST = "panel_manifest.json"  # every (repo, split) written here went into training: report it wherever these benchmarks are scored


def build_panel(args):
    """Typed-decision rows from the benchmark panel: TRAIN and TEST splits both go in (the user's call). Everything
    listed in panel_manifest.json is therefore contaminated as an evaluation and is dropped from the gate."""
    import csv
    from datasets import load_dataset
    rng = random.Random(args.seed)
    p = Part(args.out, "panel")
    manifest = []

    def mc(state, q, opts, gold, src, n_neg=3):
        jev_rows(p, state, q, list(opts), opts, gold, src, rng, n_neg=n_neg)

    def ds(repo, cfg, split):
        manifest.append([repo, cfg, split])
        return load_dataset(repo, cfg, split=split) if cfg else load_dataset(repo, split=split)

    L = "ABCDEFGHIJ"
    # MMLU (auxiliary_train is the ARC/OBQA/RACE-style pool the paper published; test = the benchmark itself)
    for split in ("auxiliary_train", "test"):
        try:
            d = ds("cais/mmlu", "all", split)
            d = d.shuffle(seed=args.seed).select(range(min(args.n_mmlu, len(d)))) if split == "auxiliary_train" else d
            for ex in d:
                opts = {L[i]: c for i, c in enumerate(ex["choices"])}
                mc(ex["question"], "Which option is the correct answer?", opts, L[int(ex["answer"])], f"mmlu_{split}")
        except Exception as e:  # noqa: BLE001
            print(f"[panel] mmlu {split} skipped: {type(e).__name__}", flush=True)
    for cfg in ("ARC-Easy", "ARC-Challenge"):
        for split in ("train", "validation", "test"):
            for ex in ds("allenai/ai2_arc", cfg, split):
                opts = dict(zip(ex["choices"]["label"], ex["choices"]["text"]))
                if ex["answerKey"] in opts:
                    mc(ex["question"], "Which option is the correct answer?", opts, ex["answerKey"], f"arc_{cfg[-4:].lower()}_{split}")
    for split in ("train", "validation"):  # HellaSwag / WinoGrande test labels are private
        for ex in ds("Rowan/hellaswag", None, split):
            opts = {L[i]: e for i, e in enumerate(ex["endings"])}
            mc(ex["ctx"], "Which ending continues the text correctly?", opts, L[int(ex["label"])], f"hellaswag_{split}")
        for ex in ds("allenai/winogrande", "winogrande_xl" if split == "train" else "winogrande_debiased", split):
            opts = {"1": ex["option1"], "2": ex["option2"]}
            mc(ex["sentence"], "Which option fills the blank correctly?", opts, str(ex["answer"]), f"winogrande_{split}", n_neg=1)
    for split in ("train", "test"):
        for ex in ds("openai/gsm8k", "main", split):
            gold = ex["answer"].split("####")[-1].strip().replace(",", "")
            try:
                g = float(gold)
            except ValueError:
                continue
            wrong = {str(int(g + d)) if g == int(g) else str(round(g + d, 2)) for d in (rng.choice([-3, -1, 1, 2, 7, 10]), rng.choice([-10, 5, 12]), int(g * 2) - int(g) or 1)}
            wrong.discard(gold)
            opts = {gold: gold, **{w: w for w in list(wrong)[:3]}}
            mc(ex["question"], "Which value is the correct final answer?", opts, gold, f"gsm8k_{split}")
    for name in ("gpqa_diamond.csv", "gpqa_main.csv"):
        path = os.path.join(args.data_dir, name)
        if os.path.exists(path):
            manifest.append(["Idavidrein/gpqa", name, "local"])
            for r in csv.DictReader(open(path)):
                opts = {"A": r["Correct Answer"], "B": r["Incorrect Answer 1"], "C": r["Incorrect Answer 2"], "D": r["Incorrect Answer 3"]}
                keys = list(opts); rng.shuffle(keys)
                shuffled = {L[i]: opts[k] for i, k in enumerate(keys)}
                mc(r["Question"], "Which option is the correct answer?", shuffled, L[keys.index("A")], f"gpqa_{name[5:-4]}")
    # NLI-shaped panel members go straight in as premise / hypothesis
    for split in ("train", "validation", "test"):
        try:
            d = ds("kiddothe2b/contract-nli", "contractnli_a", split)
            feat = d.features.get("label")
            for ex in d:
                try:
                    p.add(ex["premise"], ex["hypothesis"], norm_label(ex["label"], feat), f"contractnli_{split}")
                except ValueError:
                    continue
        except Exception as e:  # noqa: BLE001
            print(f"[panel] contract-nli {split} skipped: {type(e).__name__}: {str(e)[:80]}", flush=True)
    for split in ("train", "validation"):
        try:
            for ex in ds("tasksource/nli4ct", None, split):
                lab = str(ex.get("label", ex.get("gold_label", ""))).strip().lower()
                if lab in SYN:
                    p.add(ex["premise"], ex["hypothesis"], OURS[SYN[lab]], f"nli4ct_{split}")
        except Exception as e:  # noqa: BLE001
            print(f"[panel] nli4ct {split} skipped: {type(e).__name__}", flush=True)
    for split in ("train", "test"):
        try:
            d = ds("tasksource/esci", None, split).shuffle(seed=args.seed)
            for ex in d.select(range(min(args.n_esci, len(d)))):
                lab = str(ex.get("esci_label") or ex.get("label") or "").strip().lower()
                if lab not in ("exact", "substitute", "complement", "irrelevant"):
                    continue
                state = f"Query: {ex['query']}\nProduct: {ex.get('product_title') or ex.get('product') or ''}"
                opts = {"exact": "The product exactly matches the query", "substitute": "A reasonable substitute for what was asked",
                        "complement": "Complements the queried product but is not it", "irrelevant": "Not relevant to the query"}
                mc(state, "How relevant is the product to the shopping query?", opts, lab, f"esci_{split}")
        except Exception as e:  # noqa: BLE001
            print(f"[panel] esci {split} skipped: {type(e).__name__}: {str(e)[:80]}", flush=True)
    for split in ("train", "test"):
        try:
            for ex in ds("liminghao1630/API-Bank", None, split):
                api, inp, out = str(ex.get("api_call") or ex.get("expected_output") or ""), str(ex.get("input") or ex.get("instruction") or ""), None
                if api and inp:
                    p.add(inp[:3000], f"The next API call is: {api[:400]}", OURS["entailment"], f"apibank_{split}")
        except Exception as e:  # noqa: BLE001
            print(f"[panel] api-bank {split} skipped: {type(e).__name__}: {str(e)[:80]}", flush=True)
    for repo, cfg, col, lab_col, src in (("clinc/clinc_oos", "plus", "text", "intent", "clinc"), ("legacy-datasets/banking77", None, "text", "label", "banking77")):
        for split in ("test",):  # train splits are already in the jevfmt part
            try:
                d = ds(repo, cfg, split); names = d.features[lab_col].names
                pretty = {i: n.replace("_", " ") for i, n in enumerate(names)}
                for ex in d:
                    gold = pretty[ex[lab_col]]
                    opts = rng.sample([v for v in pretty.values() if v != gold], 5) + [gold]; rng.shuffle(opts)
                    jev_rows(p, ex[col], "Which intent does the user's message express?", opts, {o: f"The user's message is about: {o}" for o in opts}, gold, f"{src}_{split}", rng)
            except Exception as e:  # noqa: BLE001
                print(f"[panel] {src} {split} skipped: {type(e).__name__}", flush=True)
    json.dump(manifest, open(os.path.join(args.out, PANEL_MANIFEST), "w"), indent=1)
    print(f"[panel] manifest: {len(manifest)} (repo, config, split) entries written to {PANEL_MANIFEST}", flush=True)
    p.close()


# --------------------------------------------------------------------------------------- merge
def build_final(args):
    from datasets import Dataset
    rng = random.Random(args.seed)
    rows, by_source, by_label = [], Counter(), Counter()
    drop = set(x for x in args.drop.split(",") if x)
    cap_prefixes = tuple(x for x in args.cap_prefixes.split(",") if x) or ("\0",)
    part_dir = os.path.join(args.out, "parts")
    for fn in sorted(os.listdir(part_dir)):
        if not fn.endswith(".jsonl"):
            continue
        with open(os.path.join(part_dir, fn)) as f:
            for line in f:
                r = json.loads(line)
                if r["source"] in drop:
                    continue
                if (args.cap_per_source and r["source"].startswith(cap_prefixes)
                        and by_source[r["source"]] >= args.cap_per_source):
                    continue
                rows.append(r)
                by_source[r["source"]] += 1
                by_label[r["label"]] += 1
    if args.mix_in:  # stage 2: keep a slice of the stage-1 mixture so the model does not forget it
        from datasets import load_from_disk
        prev = load_from_disk(os.path.join(args.mix_in, "mix"))["train"].shuffle(seed=args.seed)
        # --mix-in-quota "bullshit=16000,faith=20000": per-group row quotas (group = source prefix) taken BEFORE the
        # uniform sample, so a small but important stage-1 part is not diluted to a few hundred rows
        quota = {k: int(v) for k, v in (x.split("=") for x in args.mix_in_quota.split(",") if x)}
        groups = {"bullshit": ("falseqa", "bs_synth"), "faith": ("ragtruth", "minicheck"), "ifollow": ("ifollow",),
                  "nli": ("snli", "multi_nli", "anli", "wanli")}
        taken, picked = Counter(), []
        for r in prev:
            g = next((name for name, pref in groups.items() if r["source"].startswith(pref)), None)
            if g in quota and taken[g] < quota[g] and not r["image"]:
                taken[g] += 1
                picked.append(r)
        print(f"[build] replay quotas filled: {dict(taken)}", flush=True)
        for r in picked + list(prev.select(range(min(args.mix_in_n, len(prev))))):
            if r["image"]:
                continue
            rows.append({k: r[k] for k in ("premise", "hypothesis", "label", "source", "image")})
            by_source["stage1:" + r["source"]] += 1
            by_label[r["label"]] += 1
    print(f"[build] {len(rows)} rows from {len(by_source)} sources; labels {dict(by_label)}", flush=True)

    # class balance: downsample the dominant class to at most balance_ratio x the smallest
    target = int(min(by_label.values()) * args.balance_ratio)
    keep, per = [], Counter()
    rng.shuffle(rows)
    for r in rows:
        if per[r["label"]] < target:
            keep.append(r)
            per[r["label"]] += 1
    rows = keep
    print(f"[build] after balancing: {len(rows)}; labels {dict(per)}", flush=True)

    # leakage check against the MNLI validation splits that eval.py reports
    from datasets import load_dataset
    banned_pairs = set()
    for split in ("validation_matched", "validation_mismatched"):
        for ex in load_dataset("nyu-mll/multi_nli", split=split):
            banned_pairs.add((ex["premise"].strip().lower()[:200], ex["hypothesis"].strip().lower()[:200]))
    before = len(rows)
    rows = [r for r in rows if (r["premise"].strip().lower()[:200], r["hypothesis"].strip().lower()[:200]) not in banned_pairs]
    print(f"[build] leakage filter dropped {before - len(rows)} rows overlapping MNLI val", flush=True)

    rng.shuffle(rows)
    n_val = args.n_val
    val, train = rows[:n_val], rows[n_val:]
    ds = {"train": Dataset.from_list(train), "val": Dataset.from_list(val)}
    from datasets import DatasetDict
    DatasetDict(ds).save_to_disk(os.path.join(args.out, "mix"))

    comp = {"n_train": len(train), "n_val": len(val), "by_source": dict(by_source),
            "by_label_final": dict(per), "images": sum(1 for r in rows if r["image"])}
    json.dump(comp, open(os.path.join(args.out, "composition.json"), "w"), indent=2)
    print(json.dumps(comp, indent=2)[:2000])
    print("\n| source | rows |\n|---|---|")
    for s, n in by_source.most_common():
        print(f"| {s} | {n} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["text", "images", "agentic", "faith", "ifollow", "bullshit", "jevfmt", "longdoc", "agentic2", "agentic_if", "agentic_distill", "hardfmt", "ifcomplex", "panel", "build"])
    ap.add_argument("--out", default="/mnt/nli_mix")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--seed", type=int, default=0)
    # text
    ap.add_argument("--n-snli", type=int, default=120_000)
    ap.add_argument("--n-mnli", type=int, default=120_000)
    ap.add_argument("--n-fever", type=int, default=150_000)
    ap.add_argument("--n-qnli", type=int, default=60_000)
    ap.add_argument("--n-haystack", type=int, default=80_000)
    # images
    ap.add_argument("--n-rows", type=int, default=200_000)
    ap.add_argument("--n-claims", type=int, default=220_000)
    ap.add_argument("--max-images", type=int, default=60_000)
    ap.add_argument("--spatial-per-image", type=int, default=1)
    ap.add_argument("--answer-neg-prob", type=float, default=0.5)
    ap.add_argument("--vqa-repo", default="Multimodal-Fatima/VQAv2_train")
    ap.add_argument("--vqa-split", default="train")
    ap.add_argument("--part-name", default="vqa")
    # agentic
    ap.add_argument("--n-traj", type=int, default=40_000)
    ap.add_argument("--n-synth", type=int, default=50_000)
    ap.add_argument("--no-synth-state", action="store_true")
    # faith / ifollow / bullshit
    ap.add_argument("--faith-sents-per-resp", type=int, default=3)
    ap.add_argument("--n-ifollow", type=int, default=15_000, help="source examples; each gives ~9 rows")
    ap.add_argument("--n-bs-synth", type=int, default=3000)
    # agentic2
    ap.add_argument("--n-m2w", type=int, default=8000, help="Mind2Web steps (each gives ~3 rows)")
    ap.add_argument("--n-traj2", type=int, default=8000)
    ap.add_argument("--n-toolace", type=int, default=12000)
    # longdoc
    ap.add_argument("--long-chars", type=int, default=24000, help="premise cap; ~6k tokens, one WebQL window")
    ap.add_argument("--n-gov", type=int, default=12000)
    ap.add_argument("--n-haystack-long", type=int, default=20000)
    ap.add_argument("--text-part", default="/mnt/nli_mix/parts/text.jsonl", help="source of filler + pairs for the long haystack")
    # jevfmt
    ap.add_argument("--no-jevbench", action="store_true", help="leave the JevBench public items out (keeps them a clean eval)")
    ap.add_argument("--jevbench-repeat", type=int, default=8)
    ap.add_argument("--n-intent", type=int, default=8000)
    ap.add_argument("--n-tool", type=int, default=8000)
    ap.add_argument("--n-policy", type=int, default=6000)
    ap.add_argument("--n-ordinal", type=int, default=4000)
    ap.add_argument("--n-adequacy", type=int, default=8000)
    ap.add_argument("--n-adequacy-combo", type=int, default=12000)
    ap.add_argument("--n-mmlu", type=int, default=40000, help="MMLU auxiliary_train rows to take")
    ap.add_argument("--n-esci", type=int, default=30000)
    ap.add_argument("--n-ifcomplex", type=int, default=9000, help="prompts with 3-5 constraints; each gives ~8-10 rows per response")
    ap.add_argument("--if-gen", default="data/if_gen.jsonl", help="small-model responses from gen_if_responses.py")
    ap.add_argument("--n-temporal", type=int, default=16000)
    ap.add_argument("--n-multihop", type=int, default=14000)
    ap.add_argument("--n-longpolicy", type=int, default=9000)
    ap.add_argument("--n-routing", type=int, default=6000)
    ap.add_argument("--n-prob", type=int, default=6000)
    ap.add_argument("--ifollow-part", default=None, help="parts/ifollow.jsonl of the stage-1 mixture (adequacy rows)")
    # build
    ap.add_argument("--n-val", type=int, default=4000)
    ap.add_argument("--drop", default="xlam_underspec", help="comma-separated sources to exclude (xlam_underspec is mislabeled)")
    ap.add_argument("--cap-per-source", type=int, default=40000)
    ap.add_argument("--balance-ratio", type=float, default=1.15, help="cap per class = ratio x smallest class")
    ap.add_argument("--mix-in", default=None, help="build: also sample rows from another mixture dir (stage 2)")
    ap.add_argument("--mix-in-n", type=int, default=40000)
    ap.add_argument("--mix-in-quota", default="", help='e.g. "bullshit=16000,faith=20000,ifollow=20000,nli=30000"')
    ap.add_argument("--cap-prefixes", default="xlam", help="the per-source cap applies only to sources with these prefixes")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    {"text": build_text, "images": build_images, "agentic": build_agentic, "faith": build_faith,
     "ifollow": build_ifollow, "bullshit": build_bullshit, "jevfmt": build_jevfmt, "longdoc": build_longdoc,
     "agentic2": build_agentic2, "agentic_if": build_agentic_if, "agentic_distill": build_agentic_distill,
     "hardfmt": build_hardfmt, "ifcomplex": build_ifcomplex, "panel": build_panel, "build": build_final}[args.cmd](args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Minecraft long-horizon crafting (log -> ... -> iron pickaxe) played zero-shot by the NLI cross-encoder.

The model never outputs text: every decision is an entailment check over a text rendering of the game state.
Planners:
  flat   one argmax over all skills; each skill has a hypothesis (--hyp action|state), as in flappy.py / doom.py
  chain  the scaffold: backward chaining over the tech tree. Starting from the goal item, the model is asked state
         predicates ("The number of planks in the inventory is 3 or more." vs "... is less than 3.", ...); the first
         requirement it judges unsatisfied becomes the sub-goal, and a node whose requirements are all judged
         satisfied is executed. The tree (recipes) lives in the scaffold, all judgements about the state are the model's.
  oracle chain with ground-truth predicates; random = uniform over skills.
Envs: sim (symbolic inventory, for fast iteration) and mc (real Minecraft 1.20.4 through the mineflayer skill server mc_bot.js).

    python minecraft.py --env sim --planners random oracle flat chain --episodes 10
    node mc_bot.js &  python minecraft.py --env mc --planners chain --episodes 3 --out results/minecraft_4b.json
"""
import argparse
import json
import os
import random
import time
import urllib.request

import numpy as np
import torch

# requirement kinds: ("have", item, n) | ("near", station) | ("visible", block)
TREE = {
    "log":            {"skill": ("collect", "log"), "batch": 4, "reqs": [("visible", "log")]},
    "planks":         {"skill": ("craft", "planks"), "reqs": [("have", "log", 1)]},
    "stick":          {"skill": ("craft", "stick"), "reqs": [("have", "planks", 2)]},
    "crafting_table": {"skill": ("craft", "crafting_table"), "reqs": [("have", "planks", 4)]},
    "wooden_pickaxe": {"skill": ("craft", "wooden_pickaxe"), "reqs": [("have", "stick", 2), ("have", "planks", 3), ("near", "crafting_table")]},
    "cobblestone":    {"skill": ("collect", "stone"), "reqs": [("have", "wooden_pickaxe", 1), ("visible", "stone")]},
    "stone_pickaxe":  {"skill": ("craft", "stone_pickaxe"), "reqs": [("have", "stick", 2), ("have", "cobblestone", 3), ("near", "crafting_table")]},
    "furnace":        {"skill": ("craft", "furnace"), "reqs": [("have", "cobblestone", 8), ("near", "crafting_table")]},
    "raw_iron":       {"skill": ("collect", "iron_ore"), "reqs": [("have", "stone_pickaxe", 1), ("visible", "iron_ore")]},
    "iron_ingot":     {"skill": ("smelt", "raw_iron"), "reqs": [("have", "raw_iron", 3), ("have", "planks", 2), ("near", "furnace")]},
    "iron_pickaxe":   {"skill": ("craft", "iron_pickaxe"), "reqs": [("have", "iron_ingot", 3), ("have", "stick", 2), ("near", "crafting_table")]},
}
RECIPE_OUT = {"planks": 4, "stick": 4}
CONSUMES = {"planks": {"log": 1}, "stick": {"planks": 2}, "crafting_table": {"planks": 4}, "wooden_pickaxe": {"stick": 2, "planks": 3},
            "stone_pickaxe": {"stick": 2, "cobblestone": 3}, "furnace": {"cobblestone": 8}, "iron_pickaxe": {"iron_ingot": 3, "stick": 2}}
MILESTONES = list(TREE)
NAME = {"log": ("log", "logs"), "planks": ("plank", "planks"), "stick": ("stick", "sticks"), "crafting_table": ("crafting table", "crafting tables"),
        "wooden_pickaxe": ("wooden pickaxe", "wooden pickaxes"), "cobblestone": ("cobblestone block", "cobblestone blocks"), "stone_pickaxe": ("stone pickaxe", "stone pickaxes"),
        "furnace": ("furnace", "furnaces"), "raw_iron": ("raw iron chunk", "raw iron chunks"), "iron_ingot": ("iron ingot", "iron ingots"),
        "iron_pickaxe": ("iron pickaxe", "iron pickaxes"), "stone": ("stone", "stone"), "iron_ore": ("iron ore", "iron ore")}
nm = lambda item, n=1: NAME.get(item, (item.replace("_", " "),) * 2)[0 if n == 1 else 1]
VERB = {"collect": "mine", "craft": "craft", "smelt": "smelt", "place": "place"}

# skills = what the env executes; (skill, arg, n)
SKILLS = [TREE[i]["skill"] + (TREE[i].get("batch", 1),) for i in TREE] + [("place", "crafting_table", 1), ("place", "furnace", 1), ("explore", None, 1)]


def skill_text(sk):
    if sk[0] == "explore":
        return "walk away to explore a new area"
    if sk[0] == "collect":
        return f"mine {nm(sk[1])} blocks to get {nm(next(i for i in TREE if TREE[i]['skill'] == sk[:2]), 2)}"
    if sk[0] == "smelt":
        return f"smelt {nm(sk[1])} into iron ingots in the furnace"
    return f"{VERB[sk[0]]} {'' if sk[1] == 'planks' else ('an ' if nm(sk[1])[0] in 'aeiou' else 'a ')}{nm(sk[1], 2 if sk[1] == 'planks' else 1)}"


# ----------------------------------------------------------------------------- environments
class SimEnv:
    """Symbolic stand-in for mc_bot.js with the same state / result format."""

    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.reset()

    def reset(self):
        self.inv, self.near = {}, {"crafting_table": False, "furnace": False}
        self.visible = {"log": self.rng.random() < 0.8, "stone": self.rng.random() < 0.7, "iron_ore": self.rng.random() < 0.3}
        return self.state()

    def state(self):
        return {"inventory": {k: v for k, v in self.inv.items() if v > 0}, "near": dict(self.near), "visible": dict(self.visible), "pos": [0, 64, 0]}

    def act(self, sk):
        kind, arg, n = sk
        have = lambda i, k=1: self.inv.get(i, 0) >= k
        if kind == "explore":
            self.near = {k: False for k in self.near}
            self.visible = {"log": self.rng.random() < 0.8, "stone": self.rng.random() < 0.8, "iron_ore": self.rng.random() < 0.5}
            return {"ok": True, "msg": "walked 40 blocks"}
        if kind == "place":
            if not have(arg):
                return {"ok": False, "msg": f"no {arg} in the inventory"}
            self.inv[arg] -= 1; self.near[arg] = True
            return {"ok": True, "msg": f"placed {arg}"}
        item = next(i for i in TREE if TREE[i]["skill"] == (kind, arg))
        for r in TREE[item]["reqs"]:
            ok = have(r[1], r[2]) if r[0] == "have" else (self.near[r[1]] if r[0] == "near" else self.visible[r[1]])
            if not ok:
                return {"ok": False, "msg": f"cannot {VERB[kind]} {nm(arg)}: requirement not met ({r[0]} {nm(r[1])})"}
        if kind == "collect":
            self.inv[item] = self.inv.get(item, 0) + n
            return {"ok": True, "msg": f"collected {n} {item}"}
        if kind == "smelt":
            k = self.inv["raw_iron"]; self.inv["raw_iron"] = 0; self.inv["planks"] -= 2; self.inv["iron_ingot"] = self.inv.get("iron_ingot", 0) + k
            return {"ok": True, "msg": f"smelted {k} iron_ingot"}
        for i, k in CONSUMES[item].items():
            self.inv[i] -= k
        self.inv[item] = self.inv.get(item, 0) + RECIPE_OUT.get(item, 1)
        return {"ok": True, "msg": f"crafted {item}"}


class MineflayerEnv:
    def __init__(self, seed, url="http://127.0.0.1:3007"):
        self.url, self.rng = url, random.Random(seed * 7919 + 13)  # consecutive seeds give nearly the same first draw

    def _call(self, path, payload=None):
        req = urllib.request.Request(self.url + path, data=None if payload is None else json.dumps(payload).encode(), headers={"content-type": "application/json"})
        return json.loads(urllib.request.urlopen(req, timeout=300).read())

    def reset(self):
        print("reset:", self._call("/reset", {"x": self.rng.randrange(-3000, 3000), "z": self.rng.randrange(-3000, 3000)})["msg"], flush=True)
        return self.state()

    def state(self):
        return self._call("/state")

    def act(self, sk):
        r = self._call("/act", {"skill": sk[0], "arg": sk[1], "n": sk[2]})
        return {"ok": r["ok"], "msg": r["msg"]}


# ----------------------------------------------------------------------------- text
def render_state(s, goal=None, last=None, recipes=False):
    """Explicit zero counts and yes/no sentences: with a sparse "Inventory: 4 logs" the model hallucinates sticks (predicate acc 0.82 -> 0.98)."""
    inv = ", ".join(f"{s['inventory'].get(i, 0)} {nm(i, s['inventory'].get(i, 0))}" for i in TREE)
    near = " ".join(f"A placed {nm(k)} {'stands' if v else 'does not stand'} nearby." for k, v in s["near"].items())
    vis = " ".join(f"{nm(k).capitalize()} blocks {'are' if v else 'are not'} visible nearby." for k, v in s["visible"].items())
    t = "Minecraft survival. "
    if goal:
        t += f"The goal is to craft {'an' if nm(goal)[0] in 'aeiou' else 'a'} {nm(goal)}. "
    if recipes:
        t += ("Recipes: planks = 1 log; sticks = 2 planks; crafting table = 4 planks; wooden pickaxe = 3 planks + 2 sticks; stone pickaxe = 3 cobblestone + 2 sticks; "
              "furnace = 8 cobblestone; iron pickaxe = 3 iron ingots + 2 sticks. Pickaxes and the furnace are crafted at a placed crafting table. Stone needs a wooden pickaxe, "
              "iron ore needs a stone pickaxe, iron ingots are smelted from raw iron in a placed furnace with planks as fuel. ")
    t += f"Inventory counts: {inv}. {near} {vis}"
    if last:
        t += f" Last action: {last}"
    return t


def req_hyps(r, negated=False):
    """A predicate (or its negation) in several phrasings. The chain planner sums P(entailment) over the phrasings and compares the
    predicate with its negation instead of thresholding. One phrasing alone breaks on some inputs ("number ... is 8 or more" with 19)."""
    if r[0] == "have":
        i, n = r[1], r[2]
        return [f"The player has {'fewer than' if negated else 'at least'} {n} {nm(i, n)}.",
                f"The {nm(i)} count in the inventory is {'smaller than' if negated else 'greater than or equal to'} {n}.",
                f"The number of {nm(i, 2)} in the inventory is {'less than ' + str(n) if negated else str(n) + ' or more'}."]
    if r[0] == "near":
        return [f"The answer to whether a {nm(r[1])} is placed nearby is {'no' if negated else 'yes'}."]
    return [f"{'No' if negated else 'A'} {nm(r[1])} block is visible nearby."]


req_hyp = lambda r: req_hyps(r)[0]


def req_truth(r, s):
    return s["inventory"].get(r[1], 0) >= r[2] if r[0] == "have" else (s["near"][r[1]] if r[0] == "near" else s["visible"][r[1]])


def flat_hyp(sk, variant):
    if variant == "action":
        return f"The best next action is to {skill_text(sk)}."
    if sk[0] == "explore":
        return "None of the blocks the player needs are visible nearby."
    if sk[0] == "place":
        return f"The player has a {nm(sk[1])} in the inventory and no {nm(sk[1])} is placed nearby."
    item = next(i for i in TREE if TREE[i]["skill"] == sk[:2])
    have = " and ".join(req_hyp(r)[0].lower() + req_hyp(r)[1:-1] for r in TREE[item]["reqs"])
    return f"The player does not have {'any ' + nm(item, 2) if item in ('log', 'planks', 'stick', 'cobblestone', 'raw_iron', 'iron_ingot') else 'a ' + nm(item)} yet, and {have}."


# ----------------------------------------------------------------------------- model
class Scorer:
    def __init__(self, ckpt):
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(ckpt)
        self.model = AutoModelForSequenceClassification.from_pretrained(ckpt, dtype=torch.bfloat16).cuda().eval()
        self.template = getattr(self.model.config, "nli_template", None) or "Premise: {premise}\nHypothesis: {hypothesis}"
        if self.model.config.get_text_config().pad_token_id is None:
            self.model.config.get_text_config().pad_token_id = self.tok.pad_token_id
        self.tok.padding_side = "right"
        self.calls, self.secs = 0, 0.0

    @torch.no_grad()
    def probs(self, premise, hyps):
        """-> [len(hyps), 3] softmax over (contradiction, entailment, neutral)"""
        t0 = time.perf_counter()
        enc = self.tok([self.template.format(premise=premise, hypothesis=h) for h in hyps], truncation=True, max_length=512, padding=True, return_tensors="pt").to("cuda")
        p = torch.softmax(self.model(**enc).logits.float(), -1).cpu().numpy()
        self.calls += 1; self.secs += time.perf_counter() - t0
        return p


# ----------------------------------------------------------------------------- planners
class Chain:
    """Backward chaining; `judge(state, reqs, trace) -> [margin]` is the model (or ground truth for the oracle), margin > 0 = satisfied.

    Environment feedback: if the skill of a node just failed (state unchanged), the model must have been wrong about one of the
    requirements it accepted, so the least confident "yes" of that node is flipped (one more flip per repeated failure)."""

    def __init__(self, goal, judge):
        self.goal, self.judge, self.fails = goal, judge, {}

    def decide(self, s, trace, failed=()):
        self.fails = {k: v for k, v in self.fails.items() if k in failed}
        for sk in failed:
            self.fails.setdefault(sk, 0)
        trace.append({"node": "goal reached?"})
        if self.judge(s, [("have", self.goal, 1)], trace)[0] > 0:
            return None
        item, n = self.goal, 1
        for _ in range(12):
            trace.append({"node": item})
            reqs = TREE[item]["reqs"]
            m = list(self.judge(s, reqs, trace))
            sk = TREE[item]["skill"]
            sk = sk + (max(n, TREE[item].get("batch", 1)) if sk[0] == "collect" else 1,)
            if all(x > 0 for x in m) and sk in failed:
                self.fails[sk] += 1
                for k in np.argsort(m)[:self.fails[sk]]:
                    m[k] = -1.0
                    trace.append({"node": f"action failed -> doubting: {req_hyp(reqs[k])}"})
            miss = next((r for r, x in zip(reqs, m) if x <= 0), None)
            if miss is None:
                return sk
            if miss[0] == "visible":
                return ("explore", None, 1)
            if miss[0] == "near":
                trace.append({"node": "placed " + miss[1]})
                if self.judge(s, [("have", miss[1], 1)], trace)[0] > 0:
                    return ("place", miss[1], 1)
                item, n = miss[1], 1
            else:
                item, n = miss[1], miss[2]
        return ("explore", None, 1)


def make_planner(name, scorer, args, rng):
    goal = args.goal
    if name == "random":
        return lambda s, last, failed, trace: rng.choice(SKILLS)
    if name == "oracle":
        ch = Chain(goal, lambda s, reqs, trace: [1.0 if req_truth(r, s) else -1.0 for r in reqs])
        return lambda s, last, failed, trace: ch.decide(s, trace, failed)
    if name == "chain":
        def judge(s, reqs, trace):
            hyps, owner = [], []
            for k, r in enumerate(reqs):
                for sign, neg in ((1, False), (-1, True)):
                    for h in req_hyps(r, neg):
                        hyps.append(h); owner.append((k, sign / len(req_hyps(r))))
            p = scorer.probs(render_state(s), hyps)[:, 1]
            pos, neg = np.zeros(len(reqs)), np.zeros(len(reqs))
            for (k, w), pi in zip(owner, p):
                (pos if w > 0 else neg)[k] += abs(w) * pi
            margin = [float(a - b) if args.rule == "pair" else float(a - 0.5) for a, b in zip(pos, neg)]
            for r, a, b, mg in zip(reqs, pos, neg, margin):
                trace.append({"hyp": req_hyp(r), "p_ent": float(a), "p_ent_neg": float(b), "judged": mg > 0, "truth": bool(req_truth(r, s))})
            return margin
        ch = Chain(goal, judge)
        return lambda s, last, failed, trace: ch.decide(s, trace, failed)
    if name == "flat":
        hyps = [flat_hyp(sk, args.hyp) for sk in SKILLS]

        def flat(s, last, failed, trace):
            p = scorer.probs(render_state(s, goal=goal, last=last, recipes=True), hyps)[:, 1].copy()
            for sk, pi in zip(SKILLS, p):
                trace.append({"hyp": flat_hyp(sk, args.hyp), "p_ent": float(pi)})
            for i, sk in enumerate(SKILLS):  # scaffold: do not repeat a skill that failed since the state last changed
                if sk in failed:
                    p[i] = -1
            return SKILLS[int(p.argmax())]
        return flat
    raise ValueError(name)


def run_episode(env, planner, goal, max_steps, verbose=False):
    s = env.reset()
    reached, steps, failed, last, t0 = set(i for i in MILESTONES if s["inventory"].get(i, 0) > 0), [], set(), None, time.time()
    for t in range(max_steps):
        trace, ts = [], time.time()
        sk = planner(s, last, failed, trace)
        ts_act = time.time()
        if sk is None or s["inventory"].get(goal, 0) > 0:
            break
        r = env.act(sk)
        s2 = env.state()
        failed = failed | {sk} if (not r["ok"] and s2["inventory"] == s["inventory"] and s2["near"] == s["near"]) else set()
        last = f"{skill_text(sk)} - {'succeeded' if r['ok'] else 'failed'}: {r['msg']}."
        steps.append({"t": t, "state": s, "skill": list(sk), "ok": r["ok"], "msg": r["msg"], "trace": trace, "ts": ts, "ts_act": ts_act, "ts_end": time.time(), "state_after": s2})
        if verbose:
            print(f"  [{t:3d}] {skill_text(sk):55s} {'ok  ' if r['ok'] else 'FAIL'} {r['msg']}   inv={s2['inventory']}", flush=True)
        s = s2
        reached |= {i for i in MILESTONES if s["inventory"].get(i, 0) > 0} | {k for k, v in s["near"].items() if v}
    return {"success": s["inventory"].get(goal, 0) > 0, "milestones": [m for m in MILESTONES if m in reached], "n_steps": len(steps), "steps": steps,
            "final_inventory": s["inventory"], "seconds": time.time() - t0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="ckpt/qwen3.5-4b-nli")
    ap.add_argument("--env", default="sim", choices=["sim", "mc"])
    ap.add_argument("--planners", nargs="+", default=["random", "oracle", "flat", "chain"])
    ap.add_argument("--goal", default="iron_pickaxe", choices=list(TREE))
    ap.add_argument("--hyp", default="state", choices=["action", "state"], help="flat planner hypotheses")
    ap.add_argument("--rule", default="pair", choices=["pair", "threshold"], help="chain: predicate holds if P(ent) beats its negation / beats 0.5")
    ap.add_argument("--episodes", type=int, default=10)
    ap.add_argument("--max-steps", type=int, default=60)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/minecraft_4b.json")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    rng = random.Random(args.seed)
    scorer = Scorer(args.ckpt) if {"flat", "chain"} & set(args.planners) else None
    results, episodes = {}, {}
    for name in args.planners:
        planner = make_planner(name, scorer, args, rng)
        eps = []
        for e in range(args.episodes):
            env = SimEnv(args.seed + e) if args.env == "sim" else MineflayerEnv(args.seed + e)
            if args.verbose:
                print(f"== {name} episode {e}", flush=True)
            eps.append(run_episode(env, planner, args.goal, args.max_steps, args.verbose))
        judged = [j for ep in eps for st in ep["steps"] for j in st["trace"] if "truth" in j]
        results[name] = {"success_rate": float(np.mean([ep["success"] for ep in eps])), "mean_milestones": float(np.mean([len(ep["milestones"]) for ep in eps])),
                         "mean_steps": float(np.mean([ep["n_steps"] for ep in eps])), "mean_seconds": float(np.mean([ep["seconds"] for ep in eps])),
                         "predicate_acc": float(np.mean([j["judged"] == j["truth"] for j in judged])) if judged else None, "n_predicates": len(judged)}
        episodes[name] = eps
        r = results[name]
        print(f"{name:7s} success {r['success_rate']:.2f}  milestones {r['mean_milestones']:5.2f}/{len(MILESTONES)}  steps {r['mean_steps']:5.1f}"
              + (f"  predicate acc {r['predicate_acc']:.3f} ({r['n_predicates']})" if judged else ""), flush=True)
        for j in [j for j in judged if j["judged"] != j["truth"]][:8]:
            print(f"      wrong: {j['hyp']}  p_ent={j['p_ent']:.2f} truth={j['truth']}", flush=True)
    if scorer:
        print(f"model calls {scorer.calls}, {1000 * scorer.secs / max(1, scorer.calls):.0f} ms per call", flush=True)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump({"args": vars(args), "results": results, "episodes": episodes}, open(args.out, "w"), indent=1)


if __name__ == "__main__":
    main()

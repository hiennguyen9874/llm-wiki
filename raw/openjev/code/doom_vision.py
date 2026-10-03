#!/usr/bin/env python
"""Doom from pixels: the NLI-Qwen3.5-4B cross-encoder gets the game FRAME as the premise (image tokens through the
Qwen3.5 vision tower, untouched by the NLI fine-tune) and the three actions as text hypotheses. The oracle (labels
buffer) is used only to label training states for the latent + MLP head; the policy itself sees pixels only.

    python doom_vision.py --ckpt ckpt/qwen3.5-4b-nli --episodes 5 --out results/doom_vision_4b.json --video results/doom_vision_mlp.mp4
"""
import argparse
import json
import os
import random
import time

import numpy as np
import torch
from PIL import Image

import doom as D
from doom import ACTIONS, BUTTONS, oracle, parse_state, write_video
from latent_mlp import fit, predict, grouped_split

PREMISE = "Doom, Defend the Center, seen from the player's eyes: {img} You can only turn left, turn right, or fire the pistol; a shot hits only if an enemy is on the crosshair."

# zero-shot formulations: premise template (with {img}) and one hypothesis per action [turn left, turn right, attack]
ZS_VARIANTS = {
    "action": (PREMISE, ["The correct action is: turn left", "The correct action is: turn right", "The correct action is: attack"]),
    "should": (PREMISE, ["The marine should turn left.", "The marine should turn right.", "The marine should fire now."]),
    "where": ("A first-person Doom screenshot: {img}",
              ["There is an enemy on the left side of the screen.", "There is an enemy on the right side of the screen.",
               "There is an enemy in the centre of the screen, right on the crosshair."]),
    "where_closest": ("A first-person Doom screenshot: {img}",
                      ["The closest monster is to the left of the crosshair.", "The closest monster is to the right of the crosshair.",
                       "The closest monster is directly under the crosshair, in the middle of the screen."]),
    "where_plain": ("{img}", ["A monster on the left.", "A monster on the right.", "A monster in the middle of the picture."]),
    "danger": ("A first-person Doom screenshot: {img}",
               ["The nearest threat is on the left, the player must turn left to face it.",
                "The nearest threat is on the right, the player must turn right to face it.",
                "The nearest threat is straight ahead in the crosshair, the player must shoot."]),
    # precise position statements; the third element maps each hypothesis to an action index (0 left, 1 right, 2 attack)
    "precise": ("A first-person Doom screenshot, the crosshair is in the exact centre of the image: {img}",
                ["The nearest monster is far to the left of the crosshair.", "The nearest monster is slightly to the left of the crosshair.",
                 "The nearest monster is exactly under the crosshair, in the centre of the image.",
                 "The nearest monster is slightly to the right of the crosshair.", "The nearest monster is far to the right of the crosshair.",
                 "There is no monster anywhere in the image."], [0, 0, 2, 1, 1, 0]),
    "thirds": ("A first-person Doom screenshot: {img}",
               ["The monster is in the left third of the image.", "The monster is in the middle third of the image.",
                "The monster is in the right third of the image.", "The image shows an empty corridor with no monster."], [0, 2, 1, 0]),
    "pixels": ("A first-person Doom screenshot, 320 pixels wide, the crosshair at x = 160: {img}",
               ["The monster is at x < 100, on the left.", "The monster is around x = 130, a little left of centre.",
                "The monster is at x = 160, dead centre.", "The monster is around x = 190, a little right of centre.",
                "The monster is at x > 220, on the right.", "There is no monster in the image."], [0, 0, 2, 1, 1, 0]),
    "pixels_sym": ("A first-person Doom screenshot, 320 pixels wide, the crosshair at x = 160: {img}",
                   ["The monster is left of the crosshair, at x < 140.", "The monster is right of the crosshair, at x > 180.",
                    "The monster is at the crosshair, x = 160.", "There is no monster in the image."], [0, 1, 2, 0]),
    "pixels_pct": ("A first-person Doom screenshot, the crosshair is at the horizontal centre: {img}",
                   ["The monster is 30% of the screen width to the left of the crosshair.", "The monster is 10% of the screen width to the left of the crosshair.",
                    "The monster is at the crosshair, 0% off centre.", "The monster is 10% of the screen width to the right of the crosshair.",
                    "The monster is 30% of the screen width to the right of the crosshair.", "There is no monster in the image."], [0, 0, 2, 1, 1, 0]),
}
ZS_VARIANTS = {k: (v[0], v[1], v[2] if len(v) > 2 else [0, 1, 2]) for k, v in ZS_VARIANTS.items()}


class FastPatchEmbed(torch.nn.Module):
    """Qwen3.5 vision patch embed is a Conv3d with kernel == stride; cuDNN's bf16 path takes ~2 s,
    the fp32 conv takes 0.3 ms and is numerically closer to the reference. `weight` is kept bf16 because the caller
    reads `proj.weight.dtype` to cast its input."""

    def __init__(self, conv):
        super().__init__()
        self.weight, self.bias, self.stride = conv.weight, conv.bias, conv.stride

    def forward(self, x):
        y = torch.nn.functional.conv3d(x.float(), self.weight.float(), self.bias.float(), stride=self.stride)
        return y.to(self.weight.dtype)


class VisionScorer:
    def __init__(self, ckpt, image_size=(320, 240), variant="action"):
        self.premise, self.hyps, self.amap = ZS_VARIANTS[variant]
        from transformers import AutoImageProcessor, AutoModelForSequenceClassification, AutoTokenizer
        self.ip = AutoImageProcessor.from_pretrained("Qwen/Qwen3.5-4B")
        self.tok = AutoTokenizer.from_pretrained(ckpt)
        self.tok.padding_side = "right"
        self.model = AutoModelForSequenceClassification.from_pretrained(ckpt, dtype=torch.bfloat16).cuda().eval()
        self.model.config.get_text_config().pad_token_id = self.tok.pad_token_id
        self.model.model.visual.patch_embed.proj = FastPatchEmbed(self.model.model.visual.patch_embed.proj)
        self.template = self.model.config.nli_template
        self.img_id = self.tok.convert_tokens_to_ids("<|image_pad|>")
        self.image_size = image_size
        self.n_img_tokens = None

    def _prep(self, frame):
        img = Image.fromarray(frame).resize(self.image_size)
        vis = self.ip(images=[img], return_tensors="pt")
        n = int(vis["image_grid_thw"].prod()) // self.ip.merge_size ** 2
        return vis["pixel_values"], vis["image_grid_thw"], n

    def texts(self, n):
        img = "<|vision_start|>" + "<|image_pad|>" * n + "<|vision_end|>"
        return [self.template.format(premise=self.premise.format(img=img), hypothesis=h) for h in self.hyps]

    def set_variant(self, variant):
        self.premise, self.hyps, self.amap = ZS_VARIANTS[variant]

    def to_actions(self, p):
        """hypothesis scores -> (action, per-action score = max over that action's hypotheses)"""
        pa = np.array([max([p[i] for i, a in enumerate(self.amap) if a == j] or [0.0]) for j in range(3)])
        return int(self.amap[int(np.argmax(p))]), pa

    def batch_inputs(self, frames):
        """3 sequences per frame (one per action), each with its own copy of the image."""
        pvs, grids, n = [], [], None
        for f in frames:
            pv, grid, n = self._prep(f)
            pvs += [pv] * 3; grids += [grid] * 3
        enc = self.tok(self.texts(n) * len(frames), return_tensors="pt", padding=True)
        return {"input_ids": enc["input_ids"].cuda(), "attention_mask": enc["attention_mask"].cuda(),
                "mm_token_type_ids": (enc["input_ids"] == self.img_id).long().cuda(),
                "pixel_values": torch.cat(pvs).cuda(), "image_grid_thw": torch.cat(grids).cuda()}

    def finetune(self, frames, labels, epochs=2, lr=1e-4, bs=4, seed=0, r=16):
        """Train the cross-encoder itself (LoRA on the text backbone + the NLI head) with the 3-way NLI loss:
        the oracle action is 'entailment', the other two are 'contradiction'. No extra head."""
        from peft import LoraConfig, TaskType, get_peft_model
        lcfg = LoraConfig(task_type=TaskType.SEQ_CLS, r=r, lora_alpha=2 * r, lora_dropout=0.05,
                          target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj",
                                          "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b", "out_proj"],
                          modules_to_save=["score"])
        peft_model = get_peft_model(self.model, lcfg)
        for n_, p in peft_model.named_parameters():
            if "visual" in n_:
                p.requires_grad = False
        peft_model.print_trainable_parameters()
        rng = np.random.RandomState(seed)
        idx = rng.permutation(len(frames)); n_val = max(1, len(frames) // 10)
        val, tr = idx[:n_val], idx[n_val:]
        params = [p for p in peft_model.parameters() if p.requires_grad]
        opt = torch.optim.AdamW(params, lr=lr, weight_decay=0.01)
        total = epochs * ((len(tr) + bs - 1) // bs)
        sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda st: min(1.0, st / max(1, int(0.05 * total))) * max(0.0, 1 - st / total))
        ENT, CON = 1, 0
        step = 0
        for ep in range(epochs):
            rng.shuffle(tr)
            peft_model.train()
            for b in range(0, len(tr), bs):
                ids = tr[b:b + bs]
                inp = self.batch_inputs([frames[i] for i in ids])
                y = torch.tensor([ENT if j == labels[i] else CON for i in ids for j in range(3)], device="cuda")
                logits = peft_model(**inp).logits.float()
                loss = torch.nn.functional.cross_entropy(logits, y)
                loss.backward(); torch.nn.utils.clip_grad_norm_(params, 1.0); opt.step(); sched.step(); opt.zero_grad(); step += 1
                if step % 50 == 0:
                    print(f"  ep {ep} step {step}/{total} loss {loss.item():.3f}", flush=True)
            peft_model.eval()
            hits = 0
            with torch.no_grad():
                for b in range(0, len(val), 8):
                    ids = val[b:b + 8]
                    lg = peft_model(**self.batch_inputs([frames[i] for i in ids])).logits.float().view(len(ids), 3, 3)
                    hits += int((lg[:, :, ENT].argmax(-1).cpu().numpy() == np.array([labels[i] for i in ids])).sum())
            print(f"epoch {ep}: val agreement with oracle {hits / len(val):.3f}", flush=True)
        self.model = peft_model.merge_and_unload()
        self.model.eval()
        return hits / len(val)

    @torch.no_grad()
    def latents(self, frames):
        """One decision = 3 sequences (one per action) sharing the same image. Returns (X [3n, d], logits [3n, 3])."""
        X, L = [], []
        for f in frames:
            pv, grid, n = self._prep(f)
            k = len(self.hyps)
            enc = self.tok(self.texts(n), return_tensors="pt", padding=True)
            inp = {"input_ids": enc["input_ids"].cuda(), "attention_mask": enc["attention_mask"].cuda(),
                   "mm_token_type_ids": (enc["input_ids"] == self.img_id).long().cuda(),
                   "pixel_values": pv.repeat(k, 1).cuda(), "image_grid_thw": grid.repeat(k, 1).cuda()}
            h = self.model.model(**inp).last_hidden_state
            last = inp["attention_mask"].sum(1) - 1
            pooled = h[torch.arange(k, device=h.device), last]
            X.append(pooled.float().cpu().numpy()); L.append(self.model.score(pooled).float().cpu().numpy())
        return np.concatenate(X), np.concatenate(L)


def play(game, policy, seed, frame_skip, record=False):
    game.set_seed(seed); game.new_episode()
    frames, lats, steps = [], [], 0
    while not game.is_episode_finished():
        s = parse_state(game)
        if s is None:
            break
        t0 = time.perf_counter()
        a = policy(s)
        probs = None
        if isinstance(a, tuple):
            a, probs = a
        lats.append(time.perf_counter() - t0)
        if record:
            frames.append({"frame": s["frame"], "text": "[frame as image tokens] " + PREMISE.format(img="<image>"), "a": int(a),
                           "probs": None if probs is None else [float(p) for p in probs], "kills": s["kills"], "ammo": s["ammo"],
                           "health": s["health"], "lat_ms": lats[-1] * 1000})
        game.make_action(BUTTONS[a], frame_skip)
        steps += 1
    return {"kills": int(game.get_game_variable(D.vzd.GameVariable.KILLCOUNT)), "reward": game.get_total_reward(), "steps": steps,
            "lat_ms": float(np.mean(lats) * 1000) if lats else 0.0, "frames": frames}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="ckpt/qwen3.5-4b-nli")
    ap.add_argument("--episodes", type=int, default=5)
    ap.add_argument("--collect-episodes", type=int, default=12)
    ap.add_argument("--noise", type=float, default=0.2)
    ap.add_argument("--eps", type=float, default=0.1)
    ap.add_argument("--frame-skip", type=int, default=4, help="tics per decision; raise it if the model is slower than the budget")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/doom_vision_4b.json")
    ap.add_argument("--video", default=None)
    ap.add_argument("--video-nli", default=None)
    ap.add_argument("--mode", default="zeroshot", choices=["zeroshot", "finetune", "mlp"], help="zeroshot: no training at all, sweep formulations")
    ap.add_argument("--variants", nargs="+", default=list(ZS_VARIANTS))
    ap.add_argument("--calibrate", action="store_true", help="zero-shot with black-frame contrast calibration")
    ap.add_argument("--ft-epochs", type=int, default=2)
    ap.add_argument("--ft-lr", type=float, default=1e-4)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    game = D.make_game()
    results, replays = {}, {}

    def evaluate(name, policy, record=False):
        eps = [play(game, policy, 100 + i, args.frame_skip, record=record) for i in range(args.episodes)]
        k = [e["kills"] for e in eps]
        results[name] = {"mean_kills": float(np.mean(k)), "max_kills": int(max(k)), "mean_reward": float(np.mean([e["reward"] for e in eps])),
                         "mean_steps": float(np.mean([e["steps"] for e in eps])), "lat_ms": float(np.mean([e["lat_ms"] for e in eps]))}
        if record:
            replays[name] = max(eps, key=lambda e: e["kills"])["frames"]
        print(f"{name:8s} kills mean {np.mean(k):5.2f} max {max(k):2d}  reward {np.mean([e['reward'] for e in eps]):6.1f}  "
              f"steps {np.mean([e['steps'] for e in eps]):6.1f}  latency {results[name]['lat_ms']:.1f} ms", flush=True)

    evaluate("random", lambda s: rng.randrange(3))
    evaluate("oracle", oracle)
    scorer = VisionScorer(args.ckpt)

    def nli_policy(s):
        _, L = scorer.latents([s["frame"]])
        p = torch.softmax(torch.tensor(L), -1).numpy()[:, 1]
        return scorer.to_actions(p)

    def calibrated_policy(s):
        """zero-shot, contrast-calibrated: P(ent | frame, h) - P(ent | black frame, h) removes the head's action prior."""
        _, L = scorer.latents([s["frame"], np.zeros_like(s["frame"])])
        p = torch.softmax(torch.tensor(L), -1).numpy()[:, 1]
        k = len(scorer.hyps)
        d = p[:k] - p[k:]
        return scorer.to_actions(d - d.min() + 1e-3)

    if args.mode == "zeroshot":
        best = None
        for v in args.variants:
            scorer.set_variant(v)
            pol = calibrated_policy if args.calibrate else nli_policy
            evaluate(f"nli_{v}", pol, record=True)
            frames_v = replays.pop(f"nli_{v}")
            results[f"nli_{v}"]["premise"], results[f"nli_{v}"]["hypotheses"], results[f"nli_{v}"]["action_map"] = ZS_VARIANTS[v]
            # action distribution of the policy
            acts = np.bincount([f["a"] for f in frames_v], minlength=3) / max(1, len(frames_v))
            results[f"nli_{v}"]["action_dist"] = acts.tolist()
            print(f"    action dist {acts.round(2)}", flush=True)
            if best is None or results[f"nli_{v}"]["mean_kills"] > results[best[0]]["mean_kills"]:
                best = (f"nli_{v}", frames_v)
        game.close()
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        json.dump({"args": vars(args), "results": results}, open(args.out, "w"), indent=2)
        print("best variant:", best[0])
        if args.video:
            for f in best[1]:
                f["text"] = "[frame] premise: " + results[best[0]]["premise"].replace("{img}", "<image>") + "\nhypotheses: " + " | ".join(results[best[0]]["hypotheses"])
            write_video(best[1], args.video, "nli")
        return
    evaluate("nli", nli_policy, record=bool(args.video_nli))

    # training states from noisy-oracle rollouts: labels from the labels buffer, inputs = frames
    frames, labels = [], []
    for i in range(args.collect_episodes):
        game.set_seed(i); game.new_episode()
        while not game.is_episode_finished():
            s = parse_state(game)
            if s is None:
                break
            a_or = oracle(s)
            frames.append(s["frame"]); labels.append(a_or)
            a = rng.randrange(3) if rng.random() < args.noise else a_or
            game.make_action(BUTTONS[a], args.frame_skip)
    print(f"collected {len(frames)} frames; action dist {np.bincount(labels, minlength=3) / len(labels)}", flush=True)
    if args.mode == "finetune":
        results["ft_val_acc"] = scorer.finetune(frames, labels, epochs=args.ft_epochs, lr=args.ft_lr, seed=args.seed)
        evaluate("ft", nli_policy, record=bool(args.video))  # same zero-shot policy, fine-tuned weights, no extra head
        game.close()
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        json.dump({"args": vars(args), "results": results}, open(args.out, "w"), indent=2)
        for name, path in [("ft", args.video), ("nli", args.video_nli)]:
            if path and name in replays:
                write_video(replays[name], path, name)
        return
    t0 = time.time()
    X, _ = scorer.latents(frames)
    print(f"latents {X.shape} in {time.time()-t0:.0f}s", flush=True)
    qid = np.repeat(np.arange(len(frames)), 3)
    gold = np.array([[int(j == l) for j in range(3)] for l in labels]).ravel()
    tr, va = grouped_split(qid, 0.1, args.seed)
    ns = argparse.Namespace(hidden=512, dropout=0.1, lr=1e-3, wd=1e-2, bs=512, epochs=60, patience=8, eps=args.eps, seed=args.seed)
    model, stats, va_acc, _ = fit(X[tr], gold[tr], qid[tr], X[va], gold[va], qid[va], ns)
    print(f"mlp val agreement with oracle: {va_acc:.3f}", flush=True)
    results["mlp_val_acc"] = va_acc

    def mlp_policy(s):
        Xs, _ = scorer.latents([s["frame"]])
        z = predict(model, stats, Xs)
        return int(z.argmax()), 1 / (1 + np.exp(-z))
    evaluate("mlp", mlp_policy, record=bool(args.video))
    game.close()
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump({"args": vars(args), "results": results}, open(args.out, "w"), indent=2)
    for name, path in [("mlp", args.video), ("nli", args.video_nli)]:
        if path and name in replays:
            write_video(replays[name], path, name)


if __name__ == "__main__":
    main()

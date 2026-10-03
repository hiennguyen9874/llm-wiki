"""Client for an openjev checkpoint served by SGLang (serve_sglang.sh). Same interface as
`OpenJevCrossEncoder.predict/rerank`, plus `--check` to compare the server against transformers.

    python sglang_client.py --premise "A man is playing a guitar." --hypothesis "Someone is making music."
    python sglang_client.py --check ckpt/qwen3.5-0.8b-nli-v2s-long        # max |p_sglang - p_hf| on a few pairs
"""
from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import requests

CON, ENT, NEU = 0, 1, 2
LABELS = ["contradiction", "entailment", "neutral"]
DEFAULT_TEMPLATE = "Premise: {premise}\nHypothesis: {hypothesis}"
IMG_MARK = "<<IMG>>"
IMG_BLOCK = "<|vision_start|><|image_pad|><|vision_end|>"  # SGLang expands the single pad to the patch count


class OpenJevSGLang:
    def __init__(self, url: str = "http://127.0.0.1:30000", template: str = DEFAULT_TEMPLATE, bs: int = 32,
                 workers: int = 16):
        # `workers` requests of `bs` pairs are in flight at once; the server batches across them
        self.url, self.template, self.bs, self.workers = url.rstrip("/"), template, bs, workers

    def _post(self, payload):
        r = requests.post(f"{self.url}/classify", json=payload, timeout=600)
        r.raise_for_status()
        out = r.json()
        return [o["embedding"] for o in (out if isinstance(out, list) else [out])]

    def logits(self, pairs, images=None) -> np.ndarray:
        """Raw [contradiction, entailment, neutral] logits. `images[i]` is a path / URL / bytes or None and is
        spliced into premise i at the `<<IMG>>` marker (appended if the marker is absent)."""
        payloads = []
        for i in range(0, len(pairs), self.bs):
            texts, imgs = [], []
            for j, (p, h) in enumerate(pairs[i:i + self.bs]):
                img = images[i + j] if images else None
                if img is not None:
                    p = p.replace(IMG_MARK, IMG_BLOCK) if IMG_MARK in p else f"{p.rstrip()} {IMG_BLOCK}"
                    img = base64.b64encode(img).decode() if isinstance(img, bytes) else img
                texts.append(self.template.format(premise=p.strip(), hypothesis=h.strip()))
                imgs.append(img)
            payload = {"text": texts}
            if any(x is not None for x in imgs):
                payload["image_data"] = imgs
            payloads.append(payload)
        with ThreadPoolExecutor(self.workers) as ex:
            out = [z for part in ex.map(self._post, payloads) for z in part]
        return np.asarray(out, np.float32)

    def predict(self, pairs, images=None) -> np.ndarray:
        """Softmax probabilities [contradiction, entailment, neutral] per pair."""
        z = self.logits(pairs, images)
        z = np.exp(z - z.max(-1, keepdims=True))
        return z / z.sum(-1, keepdims=True)

    def rerank(self, question: str, options, hyp_fmt: str = "The correct answer is: {}") -> int:
        return int(self.predict([(question, hyp_fmt.format(o)) for o in options])[:, ENT].argmax())


CHECK_PAIRS = [
    ("A man is playing a guitar.", "Someone is making music."),
    ("A man is playing a guitar.", "The man is asleep."),
    ("A man is playing a guitar.", "The man is a professional musician."),
    ("The Eiffel Tower is in Paris. " * 40, "The Eiffel Tower is in Berlin."),
    ("What is the capital of France?", "The correct answer is: Paris"),
]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:30000")
    ap.add_argument("--premise")
    ap.add_argument("--hypothesis")
    ap.add_argument("--image")
    ap.add_argument("--check", metavar="CKPT", help="compare against transformers on this checkpoint")
    a = ap.parse_args()
    client = OpenJevSGLang(a.url)
    if a.check:
        from modeling_openjev import OpenJevCrossEncoder

        ours, ref = client.predict(CHECK_PAIRS), OpenJevCrossEncoder(a.check).predict(CHECK_PAIRS)
        for (p, h), x, y in zip(CHECK_PAIRS, ours, ref):
            print(f"{h[:50]:52s} sglang {np.round(x, 4)}  hf {np.round(y, 4)}")
        print("max abs diff:", float(np.abs(ours - ref).max()), "| argmax agree:", bool((ours.argmax(1) == ref.argmax(1)).all()))
    else:
        p = client.predict([(a.premise, a.hypothesis)], [a.image] if a.image else None)[0]
        print({l: round(float(v), 4) for l, v in zip(LABELS, p)})

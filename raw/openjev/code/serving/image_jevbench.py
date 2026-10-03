"""Image JevBench bridge and reproducible public-example runner.

The published benchmark runner/sealed corpus are not in the public repository.
This bridge consumes its public example schema without passing alt text or gold
to inference. Output probabilities are explicitly normalized NLI entailment,
not calibrated forecasts. No temperature is fitted on benchmark examples.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import time

import httpx
import numpy as np


class OpenJevImageAdapter:
    def __init__(self, endpoint, model, timeout=180):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.client = httpx.Client(timeout=timeout)

    def close(self):
        self.client.close()

    def build_request(self, item, image_bytes):
        options = item["options"]
        criteria = {o["label"]: o["text"] for o in options}
        if not criteria or len(criteria) != len(options):
            raise ValueError("Options must have unique labels")
        return {"model": self.model, "state": "An image: <<IMG>>",
                "image_data": base64.b64encode(image_bytes).decode("ascii"),
                "questions": {"decision": {"type": "choice", "instructions": item["question"],
                                             "criteria": criteria}}}

    def run(self, item, image_bytes):
        body = self.build_request(item, image_bytes)
        start = time.perf_counter()
        r = self.client.post(self.endpoint + "/v1/systemone", json=body)
        latency = time.perf_counter() - start
        r.raise_for_status()
        raw = r.json()
        answer = raw["answers"]["decision"]
        p = answer["probabilities"]
        labels = list(body["questions"]["decision"]["criteria"])
        if set(p) != set(labels) or any(isinstance(v, bool) or not isinstance(v, (int, float))
                                      or not math.isfinite(v) or not 0 <= v <= 1 for v in p.values()):
            raise ValueError("Invalid categorical probabilities")
        total = sum(p.values())
        if abs(total - 1) > 0.005:
            raise ValueError("Probabilities do not sum to one")
        # Remove API decimal rounding error, preserving score order.
        p = {label: p[label] / total for label in labels}
        choice = answer["choice"]
        if choice not in p or p[choice] < max(p.values()):
            raise ValueError("Choice disagrees with distribution")
        return {"id": item.get("sourceItemId", item.get("key")), "choice": choice,
                "probabilities": p, "probability_method": raw.get("probability_method", "unknown"),
                "latency_s": latency, "image_sha256": hashlib.sha256(image_bytes).hexdigest(),
                "request_sha256": hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest(),
                "raw": raw}


def summarize(rows):
    good = [r for r in rows if "probabilities" in r]
    labelled = [r for r in good if r.get("gold") is not None]
    result = {"attempted": len(rows), "completed": len(good), "errors": len(rows)-len(good),
              "scope": "published resized public examples only; not the full benchmark",
              "probability_method": "normalized_entailment_v1; no fitted calibration",
              "cost": None}
    if good:
        result.update({"p50_s": float(np.percentile([r["latency_s"] for r in good], 50)),
                       "p95_s": float(np.percentile([r["latency_s"] for r in good], 95))})
    if labelled:
        correct = [r["choice"] == r["gold"] for r in labelled]
        conf = [r["probabilities"][r["choice"]] for r in labelled]
        ece = 0.0
        for i in range(10):
            indices = [j for j, c in enumerate(conf) if min(int(c*10), 9) == i]
            if indices:
                ece += abs(sum(conf[j] - correct[j] for j in indices)) / len(labelled)
        result.update({"scored": len(labelled), "correct": sum(correct), "accuracy": sum(correct)/len(labelled),
                       "top_label_ece_10_bins": ece,
                       "brier_multiclass": float(np.mean([sum((p-(k==r["gold"]))**2
                           for k, p in r["probabilities"].items()) for r in labelled]))})
    return result


def main():
    ap = argparse.ArgumentParser(__doc__)
    ap.add_argument("--items", type=Path, required=True, help="JSON array exported from PUBLIC_IMAGE_JEV_EXAMPLES")
    ap.add_argument("--assets-root", type=Path, required=True, help="Repository public/ directory")
    ap.add_argument("--endpoint", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    items = json.loads(args.items.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    adapter = OpenJevImageAdapter(args.endpoint, args.model)
    rows = []
    try:
        with (args.output / "predictions.jsonl").open("x") as f:
            for item in items:
                try:
                    root = args.assets_root.resolve()
                    path = (root / item["image"].lstrip("/")).resolve()
                    if not path.is_relative_to(root):
                        raise ValueError("Image escapes assets root")
                    row = adapter.run(item, path.read_bytes())
                    row["gold"] = item.get("correctLabel")
                    if row["gold"] is not None and row["gold"] not in row["probabilities"]:
                        raise ValueError("Gold is not an option")
                except Exception as e:
                    row = {"id": item.get("sourceItemId", item.get("key")), "error": str(e)}
                rows.append(row)
                f.write(json.dumps(row) + "\n")
                f.flush()
                print(json.dumps({k: v for k, v in row.items() if k != "raw"}), flush=True)
    finally:
        adapter.close()
    report = summarize(rows)
    (args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if report["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

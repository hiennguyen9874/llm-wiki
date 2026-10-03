"""Create a serving overlay without modifying the training checkpoint."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("checkpoint", type=Path)
ap.add_argument("destination", type=Path)
ap.add_argument("--base-size", choices=["4B", "0.8B"], default="4B")
a = ap.parse_args()
source, dest = a.checkpoint.resolve(), a.destination.resolve()
if source == dest:
    ap.error("destination must differ from checkpoint")
if not (source / "config.json").is_file():
    ap.error("checkpoint has no config.json")
dest.mkdir(parents=True, exist_ok=True)
for p in source.iterdir():
    target = dest / p.name
    if target.exists() or target.is_symlink():
        if target.resolve() != p.resolve():
            raise FileExistsError(target)
    else:
        target.symlink_to(p)

repo = f"Qwen/Qwen3.5-{a.base_size}"
revision = {"4B": "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a",
            "0.8B": "2fc06364715b967f1860aea9cf38778875588b17"}[a.base_size]
hashes = {
    "preprocessor_config.json": "27225450ac9c6529872ee1924fcb0962ff5634834f817040f444118116f4e516",
    "video_preprocessor_config.json": "7768af27c1fafa9cc9011c1dc20067e03f8915e03b63504550e11d5066986d13",
}
added = {}
for name, expected in hashes.items():
    target = dest / name
    if target.is_symlink():
        continue  # Keep any processor already supplied with the checkpoint.
    url = f"https://huggingface.co/{repo}/resolve/{revision}/{name}"
    data = target.read_bytes() if target.exists() else urllib.request.urlopen(url, timeout=60).read()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"Unexpected processor contents: {name}")
    target.write_bytes(data)
    added[name] = expected
(dest / "SERVING_SOURCE.json").write_text(json.dumps(dict(
    checkpoint=str(source), processor_repo=repo,
    processor_revision=revision, added_sha256=added), indent=2) + "\n")
print(dest)

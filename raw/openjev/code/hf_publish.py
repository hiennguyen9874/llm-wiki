#!/usr/bin/env python
"""Publish checkpoints / model card / results to the HF Hub repo. Token from HF_TOKEN env (never written to disk here).
    HF_TOKEN=... python hf_publish.py --repo AlexWortega/openjev --ckpt ckpt/qwen3.5-4b-nli --subdir qwen3.5-4b-nli
    HF_TOKEN=... python hf_publish.py --repo AlexWortega/openjev --files README.md results/*.json results/*.mp4 assets/*.png
"""
import argparse, glob, os
from huggingface_hub import HfApi

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="AlexWortega/openjev")
ap.add_argument("--ckpt", default=None)
ap.add_argument("--subdir", default=None, help="path in repo for the checkpoint (default: root)")
ap.add_argument("--files", nargs="*", default=[])
ap.add_argument("--dest", default="", help="repo folder for --files")
args = ap.parse_args()
api = HfApi(token=os.environ["HF_TOKEN"])
api.create_repo(args.repo, repo_type="model", exist_ok=True)
if args.ckpt:
    api.upload_folder(folder_path=args.ckpt, repo_id=args.repo, path_in_repo=args.subdir or "", repo_type="model",
                      ignore_patterns=["*_trainer/*", "checkpoint-*"], commit_message=f"upload {os.path.basename(args.ckpt)}")
    print("uploaded", args.ckpt)
for pat in args.files:
    for f in glob.glob(pat):
        api.upload_file(path_or_fileobj=f, path_in_repo=os.path.join(args.dest, os.path.basename(f)) if args.dest else os.path.basename(f) if not f.startswith("results/") else f,
                        repo_id=args.repo, repo_type="model", commit_message=f"add {f}")
        print("uploaded", f)

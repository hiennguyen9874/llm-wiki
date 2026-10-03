"""Install NVIDIA's CUDA compiler redistributables into a private directory.

No driver/system modifications. Archives are hash-verified against NVIDIA's
versioned redistribution manifest before extraction.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("--version", default="12.6.3")
a = ap.parse_args()
root = Path(a.root).resolve()
root.mkdir(parents=True, exist_ok=True)
url = "https://developer.download.nvidia.com/compute/cuda/redist/"
manifest = json.load(urllib.request.urlopen(url + f"redistrib_{a.version}.json"))
archives = root.parent / "cuda_archives"
archives.mkdir(exist_ok=True)
for package in ("cuda_nvcc", "cuda_cudart", "cuda_cccl", "cuda_nvrtc"):
    info = manifest[package]["linux-x86_64"]
    archive = archives / Path(info["relative_path"]).name
    if not archive.exists():
        urllib.request.urlretrieve(url + info["relative_path"], archive)
    if hashlib.file_digest(archive.open("rb"), "sha256").hexdigest() != info["sha256"]:
        raise RuntimeError(f"Checksum mismatch: {archive}")
    with tarfile.open(archive) as source:
        for member in source.getmembers():
            parts = Path(member.name).parts
            if len(parts) < 2:
                continue
            member.name = str(Path(*parts[1:]))
            source.extract(member, path=root, filter="data")
    print(f"Installed {package}: {info['sha256']}", flush=True)
(root / f"redistrib_{a.version}.json").write_text(json.dumps(manifest, indent=2))
lib64 = root / "lib64"
if not lib64.exists():
    lib64.symlink_to("lib", target_is_directory=True)

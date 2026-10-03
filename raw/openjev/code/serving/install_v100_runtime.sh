#!/usr/bin/env bash
# Run after the isolated torch environment and prepare_v100_cuda.py complete.
# Builds a Volta-compatible SGLang runtime for the unchanged HF OpenJEV adapter.
set -euo pipefail
OPENJEV_V100_ROOT=${OPENJEV_V100_ROOT:-$HOME/storage/sglang-openjev-v100}
export PIP_CONFIG_FILE=/dev/null PIP_EXTRA_INDEX_URL=
export PIP_CACHE_DIR="$OPENJEV_V100_ROOT/cache" TMPDIR="$OPENJEV_V100_ROOT/tmp"
export CUDA_HOME="$OPENJEV_V100_ROOT/cuda126"
export CUDACXX="$CUDA_HOME/bin/nvcc" CUDAToolkit_ROOT="$CUDA_HOME"
export PATH="$OPENJEV_V100_ROOT/venv/bin:$OPENJEV_V100_ROOT/protoc/bin:$CUDA_HOME/bin:$HOME/.cargo/bin:$PATH"
export CARGO_HOME="$OPENJEV_V100_ROOT/cargo"
export CARGO_TARGET_DIR="$OPENJEV_V100_ROOT/cargo_target"
export RUSTUP_HOME="$OPENJEV_V100_ROOT/rustup"
export TORCH_EXTENSIONS_DIR="$OPENJEV_V100_ROOT/torch_extensions"
export TRITON_CACHE_DIR="$OPENJEV_V100_ROOT/triton"
export MAX_JOBS=8 CMAKE_BUILD_PARALLEL_LEVEL=8 NVCC_THREADS=1 TORCH_CUDA_ARCH_LIST=7.0
export OPENJEV_V100_ROOT
if [[ ${1:-all} != kernel ]]; then
python - <<'PY'
import torch
print('torch', torch.__version__, 'CUDA', torch.version.cuda, 'arches', torch.cuda.get_arch_list(), flush=True)
assert 'sm_70' in torch.cuda.get_arch_list(), 'PyTorch wheel lacks V100 support'
x = torch.ones((16, 16), device='cuda', dtype=torch.float16)
assert (x @ x).float().mean().item() == 16
print('V100 FP16 CUDA smoke: PASS', flush=True)
PY
python -m pip install --index-url https://pypi.org/simple cmake ninja scikit-build-core setuptools wheel setuptools-scm setuptools-rust packaging psutil
python - <<'PY'
import os, tomllib
from pathlib import Path
from packaging.requirements import Requirement
root=Path(os.environ['OPENJEV_V100_ROOT'])
project=tomllib.loads((root/'runtime/python/pyproject.toml').read_text())['project']
# The source-built SM70 packages replace the stock GPU wheels. Audio/diffusion
# components are not needed for this text classification checkpoint.
exclude={'torch','torchvision','torchaudio','torchcodec','flashinfer-python','flashinfer-cubin','sglang-kernel'}
deps=[s for s in project['dependencies'] if Requirement(s).name.lower().replace('_','-') not in exclude]
deps += ['tilelang==0.1.8', 'grpcio==1.81.1', 'grpcio-health-checking==1.81.1', 'grpcio-reflection==1.81.1', 'protobuf==6.33.6']
(root/'requirements.txt').write_text('\n'.join(deps)+'\n')
(root/'constraints.txt').write_text('torch==2.9.1+cu126\ntorchvision==0.24.1+cu126\nnvidia-nccl-cu12==2.27.5\n')
PY
python -m pip install --index-url https://pypi.org/simple -c "$OPENJEV_V100_ROOT/constraints.txt" -r "$OPENJEV_V100_ROOT/requirements.txt"
python -m pip install --no-deps -e "$OPENJEV_V100_ROOT/runtime/python"
python -m pip install --no-deps --no-build-isolation -e "$OPENJEV_V100_ROOT/flashinfer"
fi
# CMake's Torch discovery expects CUDA library targets under CUDA_HOME. Reuse
# this venv's NVIDIA wheels; no host CUDA installation is modified.
python - <<'PY'
import os, site
from pathlib import Path
root=Path(os.environ['OPENJEV_V100_ROOT'])
cuda=root/'cuda126'
for site_dir in site.getsitepackages():
    for package in (Path(site_dir)/'nvidia').glob('*'):
        for folder in ('lib','include'):
            source=package/folder
            if not source.is_dir(): continue
            dest=cuda/folder
            dest.mkdir(exist_ok=True)
            for item in source.iterdir():
                target=dest/item.name
                if not target.exists() and not target.is_symlink():
                    target.symlink_to(item)
PY
export CMAKE_ARGS="-DSGL_KERNEL_V100_ONLY=ON -DSGL_KERNEL_COMPILE_THREADS=1 -DCMAKE_CUDA_COMPILER=$CUDACXX -DCUDAToolkit_ROOT=$CUDA_HOME -DCUDA_TOOLKIT_ROOT_DIR=$CUDA_HOME"
python -m pip install --no-deps --no-build-isolation --config-settings="build-dir=$OPENJEV_V100_ROOT/build_sgl_kernel" "$OPENJEV_V100_ROOT/runtime/sgl-kernel"
python - <<'PY'
import torch, sglang, sgl_kernel
print('runtime ready', torch.__version__, sglang.__version__, sgl_kernel.common_ops.__file__, flush=True)
assert '/sm70/' in sgl_kernel.common_ops.__file__
PY

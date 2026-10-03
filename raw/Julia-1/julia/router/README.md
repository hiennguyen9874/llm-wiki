# Julia router

Resident inference for Julia on **CPU or CUDA**, located in the existing `julia`
package. No separate repository. Python loads Bend-generated C with `ctypes`;
there is no compiler or subprocess in the request path.

## Build and use

From the **Julia-1** directory (the outer workspace also has an older package
named `julia`, so running there can import the wrong one):

```bash
python -m pip install -e .
python -m julia.router.build --bend /home/klee/.bend/bin/bend
```

The native build requires Bend **2.0.27**, Clang, and Linux. It checks `native/PROOF.bend`, generated
function arities, and the borrowed-tree contract before compiling. `--native-cpu`
adds host-specific machine instructions; use that build only on compatible CPUs. The bridge
uses private Bend runtime internals, so upgrading Bend requires adapting and
retesting the bridge. `--output` selects another library location; pass that
path as `library=` or set `JULIA_ROUTER_LIBRARY` at runtime.

```python
from julia.router import FastEngine

engine = FastEngine('/path/to/real/checkpoint', device='cpu', batch_size=16)
# device='cuda' uses CUDA/BF16 and device-side softmax/argmax.
rows = [{
    'state': 'Preciso trocar minha senha.',
    'question': 'Qual é a intenção?',
    'options': ['Redefinir senha', 'Cancelar conta', 'Consultar saldo'],
}]
print(engine.predict(rows))
print(engine.predict(rows, probabilities=False))  # return only indices
```

Use real checkpoint files, not Git LFS pointer files. The 2026-09-23 runtime audit
loaded the actual 551 MiB checkpoint offline and exercised resident inference.

## Faster inference path

- Bounded LRU caches reuse token fragments and full request encodings. Model
  forward passes still run on **every request**; no answer cache inflates timings.
- Sort by encoded length before bounded microbatches, then restore request order.
  This reduces padding on mixed-length inputs; it does not guarantee a speedup
  for every batch or request size.
- Build one NumPy arena for integer inputs, with zero-copy CPU tensor views.
  CUDA uses two pinned bulk transfers instead of per-field transfers.
- Softmax and argmax run on the model's device. CUDA does not copy hidden states
  or attention matrices into CPU Bend kernels.
- `compile_model=True` enables optional `torch.compile(dynamic=True)`. Compilation
  adds first-call cost and requires validation on the target device.
- CPU inference retains private file-backed safetensors storage instead of copying
  the full vocabulary embedding into anonymous RAM. Keep checkpoint files immutable
  while loaded; use `memory_map=False` for a detached copy. Training model loading
  still copies by default.
- CPU PyTorch heads compute only option queries and feed-forward outputs in the
  final layer. Full context keys/values are retained. `marker_only_head=False`
  selects the original path; training and the separate experimental Bend normalization head use the original
  path automatically. CUDA retains the original default until hardware validation.
- `strict_encoding=True` rejects marker injection and any question/option/state
  truncation. `encoding_info(rows)` audits the same cached encoding used in inference;
  the game worker no longer tokenizes each request twice.
- Preserve Julia's original marker serialization, truncation, weights, and
  option order. Returned probabilities use the model card presentation rules;
`logits()` retains raw scores.

CPU defaults to Python/PyTorch (`torch`), with no Bend build required. CUDA also
uses PyTorch. Select `transformer_backend='bend-dense'` explicitly to use the
optional CPU FP32 Bend encoder. `compile_model=True` works with the default Torch
backend.

## Bend transformer operations

`native/router.bend` implements candidate argmax, numerically stabilized softmax,
and two-pass LayerNorm (mean, centered variance, affine scale/bias). Balanced
`Leaf`/`Fork` trees expose candidate reductions. LayerNorm forks over independent
rows and uses flat tail loops over feature lists within each row, following the
Bend guide's coarse-work/flat-leaf cost model. All use Bend's own heap. The C adapter transports arrays and owns the ABI; it does
not duplicate the numerical algorithms.

```python
from julia.router import BendReducer, FastEngine

bend = BendReducer()
index, probabilities = bend.softmax([1.0, 3.0, -2.0])
normalized = bend.layernorm([[1.0, 2.0, 3.0]])

# Explicit experimental CPU transformer-head backend:
engine = FastEngine('/path/to/checkpoint', device='cpu',
                    transformer_backend='bend', bend_postprocess=True)

# All 88 encoder projections of the real checkpoint also execute in Bend:
# Set JULIA_BEND_THREADS=4 before creating the engine.
engine = FastEngine('/path/to/checkpoint', device='cpu',
                    transformer_backend='bend-dense', bend_postprocess=True)
```

The experimental head executes its pre-attention and pre-MLP LayerNorms, plus
scorer LayerNorm, in Bend. Dense projections, attention, and the encoder remain
PyTorch. This is **not a complete transformer rewrite in Bend**. Bend head math
is inference-only CPU float32. The CPU library defaults to up to eight available Bend runtime
workers. Set `JULIA_BEND_THREADS=4` **before the first native call** to test row
parallelism; the worker count is fixed for the process. Pool sizing depends on the kernel and workload; the older normalization-only
experiment does not determine the dense backend defaults. Reduction order differs from the
old tree algorithm and PyTorch: probabilities can differ by floating-point rounding,
and effectively tied choices may choose a different index.
Calls share a mutex because Bend's runtime has global state. Instantiate model
workers in spawned processes; do not fork an active inference process.

### Resident dense projections (CPU default)

`bend-dense` executes all 88 encoder projections in Bend. Resident packed FP32
arrays replace linked weight trees. Contiguous 8×8 tiles expose vector arithmetic;
coarse parallel ranges end in flat tail loops. Shared input/weight handles are
read-only, output tiles are disjoint, and all handles are joined after evaluation.
The bridge packs/transports buffers and checks bounds; the public API validates
finite values, while engine inference validates weights once and final logits.

PyTorch retains embeddings, SDPA, elementwise activations and the selected-output
decision head. The native pool defaults to up to eight available CPUs; override
with `JULIA_BEND_THREADS` before the first call. `JULIA_BEND_TILE_GRAIN` overrides
the adaptive projection-specific chunk size. The snapshot rejects changed weights and must be recreated after mutation.
Use the training loader to save or train checkpoints, not an installed backend.

Packed kernels use
validated unsafe array sharing and bounded loops; the tree shape proofs do not
constitute a formal proof of packed-array memory safety or floating-point math.

## Larger choice sets

```python
from julia.router import Router, FastEngine
router = Router(FastEngine('/path/to/checkpoint', device='cuda'), survivors=2)
result = router.route(row_with_up_to_4096_options)
```

Julia's trained head still supports **2–20** options. Larger *choice* requests
use batched groups and rerank survivors until a final group remains. A group
retains only its winner when raw softmax gives it over 95% and every other
option is below 4.5%; otherwise it retains the configured survivor count.
This can reduce later model calls for decisive groups, but group probabilities
are not comparable across different groups. This adds model calls and can discard the correct candidate;
it is a capacity feature, not a speed or quality guarantee. Final probabilities
are conditional on `result.candidates`, never a fabricated global distribution.
`model_rows` and `cache_hits` report aggregate work for the whole `route_many`
call. Optional `cache_size` caches logits; it defaults to zero. Clear caches
with `clear_cache()` after changing weights, tokenization or inference settings.

## Tests

```bash
python -m unittest discover -s julia/router/tests -v
```

The tests exercise CPU inference and optional native behavior where available.

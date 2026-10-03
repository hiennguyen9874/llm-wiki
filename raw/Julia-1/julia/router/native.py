"""ctypes boundary; no subprocess or compilation in the request path."""
import ctypes
import math
import os
from pathlib import Path


class BendReducer:
    def __init__(self, library=None):
        path = Path(library or os.environ.get('JULIA_ROUTER_LIBRARY') or
                    Path(__file__).parent / 'build/libjulia_router.so')
        try:
            self._lib = ctypes.CDLL(str(path.resolve()))
        except OSError as error:
            raise RuntimeError(
                f'Cannot load Bend runtime {path.resolve()}. From Julia-1 run '
                'python -m julia.router.build --native-cpu; or explicitly select '
                'transformer_backend="torch".') from error
        self._argmax = self._lib.julia_router_argmax
        self._argmax.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_uint32,
                                ctypes.POINTER(ctypes.c_uint32)]
        self._argmax.restype = ctypes.c_int
        self._ptr = ctypes.POINTER(ctypes.c_float)
        self._softmax = self._lib.julia_router_softmax
        self._softmax.argtypes = [self._ptr, ctypes.c_uint32, self._ptr, ctypes.POINTER(ctypes.c_uint32)]
        self._softmax.restype = ctypes.c_int
        self._layernorm = self._lib.julia_router_layernorm
        self._layernorm.argtypes = [self._ptr, self._ptr, self._ptr, ctypes.c_uint32,
                                   ctypes.c_uint32, ctypes.c_float, self._ptr]
        self._layernorm.restype = ctypes.c_int

    def profile(self, *, enabled=False, reset=False):
        """Process-wide packed projection timings; opt in only for diagnostics."""
        fn = self._lib.julia_router_profile
        fn.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
        fn.restype = None
        values = (ctypes.c_double * 4)()
        fn(enabled, reset, values)
        return dict(zip(('pack_ms', 'execute_ms', 'unpack_ms', 'calls'), values))

    def argmax(self, scores):
        scores = tuple(scores)
        if not 1 <= len(scores) <= 1048576:
            raise ValueError('Expected 1–1048576 scores')
        if not all(math.isfinite(x) for x in scores):
            raise ValueError('Scores must be finite')
        values = (ctypes.c_float * len(scores))(*scores)
        result = ctypes.c_uint32()
        code = self._argmax(values, len(scores), ctypes.byref(result))
        if code:
            raise ValueError(f'Bend rejected scores (status {code})')
        return result.value

    def softmax(self, scores):
        import numpy as np
        values = np.ascontiguousarray(scores, dtype=np.float32)
        if values.ndim != 1 or not 1 <= values.size <= 1048576:
            raise ValueError('Expected a nonempty vector of at most 1048576 scores')
        output = np.empty_like(values)
        index = ctypes.c_uint32()
        code = self._softmax(values.ctypes.data_as(self._ptr), values.size,
                             output.ctypes.data_as(self._ptr), ctypes.byref(index))
        if code:
            raise ValueError(f'Bend rejected scores (status {code})')
        return index.value, output

    def layernorm(self, values, gamma=None, beta=None, epsilon=1e-5):
        import numpy as np
        x = np.ascontiguousarray(values, dtype=np.float32)
        if x.ndim < 1 or x.size == 0:
            raise ValueError('Expected a nonempty feature array')
        width = x.shape[-1]
        g = np.ones(width, np.float32) if gamma is None else np.ascontiguousarray(gamma, dtype=np.float32)
        b = np.zeros(width, np.float32) if beta is None else np.ascontiguousarray(beta, dtype=np.float32)
        if g.shape != (width,) or b.shape != (width,):
            raise ValueError('gamma and beta must match the last dimension')
        if x.size > 1048576 or width > 65536:
            raise ValueError('LayerNorm input exceeds native capacity')
        output = np.empty_like(x)
        code = self._layernorm(x.ctypes.data_as(self._ptr), g.ctypes.data_as(self._ptr),
            b.ctypes.data_as(self._ptr), x.size // width, width, epsilon,
            output.ctypes.data_as(self._ptr))
        if code:
            raise ValueError(f'Bend rejected LayerNorm inputs (status {code})')
        return output


class BendMatrix:
    """Resident immutable FP32 projection weights owned by the Bend heap."""
    def __init__(self, weights, reducer=None):
        import numpy as np
        import threading
        import weakref
        self.reducer = reducer or BendReducer()
        self._lock = threading.RLock()
        values = np.ascontiguousarray(weights, dtype=np.float32)
        if values.ndim != 2 or not all(values.shape):
            raise ValueError('Projection weights must be a nonempty matrix')
        self.outputs, self.inputs = values.shape
        lib = self.reducer._lib
        create = lib.julia_router_matrix_create
        create.argtypes = [self.reducer._ptr, ctypes.c_uint32, ctypes.c_uint32]
        create.restype = ctypes.c_void_p
        release = lib.julia_router_matrix_free
        release.argtypes = [ctypes.c_void_p]
        release.restype = None
        self._linear = lib.julia_router_linear
        self._linear.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
        self._linear.restype = ctypes.c_int
        self._linear_inference = lib.julia_router_linear_inference
        self._linear_inference.argtypes = self._linear.argtypes
        self._linear_inference.restype = ctypes.c_int
        self._handle = create(values.ctypes.data_as(self.reducer._ptr), self.inputs, self.outputs)
        if not self._handle:
            raise ValueError('Bend rejected projection dimensions or nonfinite weights')
        self._finalize = weakref.finalize(self, release, self._handle)

    def close(self):
        with self._lock:
            self._finalize()

    def tensor(self, values, *, validate=True):
        """Fill a contiguous Torch output directly, without NumPy/list/concat wrappers."""
        import torch
        if values.device.type != 'cpu' or values.dtype != torch.float32 or values.shape[-1] != self.inputs:
            raise ValueError('Bend tensor projection requires matching CPU FP32 inputs')
        x = values.contiguous()
        rows = x.numel() // self.inputs
        if not rows:
            raise ValueError('Projection input must be nonempty')
        out = torch.empty((*x.shape[:-1], self.outputs), dtype=x.dtype, device=x.device)
        linear = self._linear if validate else self._linear_inference
        limit = min(1048576 // self.inputs, 1048576 // self.outputs)
        with self._lock:
            if not self._finalize.alive:
                raise RuntimeError('Bend matrix has been closed')
            for start in range(0, rows, limit):
                code = linear(self._handle,
                    x.data_ptr() + start * self.inputs * 4,
                    min(limit, rows - start),
                    out.data_ptr() + start * self.outputs * 4)
                if code:
                    raise ValueError(f'Bend projection failed (status {code})')
        return out

    def __call__(self, values):
        import numpy as np
        x = np.ascontiguousarray(values, dtype=np.float32)
        if x.ndim < 1 or x.shape[-1] != self.inputs or not x.size:
            raise ValueError('Projection input must match resident weights')
        out = np.empty((*x.shape[:-1], self.outputs), dtype=np.float32)
        with self._lock:
            if not self._finalize.alive:
                raise RuntimeError('Bend matrix has been closed')
            code = self._linear(self._handle, x.ctypes.data_as(self.reducer._ptr),
                                x.size // self.inputs, out.ctypes.data_as(self.reducer._ptr))
        if code:
            raise ValueError(f'Bend projection failed (status {code})')
        return out

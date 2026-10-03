"""Explicit, reproducible native build: python -m julia.router.build."""
import argparse
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile


def build(output=None, bend=None, native_cpu=False):
    source = Path(__file__).parent / 'native' / 'router.bend'
    bend = bend or shutil.which('bend') or str(Path.home() / '.bend/bin/bend')
    version = subprocess.check_output([bend, 'version'], text=True).strip()
    if not re.search(r'(?<![0-9.])2\.0\.27(?![0-9.])', version):
        raise RuntimeError(f'Native adapter requires Bend 2.0.27; found {version}')
    subprocess.run([bend, str(source.with_name('PROOF.bend'))], check=True)
    output = Path(output or Path(__file__).parent / 'build/libjulia_router.so').resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        generated = Path(temp) / 'router.c'
        library = Path(temp) / 'router.so'
        subprocess.run([bend, str(source), '-o', str(generated)], check=True)
        emitted = generated.read_text()
        if not all(re.search(pattern, emitted) for pattern in (
                r'#define CUBE_T\s+128', r'#define LINE\s+16',
                r'static u32\s+CUBE_LOG = 7;', r'#define RING_LOG\s+\(17 - CUBE_LOG\)')):
            raise RuntimeError('CPU scheduling layout changed; refusing unsafe native build')
        # The adapter depends on these private generated ABI/ownership contracts.
        for name, arity in [('WINNER', 1), ('SOFTMAX', 1), ('LAYERNORM', 3), ('NORM_ROWS', 3), ('DENSE_TILE', 2), ('DENSE_BATCH', 2), ('PACKED_GEMM', 9)]:
            match = re.search(rf'#define FID_{name} (\d+)', emitted)
            table = re.search(r'FID_ARITY_T\[\] = \{([^}]+)', emitted)
            if not match or not table or int(table[1].split(',')[int(match[1])]) != arity:
                raise RuntimeError(f'Unsupported generated Bend ABI for {name}')
        winner = emitted.split('WL_CASE(FID_WINNER)', 1)[1].split('#endif', 1)[0]
        if 'term_peek(e, _tree_0)' not in winner:
            raise RuntimeError('WINNER ownership changed; refusing unsafe native build')
        tile = emitted.split('WL_CASE(FID_DENSE_TILE)', 1)[1].split('#endif', 1)[0]
        if 'term_peek(e, _weights_0)' not in tile or 'term_peek(e, _ws_0)' not in emitted:
            raise RuntimeError('Tiled weights must be borrowed; refusing unsafe native build')
        batch = emitted.split('WL_CASE(FID_DENSE_BATCH)', 1)[1].split('#endif', 1)[0]
        if 'term_peek(e, _tiles_0)' not in batch:
            raise RuntimeError('Dense input tiles must be borrowed; refusing unsafe native build')
        packed = emitted.split('WL_CASE(FID_PACKED_DOT)', 1)[1].split('#endif', 1)[0]
        if not all(fragment in packed for fragment in ('r0 = _x_0;', 'r1 = _w_0;', 'r2 = _o_0;', 'WL_RETN(3);')):
            raise RuntimeError('Packed result ABI changed; refusing unsafe native build')
        from .specialize import packed_cpu
        generated.write_text(packed_cpu(emitted))
        subprocess.run([os.environ.get('CC', 'clang'), '-O3', '-ffp-contract=fast',
                        *(['-march=native'] if native_cpu else []), '-fPIC', '-shared',
                        '-pthread', str(generated), '-lm', '-ldl', '-o', str(library)], check=True)
        os.replace(library, output)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output')
    parser.add_argument('--bend')
    parser.add_argument('--native-cpu', action='store_true', help='Optimize for this CPU; do not distribute to other CPUs')
    args = parser.parse_args()
    print(build(args.output, args.bend, args.native_cpu))

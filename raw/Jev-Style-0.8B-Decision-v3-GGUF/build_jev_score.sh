#!/bin/sh
# Build jev-score (jev_score.cpp) against a llama.cpp checkout.
#   sh build_jev_score.sh /path/to/llama.cpp          -> ./build/jev-score
# Tested with llama.cpp commit 441df11f65ea0b6d0c72965aaf70c8241070ddcb (2026-09-23), macOS/Metal.
# If llama.cpp has no shared-library build yet, it is configured and built first (Metal on macOS;
# pass extra CMake flags in LLAMA_CMAKE_FLAGS, e.g. "-DGGML_CUDA=ON" on Linux/CUDA).
# OUT=/some/path/jev-score overrides the output file.
set -eu
LC=${1:?usage: sh build_jev_score.sh /path/to/llama.cpp}
LC=$(cd "$LC" && pwd)
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-"$HERE/build/jev-score"}
LIBDIR="$LC/build/bin"
if [ ! -f "$LIBDIR/libllama.dylib" ] && [ ! -f "$LIBDIR/libllama.so" ]; then
  cmake -S "$LC" -B "$LC/build" -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON \
        -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_SERVER=OFF -DLLAMA_CURL=OFF ${LLAMA_CMAKE_FLAGS:-}
  cmake --build "$LC/build" -j 8 --target llama
fi
if [ ! -f "$LIBDIR/libllama.dylib" ] && [ ! -f "$LIBDIR/libllama.so" ]; then
  LIBDIR=$(dirname "$(find "$LC/build" -name 'libllama.so' -o -name 'libllama.dylib' | head -n 1)")
fi
mkdir -p "$(dirname "$OUT")"
c++ -std=c++17 -O2 -Wall -Wno-unused-function \
  -I"$LC/include" -I"$LC/ggml/include" -I"$LC/vendor" \
  "$HERE/jev_score.cpp" -o "$OUT" \
  -L"$LIBDIR" -lllama -lggml -lggml-base -Wl,-rpath,"$LIBDIR"
echo "$OUT"

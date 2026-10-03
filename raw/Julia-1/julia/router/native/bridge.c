/* Bend 2.0.27 ABI adapter. Arithmetic lives in router.bend.
 * WINNER borrows its tree; SOFTMAX/LAYERNORM consume it (checked at build).
 * The generated runtime uses process globals, hence the single shared mutex.
 */
#include <pthread.h>
#if defined(__AVX2__)
#include <immintrin.h>
#endif
static pthread_mutex_t router_mutex = PTHREAD_MUTEX_INITIALIZER;
static Corpus router_heap;
/* Opt-in diagnostics, disabled during ordinary inference. Protected by router_mutex. */
static bool router_profile_enabled = false;
static double router_profile_totals[4] = {0}; /* pack, eval, unpack milliseconds; calls */
static double router_clock_ms(void) {
  struct timespec now;
  clock_gettime(CLOCK_MONOTONIC, &now);
  return (double)now.tv_sec * 1000.0 + (double)now.tv_nsec / 1000000.0;
}
void julia_router_profile(int enabled, int reset, double *out) {
  pthread_mutex_lock(&router_mutex);
  if (out) memcpy(out, router_profile_totals, sizeof(router_profile_totals));
  if (reset) memset(router_profile_totals, 0, sizeof(router_profile_totals));
  router_profile_enabled = enabled != 0;
  pthread_mutex_unlock(&router_mutex);
}
static Env router_env(void) {
  if (!router_heap) {
    const char *setting = getenv("JULIA_BEND_THREADS");
    long available = cpu_count();
    long threads = setting ? strtol(setting, NULL, 10) : (available < 8 ? available : 8);
    if (threads < 1 || threads > 32) threads = 1;
    /* CPU projections need about two coarse tasks per worker, not the GPU-sized
     * default 16,384-lane frontier. A smaller bag keeps the same total ring
     * capacity (deeper queues) and cuts empty-row scans on every pool turn. */
    CUBE_LOG = 0;
    while ((CUBE_T / LINE) * (1u << CUBE_LOG) < (u32)threads) ++CUBE_LOG;
    const char *cube = getenv("JULIA_BEND_CUBE_LOG");
    if (cube) {
      char *end;
      long value = strtol(cube, &end, 10);
      if (*cube && !*end && value >= (long)CUBE_LOG && value <= 7) CUBE_LOG = value;
    }
    router_heap = corpus_setup(false, threads, 0);
    io_stk = pool_stack();
  }
  return (Env){router_heap, ALC[0]};
}
static Term router_tree(Env e, const float *scores, u32 start, u32 end) {
  if (end - start == 1)
    return io_node(e, CID_LEAF, start, f32_rewrap(scores[start]));
  u32 mid = start + (end - start) / 2;
  Term left = router_tree(e, scores, start, mid);
  Term right = router_tree(e, scores, mid, end);
  return io_node(e, CID_FORK, left, right);
}
static Term router_eval(Env e, u32 fid, Term tree) {
  Loc task = task_node(e, fid, TERM_HOLE, 0, 0);
  e.mem[task] = tree;
  return corpus_eval(e.mem, term_tsk(fid, task));
}
static void router_unpack(Env e, Term tree, float *output) {
  Loc node = term_loc(tree);
  if (term_aux(tree) == CID_LEAF) {
    if (output) output[(u32)e.mem[node]] = f32_unbox(e.mem[node + 1]);
  } else {
    router_unpack(e, e.mem[node], output);
    router_unpack(e, e.mem[node + 1], output);
  }
  heap_free(e, cls_fit(2), node);
}
static int router_valid(const float *scores, u32 count) {
  if (!scores || !count || count > 1048576) return -1;
  for (u32 i = 0; i < count; ++i) if (!isfinite(scores[i])) return -2;
  return 0;
}
int julia_router_argmax(const float *scores, uint32_t count, uint32_t *index) {
  int status = router_valid(scores, count);
  if (status || !index) return status ? status : -1;
  pthread_mutex_lock(&router_mutex);
  Env e = router_env();
  Term tree = router_tree(e, scores, 0, count);
  Term result = router_eval(e, FID_WINNER, tree);
  *index = (u32)e.mem[term_loc(result)];
  term_drop(e, result);
  router_unpack(e, tree, NULL);
  pthread_mutex_unlock(&router_mutex);
  return 0;
}
int julia_router_softmax(const float *scores, uint32_t count, float *out, uint32_t *index) {
  int status = router_valid(scores, count);
  if (status || !out || !index) return status ? status : -1;
  pthread_mutex_lock(&router_mutex);
  Env e = router_env();
  Term tree = router_tree(e, scores, 0, count);
  Term best = router_eval(e, FID_WINNER, tree);
  *index = (u32)e.mem[term_loc(best)];
  term_drop(e, best);
  router_unpack(e, router_eval(e, FID_SOFTMAX, tree), out);
  pthread_mutex_unlock(&router_mutex);
  return router_valid(out, count);
}
static Term router_features(Env e, const float *x, const float *g, const float *b, u32 lo, u32 hi) {
  if (hi - lo == 1) {
    Loc node = heap_alloc(e, cls_fit(3));
    e.mem[node] = f32_rewrap(x[lo]);
    e.mem[node + 1] = f32_rewrap(g[lo]);
    e.mem[node + 2] = f32_rewrap(b[lo]);
    return term_ctr(CID_FEATURE, node);
  }
  u32 mid = lo + (hi - lo) / 2;
  Term left = router_features(e, x, g, b, lo, mid);
  Term right = router_features(e, x, g, b, mid, hi);
  return io_node(e, CID_BRANCH, left, right);
}
static void router_unfeatures(Env e, Term tree, float *out, u32 lo, u32 hi) {
  Loc node = term_loc(tree);
  if (hi - lo == 1) {
    out[lo] = f32_unbox(e.mem[node]);
    heap_free(e, cls_fit(3), node);
  } else {
    u32 mid = lo + (hi - lo) / 2;
    router_unfeatures(e, e.mem[node], out, lo, mid);
    router_unfeatures(e, e.mem[node + 1], out, mid, hi);
    heap_free(e, cls_fit(2), node);
  }
}
static Term router_vector(Env e, const float *x, const float *g, const float *b, u32 width) {
  Term tail = term_ctr(CID_VNIL, 0);
  for (u32 i = width; i-- > 0;) {
    Loc node = heap_alloc(e, cls_fit(4));
    e.mem[node] = f32_rewrap(x[i]);
    e.mem[node + 1] = f32_rewrap(g[i]);
    e.mem[node + 2] = f32_rewrap(b[i]);
    e.mem[node + 3] = tail;
    tail = term_ctr(CID_VCONS, node);
  }
  return tail;
}
static Term router_rows(Env e, const float *x, const float *g, const float *b,
                        u32 width, u32 lo, u32 hi) {
  if (hi - lo == 1) {
    Loc node = heap_alloc(e, cls_fit(1));
    e.mem[node] = router_vector(e, x + lo * width, g, b, width);
    return term_ctr(CID_NLEAF, node);
  }
  u32 mid = lo + (hi - lo) / 2;
  Term left = router_rows(e, x, g, b, width, lo, mid);
  Term right = router_rows(e, x, g, b, width, mid, hi);
  return io_node(e, CID_NFORK, left, right);
}
static void router_unrows(Env e, Term tree, float *out, u32 width, u32 lo, u32 hi) {
  Loc node = term_loc(tree);
  if (hi - lo == 1) {
    Term vector = e.mem[node];
    // The flat affine loop builds the result in reverse order.
    for (u32 i = width; i-- > 0;) {
      Loc item = term_loc(vector);
      out[lo * width + i] = f32_unbox(e.mem[item]);
      vector = e.mem[item + 3];
      heap_free(e, cls_fit(4), item);
    }
    heap_free(e, cls_fit(1), node);
  } else {
    u32 mid = lo + (hi - lo) / 2;
    router_unrows(e, e.mem[node], out, width, lo, mid);
    router_unrows(e, e.mem[node + 1], out, width, mid, hi);
    heap_free(e, cls_fit(2), node);
  }
}
int julia_router_layernorm(const float *x, const float *gamma, const float *beta,
                          uint32_t rows, uint32_t width, float epsilon, float *out) {
  if (!rows || !width || width > 65536 || rows > 1048576 / width || !out ||
      !isfinite(epsilon) || epsilon <= 0) return -1;
  int status = router_valid(x, rows * width);
  if (!status) status = router_valid(gamma, width);
  if (!status) status = router_valid(beta, width);
  if (status) return status;
  pthread_mutex_lock(&router_mutex);
  Env e = router_env();
  Term tree = router_rows(e, x, gamma, beta, width, 0, rows);
  Loc task = task_node(e, FID_NORM_ROWS, TERM_HOLE, 0, 0);
  e.mem[task] = tree;
  e.mem[task + 1] = f32_rewrap((float)width);
  e.mem[task + 2] = f32_rewrap(epsilon);
  Term result = corpus_eval(e.mem, term_tsk(FID_NORM_ROWS, task));
  router_unrows(e, result, out, width, 0, rows);
  pthread_mutex_unlock(&router_mutex);
  return router_valid(out, rows * width);
}

/* Resident immutable weights are built once and borrowed by every forward. */
typedef struct { Term tree; u32 inputs; u32 outputs; bool packed; } RouterMatrix;
static Term router_matrix(Env e, const float *w, u32 inputs, u32 outputs, u32 lo, u32 hi) {
  if (hi - lo == 1) {
    Term tail = term_ctr(CID_JWEND, 0);
    for (u32 j = inputs; j-- > 0;) {
      Loc node = heap_alloc(e, cls_fit(8));
      for (u32 k = 0; k < 7; ++k)
        e.mem[node + k] = f32_rewrap(lo * 7 + k < outputs ? w[(lo * 7 + k) * inputs + j] : 0.f);
      e.mem[node + 7] = tail;
      tail = term_ctr(CID_JWVAL, node);
    }
    Loc leaf = heap_alloc(e, cls_fit(1));
    e.mem[leaf] = tail;
    return term_ctr(CID_JMLEAF, leaf);
  }
  u32 mid = lo + (hi - lo) / 2;
  Term left = router_matrix(e, w, inputs, outputs, lo, mid);
  Term right = router_matrix(e, w, inputs, outputs, mid, hi);
  return io_node(e, CID_JMFORK, left, right);
}
static void router_free_matrix(Env e, Term tree) {
  Loc node = term_loc(tree);
  if (term_aux(tree) == CID_JMLEAF) {
    Term ws = e.mem[node];
    while (term_aux(ws) == CID_JWVAL) {
      Loc item = term_loc(ws);
      ws = e.mem[item + 7];
      heap_free(e, cls_fit(8), item);
    }
    heap_free(e, cls_fit(1), node);
  } else {
    router_free_matrix(e, e.mem[node]);
    router_free_matrix(e, e.mem[node + 1]);
    heap_free(e, cls_fit(2), node);
  }
}
/* Packed FP32 buffers: padding is explicit because Bend array indices wrap. */
static Term router_buffer_raw(Env e, u32 cells) {
  Cls depth = cls_fit(cells);
  Loc loc = heap_alloc(e, buf_wcls(depth));
  return term_buf(depth, loc);
}
static Term router_packed_weights(Env e, const float *w, u32 inputs, u32 outputs) {
  u32 cols = (outputs + 7) / 8 * 8;
  Term array = router_buffer_raw(e, inputs * cols);
  memset((void *)(e.mem + term_loc(array)), 0, (size_t)inputs * cols * sizeof(float));
  float *data = (float *)(e.mem + term_loc(array));
  for (u32 j = 0; j < inputs; ++j)
    for (u32 col = 0; col < outputs; ++col)
      data[(col / 8 * inputs + j) * 8 + col % 8] = w[col * inputs + j];
  return array;
}
/* Layout conversion only: transpose eight FP32 rows without doing arithmetic. */
static void router_pack_input(float *restrict dst, const float *restrict src, u32 rows, u32 width) {
  u32 row = 0;
#if defined(__AVX2__)
  for (; row + 8 <= rows; row += 8) {
    u32 j = 0;
    for (; j + 8 <= width; j += 8) {
      __m256 r[8], t[8], v[8];
      for (u32 k = 0; k < 8; ++k) r[k] = _mm256_loadu_ps(src + (row + k) * width + j);
      for (u32 k = 0; k < 8; k += 2) {
        t[k] = _mm256_unpacklo_ps(r[k], r[k+1]);
        t[k+1] = _mm256_unpackhi_ps(r[k], r[k+1]);
      }
      for (u32 k = 0; k < 8; k += 4) {
        v[k] = _mm256_shuffle_ps(t[k], t[k+2], 0x44);
        v[k+1] = _mm256_shuffle_ps(t[k], t[k+2], 0xee);
        v[k+2] = _mm256_shuffle_ps(t[k+1], t[k+3], 0x44);
        v[k+3] = _mm256_shuffle_ps(t[k+1], t[k+3], 0xee);
      }
      for (u32 k = 0; k < 4; ++k) {
        _mm256_storeu_ps(dst + (row / 8 * width + j + k) * 8,
                        _mm256_permute2f128_ps(v[k], v[k+4], 0x20));
        _mm256_storeu_ps(dst + (row / 8 * width + j + k + 4) * 8,
                        _mm256_permute2f128_ps(v[k], v[k+4], 0x31));
      }
    }
    for (; j < width; ++j)
      for (u32 k = 0; k < 8; ++k) dst[(row / 8 * width + j) * 8 + k] = src[(row+k) * width + j];
  }
#endif
  for (; row < rows; ++row)
    for (u32 j = 0; j < width; ++j)
      dst[(row / 8 * width + j) * 8 + row % 8] = src[row * width + j];
}
static void router_packed_linear(Env e, RouterMatrix *matrix, const float *x, u32 rows, float *out) {
  double begin = router_profile_enabled ? router_clock_ms() : 0.0;
  u32 cols = (matrix->outputs + 7) / 8 * 8;
  u32 padded_rows = (rows + 7) / 8 * 8;
  u32 count = padded_rows / 8 * (cols / 8);
  Term input = router_buffer_raw(e, padded_rows * matrix->inputs);
  Term output = router_buffer_raw(e, padded_rows * cols);
  float *input_data = (float *)(e.mem + term_loc(input));
  if (rows % 8)
    memset(input_data + (rows / 8) * matrix->inputs * 8, 0, matrix->inputs * 8 * sizeof(float));
  router_pack_input(input_data, x, rows, matrix->inputs);
  Loc task = task_node(e, FID_PACKED_GEMM, TERM_HOLE, 0, 0);
  e.mem[task + 0] = input;
  e.mem[task + 1] = matrix->tree;
  e.mem[task + 2] = output;
  e.mem[task + 3] = 0;
  e.mem[task + 4] = count;
  e.mem[task + 5] = cols / 8;
  const char *grain_setting = getenv("JULIA_BEND_TILE_GRAIN");
  u32 automatic_grain = (count + pool_size * 2 - 1) / (pool_size * 2);
  u32 grain = grain_setting ? strtoul(grain_setting, NULL, 10) : automatic_grain;
  if (!grain || grain > 65536) grain = automatic_grain;
  e.mem[task + 6] = grain;
  e.mem[task + 7] = matrix->inputs;
  e.mem[task + 8] = (count <= grain);
  /* PackedBuffers is flattened to three result words by Bend 2.0.27.
   * corpus_eval clears the ready flag but leaves these words intact. The
   * runtime mutex prevents another evaluation from overwriting the mailbox. */
  double dispatched = router_profile_enabled ? router_clock_ms() : 0.0;
  corpus_eval(e.mem, term_tsk(FID_PACKED_GEMM, task));
  double evaluated = router_profile_enabled ? router_clock_ms() : 0.0;
  input = e.mem[H_ROOT_WORD];
  matrix->tree = e.mem[H_ROOT_WORD + 1];
  output = e.mem[H_ROOT_WORD + 2];
  const float *data = (const float *)(e.mem + blk_loc(e.mem, output));
  for (u32 row = 0; row < rows; ++row) {
    const float *tiles = data + (row / 8 * (cols / 8)) * 64 + row % 8 * 8;
    u32 col = 0;
    for (; col + 8 <= matrix->outputs; col += 8)
      memcpy(out + row * matrix->outputs + col, tiles + (col / 8) * 64, 8 * sizeof(float));
    if (col < matrix->outputs)
      memcpy(out + row * matrix->outputs + col, tiles + (col / 8) * 64,
             (matrix->outputs - col) * sizeof(float));
  }
  blk_free(e, input);
  blk_free(e, output);
  if (router_profile_enabled) {
    router_profile_totals[0] += dispatched - begin;
    router_profile_totals[1] += evaluated - dispatched;
    router_profile_totals[2] += router_clock_ms() - evaluated;
    router_profile_totals[3] += 1;
  }
}
void *julia_router_matrix_create(const float *weights, u32 inputs, u32 outputs) {
  if (!inputs || !outputs || inputs > 65536 || outputs > 65536 ||
      (u64)inputs * outputs > 16777216) return NULL;
  if (!weights) return NULL;
  for (u64 i = 0; i < (u64)inputs * outputs; ++i) if (!isfinite(weights[i])) return NULL;
  RouterMatrix *matrix = malloc(sizeof(*matrix));
  if (!matrix) return NULL;
  pthread_mutex_lock(&router_mutex);
  Env e = router_env();
  matrix->inputs = inputs;
  matrix->outputs = outputs;
  const char *kernel = getenv("JULIA_BEND_KERNEL");
  matrix->packed = !kernel || strcmp(kernel, "tree") != 0;
  matrix->tree = matrix->packed ? router_packed_weights(e, weights, inputs, outputs)
      : router_matrix(e, weights, inputs, outputs, 0, (outputs + 6) / 7);
  pthread_mutex_unlock(&router_mutex);
  return matrix;
}
void julia_router_matrix_free(void *handle) {
  if (!handle) return;
  RouterMatrix *matrix = handle;
  pthread_mutex_lock(&router_mutex);
  if (matrix->packed) blk_free(router_env(), matrix->tree);
  else router_free_matrix(router_env(), matrix->tree);
  pthread_mutex_unlock(&router_mutex);
  free(matrix);
}
static void router_tile_result(Env e, Term tree, float *out, u32 rows, u32 outputs, u32 lo, u32 hi) {
  Loc node = term_loc(tree);
  if (hi - lo == 1) {
    for (u32 row = 0; row < rows; ++row)
      for (u32 k = 0; k < 7 && lo * 7 + k < outputs; ++k)
        out[row * outputs + lo * 7 + k] = f32_unbox(e.mem[node + row * 7 + k]);
    heap_free(e, cls_fit(28), node);
  } else {
    u32 mid = lo + (hi - lo) / 2;
    router_tile_result(e, e.mem[node], out, rows, outputs, lo, mid);
    router_tile_result(e, e.mem[node + 1], out, rows, outputs, mid, hi);
    heap_free(e, cls_fit(2), node);
  }
}
static Term router_input_tiles(Env e, const float *x, u32 rows, u32 inputs, u32 lo, u32 hi) {
  if (hi - lo == 1) {
    Term xs = term_ctr(CID_JTEND, 0);
    for (u32 i = inputs; i-- > 0;) {
      Loc item = heap_alloc(e, cls_fit(5));
      for (u32 k = 0; k < 4; ++k)
        e.mem[item + k] = f32_rewrap(lo * 4 + k < rows ? x[(lo * 4 + k) * inputs + i] : 0.f);
      e.mem[item + 4] = xs;
      xs = term_ctr(CID_JTVAL, item);
    }
    Loc leaf = heap_alloc(e, cls_fit(1));
    e.mem[leaf] = xs;
    return term_ctr(CID_JILEAF, leaf);
  }
  u32 mid = lo + (hi - lo) / 2;
  Term left = router_input_tiles(e, x, rows, inputs, lo, mid);
  Term right = router_input_tiles(e, x, rows, inputs, mid, hi);
  return io_node(e, CID_JIFORK, left, right);
}
static void router_free_tiles(Env e, Term tree) {
  Loc node = term_loc(tree);
  if (term_aux(tree) == CID_JILEAF) {
    Term xs = e.mem[node];
    while (term_aux(xs) == CID_JTVAL) {
      Loc item = term_loc(xs);
      xs = e.mem[item + 4];
      heap_free(e, cls_fit(5), item);
    }
    heap_free(e, cls_fit(1), node);
  } else {
    router_free_tiles(e, e.mem[node]);
    router_free_tiles(e, e.mem[node + 1]);
    heap_free(e, cls_fit(2), node);
  }
}
static void router_output_tiles(Env e, Term tree, float *out, u32 rows, u32 outputs, u32 lo, u32 hi) {
  Loc node = term_loc(tree);
  if (hi - lo == 1) {
    u32 count = rows - lo * 4 < 4 ? rows - lo * 4 : 4;
    router_tile_result(e, e.mem[node], out + lo * 4 * outputs, count, outputs, 0, (outputs + 6) / 7);
    heap_free(e, cls_fit(1), node);
  } else {
    u32 mid = lo + (hi - lo) / 2;
    router_output_tiles(e, e.mem[node], out, rows, outputs, lo, mid);
    router_output_tiles(e, e.mem[node + 1], out, rows, outputs, mid, hi);
    heap_free(e, cls_fit(2), node);
  }
}
static int router_linear(void *handle, const float *x, u32 rows, float *out, bool validate) {
  if (!handle || !x || !out || !rows) return -1;
  RouterMatrix *matrix = handle;
  if (rows > 1048576 / matrix->inputs || rows > 1048576 / matrix->outputs) return -1;
  int status = validate ? router_valid(x, rows * matrix->inputs) : 0;
  if (status) return status;
  pthread_mutex_lock(&router_mutex);
  Env e = router_env();
  if (matrix->packed) {
    router_packed_linear(e, matrix, x, rows, out);
    pthread_mutex_unlock(&router_mutex);
    return validate ? router_valid(out, rows * matrix->outputs) : 0;
  }
  u32 count = (rows + 3) / 4;
  Term xs = router_input_tiles(e, x, rows, matrix->inputs, 0, count);
  Loc task = task_node(e, FID_DENSE_BATCH, TERM_HOLE, 0, 0);
  e.mem[task] = xs;
  e.mem[task + 1] = matrix->tree;
  Term result = corpus_eval(e.mem, term_tsk(FID_DENSE_BATCH, task));
  router_output_tiles(e, result, out, rows, matrix->outputs, 0, count);
  router_free_tiles(e, xs);
  pthread_mutex_unlock(&router_mutex);
  return validate ? router_valid(out, rows * matrix->outputs) : 0;
}

int julia_router_linear(void *handle, const float *x, u32 rows, float *out) {
  return router_linear(handle, x, rows, out, true);
}
/* Internal engine path: weights are validated once, logits at the model boundary.
 * Shape, pointer, lifetime and buffer bounds checks remain mandatory. */
int julia_router_linear_inference(void *handle, const float *x, u32 rows, float *out) {
  return router_linear(handle, x, rows, out, false);
}

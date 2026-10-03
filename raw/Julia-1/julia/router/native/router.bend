import Base

type Candidates is Data:
  Leaf{index: U32, score: F32}
  Fork{left: Candidates, right: Candidates}

def pick(flag: Bool, a: Candidates, b: Candidates) -> Candidates:
  match flag:
    case True{}:
      a
    case False{}:
      b

def better(a: Candidates, b: Candidates) -> Candidates:
  match a b:
    case Leaf{+i, +x} Leaf{+j, +y}:
      pick(F32.is_gt(x, y) || (F32.is_eq(x, y) && U32.is_le(i, j)), Leaf{i, x}, Leaf{j, y})
    case _ _:
      a

def winner(tree: Candidates) -> Candidates:
  match tree:
    case Leaf{i, x}:
      Leaf{i, x}
    case Fork{left, right}:
      a b = winner(left) winner(right)
      better(a, b)

def input() -> IO(Candidates):
  import "./bridge.c"

def output(tree: Candidates) -> IO(Unit):
  import "./bridge.c"

# Transformer math uses the same affine trees. Forks expose independent work.
def exponentials(tree: Candidates, +maximum: F32) -> Candidates:
  match tree:
    case Leaf{i, x}:
      Leaf{i, F32.exp(F32.sub(x, maximum))}
    case Fork{left, right}:
      a b = exponentials(left, maximum) exponentials(right, maximum)
      Fork{a, b}

def total(tree: Candidates) -> F32:
  match tree:
    case Leaf{i, x}:
      x
    case Fork{left, right}:
      a b = total(left) total(right)
      F32.add(a, b)

def divide(tree: Candidates, +sum: F32) -> Candidates:
  match tree:
    case Leaf{i, x}:
      Leaf{i, F32.div(x, sum)}
    case Fork{left, right}:
      a b = divide(left, sum) divide(right, sum)
      Fork{a, b}

def softmax_best(tree: Candidates, best: Candidates) -> Candidates:
  match best:
    case Leaf{i, maximum}:
      +values = exponentials(tree, maximum)
      divide(values, total(values))
    case Fork{left, right}:
      tree

def softmax(+tree: Candidates) -> Candidates:
  softmax_best(tree, winner(tree))

type Features is Data:
  Feature{x: F32, gamma: F32, beta: F32}
  Branch{left: Features, right: Features}

def feature_sum(tree: Features) -> F32:
  match tree:
    case Feature{x, gamma, beta}:
      x
    case Branch{left, right}:
      a b = feature_sum(left) feature_sum(right)
      F32.add(a, b)

def variance(tree: Features, +mean: F32) -> F32:
  match tree:
    case Feature{x, gamma, beta}:
      F32.square(F32.sub(x, mean))
    case Branch{left, right}:
      a b = variance(left, mean) variance(right, mean)
      F32.add(a, b)

def affine(tree: Features, +mean: F32, +scale: F32) -> Features:
  match tree:
    case Feature{x, +gamma, +beta}:
      Feature{F32.add(F32.mul(F32.mul(F32.sub(x, mean), scale), gamma), beta), gamma, beta}
    case Branch{left, right}:
      a b = affine(left, mean, scale) affine(right, mean, scale)
      Branch{a, b}

def layernorm(+tree: Features, +count: F32, epsilon: F32) -> Features:
  +mean = F32.div(feature_sum(tree), count)
  scale = F32.div(1.0, F32.sqrt(F32.add(F32.div(variance(tree, mean), count), epsilon)))
  affine(tree, mean, scale)

def features() -> IO(Features):
  import "./bridge.c"

def write_features(tree: Features) -> IO(Unit):
  import "./bridge.c"

# Coarse parallelism: fork over independent rows, flat tail loops within a row.
# Scalar-level tasks cost more to schedule than the arithmetic they perform.
type Vector is Data:
  VNil{}
  VCons{x: F32, gamma: F32, beta: F32, next: Vector}

type NormRows is Data:
  NLeaf{values: Vector}
  NFork{left: NormRows, right: NormRows}

def vector_sum(xs: Vector, acc: F32) -> F32:
  match xs:
    case VNil{}:
      acc
    case VCons{x, g, b, next}:
      vector_sum(next, F32.add(acc, x))

def vector_variance(xs: Vector, +mean: F32, acc: F32) -> F32:
  match xs:
    case VNil{}:
      acc
    case VCons{x, g, b, next}:
      vector_variance(next, mean, F32.add(acc, F32.square(F32.sub(x, mean))))

def vector_affine(xs: Vector, +mean: F32, +scale: F32, out: Vector) -> Vector:
  match xs:
    case VNil{}:
      out
    case VCons{x, +g, +b, next}:
      value = F32.add(F32.mul(F32.mul(F32.sub(x, mean), scale), g), b)
      vector_affine(next, mean, scale, VCons{value, g, b, out})

def norm_vector(+xs: Vector, +count: F32, epsilon: F32) -> Vector:
  +mean = F32.div(vector_sum(xs, 0.0), count)
  scale = F32.div(1.0, F32.sqrt(F32.add(F32.div(vector_variance(xs, mean, 0.0), count), epsilon)))
  vector_affine(xs, mean, scale, VNil{})

def norm_rows(xs: NormRows, +count: F32, +epsilon: F32) -> NormRows:
  match xs:
    case NLeaf{values}:
      NLeaf{norm_vector(values, count, epsilon)}
    case NFork{left, right}:
      a b = norm_rows(left, count, epsilon) norm_rows(right, count, epsilon)
      NFork{a, b}

def batch_features() -> IO(NormRows):
  import "./bridge.c"

def write_batch(tree: NormRows) -> IO(Unit):
  import "./bridge.c"

# Resident dense projections. Each leaf computes four output channels in one
# flat loop; only independent output tiles fork. Inputs and weights are borrowed.
type DenseWeights is Data:
  JWEnd{}
  JWVal{w0: F32, w1: F32, w2: F32, w3: F32, w4: F32, w5: F32, w6: F32, next: DenseWeights}

type JuliaMatrix is Data:
  JMLeaf{weights: DenseWeights}
  JMFork{left: JuliaMatrix, right: JuliaMatrix}

def dense_weights() -> IO(JuliaMatrix):
  import "./bridge.c"

# A 4x7 tile fits seven weights plus a link in one eight-word heap allocation.
# Each weight is reused across four tokens; no half-empty 16-word allocations.
type TileInput is Data:
  JTEnd{}
  JTVal{a: F32, b: F32, c: F32, d: F32, next: TileInput}

type TileResult is Data:
  JTLeaf{v0: F32, v1: F32, v2: F32, v3: F32, v4: F32, v5: F32, v6: F32, v7: F32, v8: F32, v9: F32, v10: F32, v11: F32, v12: F32, v13: F32, v14: F32, v15: F32, v16: F32, v17: F32, v18: F32, v19: F32, v20: F32, v21: F32, v22: F32, v23: F32, v24: F32, v25: F32, v26: F32, v27: F32}
  JTFork{left: TileResult, right: TileResult}

def dot_tile(xs: TileInput, ws: DenseWeights, s0: F32, s1: F32, s2: F32, s3: F32, s4: F32, s5: F32, s6: F32, s7: F32, s8: F32, s9: F32, s10: F32, s11: F32, s12: F32, s13: F32, s14: F32, s15: F32, s16: F32, s17: F32, s18: F32, s19: F32, s20: F32, s21: F32, s22: F32, s23: F32, s24: F32, s25: F32, s26: F32, s27: F32) -> TileResult:
  match xs ws:
    case JTVal{+x0, +x1, +x2, +x3, xt} JWVal{+w0, +w1, +w2, +w3, +w4, +w5, +w6, wt}:
      dot_tile(xt, wt, F32.add(s0, F32.mul(x0, w0)),
           F32.add(s1, F32.mul(x0, w1)),
           F32.add(s2, F32.mul(x0, w2)),
           F32.add(s3, F32.mul(x0, w3)),
           F32.add(s4, F32.mul(x0, w4)),
           F32.add(s5, F32.mul(x0, w5)),
           F32.add(s6, F32.mul(x0, w6)),
           F32.add(s7, F32.mul(x1, w0)),
           F32.add(s8, F32.mul(x1, w1)),
           F32.add(s9, F32.mul(x1, w2)),
           F32.add(s10, F32.mul(x1, w3)),
           F32.add(s11, F32.mul(x1, w4)),
           F32.add(s12, F32.mul(x1, w5)),
           F32.add(s13, F32.mul(x1, w6)),
           F32.add(s14, F32.mul(x2, w0)),
           F32.add(s15, F32.mul(x2, w1)),
           F32.add(s16, F32.mul(x2, w2)),
           F32.add(s17, F32.mul(x2, w3)),
           F32.add(s18, F32.mul(x2, w4)),
           F32.add(s19, F32.mul(x2, w5)),
           F32.add(s20, F32.mul(x2, w6)),
           F32.add(s21, F32.mul(x3, w0)),
           F32.add(s22, F32.mul(x3, w1)),
           F32.add(s23, F32.mul(x3, w2)),
           F32.add(s24, F32.mul(x3, w3)),
           F32.add(s25, F32.mul(x3, w4)),
           F32.add(s26, F32.mul(x3, w5)),
           F32.add(s27, F32.mul(x3, w6)))
    case _ _:
      JTLeaf{s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24, s25, s26, s27}

def dense_tile(+xs: TileInput, weights: JuliaMatrix) -> TileResult:
  match weights:
    case JMLeaf{ws}:
      dot_tile(xs, ws, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    case JMFork{left, right}:
      a b = dense_tile(xs, left) dense_tile(xs, right)
      JTFork{a, b}

def tile_input() -> IO(TileInput):
  import "./bridge.c"

def tile_output(result: TileResult) -> IO(Unit):
  import "./bridge.c"

# One fork tree spans token tiles and output tiles; one runtime dispatch per matrix.
type InputTiles is Data:
  JILeaf{tile: TileInput}
  JIFork{left: InputTiles, right: InputTiles}

type OutputTiles is Data:
  JOLeaf{tile: TileResult}
  JOFork{left: OutputTiles, right: OutputTiles}

def dense_batch(tiles: InputTiles, +weights: JuliaMatrix) -> OutputTiles:
  match tiles:
    case JILeaf{tile}:
      JOLeaf{dense_tile(tile, weights)}
    case JIFork{left, right}:
      a b = dense_batch(left, weights) dense_batch(right, weights)
      JOFork{a, b}

def input_tiles() -> IO(InputTiles):
  import "./bridge.c"

def output_tiles(result: OutputTiles) -> IO(Unit):
  import "./bridge.c"

# Packed tiles expose contiguous lanes to the native compiler. All arithmetic
# stays in Bend. Shared inputs are read-only; output tiles are disjoint.
# Unsafe loops terminate at the positive, validated dimensions in the bridge.
type Input8 is Data:
  JInput8{v0: F32, v1: F32, v2: F32, v3: F32, v4: F32, v5: F32, v6: F32, v7: F32}

type Weight8 is Data:
  JWeight8{v0: F32, v1: F32, v2: F32, v3: F32, v4: F32, v5: F32, v6: F32, v7: F32}

type Output64 is Data:
  JOutput64{v0: F32, v1: F32, v2: F32, v3: F32, v4: F32, v5: F32, v6: F32, v7: F32, v8: F32, v9: F32, v10: F32, v11: F32, v12: F32, v13: F32, v14: F32, v15: F32, v16: F32, v17: F32, v18: F32, v19: F32, v20: F32, v21: F32, v22: F32, v23: F32, v24: F32, v25: F32, v26: F32, v27: F32, v28: F32, v29: F32, v30: F32, v31: F32, v32: F32, v33: F32, v34: F32, v35: F32, v36: F32, v37: F32, v38: F32, v39: F32, v40: F32, v41: F32, v42: F32, v43: F32, v44: F32, v45: F32, v46: F32, v47: F32, v48: F32, v49: F32, v50: F32, v51: F32, v52: F32, v53: F32, v54: F32, v55: F32, v56: F32, v57: F32, v58: F32, v59: F32, v60: F32, v61: F32, v62: F32, v63: F32}

type PackedBuffers is Type:
  JBuffers{x: Array<Input8>, w: Array<Weight8>, o: Array<Output64>}

@unsafe
def packed_dot(x: Array<Input8>, w: Array<Weight8>, o: Array<Output64>, +row: U32, +col: U32, +cols: U32, +inner: U32, +end: U32, +j: U32, +s0: F32, +s1: F32, +s2: F32, +s3: F32, +s4: F32, +s5: F32, +s6: F32, +s7: F32, +s8: F32, +s9: F32, +s10: F32, +s11: F32, +s12: F32, +s13: F32, +s14: F32, +s15: F32, +s16: F32, +s17: F32, +s18: F32, +s19: F32, +s20: F32, +s21: F32, +s22: F32, +s23: F32, +s24: F32, +s25: F32, +s26: F32, +s27: F32, +s28: F32, +s29: F32, +s30: F32, +s31: F32, +s32: F32, +s33: F32, +s34: F32, +s35: F32, +s36: F32, +s37: F32, +s38: F32, +s39: F32, +s40: F32, +s41: F32, +s42: F32, +s43: F32, +s44: F32, +s45: F32, +s46: F32, +s47: F32, +s48: F32, +s49: F32, +s50: F32, +s51: F32, +s52: F32, +s53: F32, +s54: F32, +s55: F32, +s56: F32, +s57: F32, +s58: F32, +s59: F32, +s60: F32, +s61: F32, +s62: F32, +s63: F32, active: Bool) -> PackedBuffers:
  match active:
    case True{}:
      packed_read_x(Array.get(Input8, x, U32.add(U32.mul(row, inner), j)), w, o, row, col, cols, inner, end, j, s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24, s25, s26, s27, s28, s29, s30, s31, s32, s33, s34, s35, s36, s37, s38, s39, s40, s41, s42, s43, s44, s45, s46, s47, s48, s49, s50, s51, s52, s53, s54, s55, s56, s57, s58, s59, s60, s61, s62, s63)
    case False{}:
      o = Array.set(Output64, o, U32.add(U32.mul(row, cols), col), JOutput64{s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24, s25, s26, s27, s28, s29, s30, s31, s32, s33, s34, s35, s36, s37, s38, s39, s40, s41, s42, s43, s44, s45, s46, s47, s48, s49, s50, s51, s52, s53, s54, s55, s56, s57, s58, s59, s60, s61, s62, s63})
      packed_step(x, w, o, U32.add(U32.add(U32.mul(row, cols), col), 1), end, cols, inner, U32.is_lt(U32.add(U32.add(U32.mul(row, cols), col), 1), end))

@unsafe
def packed_read_x(pair: Array<Input8> & Input8, w: Array<Weight8>, o: Array<Output64>, +row: U32, +col: U32, +cols: U32, +inner: U32, +end: U32, +j: U32, +s0: F32, +s1: F32, +s2: F32, +s3: F32, +s4: F32, +s5: F32, +s6: F32, +s7: F32, +s8: F32, +s9: F32, +s10: F32, +s11: F32, +s12: F32, +s13: F32, +s14: F32, +s15: F32, +s16: F32, +s17: F32, +s18: F32, +s19: F32, +s20: F32, +s21: F32, +s22: F32, +s23: F32, +s24: F32, +s25: F32, +s26: F32, +s27: F32, +s28: F32, +s29: F32, +s30: F32, +s31: F32, +s32: F32, +s33: F32, +s34: F32, +s35: F32, +s36: F32, +s37: F32, +s38: F32, +s39: F32, +s40: F32, +s41: F32, +s42: F32, +s43: F32, +s44: F32, +s45: F32, +s46: F32, +s47: F32, +s48: F32, +s49: F32, +s50: F32, +s51: F32, +s52: F32, +s53: F32, +s54: F32, +s55: F32, +s56: F32, +s57: F32, +s58: F32, +s59: F32, +s60: F32, +s61: F32, +s62: F32, +s63: F32) -> PackedBuffers:
  (x, input) = pair
  JInput8{+x0, +x1, +x2, +x3, +x4, +x5, +x6, +x7} = input
  packed_read_w(Array.get(Weight8, w, U32.add(U32.mul(col, inner), j)), x, o, row, col, cols, inner, end, j, s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24, s25, s26, s27, s28, s29, s30, s31, s32, s33, s34, s35, s36, s37, s38, s39, s40, s41, s42, s43, s44, s45, s46, s47, s48, s49, s50, s51, s52, s53, s54, s55, s56, s57, s58, s59, s60, s61, s62, s63, x0, x1, x2, x3, x4, x5, x6, x7)

@unsafe
def packed_read_w(pair: Array<Weight8> & Weight8, x: Array<Input8>, o: Array<Output64>, +row: U32, +col: U32, +cols: U32, +inner: U32, +end: U32, +j: U32, +s0: F32, +s1: F32, +s2: F32, +s3: F32, +s4: F32, +s5: F32, +s6: F32, +s7: F32, +s8: F32, +s9: F32, +s10: F32, +s11: F32, +s12: F32, +s13: F32, +s14: F32, +s15: F32, +s16: F32, +s17: F32, +s18: F32, +s19: F32, +s20: F32, +s21: F32, +s22: F32, +s23: F32, +s24: F32, +s25: F32, +s26: F32, +s27: F32, +s28: F32, +s29: F32, +s30: F32, +s31: F32, +s32: F32, +s33: F32, +s34: F32, +s35: F32, +s36: F32, +s37: F32, +s38: F32, +s39: F32, +s40: F32, +s41: F32, +s42: F32, +s43: F32, +s44: F32, +s45: F32, +s46: F32, +s47: F32, +s48: F32, +s49: F32, +s50: F32, +s51: F32, +s52: F32, +s53: F32, +s54: F32, +s55: F32, +s56: F32, +s57: F32, +s58: F32, +s59: F32, +s60: F32, +s61: F32, +s62: F32, +s63: F32, +x0: F32, +x1: F32, +x2: F32, +x3: F32, +x4: F32, +x5: F32, +x6: F32, +x7: F32) -> PackedBuffers:
  (w, weight) = pair
  JWeight8{+w0, +w1, +w2, +w3, +w4, +w5, +w6, +w7} = weight
  packed_dot(x, w, o, row, col, cols, inner, end, U32.add(j, 1), F32.add(s0, F32.mul(x0, w0)), F32.add(s1, F32.mul(x0, w1)), F32.add(s2, F32.mul(x0, w2)), F32.add(s3, F32.mul(x0, w3)), F32.add(s4, F32.mul(x0, w4)), F32.add(s5, F32.mul(x0, w5)), F32.add(s6, F32.mul(x0, w6)), F32.add(s7, F32.mul(x0, w7)), F32.add(s8, F32.mul(x1, w0)), F32.add(s9, F32.mul(x1, w1)), F32.add(s10, F32.mul(x1, w2)), F32.add(s11, F32.mul(x1, w3)), F32.add(s12, F32.mul(x1, w4)), F32.add(s13, F32.mul(x1, w5)), F32.add(s14, F32.mul(x1, w6)), F32.add(s15, F32.mul(x1, w7)), F32.add(s16, F32.mul(x2, w0)), F32.add(s17, F32.mul(x2, w1)), F32.add(s18, F32.mul(x2, w2)), F32.add(s19, F32.mul(x2, w3)), F32.add(s20, F32.mul(x2, w4)), F32.add(s21, F32.mul(x2, w5)), F32.add(s22, F32.mul(x2, w6)), F32.add(s23, F32.mul(x2, w7)), F32.add(s24, F32.mul(x3, w0)), F32.add(s25, F32.mul(x3, w1)), F32.add(s26, F32.mul(x3, w2)), F32.add(s27, F32.mul(x3, w3)), F32.add(s28, F32.mul(x3, w4)), F32.add(s29, F32.mul(x3, w5)), F32.add(s30, F32.mul(x3, w6)), F32.add(s31, F32.mul(x3, w7)), F32.add(s32, F32.mul(x4, w0)), F32.add(s33, F32.mul(x4, w1)), F32.add(s34, F32.mul(x4, w2)), F32.add(s35, F32.mul(x4, w3)), F32.add(s36, F32.mul(x4, w4)), F32.add(s37, F32.mul(x4, w5)), F32.add(s38, F32.mul(x4, w6)), F32.add(s39, F32.mul(x4, w7)), F32.add(s40, F32.mul(x5, w0)), F32.add(s41, F32.mul(x5, w1)), F32.add(s42, F32.mul(x5, w2)), F32.add(s43, F32.mul(x5, w3)), F32.add(s44, F32.mul(x5, w4)), F32.add(s45, F32.mul(x5, w5)), F32.add(s46, F32.mul(x5, w6)), F32.add(s47, F32.mul(x5, w7)), F32.add(s48, F32.mul(x6, w0)), F32.add(s49, F32.mul(x6, w1)), F32.add(s50, F32.mul(x6, w2)), F32.add(s51, F32.mul(x6, w3)), F32.add(s52, F32.mul(x6, w4)), F32.add(s53, F32.mul(x6, w5)), F32.add(s54, F32.mul(x6, w6)), F32.add(s55, F32.mul(x6, w7)), F32.add(s56, F32.mul(x7, w0)), F32.add(s57, F32.mul(x7, w1)), F32.add(s58, F32.mul(x7, w2)), F32.add(s59, F32.mul(x7, w3)), F32.add(s60, F32.mul(x7, w4)), F32.add(s61, F32.mul(x7, w5)), F32.add(s62, F32.mul(x7, w6)), F32.add(s63, F32.mul(x7, w7)), U32.is_lt(U32.add(j, 1), inner))

def packed_join(a: PackedBuffers, b: PackedBuffers) -> PackedBuffers:
  JBuffers{xa, wa, oa} = a
  JBuffers{xb, wb, ob} = b
  JBuffers{Array.join(Input8, xa, xb), Array.join(Weight8, wa, wb), Array.join(Output64, oa, ob)}

@unsafe
def packed_step(x: Array<Input8>, w: Array<Weight8>, o: Array<Output64>,
                 +lo: U32, +hi: U32, +tiles_col: U32, +inner: U32, active: Bool) -> PackedBuffers:
  match active:
    case False{}:
      JBuffers{x, w, o}
    case True{}:
      row = U32.div(lo, tiles_col)
      col = U32.mod(lo, tiles_col)
      packed_dot(x, w, o, row, col, tiles_col, inner, hi, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, True{})

@unsafe
def packed_split(x: Array<Input8> & Array<Input8>, w: Array<Weight8> & Array<Weight8>, o: Array<Output64> & Array<Output64>,
                 +lo: U32, +hi: U32, +tiles_col: U32, +grain: U32, +inner: U32) -> PackedBuffers:
  (xa, xb) = x
  (wa, wb) = w
  (oa, ob) = o
  +mid = U32.add(lo, U32.div(U32.sub(hi, lo), 2))
  left right = packed_gemm(xa, wa, oa, lo, mid, tiles_col, grain, inner, U32.is_le(U32.sub(mid, lo), grain)) packed_gemm(xb, wb, ob, mid, hi, tiles_col, grain, inner, U32.is_le(U32.sub(hi, mid), grain))
  packed_join(left, right)

@unsafe
def packed_gemm(x: Array<Input8>, w: Array<Weight8>, o: Array<Output64>,
                +lo: U32, +hi: U32, +tiles_col: U32, +grain: U32, +inner: U32, leaf: Bool) -> PackedBuffers:
  match leaf:
    case True{}:
      row = U32.div(lo, tiles_col)
      col = U32.mod(lo, tiles_col)
      packed_dot(x, w, o, row, col, tiles_col, inner, hi, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, True{})
    case False{}:
      packed_split(Array.fork(Input8, x), Array.fork(Weight8, w), Array.fork(Output64, o), lo, hi, tiles_col, grain, inner)

def packed_input() -> IO(Array<Input8>):
  import "./bridge.c"

def packed_weights() -> IO(Array<Weight8>):
  import "./bridge.c"

def packed_out() -> IO(Array<Output64>):
  import "./bridge.c"

def packed_output(result: PackedBuffers) -> IO(Unit):
  import "./bridge.c"

def main() -> IO(Unit):
  do IO<Unit>:
    +tree : Candidates <- input()
    output(winner(tree))
    output(softmax(tree))
    vector : Features <- features()
    write_features(layernorm(vector, 384.0, 0.00001))
    rows : NormRows <- batch_features()
    write_batch(norm_rows(rows, 384.0, 0.00001))
    +tile : TileInput <- tile_input()
    +w : JuliaMatrix <- dense_weights()
    tile_output(dense_tile(tile, w))
    tile_output(dense_tile(tile, w))
    +tiles : InputTiles <- input_tiles()
    +matrix : JuliaMatrix <- dense_weights()
    output_tiles(dense_batch(tiles, matrix))
    output_tiles(dense_batch(tiles, matrix))
    px : Array<Input8> <- packed_input()
    pw : Array<Weight8> <- packed_weights()
    po : Array<Output64> <- packed_out()
    packed_output(packed_gemm(px, pw, po, 0, 1, 1, 1, 1, True{}))

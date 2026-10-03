import Base
import ./router.bend as R

# Runtime ABI invariant: each output leaf has exactly one 4x7 tile.
def output_tiles(result: R.TileResult) -> Nat:
  match result:
    case R.JTLeaf{_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _}:
      1n
    case R.JTFork{left, right}:
      Nat.add(output_tiles(left), output_tiles(right))

def matrix_tiles(weights: R.JuliaMatrix) -> Nat:
  match weights:
    case R.JMLeaf{ws}:
      1n
    case R.JMFork{left, right}:
      Nat.add(matrix_tiles(left), matrix_tiles(right))

# No flat dot-product branch may omit or duplicate an output tile.
law dot_tile_shape:
  for +xs: R.TileInput
  for ws: R.DenseWeights
  for s0: F32
  for s1: F32
  for s2: F32
  for s3: F32
  for s4: F32
  for s5: F32
  for s6: F32
  for s7: F32
  for s8: F32
  for s9: F32
  for s10: F32
  for s11: F32
  for s12: F32
  for s13: F32
  for s14: F32
  for s15: F32
  for s16: F32
  for s17: F32
  for s18: F32
  for s19: F32
  for s20: F32
  for s21: F32
  for s22: F32
  for s23: F32
  for s24: F32
  for s25: F32
  for s26: F32
  for s27: F32
  {output_tiles(R.dot_tile(xs, ws, s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24, s25, s26, s27)) == 1n : Nat}

# Fork/join must preserve the output tile count for every matrix/input tree.
law dense_shape:
  for +xs: R.TileInput
  for weights: R.JuliaMatrix
  {output_tiles(R.dense_tile(xs, weights)) == matrix_tiles(weights) : Nat}

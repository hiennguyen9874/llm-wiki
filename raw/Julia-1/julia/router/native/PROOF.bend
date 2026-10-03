import Base
import ./router.bend as R
import ./LAWS.bend as Laws

def Laws.dot_tile_shape(xs, ws, s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24, s25, s26, s27):
  match xs ws:
    case R.JTVal{+x0, +x1, +x2, +x3, xt} R.JWVal{+w0, +w1, +w2, +w3, +w4, +w5, +w6, wt}:
      Laws.dot_tile_shape(xt, wt, F32.add(s0, F32.mul(x0, w0)),
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
    case R.JTVal{_, _, _, _, _} R.JWEnd{}:
      {==}
    case R.JTEnd{} R.JWVal{_, _, _, _, _, _, _, _}:
      {==}
    case R.JTEnd{} R.JWEnd{}:
      {==}

def Laws.dense_shape(xs, weights):
  match weights:
    case R.JMLeaf{ws}:
      Laws.dot_tile_shape(xs, ws, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    case R.JMFork{+left, +right}:
      %Laws.dense_shape(xs, left) : {Nat.add(Laws.output_tiles(R.dense_tile(xs, left)), Laws.output_tiles(R.dense_tile(xs, right))) == Nat.add(_, Laws.matrix_tiles(right)) : Nat}
      %Laws.dense_shape(xs, right) : {Nat.add(Laws.output_tiles(R.dense_tile(xs, left)), Laws.output_tiles(R.dense_tile(xs, right))) == Nat.add(Laws.output_tiles(R.dense_tile(xs, left)), _) : Nat}
      {==}

# M0 spike — `/root/models/Qwen3.5-9B` on NVIDIA B200

load time 13s · text params 8.95B · hidden 4096 · weights 16.7 GB (incl. lm_head)

## Verbalizer table (bare, line-start single token)

| slot | verbalizer | token id | bare tokens | line-start tokens | ok |
|---|---|---|---|---|---|
| 0 | `false` | 3721 | [3721] | [198, 3721] | ✅ |
| 1 | `true` | 1802 | [1802] | [198, 1802] | ✅ |
| 2 | `0` | 15 | [15] | [198, 15] | ✅ |
| 3 | `1` | 16 | [16] | [198, 16] | ✅ |
| 4 | `2` | 17 | [17] | [198, 17] | ✅ |
| 5 | `3` | 18 | [18] | [198, 18] | ✅ |
| 6 | `4` | 19 | [19] | [198, 19] | ✅ |
| 7 | `5` | 20 | [20] | [198, 20] | ✅ |
| 8 | `A` | 32 | [32] | [198, 32] | ✅ |
| 9 | `B` | 33 | [33] | [198, 33] | ✅ |
| 10 | `C` | 34 | [34] | [198, 34] | ✅ |
| 11 | `D` | 35 | [35] | [198, 35] | ✅ |
| 12 | `E` | 36 | [36] | [198, 36] | ✅ |
| 13 | `F` | 37 | [37] | [198, 37] | ✅ |
| 14 | `G` | 38 | [38] | [198, 38] | ✅ |
| 15 | `H` | 39 | [39] | [198, 39] | ✅ |
| 16 | `I` | 40 | [40] | [198, 40] | ✅ |
| 17 | `J` | 41 | [41] | [198, 41] | ✅ |
| 18 | `K` | 42 | [42] | [198, 42] | ✅ |
| 19 | `L` | 43 | [43] | [198, 43] | ✅ |
| 20 | `M` | 44 | [44] | [198, 44] | ✅ |
| 21 | `N` | 45 | [45] | [198, 45] | ✅ |
| 22 | `O` | 46 | [46] | [198, 46] | ✅ |
| 23 | `P` | 47 | [47] | [198, 47] | ✅ |

## Linear leaves inside decoder layers (LoRA candidates)

| leaf | count |
|---|---|
| down_proj | 32 |
| gate_proj | 32 |
| in_proj_a | 24 |
| in_proj_b | 24 |
| in_proj_qkv | 24 |
| in_proj_z | 24 |
| k_proj | 8 |
| o_proj | 8 |
| out_proj | 24 |
| q_proj | 8 |
| up_proj | 32 |
| v_proj | 8 |

## Equivalence gate (step-0 head vs restricted decoding, fp32)

rows: 96 · max |Δp| = **1.490e-06** · gate 1e-5 → **PASS**

## Throughput (real length distribution, kind-stratified batches, fla kernels)

| mode | micro_batch | real tok/s | median tok/s | padded tok/s | samples/s | pad eff. | peak mem GB |
|---|---|---|---|---|---|---|---|
| fwd-only | 32 | 29716 | 30717 | 42178 | 219.5 | 0.70 | 17.1 |
| fwd-only | 128 | 29224 | 35661 | 46953 | 212.0 | 0.62 | 24.1 |

LoRA r=16 attached to ['in_proj_qkv', 'in_proj_z', 'in_proj_a', 'in_proj_b', 'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj', 'out_proj'] → 43.3M adapter params

| mode | micro_batch | real tok/s | median tok/s | padded tok/s | samples/s | pad eff. | peak mem GB |
|---|---|---|---|---|---|---|---|
| S2 fwd+bwd | 8 | 2576 | 1992 | 3708 | 17.5 | 0.69 | 67.0 |
| S2 fwd+bwd | 16 | 4036 | 3866 | 5206 | 36.1 | 0.78 | 100.3 |
| S2 fwd+bwd | 24 | 5069 | 4580 | 6350 | 48.1 | 0.80 | 77.2 |

**Projection** (best S2 config micro_batch=24, 5069 real tok/s): 1 epoch of train (84.6M tok) ≈ **4.64 h**; 2 epochs ≈ 9.27 h; 10% scan (2 ep) ≈ 56 min

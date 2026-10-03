# Evaluation — checkpoints/s2_9b_cooldown/best

base: `/root/models/Qwen3.5-9B` · temperature: yes · max_seq_len 1024

## Acceptance (DESIGN §8.3, main = test_set_30k)

**all rows**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.9938 | 0.8236 | ✅ |
| noul_brier_soft | <= 0.1 | 0.0022 | 0.0960 | ✅ |
| choice_top1 | >= 0.9 | 0.8836 | 0.5323 | ❌ |
| score_mae_expected | <= 0.35 | 0.1187 | 1.1297 | ✅ |
| kl | <= 0.15 | 0.0276 | 0.5100 | ✅ |
| ece | <= 0.03 | 0.0014 | 0.0942 | ✅ |
| ood KL ratio (ood/test_set_30k) | <= 2.0 | 7.526 | — | ❌ |

**excluding yuri_v1 exact-uniform placeholders (D1)**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.9938 | nan | ✅ |
| noul_brier_soft | <= 0.1 | 0.0026 | nan | ✅ |
| choice_top1 | >= 0.9 | 0.8836 | nan | ❌ |
| score_mae_expected | <= 0.35 | 0.1187 | nan | ✅ |
| kl | <= 0.15 | 0.0299 | nan | ✅ |
| ece | <= 0.03 | 0.0016 | nan | ✅ |
| ood KL ratio (ood/test_set_30k) | <= 2.0 | 6.966 | — | ❌ |

## test_set_30k

all rows: `n=29955 · kl=0.0276 · js=0.0072 · top1=0.9036 · ece=0.0014 · mce=0.0079 · noul_auroc=0.9938 · noul_brier_soft=0.0022 · noul_brier_hard=0.0761 · score_mae_expected=0.1187 · score_rps=0.0113 · choice_top1=0.8836 · choice_kl=0.0549`

excluding yuri_v1 placeholders (2260 rows): `n=27695 · kl=0.0299 · js=0.0078 · top1=0.9036 · ece=0.0016 · mce=0.0079 · noul_auroc=0.9938 · noul_brier_soft=0.0026 · noul_brier_hard=0.0761 · score_mae_expected=0.1187 · score_rps=0.0113 · choice_top1=0.8836 · choice_kl=0.0549`

throughput: 25870 tok/s · 242.6 rows/s

### test_set_30k by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 9199 | 0.055 | 0.884 | 0.003 | — | — | — | 0.884 |
| noul | 12229 | 0.006 | 0.959 | 0.002 | 0.994 | 0.002 | — | — |
| score | 8527 | 0.030 | 0.861 | 0.002 | — | — | 0.119 | — |

### test_set_30k by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 887 | 0.220 | 0.858 | 0.018 | — | — | — | 0.858 |
| openjev_v2 | noul | 1432 | 0.010 | 0.997 | 0.004 | 1.000 | 0.003 | — | — |
| yuri_v1 | noul | 2260 | 0.000 | — | 0.009 | — | 0.000 | — | — |
| yuri_v3 | choice | 8312 | 0.037 | 0.886 | 0.002 | — | — | — | 0.886 |
| yuri_v3 | noul | 8537 | 0.006 | 0.953 | 0.001 | 0.992 | 0.003 | — | — |
| yuri_v3 | score | 8527 | 0.030 | 0.861 | 0.002 | — | — | 0.119 | — |

### test_set_30k by family

| family | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| agent | 2583 | 0.023 | 0.897 | 0.003 | 0.994 | 0.002 | 0.123 | 0.877 |
| biology | 1654 | 0.024 | 0.898 | 0.004 | 0.998 | 0.002 | 0.148 | 0.902 |
| business | 2352 | 0.022 | 0.930 | 0.003 | 0.997 | 0.002 | 0.089 | 0.904 |
| chemistry | 1333 | 0.020 | 0.931 | 0.005 | 0.997 | 0.002 | 0.113 | 0.946 |
| genomics | 1914 | 0.026 | 0.893 | 0.005 | 0.991 | 0.003 | 0.114 | 0.882 |
| knowledge | 4807 | 0.014 | 0.888 | 0.005 | 0.983 | 0.001 | 0.132 | 0.879 |
| medical | 2120 | 0.024 | 0.901 | 0.004 | 0.994 | 0.002 | 0.092 | 0.865 |
| openjev | 2319 | 0.090 | 0.945 | 0.007 | 1.000 | 0.003 | — | 0.858 |
| physics | 1656 | 0.023 | 0.881 | 0.004 | 0.992 | 0.002 | 0.117 | 0.869 |
| science | 1667 | 0.026 | 0.890 | 0.005 | 0.989 | 0.002 | 0.136 | 0.906 |
| spatial | 1647 | 0.025 | 0.886 | 0.007 | 0.984 | 0.002 | 0.119 | 0.850 |
| structured | 1668 | 0.025 | 0.885 | 0.004 | 0.983 | 0.004 | 0.152 | 0.881 |
| technical | 2581 | 0.025 | 0.918 | 0.004 | 0.993 | 0.002 | 0.089 | 0.878 |
| theology | 1654 | 0.025 | 0.893 | 0.005 | 0.992 | 0.002 | 0.144 | 0.909 |

## test

all rows: `n=14261 · kl=0.0252 · js=0.0065 · top1=0.9076 · ece=0.0029 · mce=0.0243 · noul_auroc=0.9948 · noul_brier_soft=0.0018 · noul_brier_hard=0.0653 · score_mae_expected=0.1165 · score_rps=0.0111 · choice_top1=0.8751 · choice_kl=0.0622`

excluding yuri_v1 placeholders (2951 rows): `n=11310 · kl=0.0317 · js=0.0082 · top1=0.9076 · ece=0.0014 · mce=0.0243 · noul_auroc=0.9948 · noul_brier_soft=0.0029 · noul_brier_hard=0.0653 · score_mae_expected=0.1165 · score_rps=0.0111 · choice_top1=0.8751 · choice_kl=0.0622`

throughput: 26259 tok/s · 204.4 rows/s

### test by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3620 | 0.062 | 0.875 | 0.004 | — | — | — | 0.875 |
| noul | 7298 | 0.005 | 0.962 | 0.004 | 0.995 | 0.002 | — | — |
| score | 3343 | 0.030 | 0.872 | 0.003 | — | — | 0.116 | — |

### test by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 457 | 0.238 | 0.860 | 0.018 | — | — | — | 0.860 |
| openjev_v2 | noul | 1139 | 0.012 | 0.994 | 0.004 | 1.000 | 0.004 | — | — |
| yuri_v1 | noul | 2951 | 0.000 | — | 0.009 | — | 0.000 | — | — |
| yuri_v3 | choice | 3163 | 0.037 | 0.877 | 0.003 | — | — | — | 0.877 |
| yuri_v3 | noul | 3208 | 0.006 | 0.951 | 0.003 | 0.992 | 0.003 | — | — |
| yuri_v3 | score | 3343 | 0.030 | 0.872 | 0.003 | — | — | 0.116 | — |

## ood

all rows: `n=13058 · kl=0.2080 · js=0.0454 · top1=0.9164 · ece=0.0288 · mce=0.3191 · noul_auroc=0.9852 · noul_brier_soft=0.0427 · noul_brier_hard=0.0427 · score_mae_expected=0.7871 · score_rps=0.5324 · choice_top1=0.8397 · choice_kl=0.2989`

excluding yuri_v1 placeholders (0 rows): `n=13058 · kl=0.2080 · js=0.0454 · top1=0.9164 · ece=0.0288 · mce=0.3191 · noul_auroc=0.9852 · noul_brier_soft=0.0427 · noul_brier_hard=0.0427 · score_mae_expected=0.7871 · score_rps=0.5324 · choice_top1=0.8397 · choice_kl=0.2989`

throughput: 27200 tok/s · 102.6 rows/s

### ood by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3219 | 0.299 | 0.840 | 0.044 | — | — | — | 0.840 |
| noul | 9767 | 0.170 | 0.945 | 0.024 | 0.985 | 0.043 | — | — |
| score | 72 | 1.278 | 0.444 | 0.236 | — | — | 0.787 | — |

### ood by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 3219 | 0.299 | 0.840 | 0.044 | — | — | — | 0.840 |
| openjev_v2 | noul | 9767 | 0.170 | 0.945 | 0.024 | 0.985 | 0.043 | — | — |
| openjev_v2 | score | 72 | 1.278 | 0.444 | 0.236 | — | — | 0.787 | — |

## validation

all rows: `n=14111 · kl=0.0260 · js=0.0067 · top1=0.9111 · ece=0.0030 · mce=0.0097 · noul_auroc=0.9943 · noul_brier_soft=0.0019 · noul_brier_hard=0.0656 · score_mae_expected=0.1196 · score_rps=0.0115 · choice_top1=0.8843 · choice_kl=0.0644`

excluding yuri_v1 placeholders (2920 rows): `n=11191 · kl=0.0327 · js=0.0084 · top1=0.9111 · ece=0.0020 · mce=0.0097 · noul_auroc=0.9943 · noul_brier_soft=0.0031 · noul_brier_hard=0.0656 · score_mae_expected=0.1196 · score_rps=0.0115 · choice_top1=0.8843 · choice_kl=0.0644`

throughput: 26303 tok/s · 204.2 rows/s

### validation by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3592 | 0.064 | 0.884 | 0.005 | — | — | — | 0.884 |
| noul | 7318 | 0.005 | 0.963 | 0.004 | 0.994 | 0.002 | — | — |
| score | 3201 | 0.030 | 0.870 | 0.003 | — | — | 0.120 | — |

### validation by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 463 | 0.239 | 0.859 | 0.027 | — | — | — | 0.859 |
| openjev_v2 | noul | 1167 | 0.015 | 0.992 | 0.005 | 1.000 | 0.005 | — | — |
| yuri_v1 | noul | 2920 | 0.000 | — | 0.009 | — | 0.000 | — | — |
| yuri_v3 | choice | 3129 | 0.039 | 0.888 | 0.003 | — | — | — | 0.888 |
| yuri_v3 | noul | 3231 | 0.006 | 0.952 | 0.002 | 0.992 | 0.003 | — | — |
| yuri_v3 | score | 3201 | 0.030 | 0.870 | 0.003 | — | — | 0.120 | — |

## Choice permutation consistency

`{"n_rows": 1000, "mean_max_abs_diff": 0.030732551589608192, "p90_max_abs_diff": 0.06812191009521484, "top1_flip_rate": 0.04675}`

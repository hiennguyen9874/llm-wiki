# Evaluation — checkpoints/s2_9b_epoch1/best

base: `/root/models/Qwen3.5-9B` · temperature: yes · max_seq_len 1024

## Acceptance (DESIGN §8.3, main = test_set_30k)

**all rows**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.9958 | 0.8236 | ✅ |
| noul_brier_soft | <= 0.1 | 0.0015 | 0.0960 | ✅ |
| choice_top1 | >= 0.9 | 0.8980 | 0.5323 | ❌ |
| score_mae_expected | <= 0.35 | 0.1030 | 1.1297 | ✅ |
| kl | <= 0.15 | 0.0210 | 0.5100 | ✅ |
| ece | <= 0.03 | 0.0007 | 0.0942 | ✅ |
| ood KL ratio (ood/test_set_30k) | <= 2.0 | 11.106 | — | ❌ |

**excluding yuri_v1 exact-uniform placeholders (D1)**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.9958 | nan | ✅ |
| noul_brier_soft | <= 0.1 | 0.0019 | nan | ✅ |
| choice_top1 | >= 0.9 | 0.8980 | nan | ❌ |
| score_mae_expected | <= 0.35 | 0.1030 | nan | ✅ |
| kl | <= 0.15 | 0.0227 | nan | ✅ |
| ece | <= 0.03 | 0.0009 | nan | ✅ |
| ood KL ratio (ood/test_set_30k) | <= 2.0 | 10.271 | — | ❌ |

## test_set_30k

all rows: `n=29955 · kl=0.0210 · js=0.0054 · top1=0.9179 · ece=0.0007 · mce=0.0539 · noul_auroc=0.9958 · noul_brier_soft=0.0015 · noul_brier_hard=0.0744 · score_mae_expected=0.1030 · score_rps=0.0085 · choice_top1=0.8980 · choice_kl=0.0422`

excluding yuri_v1 placeholders (2260 rows): `n=27695 · kl=0.0227 · js=0.0059 · top1=0.9179 · ece=0.0009 · mce=0.0539 · noul_auroc=0.9958 · noul_brier_soft=0.0019 · noul_brier_hard=0.0744 · score_mae_expected=0.1030 · score_rps=0.0085 · choice_top1=0.8980 · choice_kl=0.0422`

throughput: 25820 tok/s · 242.1 rows/s

### test_set_30k by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 9199 | 0.042 | 0.898 | 0.002 | — | — | — | 0.898 |
| noul | 12229 | 0.004 | 0.967 | 0.002 | 0.996 | 0.002 | — | — |
| score | 8527 | 0.023 | 0.883 | 0.002 | — | — | 0.103 | — |

### test_set_30k by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 887 | 0.176 | 0.857 | 0.020 | — | — | — | 0.857 |
| openjev_v2 | noul | 1432 | 0.004 | 0.998 | 0.003 | 1.000 | 0.001 | — | — |
| yuri_v1 | noul | 2260 | 0.000 | — | 0.005 | — | 0.000 | — | — |
| yuri_v3 | choice | 8312 | 0.028 | 0.902 | 0.002 | — | — | — | 0.902 |
| yuri_v3 | noul | 8537 | 0.005 | 0.961 | 0.001 | 0.994 | 0.002 | — | — |
| yuri_v3 | score | 8527 | 0.023 | 0.883 | 0.002 | — | — | 0.103 | — |

### test_set_30k by family

| family | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| agent | 2583 | 0.018 | 0.914 | 0.003 | 0.996 | 0.002 | 0.104 | 0.896 |
| biology | 1654 | 0.018 | 0.913 | 0.006 | 0.999 | 0.002 | 0.131 | 0.922 |
| business | 2352 | 0.017 | 0.942 | 0.003 | 0.998 | 0.001 | 0.074 | 0.919 |
| chemistry | 1333 | 0.015 | 0.934 | 0.003 | 0.997 | 0.002 | 0.099 | 0.939 |
| genomics | 1914 | 0.019 | 0.910 | 0.003 | 0.995 | 0.002 | 0.104 | 0.895 |
| knowledge | 4807 | 0.011 | 0.907 | 0.004 | 0.992 | 0.001 | 0.116 | 0.894 |
| medical | 2120 | 0.018 | 0.921 | 0.005 | 0.996 | 0.002 | 0.080 | 0.890 |
| openjev | 2319 | 0.070 | 0.945 | 0.008 | 1.000 | 0.001 | — | 0.857 |
| physics | 1656 | 0.018 | 0.895 | 0.002 | 0.993 | 0.002 | 0.101 | 0.873 |
| science | 1667 | 0.019 | 0.903 | 0.005 | 0.992 | 0.002 | 0.118 | 0.917 |
| spatial | 1647 | 0.019 | 0.907 | 0.005 | 0.989 | 0.002 | 0.101 | 0.880 |
| structured | 1668 | 0.020 | 0.905 | 0.005 | 0.988 | 0.003 | 0.135 | 0.899 |
| technical | 2581 | 0.019 | 0.925 | 0.003 | 0.994 | 0.002 | 0.077 | 0.897 |
| theology | 1654 | 0.018 | 0.915 | 0.003 | 0.995 | 0.002 | 0.124 | 0.928 |

## test

all rows: `n=14261 · kl=0.0180 · js=0.0047 · top1=0.9201 · ece=0.0026 · mce=0.0061 · noul_auroc=0.9968 · noul_brier_soft=0.0011 · noul_brier_hard=0.0631 · score_mae_expected=0.0998 · score_rps=0.0083 · choice_top1=0.8945 · choice_kl=0.0442`

excluding yuri_v1 placeholders (2951 rows): `n=11310 · kl=0.0227 · js=0.0059 · top1=0.9201 · ece=0.0023 · mce=0.0059 · noul_auroc=0.9968 · noul_brier_soft=0.0018 · noul_brier_hard=0.0631 · score_mae_expected=0.0998 · score_rps=0.0083 · choice_top1=0.8945 · choice_kl=0.0442`

throughput: 26354 tok/s · 205.1 rows/s

### test by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3620 | 0.044 | 0.895 | 0.003 | — | — | — | 0.895 |
| noul | 7298 | 0.003 | 0.969 | 0.003 | 0.997 | 0.001 | — | — |
| score | 3343 | 0.023 | 0.885 | 0.002 | — | — | 0.100 | — |

### test by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 457 | 0.160 | 0.873 | 0.025 | — | — | — | 0.873 |
| openjev_v2 | noul | 1139 | 0.005 | 0.997 | 0.002 | 1.000 | 0.001 | — | — |
| yuri_v1 | noul | 2951 | 0.000 | — | 0.005 | — | 0.000 | — | — |
| yuri_v3 | choice | 3163 | 0.027 | 0.898 | 0.003 | — | — | — | 0.898 |
| yuri_v3 | noul | 3208 | 0.005 | 0.958 | 0.002 | 0.995 | 0.002 | — | — |
| yuri_v3 | score | 3343 | 0.023 | 0.885 | 0.002 | — | — | 0.100 | — |

## ood

all rows: `n=13058 · kl=0.2335 · js=0.0410 · top1=0.9181 · ece=0.0396 · mce=0.3032 · noul_auroc=0.9886 · noul_brier_soft=0.0416 · noul_brier_hard=0.0416 · score_mae_expected=0.7484 · score_rps=0.5016 · choice_top1=0.8372 · choice_kl=0.3513`

excluding yuri_v1 placeholders (0 rows): `n=13058 · kl=0.2335 · js=0.0410 · top1=0.9181 · ece=0.0396 · mce=0.3032 · noul_auroc=0.9886 · noul_brier_soft=0.0416 · noul_brier_hard=0.0416 · score_mae_expected=0.7484 · score_rps=0.5016 · choice_top1=0.8372 · choice_kl=0.3513`

throughput: 27251 tok/s · 102.8 rows/s

### ood by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3219 | 0.351 | 0.837 | 0.055 | — | — | — | 0.837 |
| noul | 9767 | 0.187 | 0.949 | 0.033 | 0.989 | 0.042 | — | — |
| score | 72 | 1.236 | 0.347 | 0.246 | — | — | 0.748 | — |

### ood by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 3219 | 0.351 | 0.837 | 0.055 | — | — | — | 0.837 |
| openjev_v2 | noul | 9767 | 0.187 | 0.949 | 0.033 | 0.989 | 0.042 | — | — |
| openjev_v2 | score | 72 | 1.236 | 0.347 | 0.246 | — | — | 0.748 | — |

## validation

all rows: `n=14111 · kl=0.0190 · js=0.0049 · top1=0.9229 · ece=0.0028 · mce=0.0099 · noul_auroc=0.9961 · noul_brier_soft=0.0013 · noul_brier_hard=0.0636 · score_mae_expected=0.1021 · score_rps=0.0083 · choice_top1=0.8985 · choice_kl=0.0458`

excluding yuri_v1 placeholders (2920 rows): `n=11191 · kl=0.0239 · js=0.0061 · top1=0.9229 · ece=0.0025 · mce=0.0099 · noul_auroc=0.9961 · noul_brier_soft=0.0021 · noul_brier_hard=0.0636 · score_mae_expected=0.1021 · score_rps=0.0083 · choice_top1=0.8985 · choice_kl=0.0458`

throughput: 26305 tok/s · 204.2 rows/s

### validation by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3592 | 0.046 | 0.899 | 0.004 | — | — | — | 0.899 |
| noul | 7318 | 0.004 | 0.971 | 0.003 | 0.996 | 0.001 | — | — |
| score | 3201 | 0.023 | 0.885 | 0.004 | — | — | 0.102 | — |

### validation by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 463 | 0.165 | 0.875 | 0.030 | — | — | — | 0.875 |
| openjev_v2 | noul | 1167 | 0.013 | 0.997 | 0.003 | 1.000 | 0.003 | — | — |
| yuri_v1 | noul | 2920 | 0.000 | — | 0.005 | — | 0.000 | — | — |
| yuri_v3 | choice | 3129 | 0.028 | 0.902 | 0.002 | — | — | — | 0.902 |
| yuri_v3 | noul | 3231 | 0.005 | 0.962 | 0.001 | 0.994 | 0.002 | — | — |
| yuri_v3 | score | 3201 | 0.023 | 0.885 | 0.004 | — | — | 0.102 | — |

## Choice permutation consistency

`{"n_rows": 1000, "mean_max_abs_diff": 0.024422522634267807, "p90_max_abs_diff": 0.054626550525426865, "top1_flip_rate": 0.0385}`

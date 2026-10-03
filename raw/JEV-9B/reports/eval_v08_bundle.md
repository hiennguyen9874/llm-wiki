# Evaluation — export exports/jev-judge-qwen35-9b-v0.8

base: `/root/models/Qwen3.5-9B` · temperature: yes · max_seq_len 1024

## Acceptance (DESIGN §8.3, main = test_set_30k)

**all rows**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.9958 | nan | ✅ |
| noul_brier_soft | <= 0.1 | 0.0015 | nan | ✅ |
| choice_top1 | >= 0.9 | 0.8975 | nan | ❌ |
| score_mae_expected | <= 0.35 | 0.1030 | nan | ✅ |
| kl | <= 0.15 | 0.0211 | nan | ✅ |
| ece | <= 0.03 | 0.0008 | nan | ✅ |

**excluding yuri_v1 exact-uniform placeholders (D1)**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.9958 | nan | ✅ |
| noul_brier_soft | <= 0.1 | 0.0019 | nan | ✅ |
| choice_top1 | >= 0.9 | 0.8975 | nan | ❌ |
| score_mae_expected | <= 0.35 | 0.1030 | nan | ✅ |
| kl | <= 0.15 | 0.0228 | nan | ✅ |
| ece | <= 0.03 | 0.0010 | nan | ✅ |

## test_set_30k

all rows: `n=29955 · kl=0.0211 · js=0.0054 · top1=0.9176 · ece=0.0008 · mce=0.0557 · noul_auroc=0.9958 · noul_brier_soft=0.0015 · noul_brier_hard=0.0744 · score_mae_expected=0.1030 · score_rps=0.0084 · choice_top1=0.8975 · choice_kl=0.0423`

excluding yuri_v1 placeholders (2260 rows): `n=27695 · kl=0.0228 · js=0.0059 · top1=0.9176 · ece=0.0010 · mce=0.0557 · noul_auroc=0.9958 · noul_brier_soft=0.0019 · noul_brier_hard=0.0744 · score_mae_expected=0.1030 · score_rps=0.0084 · choice_top1=0.8975 · choice_kl=0.0423`

throughput: 43375 tok/s · 406.7 rows/s

### test_set_30k by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 9199 | 0.042 | 0.897 | 0.002 | — | — | — | 0.897 |
| noul | 12229 | 0.004 | 0.967 | 0.002 | 0.996 | 0.002 | — | — |
| score | 8527 | 0.023 | 0.882 | 0.002 | — | — | 0.103 | — |

### test_set_30k by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 887 | 0.176 | 0.858 | 0.021 | — | — | — | 0.858 |
| openjev_v2 | noul | 1432 | 0.004 | 0.997 | 0.003 | 1.000 | 0.001 | — | — |
| yuri_v1 | noul | 2260 | 0.000 | — | 0.005 | — | 0.000 | — | — |
| yuri_v3 | choice | 8312 | 0.028 | 0.902 | 0.002 | — | — | — | 0.902 |
| yuri_v3 | noul | 8537 | 0.005 | 0.962 | 0.001 | 0.994 | 0.002 | — | — |
| yuri_v3 | score | 8527 | 0.023 | 0.882 | 0.002 | — | — | 0.103 | — |

### test_set_30k by family

| family | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| agent | 2583 | 0.018 | 0.915 | 0.003 | 0.996 | 0.002 | 0.104 | 0.897 |
| biology | 1654 | 0.018 | 0.912 | 0.006 | 0.999 | 0.002 | 0.130 | 0.922 |
| business | 2352 | 0.017 | 0.944 | 0.002 | 0.998 | 0.001 | 0.074 | 0.920 |
| chemistry | 1333 | 0.015 | 0.932 | 0.003 | 0.997 | 0.002 | 0.099 | 0.939 |
| genomics | 1914 | 0.019 | 0.907 | 0.003 | 0.995 | 0.002 | 0.104 | 0.892 |
| knowledge | 4807 | 0.011 | 0.908 | 0.004 | 0.992 | 0.001 | 0.116 | 0.893 |
| medical | 2120 | 0.018 | 0.922 | 0.005 | 0.996 | 0.002 | 0.080 | 0.891 |
| openjev | 2319 | 0.070 | 0.945 | 0.008 | 1.000 | 0.001 | — | 0.858 |
| physics | 1656 | 0.018 | 0.896 | 0.002 | 0.994 | 0.002 | 0.101 | 0.875 |
| science | 1667 | 0.019 | 0.902 | 0.006 | 0.992 | 0.002 | 0.118 | 0.913 |
| spatial | 1647 | 0.019 | 0.903 | 0.005 | 0.989 | 0.002 | 0.102 | 0.874 |
| structured | 1668 | 0.020 | 0.907 | 0.005 | 0.988 | 0.003 | 0.135 | 0.899 |
| technical | 2581 | 0.019 | 0.925 | 0.003 | 0.994 | 0.002 | 0.077 | 0.896 |
| theology | 1654 | 0.018 | 0.913 | 0.003 | 0.995 | 0.002 | 0.124 | 0.926 |

# Evaluation — export exports/jev-judge-qwen38-27b-v0.8

base: `/root/models/Qwen3.8-27B` · temperature: yes · max_seq_len 1024

## Acceptance (DESIGN §8.3, main = test_set_30k)

**all rows**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.9961 | nan | ✅ |
| noul_brier_soft | <= 0.1 | 0.0013 | nan | ✅ |
| choice_top1 | >= 0.9 | 0.9041 | nan | ✅ |
| score_mae_expected | <= 0.35 | 0.0976 | nan | ✅ |
| kl | <= 0.15 | 0.0185 | nan | ✅ |
| ece | <= 0.03 | 0.0011 | nan | ✅ |

**excluding yuri_v1 exact-uniform placeholders (D1)**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.9961 | nan | ✅ |
| noul_brier_soft | <= 0.1 | 0.0016 | nan | ✅ |
| choice_top1 | >= 0.9 | 0.9041 | nan | ✅ |
| score_mae_expected | <= 0.35 | 0.0976 | nan | ✅ |
| kl | <= 0.15 | 0.0201 | nan | ✅ |
| ece | <= 0.03 | 0.0013 | nan | ✅ |

## test_set_30k

all rows: `n=29955 · kl=0.0185 · js=0.0048 · top1=0.9220 · ece=0.0011 · mce=0.0043 · noul_auroc=0.9961 · noul_brier_soft=0.0013 · noul_brier_hard=0.0741 · score_mae_expected=0.0976 · score_rps=0.0077 · choice_top1=0.9041 · choice_kl=0.0364`

excluding yuri_v1 placeholders (2260 rows): `n=27695 · kl=0.0201 · js=0.0052 · top1=0.9220 · ece=0.0013 · mce=0.0043 · noul_auroc=0.9961 · noul_brier_soft=0.0016 · noul_brier_hard=0.0741 · score_mae_expected=0.0976 · score_rps=0.0077 · choice_top1=0.9041 · choice_kl=0.0364`

throughput: 14321 tok/s · 134.3 rows/s

### test_set_30k by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 9199 | 0.036 | 0.904 | 0.003 | — | — | — | 0.904 |
| noul | 12229 | 0.003 | 0.966 | 0.002 | 0.996 | 0.001 | — | — |
| score | 8527 | 0.021 | 0.891 | 0.003 | — | — | 0.098 | — |

### test_set_30k by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 887 | 0.146 | 0.885 | 0.020 | — | — | — | 0.885 |
| openjev_v2 | noul | 1432 | 0.003 | 0.999 | 0.002 | 1.000 | 0.001 | — | — |
| yuri_v1 | noul | 2260 | 0.000 | — | 0.004 | — | 0.000 | — | — |
| yuri_v3 | choice | 8312 | 0.025 | 0.906 | 0.003 | — | — | — | 0.906 |
| yuri_v3 | noul | 8537 | 0.004 | 0.960 | 0.001 | 0.995 | 0.002 | — | — |
| yuri_v3 | score | 8527 | 0.021 | 0.891 | 0.003 | — | — | 0.098 | — |

### test_set_30k by family

| family | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| agent | 2583 | 0.016 | 0.920 | 0.002 | 0.995 | 0.002 | 0.099 | 0.894 |
| biology | 1654 | 0.016 | 0.916 | 0.004 | 0.998 | 0.002 | 0.123 | 0.917 |
| business | 2352 | 0.016 | 0.939 | 0.003 | 0.997 | 0.001 | 0.071 | 0.922 |
| chemistry | 1333 | 0.013 | 0.945 | 0.004 | 0.998 | 0.002 | 0.088 | 0.948 |
| genomics | 1914 | 0.018 | 0.917 | 0.005 | 0.993 | 0.002 | 0.098 | 0.915 |
| knowledge | 4807 | 0.010 | 0.912 | 0.002 | 0.990 | 0.001 | 0.110 | 0.907 |
| medical | 2120 | 0.016 | 0.921 | 0.006 | 0.995 | 0.002 | 0.078 | 0.887 |
| openjev | 2319 | 0.058 | 0.956 | 0.008 | 1.000 | 0.001 | — | 0.885 |
| physics | 1656 | 0.016 | 0.909 | 0.003 | 0.995 | 0.001 | 0.097 | 0.908 |
| science | 1667 | 0.017 | 0.907 | 0.005 | 0.992 | 0.001 | 0.115 | 0.915 |
| spatial | 1647 | 0.017 | 0.913 | 0.005 | 0.991 | 0.002 | 0.094 | 0.880 |
| structured | 1668 | 0.018 | 0.911 | 0.004 | 0.989 | 0.003 | 0.123 | 0.886 |
| technical | 2581 | 0.017 | 0.923 | 0.004 | 0.995 | 0.002 | 0.074 | 0.893 |
| theology | 1654 | 0.016 | 0.910 | 0.004 | 0.996 | 0.002 | 0.120 | 0.928 |

# Evaluation — checkpoints/s2_27b/best

base: `/root/models/Qwen3.8-27B` · temperature: yes · max_seq_len 1024

## Acceptance (DESIGN §8.3, main = test_set_30k)

**all rows**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.9961 | 0.8763 | ✅ |
| noul_brier_soft | <= 0.1 | 0.0013 | 0.0628 | ✅ |
| choice_top1 | >= 0.9 | 0.9034 | 0.5814 | ✅ |
| score_mae_expected | <= 0.35 | 0.0976 | 0.8420 | ✅ |
| kl | <= 0.15 | 0.0186 | 0.4296 | ✅ |
| ece | <= 0.03 | 0.0009 | 0.0501 | ✅ |
| ood KL ratio (ood/test_set_30k) | <= 2.0 | 5.620 | — | ❌ |

**excluding yuri_v1 exact-uniform placeholders (D1)**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.9961 | 0.8763 | ✅ |
| noul_brier_soft | <= 0.1 | 0.0016 | 0.0552 | ✅ |
| choice_top1 | >= 0.9 | 0.9034 | 0.5814 | ✅ |
| score_mae_expected | <= 0.35 | 0.0976 | 0.8420 | ✅ |
| kl | <= 0.15 | 0.0201 | 0.4411 | ✅ |
| ece | <= 0.03 | 0.0013 | 0.0307 | ✅ |
| ood KL ratio (ood/test_set_30k) | <= 2.0 | 5.197 | — | ❌ |

## test_set_30k

all rows: `n=29955 · kl=0.0186 · js=0.0048 · top1=0.9215 · ece=0.0009 · mce=0.0030 · noul_auroc=0.9961 · noul_brier_soft=0.0013 · noul_brier_hard=0.0741 · score_mae_expected=0.0976 · score_rps=0.0077 · choice_top1=0.9034 · choice_kl=0.0365`

excluding yuri_v1 placeholders (2260 rows): `n=27695 · kl=0.0201 · js=0.0052 · top1=0.9215 · ece=0.0013 · mce=0.0030 · noul_auroc=0.9961 · noul_brier_soft=0.0016 · noul_brier_hard=0.0741 · score_mae_expected=0.0976 · score_rps=0.0077 · choice_top1=0.9034 · choice_kl=0.0365`

throughput: 8687 tok/s · 81.5 rows/s

### test_set_30k by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 9199 | 0.036 | 0.903 | 0.003 | — | — | — | 0.903 |
| noul | 12229 | 0.003 | 0.965 | 0.002 | 0.996 | 0.001 | — | — |
| score | 8527 | 0.021 | 0.891 | 0.003 | — | — | 0.098 | — |

### test_set_30k by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 887 | 0.146 | 0.888 | 0.022 | — | — | — | 0.888 |
| openjev_v2 | noul | 1432 | 0.003 | 0.999 | 0.002 | 1.000 | 0.001 | — | — |
| yuri_v1 | noul | 2260 | 0.000 | — | 0.003 | — | 0.000 | — | — |
| yuri_v3 | choice | 8312 | 0.025 | 0.905 | 0.002 | — | — | — | 0.905 |
| yuri_v3 | noul | 8537 | 0.004 | 0.959 | 0.001 | 0.995 | 0.002 | — | — |
| yuri_v3 | score | 8527 | 0.021 | 0.891 | 0.003 | — | — | 0.098 | — |

### test_set_30k by family

| family | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| agent | 2583 | 0.016 | 0.919 | 0.002 | 0.995 | 0.002 | 0.099 | 0.894 |
| biology | 1654 | 0.016 | 0.913 | 0.004 | 0.998 | 0.002 | 0.124 | 0.911 |
| business | 2352 | 0.016 | 0.939 | 0.003 | 0.998 | 0.001 | 0.071 | 0.921 |
| chemistry | 1333 | 0.013 | 0.942 | 0.003 | 0.998 | 0.002 | 0.088 | 0.948 |
| genomics | 1914 | 0.018 | 0.918 | 0.005 | 0.993 | 0.002 | 0.098 | 0.914 |
| knowledge | 4807 | 0.010 | 0.910 | 0.002 | 0.990 | 0.001 | 0.109 | 0.906 |
| medical | 2120 | 0.016 | 0.920 | 0.006 | 0.995 | 0.002 | 0.078 | 0.882 |
| openjev | 2319 | 0.058 | 0.958 | 0.009 | 1.000 | 0.001 | — | 0.888 |
| physics | 1656 | 0.016 | 0.909 | 0.003 | 0.995 | 0.001 | 0.097 | 0.906 |
| science | 1667 | 0.017 | 0.907 | 0.005 | 0.992 | 0.001 | 0.115 | 0.913 |
| spatial | 1647 | 0.017 | 0.913 | 0.005 | 0.991 | 0.002 | 0.094 | 0.882 |
| structured | 1668 | 0.018 | 0.909 | 0.003 | 0.989 | 0.003 | 0.123 | 0.886 |
| technical | 2581 | 0.018 | 0.924 | 0.004 | 0.995 | 0.002 | 0.074 | 0.894 |
| theology | 1654 | 0.016 | 0.910 | 0.004 | 0.996 | 0.002 | 0.119 | 0.926 |

## test

all rows: `n=14261 · kl=0.0170 · js=0.0044 · top1=0.9231 · ece=0.0022 · mce=0.0107 · noul_auroc=0.9972 · noul_brier_soft=0.0009 · noul_brier_hard=0.0627 · score_mae_expected=0.0966 · score_rps=0.0076 · choice_top1=0.8967 · choice_kl=0.0434`

excluding yuri_v1 placeholders (2951 rows): `n=11310 · kl=0.0214 · js=0.0056 · top1=0.9231 · ece=0.0019 · mce=0.0107 · noul_auroc=0.9972 · noul_brier_soft=0.0014 · noul_brier_hard=0.0627 · score_mae_expected=0.0966 · score_rps=0.0076 · choice_top1=0.8967 · choice_kl=0.0434`

throughput: 8852 tok/s · 68.9 rows/s

### test by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3620 | 0.043 | 0.897 | 0.005 | — | — | — | 0.897 |
| noul | 7298 | 0.002 | 0.971 | 0.003 | 0.997 | 0.001 | — | — |
| score | 3343 | 0.021 | 0.889 | 0.002 | — | — | 0.097 | — |

### test by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 457 | 0.172 | 0.875 | 0.018 | — | — | — | 0.875 |
| openjev_v2 | noul | 1139 | 0.003 | 0.998 | 0.002 | 1.000 | 0.001 | — | — |
| yuri_v1 | noul | 2951 | 0.000 | — | 0.004 | — | 0.000 | — | — |
| yuri_v3 | choice | 3163 | 0.025 | 0.900 | 0.005 | — | — | — | 0.900 |
| yuri_v3 | noul | 3208 | 0.004 | 0.962 | 0.002 | 0.995 | 0.002 | — | — |
| yuri_v3 | score | 3343 | 0.021 | 0.889 | 0.002 | — | — | 0.097 | — |

## ood

all rows: `n=13058 · kl=0.1043 · js=0.0266 · top1=0.9419 · ece=0.0067 · mce=0.2267 · noul_auroc=0.9964 · noul_brier_soft=0.0207 · noul_brier_hard=0.0207 · score_mae_expected=0.5168 · score_rps=0.3693 · choice_top1=0.8593 · choice_kl=0.1875`

excluding yuri_v1 placeholders (0 rows): `n=13058 · kl=0.1043 · js=0.0266 · top1=0.9419 · ece=0.0067 · mce=0.2267 · noul_auroc=0.9964 · noul_brier_soft=0.0207 · noul_brier_hard=0.0207 · score_mae_expected=0.5168 · score_rps=0.3693 · choice_top1=0.8593 · choice_kl=0.1875`

throughput: 9340 tok/s · 35.2 rows/s

### ood by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3219 | 0.187 | 0.859 | 0.023 | — | — | — | 0.859 |
| noul | 9767 | 0.071 | 0.972 | 0.005 | 0.996 | 0.021 | — | — |
| score | 72 | 0.884 | 0.597 | 0.094 | — | — | 0.517 | — |

### ood by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 3219 | 0.187 | 0.859 | 0.023 | — | — | — | 0.859 |
| openjev_v2 | noul | 9767 | 0.071 | 0.972 | 0.005 | 0.996 | 0.021 | — | — |
| openjev_v2 | score | 72 | 0.884 | 0.597 | 0.094 | — | — | 0.517 | — |

## validation

all rows: `n=14111 · kl=0.0170 · js=0.0045 · top1=0.9261 · ece=0.0020 · mce=0.0074 · noul_auroc=0.9962 · noul_brier_soft=0.0012 · noul_brier_hard=0.0636 · score_mae_expected=0.0970 · score_rps=0.0076 · choice_top1=0.9094 · choice_kl=0.0416`

excluding yuri_v1 placeholders (2920 rows): `n=11191 · kl=0.0214 · js=0.0057 · top1=0.9261 · ece=0.0016 · mce=0.0074 · noul_auroc=0.9962 · noul_brier_soft=0.0020 · noul_brier_hard=0.0636 · score_mae_expected=0.0970 · score_rps=0.0076 · choice_top1=0.9094 · choice_kl=0.0416`

throughput: 8853 tok/s · 68.7 rows/s

### validation by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3592 | 0.042 | 0.909 | 0.003 | — | — | — | 0.909 |
| noul | 7318 | 0.003 | 0.967 | 0.002 | 0.996 | 0.001 | — | — |
| score | 3201 | 0.021 | 0.888 | 0.002 | — | — | 0.097 | — |

### validation by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 463 | 0.151 | 0.886 | 0.028 | — | — | — | 0.886 |
| openjev_v2 | noul | 1167 | 0.009 | 0.995 | 0.003 | 1.000 | 0.003 | — | — |
| yuri_v1 | noul | 2920 | 0.000 | — | 0.003 | — | 0.000 | — | — |
| yuri_v3 | choice | 3129 | 0.026 | 0.913 | 0.004 | — | — | — | 0.913 |
| yuri_v3 | noul | 3231 | 0.004 | 0.957 | 0.001 | 0.994 | 0.002 | — | — |
| yuri_v3 | score | 3201 | 0.021 | 0.888 | 0.002 | — | — | 0.097 | — |

## Choice permutation consistency

`{"n_rows": 1000, "mean_max_abs_diff": 0.02205398865044117, "p90_max_abs_diff": 0.05050674080848694, "top1_flip_rate": 0.02925}`

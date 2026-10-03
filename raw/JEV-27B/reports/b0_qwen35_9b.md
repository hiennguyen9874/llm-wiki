# Evaluation — B0 /root/models/Qwen3.5-9B

base: `/root/models/Qwen3.5-9B` · temperature: no · max_seq_len 1024

## Acceptance (DESIGN §8.3, main = test_set_30k)

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.8236 | nan | ❌ |
| noul_brier_soft | <= 0.1 | 0.0960 | nan | ✅ |
| choice_top1 | >= 0.9 | 0.5323 | nan | ❌ |
| score_mae_expected | <= 0.35 | 1.1297 | nan | ❌ |
| kl | <= 0.15 | 0.5100 | nan | ❌ |
| ece | <= 0.03 | 0.0942 | nan | ❌ |
| ood KL ratio (ood/test_set_30k) | <= 2.0 | 1.680 | — | ✅ |

## test_set_30k

`n=29955 · kl=0.5100 · js=0.1313 · top1=0.4411 · ece=0.0942 · mce=0.2955 · noul_auroc=0.8236 · noul_brier_soft=0.0960 · noul_brier_hard=0.2258 · score_mae_expected=1.1297 · score_rps=0.5499 · choice_top1=0.5323 · choice_kl=0.5144`

throughput: 43510 tok/s · 408.0 rows/s

### test_set_30k by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 9199 | 0.514 | 0.532 | 0.014 | — | — | — | 0.532 |
| noul | 12229 | 0.247 | 0.605 | 0.136 | 0.824 | 0.096 | — | — |
| score | 8527 | 0.882 | 0.154 | 0.128 | — | — | 1.130 | — |

### test_set_30k by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 887 | 1.157 | 0.400 | 0.159 | — | — | — | 0.400 |
| openjev_v2 | noul | 1432 | 0.666 | 0.598 | 0.076 | 0.580 | 0.237 | — | — |
| yuri_v1 | noul | 2260 | 0.244 | — | 0.253 | — | 0.081 | — | — |
| yuri_v3 | choice | 8312 | 0.446 | 0.546 | 0.012 | — | — | — | 0.546 |
| yuri_v3 | noul | 8537 | 0.178 | 0.606 | 0.119 | 0.843 | 0.076 | — | — |
| yuri_v3 | score | 8527 | 0.882 | 0.154 | 0.128 | — | — | 1.130 | — |

### test_set_30k by family

| family | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| agent | 2583 | 0.517 | 0.384 | 0.119 | 0.791 | 0.103 | 1.203 | 0.481 |
| biology | 1654 | 0.488 | 0.453 | 0.073 | 0.936 | 0.066 | 0.973 | 0.478 |
| business | 2352 | 0.587 | 0.432 | 0.079 | 0.881 | 0.073 | 1.313 | 0.506 |
| chemistry | 1333 | 0.548 | 0.473 | 0.092 | 0.870 | 0.070 | 1.465 | 0.687 |
| genomics | 1914 | 0.446 | 0.449 | 0.089 | 0.867 | 0.073 | 0.954 | 0.609 |
| knowledge | 4807 | 0.339 | 0.446 | 0.158 | 0.801 | 0.080 | 0.862 | 0.509 |
| medical | 2120 | 0.537 | 0.471 | 0.062 | 0.862 | 0.062 | 1.394 | 0.543 |
| openjev | 2319 | 0.854 | 0.524 | 0.091 | 0.580 | 0.237 | — | 0.400 |
| physics | 1656 | 0.404 | 0.444 | 0.077 | 0.785 | 0.076 | 0.821 | 0.581 |
| science | 1667 | 0.461 | 0.427 | 0.084 | 0.816 | 0.085 | 0.814 | 0.564 |
| spatial | 1647 | 0.519 | 0.384 | 0.111 | 0.916 | 0.061 | 1.176 | 0.509 |
| structured | 1668 | 0.397 | 0.463 | 0.066 | 0.831 | 0.057 | 0.796 | 0.539 |
| technical | 2581 | 0.689 | 0.381 | 0.141 | 0.832 | 0.089 | 1.679 | 0.542 |
| theology | 1654 | 0.417 | 0.476 | 0.069 | 0.786 | 0.085 | 0.972 | 0.645 |

## test

`n=14261 · kl=0.4927 · js=0.1262 · top1=0.4496 · ece=0.1151 · mce=0.4147 · noul_auroc=0.8071 · noul_brier_soft=0.1046 · noul_brier_hard=0.2267 · score_mae_expected=1.1373 · score_rps=0.5592 · choice_top1=0.5210 · choice_kl=0.5354`

throughput: 37440 tok/s · 291.4 rows/s

### test by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3620 | 0.535 | 0.521 | 0.023 | — | — | — | 0.521 |
| noul | 7298 | 0.284 | 0.605 | 0.163 | 0.807 | 0.105 | — | — |
| score | 3343 | 0.902 | 0.172 | 0.125 | — | — | 1.137 | — |

### test by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 457 | 1.121 | 0.434 | 0.133 | — | — | — | 0.434 |
| openjev_v2 | noul | 1139 | 0.679 | 0.587 | 0.092 | 0.578 | 0.243 | — | — |
| yuri_v1 | noul | 2951 | 0.245 | — | 0.252 | — | 0.081 | — | — |
| yuri_v3 | choice | 3163 | 0.451 | 0.533 | 0.013 | — | — | — | 0.533 |
| yuri_v3 | noul | 3208 | 0.179 | 0.611 | 0.119 | 0.847 | 0.077 | — | — |
| yuri_v3 | score | 3343 | 0.902 | 0.172 | 0.125 | — | — | 1.137 | — |

## ood

`n=13058 · kl=0.8567 · js=0.2429 · top1=0.5180 · ece=0.0720 · mce=0.1899 · noul_auroc=0.6880 · noul_brier_soft=0.2479 · noul_brier_hard=0.2479 · score_mae_expected=0.9703 · score_rps=0.7063 · choice_top1=0.3641 · choice_kl=1.3434`

throughput: 39237 tok/s · 148.0 rows/s

### ood by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3219 | 1.343 | 0.364 | 0.117 | — | — | — | 0.364 |
| noul | 9767 | 0.690 | 0.570 | 0.070 | 0.688 | 0.248 | — | — |
| score | 72 | 1.651 | 0.278 | 0.145 | — | — | 0.970 | — |

### ood by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 3219 | 1.343 | 0.364 | 0.117 | — | — | — | 0.364 |
| openjev_v2 | noul | 9767 | 0.690 | 0.570 | 0.070 | 0.688 | 0.248 | — | — |
| openjev_v2 | score | 72 | 1.651 | 0.278 | 0.145 | — | — | 0.970 | — |

## validation

`n=14111 · kl=0.4854 · js=0.1246 · top1=0.4520 · ece=0.1126 · mce=0.3819 · noul_auroc=0.8143 · noul_brier_soft=0.1024 · noul_brier_hard=0.2240 · score_mae_expected=1.1391 · score_rps=0.5592 · choice_top1=0.5231 · choice_kl=0.5381`

throughput: 39954 tok/s · 310.2 rows/s

### validation by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3592 | 0.538 | 0.523 | 0.022 | — | — | — | 0.523 |
| noul | 7318 | 0.278 | 0.610 | 0.158 | 0.814 | 0.102 | — | — |
| score | 3201 | 0.902 | 0.157 | 0.131 | — | — | 1.139 | — |

### validation by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 463 | 1.080 | 0.426 | 0.129 | — | — | — | 0.426 |
| openjev_v2 | noul | 1167 | 0.657 | 0.606 | 0.084 | 0.621 | 0.234 | — | — |
| yuri_v1 | noul | 2920 | 0.240 | — | 0.250 | — | 0.080 | — | — |
| yuri_v3 | choice | 3129 | 0.458 | 0.537 | 0.014 | — | — | — | 0.537 |
| yuri_v3 | noul | 3231 | 0.174 | 0.612 | 0.113 | 0.860 | 0.075 | — | — |
| yuri_v3 | score | 3201 | 0.902 | 0.157 | 0.131 | — | — | 1.139 | — |

## Choice permutation consistency

`{"n_rows": 1000, "mean_max_abs_diff": 0.17348456382751465, "p90_max_abs_diff": 0.3202178478240967, "top1_flip_rate": 0.3815}`

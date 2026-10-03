# Evaluation — B0 /root/models/Qwen3.8-27B

base: `/root/models/Qwen3.8-27B` · temperature: no · max_seq_len 1024

## Acceptance (DESIGN §8.3, main = test_set_30k)

**all rows**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.8763 | nan | ❌ |
| noul_brier_soft | <= 0.1 | 0.0628 | nan | ✅ |
| choice_top1 | >= 0.9 | 0.5814 | nan | ❌ |
| score_mae_expected | <= 0.35 | 0.8420 | nan | ❌ |
| kl | <= 0.15 | 0.4296 | nan | ❌ |
| ece | <= 0.03 | 0.0501 | nan | ❌ |
| ood KL ratio (ood/test_set_30k) | <= 2.0 | 1.525 | — | ✅ |

**excluding yuri_v1 exact-uniform placeholders (D1)**

| metric | target | value | B0 | pass |
|---|---|---|---|---|
| noul_auroc | >= 0.95 | 0.8763 | nan | ❌ |
| noul_brier_soft | <= 0.1 | 0.0552 | nan | ✅ |
| choice_top1 | >= 0.9 | 0.5814 | nan | ❌ |
| score_mae_expected | <= 0.35 | 0.8420 | nan | ❌ |
| kl | <= 0.15 | 0.4411 | nan | ❌ |
| ece | <= 0.03 | 0.0307 | nan | ❌ |
| ood KL ratio (ood/test_set_30k) | <= 2.0 | 1.485 | — | ✅ |

## test_set_30k

all rows: `n=29955 · kl=0.4296 · js=0.1105 · top1=0.5597 · ece=0.0501 · mce=0.2047 · noul_auroc=0.8763 · noul_brier_soft=0.0628 · noul_brier_hard=0.1580 · score_mae_expected=0.8420 · score_rps=0.3772 · choice_top1=0.5814 · choice_kl=0.4314`

excluding yuri_v1 placeholders (2260 rows): `n=27695 · kl=0.4411 · js=0.1147 · top1=0.5597 · ece=0.0307 · mce=0.0532 · noul_auroc=0.8763 · noul_brier_soft=0.0552 · noul_brier_hard=0.1580 · score_mae_expected=0.8420 · score_rps=0.3772 · choice_top1=0.5814 · choice_kl=0.4314`

throughput: 13918 tok/s · 130.5 rows/s

### test_set_30k by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 9199 | 0.431 | 0.581 | 0.056 | — | — | — | 0.581 |
| noul | 12229 | 0.176 | 0.805 | 0.054 | 0.876 | 0.063 | — | — |
| score | 8527 | 0.791 | 0.253 | 0.051 | — | — | 0.842 | — |

### test_set_30k by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 887 | 0.836 | 0.551 | 0.121 | — | — | — | 0.551 |
| openjev_v2 | noul | 1432 | 0.659 | 0.680 | 0.096 | 0.619 | 0.226 | — | — |
| yuri_v1 | noul | 2260 | 0.288 | — | 0.288 | — | 0.096 | — | — |
| yuri_v3 | choice | 8312 | 0.388 | 0.584 | 0.054 | — | — | — | 0.584 |
| yuri_v3 | noul | 8537 | 0.066 | 0.826 | 0.020 | 0.923 | 0.027 | — | — |
| yuri_v3 | score | 8527 | 0.791 | 0.253 | 0.051 | — | — | 0.842 | — |

### test_set_30k by family

| family | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| agent | 2583 | 0.393 | 0.543 | 0.035 | 0.921 | 0.026 | 0.937 | 0.570 |
| biology | 1654 | 0.384 | 0.562 | 0.048 | 0.967 | 0.023 | 0.780 | 0.624 |
| business | 2352 | 0.496 | 0.536 | 0.033 | 0.932 | 0.024 | 1.012 | 0.478 |
| chemistry | 1333 | 0.429 | 0.563 | 0.075 | 0.912 | 0.035 | 1.127 | 0.788 |
| genomics | 1914 | 0.420 | 0.559 | 0.057 | 0.913 | 0.027 | 0.746 | 0.635 |
| knowledge | 4807 | 0.342 | 0.538 | 0.157 | 0.897 | 0.076 | 0.674 | 0.514 |
| medical | 2120 | 0.442 | 0.586 | 0.024 | 0.954 | 0.030 | 0.917 | 0.566 |
| openjev | 2319 | 0.727 | 0.632 | 0.063 | 0.619 | 0.226 | — | 0.551 |
| physics | 1656 | 0.421 | 0.521 | 0.052 | 0.882 | 0.026 | 0.707 | 0.561 |
| science | 1667 | 0.338 | 0.596 | 0.019 | 0.909 | 0.023 | 0.657 | 0.632 |
| spatial | 1647 | 0.397 | 0.597 | 0.045 | 0.948 | 0.023 | 0.791 | 0.605 |
| structured | 1668 | 0.320 | 0.565 | 0.036 | 0.878 | 0.032 | 0.607 | 0.600 |
| technical | 2581 | 0.535 | 0.501 | 0.059 | 0.947 | 0.025 | 1.070 | 0.548 |
| theology | 1654 | 0.350 | 0.566 | 0.042 | 0.913 | 0.030 | 0.807 | 0.632 |

## ood

all rows: `n=13058 · kl=0.6550 · js=0.1893 · top1=0.6902 · ece=0.0617 · mce=0.2023 · noul_auroc=0.6069 · noul_brier_soft=0.2071 · noul_brier_hard=0.2071 · score_mae_expected=0.6939 · score_rps=0.5406 · choice_top1=0.6356 · choice_kl=0.7858`

excluding yuri_v1 placeholders (0 rows): `n=13058 · kl=0.6550 · js=0.1893 · top1=0.6902 · ece=0.0617 · mce=0.2023 · noul_auroc=0.6069 · noul_brier_soft=0.2071 · noul_brier_hard=0.2071 · score_mae_expected=0.6939 · score_rps=0.5406 · choice_top1=0.6356 · choice_kl=0.7858`

throughput: 9876 tok/s · 37.3 rows/s

### ood by kind

| kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|
| choice | 3219 | 0.786 | 0.636 | 0.036 | — | — | — | 0.636 |
| noul | 9767 | 0.606 | 0.710 | 0.083 | 0.607 | 0.207 | — | — |
| score | 72 | 1.488 | 0.472 | 0.348 | — | — | 0.694 | — |

### ood by source × kind

| source | kind | n | kl | top1 | ece | noul_auroc | noul_brier_soft | score_mae_expected | choice_top1 |
|---|---|---|---|---|---|---|---|---|---|
| openjev_v2 | choice | 3219 | 0.786 | 0.636 | 0.036 | — | — | — | 0.636 |
| openjev_v2 | noul | 9767 | 0.606 | 0.710 | 0.083 | 0.607 | 0.207 | — | — |
| openjev_v2 | score | 72 | 1.488 | 0.472 | 0.348 | — | — | 0.694 | — |

## Choice permutation consistency

`{"n_rows": 500, "mean_max_abs_diff": 0.23575635254383087, "p90_max_abs_diff": 0.4639355540275574, "top1_flip_rate": 0.4095}`

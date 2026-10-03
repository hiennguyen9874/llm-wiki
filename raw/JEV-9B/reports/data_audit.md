# Data audit — `jev-distill-corpus-v3`

tokenizer: `/root/models/Qwen3.5-9B` · max_seq_len: 1024 · template: bare-v1 (whole-string tokenization)

## Splits

| split | rows | schema violations | mean tok | p50 | p95 | p99 | max | > max_seq_len | time |
|---|---|---|---|---|---|---|---|---|---|
| train | 655,806 | 0 | 129.0 | 87 | 351 | 531 | 856 | 0 | 83s |
| validation | 14,111 | 0 | 128.8 | 87 | 339 | 530 | 699 | 0 | 2s |
| calibration | 13,766 | 0 | 128.2 | 87 | 354 | 525 | 699 | 0 | 2s |
| test | 14,261 | 0 | 128.5 | 87 | 345 | 527 | 716 | 0 | 1s |
| test_set_30k | 29,955 | 0 | 106.6 | 85 | 214 | 509 | 702 | 0 | 3s |
| ood | 13,058 | 0 | 265.0 | 178 | 553 | 662 | 734 | 0 | 2s |

train tokens / epoch ≈ **84.6M**; 2 epochs ≈ **169M**

## D1 — exactly-uniform teacher labels by split × source × kind

| split | source | kind | rows | uniform | share |
|---|---|---|---|---|---|
| train | openjev_v2 | choice | 20,434 | 511 | 2.5% |
| train | openjev_v2 | noul | 54,192 | 0 | 0.0% |
| train | yuri_v1 | noul | 137,203 | 137,203 | 100.0% |
| train | yuri_v3 | choice | 143,223 | 0 | 0.0% |
| train | yuri_v3 | noul | 150,515 | 1,514 | 1.0% |
| train | yuri_v3 | score | 150,239 | 0 | 0.0% |
| validation | openjev_v2 | choice | 463 | 15 | 3.2% |
| validation | openjev_v2 | noul | 1,167 | 0 | 0.0% |
| validation | yuri_v1 | noul | 2,920 | 2,920 | 100.0% |
| validation | yuri_v3 | choice | 3,129 | 0 | 0.0% |
| validation | yuri_v3 | noul | 3,231 | 35 | 1.1% |
| validation | yuri_v3 | score | 3,201 | 0 | 0.0% |
| calibration | openjev_v2 | choice | 463 | 9 | 1.9% |
| calibration | openjev_v2 | noul | 1,109 | 0 | 0.0% |
| calibration | yuri_v1 | noul | 2,812 | 2,812 | 100.0% |
| calibration | yuri_v3 | choice | 2,955 | 0 | 0.0% |
| calibration | yuri_v3 | noul | 3,254 | 30 | 0.9% |
| calibration | yuri_v3 | score | 3,173 | 0 | 0.0% |
| test | openjev_v2 | choice | 457 | 8 | 1.8% |
| test | openjev_v2 | noul | 1,139 | 0 | 0.0% |
| test | yuri_v1 | noul | 2,951 | 2,951 | 100.0% |
| test | yuri_v3 | choice | 3,163 | 0 | 0.0% |
| test | yuri_v3 | noul | 3,208 | 37 | 1.2% |
| test | yuri_v3 | score | 3,343 | 0 | 0.0% |
| test_set_30k | openjev_v2 | choice | 887 | 29 | 3.3% |
| test_set_30k | openjev_v2 | noul | 1,432 | 0 | 0.0% |
| test_set_30k | yuri_v1 | noul | 2,260 | 2,260 | 100.0% |
| test_set_30k | yuri_v3 | choice | 8,312 | 0 | 0.0% |
| test_set_30k | yuri_v3 | noul | 8,537 | 91 | 1.1% |
| test_set_30k | yuri_v3 | score | 8,527 | 0 | 0.0% |
| ood | openjev_v2 | choice | 3,219 | 0 | 0.0% |
| ood | openjev_v2 | noul | 9,767 | 0 | 0.0% |
| ood | openjev_v2 | score | 72 | 0 | 0.0% |

## Train mix

| kind | rows | share |
|---|---|---|
| noul | 341,910 | 52.1% |
| choice | 163,657 | 25.0% |
| score | 150,239 | 22.9% |

| source | rows | share |
|---|---|---|
| yuri_v3 | 443,977 | 67.7% |
| yuri_v1 | 137,203 | 20.9% |
| openjev_v2 | 74,626 | 11.4% |

choice n_options histogram (train): 2:910, 3:8,826, 4:142,002, 5:3,586, 6:511, 7:1,593, 8:8, 9:3,121, 16:3,100

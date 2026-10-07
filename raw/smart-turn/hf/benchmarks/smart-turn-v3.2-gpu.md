# Endpointing Model Benchmark Report

**Model:** `/data/smart-turn-v3.2-gpu.onnx`

**Generated:** 2026-01-07 17:59:39 UTC

## Accuracy Results

**Total Samples:** 31,527

**Unique Languages:** 🇸🇦 Arabic, 🇧🇩 Bengali, 🇩🇰 Danish, 🇩🇪 German, 🇬🇧 🇺🇸 English, 🇫🇮 Finnish, 🇫🇷 French, 🇮🇳 Hindi, 🇮🇩 Indonesian, 🇮🇹 Italian, 🇯🇵 Japanese, 🇰🇷 Korean, 🇮🇳 Marathi, 🇳🇱 Dutch, 🇳🇴 Norwegian, 🇵🇱 Polish, 🇵🇹 Portuguese, 🇷🇺 Russian, 🇪🇸 Spanish, 🇹🇷 Turkish, 🇺🇦 Ukrainian, 🇻🇳 Vietnamese, 🇨🇳 Chinese

**Unique Datasets:** chirp3_1, chirp3_2, chirp3_3_short, human_5, human_convcollector_1, liva_1, midcentury_1, mundo_1, orpheus_endfiller_1, orpheus_grammar_1, orpheus_midfiller_1, rime_2

### Overall Performance

| Metric  | Sample Count | Accuracy (%) | Precision | Recall |    F1 | FPR (%) | FNR (%) |
| :------ | -----------: | -----------: | --------: | -----: | ----: | ------: | ------: |
| Overall |       31,527 |        93.71 |     0.931 |  0.944 | 0.937 |    3.51 |    2.78 |

### Performance by Language

| Language      | Sample Count | Accuracy (%) | Precision | Recall |    F1 | FPR (%) | FNR (%) |
| :------------ | -----------: | -----------: | --------: | -----: | ----: | ------: | ------: |
| 🇰🇷 Korean     |          889 |        97.64 |     0.977 |  0.975 | 0.976 |    1.12 |    1.24 |
| 🇯🇵 Japanese   |          834 |        97.12 |     0.974 |  0.969 | 0.971 |    1.32 |    1.56 |
| 🇹🇷 Turkish    |          966 |        97.00 |     0.967 |  0.973 | 0.970 |    1.66 |    1.35 |
| 🇳🇱 Dutch      |        1,398 |        96.92 |     0.966 |  0.975 | 0.970 |    1.79 |    1.29 |
| 🇩🇪 German     |        1,322 |        96.60 |     0.957 |  0.976 | 0.966 |    2.19 |    1.21 |
| 🇵🇹 Portuguese |        1,398 |        95.49 |     0.948 |  0.960 | 0.954 |    2.58 |    1.93 |
| 🇮🇩 Indonesian |          971 |        95.47 |     0.939 |  0.971 | 0.955 |    3.09 |    1.44 |
| 🇫🇮 Finnish    |        1,010 |        95.25 |     0.950 |  0.954 | 0.952 |    2.48 |    2.28 |
| 🇵🇱 Polish     |          974 |        95.17 |     0.946 |  0.952 | 0.949 |    2.57 |    2.26 |
| 🇺🇦 Ukrainian  |          929 |        95.05 |     0.943 |  0.952 | 0.947 |    2.69 |    2.26 |
| 🇮🇹 Italian    |          782 |        95.01 |     0.949 |  0.951 | 0.950 |    2.56 |    2.43 |
| 🇫🇷 French     |        1,252 |        94.73 |     0.941 |  0.956 | 0.949 |    3.04 |    2.24 |
| 🇬🇧 🇺🇸 English |        7,820 |        94.71 |     0.940 |  0.953 | 0.946 |    2.98 |    2.31 |
| 🇷🇺 Russian    |        1,468 |        94.41 |     0.937 |  0.958 | 0.947 |    3.41 |    2.18 |
| 🇩🇰 Danish     |          779 |        93.58 |     0.930 |  0.944 | 0.937 |    3.59 |    2.82 |
| 🇳🇴 Norwegian  |        1,014 |        93.00 |     0.929 |  0.934 | 0.932 |    3.65 |    3.35 |
| 🇮🇳 Hindi      |        1,284 |        92.76 |     0.930 |  0.931 | 0.931 |    3.66 |    3.58 |
| 🇪🇸 Spanish    |        1,783 |        91.53 |     0.908 |  0.920 | 0.914 |    4.54 |    3.93 |
| 🇨🇳 Chinese    |          929 |        90.53 |     0.899 |  0.918 | 0.908 |    5.27 |    4.20 |
| 🇸🇦 Arabic     |          947 |        89.12 |     0.869 |  0.925 | 0.896 |    7.07 |    3.80 |
| 🇮🇳 Marathi    |          774 |        88.11 |     0.870 |  0.901 | 0.885 |    6.85 |    5.04 |
| 🇧🇩 Bengali    |        1,000 |        85.10 |     0.847 |  0.849 | 0.848 |    7.50 |    7.40 |
| 🇻🇳 Vietnamese |        1,004 |        82.47 |     0.814 |  0.840 | 0.826 |    9.56 |    7.97 |

### Performance by Dataset

| Dataset               | Sample Count | Accuracy (%) | Precision | Recall |    F1 | FPR (%) | FNR (%) |
| :-------------------- | -----------: | -----------: | --------: | -----: | ----: | ------: | ------: |
| midcentury_1          |        1,044 |        98.85 |     0.992 |  0.984 | 0.988 |    0.38 |    0.77 |
| rime_2                |          394 |        98.22 |     0.982 |  0.976 | 0.979 |    0.76 |    1.02 |
| human_5               |          402 |        97.01 |     0.977 |  0.955 | 0.966 |    1.00 |    1.99 |
| orpheus_endfiller_1   |          181 |        95.58 |     0.988 |  0.924 | 0.955 |    0.55 |    3.87 |
| chirp3_1              |       16,254 |        94.80 |     0.943 |  0.954 | 0.948 |    2.89 |    2.31 |
| liva_1                |        3,831 |        94.49 |     0.934 |  0.958 | 0.946 |    3.39 |    2.11 |
| orpheus_grammar_1     |          163 |        92.02 |     0.919 |  0.929 | 0.924 |    4.29 |    3.68 |
| chirp3_3_short        |          104 |        91.35 |     0.933 |  0.875 | 0.903 |    2.88 |    5.77 |
| chirp3_2              |        8,428 |        90.76 |     0.898 |  0.918 | 0.908 |    5.17 |    4.07 |
| human_convcollector_1 |           90 |        90.00 |     0.837 |  0.947 | 0.889 |    7.78 |    2.22 |
| orpheus_midfiller_1   |          140 |        87.86 |     0.859 |  0.873 | 0.866 |    6.43 |    5.71 |
| mundo_1               |          496 |        87.70 |     0.871 |  0.882 | 0.877 |    6.45 |    5.85 |


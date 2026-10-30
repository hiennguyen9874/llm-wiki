# OCR benchmark evidence fetched on 2026-10-30

Task-scoped archive of public benchmark assets linked from the ten requested OCR model sources. These are external source artifacts, not new benchmark runs. Original URLs, fetch times and SHA256 values are in `manifest.json`, `manifest-retry.json`, `manifest-text.json` and `manifest-extra.json`.

## Coverage ledger

- Visually inspected all 11 downloaded benchmark images: MinerU leaderboard/end-to-end/text/formula/table (5), Infinity olmOCR/ParseBench (2), Chandra olmOCR/multilingual (2), Surya parameter-score chart (1), OvisOCR3 overview (1).
- The MinerU end-to-end, formula and table files are JPEG bytes with upstream `.png` names. Initial signature-only attempts failed; `manifest-retry.json` records successful downloads and actual format. Both attempt histories are retained.
- Inspected `omniparsebench-card.md`: Results, design, test-family counts and run caveats. Dataset pages, gold annotations, results parquet, adapters and linked SVG breakdowns were not downloaded or evaluated; no per-tag conclusions are drawn.
- Inspected `mdpbench-readme.md`: Main Results including digital/photo, language and private columns. Parsed the four target model rows using Python standard-library HTMLParser. Dataset and scoring implementation were not downloaded or executed.
- Inspected complete per-language tables in `chandra-full-benchmarks.md` and `surya-multilingual.md`. They are separate reported populations; no shared-population comparison was performed.
- Text-extracted `mineru-pro-report.pdf` (arXiv 2604.04771) into disposable `outputs/ocr-comparison-work/mineru-pro-report.txt`; inspected §§5–6, Tables 2–6 and relevant appendix tables. Its numerical image tables were also inspected directly in the downloaded MinerU images. This is focused benchmark coverage, not complete ingestion of the report's training pipeline, bibliography, supplements or qualitative figures.
- Manifests inspected for acquisition provenance. Public-download redirect URLs may be temporary; canonical fetch URLs and content hashes identify artifacts.
- Excluded decorative logos, unrelated model training examples and inference demonstrations. Existing MiniCPM and LightOn benchmark images are retained in their original raw packages, not copied here.
- No model inference, scorer, benchmark, remote repository code, or downloaded executable was run. Source reporting is not independently reproduced performance.

## Compiled result

See [ten-model dataset comparison](../../wiki/ocr-ten-model-benchmark-comparison.md). Missing entries mean no score retrieved for the exact requested checkpoint and protocol, never a score of zero.

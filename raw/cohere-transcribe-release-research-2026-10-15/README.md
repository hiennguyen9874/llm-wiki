# Cohere Transcribe release-blog and chart capture

## Source identity

- Canonical upstream: [Introducing Cohere-transcribe: state-of-the-art speech recognition](https://huggingface.co/blog/CohereLabs/cohere-transcribe-03-2026-release), Cohere Labs on Hugging Face; English, vendor-authored release documentation for the March 2026 checkpoint.
- Captured and archived 2026-10-15 UTC, without an immutable upstream revision. Blog Results dates its English leaderboard snapshot 03.26.2026; this is not a new October benchmark.
- This package archives the six artifacts downloaded/extracted in `outputs/cohere-benchmark-research/` during the preceding source-level query. Copies were checked byte-for-byte by SHA-256 at archiving. Original HTML is not retained; `release-blog.txt` contains extracted article body from the introduction through Conclusion, excluding references, navigation, scripts and comments. It is not an independent source.
- Model's Apache-2.0 claim does not establish a separate license for blog/figure redistribution; these are public-source research captures, not a new license grant. No private audio, credentials or model weights are included. Read statically; no remote code or model executed.

## Coverage ledger

All six material captured artifacts were inspected in full: article text statically, PNGs visually. Local figure numbering differs from blog numbering because its Figure 2 is an HTML table, already included in the text.

| Artifact | Blog locator / inspection | Upstream |
|---|---|---|
| `release-blog.txt` | Introduction, Architecture, Training data, Results (English table and figure captions), High-performance production inference with vLLM, Limitations & future work, Conclusion. All retained text inspected. | Canonical blog URL above |
| `figure-1.png` | Figure 1: English WER x-axis (lower better), throughput RTFx y-axis; model legend and numeric point labels inspected. Cohere 525, Qwen 148 RTFx. | https://cdn-uploads.huggingface.co/production/uploads/6867ac274d8d690302fd0378/VtvUqMr9ibvv47Wj3gvI3.png |
| `figure-2.png` | Figure 3: English Cohere-vs-model human preference, labels and 50% reference line inspected. | https://cdn-uploads.huggingface.co/production/uploads/6867ac274d8d690302fd0378/8afqt1I-fs5Sqvt8NFZj5.png |
| `figure-3.png` | Figure 4: 13-language grouped WER/CER chart; axes, model legend and bar ordering inspected. Vietnamese bar heights estimated visually at approximately Cohere 8.8%, Qwen 8.3%; no exact data labels. Caption averages FLEURS, Common Voice 17.0, MLS and Wenet where relevant. | https://cdn-uploads.huggingface.co/production/uploads/6867ac274d8d690302fd0378/JBpnQDhJmTsZChY0swntW.png |
| `figure-4.png` | Figure 5: Italian/French/German/Spanish/Portuguese/Japanese human preference; all three comparator series and numeric labels inspected. No Vietnamese panel. | https://cdn-uploads.huggingface.co/production/uploads/6867ac274d8d690302fd0378/rpJZNAkTKp8GS_60mT-2e.png |
| `figure-5.png` | Figure 6: vLLM serving schematic, audio input → variable-length encoder batching → packed sequences → FlashAttention decoder → transcripts; inspected visually, not implementation verification. | https://cdn-uploads.huggingface.co/production/uploads/6867ac274d8d690302fd0378/ifv5Wq0jdevjJiofwEqan.png |
| `checksums.json` | Generated SHA-256/byte-length identity record for text and PNGs; does not verify vendor benchmark claims. | Local |

## Exclusions and limits

- Original HTML shell, scripts, navigation, comments, author profiles, decorative avatars and social thumbnails excluded as irrelevant. The extraction does not preserve reference bodies or outbound link targets; paper references, PR/code, demo, models, datasets, API docs and Model Vault are not compiled from this package. Public links in the previously compiled model card remain separate evidence.
- No new model-card source identity: the existing `../cohere-transcribe-03-2026.md` remains canonical for that card; the blog and attachments here form a distinct source package. Earlier direct requests for the card's two relative asset URLs returned HTTP 401 according to the retained query notes; this does not identify why access failed. These PNGs were downloaded from the public blog CDN, not proven byte-identical to those model-card assets. No HTTP request rerun during archiving.
- Exact per-language data, language-specific dataset membership/weights, normalizers, benchmark hardware/batch/runtime parity, human-evaluation sample counts, tie handling, uncertainty and statistical significance are not established by the captured materials. Figure values are Reported results; reading labels is Observed, not independent verification. Vietnamese numeric estimates are explicitly approximate.
- Nemotron 3.5 is not in these figures; Parakeet TDT 0.6B v3 in Figure 4 is a different checkpoint. Offline throughput is not microphone/stable-text latency or sustainable streaming concurrency.
- No benchmark reproduction, model download, audio listening, package installation or inference. Coverage is complete for the captured article body and its five images, not for all linked research or implementations.

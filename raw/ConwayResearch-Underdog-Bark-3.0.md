---
license: cc-by-4.0
language:
- en
library_name: transformers
pipeline_tag: automatic-speech-recognition
base_model: nvidia/parakeet-tdt-0.6b-v3
base_model_relation: finetune
tags:
- underdog
- speech-to-text
- asr
- stt
- low-bit
- on-device
- mlx
- apple-silicon
- parakeet
metrics:
- wer
---

# Underdog Bark 3.0

Bark 3.0 is state-of-the-art speech recognition for its size: a 0.6B English model in a 163 MB download that averages 4.94 % word error across the Open ASR Leaderboard's seven English sets. No open model under 900 MB is more accurate except its larger sibling, Bark 3.0 Plus. It beats Phonon-2 at the same size, edges out NVIDIA's 2.5 GB Parakeet TDT 0.6B v3 (4.937 against 4.941 at three decimals), and beats Whisper large-v3, a download 57 times bigger.

It is at its best on the speech people actually record: 7.82 % on meetings (AMI) and 2.05 % on parliamentary speeches (VoxPopuli). On an Apple M2 laptop it transcribes a minute of audio in about 1.5 seconds (41x realtime) with stock mlx-audio.

![Accuracy vs download size](bark_frontier.png)

## In Underdog

[Underdog](https://underdog.ai) runs this file as it is, with no Python. A native Swift runtime reads `model.bark`, unpacks it in memory in about 2 seconds on Apple silicon, and runs the model on MLX. The unpacked weights are bit-identical to what `bark_loader.py` produces. Underdog downloads `model.bark` and `mlx/config.json` and checks each against a pinned size and SHA-256. Your audio never leaves the device. For dictation that leaves out the "um"s, Underdog uses [Underdog Bark 3.0 Clean](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Clean).

## Highlights

- State of the art for its size: the most accurate open speech recognition model at 163 MB.
- The Bark 3.0 family holds the accuracy frontier for open speech recognition at every size from 163 MB to 1.25 GB.
- Smaller and more accurate than Phonon-2: 163.4 MB and 4.94 %, against 163.5 MB and 5.21 %.
- More accurate than Whisper large-v3 (6.04 %, 9.3 GB) and Voxtral Small 24B (5.21 %, 97 GB), from a download 57 and about 600 times smaller.
- More accurate than Qwen3-ASR-0.6B (5.16 %), Canary 1B v2 (5.81 %) and Phi-4-multimodal (5.10 %).
- Edges out NVIDIA's Parakeet TDT 0.6B v3 (4.937 % against 4.941 % at three decimals) at a fifteenth of its size.


## Benchmarks

| Model | Download | LS clean | LS other | AMI | Earnings-22 | GigaSpeech | SPGISpeech | VoxPopuli | Average |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Bark 3.0 Pro | 1,254 MB | 1.38 | 3.11 | 7.16 | **5.65** | 7.46 | 3.54 | **1.70** | **4.29** |
| Bark 3.0 Plus | 180 MB | 1.71 | 3.82 | 7.76 | 6.70 | 7.77 | 3.64 | 1.92 | 4.76 |
| **Bark 3.0** | **163 MB** | 1.89 | 4.08 | 7.82 | 7.05 | 7.95 | 3.72 | 2.05 | 4.94 |
| Phonon-2† | 164 MB | 1.73 | 3.92 | 9.32 | 6.96 | 8.35 | 3.70 | 2.46 | 5.21 |
| Hojo-ASR-V1† | 11,957 MB | 1.30 | 3.24 | 7.54 | 6.97 | **6.14** | 1.74 | 3.11 | 4.29 |
| Qwen3-ASR-1.7B† | 4,699 MB | 1.26 | 2.94 | 8.31 | 5.84 | 7.22 | 2.57 | 2.85 | 4.43 |
| higgs-audio-v3-stt† | 5,351 MB | 1.08 | 2.61 | 7.19 | 7.04 | 7.45 | 2.07 | 3.73 | 4.45 |
| Canary-Qwen 2.5B† | 5,119 MB | 1.23 | 2.63 | 7.91 | 6.41 | 7.80 | **1.70** | 4.14 | 4.55 |
| Granite Speech 4.1 2B† | 4,832 MB | 1.03 | 2.19 | 7.06 | 6.69 | 8.18 | 3.47 | 4.18 | 4.69 |
| Cohere Transcribe† | 4,132 MB | **0.97** | **2.05** | **7.02** | 7.88 | 7.88 | 2.74 | 5.38 | 4.85 |
| Granite Speech 5.0 470M (NC)† | 946 MB | 1.45 | 2.67 | 7.31 | 8.23 | 8.37 | 1.75 | 4.67 | 4.92 |
| Parakeet TDT 0.6B v3† | 2,508 MB | 1.52 | 3.13 | 9.42 | 5.85 | 7.99 | 3.63 | 3.05 | 4.94 |
| Granite Speech 5.0 470M† | 946 MB | 1.48 | 2.71 | 7.71 | 6.75 | 8.74 | 3.22 | 4.90 | 5.07 |
| Qwen3-ASR-0.6B† | 1,876 MB | 1.70 | 4.01 | 9.33 | 7.83 | 7.62 | 2.74 | 2.90 | 5.16 |
| Whisper large-v3† | 9,261 MB | 1.56 | 3.52 | 13.63 | 7.99 | 8.35 | 2.71 | 4.53 | 6.04 |
| Whisper large-v3-turbo† | 1,618 MB | 2.13 | 3.71 | 13.88 | 8.09 | 8.47 | 2.79 | 7.02 | 6.58 |

Word error rate (%), lower is better, on the full test sets of the Open ASR Leaderboard's seven English sets (cleaned versions of AMI, Earnings-22, GigaSpeech and VoxPopuli). † The leaderboard's published row, as of 9 October 2026; the Bark rows use its scoring code and are not on the leaderboard yet. Bold marks the best value in each column. At three decimals, by the leaderboard's own averaging, Bark 3.0 Pro averages 4.286 and Hojo-ASR-V1 4.291. NC: non-commercial licence. Download is the size of the weight files on Hugging Face.


### Disfluent speech

On the DisfluencySpeech test set (250 clips of unscripted conversation full of "um", "uh", restarts and repeats), scored against its verbatim transcripts with fillers counted:

| Model | Word error rate (%) |
|---|--:|
| Bark 3.0 Pro | **2.95** |
| Bark 3.0 | 3.15 |
| Bark 3.0 Plus | 3.21 |
| Phonon-2 | 3.39 |

Bark 3.0 writes what was said, fillers included. It does not clean speech up.

## Run it

```bash
pip install huggingface_hub==2.2.0
hf download ConwayResearch/Underdog-Bark-3.0 --local-dir bark-3.0 \
  --include "model.bark" --include "bark_loader.py" --include "bark_mlx.py" --include "mlx/*" --include "NOTICE"
cd bark-3.0
pip install transformers==5.19.0 torch==2.8.0 constriction==0.5.0 numpy==2.4.6 soundfile==0.14.0 soxr==1.1.0 librosa==0.11.0
python bark_loader.py model.bark recording.wav
```

```python
from bark_loader import load_model, transcribe
import soundfile as sf

model = load_model("model.bark", device="cuda")          # or "cpu", "mps"
wave, sr = sf.read("recording.wav", dtype="float32", always_2d=True)
print(transcribe(model, wave.mean(1), sr))
```

On Apple silicon with MLX:

```bash
pip install mlx==0.32.2 mlx-audio==0.5.3 constriction==0.5.0 numpy==2.4.6 soundfile==0.14.0 soxr==1.1.0
python bark_mlx.py recording.wav
```

The first run unpacks the weights into an MLX folder and caches it. Unpacking is exact: the weights you load are the weights that were measured. `transcribe` adds 0.25 s of silence before the audio, the setting the numbers above use. Stock mlx-audio transcribes a file in one pass, so memory grows with its length: on a 16 GB M2, a 10-minute file peaked at about 15 GB. Split long recordings into pieces of a few minutes on an 8 or 16 GB Mac.

## Notes

Based on parakeet-tdt-0.6b-v3 by NVIDIA, through moondream/parakeet-ultra; the tokenizer and output conventions (punctuation, casing, numerals) are the original's. Licence CC-BY-4.0, same as the original; `NOTICE` lists the attribution. English only. Bark 3.0 Plus (180 MB) and Bark 3.0 Pro (full precision) are the larger members of the family.


## Additional platform runtimes

The original interfaces above remain available. Choose one runtime below and download only its files.

### Mac: Core ML GPU or ANE

Requires Apple Silicon, macOS 15 or later and Python 3.11. The GPU route runs supported encoder operations on the Apple GPU; the ANE route uses the Apple Neural Engine. Both use the CPU for audio preprocessing and greedy text decoding. Core ML controls operation placement, so neither option means every operation runs on that accelerator.

Both packages retain the source quantized weight values, with FP16 encoder arithmetic and FP32 preprocessing/decoding. The GPU package uses a fixed 15-second encoder. The ANE package shares weights between 8-second and 15-second encoder functions and automatically selects the smallest suitable window. Download only the selected package; these are alternative execution packages for the same model.

```bash
python3.11 -m venv .venv-bark-coreml
source .venv-bark-coreml/bin/activate
python -m pip install --upgrade pip huggingface_hub==2.2.0
# Choose gpu or ane:
BARK_BACKEND=ane
hf download ConwayResearch/Underdog-Bark-3.0 --local-dir bark-model \
  --include "coreml/$BARK_BACKEND/*" --include 'coreml/LICENSE' --include 'coreml/NOTICE' --include 'runtime/requirements-coreml.txt'
python -m pip install -r bark-model/runtime/requirements-coreml.txt
python "bark-model/coreml/$BARK_BACKEND/bark_coreml.py" recording.wav --units "$BARK_BACKEND"
```

The program downmixes/resamples the audio and prints the transcript. Use short recordings for the validated path; long-recording segmentation has not been qualified. Model loading and first-use Core ML compilation can take several minutes. For repeated requests, keep a `Transcriber` instance alive to avoid reloading. See [license](coreml/LICENSE) and [attribution](coreml/NOTICE). If repository access requires authentication, run `hf auth login` before downloading.

### iPhone and iPad (iOS)

Requires iOS 18 or later (the encoder is a Core ML multifunction model: `w8` and `w15` in the ANE package, `w15` in the GPU package). The model files are the same as on the Mac; nothing is converted for iOS. **Not yet tested on an iPhone or iPad.**

What an app needs:

- From one package, `coreml/ane/` (Neural Engine, 8-second and 15-second windows) or `coreml/gpu/` (GPU, 15-second window): `BarkEncoder.mlpackage` (about 185 MB), `decoder.npz` (11 MB) and `vocab.json`. Add the `.mlpackage` to the Xcode target, which compiles it to `.mlmodelc` at build time, or download it and compile it once on the device with `MLModel.compileModel(at:)`, then keep the compiled copy.
- Load the encoder with `MLModelConfiguration.computeUnits` set to `.cpuAndNeuralEngine` (ANE) or `.cpuAndGPU` (GPU) and `functionName` set to `w8` or `w15`. Inputs: `features`, FP16 `[1, T, 128]` with `T = window_seconds * 100 + 1`, and `mask`, Int32 `[1, T]`; output: `encoded`, `[1, T', 640]`.
- Swift code for the two CPU stages that `bark_coreml.py` runs in NumPy, since iOS has no Python: the audio frontend (`Frontend`: pre-emphasis, centred STFT, mel filters from `mel_filters` in `decoder.npz`, log, per-utterance normalization) and greedy TDT decoding (`Decoder`: a 2-layer LSTM and the joint head; int8 weights `*.q` times per-row FP16 scales `*.s`). `bark_coreml.py` is the reference implementation; port it line by line and compare transcripts with it on the Mac. `decoder.npz` is a zip of `.npy` arrays; read it in Swift or convert it once to raw arrays.
- The same input handling as `bark_coreml.py`: mono 16 kHz float audio, 0.25 seconds of leading silence, the smallest window that holds the clip, and longer audio cut at pauses into pieces of at most 15 seconds.

For an iOS app that should not port the decoder, Bark 3.0 Pro ships its whole pipeline (frontend, encoder, decoder and joint) as Core ML models, runs it through the FluidAudio Swift package, and has iOS instructions; its download is 1.23 GB instead of about 200 MB.

### Windows: NVIDIA CUDA or CPU

Requires 64-bit Python 3.11. Windows uses the existing `model.bark` and its original `bark_loader.py`, not the Core ML packages. The loader expands the packed weights to FP32 in memory; the download size is not the RAM/VRAM requirement. This is a PyTorch runtime, not an ONNX/DirectML or native low-bit CUDA export. The CUDA path has been tested on Windows with an NVIDIA GPU.

For NVIDIA GPUs with a driver compatible with the CUDA 12.8 PyTorch wheel, run in PowerShell:

```powershell
py -3.11 -m venv .venv-bark
.\.venv-bark\Scripts\python.exe -m pip install --upgrade pip huggingface_hub==2.2.0
.\.venv-bark\Scripts\hf.exe download ConwayResearch/Underdog-Bark-3.0 --local-dir bark-model --include "model.bark" --include "bark_loader.py" --include "NOTICE" --include "runtime/transcribe_bark.py" --include "runtime/requirements-windows.txt"
.\.venv-bark\Scripts\python.exe -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128
.\.venv-bark\Scripts\python.exe -m pip install -r bark-model/runtime/requirements-windows.txt
.\.venv-bark\Scripts\python.exe -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')"
.\.venv-bark\Scripts\python.exe bark-model/runtime/transcribe_bark.py --model bark-model --audio recording.wav --device cuda
```

For CPU execution, use a fresh environment and replace the CUDA wheel installation with:

```powershell
.\.venv-bark\Scripts\python.exe -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
```

Install the same requirements, then run:

```powershell
.\.venv-bark\Scripts\python.exe bark-model/runtime/transcribe_bark.py --model bark-model --audio recording.wav --device cpu
```

CUDA requires NVIDIA hardware; use the CPU path for other GPUs with this runtime. The entry point fails explicitly if the requested accelerator is unavailable. It downmixes/resamples input and preserves the original loader's per-model padding. First use needs internet access to fetch the NVIDIA processor and generation configuration, not NVIDIA model weights. If authentication is required, run `.\.venv-bark\Scripts\hf.exe auth login` before downloading.

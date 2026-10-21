---
license: apache-2.0
language: vi
base_model: rhasspy/piper-voices
base_model_relation: finetune
datasets: rhasspy/piper-checkpoints
pipeline_tag: text-to-speech
repo: https://github.com/nghimestudio/nghitts
---

# unofficial mirror of NGHI-TTS models

official announcement: https://www.facebook.com/groups/binhdanhocai/permalink/921555793666509/

official repo: https://github.com/nghimestudio/nghitts

official download: https://drive.google.com/drive/folders/1f_pCpvgqfvO4fdNKM7WS4zTuXC0HBskL

this repo contains only Vietnamese voices:
- Ban Mai
- Chiếu Thành
- Duy Oryx (giọng nam siêu trầm)
- Lạc Phi
- Mai Phương
- Mạnh Dũng
- Minh Khang (Kiến Giải Mã)
- Minh Quang
- Minh Thu
- Mỹ Tâm - 2 phiên bản
- Ngọc Huyền (review phim) - 2 phiên bản
- Ngọc Ngạn
- Phương Trang
- Tài An (CD Media) - 2 phiên bản
- Thanh Phương Viettel
- Thiện Tâm
- Trấn Thành
- Việt Thảo

folder structure:
- original onnx files are in [`piper-tts/`](piper-tts) folder can be used directly with Piper TTS
- also including converted onnx files in [`sherpa-onnx/`](sherpa-onnx) folder compatible with Sherpa ONNX
  - convert following https://k2-fsa.github.io/sherpa/onnx/tts/piper.html
    - also including generated `tokens.txt` file

**example usage in python:**

## 0. PiperTTS as OpenAI-compatible endpoint

see: https://gist.github.com/phineas-pta/7d08a3ac21d64e67ed5fa6b47e93c097

## 1. with Piper TTS

to run on cpu:
```bash
pip install piper-tts
```

to run on nvidia gpu:
```bash
pip install piper-tts
pip uninstall -y onnxruntime
pip install onnxruntime-gpu # cuda 13
# pip install onnxruntime-gpu --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/
```

download the desired onnx file and `config.json` file

save audio as wav file:
```python
import wave
from piper import PiperVoice, SynthesisConfig

TTS = PiperVoice.load("piper-tts/ngocngan3701.onnx", config_path="piper-tts/config.json") # use_cuda=True
CONF = SynthesisConfig(noise_scale=1., noise_w_scale=1.) # add more variation

text = "Mẹ tôi đang ngồi bên hiên nhà, vừa đan chiếc áo len màu xanh, vừa lắng nghe tiếng mưa rơi tí tách trên mái tôn."
with wave.open("output.wav", mode="wb") as wav_file:
	TTS.synthesize_wav(text, wav_file, syn_config=CONF)
```

streaming audio:
```python
import sounddevice as sd
from piper.voice import PiperVoice, SynthesisConfig

TTS = PiperVoice.load("piper-tts/ngocngan3701.onnx", config_path="piper-tts/config.json") # use_cuda=True

# set up audio stream configuration
dummy_chunk = next(TTS.synthesize("Xin chào"))
stream = sd.OutputStream(
	samplerate=dummy_chunk.sample_rate,
	channels=dummy_chunk.sample_channels,
	dtype=dummy_chunk.audio_float_array.dtype
)
stream.start()

text = "Mẹ tôi đang ngồi bên hiên nhà, vừa đan chiếc áo len màu xanh, vừa lắng nghe tiếng mưa rơi tí tách trên mái tôn."
for chunk in TTS.synthesize(text):
	stream.write(chunk.audio_float_array)

stream.stop()
stream.close()
```

reference: https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md

### 1.1. Intel CPU

if u have Intel CPU but no discrete GPU, u may want to use OpenVINO to be a bit faster

**installation**

at the time of writing `onnxruntime-openvino` depends on python up to v3.13 and openvino up to v2025.4.1
```bash
pip install piper-tts
pip uninstall -y onnxruntime
pip install openvino==2025.4.1 onnxruntime-openvino
```

**usage**

on windows specically, must add those 2 lines
```python
import onnxruntime.tools.add_openvino_win_libs as utils
utils.add_openvino_libs_to_path()
```
(source: https://github.com/intel/onnxruntime/releases)

```python
import json
import wave
import onnxruntime as ort
from piper import PiperVoice, PiperConfig, SynthesisConfig

_ONNX_FILE = "piper-tts/ngocngan3701.onnx"

with open(_ONNX_FILE + ".json", mode="r", encoding="utf-8") as config_file:
	_PIPER_CONFIG = PiperConfig.from_dict(json.load(config_file))

_SESSION = ort.InferenceSession(
	_ONNX_FILE,
	providers=["OpenVINOExecutionProvider"],
	provider_options=[{"device_type": "HETERO:GPU,CPU"}]
) # for more options see https://onnxruntime.ai/docs/execution-providers/OpenVINO-ExecutionProvider.html

PIPER = PiperVoice(config=_PIPER_CONFIG, session=_SESSION)
CONF = SynthesisConfig(noise_scale=1., noise_w_scale=1.)

text = "Mẹ tôi đang ngồi bên hiên nhà, vừa đan chiếc áo len màu xanh, vừa lắng nghe tiếng mưa rơi tí tách trên mái tôn."
with wave.open("output.wav", mode="wb") as wav_file:
	PIPER.synthesize_wav(text, wav_file, syn_config=CONF)
```

## 2. with Sherpa ONNX

to run on cpu:
```bash
pip install sherpa-onnx onnxruntime
```

to run on nvidia gpu (only for cuda 12 at the time of writing):
```bash
pip install sherpa-onnx --find-link https://k2-fsa.github.io/sherpa/onnx/cuda.html
pip install onnxruntime-gpu --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/
```

download the desired onnx file and `tokens.txt` file, also download and untar https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/espeak-ng-data.tar.bz2

save audio as wav file:
```python
import sherpa_onnx as so
import soundfile as sf

TTS = so.OfflineTts(config=so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(
	vits=so.OfflineTtsVitsModelConfig(
		model="sherpa-onnx/ngocngan3701.onnx",
		tokens="sherpa-onnx/tokens.txt",
		data_dir="espeak-ng-data"
	),
	# provider="cuda"
)))

audio = TTS.generate("Mẹ tôi đang ngồi bên hiên nhà, vừa đan chiếc áo len màu xanh, vừa lắng nghe tiếng mưa rơi tí tách trên mái tôn.")
sf.write("output.wav", audio.samples, samplerate=audio.sample_rate, subtype="PCM_16")
```

reference: https://github.com/k2-fsa/sherpa-onnx/blob/master/python-api-examples/offline-tts.py

i failed to use OpenVINO in Python because the source code is written in C

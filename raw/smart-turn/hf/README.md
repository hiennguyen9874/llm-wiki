---
pipeline_tag: voice-activity-detection
license: bsd-2-clause
tags:
  - speech-processing
  - semantic-vad
  - multilingual
datasets:
  - pipecat-ai/smart-turn-data-v3.1-train
  - pipecat-ai/smart-turn-data-v3.1-test
---

# Smart Turn v3.x

**Smart Turn** is an open‑source semantic Voice Activity Detection (VAD) model that tells you whether a speaker has finished their turn by analysing the raw waveform, not the transcript.

## Links

* [Blog post: Smart Turn v3](https://www.daily.co/blog/announcing-smart-turn-v3-with-cpu-inference-in-just-12ms/)
* [GitHub repo](https://github.com/pipecat-ai/smart-turn) with training and inference code, and more information
* [Datasets](https://huggingface.co/pipecat-ai/datasets)


## Model architecture

* Backbone: Whisper Tiny encoder
* Head: shallow linear classifier
* Params: 8M
* Checkpoint: 8 MB ONNX (int8 quantized), 32MB ONNX (unquantized)


## How to use

Please see the blog post and GitHub repo for more information on using the model, either standalone or with Pipecat.


## Thanks

Thank you to the following organisations for contributing audio datasets:

- [Liva AI](https://www.theliva.ai/)
- [Midcentury](https://www.midcentury.xyz/)
- [MundoAI](https://mundoai.world/)


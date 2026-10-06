---
license: openmdw-1.1
language:
- en
base_model:
- nvidia/NVIDIA-Nemotron-Nano-9B-v2
---
# NVIDIA NemotronLabs VoiceChat 11B

▶ **Hear it first.** Natural turn-taking, barge-in and live tool calling.

| Sample | What to listen for | Player |
|---|---|---|
| Natural turn-taking | Smooth back-and-forth, ~450 ms response | <audio controls src="https://huggingface.co/nvidia/NVIDIA-NemotronLabs-VoiceChat-11B/resolve/main/turn_taking.wav"></audio> |
| Barge-in / interruption | User cuts in; model yields instantly | <audio controls src="https://huggingface.co/nvidia/NVIDIA-NemotronLabs-VoiceChat-11B/resolve/main/interruptions.wav"></audio> |
| Tool calling live | Tools are called when needed | <audio controls src="https://huggingface.co/nvidia/NVIDIA-NemotronLabs-VoiceChat-11B/resolve/main/tool_call.wav"></audio> |

▶ **Code:** On [Github](https://github.com/NVIDIA-NeMo/Speech/tree/nemotron-labs-voicechat)

# Model Overview

## Description:
NVIDIA NemotronLabs VoiceChat is a **11B end-to-end, real-time speech full duplex (FD)** model for conversational AI that jointly performs streaming speech understanding and speech generation [1, 2, 3]. Unlike traditional cascaded stacks (ASR → LLM → TTS), this model achieves full duplex, real-time, seamless voice interaction in one unified architecture, eliminating the need for multiple models or API handoffs, thus reducing end-to-end latency. 
It sets new benchmarks by bringing open, robust, and highly natural conversation capabilities. Moreover, NVIDIA NemotronLabs VoiceChat is **the first open full-duplex model to support tool calling** while maintaining a natural conversation flow during tool execution. For each tool, a specific “on-hold” message can be defined that will be spoken by the agent as soon as the LLM generates the text that will trigger the tool call and response. 

The model operates on audio signals, which are encoded using a fast conformer module. The resulting audio tokens are inputted into a Nemotron Nano V2 9B LLM backbone to predict text tokens, which are fed to a TTS decoder to predict audio codes for generating the agent's speech. A separate output channel is used to predict tool calling scripts. 
NemotronLabs VoiceChat offers an unprecedented trade-off between intelligence and latency in the space of open-source voice agents, as highlighted by our benchmarking results [below](#testingevaluation-dataset).


### Highlights

| Parameters | Turn-taking latency | VoiceBench (open FD) | Tool calling | Architecture |
|---|---|---|---|---|
| 11B | ~450 ms | #2 | 1st open FD | 1 unified model |

### License/Terms of Use
GOVERNING TERMS:  The use of this model is governed by the [OpenMDW License Agreement, version 1.1](https://github.com/OpenMDW/OpenMDW/blob/main/1.1/LICENSE.OpenMDW-1.1).

### Use Case: <br>
NemotronLabs VoiceChat is targeted for researchers, developers, and professionals in the field of natural language processing (NLP) and speech technology for purposes such as automatic speech recognition (ASR), text-to-speech synthesis (TTS), and voice assistant development.

### Deployment Geography
Global

### Release Date:  <br>
August 3, 2026.


## Model Architecture
**Architecture Type:** Hybrid Mamba/Transformer &nbsp;·&nbsp; **Parameters:** 11B

**Network Architecture:** <br>

NemotronLabs VoiceChat uses:
* Fast Conformer Speech Encoder from [Nemotron-Speech-Streaming-En-0.6b](https://huggingface.co/nvidia/nemotron-speech-streaming-en-0.6b)
* [NVIDIA Nemotron Nano v2 LLM backbone](https://huggingface.co/nvidia/NVIDIA-Nemotron-Nano-9B-v2)
* NVIDIA TTS decoder and codec
* Separate output channel for tool-calling scripts

![NemotronLabs VoiceChat Architecture](./VoiceChat-v1-TC%20voicechatv1.png)

### Input

| Property | Value |
|---|---|
| Input Type(s) | Text (prompt), Audio (user speech) |
| Input Format | String, WAV/WebAudio |
| Sample rate | 16 kHz |

### Output

| Property | Value |
|---|---|
| Output Type(s) | Text (agent), Audio (agent speech), Text (user transcription) |
| Output Format | String, WAV/WebAudio |
| Sample rate | 22.05 kHz |


## Software Integration

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA’s hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions. <br> 

**Runtime Engine:** vLLM <br>

**Supported Hardware Microarchitecture Compatibility:** <br>

* NVIDIA A100
* NVIDIA H100
* NVIDIA H200
* NVIDIA B100
* NVIDIA B200
* NVIDIA RTX-6000

**Preferred/Supported Operating System(s):**
* Linux

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment. <br>

## Model Version(s)
* v1.0


## Quickstart

To try inference with the model, check the instructions below:

* **Offline inference** — load this Hugging Face checkpoint for non-interactive batch speech-to-speech testing ([Offline inference](#offline-inference)).
* **Interactive streaming** — deploy the optimized NVIDIA inference container for real-time WebSocket conversations ([Interactive streaming deployment](#interactive-streaming-deployment)).

Full setup details are also availabel in the [Github repo](https://github.com/NVIDIA-NeMo/Speech/tree/nemotron-labs-voicechat).


## Training, Testing, and Evaluation Datasets:

### Training Dataset:

**Data Modality:** Audio (speech) and Text <br>
**Audio Training Data Size:**  ~550k hours <br>

VoiceChat has been trained on a blend of different datasets comprising both real audio datasets and synthetic speech datasets generated using various TTS systems on text training corpora, including:

- Nemotron 5.5 pre-training and SFT text data
- Brainy-mantis text data
- Greteal AI v1 and v2 text data
- [Ultrachat text data](https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k)
- Blackwell studio recordings real speech data
- [Fisher real speech data](https://catalog.ldc.upenn.edu/LDC2004S13)
- [LibriVox](https://librivox.org/)
- [LibriTTS](https://www.openslr.org/60/)
- [HiFi-TTS](https://www.openslr.org/109/)
- Riva Speakers: Internal Dataset
- Publicly available internet scale data
- [PromptTTS](https://speechresearch.github.io/prompttts/)
- [VCTK](https://datashare.ed.ac.uk/handle/10283/3443)
- [Voxmovies](https://mmai.io/datasets/voxmovies/)
- [JL-Corpus](https://huggingface.co/datasets/CLAPv2/JL-Corpus)
- Nemotron Nano v3 function calling data
- Persona Plex training datasets

**Data Collection Method by dataset:** Hybrid: Human, Synthetic, Automated. <br>
**Labeling Method by dataset:** Automated. <br>

### Testing/Evaluation Dataset:

#### VoiceBench
VoiceBench is a benchmark dataset developed to evaluate large language model (LLM)-based voice assistants, focusing on real-world spoken interactions rather than just text or clean speech recognition. It combines audio and text data. The dataset includes multiple subsets covering tasks like open-ended questions, multiple-choice QA, instruction following, and adversarial cases — sourced from both real human speech and synthetic text-to-speech examples.

**Link:** [VoiceBench](https://github.com/MatthewCYM/VoiceBench) <br>
**Data Collection Method by dataset:** Hybrid: Human, Synthetic, Automated. <br>
**Labeling Method by dataset:** Automated. <br>
**Properties:**  VoiceChat is #2 amongst all open full-duplex models on [VoiceBench](https://arxiv.org/abs/2410.17196). <br>


#### Full-Duplex-Bench 1.0
Full-Duplex-Bench 1.0 is a benchmark designed to evaluate the interactive capabilities of full-duplex spoken dialogue models like VoiceChat. It focuses on measuring natural, human-like conversational behaviors such as pause handling, backchanneling, smooth turn-taking, and user interruption management, using automatic metrics to provide consistent, reproducible assessments of model performance.


**Link:** [Full-Duplex-Bench 1.0](https://arxiv.org/abs/2503.04721) <br>
**Data Collection Method by dataset:** Hybrid: Human, Synthetic, Automated. <br>
**Labeling Method by dataset:** Automated. <br>
**Properties:** NemotronLabs VoiceChat is #2 amongst all open models on [FullDuplexBench 1.0](https://arxiv.org/abs/2503.04721). <br>


**Benchmark Scores:**

| Metric                                   | Value |
|------------------------------------------|-------|
| Pause Handling(Synthetic): TOR↓          | 0.153 |
| Pause Handling(Candor): TOR↓             | 0.255 |
| Smooth Turn Taking: TOR↑                 | 0.82 |
| Smooth Turn Taking: Latency↓             | 448 ms |
| User Interruption: TOR↑                  | 1    |
| User Interruption:  Latency↓             | 480 ms |
| User Interruption: GPT-4o↑               | 4.33 |


#### AU Harness BFCL-v3 (tool calling)
This is the subset of the [AU Harness benchmark](https://github.com/ServiceNow/AU-Harness) focused on the evaluation of tool calling within audio conversation. It was created by systematically converting the original [BFCL-v3](https://openreview.net/pdf?id=2GmDdhBdDk) textual instructions into spoken counterparts. 


**Link:** [AU Harness](https://github.com/ServiceNow/AU-Harness) <br>
**Data Collection Method by dataset:** Hybrid: Human, Synthetic, Automated. <br>
**Properties:** NemotronLabs VoiceChat is the first open full-duplex model to support tool calling while maintaining a natural conversation flow during tool execution.<br>


**Benchmark Scores:** 

| Metric             | Value |
|--------------------|-------|
| Simple             | 58.5% |
| Multiple           | 62.5% |
| Parallel           | 42.5% |
| Parallel Multiple  | 27.5% |
| Irrelevance        | 89.6% |
| Average            | 56.1% |


#### Full-Duplex-Bench v3 (tool calling)
[Full-Duplex-Bench-v3 (FDB-v3)](https://arxiv.org/abs/2604.04847) is a benchmark for evaluating spoken language models under naturalistic speech conditions and multi-step tool use. 

**Link:** [Full-Duplex-Bench v3](https://daniellin94144.github.io/FDB-v3-demo/) <br>
**Data Collection Method by dataset:** Human. <br>
**Properties:** NemotronLabs VoiceChat is competitive with frontier models in terms of tool selection accuracy on this benchmark. <br>


**Benchmark Scores:** 

| Metric             | Value |
|--------------------|-------|
| Tool Selection     | 82.5% |
| Argument accuracy  | 42.2% |
| Pass@1             | 33%   |


# Inference:
**Acceleration Engine:** vLLM <br>
**Test Hardware:** NVIDIA H100 <br>

This section explains how to test NVIDIA Nemotron Labs VoiceChat using either of the following approaches:

- **Offline inference** — quick, non-interactive speech-to-speech checks from a conda environment ([Offline inference](#offline-inference)).
- **Interactive streaming** — real-time WebSocket voice conversations via the optimized NVIDIA inference container ([Interactive streaming deployment](#interactive-streaming-deployment)).

### Offline inference

Run offline speech-to-speech inference from this Hugging Face checkpoint. Requires an NVIDIA GPU, conda, and the Speech repository on the [`nemotron-labs-voicechat`](https://github.com/NVIDIA-NeMo/Speech/tree/nemotron-labs-voicechat) branch.

#### 1. Clone and set up the environment

```bash
git clone https://github.com/NVIDIA-NeMo/Speech.git
cd Speech
git switch nemotron-labs-voicechat
export NEMO_DIR="$(pwd)"

conda create -y -n voicechat python=3.12
conda activate voicechat
pip install torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0
pip install -e ".[all]"
pip uninstall -y nvidia-resiliency-ext
pip install transformers==4.56.0 tokenizers==0.22.0 lhotse==1.32.2 \
            huggingface-hub==0.34.4 hf-xet==1.1.9 torchcodec==0.10.0 \
            torch_audiomentations jinja2
pip install ninja packaging wheel einops
pip install --no-build-isolation --no-deps causal-conv1d==1.6.2.post1 mamba-ssm==2.3.2.post1
```

#### 2. Download the checkpoint

```bash
hf download nvidia/NVIDIA-NemotronLabs-VoiceChat-11B \
  --local-dir /path/to/checkpoint
```

#### 3. Run inference

```bash
conda activate voicechat
export NEMO_DIR=/path/to/Speech

# General conversation
python "$NEMO_DIR/examples/speechlm2/offline_voicechat_infer.py" \
  --checkpoint /path/to/checkpoint \
  --wav "$NEMO_DIR/examples/speechlm2/sample_audio/sample_general.wav" \
  --output-dir /path/to/output
```

When using a custom audio file, include sufficient trailing silence so the agent has time to respond.

Offline function calling does not invoke a live tool. `--api-response-json` points to a JSON file with a pre-written tool response. Its `tool_name` must match an available tool, and `response` must be ASCII-only and TTS-friendly. For interactive function calling with live tool execution, see [Interactive streaming deployment](#interactive-streaming-deployment).

```bash
# Function calling
python "$NEMO_DIR/examples/speechlm2/offline_voicechat_fc_infer.py" \
  --checkpoint /path/to/checkpoint \
  --wav "$NEMO_DIR/examples/speechlm2/sample_audio/sample_fc.wav" \
  --api-response-json "$NEMO_DIR/examples/speechlm2/function_calling/random_number_response.json" \
  --output-dir /path/to/output
```

After the run, inspect the JSON file in the output directory to see the predicted function call, such as:

```text
<TOOLCALL>[{"name": "generate_random_number", "arguments": {"min": 1, "max": 50}}]</TOOLCALL>
```

### Interactive streaming deployment

For interactive, low-latency voice conversations with this Hugging Face checkpoint, use the optimized NVIDIA inference container. It packages the model with the NVIDIA inference stack (CUDA, Triton, vLLM) and exposes a bidirectional WebSocket interface with function calling support. Full instructions are in the [Github repo](https://github.com/NVIDIA-NeMo/Speech/tree/nemotron-labs-voicechat/voicechat_realtime_instructions):

* [Prerequisites](https://github.com/NVIDIA-NeMo/Speech/blob/nemotron-labs-voicechat/voicechat_realtime_instructions/prerequisites.md) — hardware, software, and driver requirements
* [Deploy and Run](https://github.com/NVIDIA-NeMo/Speech/blob/nemotron-labs-voicechat/voicechat_realtime_instructions/deploy.md) — launch the container and run voice conversations
* [Generate Model Repository](https://github.com/NVIDIA-NeMo/Speech/blob/nemotron-labs-voicechat/voicechat_realtime_instructions/generate-model-repo.md) — build a Triton model repository from a local NeMo checkpoint
* [API Reference](https://github.com/NVIDIA-NeMo/Speech/blob/nemotron-labs-voicechat/voicechat_realtime_instructions/api-reference.md) — WebSocket and HTTP API reference

## Function-calling system prompt example

The default Jinja template appends the available tools and tool-call protocol to the supplied system message. See [`offline_voicechat_fc_infer.py`](https://github.com/NVIDIA-NeMo/Speech/blob/nemotron-labs-voicechat/examples/speechlm2/offline_voicechat_fc_infer.py) for the default function-calling system prompt and prompt construction logic, and [`template.jinja`](https://github.com/NVIDIA-NeMo/Speech/blob/nemotron-labs-voicechat/examples/speechlm2/function_calling/template.jinja) for the template.

System prompts and API/tool responses must be ASCII-only. Avoid Unicode punctuation and symbols (for example em dashes, en dashes, degree symbols, and emoji). Convert tool responses into concise, TTS-friendly ASCII sentences before passing them to the model.

For example, the rendered prompt can look like:

```text
You are an AI voice assistant developed by NVIDIA. Your name is NVIDIA Voice Chat. Your job is to be helpful and harmless and have engaging conversations in English. Maintain a warm and friendly tone. Keep the dialogue open and ongoing. Be clear and direct, especially when answering yes or no questions and multiple-choice questions. Avoid long answers unless the user asks you to provide details or context. You must provide diverse responses and rephrase answers if the user asks the same question. DO NOT interrupt the user when they are speaking, let them finish their turn before answering.

When you receive a request, follow this decision process:
1. Does the request match one of your available tools below? If yes, you MUST call that tool - never answer it directly from your own knowledge, even if you think you know the answer.
2. Is it a general knowledge question (history, science, geography, math, facts, etc.)? If yes, answer directly from your own knowledge - do not call any tool.
3. Does it require an external action or live data that none of your tools cover (e.g. ordering food, sending email)? If yes, politely say you don't have that capability.

NEVER say "I don't have a tool for that" for general knowledge questions you can answer yourself.

DO NOT use any tools when not needed to answer the user's requests, under no circumstance.

You are an expert across history, geography, science, math, literature, biographies, languages, recipes, programming, current affairs, and general knowledge. When the user asks about any of these, answer directly and conversationally from your own knowledge - no <TOOLCALL>.

Call a tool ONLY when the user's request matches one of the tools listed in <AVAILABLE_TOOLS> below. For every other request, do not call any tool - just answer from your knowledge. Never invent or call a tool name that is not literally in <AVAILABLE_TOOLS>.

Tool-call arguments must be values the user spoke. If a required argument is missing, ask the user; never guess.

If a tool call fails or returns an error, do not retry the tool call for the same request. Tell the user that the API has an issue.

You can use the following tools to assist the user if required:
<AVAILABLE_TOOLS>[{"name": "get_weather", "description": "Get the current weather for a city", "parameters": {"type": "object", "properties": {"city": {"type": "string", "description": "The city name as the user spoke it"}}, "required": ["city"]}}, {"name": "get_stock_price", "description": "Get the current stock price for a given ticker symbol", "parameters": {"type": "object", "properties": {"symbol": {"type": "string", "description": "The stock ticker symbol as stated by the user"}}, "required": ["symbol"]}}, {"name": "get_top_news", "description": "Get today's top one news headline from Google News", "parameters": {"type": "object", "properties": {"topic": {"type": "string", "description": "Optional topic: business, technology, science, health, sports, entertainment"}}, "required": []}}]</AVAILABLE_TOOLS>

If you decide to call any tool(s), use the following format:
<TOOLCALL>[{"name": "tool_name1", "arguments": "tool_args1"}, {"name": "tool_name2", "arguments": "tool_args2"}]</TOOLCALL>

The user will execute tool-calls and return responses from tool(s) in this format:
<TOOL_RESPONSE>[{"tool_response1"}, {"tool_response2"}]</TOOL_RESPONSE>

Based on the tool responses, you can call additional tools if needed, correct tool calls if any errors are found, or just respond to the user.
```

## Known Limitations

See the [Known Limitations](https://github.com/NVIDIA-NeMo/Speech/blob/nemotron-labs-voicechat/README.md#known-limitations) section for issues identified through extensive internal testing. These limitations may not affect typical usage.

## Ethical Considerations
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications.  When downloaded or used in accordance with our terms of service, developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse. <br> 

Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).


## References:
[1] [NemotronLabs VoiceChat: An Open Full-duplex Speech-to-Speech Model with Tool Calling Capabilities](https://arxiv.org/pdf/2609.21967) <br> 
[2] [SALM-Duplex: Efficient and Direct Duplex Modeling for Speech-to-Speech Language Model](https://arxiv.org/abs/2505.15670) <br> 
[3] [Open Full-duplex Voice Agent with Speech-to-Speech Language Model](https://ieeexplore.ieee.org/abstract/document/11434669) <br>
[4] [Audio Flamingo 3: Advancing Audio Intelligence with Fully Open Large Audio Language Models](https://arxiv.org/abs/2507.08128) <br>
[5] [PersonaPlex: Voice and role control for full duplex conversational speech models](https://research.nvidia.com/labs/adlr/files/personaplex/personaplex_preprint.pdf) <br>

## Citation

```
@misc{balam2026nemotronlabsvoicechatopenfullduplex,
      title={NemotronLabs VoiceChat: An Open Full-duplex Speech-to-Speech Model with Tool Calling Capabilities}, 
      author={NVIDIA},
      year={2026},
      eprint={2609.21967},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2609.21967}, 
}
```
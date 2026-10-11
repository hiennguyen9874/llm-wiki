---
pipeline_tag: text-generation
tags:
- turn detection
- conversational
- natural language understanding
license: apache-2.0
---
# **TEN Turn Detection**

***Turn detection for full-duplex dialogue communication***


## Introduction

**TEN Turn Detection** is an advanced intelligent turn detection model designed specifically for natural and dynamic communication between humans and AI agents. This technology addresses one of the most challenging aspects of human-AI conversation: detecting natural turn-taking cues and enabling contextually-aware interruptions. TEN incorporates deep semantic understanding of conversation context and linguistic patterns to create more natural dialogue with AI.
<div align="center">
  <img src="images/turn_detection.svg" alt="TEN Turn Detection SVG Diagram" width="800"/>
</div>

**TEN Turn Detection** categorizes user's text into three key states:

**finished**: A finished utterance where the user has expressed a complete thought and expects a response. Example: "Hey there I was wondering can you help me with my order"

**wait**: An wait utterance where the user has explicitly instructed the AI not to speak. Example: "Shut up"

**unfinished**: A clearly unfinished utterance where the user has momentarily paused but intends to continue speaking. Example: "Hello I have a question about"

These three classification states allow the TEN system to create natural conversation dynamics by intelligently managing turn-taking, reducing awkward interruptions while maintaining conversation flow.

TEN Turn Detection utilizes a multi-layered approach based on the transformer-based language model（Qwen2.5-7B） for semantic analysis.

## Key Features

- **Context-Aware Turn Management**
TEN Turn Detection analyzes linguistic patterns and semantic context to accurately identify turn completion points. This capability enables intelligent interruption handling, allowing the system to determine when interruptions are contextually appropriate while maintaining natural conversation flow across various dialogue scenarios.

- **Multilingual Turn Detection Support**
TEN Turn Detection provides comprehensive support for both English and Chinese languages. It is engineered to accurately identify turn-taking cues and completion signals across multilingual conversations.

- **Superior Performance**
Compared with multiple open-source solutions, TEN achieves superior performance across all metrics on our publicly available test dataset.

## Prepared Dataset
We have open-sourced the TEN-Turn-Detection TestSet, a bilingual (Chinese and English) collection of conversational inputs specifically designed to evaluate turn detection capabilities in AI dialogue systems. The dataset consists of three distinct components:

*wait.txt*: Contains expressions requesting conversation pauses or termination

*unfinished.txt*: Features incomplete dialogue inputs with truncated utterances

*finished.txt*: Provides complete conversational inputs across multiple domains


## Detection Performance

We conducted comprehensive evaluations comparing several open-source models for turn detection using our test dataset:

<div align="center">


| LANGUAGE | MODEL | FINISHED<br>ACCURACY | UNFINISHED<br>ACCURACY | WAIT<br>ACCURACY |
|:--------:|:-----:|:--------------------:|:----------------------:|:----------------:|
| English  | Model A | 59.74% | 86.46% | N/A |
| English  | Model B | 71.61% | 96.88% | N/A |
| English  | **TEN Turn Detection** | **90.64%** | **98.44%** | **91%** |




| LANGUAGE | MODEL | FINISHED<br>ACCURACY | UNFINISHED<br>ACCURACY | WAIT<br>ACCURACY |
|:--------:|:-----:|:--------------------:|:----------------------:|:----------------:|
| Chinese  | Model B | 74.63% | 88.89% | N/A |
| Chinese  | **TEN Turn Detection** | **98.90%** | **92.74%** | **92%** |


</div>

> **Notes:** 
> 1. Model A doesn't support Chinese language processing
> 2. Neither Model A nor Model B support the "WAIT" state detection

## Quick Start

TEN Turn Detection is also available on github [TEN-framework/ten-turn-detection](https://github.com/TEN-framework/ten-turn-detection)

### Installation

```
pip install "transformers>=4.45.0"
pip install "torch>=2.0.0"
```

### Model Weights

The TEN Turn Detection model is available on HuggingFace

### Inference

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load model and tokenizer
model_id = 'TEN-framework/TEN_Turn_Detection'
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, torch_dtype=torch.bfloat16)
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

# Move model to GPU
model = model.cuda()
model.eval()

# Function for inference
def analyze_text(text, system_prompt=""):
    inf_messages = [{"role":"system", "content":system_prompt}] + [{"role":"user", "content":text}]
    input_ids = tokenizer.apply_chat_template(
        inf_messages, 
        add_generation_prompt=True, 
        return_tensors="pt"
    ).cuda()
    
    with torch.no_grad():
        outputs = model.generate(
            input_ids, 
            max_new_tokens=1, 
            do_sample=True, 
            top_p=0.1, 
            temperature=0.1, 
            pad_token_id=tokenizer.eos_token_id
        )
        
    response = outputs[0][input_ids.shape[-1]:]
    return tokenizer.decode(response, skip_special_tokens=True)

# Example usage
text = "Hello I have a question about"
result = analyze_text(text)
print(f"Input: '{text}'")
print(f"Turn Detection Result: '{result}'")
```

## Citation
If you use TEN Turn Detection in your research or applications, please cite:

```
@misc{TEN_Turn_Detection,
author = {TEN Team},
title = {TEN Turn Detection: Turn detection for full-duplex dialogue communication 

},
year = {2025},
url = {https://github.com/TEN-framework/ten-turn-detection},
}
```
## License 
This project is Apache 2.0 licensed.
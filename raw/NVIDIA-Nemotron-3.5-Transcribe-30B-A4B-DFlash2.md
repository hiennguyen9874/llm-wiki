---
license: other
license_name: openmdw-1.1
license_link: https://openmdw.ai/license/1-1/
tags:
- nvidia
- nemotron-3.5
- speculative-decoding
- dflash2
- draft-model
- speech
- asr
- vllm
base_model: nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B
track_downloads: true
---

# NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-DFlash2

This is a DFlash2 draft model for speculative decoding with [NVIDIA-Nemotron-3.5-Transcribe-30B-A4B](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B). It speeds up generation by proposing several tokens at once, which the main model then verifies.

**This is not a standalone model.** It cannot transcribe audio on its own and must be served together with Nemotron-3.5-Transcribe-30B-A4B. For the model description, capabilities, benchmark results, prompts, training data, and the Model Card++ subcards, see the [main model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B).

This model is ready for commercial or non-commercial use.

## Model Summary

| | |
|:---|:---|
| **Parameters** | Approximately 570M |
| **Architecture** | DFlash2 block-diffusion draft model with 6 layers, conditioned on the hidden states of 6 layers of the main model (layers 1, 5, 19, 29, 41, and 51) |
| **Precision** | BF16 |
| **Draft Length** | Up to 15 tokens per step; 7 is the recommended starting point |
| **Training** | Trained to predict the greedy outputs of the main model on examples from its supervised fine-tuning mixture |
| **Compatible Main Models** | Nemotron-3.5-Transcribe-30B-A4B in BF16, FP8, and NVFP4 |
| **License** | [OpenMDW-1.1](https://openmdw.ai/license/1-1/) |

## License / Terms of Use

Use of this model is governed by the [OpenMDW License Agreement, version 1.1 (OpenMDW-1.1)](https://openmdw.ai/license/1-1/). Users are responsible for complying with this license and with any third-party licenses or notices applicable to components included in the distributed model materials.

## Quick Start

**NOTICE AND DISCLAIMER:** This software automatically retrieves, accesses or interacts with external materials. Those retrieved materials are not distributed with this software and are governed solely by separate terms, conditions and licenses. You are solely responsible for finding, reviewing and complying with all applicable terms, conditions, and licenses, and for verifying the security, integrity and suitability of any retrieved materials for your specific use case. This software is provided "AS IS", without warranty of any kind. The author makes no representations or warranties regarding any retrieved materials, and assumes no liability for any losses, damages, liabilities or legal consequences from your use or inability to use this software or any retrieved materials. Use this software and the retrieved materials at your own risk.

1. Set up vLLM 0.32.0 and the latest NeMo Speech main branch, and download the main model, as described in the main model's [inference setup](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B#environment-setup).

2. vLLM 0.32.0 needs a small fix to its DFlash2 implementation; without it, the server can fail when requests finish. Apply it once to the environment:

```bash
python - <<'EOF_PATCH'
from pathlib import Path
import vllm
path = Path(vllm.__file__).parent / "model_executor/models/qwen3_dflash2.py"
source = path.read_text()
if "safe_anchor_token_ids" not in source:
    old = "    successors = successor_table[candidate_ids]\n"
    anchor = "            anchor_token_ids[:, None, None].expand(-1, 1, top_k),"
    assert source.count(old) == 1 and source.count(anchor) == 1, "unexpected vLLM version"
    source = source.replace(old, (
        "    safe_anchor_token_ids = anchor_token_ids.clamp(\n"
        "        min=0, max=predecessor_table.shape[0] - 1\n"
        "    )\n" + old
    )).replace(anchor, "            safe_anchor_token_ids[:, None, None].expand(-1, 1, top_k),")
    path.write_text(source)
EOF_PATCH
```

The fix modifies vLLM source code (Copyright contributors to the vLLM project), which is licensed under the Apache License, Version 2.0, not under OpenMDW-1.1; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

3. Start the main model's server as described in its [Quick Start](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B#quick-start), with these changes: replace the MTP `--speculative-config` with the DFlash2 configuration below, remove `--middleware`, and disable the CTC timestamp alignment. The draft model is downloaded from Hugging Face automatically.

```bash
--speculative-config '{"method":"dflash","num_speculative_tokens":7,"model":"nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-DFlash2"}'
```

The CTC timestamp alignment is not available with DFlash2:

```bash
--hf-overrides '{"ctc_timestamps":{"enabled":false}}'
```

vLLM runs DFlash2 only on its V2 model runner, so also run `unset VLLM_USE_V2_MODEL_RUNNER` before starting the server.

Send requests exactly as to the main model; the draft model does not change the API.

## Contributing

Contributions are welcome. All contributions must be signed off under the Developer Certificate of Origin; see [CONTRIBUTING.md](CONTRIBUTING.md).

## Limitations

- **Requires the main model.** Use this draft model only with Nemotron-3.5-Transcribe-30B-A4B. It was trained against the released checkpoint, and its speedup on other checkpoints has not been measured.
- **Same output as the main model.** The main model verifies every proposed token, so with greedy decoding the output matches that of the main model without speculative decoding, apart from small numerical differences. The draft model affects speed, not accuracy.
- **No word timestamps.** The DFlash2 integration in vLLM does not support the CTC timestamp alignment. Use MTP speculative decoding, or none, when word timestamps are needed.
- **Speedup depends on the workload.** The acceptance length is lower on long recordings than on short ones. On a single RTX PRO 6000 Blackwell GPU, DFlash2 gives the lowest latency for a single request, whereas MTP can give higher throughput on 10-minute recordings; see the [tech report](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf) for measurements. DFlash2 and MTP are alternatives and are not combined.

## Ethical Considerations

NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications. Developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.

For more detailed information on ethical considerations for this model, please see the Model Card++ Bias, Explainability, Safety & Security, and Privacy Subcards of the [main model](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B).

Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).

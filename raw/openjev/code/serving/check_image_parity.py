"""Compare SGLang image logits to Transformers FP16 on identical pixel/token inputs.

Run --capture while the SGLang candidate is up, then --reference on a free GPU.
"""
import argparse
import base64
import json
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser(__doc__)
ap.add_argument("--model", required=True)
ap.add_argument("--image", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--endpoint", default="http://localhost:31013")
ap.add_argument("--capture", action="store_true")
ap.add_argument("--reference", action="store_true")
a = ap.parse_args()
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
hyps = ["The parcel is damaged.", "The parcel is undamaged."]
template = "Premise: An image: {block}\nHypothesis: {hyp}"
if a.capture:
    import httpx
    im = base64.b64encode(Path(a.image).read_bytes()).decode()
    r = httpx.post(a.endpoint + "/classify", json={
        "text": [template.format(block="<|vision_start|><|image_pad|><|vision_end|>", hyp=h) for h in hyps],
        "image_data": [im]*2}, timeout=180)
    r.raise_for_status()
    (out / "sglang.json").write_text(json.dumps(r.json(), indent=2))
    print(r.text, flush=True)
if a.reference:
    import torch
    from PIL import Image
    from transformers import AutoProcessor
    from transformers.models.qwen3_5.modeling_qwen3_5 import Qwen3_5Model, Qwen3_5PreTrainedModel
    torch.set_num_threads(4)
    processor = AutoProcessor.from_pretrained(a.model)
    tok = processor.tokenizer
    # Match SGLang's AutoProcessor image backend and grid, with no resizing overrides.
    vis = processor.image_processor(images=[Image.open(a.image).convert("RGB")], return_tensors="pt")
    count = int(vis["image_grid_thw"].prod()) // processor.image_processor.merge_size**2
    block = "<|vision_start|>" + "<|image_pad|>"*count + "<|vision_end|>"
    # Current Transformers' auto seq-cls class drops the vision tower. Use its
    # unmodified multimodal backbone plus the checkpoint's exact 3-way head.
    class ImageNLI(Qwen3_5PreTrainedModel):
        def __init__(self, config):
            super().__init__(config)
            self.model = Qwen3_5Model(config)
            self.score = torch.nn.Linear(config.text_config.hidden_size, 3, bias=False)
            self.post_init()

        def forward(self, **inputs):
            return self.score(self.model(**inputs, use_cache=False).last_hidden_state[:, -1])

    model, loading = ImageNLI.from_pretrained(a.model, dtype=torch.float16,
                                             attn_implementation="sdpa", output_loading_info=True)
    assert not loading.get("missing_keys") and not loading.get("unexpected_keys"), loading
    model = model.cuda().eval()
    logits = []
    lengths = []
    with torch.inference_mode():
        for h in hyps:
            inputs = tok(template.format(block=block, hyp=h), add_special_tokens=False, return_tensors="pt")
            lengths.append(inputs.input_ids.shape[1])
            inputs = {k: v.cuda() for k, v in inputs.items()}
            inputs.update({k: v.cuda().to(torch.float16) if k == "pixel_values" else v.cuda() for k, v in vis.items()})
            inputs["mm_token_type_ids"] = (inputs["input_ids"] == tok.convert_tokens_to_ids("<|image_pad|>")).long()
            logits.append(model(**inputs).float().cpu().tolist()[0])
    ours = np.array([r["embedding"] for r in json.loads((out / "sglang.json").read_text())])
    ref = np.array(logits)
    def softmax(x):
        x = np.exp(x-x.max(axis=1, keepdims=True))
        return x/x.sum(axis=1, keepdims=True)
    report = {"transformers_logits": logits, "tokens": lengths,
              "max_probability_error": float(abs(softmax(ours)-softmax(ref)).max()),
              "argmax_agree": bool((ours.argmax(1)==ref.argmax(1)).all())}
    (out / "parity.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    assert report["argmax_agree"] and report["max_probability_error"] < 0.02

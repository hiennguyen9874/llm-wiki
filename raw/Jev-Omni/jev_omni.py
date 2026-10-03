"""Public Jev-Omni multimodal loader and classifier inference helper."""
from __future__ import annotations

import inspect
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import torch
from huggingface_hub import snapshot_download
from PIL import Image
from transformers import AutoConfig, AutoProcessor

MODEL_ID = "akhilaaa3/Jev-Omni"


def _find_backbone(model):
    for path in ("model.language_model", "language_model.model", "model.text_model", "model"):
        node = model
        for part in path.split("."):
            node = getattr(node, part, None)
            if node is None:
                break
        if node is not None and hasattr(node, "layers"):
            return path, node
    raise RuntimeError("Could not locate the Gemma text backbone")


def _prompt(state, question, options):
    choices = "\n".join(f"{i + 1}. {value}" for i, value in enumerate(options))
    return (f"{state}\n\n---\n\nQUESTION: {question}\n\nOPTIONS:\n{choices}\n\n"
            f"Reply with only the number of the correct option (1-{len(options)}).\n"
            "Output a single number and nothing else.")


def _video_frames(path, count=16):
    import cv2
    cap = cv2.VideoCapture(str(path))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    wanted = sorted({int(round((total - 1) * (k + .5) / count)) for k in range(count)})
    frames, current = [], 0
    for index in wanted:
        while current < index and cap.grab():
            current += 1
        ok, frame = cap.read(); current += 1
        if not ok:
            break
        frames.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
    cap.release()
    if not frames:
        raise ValueError(f"Could not decode video: {path}")
    return frames


class JevOmni:
    """Probability classifier over 2–256 user-supplied options."""

    def __init__(self, model, head, processor, decoder, device="cuda"):
        self.model, self.head, self.processor, self.device = model, head, processor, device
        self._capture = {}
        decoder.register_forward_hook(lambda _m, _a, out: self._capture.__setitem__(
            "hidden", (out.last_hidden_state if hasattr(out, "last_hidden_state") else out[0])[:, -1].float()))
        self._extra = ({"logits_to_keep": 1}
                       if "logits_to_keep" in inspect.signature(model.forward).parameters else {})

    @torch.inference_mode()
    def predict(self, *, state, question, options, media=None, modality="text", video_frames=16):
        """Return {prediction, prediction_index, confidence, probabilities}.

        `media` is a local image/audio/video path. Omit it for text.
        """
        if not 2 <= len(options) <= 256:
            raise ValueError("Jev-Omni needs 2–256 options")
        if modality not in {"text", "image", "audio", "video"}:
            raise ValueError("modality must be text, image, audio, or video")
        if modality != "text" and media is None:
            raise ValueError(f"{modality} inference requires media=...")
        content, temporary = [], None
        if modality == "image":
            content.append({"type": "image", "image": Image.open(media).convert("RGB")})
        elif modality == "video":
            content.extend({"type": "image", "image": frame}
                           for frame in _video_frames(media, video_frames))
        elif modality == "audio":
            temporary = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temporary.close()
            subprocess.run(["ffmpeg", "-v", "error", "-i", str(media), "-t", "30",
                            "-ac", "1", "-ar", "16000", temporary.name], check=True)
            content.append({"type": "audio", "audio": temporary.name})
        content.append({"type": "text", "text": _prompt(state, question, options)})
        try:
            inputs = self.processor.apply_chat_template(
                [{"role": "user", "content": content}], add_generation_prompt=True,
                tokenize=True, return_dict=True, return_tensors="pt", enable_thinking=False)
        finally:
            if temporary is not None:
                Path(temporary.name).unlink(missing_ok=True)
        inputs = {k: v.to(self.device, dtype=torch.bfloat16) if torch.is_floating_point(v)
                  else v.to(self.device) for k, v in inputs.items()}
        self._capture.clear()
        with torch.autocast("cuda", dtype=torch.bfloat16):
            self.model(**inputs, use_cache=False, **self._extra)
            probs = self.head(self._capture["hidden"], torch.tensor([len(options)], device=self.device))[0, :len(options)].softmax(-1)
        values = probs.float().cpu().tolist()
        best = int(np.argmax(values))
        return {"prediction": options[best], "prediction_index": best,
                "confidence": values[best], "probabilities": dict(zip(options, values))}


class _Head256(torch.nn.Module):
    """Decision head: normalise the last hidden state, one logit per option slot."""

    def __init__(self, hidden):
        super().__init__()
        self.register_buffer("mu", torch.zeros(1, hidden))
        self.register_buffer("sd", torch.ones(1, hidden))
        self.linear = torch.nn.Linear(hidden, 256, dtype=torch.float32)

    def forward(self, features, counts):
        z = self.linear((features.float() - self.mu) / self.sd)
        return z.masked_fill(torch.arange(256, device=z.device)[None] >= counts[:, None], -1e30)


def load_jev_omni(model_id=MODEL_ID, device="cuda"):
    """Download and assemble the complete multimodal classifier.

    The repository root is one standard Transformers checkpoint (bf16, text +
    vision + audio) plus the decision head, so a single ~24 GB download is all
    it takes - no base-model download, no merging at load time.
    """
    if device != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("The reference loader currently requires a CUDA GPU")
    import json
    import transformers
    path = snapshot_download(model_id, allow_patterns=[
        "config.json", "generation_config.json", "model*.safetensors*", "processor_config.json",
        "tokenizer.json", "tokenizer_config.json", "chat_template.jinja",
        "decision_config.json", "head.pt"])
    config = AutoConfig.from_pretrained(path)
    model = getattr(transformers, config.architectures[0]).from_pretrained(
        path, dtype=torch.bfloat16, device_map=device).eval()
    decision = json.loads((Path(path) / "decision_config.json").read_text())
    head = _Head256(decision["hidden_size"]).to(device).eval()
    head.load_state_dict(torch.load(Path(path) / "head.pt", map_location=device, weights_only=True))
    _, decoder = _find_backbone(model)
    return JevOmni(model, head, AutoProcessor.from_pretrained(path), decoder, device)

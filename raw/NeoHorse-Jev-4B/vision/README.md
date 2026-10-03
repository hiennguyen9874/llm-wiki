# Image Inference Examples

See the [Deployment guide](https://huggingface.co/TokenRhythm/NeoHorse-Jev-4B/blob/main/DEPLOYMENT.md) for environment setup, image request formats, response fields, limits, and error handling.

| File | Purpose |
| --- | --- |
| `example.py` | Run image-based decisions locally |
| `example_request.json` | Sample question; replace it with your own single-question request |
| `http_example.py` | Encode a local image and send it to the HTTP API |
| `predictor.py` | Import wrapper for the installed `neohorse_decision.vision.VisionDecisionEngine` |
| `base_vision_provenance.json` | Record the source of the vision weights |
| `verification.json` | Record basic vision smoke tests and consistency checks |
| `LICENSE` | License for the vision components |

The language and vision weights are stored together in `backbone/`. The decision head is stored in `pointer_head.safetensors` at the model root. The vision weights come from Qwen3.5-4B and have not undergone additional vision training. The hashes of separate vision files in the provenance record are for traceability only; those files do not need to be loaded separately at runtime.

After installing the matching runtime package, set `MODEL_DIR` to the complete downloaded model directory. You can then run these commands from any working directory:

```bash
CUDA_VISIBLE_DEVICES=0 python "$MODEL_DIR/vision/example.py" \
  --model-dir "$MODEL_DIR" --image /path/to/image.png \
  --request "$MODEL_DIR/vision/example_request.json"

python "$MODEL_DIR/vision/http_example.py" --image /path/to/image.png \
  --base-url http://127.0.0.1:8080 --endpoint systemone
```

Each image request supports one static image and one question, using Noul, Choice, or Score. The basic vision verification records are not a general visual capability evaluation.

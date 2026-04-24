<div>

# Bi-IRRA: Multilingual Text-to-Image Person Retrieval via Bidirectional Relation Reasoning and Alignment

</div>

This repository provides the official PyTorch implementation of **Bi-IRRA**.

- [x] Release of code and multilingual annotation JSON files  
- [x] Release of pretraining checkpoints

---

## Environment

All experiments are conducted on 4 Nvidia A40 (48GB) GPUs with CUDA 11.7.

Install the required packages using:

```sh
pip install -r requirements.txt
```

---

## Download

1. **Datasets**  
   - Download CUHK-PEDES from [here](https://github.com/ShuangLI59/Person-Search-with-Natural-Language-Description)  
   - Download ICFG-PEDES from [here](https://github.com/zifyloo/SSAN)  
   - Download RSTPReid from [here](https://github.com/NjtechCVLab/RSTPReid-Dataset)  
   - Download UFineBench from [here](https://github.com/Zplusdragon/UFineBench)

2. **Annotations**  
   - Download the multilingual annotation JSON files from [here](https://huggingface.co/datasets/zzhugging/Bi-IRRA/tree/main)

3. **Pretrained Models**  
   - Download the xlm-roberta-base checkpoint from [here](https://huggingface.co/FacebookAI/xlm-roberta-base)
   - Download the CCLM-X2VLM checkpoint from [here](https://lf-robot-opensource.bytetos.com/obj/lab-robot-public/x2vlm_ckpts_2release/cclm_x2vlm_base.th)
   - We also provide the [checkpoint](https://huggingface.co/datasets/zzhugging/Bi-IRRA/tree/main) pretrained on the LUPerson dataset, which can be used as a replacement for the CCLM-X2VLM checkpoint to achieve better retrieval performance. 

---

## Configuration

Edit `config/config.yaml` (for CUHK-PEDES, ICFG-PEDES, RSTPReid) or `config/config_UFine.yaml` (for UFineBench) to set the paths for annotation files, image directories, tokenizer, and checkpoints.

A recommended directory structure:

```
|- CUHK-PEDES
   |- imgs
   |- annos
      |- train_reid_en.json
      |- train_reid_ch.json
      |- test_reid_en.json
      |- test_reid_ch.json
```

Example configuration in `config.yaml`:

```yaml
anno_dir: /path/to/CUHK-PEDES/annos
image_dir: /path/to/CUHK-PEDES/imgs
text_encoder: /path/to/xlm-roberta-base
resume: /path/to/CCLM-X2VLM
```

---

## Training

Start training with:

```sh
CUDA_VISIBLE_DEVICES=0,1,2,3 \
torchrun --rdzv_id=3 --rdzv_backend=c10d --rdzv_endpoint=localhost:0 --nnodes=1 --nproc_per_node=4 \
main.py
```

or simply run:

```sh
bash shell/train.sh
```

---

## Acknowledgements

This repository is partially based on [TBPS-CLIP](https://github.com/Flame-Chasers/TBPS-CLIP) and [X2-VLM](https://github.com/zengyan-97/X2-VLM). We thank the authors for their contributions.

---

## License

This project is licensed under the MIT License.

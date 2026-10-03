#!/usr/bin/env bash
# Full evaluation of openjev-4B v2 vs v1, as two parallel chains (devices 0 and 1). Runs after training finishes.
cd ~/qwen_nli
P=${PY:-python}
V1=ckpt/qwen3.5-4b-nli
V2=/mnt/qwen_nli_ckpt/qwen3.5-4b-nli-v2
E="env HF_HOME=/mnt/hf TOKENIZERS_PARALLELISM=false"
mkdir -p results/v2 logs/v2
RADAR="mnli gpqa mmlu arc_easy arc_challenge winogrande hellaswag gsm8k_mc4 gsm8k_mc10 chess gsm8k"
HARD="anli_r1 anli_r2 anli_r3 wanli scitail control"
(
  # chain 0: v2 on everything text, then images, then keenable
  $E CUDA_VISIBLE_DEVICES=0 $P eval.py --models $V2 --out results/v2/eval_v2.json --tasks $RADAR $HARD --bs 16 --max-len 4096 > logs/v2/eval_v2.log 2>&1
  $E CUDA_VISIBLE_DEVICES=0 $P eval_image_nli.py --models $V1 $V2 --data /mnt/nli_eval_vqa/parts/vqa_val.jsonl --image-root /mnt/nli_eval_vqa --out results/v2/image_nli.json > logs/v2/image_nli.log 2>&1
  $E CUDA_VISIBLE_DEVICES=0 $P webql_fulldoc.py --ckpt $V2 --out results/v2/webql_fulldoc_v2.json > logs/v2/webql_fulldoc.log 2>&1
  $E CUDA_VISIBLE_DEVICES=0 $P webql_gemini_prompt.py --ckpt $V2 --out results/v2/webql_geminiprompt_v2.json --bs 2 > logs/v2/webql_gp.log 2>&1
  $E CUDA_VISIBLE_DEVICES=0 $P webql_bench.py --ckpt $V2 --data data/sem_extract_bench.jsonl --gemini data/sem_extract_bench_gemini-3.5-flash-lite.jsonl --out results/v2/webql_bench_v2.json > logs/v2/webql_bench.log 2>&1
  echo CHAIN0_DONE
) > logs/v2/chain0.log 2>&1 &
(
  # chain 1: baselines on the new hard-NLI sets, then games, then the unchanged latent+MLP scheme
  $E CUDA_VISIBLE_DEVICES=1 $P eval.py --models $V1 dleemiller/ModernCE-large-nli --out results/v2/hardnli_v1_modernce.json --tasks $HARD --bs 16 --max-len 4096 > logs/v2/hardnli_v1.log 2>&1
  $E CUDA_VISIBLE_DEVICES=1 $P flappy.py --ckpt $V2 --episodes 6 --fps 15 --max-steps 900 --record-only --seed 1 --zero-shot-only --hyp sign --out results/v2/flappy_sign_v2.json > logs/v2/flappy.log 2>&1
  $E CUDA_VISIBLE_DEVICES=1 $P flappy.py --ckpt $V2 --episodes 6 --fps 15 --max-steps 900 --record-only --seed 1 --zero-shot-only --hyp position --out results/v2/flappy_position_v2.json > logs/v2/flappy_pos.log 2>&1
  $E CUDA_VISIBLE_DEVICES=1 $P doom.py --ckpt $V2 --episodes 5 --zero-shot-only --hyp position --out results/v2/doom_position_v2.json --video-nli results/v2/doom_position_v2.mp4 > logs/v2/doom.log 2>&1
  $E CUDA_VISIBLE_DEVICES=1 $P doom_vision.py --ckpt $V2 --episodes 5 --mode zeroshot --variants pixels pixels_sym thirds precise where_closest --out results/v2/doom_vision_v2.json --video results/v2/doom_vision_v2.mp4 > logs/v2/doom_vision.log 2>&1
  $E CUDA_VISIBLE_DEVICES=1 $P latent_mlp.py extract --ckpt $V2 --out /mnt/qwen_nli_ckpt/latents_4b_v2 --tasks gpqa mmlu arc_easy arc_challenge winogrande chess hellaswag gsm8k_mc4 gsm8k_mc10 > logs/v2/latent_extract.log 2>&1
  $E CUDA_VISIBLE_DEVICES=1 $P latent_mlp.py train --latents /mnt/qwen_nli_ckpt/latents_4b_v2 --tasks gpqa mmlu arc_easy arc_challenge winogrande chess hellaswag gsm8k_mc4 gsm8k_mc10 --out results/v2/latent_mlp_4b_v2.json > logs/v2/latent_train.log 2>&1
  echo CHAIN1_DONE
) > logs/v2/chain1.log 2>&1 &
wait
echo ALL_EVALS_DONE

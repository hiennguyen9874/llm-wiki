#!/usr/bin/env bash
# 11 Flappy variants (prompts / hypothesis phrasing / label & training params / backbone), as two parallel chains.
# usage: bash sweep_flappy.sh
cd ~/qwen_nli
P=${PY:-python}
COMMON="--episodes 6 --fps 15 --max-steps 900 --record-only --seed 1"
run() { name=$1; gpu=$2; shift 2; HF_HOME=/mnt/hf CUDA_VISIBLE_DEVICES=$gpu $P flappy.py $COMMON --out results/sweep/$name.json "$@" > logs/sweep_$name.log 2>&1; }
mkdir -p results/sweep logs
(
run v00_base          0
run v01_numeric       0 --prompt numeric
run v02_coach         0 --prompt coach
run v03_ascii         0 --prompt ascii
run v04_hyp_should    0 --hyp should
run v05_coach_should  0 --prompt coach --hyp should
) &
(
run v06_lookahead6    1 --lookahead 6 --skip-nli
run v07_noise0.3      1 --noise 0.3 --skip-nli
run v08_data200       1 --collect-episodes 200 --skip-nli
run v09_eps0.3        1 --eps 0.3 --skip-nli
run v10_raw4b         1 --ckpt Qwen/Qwen3.5-4B
) &
wait
echo SWEEP_DONE

---
type: Concept
title: DeepSeek-V4.1-Flash Reference Inference Implementation
description: Readable PyTorch plus TileLang reference for DeepSeek-V4.1-Flash covering TP checkpoint conversion, autoregressive runtime, sparse attention, Engram, DSpark forward, and vision preprocessing.
tags: [deepseek-v4.1, inference, reference-implementation, tensor-parallel, sparse-attention, engram, dspark, tilelang, multimodal]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: readme
    resource: ../raw/inference/README.md
    title: Minimal inference README
  - id: config
    resource: ../raw/inference/config.json
    title: Reference inference config
  - id: convert
    resource: ../raw/inference/convert.py
    title: HF to TP checkpoint conversion
  - id: generate
    resource: ../raw/inference/generate.py
    title: Autoregressive generation entry point
  - id: model
    resource: ../raw/inference/model.py
    title: Transformer reference model
  - id: kernel
    resource: ../raw/inference/kernel.py
    title: TileLang quantization, GEMM, attention, and mHC kernels
  - id: engram
    resource: ../raw/inference/engram.py
    title: Engram hash layout and state
  - id: vision
    resource: ../raw/inference/vision.py
    title: ViT and aligner reference
  - id: imgproc
    resource: ../raw/inference/image_processor.py
    title: Image preprocessing and VL input preparation
  - id: run
    resource: ../raw/inference/run.sh
    title: Reference run wrapper
  - id: reqs
    resource: ../raw/inference/requirements.txt
    title: Reference inference dependencies
  - id: extxt
    resource: ../raw/inference/examples/example.txt
    title: Plain-text example prompts
  - id: exjson
    resource: ../raw/inference/examples/example_harmony.json
    title: Harmony JSON example cases
---

DeepSeek-V4.1-Flash ships a readable reference implementation rather than a production serving engine: the model code covers vision encoder plus aligner, sliding-window plus compressed sparse attention with two-level indexing, Engram n-gram lookups, MoE, Hyper-Connections, and the DSpark forward path, while generation itself is plain autoregressive sampling[^readme][^model][^generate].

## Scope and non-goals

The README frames this explicitly as a readable reference, not a production server[^readme]. There is no disaggregated prefill/decode, Radix/prefix cache, continuous batching, or speculative-verify loop: `generate.py` does right-padded batch prefill plus one-token decode steps, and DSpark only implements the forward/embed/head path with no caller for `forward_spec` in the runtime[^generate][^model].

`ModelArgs` field names are exactly the config JSON keys; its Python defaults build a small `dim=1024`, 5-layer test model, not the released shapes, though scale-independent values such as `norm_eps`, `score_func`, and `hc_*`/Engram settings do match the release[^model]. Runtime limits `max_batch_size` and `max_seq_len` size the KV caches rather than describing model shape[^model].

Dependencies are `torch>=2.10.0`, `transformers`, `tokenizers`, `safetensors>=0.7.0`, `numpy`, `sympy`, `Pillow`, `tilelang==0.1.8`, and `tqdm`[^reqs].

## Checkpoint conversion

The runtime uses one converted checkpoint file per tensor-parallel rank, produced from an HF checkpoint directory by `convert.py`[^readme][^convert][^run].

Invocation shape from the README[^readme]:

```bash
python convert.py \
  --hf-ckpt-path "${HF_CKPT_PATH}" \
  --save-path "${SAVE_PATH}" \
  --model-parallel "${MP}" \
  --expert-dtype fp4 \
  --tokenizer-path "${HF_CKPT_PATH}"
```

Conversion behavior[^convert]:

- Expert counts are inferred from weight names, so they are not passed explicitly; backbone and MTP counts come from `mlp`/`ffn.experts.N` with and without the `mtp.` prefix[^readme][^convert].
- Both counts must divide `MP`; MTP token embedding and output head tied to the backbone are skipped[^convert].
- Names are normalized: strip leading `model.`, `self_attn` to `attn`, non-vision `mlp` to `ffn`, `weight_scale_inv` to `scale`, and `e_score_correction_bias` to `bias`[^convert].
- Sharding: routed experts split by expert-index range per rank; `engram.embed` rows shard with ceiling division and zero/one padding for weight/scale; `embed`, `wq_b`, `wo_a`, `wo_b`, `head`, `attn_sink`, and `weights_proj` shard along the mapped dimension; all other tensors replicate[^convert].
- `wo_a.weight` blocks are dequantized from 32- or 128-sized blocks through their scale to BF16[^convert].
- INT8 expert weights become FP8 E4M3 plus E8M0 `scale_max_offset_bits` when `--expert-dtype fp8`, via a lossless E2M1-to-E4M3 cast whose `MAX_OFFSET_BITS=6` keeps `6.0*2^6=384` under the 448 E4M3 maximum; otherwise they are viewed as `float4_e2m1fn_x2` for FP4[^convert].
- Outputs are `model{rank}-mp{MP}.safetensors` plus copied `tokenizer.json` and `tokenizer_config.json`[^convert][^run].
- When `model.safetensors.index.json` exists, seen tensors must exactly equal the expected map, guarding against mid-upload sources[^convert].

`run.sh` validates that all `MP` shards and the input file exist before launching `torchrun --nproc-per-node MP generate.py --ckpt-path --config --input-file`; paths inside examples resolve from the inference directory[^run].

## Runtime and generation

`generate()` right-pads prompts, runs the first forward over `[:min_prompt_len]` as prefill, then generates one token per step while overriding positions still inside a prompt with ground-truth tokens[^generate]. Total length is capped by `max_seq_len` and `max_new_tokens + max(prompt_lens)`; completion slicing stops at `eos_id`[^generate].

Multimodal constraints are strict: image spans must end before the shortest prompt so they are only visible to the prefill pass, `generate.py` asserts that span, and VL prompts are generated one at a time rather than batched[^generate]. `TEXT` is `-1`, so any `token_types >= 0` marks an image span for MoE routing and Engram masking[^model][^imgproc].

Launch defaults: NCCL when `WORLD_SIZE>1`, rank-0-only printing, CUDA device selection, `expandable_segments`, BF16 default dtype, 8 CPU threads, and fixed seed `33377335`; interactive mode forces batch size 1 and 64K `max_seq_len`, broadcasts typed prompts from rank 0, and supports `/exit` and `/clear` with `thinking_mode` in `chat` or `thinking`[^generate]. File mode accepts blank-line-separated TXT prompts with `<image>path</image>` tags or Harmony JSON cases, encoding each case then expanding image placeholders[^generate]. Sampling uses the Gumbel-max trick as a GPU-friendly multinomial equivalent, with exact argmax at temperature 0[^model].

One model exists per process: `Transformer.__init__` sets module-global `world_size`, `rank`, and weight-storage dtype from `args.dtype`[^model].

## Released configuration snapshot

`config.json` is the durable shape snapshot for this stack[^config]:

- Backbone: `vocab_size=129280`, `dim=5120`, `n_layers=40`, `n_mtp_layers=3`, `moe_inter_dim=2304`, `n_heads=64`, `head_dim=512`, `rope_head_dim=64`[^config].
- MoE: 384 routed plus 1 shared expert, 6 active per token, `sqrtsoftplus` scoring, `route_scale=1.5`, `swiglu_limit=10.0`[^config].
- Attention: `q_lora_rank=1280`, `o_groups=8`, `o_lora_rank=1024`, `window_size=128`, `norm_eps=1e-20`[^config].
- Sparse layout: `kv_source_layers=[2,8,14,20]`, `index_source_layers=[2,8,14,20,24,28,32,36]`, `candidate_source_layer=20`, `candidate_topk_blocks=2048`, `candidate_block_size=8`, `index_topk=512`, `index_n_heads=32`, `index_head_dim=128`[^config].
- Positions: `original_seq_len=65536`, `rope_theta=10000`, `rope_factor=16`, `beta_fast=32`, `beta_slow=1`, `compress_rope_theta=160000`[^config].
- `compress_ratios` has 43 entries for 40 backbone plus 3 MTP layers: two leading `0`, eighteen `2`, twenty `1`, three trailing `0`[^config][^model].
- Hyper-Connections: `hc_mult=4`, `hc_sinkhorn_iters=20`, `hc_eps=1e-6`[^config].
- Engram: layers `[1,14]`, `engram_vocab_size=16000000`, `engram_num_embeddings=[384006168,384016682]`, `max_ngram_size=4`, `pad_id=2`, `compressed_vocab_size=99092`, `n_heads=8`, `head_dim=256`[^config].
- Dtypes: `dtype=fp8`, `expert_dtype=fp4`[^config].
- Vision: 32 layers, `dim=1024`, 16 heads, `inter_dim=2816`, `patch_size=14`, `downsample_ratio=3`, `max_n_token=1024`, `min_pixels=295936`, no max aspect-ratio cap, `image_token_id=129264`, `vision_rope_theta=10000`[^config].
- DSpark: `block_size=5`, `noise_token_id=128799`, `target_layer_ids=[37,38,39]`, `markov_rank=256`, 128 routed with 3 active experts[^config].

## Attention, compression, and indexer

Each layer computes its own Q and sliding-window KV; only `kv_source_layers` compress their own KV while others read the shared cache, and only `index_source_layers` run an indexer while intermediate layers reuse the published `topk_idxs`[^model]. Cross-layer handoff uses a single-slot `SharedAttentionRuntime` for compressed KV, index keys, top-k indices, and candidates; layer order makes one slot sufficient with no reset between forwards[^model].

Window path: KV is normalized, RoPE-rotated, FP8-quantized over the whole post-RoPE vector, kept in a per-layer ring of `window_size` slots, and selected by materialized `[batch, m, topk]` int32 indices with `-1` for empty slots[^model]. Prefill seeds the ring; decode writes one token and attends over the whole window oldest-first[^model].

Compression path: `Compressor` pools `compress_ratio` consecutive tokens with a learned softmax gate in FP32; ratio 1 is a plain BF16 projection with no gate or state, while higher ratios hold partial groups in `kv_state`/`score_state` and emit only on group completion[^model]. The latent is returned pre-RoPE because the indexer needs the unrotated form; `Attention` rotates it afterward, quantizes compressed KV in groups of 16 with E4M3 scales, and assigns group `j` to position `j*ratio`[^model].

Indexer path: a small side attention uses FP4 query heads against one shared key per compressed position, rectifies scores, combines them with `weights_proj`, all-reduces across TP, masks unreachable positions to `-inf`, keeps `index_topk` entries, re-sorts them into position order, shifts by the window-KV width as `offset`, and emits `-1` for unreachable picks[^model]. Index-key owners derive keys from the compressor latent before `Attention` overwrites that storage with RoPE plus quantized values; indexer Q/K use the same YaRN-extended frequencies as their layer, with pure sliding-window layers disabling YaRN[^model].

Two-level filtering: the candidate source publishes a bool mask over positions by scoring blocks with their best position score, padding the final partial block with `-inf`, pinning the block holding the newest position with `+inf`, keeping `topk_blocks`, and dropping `-inf` picks from unreachable blocks; later layers mask to that pool before their own top-k[^model].

Output handling: concatenated window plus compressed KV goes through one `sparse_attn` call, the output has the query rotation removed by inverse RoPE so caches stay in one shared rotated form, and the grouped `wo_a` projection is an einsum over groups rather than a `Linear` because it is block-diagonal; the checkpoint stores it dequantized to BF16 with a note that an FP8 grouped GEMM would halve memory[^model].

## MoE, Hyper-Connections, norms, and heads

`linear()` dispatches on stored weight dtype: FP4 weights take FP8 activations through `fp4_gemm`, FP8 weights through `fp8_gemm`, otherwise `F.linear`[^model]. `ColumnParallelLinear` splits output and needs no reduction; `RowParallelLinear` splits reduction, all-reduces in FP32, then adds bias[^model]. `ParallelEmbedding` shards vocab rows and zero-masks off-rank ids before all-reduce[^model].

Gating adds a learned correction bias only for expert selection while weights come from unbiased scores; vision-enabled models keep a separate `bias_vl` for image-span tokens and select it by `image_mask`[^model]. Supported score functions are softmax, sigmoid, and `sqrtsoftplus`; top-k weights renormalize unless top-1 and scale by `route_scale`[^model]. Each SwiGLU expert clamps the up branch on both sides and the gate branch from above at `swiglu_limit`; routed experts shard across ranks with per-rank `None` placeholders and a bincount-skipped dispatch plus all-reduce, alongside one shared expert taken by every token[^model].

Hyper-Connections carry `hc_mult` parallel residual copies: `hc_pre` collapses copies with `pre_mix`, `hc_post` expands with `post` plus residual mixing through doubly-stochastic `comb`, and `hc_mixes` derives all three coefficient sets from one flattened-stream projection followed by Sinkhorn normalization[^model]. Coefficients computed by one sublayer are consumed by the next, so attention uses the previous FFN's mix and the FFN uses the current attention's mix; the initial mix is one-hot on copy 0[^model].

`ParallelHead` shards vocab, keeps weights in FP32 for direct FP32 logits, returns only the last position during generation, and all-gathers across TP[^model].

## Engram

Engram writes hashed n-gram rows into the residual stream gated by stream-to-key match: hash ids fetch rows, `wkv` forms one key per Hyper-Connection copy plus a shared value, the gate is a dimension-normalized dot product scaled by `dim^-0.5` with signed-sqrt plus sigmoid matching the training kernel, and image-span or otherwise masked positions get zero gate and pass through untouched[^model][^engram].

Tables stay FP8 with per-32-element scales and dequantize on lookup; the table shards rows across ranks with ceiling division and an all-reduce to assemble results[^model]. Layout gives every `(n-gram size, head)` pair its own prime-sized bucket range, drawn in order without reuse; the reference uses 2- through 4-grams over 8 heads per Engram layer[^engram]. Hash multipliers are per-layer RNG draws kept odd and bounded so `token_id * multiplier` cannot overflow int64; every multiplier derives from the compressed vocab size, so a mismatch would silently rehash the table[^engram].

Token compression normalizes decoded token text through NFKC, NFD, accent stripping, lowercasing, whitespace collapsing, and strip rules with a private-use sentinel preserving a lone space; partial UTF-8 byte tokens containing U+FFFD key by raw form instead[^engram]. Tokens that normalize alike collapse, so variants such as spaced/cased forms hash together; the implementation asserts the computed compressed size equals `engram_compressed_vocab_size`[^engram]. Hash state caches compressed ids across the prefill/decode split, stops look-back at sequence start and at `DEAD` image-span tokens so no n-gram spans an image boundary, fills missing history with the mapped pad id, and XORs multiplied ids incrementally with per-layer bucket modulus plus offset[^engram].

## DSpark forward-only

DSpark stages live under the `mtp.*` checkpoint namespace with `DSparkAttention` replacing full sparse attention[^model]. Stage 0 projects concatenated target-layer hidden means through `main_norm`/`main_proj`; only the final stage owns norm plus Markov and confidence heads; all stages share the backbone embedding and head objects[^model].

Prefill only seeds the window KV cache from main hidden states and returns the draft stream unchanged; decode attends over the retained window plus the current draft block, where the draft block sees `window + block` positions via a dedicated index layout[^model]. `forward_embed` builds block-sized draft inputs seeded with the sampled token followed by noise ids, expands them to Hyper-Connection copies, and returns the projected main stream alongside[^model]. `forward_head` adds per-position Markov logits to base logits, samples autoregressively within the block, stacks Markov embeddings, and predicts per-position confidence from hidden plus Markov state for survival-aware scheduling[^model]. Draft tokens are text-only and bypass the VL routing bias[^model].

## Vision and image preprocessing

`ViT` is a full bidirectional Transformer over one image with 2D RoPE, linear patch embedding, RMSNorm, SwiGLU MLP, and final norm[^vision]. `Aligner` applies 3x3 pixel-unshuffle for 9x token reduction, pads incomplete grids, unfolds stride-matched patches, and maps through a two-layer MLP to backbone width[^vision][^imgproc].

An image becomes an LLM span of `[IMAGE_START] + ([IMAGE]*w + [IMAGE_NEW_LINE])*h + [IMAGE_END]`; every span position carries `image_token_id` in `input_ids` and only `token_types` distinguishes roles, with `TEXT=-1` elsewhere[^imgproc]. Span delimiters take learned `image_start/end/newline` embeddings while `IMAGE` slots take aligner rows in reading order; image positions use `image_token_id` embeddings as placeholders before this overwrite[^model][^imgproc].

Sizing: patch-grid dimensions round original pixels up to multiples of 14, enforce `vision_min_pixels` by upscaling small images, cap aspect ratio only when configured, then shrink until LLM tokens fit `vision_max_n_token`; ultra-tall images can collapse to one column and ultra-wide to one row[^imgproc]. Non-ultra-wide images pad with gray to the target size while ultra-wide images resize directly; pixels normalize from `[0,1]` to `[-1,1]` BF16 patches[^imgproc]. Image bytes load from raw bytes, base64, Anthropic-style source, HTTP(S), local path, or data URL, with explicit errors for unsupported data-URL encodings and unresolvable records[^imgproc]. Placeholder validation reads the training-time spelling from config and only cross-checks the tokenizer id when that spelling is known[^imgproc].

## TileLang kernels

All performance-sensitive numeric kernels are TileLang JIT kernels with warp specialization and TMA lowering disabled[^kernel].

- `act_quant`: block-wise FP8 activation quantization with per-row-block scales, optional power-of-two MXFP rounding, fused quant-plus-dequant BF16 `inplace` form, and `1e-4` amax floor[^kernel].
- `fp4_quant`/`fp4_act_quant`: block-32 FP4 with E8M0 scales for indexer state or E4M3 scales for compressed KV; compressed-KV path keeps even all-zero groups nonzero with a `6*2^-9` floor, while the E8M0 path uses `6*2^-126`[^kernel].
- `fp8_gemm`: `C=A@B^T` with per-block FP8 activation and weight scales, 32/128 block support, swizzled L2-friendly schedule, and separate scale-corrected accumulator[^kernel].
- `fp4_gemm`: FP8-activation by FP4-weight GEMM with per-32 E8M0 weight scales and per-32/128 activation scales; FP4 values packed along K are cast through FP32 to FP8 before the FP8xFP8 core[^kernel].
- `sparse_attn`: index gathering plus FlashAttention-style online softmax with learnable `attn_sink` bias; rows with no valid index use finite `-1e30` instead of `-inf` so they yield zeros rather than NaN, and head counts below 16 pad for kernel efficiency then strip[^kernel].
- `hc_split_sinkhorn`: splits one flattened mix projection into sigmoid `pre`, scaled-sigmoid `post`, and Sinkhorn-normalized `comb` with epsilon guards and row/column normalization iterations[^kernel].

## Examples, self-test, and ops limits

TXT examples are blank-line-separated prompts: two Chinese factual prompts, one DeepSeek-company prompt, and one interleaved two-image carrots/corn prompt using `<image>examples/images/carrots.jpeg</image>` tags[^extxt]. Harmony JSON holds four cases: the same two-image prompt in OpenAI format, a simple Chinese prompt, a `get_weather` tool-definition plus Beijing query, and a mid-conversation Chinese-only instruction update; image URLs are repo-relative example paths[^exjson]. The README states the TXT and JSON two-image forms express the same prompt and produce identical encoded prompts and token IDs[^readme].

Self-test builds the small `ModelArgs` default model and runs prefill plus 22 decode steps, checking shapes and dense-FP8/MoE-FP4 kernel plumbing on uninitialized weights rather than numerics[^readme]. `model.py` also contains a CUDA `__main__` smoke path with `dspark_block_size=6`, targets `(3,4)`, prefill plus `forward_spec`, and per-step decode-plus-spec assertions[^model].

Operational limits stated in code and docs: standalone inference rejects cases with `context` lacking a prefilled KV cache; image prompts require `vision_n_layers>0` and placeholder/image-count agreement; prompt length must fit `max_seq_len`; multi-node runs add standard `torchrun --nnodes/--node-rank/--master-addr/--master-port` arguments[^generate][^model][^imgproc][^readme].

## Relationships

- Uses [DeepSeek-V4.1-Flash Architecture](deepseek-v41-architecture.md) — implements the CED backbone, CSA-style sparse attention, Engram, DSpark, FP4/FP8, and multimodal design in readable code.
- Uses [DeepSeek-V4.1-Flash Systems](deepseek-v41-systems.md) — minimal single-process counterpart to the disaggregated persistent-KV, bounded-replay, and fused-kernel deployment described there.
- Related to [SGLang DeepSeek-V4.1 Inference](sglang-deepseek-v41-inference.md) — production serving realization with shared KV/candidate state, Engram host layouts, bounded replay, and fusion discipline.
- Related to [Grouped-Query Attention](grouped-query-attention.md) — grouped low-rank output projection and shared/indexed KV context for the attention implementation.
- Related to [KV Cache Compression and Optimization](kv-cache-compression-optimization.md) — windowed, compressed, quantized, and shared KV-cache techniques exercised by this runtime.

## Coverage limits

- `examples/images/` payloads were not visually inspected; image-content claims follow filenames, TXT tags, and JSON URLs rather than pixel verification.
- Numerical config values are snapshots from `config.json`, not independent measurement; figure images under the tech-report path were already excluded from that companion ingest.
- Referenced `../encoding/` helpers are outside `raw/inference/` and were not compiled; prompt-encoding claims follow their call sites in `generate.py` and `image_processor.py`.

[^readme]: Minimal inference README — `../raw/inference/README.md`, reference-not-production scope, install, HF-to-TP conversion command, TXT/JSON equivalence, interactive and multi-node launch, and uninitialized-weight self-test.
[^config]: Reference inference config — `../raw/inference/config.json`, 40 plus 3 layers, 5120 width, 384 plus 1 MoE, window 128, KV/index/candidate layout, YaRN and compression Thetas, HC/Engram/DSpark/vision settings, and FP8/FP4 dtypes.
[^convert]: Checkpoint conversion — `../raw/inference/convert.py`, expert-count inference, name normalization, TP/expert/Engram sharding, FP4/FP8 expert handling, `wo_a` dequantization, tokenizer copy, shard naming, and index-completeness check.
[^generate]: Generation runtime — `../raw/inference/generate.py`, right-padded prefill/decode loop, ground-truth prompt override, image-span prefill constraint, VL single-sample path, distributed/interactive handling, TXT/JSON inputs, and fixed launch settings.
[^model]: Transformer reference — `../raw/inference/model.py`, globals and `ModelArgs` test defaults, TP linear/embedding/head behavior, YaRN RoPE, window/compressor/indexer/candidate logic, shared runtime, gating/MoE/SwiGLU clamps, Hyper-Connections, DSpark stages, image merge, Gumbel-max sampling, and CUDA smoke test.
[^kernel]: TileLang kernels — `../raw/inference/kernel.py`, disabled warp/TMA passes, FP8/FP4 quantization, FP8 and FP4 GEMMs, index-gathering sparse attention with sink and finite empty-row bound plus head padding, and Sinkhorn mHC splitting.
[^engram]: Engram hashing — `../raw/inference/engram.py`, prime bucket layout, RNG multipliers bounded against int64 overflow, compressed token map and normalization, pad/DEAD handling, cross-split cache, and incremental XOR hashing.
[^vision]: Vision backbone — `../raw/inference/vision.py`, bidirectional 2D-RoPE ViT, patch embedding, RMSNorm/SwiGLU blocks, and 3x3 pixel-unshuffle aligner to backbone width.
[^imgproc]: Image preprocessing — `../raw/inference/image_processor.py`, span layout and `TEXT=-1` typing, resize/pad/token-budget plan, multi-source byte loading, placeholder validation, and VL token expansion.
[^run]: Run wrapper — `../raw/inference/run.sh`, shard plus input validation and `torchrun` launch with `MP`/`CONFIG` overrides.
[^reqs]: Dependencies — `../raw/inference/requirements.txt`, Torch, Transformers/tokenizers/safetensors, NumPy/sympy/Pillow, pinned TileLang, and tqdm.
[^extxt]: Text examples — `../raw/inference/examples/example.txt`, Chinese factual plus company prompts and tagged two-image carrots/corn prompt.
[^exjson]: Harmony examples — `../raw/inference/examples/example_harmony.json`, matching two-image case, simple Chinese case, weather-tool case, and Chinese-only instruction-update case.

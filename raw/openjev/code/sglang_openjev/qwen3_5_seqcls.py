"""Qwen3_5ForSequenceClassification for SGLang (which ships no seq-cls head for Qwen3.5).

SGLang keys the hybrid GDN cache, the mrope setup and the Qwen-VL multimodal processor on the architecture
*name* `Qwen3_5ForConditionalGeneration`, so instead of registering a new name this module overrides that
entry (the registry loads external packages with overwrite=True) and the server is launched with
`--json-model-override-args '{"architectures": ["Qwen3_5ForConditionalGeneration"]}' --is-embedding`.
Generation is untouched; with get_embedding the last-token hidden state goes through the linear `score`
head, same pooling as transformers (last non-pad token), and the raw logits come back as the "embedding".
"""
from typing import Optional

import torch
from torch import nn

from sglang.srt.layers.pooler import Pooler, PoolingType, score_and_pool
from sglang.srt.layers.quantization.base_config import QuantizationConfig
from sglang.srt.model_executor.forward_batch_info import ForwardBatch
from sglang.srt.models import qwen3_5 as _qwen3_5
from sglang.srt.models.qwen3_vl import general_mm_embed_routine


class Qwen3_5ForConditionalGeneration(_qwen3_5.Qwen3_5ForConditionalGeneration):
    def __init__(self, config, quant_config: Optional[QuantizationConfig] = None, prefix: str = ""):
        super().__init__(config, quant_config, prefix)
        # self.config is the text config from here on; num_labels lives on the top-level one
        self.score = nn.Linear(self.config.hidden_size, config.num_labels, bias=False)
        self.pooler = Pooler(pooling_type=PoolingType.LAST, normalize=False)

    @torch.no_grad()
    def forward(self, input_ids: torch.Tensor, positions: torch.Tensor, forward_batch: ForwardBatch,
                get_embedding: bool = False, pp_proxy_tensors=None):
        if not get_embedding:
            return super().forward(input_ids, positions, forward_batch, False, pp_proxy_tensors)
        if self.is_mrope_enabled:
            positions = forward_batch.mrope_positions
        hidden_states = general_mm_embed_routine(
            input_ids=input_ids,
            forward_batch=forward_batch,
            language_model=self.model,
            multimodal_model=self,
            positions=positions,
            use_deepstack=self.use_deepstack,
            pp_proxy_tensors=pp_proxy_tensors,
        )
        return score_and_pool(self.score, self.pooler, hidden_states, forward_batch, input_ids)


EntryClass = [Qwen3_5ForConditionalGeneration]

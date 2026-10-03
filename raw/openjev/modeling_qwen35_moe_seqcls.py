"""Sequence-classification head for Qwen3.5-MoE (transformers 5.15 ships none). Same shape as
Qwen3_5ForSequenceClassification: base model + linear `score` over the last non-pad token."""
from transformers import AutoConfig, AutoModelForSequenceClassification
from transformers.modeling_layers import GenericForSequenceClassification
from transformers.models.qwen3_5_moe.modeling_qwen3_5_moe import (
    Qwen3_5MoeForConditionalGeneration,
    Qwen3_5MoePreTrainedModel,
)
from transformers.models.qwen3_5_moe.configuration_qwen3_5_moe import Qwen3_5MoeConfig


class Qwen3_5MoeForSequenceClassification(GenericForSequenceClassification, Qwen3_5MoePreTrainedModel):
    # reuse the checkpoint key mapping (model.language_model.* -> model.*) of the generative class
    _checkpoint_conversion_mapping = getattr(Qwen3_5MoeForConditionalGeneration, "_checkpoint_conversion_mapping", {})
    _tied_weights_keys = []


def register():
    AutoModelForSequenceClassification.register(Qwen3_5MoeConfig, Qwen3_5MoeForSequenceClassification, exist_ok=True)


register()

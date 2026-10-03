"""Resident Bend encoder projections and optional decision-head normalization.

The packed FP32 kernels own matrix arithmetic and coarse parallel scheduling.
PyTorch supplies embedding lookup, SDPA, activations and the selected-output head.
"""
import numpy as np
import torch
from torch import nn


class BendLayerNorm(nn.Module):
    def __init__(self, original, reducer):
        super().__init__()
        self.weight, self.bias = original.weight, original.bias
        self.eps = original.eps
        self.normalized_shape = original.normalized_shape
        self.reducer = reducer

    def forward(self, x):
        if x.device.type != 'cpu' or x.dtype != torch.float32:
            raise ValueError('Bend LayerNorm requires CPU float32; use torch backend for CUDA')
        if torch.is_grad_enabled():
            raise RuntimeError('Bend transformer kernels require torch.inference_mode()')
        width = x.shape[-1]
        values = x.detach().contiguous().numpy().reshape(-1, width)
        gamma = self.weight.detach().numpy() if self.weight is not None else None
        beta = self.bias.detach().numpy() if self.bias is not None else None
        parts = [self.reducer.layernorm(values[start:start + 1048576 // width], gamma, beta, self.eps)
                 for start in range(0, len(values), 1048576 // width)]
        result = parts[0] if len(parts) == 1 else np.concatenate(parts)
        return torch.from_numpy(result.reshape(x.shape))


class BendHeadLayer(nn.Module):
    """Explicit pre-norm block; prevents fused MHA from bypassing Bend norms."""
    def __init__(self, layer, reducer):
        super().__init__()
        if not layer.norm_first:
            raise ValueError('Julia expects pre-norm transformer layers')
        self.layer = layer
        self.norm1 = BendLayerNorm(layer.norm1, reducer)
        self.norm2 = BendLayerNorm(layer.norm2, reducer)

    def forward(self, x, src_key_padding_mask=None):
        normalized = self.norm1(x)
        attention = self.layer.self_attn(normalized, normalized, normalized,
                    key_padding_mask=src_key_padding_mask, need_weights=False)[0]
        x = x + self.layer.dropout1(attention)
        hidden = self.layer.linear2(self.layer.dropout(
            self.layer.activation(self.layer.linear1(self.norm2(x)))))
        return x + self.layer.dropout2(hidden)


def install_bend_head(model, reducer):
    if model.head is not None:
        model.head.layers = nn.ModuleList([BendHeadLayer(layer, reducer) for layer in model.head.layers])
    model.scorer[0] = BendLayerNorm(model.scorer[0], reducer)
    model.eval()


class BendLinear(nn.Module):
    """Inference-only CPU projection using resident weights and Bend arithmetic."""
    def __init__(self, original, reducer):
        super().__init__()
        from .native import BendMatrix
        self.weight, self.bias = original.weight, original.bias
        self.in_features, self.out_features = original.in_features, original.out_features
        self.matrix = BendMatrix(original.weight.detach().numpy(), reducer)
        self._weight_version = self.weight._version
        self._weight_pointer = self.weight.data_ptr()

    def _check_weight(self):
        if self.weight._version != self._weight_version or self.weight.data_ptr() != self._weight_pointer:
            raise RuntimeError('Bend resident weights changed; recreate the inference backend')

    def forward(self, x):
        if x.device.type != 'cpu' or x.dtype != torch.float32 or torch.is_grad_enabled():
            raise ValueError('Bend dense projections require CPU FP32 inference_mode')
        self._check_weight()
        result = self.matrix.tensor(x, validate=False)
        return result if self.bias is None else result + self.bias


def install_bend_encoder(model, reducer):
    """Route all encoder linear projections through Bend; attention remains SDPA."""
    count = 0
    def install(module):
        nonlocal count
        for name, child in list(module.named_children()):
            if type(child) is nn.Linear:
                setattr(module, name, BendLinear(child, reducer))
                count += 1
            else:
                install(child)
    install(model.encoder)
    model.eval()
    return count

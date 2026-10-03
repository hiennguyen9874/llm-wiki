"""Deterministic RANDOM-weight fixtures, never trained-quality evidence."""
from pathlib import Path


def make_checkpoint(directory, *, tiny=False):
    import torch
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from tokenizers.pre_tokenizers import Whitespace
    from transformers import PreTrainedTokenizerFast, ModernBertConfig, AutoModel
    from julia.model import JuliaDecisionModel
    root = Path(directory)
    torch.manual_seed(42)
    width, layers, heads = (64, 2, 2) if tiny else (384, 22, 6)
    vocabulary = {'[PAD]': 0, '[CLS]': 1, '[SEP]': 2, '[UNK]': 3, '[MASK]': 4}
    vocabulary.update({f'word{i}': i + 5 for i in range(507)})
    backend = Tokenizer(WordLevel(vocabulary, unk_token='[UNK]'))
    backend.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(tokenizer_object=backend, pad_token='[PAD]',
        cls_token='[CLS]', sep_token='[SEP]', unk_token='[UNK]', mask_token='[MASK]')
    tokenizer.save_pretrained(root / 'tokenizer')
    config = ModernBertConfig(vocab_size=512, hidden_size=width,
        intermediate_size=width * 3, num_hidden_layers=layers, num_attention_heads=heads,
        max_position_embeddings=1024, local_attention=128, global_attn_every_n_layers=3,
        pad_token_id=0, cls_token_id=1, sep_token_id=2, reference_compile=False)
    encoder = AutoModel.from_config(config, attn_implementation='sdpa')
    model = JuliaDecisionModel(encoder, head_layers=2)
    model.save_pretrained(root)
    return root


def sample_rows(count=16):
    lengths = [8, 160, 24, 96]
    return [dict(state=' '.join(f'word{(j + i) % 500}' for j in range(lengths[i % 4])),
                 question='Choose the matching option', type='choice',
                 options=[f'word{k + i}' for k in range(2 + i % 7)]) for i in range(count)]

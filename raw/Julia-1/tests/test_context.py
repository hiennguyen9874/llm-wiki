import unittest
from pathlib import Path
from julia.inference import context_length
from julia.data import sequence

class Tokenizer:
    mask_token='[MASK]';mask_token_id=4;cls_token_id=1;sep_token_id=2
    def __call__(self,text,**kwargs):return {'input_ids':[5]*len(text.split())}

class ContextTests(unittest.TestCase):
    def test_default_uses_native_checkpoint_limit(self):
        self.assertEqual(context_length(Path(__file__).resolve().parents[1],None),8192)
    def test_rejects_beyond_native_limit(self):
        with self.assertRaises(ValueError):context_length(Path(__file__).resolve().parents[1],8193)
    def test_full_budget_and_strict_overflow(self):
        row=dict(state='',question='choose',options=['a','b'])
        overhead=len(sequence(Tokenizer(),row,strict=True)['ids'])
        row['state']=' '.join(['x']*(8192-overhead))
        self.assertEqual(len(sequence(Tokenizer(),row,strict=True)['ids']),8192)
        row['state']+=' x'
        with self.assertRaises(ValueError):sequence(Tokenizer(),row,strict=True)

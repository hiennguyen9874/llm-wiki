"""Small CPU checks for shared-prefix inference; no checkpoint download needed."""
import unittest
from unittest.mock import patch

import numpy as np
import torch
from transformers import (Qwen3_5Config, Qwen3_5ForSequenceClassification,
                          Qwen3_5TextConfig, Qwen3_5VisionConfig)

from modeling_openjev import OpenJevCrossEncoder


class CharacterTokenizer:
    pad_token_id = 0

    def __call__(self, texts, truncation=True, max_length=4096, padding=False, return_tensors=None):
        if isinstance(texts, str):
            return {"input_ids": [ord(c) + 1 for c in texts][:max_length]}
        rows = [[ord(c) + 1 for c in text][:max_length] for text in texts]
        width = max(map(len, rows))
        ids = [row + [0] * (width - len(row)) for row in rows]
        mask = [[1] * len(row) + [0] * (width - len(row)) for row in rows]
        return {"input_ids": torch.tensor(ids), "attention_mask": torch.tensor(mask)}


class SharedPrefixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.manual_seed(7)
        config = Qwen3_5TextConfig(
            vocab_size=256, hidden_size=32, intermediate_size=64,
            num_hidden_layers=4, num_attention_heads=4, num_key_value_heads=2,
            head_dim=8, linear_num_key_heads=2, linear_num_value_heads=4,
            linear_key_head_dim=8, linear_value_head_dim=8,
            layer_types=["linear_attention", "full_attention"] * 2,
            rope_parameters={"rope_type": "default", "rope_theta": 10000,
                             "partial_rotary_factor": 0.25, "mrope_section": [1, 0, 0]},
            pad_token_id=0, num_labels=3, use_cache=False,
        )
        vision = Qwen3_5VisionConfig(depth=1, hidden_size=32, intermediate_size=64,
                                    num_heads=4, out_hidden_size=32)
        model = Qwen3_5ForSequenceClassification(
            Qwen3_5Config(text_config=config, vision_config=vision, num_labels=3,
                           pad_token_id=0)).eval()
        cls.jev = OpenJevCrossEncoder.__new__(OpenJevCrossEncoder)
        cls.jev.model = model
        cls.jev.backbone = model.model
        cls.jev.tok = CharacterTokenizer()
        cls.jev.template = "Premise: {premise}\nHypothesis: {hypothesis}"
        cls.jev.device = "cpu"
        cls.jev.bs = 32
        cls.jev.max_len = 128

    def test_shared_matches_independent_and_isolates_branches(self):
        premise = "A cat sleeps."
        hypotheses = ["A cat rests.", "The dog runs.", "A cat."]
        expected = self.jev.latents([(premise, h) for h in hypotheses])
        actual = self.jev.latents_hypotheses(premise, hypotheses)
        np.testing.assert_allclose(actual, expected, atol=2e-4, rtol=2e-4)
        expected_probs = self.jev.predict([(premise, h) for h in hypotheses])
        actual_probs = self.jev.predict_hypotheses(premise, hypotheses)
        np.testing.assert_allclose(actual_probs, expected_probs, atol=2e-4, rtol=2e-4)

        changed = hypotheses.copy()
        changed[1] = "Birds fly around today."
        other = self.jev.latents_hypotheses(premise, changed)
        np.testing.assert_allclose(other[[0, 2]], actual[[0, 2]], atol=2e-4, rtol=2e-4)

    def test_small_option_sets_use_pairwise_batch(self):
        for hypotheses in (["B"], ["B", "C"]):
            with self.subTest(count=len(hypotheses)):
                with patch.object(self.jev, "_pooled", wraps=self.jev._pooled) as pooled:
                    actual = self.jev.predict_hypotheses("A", hypotheses)
                    self.assertEqual(actual.shape, (len(hypotheses), 3))
                    pooled.assert_called_once()

    def test_empty(self):
        with self.assertRaises(ValueError):
            self.jev.predict_hypotheses("A", [])


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import torch

from julia.data import Collator, sequence
from julia.inference import TransformerEngine as Engine
from julia.router.engine import FastEngine
from julia.router.native import BendReducer
from synthetic import make_checkpoint, sample_rows


class NativeMathTests(unittest.TestCase):
    def test_transformer_math(self):
        reducer = BendReducer()
        rng = np.random.default_rng(42)
        for width in [1, 7, 64, 384]:
            x = rng.normal(size=(3, width)).astype('float32')
            gamma = rng.normal(size=width).astype('float32')
            beta = rng.normal(size=width).astype('float32')
            expected = torch.nn.functional.layer_norm(torch.from_numpy(x), (width,),
                        torch.from_numpy(gamma), torch.from_numpy(beta)).numpy()
            np.testing.assert_allclose(reducer.layernorm(x, gamma, beta), expected, atol=2e-6, rtol=2e-5)
            for row in x:
                index, probs = reducer.softmax(row)
                self.assertEqual(index, int(row.argmax()))
                np.testing.assert_allclose(probs, torch.from_numpy(row).softmax(-1).numpy(), atol=2e-7)
        _, probabilities = reducer.softmax(np.array([10000, 10001, -10000], np.float32))
        self.assertAlmostEqual(float(probabilities.sum()), 1.0)

    def test_resident_dense_tiles_reuse_and_partial_edges(self):
        from julia.router.native import BendMatrix
        rng = np.random.default_rng(52)
        for inputs, outputs, rows in [(1, 1, 1), (7, 5, 9), (64, 17, 7), (33, 65, 19), (384, 1152, 5)]:
            weights = rng.normal(size=(outputs, inputs)).astype('float32')
            values = rng.normal(size=(rows, inputs)).astype('float32')
            matrix = BendMatrix(weights)
            reference = values @ weights.T
            first = matrix(values)
            np.testing.assert_allclose(first, reference, atol=1e-4, rtol=1e-4)
            for _ in range(8):
                np.testing.assert_array_equal(matrix(values), first)
            with self.assertRaises(ValueError): matrix(np.ones((2, inputs + 1), np.float32))
            with self.assertRaises(ValueError): matrix(np.full((1, inputs), np.nan, np.float32))
            matrix.close()
            matrix.close()
            with self.assertRaises(RuntimeError): matrix(values)
        with self.assertRaises(ValueError): BendMatrix([[float('nan')]])

    def test_tensor_chunks_and_opt_in_native_profile(self):
        from julia.router.native import BendMatrix
        reducer = BendReducer()
        weights = np.random.default_rng(8).normal(size=(257, 3)).astype('float32')
        matrix = BendMatrix(weights, reducer)
        # Noncontiguous input and > 1M output cells require two native chunks.
        values = torch.arange(4090 * 6, dtype=torch.float32).reshape(4090, 6)[:, ::2] / 1000
        try:
            reducer.profile(enabled=True, reset=True)
            actual = matrix.tensor(values)
            measured = reducer.profile(enabled=False)
            self.assertEqual(measured['calls'], 2)
            self.assertTrue(all(measured[k] >= 0 for k in ('pack_ms', 'execute_ms', 'unpack_ms')))
            torch.testing.assert_close(actual, values @ torch.from_numpy(weights).T, rtol=1e-5, atol=1e-5)
            matrix.tensor(values[:1])
            self.assertEqual(reducer.profile(), measured)
            with self.assertRaises(ValueError):
                matrix.tensor(torch.full((1, 3), float('nan')))
        finally:
            reducer.profile(enabled=False, reset=True)
            matrix.close()

    def test_layernorm_parallel_callers_and_large_rows(self):
        import concurrent.futures
        reducer = BendReducer()
        rng = np.random.default_rng(19)
        values = [rng.normal(size=(rows, 384)).astype('float32') for rows in (1, 7, 32, 128)]
        references = [torch.nn.functional.layer_norm(torch.from_numpy(x), (384,)).numpy() for x in values]
        with concurrent.futures.ThreadPoolExecutor(4) as pool:
            actual = list(pool.map(reducer.layernorm, values * 8))
        for i, result in enumerate(actual):
            np.testing.assert_allclose(result, references[i % len(values)], atol=3e-6, rtol=2e-5)

    def test_packed_matrix_concurrent_owners(self):
        from concurrent.futures import ThreadPoolExecutor
        from julia.router.native import BendMatrix
        rng = np.random.default_rng(2026)
        weights = [rng.normal(size=(n, 33)).astype('float32') for n in (5, 17, 128)]
        matrices = [BendMatrix(w) for w in weights]
        values = rng.normal(size=(19, 33)).astype('float32')
        try:
            with ThreadPoolExecutor(6) as pool:
                results = list(pool.map(lambda i: matrices[i % 3](values), range(96)))
            for i, actual in enumerate(results):
                np.testing.assert_allclose(actual, values @ weights[i % 3].T, atol=2e-5, rtol=2e-5)
        finally:
            for matrix in matrices:
                matrix.close()

    def test_rejected_native_math(self):
        reducer = BendReducer()
        for x in [[], [float('nan')], [float('inf')]]:
            with self.assertRaises(ValueError):
                reducer.softmax(x)
        for kwargs in [dict(epsilon=0), dict(gamma=[1]), dict(beta=[0]), dict(epsilon=float('nan'))]:
            with self.assertRaises(ValueError):
                reducer.layernorm([[1, 2, 3]], **kwargs)


class ProbabilityDisplayTests(unittest.TestCase):
    def test_rounds_decisive_answer_to_certain(self):
        from julia.probabilities import display_probabilities

        self.assertEqual(display_probabilities([0.955, 0.044, 0.001]), [1.0, 0.0, 0.0])
        self.assertNotEqual(display_probabilities([0.951, 0.049]), [1.0, 0.0])

    def test_redistributes_sub_one_percent_values(self):
        from julia.probabilities import display_probabilities

        result = display_probabilities([0.6, 0.395, 0.005])
        self.assertEqual(result[2], 0.0)
        self.assertAlmostEqual(sum(result), 1.0)
        self.assertAlmostEqual(result[0] / result[1], 0.6 / 0.395)


class InputValidationTests(unittest.TestCase):
    def test_public_loader_rejects_invalid_backend(self):
        from julia import load_model
        from julia.inference import Engine

        self.assertIs(load_model, Engine)
        with self.assertRaisesRegex(ValueError, 'backend'):
            load_model('unused', backend='unknown')

    def test_rejects_malformed_requests(self):
        from julia.data import validate_row

        valid = {'state': 'context', 'question': 'Choose', 'options': ['A', 'B']}
        for row in (None, [], {**valid, 'teacher_logits': 'bad'},
                    {**valid, 'teacher_logits': [0.0, float('nan')]},
                    {**valid, 'teacher_logits': [True, 0.0]}):
            with self.subTest(row=row), self.assertRaises(ValueError):
                validate_row(row, 1)


class InferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)
        cls.temp = tempfile.TemporaryDirectory()
        cls.path = make_checkpoint(cls.temp.name, tiny=True)
        cls.baseline = Engine(cls.path, device='cpu')
        with patch('julia.router.native.BendReducer', side_effect=AssertionError('Default CPU must not load Bend')):
            cls.fast = FastEngine(cls.path, device='cpu', batch_size=2)
        cls.rows = sample_rows(5)
        cls.rows[0]['state'] = {'text': 'Olá 世界 [MASK]', 'items': [1, 2]}

    @classmethod
    def tearDownClass(cls):
        del cls.baseline, cls.fast
        cls.temp.cleanup()

    def test_modernbert_decision_encoder_deduplicates_rope(self):
        from transformers import ModernBertConfig, ModernBertModel
        from julia.model import JuliaDecisionModel
        from julia.router.encoder import specialize_decision_encoder
        config = ModernBertConfig(vocab_size=64, pad_token_id=0, bos_token_id=1, eos_token_id=2, hidden_size=32, intermediate_size=64,
            num_hidden_layers=4, num_attention_heads=4, max_position_embeddings=128,
            local_attention=16, global_attn_every_n_layers=3, attention_dropout=0.,
            embedding_dropout=0., mlp_dropout=0.)
        config._attn_implementation = 'sdpa'
        model = JuliaDecisionModel(ModernBertModel(config), head_layers=0).eval()
        ids = torch.arange(24).reshape(2,12) % 64
        mask = torch.ones_like(ids); mask[1,8:] = 0
        calls=[]
        hook=model.encoder.rotary_emb.register_forward_hook(lambda *args: calls.append(1))
        with torch.inference_mode():
            expected=model.encoder(input_ids=ids,attention_mask=mask).last_hidden_state
            self.assertEqual(len(calls), 4)
            calls.clear()
            self.assertTrue(specialize_decision_encoder(model))
            actual=model.encoder(input_ids=ids,attention_mask=mask).last_hidden_state
            self.assertEqual(len(calls), 2)
            torch.testing.assert_close(actual, expected, rtol=0, atol=0)
        hook.remove()

    def test_default_backend_and_padding_budget(self):
        self.assertEqual(self.fast.transformer_backend, 'torch')
        self.assertIsNone(self.fast.bend)
        self.assertFalse(hasattr(self.fast, 'bend_projection_count'))
        rows = [dict(self.rows[0], state='short'), dict(self.rows[1], state='long context ' * 100),
                dict(self.rows[2], state='another short state')]
        encoded = self.fast._encode(rows)
        groups = list(self.fast._batch_indices(encoded))
        self.assertEqual(sorted(i for group in groups for i in group), list(range(3)))
        for group in groups:
            lengths = [len(encoded[i]['ids']) for i in group]
            self.assertLessEqual(max(lengths) * len(group), self.fast.padding_ratio * sum(lengths))
        actual = self.fast.predict(rows)
        expected = self.baseline.predict(rows)
        for a, b in zip(actual, expected):
            np.testing.assert_allclose(a['probabilities'], b['probabilities'], atol=2e-6)

    def test_lfs_pointer_error(self):
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / 'model.safetensors').write_text('version https://git-lfs.github.com/spec/v1\n')
            with self.assertRaisesRegex(ValueError, 'Git LFS pointers'):
                FastEngine(directory)

    def test_serialization_and_pack(self):
        encoded = self.fast._encode(self.rows)
        self.assertEqual(encoded, [sequence(self.baseline.tokenizer, row) for row in self.rows])
        packed = self.fast._pack(encoded)
        reference = Collator(self.baseline.tokenizer, 1024, 256)(self.rows)
        for name in packed:
            self.assertTrue(torch.equal(packed[name], reference[name]), name)
        self.assertEqual(self.fast.predict([]), [])
        self.assertEqual(self.fast.logits([]), [])

    def test_inference_collation_omits_training_tensors(self):
        rows = [dict(row, target=0, teacher_logits=[0.] * len(row['options']))
                for row in self.rows]
        collate = self.baseline.collate
        training = collate(rows)
        inference = collate(rows, include_targets=False)
        self.assertIn('labels', training)
        self.assertIn('teacher_logits', training)
        self.assertEqual(set(training) - set(inference), {'labels', 'teacher_logits'})
        for name, value in inference.items():
            self.assertTrue(torch.equal(value, training[name]), name)
        self.assertEqual(self.baseline.predict(rows), self.baseline.predict(self.rows))

    def test_nonfinite_real_scores_are_rejected(self):
        original = self.fast.forward
        try:
            for invalid in (float('nan'), float('inf'), -float('inf')):
                def forward(**batch):
                    result = torch.zeros_like(batch['marker_pos'], dtype=torch.float32)
                    result[0, 0] = invalid
                    return result
                self.fast.forward = forward
                with self.assertRaises(FloatingPointError):
                    self.fast.predict(self.rows)
        finally:
            self.fast.forward = original

    def test_memory_mapped_checkpoint_dtype_and_logits(self):
        from julia.model import JuliaDecisionModel
        for dtype in (torch.float32, torch.bfloat16):
            with tempfile.TemporaryDirectory() as directory:
                model = JuliaDecisionModel.from_pretrained(self.path).to(dtype=dtype)
                model.save_pretrained(directory)
                loaded = JuliaDecisionModel.from_pretrained(directory, memory_map=True)
                copied = JuliaDecisionModel.from_pretrained(directory, memory_map=False)
                for name, value in loaded.state_dict().items():
                    self.assertEqual(value.dtype, copied.state_dict()[name].dtype)
                    torch.testing.assert_close(value, copied.state_dict()[name], rtol=0, atol=0)
                if dtype == torch.float32:
                    batch = self.baseline.collate(self.rows)
                    with torch.inference_mode():
                        torch.testing.assert_close(loaded.eval()(**batch), copied.eval()(**batch), rtol=0, atol=0)

    def test_selected_head_scores_actions_and_training(self):
        model = self.baseline.model
        batch = self.baseline.collate(self.rows)
        batch['qtype'] = torch.arange(len(self.rows)) % 3
        with torch.inference_mode():
            model.marker_only_head = False
            expected = model(**batch, return_actions=True)
            model.marker_only_head = True
            actual = model(**batch, return_actions=True)
        for a, b in zip(expected, actual):
            torch.testing.assert_close(a, b, atol=2e-6, rtol=2e-5)
        # Training must retain the original full-sequence/dropout path.
        model.train()
        torch.manual_seed(123)
        model.marker_only_head = False
        expected = model(**batch)
        torch.manual_seed(123)
        model.marker_only_head = True
        actual = model(**batch)
        torch.testing.assert_close(expected, actual, atol=0, rtol=0)
        actual.sum().backward()
        self.assertTrue(torch.isfinite(model.scorer[-1].weight.grad).all())
        model.zero_grad(set_to_none=True)
        model.eval()
        model.marker_only_head = False

    def test_strict_encoding_reuses_audit_and_rejects_loss(self):
        engine = FastEngine(self.path, device='cpu', strict_encoding=True)
        row = dict(self.rows[1], state='word1 word2')
        audit = engine.encoding_info([row])[0]
        self.assertFalse(audit['stateTruncated'])
        encoded = next(iter(engine._encoded.values()))
        engine.predict([row])
        self.assertIs(next(iter(engine._encoded.values())), encoded)
        for bad in [dict(row, state='[MASK]'),
                    dict(row, state={'value': '[MASK]'}),
                    dict(row, options=['word1 ' * 49, 'word2']),
                    dict(row, state='word1 ' * 2000)]:
            with self.assertRaises(ValueError):
                engine.predict([bad])
        # Changes in the encoding budget must not reuse stale cached IDs.
        engine.max_length = 32
        with self.assertRaises(ValueError):
            engine.predict([dict(row, state='word1 ' * 100)])
        engine.head_length = 16
        with self.assertRaises(ValueError):
            engine.predict([dict(row, question='word1 ' * 40)])

    def test_inference_parity_and_order(self):
        reference = self.baseline.predict(self.rows)
        actual = self.fast.predict(self.rows)
        self.assertEqual([x['index'] for x in reference], [x['index'] for x in actual])
        for a, b in zip(reference, actual):
            np.testing.assert_allclose(a['probabilities'], b['probabilities'], atol=2e-6)
        self.assertEqual(self.fast.predict(self.rows, probabilities=False),
                         [dict(index=x['index']) for x in actual])
        self.assertTrue(self.fast._encoded)
        self.fast.clear_cache()
        self.assertFalse(self.fast._encoded)
        self.assertFalse(self.fast._tokens.cache)

    def test_bend_transformer_parity(self):
        bend = FastEngine(self.path, device='cpu', batch_size=2,
                          transformer_backend='bend', bend_postprocess=True)
        reference = self.baseline.predict(self.rows)
        actual = bend.predict(self.rows)
        # Different reduction orders can break an exact FP32 tie. Require the
        # selected reference probability to be within tolerance of its maximum.
        for a, b in zip(reference, actual):
            p = a['probabilities']
            self.assertLessEqual(max(p) - p[b['index']], 2e-6)
        for a, b in zip(reference, actual):
            np.testing.assert_allclose(a['probabilities'], b['probabilities'], atol=2e-6)
        self.assertEqual(bend.predict(self.rows, probabilities=False),
                         [dict(index=x['index']) for x in actual])

    def test_bend_dense_encoder_parity(self):
        dense = FastEngine(self.path, device='cpu', batch_size=2,
                           transformer_backend='bend-dense')
        self.assertGreater(dense.bend_projection_count, 0)
        expected = self.baseline.predict(self.rows)
        actual = dense.predict(self.rows)
        for a, b in zip(expected, actual):
            np.testing.assert_allclose(a['probabilities'], b['probabilities'], atol=2e-6)
            self.assertLessEqual(max(a['probabilities']) - a['probabilities'][b['index']], 2e-6)
        from julia.router.transformer import BendLinear
        layer = next(m for m in dense.model.modules() if isinstance(m, BendLinear))
        with torch.no_grad():
            layer.weight.add_(1)
        with self.assertRaisesRegex(RuntimeError, 'resident weights changed'):
            dense.predict(self.rows)

    @unittest.skipUnless(torch.cuda.is_available(), 'CUDA hardware unavailable')
    def test_cuda(self):
        baseline = Engine(self.path, device='cuda')
        fast = FastEngine(self.path, device='cuda', batch_size=2)
        reference, actual = baseline.predict(self.rows), fast.predict(self.rows)
        self.assertEqual([x['index'] for x in reference], [x['index'] for x in actual])
        for a, b in zip(reference, actual):
            np.testing.assert_allclose(a['probabilities'], b['probabilities'], atol=5e-3)


if __name__ == '__main__':
    unittest.main()

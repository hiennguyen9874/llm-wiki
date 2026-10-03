import concurrent.futures
import math
import os
import random
import unittest

from julia.router import BendReducer, Router

LIB = os.environ.get('JULIA_ROUTER_LIBRARY', str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'build/libjulia_router.so'))


class Engine:
    def __init__(self):
        self.batches = []

    def logits(self, rows):
        self.batches.append(rows)
        return [[float(x) for x in row['options']] for row in rows]


def request(n):
    return dict(state='Olá, 世界', question='Choose the largest number',
                options=[str(i) for i in range(n)])


class Tests(unittest.TestCase):
    def test_native_reference_and_reuse(self):
        reducer = BendReducer(LIB)
        rng = random.Random(10)
        for n in [1, 2, 3, 20, 77, 1000]:
            for _ in range(20):
                values = [rng.randrange(-100, 100) for _ in range(n)]
                self.assertEqual(reducer.argmax(values), max(range(n), key=values.__getitem__))
        self.assertEqual(reducer.argmax([3, 3, -1]), 0)

    def test_native_threads(self):
        reducer = BendReducer(LIB)
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            self.assertEqual(list(pool.map(lambda _: reducer.argmax([1, 9, 2]), range(1000))), [1]*1000)

    def test_invalid(self):
        for scores in [[], [math.nan], [math.inf], [1e100]]:
            with self.assertRaises(ValueError):
                BendReducer(LIB).argmax(scores)
        r = Router(Engine(), library=LIB)
        for row in [request(1), dict(request(30), type='score'), dict(request(3), type='noul')]:
            with self.assertRaises(ValueError):
                r.route(row)

    def test_direct_and_hierarchical(self):
        engine = Engine()
        router = Router(engine, library=LIB, batch_size=3)
        results = router.route_many([request(n) for n in [2, 20, 21, 77, 4096]])
        self.assertEqual([r.index for r in results], [1, 19, 20, 76, 4095])
        for result in results:
            self.assertAlmostEqual(sum(result.probabilities), 1)
            self.assertIn(result.index, result.candidates)
        self.assertEqual(results[0].probability_scope, 'all_options')
        self.assertEqual(results[-1].probability_scope, 'final_candidates')
        self.assertTrue(all(len(batch) <= 3 for batch in engine.batches))
        self.assertTrue(all(2 <= len(row['options']) <= 20 for batch in engine.batches for row in batch))
        self.assertEqual(router.route_many([]), [])

    def test_confident_group_shortcut(self):
        self.assertTrue(Router._confident_winner([0.0, 4.0, -3.0], 1))
        self.assertFalse(Router._confident_winner([0.0, 3.0, -3.0], 1))

        class DecisiveEngine(Engine):
            def logits(self, rows):
                self.batches.append(rows)
                return [[10.0 * float(x) for x in row['options']] for row in rows]

        engine = DecisiveEngine()
        router = Router(engine, library=LIB)
        result = router.route(request(2001))
        self.assertEqual(result.index, 2000)
        self.assertEqual(result.rounds, 3)
        self.assertEqual(result.model_rows, 106)

        baseline = Router(DecisiveEngine(), library=LIB)
        baseline._confident_winner = lambda scores, best: False
        original = baseline.route(request(2001))
        self.assertEqual(original.index, result.index)
        self.assertLess(result.rounds, original.rounds)
        self.assertLess(result.model_rows, original.model_rows)

    def test_cache_and_dedup(self):
        engine = Engine()
        router = Router(engine, library=LIB, cache_size=1)
        results = router.route_many([request(5), request(5)])
        self.assertEqual(results[0].model_rows, 1)
        self.assertEqual(results[0].cache_hits, 1)
        self.assertEqual(router.route(request(5)).model_rows, 0)
        router.clear_cache()
        self.assertEqual(router.route(request(5)).model_rows, 1)
        router.route(request(6))
        self.assertEqual(router.route(request(5)).model_rows, 1)

    def test_engine_failure(self):
        class Bad:
            def logits(self, rows):
                return [[0]] * len(rows)
        with self.assertRaises(ValueError):
            Router(Bad(), library=LIB).route(request(4))


if __name__ == '__main__':
    unittest.main()

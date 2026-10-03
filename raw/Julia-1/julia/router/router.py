"""Bounded Julia inference with a Bend candidate-tree reducer."""
from collections import OrderedDict
from dataclasses import dataclass
import json
import math
import threading

from ..probabilities import display_probabilities
from .native import BendReducer


@dataclass(frozen=True)
class RouteResult:
    index: int
    candidates: tuple[int, ...]
    probabilities: tuple[float, ...]
    rounds: int
    model_rows: int
    cache_hits: int
    hierarchical: bool
    # Probabilities are conditional on candidates, never global for a tournament.
    probability_scope: str


class Router:
    """Wrap an Engine-compatible logits(rows) implementation.

    Up to width options: one unchanged model request. Larger choice requests:
    retain survivors per group and rerank until one final group remains.
    This increases supported option count, not the model's trained capacity.
    """
    def __init__(self, engine, *, library=None, width=20, survivors=2,
                 batch_size=16, cache_size=0, max_options=4096):
        for name, value in [('width', width), ('survivors', survivors),
                            ('batch_size', batch_size), ('cache_size', cache_size),
                            ('max_options', max_options)]:
            if type(value) is not int:
                raise ValueError(f'{name} must be an integer')
        if not 2 <= width <= 20 or not 1 <= survivors < width:
            raise ValueError('Require 2 <= width <= 20 and 1 <= survivors < width')
        if batch_size < 1 or cache_size < 0 or max_options < width:
            raise ValueError('Invalid batch/cache/capacity limit')
        self.engine, self.reducer = engine, BendReducer(library)
        self.width, self.survivors = width, survivors
        self.batch_size, self.cache_size, self.max_options = batch_size, cache_size, max_options
        self._cache = OrderedDict()
        self._lock = threading.RLock()

    def clear_cache(self):
        """Call after modifying model weights or inference settings."""
        with self._lock:
            self._cache.clear()

    def _validate(self, row):
        if not isinstance(row, dict):
            raise ValueError('A request must be a dictionary')
        if not isinstance(row.get('state'), (str, dict, list)) or not isinstance(row.get('question'), str):
            raise ValueError('state must be text/JSON and question must be text')
        options = row.get('options')
        if not isinstance(options, list) or not 2 <= len(options) <= self.max_options:
            raise ValueError(f'Expected 2–{self.max_options} options')
        if not all(isinstance(x, str) and x for x in options):
            raise ValueError('Options must be nonempty strings')
        kind = row.get('type', 'choice')
        if kind not in ('choice', 'score', 'noul'):
            raise ValueError('Unknown decision type')
        if kind == 'noul' and len(options) != 2:
            raise ValueError('noul requires [false, true]')
        if kind != 'choice' and len(options) > self.width:
            raise ValueError('Hierarchical routing supports choice decisions only')
        clean = dict(state=row['state'], question=row['question'], options=options, type=kind)
        # Snapshot mutable state; preserve dict order used by Julia serialization.
        return json.loads(json.dumps(clean, ensure_ascii=False, allow_nan=False))

    def _score(self, jobs):
        values = [None] * len(jobs)
        missing = OrderedDict()
        hits = 0
        for i, row in enumerate(jobs):
            key = json.dumps(row, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
            if key in self._cache:
                values[i] = self._cache[key]
                self._cache.move_to_end(key)
                hits += 1
            elif key in missing:
                missing[key][1].append(i)
                hits += 1
            else:
                missing[key] = (row, [i])
        pending = list(missing.items())
        for offset in range(0, len(pending), self.batch_size):
            chunk = pending[offset:offset + self.batch_size]
            output = list(self.engine.logits([entry[1][0] for entry in chunk]))
            if len(output) != len(chunk):
                raise ValueError('Engine returned the wrong number of rows')
            for (key, (row, indices)), scores in zip(chunk, output):
                scores = tuple(float(x) for x in scores)
                if len(scores) != len(row['options']) or not all(math.isfinite(x) for x in scores):
                    raise ValueError('Engine logits must be finite and match option count')
                for i in indices:
                    values[i] = scores
                if self.cache_size:
                    self._cache[key] = scores
                    self._cache.move_to_end(key)
                    while len(self._cache) > self.cache_size:
                        self._cache.popitem(last=False)
        return values, len(pending), hits

    @staticmethod
    def _confident_winner(scores, best):
        """Keep one candidate when its local softmax dominates the group."""
        runner_up = max(score for i, score in enumerate(scores) if i != best)
        if runner_up - scores[best] >= math.log(0.045 / 0.95):
            return False
        total = sum(math.exp(score - scores[best]) for score in scores)
        return 1 / total > 0.95 and math.exp(runner_up - scores[best]) / total < 0.045

    def route(self, row):
        return self.route_many([row])[0]

    def route_many(self, rows):
        """Batch independent groups across requests; preserve request/option order.

        Calls on one Router serialize because most model engines and the LRU are
        mutable. The C bridge also serializes access to Bend's global runtime.
        """
        with self._lock:
            requests = [self._validate(row) for row in rows]
            candidates = [list(range(len(row['options']))) for row in requests]
            results = [None] * len(requests)
            rounds = [0] * len(requests)
            model_rows = hits = 0
            while any(result is None for result in results):
                jobs, layout = [], []
                for i, row in enumerate(requests):
                    if results[i] is not None:
                        continue
                    rounds[i] += 1
                    current = candidates[i]
                    final = len(current) <= self.width
                    groups = [current[j:j + self.width] for j in range(0, len(current), self.width)]
                    candidates[i] = []
                    for group in groups:
                        if len(group) == 1:
                            candidates[i].extend(group)
                            continue
                        jobs.append(dict(row, options=[row['options'][k] for k in group]))
                        layout.append((i, group, final))
                scored, used, cached = self._score(jobs)
                model_rows += used
                hits += cached
                for (i, group, final), scores in zip(layout, scored):
                    best = self.reducer.argmax(scores)
                    if final:
                        maximum = max(scores)
                        weights = [math.exp(x - maximum) for x in scores]
                        total = sum(weights)
                        results[i] = RouteResult(group[best], tuple(group),
                            tuple(display_probabilities([x / total for x in weights])), rounds[i], 0, 0,
                            len(requests[i]['options']) > self.width,
                            'final_candidates' if len(requests[i]['options']) > self.width else 'all_options')
                    elif self._confident_winner(scores, best):
                        candidates[i].append(group[best])
                    else:
                        remaining = list(range(len(group)))
                        chosen = []
                        for _ in range(min(self.survivors, len(group))):
                            position = self.reducer.argmax([scores[k] for k in remaining])
                            chosen.append(group[remaining.pop(position)])
                        candidates[i].extend(sorted(chosen))
            # These counters are shared batch totals, not per-request attribution.
            from dataclasses import replace
            return [replace(result, model_rows=model_rows, cache_hits=hits) for result in results]

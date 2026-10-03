"""Reproduce Julia-1 typed decisions; optionally ablate Boolean descriptions.
Requires torch, transformers 5.0.x, safetensors, numpy and pyarrow.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import sys
import time
import urllib.request
import shutil

REVISION = 'c76749ec58bd8c3d2ea706b31c333a9059c38f90'
DATA_SHA256 = '4f294f218ea1da27f3efef936359389c62ea4d3973a41457732990f1d31b647c'
WEIGHTS_SHA256 = 'df853bf7fe424420011f3d0c47a05d7341aa9eefa7fb9f203ea4aada4ad95b72'

def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--checkpoint', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--dataset', type=Path, help='Existing pinned Parquet; otherwise download and verify it')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--literal-noul-ablation', action='store_true')
    args = ap.parse_args()
    checkpoint = args.checkpoint.resolve()
    if digest(checkpoint / 'model.safetensors') != WEIGHTS_SHA256:
        raise ValueError('Weights do not match accuracy-20260924.json')
    args.output.mkdir(parents=True, exist_ok=False)
    if args.dataset is None:
        args.dataset = args.output / 'test-00000-of-00001.parquet'
        url = (f'https://huggingface.co/datasets/LocalLLaMA/typed-decisions/resolve/{REVISION}'
               '/all/test-00000-of-00001.parquet')
        temporary = args.dataset.with_suffix('.partial')
        with urllib.request.urlopen(url, timeout=180) as source, temporary.open('wb') as target:
            shutil.copyfileobj(source, target)
        temporary.replace(args.dataset)
    if digest(args.dataset) != DATA_SHA256:
        raise ValueError('Dataset does not match the pinned published evaluation')
    sys.path.insert(0, str(checkpoint))
    import pyarrow.parquet as pq
    import torch
    import transformers
    from julia.router.engine import FastEngine
    torch.set_num_threads(args.threads)
    cases = pq.read_table(args.dataset).to_pylist()
    rows, metadata = [], []
    for case in cases:
        state = json.loads(case['state'])
        gold = json.loads(case['gold'])
        for question_id, question in json.loads(case['questions']).items():
            kind = question['type']
            criteria = question.get('criteria')
            if criteria is None and kind == 'noul':
                criteria = {'false': 'false', 'true': 'true'}
            if isinstance(criteria, list):
                criteria = {str(i): value for i, value in enumerate(criteria)}
            if not isinstance(criteria, dict):
                raise ValueError('Missing option descriptions')
            keys = ['false', 'true'] if kind == 'noul' else list(criteria)
            rows.append(dict(state=state, question=question['instructions'],
                             type=kind, options=[criteria[key] for key in keys]))
            metadata.append(dict(id=case['id']+':'+question_id, type=kind,
                                 keys=keys, gold=str(gold[question_id]['label'])))
    counts = collections.Counter(row['type'] for row in rows)
    assert len(cases) == 400 and counts == {'choice': 600, 'score': 800, 'noul': 600}, counts
    engine = FastEngine(checkpoint, device='cpu', transformer_backend='torch',
                        strict_encoding=True, max_length=1024, head_length=512,
                        batch_size=16, marker_only_head=False)
    result = dict(weights_sha256=WEIGHTS_SHA256, dataset_revision=REVISION,
                  dataset_sha256=DATA_SHA256, torch=torch.__version__,
                  transformers=transformers.__version__, device='cpu',
                  threads=args.threads, marker_only_head=False,
                  encoding=dict(max_length=1024, head_length=512, strict=True),
                  runtime_sha256={str(p.relative_to(checkpoint)): digest(p)
                                  for p in sorted((checkpoint/'julia').rglob('*.py'))})
    def evaluate(name, input_rows, labels):
        started = time.monotonic()
        stats = collections.defaultdict(lambda: dict(count=0, correct=0))
        with (args.output / (name+'-predictions.jsonl')).open('w') as stream:
            # One example per forward matches the original benchmark protocol.
            for index, (row, label) in enumerate(zip(input_rows, labels), 1):
                answer = engine.predict([row])[0]
                prediction = label['keys'][answer['index']]
                correct = prediction == label['gold']
                stats[label['type']]['count'] += 1
                stats[label['type']]['correct'] += int(correct)
                stream.write(json.dumps(dict(**label, prediction=prediction, correct=correct,
                                             options=row['options'], probabilities=answer['probabilities']))+'\n')
                if index % 200 == 0:
                    print(json.dumps(dict(mode=name, done=index, total=len(input_rows))), flush=True)
        for item in stats.values():
            item['accuracy'] = item['correct']/item['count']
        summary = dict(by_type=dict(stats), elapsed_seconds=time.monotonic()-started)
        print(json.dumps(dict(mode=name, **summary)), flush=True)
        return summary
    result['original_criteria'] = evaluate('original-criteria', rows, metadata)
    if args.literal_noul_ablation:
        selected = [(dict(row, options=['false', 'true']), label)
                    for row, label in zip(rows, metadata) if row['type']=='noul']
        result['literal_noul_ablation'] = evaluate('literal-noul',
                                                 [x[0] for x in selected], [x[1] for x in selected])
    (args.output/'results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)

if __name__ == '__main__':
    main()

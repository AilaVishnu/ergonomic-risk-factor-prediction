"""Predict the 6 ergonomic risk levels for a rider."""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

ROOT    = Path(__file__).resolve().parents[1]
MODELS  = ROOT / 'outputs' / 'models'
FACTORS = ['force', 'repetition', 'duration',
           'vibration', 'contact_stress', 'posture']
LABELS  = ['Low', 'Medium', 'High']


def predict_rider(rider):
    if isinstance(rider, dict):
        frame = pd.DataFrame([rider])
    elif isinstance(rider, pd.Series):
        frame = rider.to_frame().T
    else:
        frame = rider.head(1)

    out = {}
    for factor in FACTORS:
        b = joblib.load(MODELS / f'best_{factor}.pkl')
        pred = int(b['model'].predict(frame[b['features']])[0])
        # map back from the 0-indexed model output to the original risk code
        code = int(b['classes'][pred])
        out[factor] = LABELS[code]
    return out


def required_features():
    return {f: joblib.load(MODELS / f'best_{f}.pkl')['features'] for f in FACTORS}


def _cli():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--rider-id', type=int)
    g.add_argument('--json', type=str)
    g.add_argument('--list-features', action='store_true')
    args = p.parse_args()

    if args.list_features:
        for factor, feats in required_features().items():
            print(f'{factor:18s}  ({len(feats)} features)')
            for f in feats:
                print(f'    {f}')
        return

    if args.rider_id is not None:
        df = pd.read_csv(ROOT / 'data' / 'processed' / 'model_ready.csv')
        rider = df.iloc[args.rider_id].to_dict()
        print(f'Rider {args.rider_id}:')
    else:
        rider = json.load(open(args.json))
        print(f'Rider from {args.json}:')

    print(json.dumps(predict_rider(rider), indent=2))


if __name__ == '__main__':
    _cli()

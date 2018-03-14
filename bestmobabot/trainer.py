import base64
import gzip
import json
import logging
import pickle
import sys
from collections import defaultdict
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import Any, DefaultDict, Dict, Iterable, List, Set, TextIO, Tuple

import click
import coloredlogs
import numpy
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, RandomizedSearchCV, StratifiedKFold


DROPNA_THRESHOLD = 5
CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
SCORING = 'accuracy'
CHUNK_LENGTH = 94


@click.command()
@click.argument('log_files', type=click.File('rt'), nargs=-1, required=True)
@click.option('-n', '--n-iter', type=int, default=20)
def main(log_files: Iterable[TextIO], n_iter: int):
    """
    Train and generate arena prediction model.
    https://github.com/eigenein/bestmobabot/blob/master/research/bestmoba.ipynb
    """
    coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, stream=sys.stderr)

    # Read battles.
    battles = DataFrame(read_battles(log_files)).dropna(axis=1, thresh=DROPNA_THRESHOLD).fillna(value=0.0)
    logging.info('Battles shape: %s.', battles.shape)

    # Split into X and y.
    x = battles.drop(['win'], axis=1)
    y = battles['win']

    # Train, adjust hyper-parameters and evaluate.
    logging.info('Adjusting hyper-parameters…')
    estimator, scores = train(x, y, n_iter)

    # Dump model.
    logging.info('Dumping model…')
    dump_model(estimator, x, scores)

    logging.info('Finished.')


def read_battles(log_files: Iterable[TextIO]) -> List[Dict[str, Any]]:
    logging.info('Reading battles…')
    battle_set: Set[Tuple[Tuple[str, Any]]] = {tuple(sorted(parse_battle(line).items())) for line in chain(*log_files)}
    return [dict(battle) for battle in battle_set]


def parse_heroes(heroes: Iterable[Dict[str, int]], multiplier: int, result: DefaultDict[str, int]):
    for hero in heroes:
        result[f'level_{hero["id"]}'] += multiplier * hero['level']
        result[f'color_{hero["id"]}'] += multiplier * hero['color']
        result[f'star_{hero["id"]}'] += multiplier * hero['star']


def parse_battle(line: str) -> Dict[str, Any]:
    battle = json.loads(line)
    result = defaultdict(int)

    parse_heroes(battle.get('attackers') or battle['player'], +1, result)
    parse_heroes(battle.get('defenders') or battle['enemies'], -1, result)

    return {'win': battle['win'], **result}


def train(x, y, n_iter: int):
    classifier = RandomForestClassifier(class_weight='balanced', n_jobs=5, random_state=42)
    param_grid = {
        'n_estimators': list(range(1, 501)),
        'max_features': ['sqrt', 'log2'],
        'max_depth': list(range(1, x.shape[1] + 1)),
        'criterion': ['entropy', 'gini'],
    }

    numpy.random.seed(42)
    grid_search = RandomizedSearchCV(classifier, param_grid, cv=CV, scoring=SCORING, n_iter=n_iter, random_state=42).fit(x, y)
    estimator = grid_search.best_estimator_

    numpy.random.seed(42)
    scores = cross_val_score(estimator, x, y, scoring=SCORING, cv=CV)
    logging.info('Best score: %s', grid_search.best_score_)
    logging.info('Best params: %s', grid_search.best_params_)
    logging.info('Classes: %s', estimator.classes_)
    logging.info('CV score: %s (std: %s)', scores.mean(), scores.std())

    # Re-train the best model on the entire dataset.
    logging.info('Training…')
    estimator.fit(x, y)

    return estimator, scores


def dump_model(estimator, x, scores):
    path = Path(__file__).parent / 'model.py'
    with path.open('wt') as fp:
        # Print out docstring.
        print('"""', file=fp)
        print('Arena battle prediction model.', file=fp)
        print(f'Auto-generated on {datetime.now().replace(microsecond=0)}.', file=fp)
        print(f'X shape: {x.shape}.', file=fp)
        print(f'Score: {scores.mean():.4f} (std: {scores.std():.4f}).', file=fp)
        print('"""', file=fp)

        # Imports.
        print('', file=fp)
        print('import base64', file=fp)
        print('import gzip', file=fp)
        print('import pickle', file=fp)
        print('', file=fp)
        print(f'from {estimator.__class__.__module__} import {estimator.__class__.__qualname__}', file=fp)
        print('', file=fp)

        # Model.
        print(f'feature_names = {list(x.columns)}', file=fp)
        print(f'model: {estimator.__class__.__qualname__} = pickle.loads(gzip.decompress(base64.b64decode(', file=fp)
        dump = base64.b64encode(gzip.compress(pickle.dumps(estimator))).decode()
        for i in range(0, len(dump), CHUNK_LENGTH):
            print(f"    '{dump[i:i + CHUNK_LENGTH]}'", file=fp)
        print(')))', file=fp)


if __name__ == '__main__':
    main()

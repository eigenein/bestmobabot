import base64
import gzip
import json
import logging
import pickle
import sys
import warnings
from collections import defaultdict
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import Any, DefaultDict, Dict, Iterable, List, Set, TextIO, Tuple

import click
import coloredlogs
import numpy
from pandas import DataFrame, Series
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
# noinspection PyPackageRequirements
from skopt import BayesSearchCV


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
    if not sys.warnoptions:
        warnings.simplefilter('ignore')

    # Read battles.
    battles = DataFrame(read_battles(log_files)).fillna(value=0.0)
    logging.info('Battles shape: %s.', battles.shape)

    # Split into X and y.
    x: DataFrame = battles.drop(['win'], axis=1)
    y: Series = battles['win']
    value_counts: DataFrame = y.value_counts()
    logging.info('Wins: %s. Losses: %s.', value_counts[False], value_counts[True])

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


def parse_heroes(heroes: Iterable[Dict[str, int]], is_attackers: bool, result: DefaultDict[str, int]):
    multiplier = +1 if is_attackers else -1
    for hero in heroes:
        result[f'level_{hero["id"]}'] += multiplier * int(hero['level'])
        result[f'color_{hero["id"]}'] += multiplier * int(hero['color'])
        result[f'star_{hero["id"]}'] += multiplier * int(hero['star'])


def parse_battle(line: str) -> Dict[str, Any]:
    battle = json.loads(line)
    result = defaultdict(int)

    parse_heroes(battle.get('attackers') or battle['player'], True, result)
    parse_heroes(battle.get('defenders') or battle['enemies'], False, result)

    return {'win': battle['win'], **result}


def train(x: DataFrame, y: Series, n_iter: int) -> Tuple[Any, numpy.ndarray]:
    estimator = RandomForestClassifier(class_weight='balanced', n_jobs=5, random_state=42)
    param_grid = {
        'n_estimators': (1, 200),
        'max_features': (1, x.shape[1]),
        'criterion': ['entropy', 'gini'],
    }

    numpy.random.seed(42)
    search_cv = BayesSearchCV(estimator, param_grid, cv=CV, scoring=SCORING, n_iter=n_iter, random_state=42, refit=False)
    search_cv.fit(x, y, callback=lambda result: logging.info('#%s: %.4f…', len(result.x_iters), search_cv.best_score_))
    estimator.set_params(**search_cv.best_params_)

    # Perform cross-validation.
    logging.info('Cross validation…')
    numpy.random.seed(42)
    scores: numpy.ndarray = cross_val_score(estimator, x, y, scoring=SCORING, cv=CV)
    score_interval = stats.t.interval(0.95, len(scores) - 1, loc=numpy.mean(scores), scale=stats.sem(scores))
    logging.info('Best score: %.4f', search_cv.best_score_)
    logging.info('Best params: %s', search_cv.best_params_)
    logging.info('CV score: %.4f (%.4f … %.4f).', scores.mean(), *score_interval)

    # Re-train the best model on the entire data.
    logging.info('Refitting…')
    estimator.fit(x, y)
    logging.info('Classes: %s', estimator.classes_)

    return estimator, scores


def dump_model(estimator: Any, x: DataFrame, scores: numpy.ndarray):
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

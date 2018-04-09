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
from operator import itemgetter
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

from bestmobabot.responses import Hero


SCORING = 'accuracy'
CHUNK_LENGTH = 94


@click.command()
@click.argument('log_files', type=click.File('rt'), nargs=-1, required=True)
@click.option('-v', '--verbose', is_flag=True, default=False, help='Increase verbosity.')
@click.option('-n', '--n-iterations', type=int, default=100, help='Hyper-parameters search iterations.')
@click.option('--n-splits', type=int, default=10, help='K-fold splits.')
def main(log_files: Iterable[TextIO], verbose: bool, n_iterations: int, n_splits: int):
    """
    Train and generate arena prediction model.
    https://github.com/eigenein/bestmobabot/blob/master/research/bestmoba.ipynb
    """
    coloredlogs.install(
        fmt='%(asctime)s %(levelname)s %(message)s',
        level=(logging.INFO if not verbose else logging.DEBUG),
        stream=sys.stderr,
    )
    if not sys.warnoptions:
        warnings.simplefilter('ignore')

    # Read battles.
    battles = DataFrame(read_battles(log_files)).fillna(value=0.0)
    logging.info(f'Battles shape: {battles.shape}.')

    # Split into X and y.
    x: DataFrame = battles.drop(['win'], axis=1)
    y: Series = battles['win']
    value_counts: DataFrame = y.value_counts()
    logging.info(f'Wins: {value_counts[False]}. Losses: {value_counts[True]}.')

    # Train, adjust hyper-parameters and evaluate.
    logging.info('Adjusting hyper-parameters…')
    estimator, scores = train(x, y, n_iterations, n_splits)

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
        for key, value in Hero(hero).features_dict.items():
            result[key] += multiplier * value


def parse_battle(line: str) -> Dict[str, Any]:
    battle = json.loads(line)
    result = defaultdict(int)

    parse_heroes(battle.get('attackers') or battle['player'], True, result)
    parse_heroes(battle.get('defenders') or battle['enemies'], False, result)

    return {'win': battle['win'], **result}


def train(x: DataFrame, y: Series, n_iterations: int, n_splits: int) -> Tuple[Any, numpy.ndarray]:
    estimator = RandomForestClassifier(class_weight='balanced', n_jobs=5, random_state=42)
    param_grid = {
        'n_estimators': (1, 250),
        'max_features': (1, x.shape[1]),
        'criterion': ['entropy', 'gini'],
    }
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    numpy.random.seed(42)
    search_cv = BayesSearchCV(estimator, param_grid, cv=cv, scoring=SCORING, n_iter=n_iterations, random_state=42, refit=False)
    search_cv.fit(x, y, callback=lambda result: logging.info(f'#{len(result.x_iters)} {SCORING}: {search_cv.best_score_:.4f}'))
    estimator.set_params(**search_cv.best_params_)

    # Perform cross-validation.
    logging.info('Cross validation…')
    numpy.random.seed(42)
    scores: numpy.ndarray = cross_val_score(estimator, x, y, scoring=SCORING, cv=cv)
    score_interval = stats.t.interval(0.95, len(scores) - 1, loc=numpy.mean(scores), scale=stats.sem(scores))
    logging.info(f'Best score: {search_cv.best_score_:.4f}')
    logging.info(f'Best params: {search_cv.best_params_}')
    logging.info(f'CV score: {scores.mean():.4f} ({score_interval[0]:.4f} … {score_interval[1]:.4f}).')

    # Re-train the best model on the entire data.
    logging.info('Refitting…')
    estimator.fit(x, y)

    # Print debugging info.
    logging.debug(f'Classes: {estimator.classes_}')
    for column, importance in sorted(zip(x.columns, estimator.feature_importances_), key=itemgetter(1), reverse=True):
        logging.debug(f'Feature {column}: {importance:.7f}')

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

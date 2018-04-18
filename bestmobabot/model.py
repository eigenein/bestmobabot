import logging
import pickle
from collections import defaultdict
from operator import itemgetter
from typing import Any, DefaultDict, Dict, Iterable, List, NamedTuple, Set, Tuple

import numpy
from pandas import DataFrame, Series
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from skopt import BayesSearchCV

from bestmobabot import constants, responses
from bestmobabot.database import Database


class Model(NamedTuple):
    estimator: RandomForestClassifier
    feature_names: List[str]


class Trainer:
    def __init__(self, db: Database, *, n_iterations: int, n_splits: int, logger: logging.Logger):
        self.db = db
        self.n_iterations = n_iterations
        self.n_splits = n_splits
        self.logger = logger

    def train(self):
        def fit_callback(result):
            self.logger.info(f'🤖 #{len(result.x_iters)} {constants.SCORING}: {search_cv.best_score_:.4f}')

        # Read battles.
        battle_list = self.read_battles()
        if not battle_list:
            self.logger.info('🤖 There are no battles. Wait until someone attacks you.')
            return
        battles = DataFrame(battle_list).fillna(value=0.0)
        self.logger.info(f'🤖 Battles shape: {battles.shape}.')

        # Split into X and y.
        x: DataFrame = battles.drop(['win'], axis=1)
        y: Series = battles['win']
        value_counts: DataFrame = y.value_counts()
        self.logger.info(f'🤖 Wins: {value_counts[False]}. Losses: {value_counts[True]}.')

        estimator = RandomForestClassifier(class_weight='balanced', n_jobs=5, random_state=42)
        param_grid = {
            'n_estimators': (1, 250),
            'max_features': (1, x.shape[1]),
            'criterion': ['entropy', 'gini'],
        }
        cv = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=42)

        self.logger.info('🤖 Adjusting hyper-parameters…')
        numpy.random.seed(42)
        search_cv = BayesSearchCV(
            estimator,
            param_grid,
            cv=cv,
            scoring=constants.SCORING,
            n_iter=self.n_iterations,
            random_state=42,
            refit=False,
        )
        search_cv.fit(x, y, callback=fit_callback)
        estimator.set_params(**search_cv.best_params_)

        # Perform cross-validation.
        self.logger.info('🤖 Cross validation…')
        numpy.random.seed(42)
        scores: numpy.ndarray = cross_val_score(estimator, x, y, scoring=constants.SCORING, cv=cv)
        score_interval = stats.t.interval(0.95, len(scores) - 1, loc=numpy.mean(scores), scale=stats.sem(scores))
        self.logger.info(f'🤖 Best score: {search_cv.best_score_:.4f}')
        self.logger.info(f'🤖 Best params: {search_cv.best_params_}')
        self.logger.info(f'🤖 CV score: {scores.mean():.4f} ({score_interval[0]:.4f} … {score_interval[1]:.4f}).')

        # Re-train the best model on the entire data.
        self.logger.info('🤖 Refitting…')
        estimator.fit(x, y)

        # Print debugging info.
        self.logger.debug(f'🤖 Classes: {estimator.classes_}')
        for column, importance in sorted(zip(x.columns, estimator.feature_importances_), key=itemgetter(1), reverse=True):
            self.logger.debug(f'🤖 Feature {column}: {importance:.7f}')

        logging.info('🤖 Saving model…')
        self.db.set('bot', 'model', pickle.dumps(Model(estimator, list(x.columns))), dumps=bytes.hex)

        self.logger.info('🤖 Finished.')

    def read_battles(self) -> List[Dict[str, Any]]:
        self.logger.info('🤖 Reading battles…')
        battle_set: Set[Tuple[Tuple[str, Any]]] = {
            tuple(sorted(self.parse_battle(value).items()))
            for _, value in self.db.get_by_index('replays')
        }
        return [dict(battle) for battle in battle_set]

    @classmethod
    def parse_battle(cls, battle: Dict[str, Any]) -> Dict[str, Any]:
        result = defaultdict(int)

        cls.parse_heroes(battle.get('attackers') or battle['player'], True, result)
        cls.parse_heroes(battle.get('defenders') or battle['enemies'], False, result)

        return {'win': battle['win'], **result}

    @staticmethod
    def parse_heroes(heroes: Iterable[Dict[str, int]], is_attackers: bool, result: DefaultDict[str, int]):
        multiplier = +1 if is_attackers else -1
        for hero in heroes:
            for key, value in responses.Hero(hero).feature_dict.items():
                result[key] += multiplier * value

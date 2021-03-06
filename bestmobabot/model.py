import pickle
from base64 import b85encode
from collections import defaultdict
from itertools import product
from operator import itemgetter
from typing import Any, DefaultDict, Dict, Iterable, List, NamedTuple, Optional

import numpy
from loguru import logger
from pandas import DataFrame, Series
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

from bestmobabot import constants, dataclasses_
from bestmobabot.database import Database


class Model(NamedTuple):
    estimator: RandomForestClassifier
    feature_names: List[str]


class Trainer:
    def __init__(self, db: Database, *, n_splits: int, n_last_battles: int):
        self.db = db
        self.n_splits = n_splits
        self.n_last_battles = n_last_battles

    def train(self):
        """
        Train the model. If `params` is not set, hyper-parameters search will be performed.
        """
        numpy.random.seed(42)

        # Read battles.
        battle_list = self.deduplicate_battles(self.read_battles())
        if not battle_list:
            logger.info('There are no battles. Wait until someone attacks you.')
            return
        battles = DataFrame(battle_list).fillna(value=0.0)
        logger.info(f'Battles shape: {battles.shape}.')

        # Split into X and y.
        x: DataFrame = battles.drop(['win'], axis=1)
        y: Series = battles['win']
        value_counts: DataFrame = y.value_counts()
        logger.info(f'Wins: {value_counts[False]}. Losses: {value_counts[True]}.')

        # Here's our model.
        estimator = RandomForestClassifier(class_weight='balanced', n_jobs=-1)

        # Search for hyper-parameters if not explicitly set.
        params = self.search_hyper_parameters(
            x, y, estimator, constants.MODEL_PARAM_GRID, StratifiedKFold(n_splits=self.n_splits, shuffle=True))

        # Re-train the best model on the entire data.
        logger.info(f'Refitting with params: {params}…')
        estimator.set_params(**params).fit(x, y)
        if not numpy.array_equal(estimator.classes_, numpy.array([False, True])):
            raise RuntimeError(f'unexpected classes: {estimator.classes_}')

        # Print debugging info.
        for column, importance in sorted(zip(x.columns, estimator.feature_importances_), key=itemgetter(1), reverse=True):  # noqa
            if importance > 0.0001:
                logger.trace(f'Feature {column}: {importance:.4f}')

        logger.info('Saving model…')
        self.db['bot:model'] = b85encode(pickle.dumps(
            Model(estimator, list(x.columns)),
            protocol=pickle.HIGHEST_PROTOCOL,
        )).decode()

        logger.info('Optimizing database…')
        self.db.vacuum()

        logger.info('Finished.')

    @staticmethod
    def search_hyper_parameters(x, y, estimator, param_grid, cv) -> Dict:
        logger.info('Searching for the best hyper-parameters…')
        search_cv = TTestSearchCV(
            estimator, param_grid, cv=cv, scoring=constants.MODEL_SCORING, alpha=constants.MODEL_SCORING_ALPHA)

        try:
            search_cv.fit(x, y)
        except KeyboardInterrupt:
            pass  # allow stopping the process

        score_interval = search_cv.best_confidence_interval_
        logger.info(f'Best score: {search_cv.best_score_:.4f} ({score_interval[0]:.4f} … {score_interval[1]:.4f})')
        logger.info(f'Best params: {search_cv.best_params_}')

        return search_cv.best_params_

    def read_battles(self) -> Iterable[Dict[str, Any]]:
        logger.info('Selecting battles…')
        values = [value for _, value in self.db.get_by_prefix('replays:')]
        logger.info('Sorting battles…')
        values.sort(key=lambda value: value.get('start_time', 0.0))
        values = values[-self.n_last_battles:]
        logger.info('Parsing battles…')
        return [self.parse_battle(value) for value in values]

    @staticmethod
    def deduplicate_battles(battles: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return list(dict(items) for items in {tuple(sorted(battle.items())) for battle in battles})

    @classmethod
    def parse_battle(cls, battle: Dict[str, Any]) -> Dict[str, Any]:
        # Yield battle itself.
        result = defaultdict(int)
        cls.parse_heroes(battle.get('attackers') or battle['player'], +1, result)
        cls.parse_heroes(battle.get('defenders') or battle['enemies'], -1, result)
        return {'win': battle['win'], **result}

    @staticmethod
    def parse_heroes(heroes: Iterable[Dict[str, int]], multiplier: int, result: DefaultDict[str, int]):
        for hero in heroes:
            for key, value in dataclasses_.Hero.parse_obj(hero).features.items():
                result[key] += multiplier * value


class TTestSearchCV:
    def __init__(self, estimator, param_grid, *, cv, scoring, alpha=0.95):
        self.estimator = estimator
        self.param_grid: Dict[str, Any] = param_grid
        self.cv = cv
        self.scoring = scoring
        self.alpha = alpha

        self.p = 1.0 - alpha
        self.best_params_: Optional[Dict[str, Any]] = None
        self.best_score_: Optional[float] = None
        self.best_scores_: Optional[numpy.ndarray] = None
        self.best_confidence_interval_: Optional[numpy.ndarray] = None

    def fit(self, x, y):
        for values in product(*self.param_grid.values()):
            params = dict(zip(self.param_grid.keys(), values))
            self.estimator.set_params(**params)
            logger.trace(f'CV started: {params}')
            scores: numpy.ndarray = cross_val_score(self.estimator, x, y, scoring=self.scoring, cv=self.cv)
            score: float = scores.mean()
            logger.debug(f'Score: {score:.4f} with {params}.')
            if not self.is_better_score(score, scores):
                continue
            logger.success(f'Found significantly better score: {score:.4f}.')
            self.best_params_ = params
            self.best_score_ = score
            self.best_scores_ = scores
            self.best_confidence_interval_ = stats.t.interval(
                self.alpha,
                len(scores) - 1,
                loc=scores.mean(),
                scale=stats.sem(scores),
            )

    def is_better_score(self, score: float, scores: numpy.ndarray) -> bool:
        if self.best_params_ is None:
            return True
        if score < self.best_score_:
            return False
        _, p_value = stats.ttest_ind(self.best_scores_, scores)
        logger.trace(f'P-value: {p_value:.4f}.')
        return p_value < self.p

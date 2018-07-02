import itertools
import pickle
from collections import defaultdict
from operator import itemgetter
from typing import Any, DefaultDict, Dict, Iterable, List, NamedTuple, Optional, Set, Tuple

import numpy
from pandas import DataFrame, Series
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

from bestmobabot import constants, responses
from bestmobabot.constants import SPAM
from bestmobabot.database import Database
from bestmobabot.logging_ import logger


class Model(NamedTuple):
    estimator: RandomForestClassifier
    feature_names: List[str]


class Trainer:
    def __init__(self, db: Database, *, n_splits: int):
        self.db = db
        self.n_splits = n_splits

    def train(self):
        numpy.random.seed(42)

        # Read battles.
        battle_list = self.read_battles()
        if not battle_list:
            logger.info('🤖 There are no battles. Wait until someone attacks you.')
            return
        battles = DataFrame(battle_list).fillna(value=0.0)
        logger.info(f'🤖 Battles shape: {battles.shape}.')

        # Split into X and y.
        x: DataFrame = battles.drop(['win'], axis=1)
        y: Series = battles['win']
        value_counts: DataFrame = y.value_counts()
        logger.info(f'🤖 Wins: {value_counts[False]}. Losses: {value_counts[True]}.')

        estimator = RandomForestClassifier(class_weight='balanced', n_jobs=-1)
        param_grid = {
            'n_estimators': constants.MODEL_N_ESTIMATORS_CHOICES,
            'criterion': ['entropy', 'gini'],
        }
        cv = StratifiedKFold(n_splits=self.n_splits, shuffle=True)

        logger.info('🤖 Adjusting hyper-parameters…')
        search_cv = TTestSearchCV(
            estimator,
            param_grid,
            cv=cv,
            scoring=constants.MODEL_SCORING,
            alpha=constants.MODEL_SCORING_ALPHA,
        )
        try:
            search_cv.fit(x, y)
        except KeyboardInterrupt:
            pass  # allow stopping the process
        score_interval = search_cv.best_confidence_interval_
        logger.info(f'🤖 Best score: {search_cv.best_score_:.4f} ({score_interval[0]:.4f} … {score_interval[1]:.4f})')
        logger.info(f'🤖 Best params: {search_cv.best_params_}')

        # Re-train the best model on the entire data.
        logger.info('🤖 Refitting…')
        estimator.set_params(**search_cv.best_params_)
        estimator.fit(x, y)
        if not numpy.array_equal(estimator.classes_, numpy.array([False, True])):
            raise RuntimeError(f'unexpected classes: {estimator.classes_}')

        # Print debugging info.
        for column, importance in sorted(zip(x.columns, estimator.feature_importances_), key=itemgetter(1), reverse=True):
            logger.log(SPAM, f'🤖 Feature {column}: {importance:.7f}')

        logger.info('🤖 Saving model…')
        self.db.set('bot', 'model', pickle.dumps(Model(estimator, list(x.columns))), dumps=bytes.hex)

        logger.info('🤖 Optimizing database…')
        self.db.vacuum()

        logger.info('🤖 Finished.')

    def read_battles(self) -> List[Dict[str, Any]]:
        logger.info('🤖 Reading battles…')
        battle_set: Set[Tuple[Tuple[str, Any]]] = {
            tuple(sorted(battle.items()))
            for _, value in self.db.get_by_index('replays')
            for battle in self.parse_battles(value)
        }
        return [dict(battle) for battle in battle_set]

    @classmethod
    def parse_battles(cls, battle: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        # Yield battle itself.
        result = defaultdict(int)
        cls.parse_heroes(battle.get('attackers') or battle['player'], True, result)
        cls.parse_heroes(battle.get('defenders') or battle['enemies'], False, result)
        yield {'win': battle['win'], **result}

        # Yield mirrored battle.
        result = defaultdict(int)
        cls.parse_heroes(battle.get('attackers') or battle['player'], False, result)
        cls.parse_heroes(battle.get('defenders') or battle['enemies'], True, result)
        yield {'win': not battle['win'], **result}

    @staticmethod
    def parse_heroes(heroes: Iterable[Dict[str, int]], is_attackers: bool, result: DefaultDict[str, int]):
        multiplier = +1 if is_attackers else -1
        for hero in heroes:
            for key, value in responses.Hero(hero).feature_dict.items():
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
        for values in itertools.product(*self.param_grid.values()):
            params = dict(zip(self.param_grid.keys(), values))
            self.estimator.set_params(**params)
            logger.log(SPAM, f'🤖 CV started: {params}')
            scores: numpy.ndarray = cross_val_score(self.estimator, x, y, scoring=self.scoring, cv=self.cv)
            score: float = scores.mean()
            logger.debug(f'🤖 Score: {score:.4f} with {params}.')
            if not self.is_better_score(score, scores):
                continue
            logger.debug(f'🤖 Found significantly better score: {score:.4f}.')
            self.best_params_ = params
            self.best_score_ = score
            self.best_scores_ = scores
            self.best_confidence_interval_ = stats.t.interval(self.alpha, len(scores) - 1, loc=scores.mean(), scale=stats.sem(scores))

    def is_better_score(self, score: float, scores: numpy.ndarray) -> bool:
        if self.best_params_ is None:
            return True
        if score < self.best_score_:
            return False
        _, p_value = stats.ttest_ind(self.best_scores_, scores)
        logger.log(SPAM, f'🤖 P-value: {p_value:.4f}.')
        return p_value < self.p

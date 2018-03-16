"""
Game API response wrappers.
"""

import logging
from abc import ABC, ABCMeta
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any, Dict, List, Optional

import numpy

from bestmobabot.model import feature_names
from bestmobabot.resources import COLORS, NAMES
from bestmobabot.types import *


class BaseResponse(ABC):
    """
    Base for all response classes.
    """

    def __init__(self, item: Dict):
        self.item = item


class Result(BaseResponse):
    """
    Top-most result class.
    """

    def __init__(self, item: Dict):
        super().__init__(item)
        self.response: Any = item['response']
        self.quests: 'Quests' = [Quest(quest) for quest in item.get('quests', [])]


class User(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: UserID = UserID(item['id'])
        self.name: str = item['name']
        self.tz: tzinfo = timezone(timedelta(hours=item.get('timeZone', 0)))
        self.clan_id: ClanID = str(item.get('clanId'))
        self.next_day: datetime = datetime.fromtimestamp(item.get('nextDayTs', 0), self.tz)

    def is_from_clan(self, clan_id: Optional[str]) -> bool:
        return clan_id and self.clan_id and self.clan_id == clan_id


class Expedition(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: ExpeditionID = str(item['id'])
        self.status: int = int(item['status'])
        self.end_time: Optional[datetime] = datetime.fromtimestamp(item['endTime']).astimezone() if item.get('endTime') else None
        self.power: int = int(item['power'])
        self.duration: timedelta = timedelta(seconds=item['duration'])
        self.hero_ids: List[HeroID] = [str(hero_id) for hero_id in item.get('heroes', [])]

    @property
    def is_available(self) -> bool:
        return self.status == 1

    @property
    def is_started(self) -> bool:
        return self.status == 2


class Reward(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.stamina: Stamina = item.get('stamina', 0)
        self.gold: Gold = item.get('gold', 0)
        self.experience: Experience = int(item.get('experience', 0))
        self.consumable: Dict[str, int] = item.get('consumable', {})
        self.star_money: StarMoney = int(item.get('starmoney', 0))
        self.coin: Dict[str, str] = item.get('coin', {})
        self.hero_fragment: Dict[HeroID, int] = item.get('fragmentHero', {})
        self.artifact_fragment: Dict[str, int] = item.get('fragmentArtifact', {})
        self.gear_fragment: Dict[str, int] = item.get('fragmentGear', {})
        self.gear: Dict[str, str] = item.get('gear', {})
        self.scroll_fragment: Dict[str, str] = item.get('fragmentScroll', {})

    def log(self, logger: logging.Logger):
        if self.stamina:
            logger.info('📈 Stamina: %s.', self.stamina)
        if self.gold:
            logger.info('📈 Gold: %s.', self.gold)
        if self.experience:
            logger.info('📈 Experience: %s.', self.experience)
        if self.consumable:
            logger.info('📈 Consumable: %s.', self.consumable)
        if self.star_money:
            logger.info('📈 Star money: %s.', self.star_money)
        if self.coin:
            logger.info('📈 Coin: %s.', self.coin)
        if self.hero_fragment:
            logger.info('📈 Hero fragment: %s.', self.hero_fragment)
        if self.artifact_fragment:
            logger.info('📈 Artifact fragment: %s.', self.artifact_fragment)
        if self.gear_fragment:
            logger.info('📈 Gear fragment: %s.', self.gear_fragment)
        if self.gear:
            logger.info('📈 Gear: %s.', self.gear)


class Quest(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: QuestID = str(item['id'])
        self.state: QuestState = int(item['state'])
        self.progress: int = int(item['progress'])
        self.reward: Reward = Reward(item['reward'])

    @property
    def is_reward_available(self) -> bool:
        return self.state == 2


Quests = List[Quest]


class Letter:
    def __init__(self, item: Dict):
        self.id: LetterID = str(item['id'])


class Hero(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: HeroID = str(item['id'])
        self.level: int = int(item['level'])
        self.color: int = int(item['color'])
        self.star: int = int(item['star'])
        self.power: Optional[int] = item.get('power')
        # Prediction model features.
        features = {
            f'color_{self.id}': float(self.color),
            f'level_{self.id}': float(self.level),
            f'star_{self.id}': float(self.star),
        }
        self.features = numpy.fromiter((features.get(key, 0.0) for key in feature_names), numpy.float)

    def dump(self) -> dict:
        return {
            'id': self.id,
            'level': self.level,
            'color': self.color,
            'star': self.star,
        }

    def order(self):
        """
        Get comparison order.
        """
        return self.star, self.color, self.level

    def __str__(self):
        return f'{"⭐" * self.star} {NAMES.get(self.id, self.id)} ({self.level}) {COLORS.get(self.color, self.color)}'


class BaseArenaEnemy(BaseResponse, metaclass=ABCMeta):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.user_id: UserID = str(item['userId'])
        self.place: str = str(item['place'])
        self.power: int = int(item['power'])
        self.user: Optional[User] = User(item['user']) if item.get('user') else None


class ArenaEnemy(BaseArenaEnemy):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.heroes: List[Hero] = [Hero(hero) for hero in item['heroes']]


class GrandArenaEnemy(BaseArenaEnemy):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.heroes: List[List[Hero]] = [[Hero(hero) for hero in heroes] for heroes in item['heroes']]


class ArenaResult(BaseResponse):
    """
    Unified arena result for normal arena and grand arena.
    """

    def __init__(self, item: Dict):
        super().__init__(item)
        self.win: bool = item['win']
        self.arena_place: Optional[str] = item['state'].get('arenaPlace')
        self.grand_place: Optional[str] = item['state'].get('grandPlace')
        self.battles: List['BattleResult'] = [BattleResult(result) for result in item['battles']]
        self.reward: Reward = Reward(item['reward'] or {})


class BattleResult(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.win: bool = item['result']['win']
        self.stars: int = int(item['result'].get('stars', 0))


class Boss(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: BossID = str(item['id'])


class Battle(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.seed: int = item['seed']


class Replay(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: ReplayID = item['id']
        self.win: bool = item['result']['win']
        self.stars: int = int(item['result']['stars'])
        self.attackers: List[Hero] = [Hero(hero) for hero in item['attackers'].values()]
        self.defenders: List[List[Hero]] = [[Hero(hero) for hero in defenders.values()] for defenders in item['defenders']]


class ShopSlot(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: SlotID = str(item['id'])
        self.is_bought: bool = bool(item['bought'])
        self.reward: Reward = Reward(item['reward'])


__all__ = [
    'BaseResponse',
    'Result',
    'User',
    'Expedition',
    'Reward',
    'Quest',
    'Quests',
    'Letter',
    'Hero',
    'BaseArenaEnemy',
    'ArenaEnemy',
    'GrandArenaEnemy',
    'ArenaResult',
    'BattleResult',
    'Boss',
    'Battle',
    'Replay',
    'ShopSlot',
]

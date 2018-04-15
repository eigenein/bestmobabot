"""
Game API response wrappers.
"""

import logging
from abc import ABC, ABCMeta
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any, Dict, List, Optional

import numpy

from bestmobabot import constants, model
from bestmobabot.resources import artifact_name, coin_name, consumable_name, gear_name, hero_name, scroll_name


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
        self.id: str = str(item['id'])
        self.name: str = item['name']
        self.tz: tzinfo = timezone(timedelta(hours=item.get('timeZone', 0)))
        self.clan_id: str = str(item.get('clanId'))
        self.next_day: datetime = datetime.fromtimestamp(item.get('nextDayTs', 0), self.tz)

    def is_from_clan(self, clan_id: Optional[str]) -> bool:
        return clan_id and self.clan_id and self.clan_id == clan_id


class Expedition(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: str = str(item['id'])
        self.status: int = int(item['status'])
        self.end_time: Optional[datetime] = datetime.fromtimestamp(item['endTime']).astimezone() if item.get('endTime') else None
        self.power: int = int(item['power'])
        self.duration: timedelta = timedelta(seconds=item['duration'])
        self.hero_ids: List[str] = [str(hero_id) for hero_id in item.get('heroes', [])]

    @property
    def is_available(self) -> bool:
        return self.status == 1

    @property
    def is_started(self) -> bool:
        return self.status == 2


class Reward(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.stamina: int = int(item.get('stamina', 0))
        self.gold: int = int(item.get('gold', 0))
        self.experience: int = int(item.get('experience', 0))
        self.consumable: Dict[str, int] = item.get('consumable', {})
        self.star_money: int = int(item.get('starmoney', 0))
        self.coin: Dict[str, str] = item.get('coin', {})
        self.hero_fragment: Dict[str, int] = item.get('fragmentHero', {})
        self.artifact_fragment: Dict[str, int] = item.get('fragmentArtifact', {})
        self.gear_fragment: Dict[str, int] = item.get('fragmentGear', {})
        self.gear: Dict[str, str] = item.get('gear', {})
        self.scroll_fragment: Dict[str, str] = item.get('fragmentScroll', {})
        self.tower_point = int(item.get('towerPoint', 0))

    def log(self, logger: logging.Logger):
        if self.stamina:
            logger.info(f'🔋 {self.stamina} × stamina.')
        if self.gold:
            logger.info(f'💰 {self.gold} × gold.')
        if self.experience:
            logger.info(f'📈 {self.experience} × experience.')
        for consumable_id, value in self.consumable.items():
            logger.info(f'🍔 {value} × «{consumable_name(consumable_id)}» consumable.')
        if self.star_money:
            logger.info(f'✨ {self.star_money} × star money.')
        for coin_id, value in self.coin.items():
            logger.info(f'💟️ {value} × «{coin_name(coin_id)}» coin.')
        for hero_id, value in self.hero_fragment.items():
            logger.info(f'🔮 {value} × «{hero_name(hero_id)}» hero fragment.')
        for artifact_id, value in self.artifact_fragment.items():
            logger.info(f'👕 {value} × «{artifact_name(artifact_id)}» artifact fragment.')
        for gear_id, value in self.gear_fragment.items():
            logger.info(f'👕 {value} × «{gear_name(gear_id)}» gear fragment.')
        for gear_id, value in self.gear.items():
            logger.info(f'👕 {value} × «{gear_name(gear_id)}» gear.')
        for scroll_id, value in self.scroll_fragment.items():
            logger.info(f'👕 {value} × «{scroll_name(scroll_id)}» scroll fragment.')


class Quest(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: str = str(item['id'])
        self.state: int = int(item['state'])
        self.progress: int = int(item['progress'])
        self.reward: Reward = Reward(item['reward'])

    @property
    def is_reward_available(self) -> bool:
        return self.state == 2


Quests = List[Quest]


class Letter:
    def __init__(self, item: Dict):
        self.id: str = str(item['id'])


class Hero(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: str = str(item['id'])
        self.level: int = int(item['level'])
        self.color: int = int(item['color'])
        self.star: int = int(item['star'])
        self.power: Optional[int] = item.get('power')

        # Should be here to optimise CPU usage.
        self.feature_dict = {
            f'color_{self.id}': float(self.color),
            f'level_{self.id}': float(self.level),
            f'star_{self.id}': float(self.star),
            f'color_level_star_{self.id}': float(self.color) * float(self.level) * float(self.star),
            f'color_level_{self.id}': float(self.color) * float(self.level),
            f'color_star_{self.id}': float(self.color) * float(self.star),
            f'level_star_{self.id}': float(self.level) * float(self.star),
            'total_color_level_star': float(self.color) * float(self.level) * float(self.star),
            'total_color_level': float(self.color) * float(self.level),
            'total_color_star': float(self.color) * float(self.star),
            'total_level_star': float(self.level) * float(self.star),
            'total_colors': float(self.color),
            'total_levels': float(self.level),
            'total_stars': float(self.star),
            'total_heroes': 1.0,
        }
        self.features = numpy.fromiter((self.feature_dict.get(key, 0.0) for key in model.feature_names), numpy.float)

    def dump(self) -> dict:
        return {key: self.item[key] for key in ('id', 'level', 'color', 'star')}

    def order(self):
        """
        Get comparison order.
        """
        return self.star, self.color, self.level

    def __str__(self):
        return f'{"⭐" * self.star} {hero_name(self.id)} ({self.level}) {constants.COLORS.get(self.color, self.color)}'


class BaseArenaEnemy(BaseResponse, metaclass=ABCMeta):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.user_id: str = str(item['userId'])
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
        self.id: str = str(item['id'])


class Battle(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.seed: int = item['seed']


class Replay(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: str = str(item['id'])
        self.start_time: datetime = datetime.fromtimestamp(int(item['startTime']))
        self.win: bool = item['result']['win']
        self.stars: int = int(item['result']['stars'])
        self.attackers: List[Hero] = [Hero(hero) for hero in item['attackers'].values()]
        self.defenders: List[List[Hero]] = [[Hero(hero) for hero in defenders.values()] for defenders in item['defenders']]


class ShopSlot(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.id: str = str(item['id'])
        self.is_bought: bool = bool(item['bought'])
        self.reward: Reward = Reward(item['reward'])


class Tower(BaseResponse):
    def __init__(self, item: Dict):
        super().__init__(item)
        self.floor_number = int(item['floorNumber'])
        self.may_skip_floor = int(item['maySkipFloor'])
        self.floor_type = item['floorType'].lower()
        # This is only available on a buff floor.
        self.buff_ids: List[int] = [int(buff['id']) for buff in item['floor']] if self.is_buff else []

    @property
    def is_battle(self) -> bool:
        return self.floor_type == 'battle'

    @property
    def is_buff(self) -> bool:
        return self.floor_type == 'buff'

    @property
    def is_chest(self):
        return self.floor_type == 'chest'


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
    'Tower',
]

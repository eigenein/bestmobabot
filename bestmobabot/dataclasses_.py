from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone, tzinfo
from functools import total_ordering
from typing import Any, Dict, Iterable, List, Optional, Set

from loguru import logger
from pydantic import BaseModel, validator
from pydantic.validators import _VALIDATORS

from bestmobabot import resources
from bestmobabot.constants import COLORS, RAID_N_STARS
from bestmobabot.enums import LibraryTitanElement, LibraryTitanType, TowerFloorType
from bestmobabot.telegram import TelegramLogger

_VALIDATORS.append((tzinfo, [lambda value: timezone(timedelta(hours=value))]))


class Loggable(ABC):
    # TODO: separate property specially for the Telegram logger.

    @property
    @abstractmethod
    def plain_text(self) -> Iterable[str]:
        raise NotImplementedError()

    @property
    def markdown(self) -> Iterable[str]:
        yield from self.plain_text

    def log(self, logger_: Optional[TelegramLogger] = None):
        for line in self.plain_text:
            logger.success('{}', line)
        if logger_:
            logger_.append(*self.markdown)


# FIXME: truth magic to check for emptiness.
class Reward(BaseModel, Loggable):
    artifact_fragment: Dict[str, int] = {}
    coin: Dict[str, str] = {}
    consumable: Dict[str, int] = {}
    dungeon_activity: int = 0
    experience: int = 0
    gear: Dict[str, int] = {}
    gear_fragment: Dict[str, int] = {}
    gold: int = 0
    hero_fragment: Dict[str, int] = {}
    scroll_fragment: Dict[str, int] = {}
    stamina: int = 0
    star_money: int = 0
    titan_artifact_fragment: Dict[str, int] = {}
    titan_fragment: Dict[str, int] = {}
    tower_point: int = 0

    class Config:
        fields = {
            'artifact_fragment': 'fragmentArtifact',
            'dungeon_activity': 'dungeonActivity',
            'gear_fragment': 'fragmentGear',
            'hero_fragment': 'fragmentHero',
            'scroll_fragment': 'fragmentScroll',
            'star_money': 'starmoney',
            'titan_artifact_fragment': 'fragmentTitanArtifact',
            'titan_fragment': 'fragmentTitan',
            'tower_point': 'towerPoint',
        }

    # FIXME: I don't really like this.
    @property
    def keywords(self) -> Set[str]:
        return {
            *(resources.consumable_name(consumable_id).lower() for consumable_id in self.consumable),
            *(resources.gear_name(gear_id).lower() for gear_id in self.gear),
            *(resources.gear_name(gear_id).lower() for gear_id in self.gear_fragment),
            *(resources.hero_name(hero_id).lower() for hero_id in self.hero_fragment),
            *(resources.scroll_name(scroll_id).lower() for scroll_id in self.scroll_fragment),
        }

    @property
    def plain_text(self) -> Iterable[str]:
        if self.stamina:
            yield f'{self.stamina} × stamina'
        if self.gold:
            yield f'{self.gold} × gold'
        if self.experience:
            yield f'{self.experience} × experience'
        if self.star_money:
            yield f'{self.star_money} × star money'
        if self.dungeon_activity:
            yield f'{self.dungeon_activity} × dungeon activity'
        for consumable_id, value in self.consumable.items():
            yield f'{value} × «{resources.consumable_name(consumable_id)}» consumable'
        for coin_id, value in self.coin.items():
            yield f'{value} × «{resources.coin_name(coin_id)}» coin'
        for hero_id, value in self.hero_fragment.items():
            yield f'{value} × «{resources.hero_name(hero_id)}» hero fragment'
        for artifact_id, value in self.artifact_fragment.items():
            yield f'{value} × «{resources.artifact_name(artifact_id)}» artifact fragment'
        for gear_id, value in self.gear_fragment.items():
            yield f'{value} × «{resources.gear_name(gear_id)}» gear fragment'
        for gear_id, value in self.gear.items():
            yield f'{value} × «{resources.gear_name(gear_id)}» gear'
        for scroll_id, value in self.scroll_fragment.items():
            yield f'{value} × «{resources.scroll_name(scroll_id)}» scroll fragment'
        for artifact_id, value in self.titan_artifact_fragment.items():
            yield f'{value} × «{resources.titan_artifact_name(artifact_id)}» titan artifact fragment'
        for hero_id, value in self.titan_fragment.items():
            yield f'{value} × «{resources.hero_name(hero_id)}» titan fragment'

    @property
    def markdown(self) -> Iterable[str]:
        if self.stamina:
            yield f'*{self.stamina}* × энергия'
        if self.gold:
            yield f'*{self.gold}* × золото'
        if self.experience:
            yield f'*{self.experience}* × опыт'
        if self.star_money:
            yield f'*{self.star_money}* × изумруды'
        if self.dungeon_activity:
            yield f'*{self.dungeon_activity}* × титанит'
        for consumable_id, value in self.consumable.items():
            yield f'{value} × *{resources.consumable_name(consumable_id)}*'
        for coin_id, value in self.coin.items():
            yield f'{value} × *{resources.coin_name(coin_id)}*'
        for hero_id, value in self.hero_fragment.items():
            yield f'{value} × камень души *{resources.hero_name(hero_id)}*'
        for artifact_id, value in self.artifact_fragment.items():
            yield f'{value} × фрагмент *{resources.artifact_name(artifact_id)}*'
        for gear_id, value in self.gear_fragment.items():
            yield f'{value} × фрагмент *{resources.gear_name(gear_id)}*'
        for gear_id, value in self.gear.items():
            yield f'{value} × *{resources.gear_name(gear_id)}*'
        for scroll_id, value in self.scroll_fragment.items():
            yield f'{value} × фрагмент *{resources.scroll_name(scroll_id)}*'
        for artifact_id, value in self.titan_artifact_fragment.items():
            yield f'{value} × фрагмент *{resources.titan_artifact_name(artifact_id)}*'
        for hero_id, value in self.titan_fragment.items():
            yield f'{value} × камень души *{resources.hero_name(hero_id)}*'


class LibraryMission(BaseModel):
    id: str
    is_heroic: bool

    class Config:
        fields = {'is_heroic': 'isHeroic'}


class LibraryTitan(BaseModel):
    id: str
    element: LibraryTitanElement
    type_: LibraryTitanType

    class Config:
        fields = {
            'type_': 'type',
        }


class Library(BaseModel):
    missions: Dict[str, LibraryMission]
    titans: Dict[str, LibraryTitan]

    class Config:
        fields = {
            'missions': 'mission',
            'titans': 'titan',
        }


class Letter(BaseModel):
    id: str


class Unit(BaseModel):
    id: str
    level: int
    star: int
    power: Optional[int] = None


@total_ordering
class Hero(Unit):
    color: int
    slots: List[str] = []
    skills: Dict[str, int] = {}
    runes: List[int] = []
    skins: Dict[str, int] = {}
    current_skin: Optional[str] = None
    titan_gift_level: Optional[int] = None
    artifacts: List[Dict[str, int]] = []
    scale: int = 1

    class Config:
        fields = {
            'current_skin': 'currentSkin',
            'titan_gift_level': 'titanGiftLevel',
        }

    # noinspection PyMethodParameters
    @validator('slots', pre=True, whole=True)
    def fix_slots(cls, value: Any):
        # These odd people sometimes return `{"1": 0, "0": 0}`, sometimes `[0]`.
        if isinstance(value, dict):
            return list(value)
        return value

    # noinspection PyMethodParameters
    @validator('skins', pre=True)
    def fix_skins(cls, value):
        return value or {}  # 🤦‍

    @property
    def features(self) -> Dict[str, float]:
        return {
            'total_color_level': float(self.color) * float(self.level),
            'total_color_level_star': float(self.color) * float(self.level) * float(self.star),
            'total_color_star': float(self.color) * float(self.star),
            'total_colors': float(self.color),
            'total_colors2': float(self.color ** 2),
            'total_heroes': 1.0,
            'total_level_star': float(self.level) * float(self.star),
            'total_levels': float(self.level),
            'total_levels2': float(self.level ** 2),
            'total_stars': float(self.star),
            'total_stars2': float(self.star ** 2),
            **{f'artifact_level_{self.id}_{i}': artifact['level'] for i, artifact in enumerate(self.artifacts)},
            **{f'artifact_star_{self.id}_{i}': artifact['star'] for i, artifact in enumerate(self.artifacts)},
            **{f'rune_{self.id}_{i}': float(level) for i, level in enumerate(self.runes)},
            **{f'skill_{self.id}_{skill_id}': float(level) for skill_id, level in self.skills.items()},
            **{f'slot_{self.id}_{n_slot}': 1.0 for n_slot in self.slots},
            f'color_level_star_{self.id}': float(self.color) * float(self.level) * float(self.star),
            f'color_level_{self.id}': float(self.color) * float(self.level),
            f'color_star_{self.id}': float(self.color) * float(self.star),
            f'color_{self.id}': float(self.color),
            f'level_star_{self.id}': float(self.level) * float(self.star),
            f'level_{self.id}': float(self.level),
            f'skin_{self.id}': float(self.skin_level),
            f'star_{self.id}': float(self.star),
            f'titan_gift_level_{self.id}': float(self.titan_gift_level or 0.0),
        }

    @property
    def skin_level(self) -> int:
        return self.skins.get(self.current_skin, 0)

    def __lt__(self, other: Any) -> Any:
        if isinstance(other, Hero):
            return (self.star, self.color, self.level) < (other.star, other.color, other.level)
        return NotImplemented

    def __str__(self):
        stars = '🌟' if self.star > 5 else '⭐' * self.star
        return f'{stars} {resources.hero_name(self.id)} ({self.level}) {COLORS.get(self.color, self.color)}'


class BattleResult(BaseModel):
    win: bool
    stars: int = 0

    def __str__(self) -> str:
        return '⭐' * self.stars if self.win else '⛔️'


class Replay(BaseModel):
    id: str
    start_time: datetime
    result: BattleResult
    attackers: Dict[str, Hero]
    defenders: List[Dict[str, Hero]]

    class Config:
        fields = {
            'start_time': 'startTime',
        }


class User(BaseModel):
    id: str
    name: str
    server_id: str
    level: str
    tz: tzinfo = timezone.utc
    next_day: Optional[datetime] = None
    gold: Optional[str] = None
    star_money: Optional[str] = None
    clan_id: Optional[str] = None
    clan_title: Optional[str] = None

    class Config:
        fields = {
            'clan_id': 'clanId',
            'clan_title': 'clanTitle',
            'next_day': 'nextDayTs',
            'server_id': 'serverId',
            'star_money': 'starMoney',
            'tz': 'timeZone',
        }

    def is_from_clans(self, clans: Iterable[str]) -> bool:
        return (self.clan_id and self.clan_id in clans) or (self.clan_title and self.clan_title in clans)

    def __str__(self) -> str:
        return f'«{self.name}» from «{self.clan_title}»'


class BaseArenaEnemy(BaseModel, ABC):
    user_id: str
    place: str
    power: int
    user: Optional[User] = None

    class Config:
        fields = {
            'user_id': 'userId',
        }

    @property
    def teams(self) -> List[List[Hero]]:
        raise NotImplementedError()

    def __str__(self) -> str:
        return f'{self.user} at place {self.place}'


class ArenaEnemy(BaseArenaEnemy):
    heroes: List[Hero]

    @property
    def teams(self) -> List[List[Hero]]:
        return [self.heroes]


class GrandArenaEnemy(BaseArenaEnemy):
    heroes: List[List[Hero]]

    @property
    def teams(self) -> List[List[Hero]]:
        return self.heroes


class ArenaState(BaseModel, Loggable):
    battles: int
    wins: int
    arena_place: Optional[str] = None
    grand_place: Optional[str] = None

    class Config:
        fields = {
            'arena_place': 'arenaPlace',
            'grand_place': 'grandPlace',
        }

    @property
    def plain_text(self) -> Iterable[str]:
        if self.arena_place:
            yield f'Place: {self.arena_place}.'
        if self.grand_place:
            yield f'Grand place: {self.grand_place}.'
        yield f'Battles: {self.battles}. Wins: {self.wins}.'
        yield f'Rating: {100.0 * (self.wins / self.battles):.2f}%.'

    @property
    def markdown(self) -> Iterable[str]:
        if self.arena_place:
            yield f'Место на арене: *{self.arena_place}*'
        if self.grand_place:
            yield f'Место на гранд-арене: *{self.grand_place}*'
        yield f'Рейтинг: *{100.0 * (self.wins / self.battles):.2f}%*'


class ArenaResult(BaseModel, Loggable):
    win: bool
    battles: List[Replay]
    reward: Optional[Reward]
    state: ArenaState

    @property
    def plain_text(self) -> Iterable[str]:
        yield 'You won!' if self.win else 'You lose.'
        for i, battle in enumerate(self.battles, start=1):
            yield f'Battle #{i}: {battle.result}'
        if self.reward is not None:
            yield from self.reward.plain_text
        yield from self.state.plain_text

    @property
    def markdown(self):
        yield '*Победа* 😉' if self.win else '*Поражение* 😕'
        yield ''
        for i, battle in enumerate(self.battles, start=1):
            yield f'Бой #{i}: {battle.result}'
        yield ''
        if self.reward is not None:
            yield from self.reward.markdown
            yield ''
        yield from self.state.markdown

    # noinspection PyMethodParameters
    @validator('reward', pre=True)
    def fix_reward(cls, value: Any) -> Optional[Reward]:
        # They return the empty list in case of an empty reward. 🤦
        return value or None


class Offer(BaseModel):
    id: str
    is_free_reward_obtained: bool = False
    offer_type: str = ''

    class Config:
        fields = {
            'is_free_reward_obtained': 'freeRewardObtained',
            'offer_type': 'offerType',
        }


class Mission(BaseModel):
    id: str
    tries_spent: int
    stars: int

    class Config:
        fields = {
            'tries_spent': 'triesSpent',
        }

    @property
    def is_raid_available(self) -> bool:
        return self.stars == RAID_N_STARS


class Tower(BaseModel):
    floor_number: int
    may_skip_floor: int
    may_full_skip: bool
    floor_type: TowerFloorType
    floor: Any = []  # cannot assume any specific type because it depends on the current floor type 🤦‍

    class Config:
        fields = {
            'floor_number': 'floorNumber',
            'may_skip_floor': 'maySkipFloor',
            'may_full_skip': 'mayFullSkip',
            'floor_type': 'floorType',
        }


class Cost(BaseModel):
    star_money: int = 0

    class Config:
        fields = {
            'star_money': 'starmoney',
        }


class ShopSlot(BaseModel):
    id: str
    is_bought: bool
    reward: Reward
    cost: Cost

    class Config:
        fields = {
            'is_bought': 'bought',
        }


class Boss(BaseModel):
    id: str
    may_raid: bool

    class Config:
        fields = {
            'may_raid': 'mayRaid',
        }


class Expedition(BaseModel):
    id: str
    status: int
    power: int
    duration: timedelta
    hero_ids: List[str]
    end_time: Optional[datetime] = None

    class Config:
        fields = {
            'end_time': 'endTime',
            'hero_ids': 'heroes',
        }

    @property
    def is_available(self) -> bool:
        return self.status == 1

    @property
    def is_started(self) -> bool:
        return self.status == 2


class Quest(BaseModel):
    id: str
    state: int
    progress: int
    reward: Reward

    @property
    def is_reward_available(self) -> bool:
        return self.state == 2


class HallOfFameTrophy(BaseModel):
    week: str


class HallOfFame(BaseModel):
    trophy: Optional[HallOfFameTrophy]

    # noinspection PyMethodParameters
    @validator('trophy', pre=True)
    def fix_trophy(cls, value):
        # They return the empty list in case of an empty reward. 🤦
        return value or None


class Result(BaseModel):
    """
    Top-most result class.
    """

    response: Any
    quests: List[Quest] = []

    @property
    def is_error(self) -> bool:
        return self.response and isinstance(self.response, dict) and 'error' in self.response


Quests = List[Quest]

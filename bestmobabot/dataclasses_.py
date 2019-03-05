from __future__ import annotations

from datetime import datetime, timedelta, timezone, tzinfo
from functools import total_ordering
from typing import Any, Dict, Iterable, List, Optional, Set

from loguru import logger
from pydantic import BaseModel, validator
from pydantic.validators import _VALIDATORS

from bestmobabot import resources
from bestmobabot.constants import COLORS, RAID_N_STARS
from bestmobabot.enums import DungeonDefenderType, DungeonFloorType, TowerFloorType

_VALIDATORS.append((tzinfo, [lambda value: timezone(timedelta(hours=value))]))


class Reward(BaseModel):
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

    @property
    def keywords(self) -> Set[str]:
        return {
            *(resources.consumable_name(consumable_id).lower() for consumable_id in self.consumable),
            *(resources.gear_name(gear_id).lower() for gear_id in self.gear),
            *(resources.gear_name(gear_id).lower() for gear_id in self.gear_fragment),
            *(resources.hero_name(hero_id).lower() for hero_id in self.hero_fragment),
            *(resources.scroll_name(scroll_id).lower() for scroll_id in self.scroll_fragment),
        }

    def log(self):
        if self.stamina:
            logger.success(f'{self.stamina} × stamina.')
        if self.gold:
            logger.success(f'{self.gold} × gold.')
        if self.experience:
            logger.success(f'{self.experience} × experience.')
        if self.star_money:
            logger.success(f'{self.star_money} × star money.')
        if self.dungeon_activity:
            logger.success(f'{self.dungeon_activity} × dungeon activity.')
        for consumable_id, value in self.consumable.items():
            logger.success(f'{value} × «{resources.consumable_name(consumable_id)}» consumable.')
        for coin_id, value in self.coin.items():
            logger.success(f'{value} × «{resources.coin_name(coin_id)}» coin.')
        for hero_id, value in self.hero_fragment.items():
            logger.success(f'{value} × «{resources.hero_name(hero_id)}» hero fragment.')
        for artifact_id, value in self.artifact_fragment.items():
            logger.success(f'{value} × «{resources.artifact_name(artifact_id)}» artifact fragment.')
        for gear_id, value in self.gear_fragment.items():
            logger.success(f'{value} × «{resources.gear_name(gear_id)}» gear fragment.')
        for gear_id, value in self.gear.items():
            logger.success(f'{value} × «{resources.gear_name(gear_id)}» gear.')
        for scroll_id, value in self.scroll_fragment.items():
            logger.success(f'{value} × «{resources.scroll_name(scroll_id)}» scroll fragment.')
        for artifact_id, value in self.titan_artifact_fragment.items():
            logger.success(f'{value} × «{resources.titan_artifact_name(artifact_id)}» titan artifact fragment.')
        for hero_id, value in self.titan_fragment.items():
            logger.success(f'{value} × «{resources.hero_name(hero_id)}» titan fragment.')


class LibraryMission(BaseModel):
    id: str
    is_heroic: bool

    class Config:
        fields = {'is_heroic': 'isHeroic'}


class Library(BaseModel):
    missions: Dict[str, LibraryMission]

    class Config:
        fields = {'missions': 'mission'}


class Letter(BaseModel):
    id: str


@total_ordering
class Hero(BaseModel):
    id: str
    level: int
    color: int
    star: int
    power: Optional[int] = None  # TODO: move out to a common base for `Hero` and `Titan`.

    @property
    def features(self) -> Dict[str, float]:
        return {
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

    def __lt__(self, other: Any) -> Any:
        if isinstance(other, Hero):
            return (self.star, self.color, self.level) < (other.star, other.color, other.level)
        return NotImplemented

    def __str__(self):
        stars = '🌟' if self.star > 5 else '⭐' * self.star
        return f'{stars} {resources.hero_name(self.id)} ({self.level}) {COLORS.get(self.color, self.color)}'


Team = List[Hero]
Teams = List[Team]


class BattleResult(BaseModel):
    win: bool
    stars: int = 0


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


class BaseArenaEnemy(BaseModel):
    user_id: str
    place: str
    power: int
    user: Optional[User] = None

    class Config:
        fields = {
            'user_id': 'userId',
        }

    @property
    def teams(self) -> Teams:
        raise NotImplementedError()

    def __str__(self) -> str:
        return f'{self.user} at place {self.place}'


class ArenaEnemy(BaseArenaEnemy):
    heroes: List[Hero]

    @property
    def teams(self) -> Teams:
        return [self.heroes]


class GrandArenaEnemy(BaseArenaEnemy):
    heroes: List[List[Hero]]

    @property
    def teams(self) -> Teams:
        return self.heroes


class ArenaState(BaseModel):
    battles: int
    wins: int
    arena_place: Optional[str] = None
    grand_place: Optional[str] = None

    class Config:
        fields = {
            'arena_place': 'arenaPlace',
            'grand_place': 'grandPlace',
        }

    def log(self):
        if self.arena_place:
            logger.success('Place: {}.', self.arena_place)
        if self.grand_place:
            logger.success('Grand place: {}.', self.grand_place)
        logger.success('Battles: {}. Wins: {}.', self.battles, self.wins)
        logger.success('Rating: {:.2f}%.', 100.0 * (self.wins / self.battles))


class ArenaResult(BaseModel):
    win: bool
    battles: List[Replay]
    reward: Optional[Reward]
    state: ArenaState

    # noinspection PyMethodParameters
    @validator('reward', pre=True)
    def fix_reward(cls, value: Any) -> Optional[Reward]:
        # They return the empty list in case of an empty reward. 🤦
        return value or None

    def log(self):
        logger.info('You won!' if self.win else 'You lose.')
        for i, battle in enumerate(self.battles, start=1):
            logger.info(f'Battle #{i}: {"⭐" * battle.result.stars if battle.result.win else "➖"}')
        if self.reward is not None:
            self.reward.log()
        self.state.log()


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


class DungeonUserData(BaseModel):
    defender_type: DungeonDefenderType
    attacker_type: DungeonDefenderType

    class Config:
        fields = {
            'attacker_type': 'attackerType',
            'defender_type': 'defenderType',
        }


class DungeonFloor(BaseModel):
    user_data: List[DungeonUserData]
    state: int

    class Config:
        fields = {
            'user_data': 'userData',
        }

    @property
    def should_save_progress(self) -> bool:
        return self.state == 2


class Dungeon(BaseModel):
    floor_number: int
    floor_type: DungeonFloorType
    floor: DungeonFloor

    class Config:
        fields = {
            'floor_number': 'floorNumber',
            'floor_type': 'floorType',
        }


class EndDungeonBattleResponse(BaseModel):
    reward: Reward
    reward_multiplier: int
    activity: int
    dungeon: Optional[Dungeon]

    class Config:
        fields = {
            'reward_multiplier': 'rewardMultiplier',
            'activity': 'dungeonActivity',
        }


class SaveDungeonProgressResponse(BaseModel):
    reward: Reward
    dungeon: Dungeon


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

"""
Game API response wrappers.
"""

from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any, Dict, List, NamedTuple, Optional

from bestmobabot import types
from bestmobabot.logger import logger
from bestmobabot.resources import COLORS, NAMES


class Response(NamedTuple):
    quests: 'Quests'
    payload: Any

    @staticmethod
    def parse(item: Dict) -> 'Response':
        return Response(
            payload=item['response'],
            quests=list(map(Quest.parse, item.get('quests', []))),
        )


class User(NamedTuple):
    id: types.UserID
    name: str
    tz: tzinfo
    clan_id: types.ClanID
    next_day: datetime
    item: Dict

    @staticmethod
    def parse(item: Dict) -> 'User':
        tz = timezone(timedelta(hours=item.get('timeZone', 0)))
        return User(
            item=item,
            id=str(item['id']),
            name=item['name'],
            tz=tz,
            clan_id=item.get('clanId'),
            next_day=datetime.fromtimestamp(item.get('nextDayTs', 0), tz),
        )

    def is_from_clan(self, clan_id: Optional[str]) -> bool:
        return clan_id and self.clan_id and self.clan_id == clan_id


class Expedition(NamedTuple):
    id: types.ExpeditionID
    status: int
    end_time: Optional[datetime]
    power: int
    duration: timedelta
    hero_ids: types.HeroIDs

    @staticmethod
    def parse(item: Dict) -> 'Expedition':
        end_time = datetime.fromtimestamp(item['endTime']).astimezone() if item.get('endTime') else None
        return Expedition(
            id=str(item['id']),
            status=item['status'],
            end_time=end_time,
            power=item['power'],
            duration=timedelta(seconds=item['duration']),
            hero_ids=[str(hero_id) for hero_id in item.get('heroes', [])],
        )

    @property
    def is_available(self) -> bool:
        return self.status == 1

    @property
    def is_started(self) -> bool:
        return self.status == 2


class Reward(NamedTuple):
    stamina: types.Stamina
    gold: types.Gold
    experience: types.Experience
    consumable: Dict[str, int]
    star_money: types.StarMoney
    coin: Dict[str, str]
    hero_fragment: Dict[types.HeroID, int]
    artifact_fragment: Dict[str, int]
    gear_fragment: Dict[str, int]

    @staticmethod
    def parse(item: Dict) -> 'Reward':
        return Reward(
            stamina=item.get('stamina', 0),
            gold=item.get('gold', 0),
            experience=item.get('experience', 0),
            consumable=item.get('consumable', {}),
            star_money=item.get('starmoney', 0),
            coin=item.get('coin', {}),
            hero_fragment=item.get('fragmentHero', {}),
            artifact_fragment=item.get('fragmentArtifact', {}),
            gear_fragment=item.get('fragmentGear', {}),
        )


class Quest(NamedTuple):
    id: types.QuestID
    state: types.QuestState
    progress: int
    reward: Reward

    @staticmethod
    def parse(item: Dict) -> 'Quest':
        return Quest(
            id=str(item['id']),
            state=item['state'],
            progress=item['progress'],
            reward=Reward.parse(item['reward']),
        )

    @property
    def is_reward_available(self) -> bool:
        return self.state == 2


Quests = List[Quest]


class Letter(NamedTuple):
    id: types.LetterID

    @staticmethod
    def parse(item: Dict) -> 'Letter':
        return Letter(id=str(item['id']))


class Hero(NamedTuple):
    id: types.HeroID
    level: int
    color: int
    star: int
    power: Optional[int]
    item: Dict

    @staticmethod
    def parse(item: Dict) -> 'Hero':
        return Hero(
            id=str(item['id']),
            level=item['level'],
            color=item['color'],
            star=item['star'],
            power=item.get('power'),
            item=item,
        )

    def dump(self) -> dict:
        return {
            'id': self.id,
            'level': self.level,
            'color': self.color,
            'star': self.star,
        }

    @property
    def features(self):
        return {
            f'color_{self.id}': self.color,
            f'level_{self.id}': self.level,
            f'star_{self.id}': self.star,
        }

    def __str__(self):
        return f'{"⭐" * self.star} {NAMES.get(self.id, self.id)} ~{self.level}~ {COLORS.get(self.color, self.color)}'


class ArenaEnemy(NamedTuple):
    user_id: types.UserID
    place: str
    heroes: List[Hero]
    power: int
    user: Optional[User]

    @staticmethod
    def parse(item: Dict) -> 'ArenaEnemy':
        # Somehow some enemies have no user.
        user = User.parse(item['user']) if item.get('user') else None
        if user is None:
            logger.warning('🤔 Arena enemy have no user.')
        return ArenaEnemy(
            user_id=str(item['userId']),
            place=item['place'],
            heroes=list(map(Hero.parse, item['heroes'])),
            power=int(item['power']),
            user=user,
        )


class ArenaResult(NamedTuple):
    win: bool
    battles: List['BattleResult']
    reward: Reward

    @staticmethod
    def parse(item: Dict) -> 'ArenaResult':
        return ArenaResult(
            win=item['win'],
            battles=list(map(BattleResult.parse, item['battles'])),
            reward=Reward.parse(item['reward'] or {}),
        )


class BattleResult(NamedTuple):
    win: bool
    stars: int
    old_place: str
    new_place: str

    @staticmethod
    def parse(item: Dict) -> 'BattleResult':
        result = item['result']
        return BattleResult(
            win=result['win'],
            stars=result.get('stars', 0),
            old_place=result.get('oldPlace'),
            new_place=result.get('newPlace'),
        )


class Freebie(NamedTuple):
    reward: Reward

    @staticmethod
    def parse(item: Dict) -> 'Freebie':
        return Freebie(
            reward=Reward.parse(item['reward']),
        )


class Boss(NamedTuple):
    id: types.BossID

    @staticmethod
    def parse(item: Dict) -> 'Boss':
        return Boss(id=str(item['id']))


class Battle(NamedTuple):
    seed: int

    @staticmethod
    def parse(item: Dict) -> 'Battle':
        return Battle(seed=item['seed'])


class Replay(NamedTuple):
    id: types.ReplayID
    win: bool
    stars: int
    attackers: List[Hero]
    defenders: List[List[Hero]]

    @staticmethod
    def parse(item: Dict) -> 'Replay':
        return Replay(
            id=item['id'],
            win=item['result']['win'],
            stars=item['result']['stars'],
            attackers=list(map(Hero.parse, item['attackers'].values())),
            defenders=[list(map(Hero.parse, defenders.values())) for defenders in item['defenders']],
        )

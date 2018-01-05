from datetime import timedelta, timezone
from typing import Dict, List, NamedTuple

from bestmobabot.types import *


class User(NamedTuple):
    account_id: UserID
    name: str
    time_zone: timezone

    @staticmethod
    def parse(item: Dict) -> 'User':
        return User(
            account_id=UserID(item['accountId']),
            name=item['name'],
            time_zone=timezone(timedelta(hours=item.get('timeZone', 0))),
        )


class Expedition(NamedTuple):
    id: ExpeditionID
    status: int

    @staticmethod
    def parse(item: Dict) -> 'Expedition':
        return Expedition(
            id=ExpeditionID(item['id']),
            status=ExpeditionStatus(item['status']),
        )


class Reward(NamedTuple):
    stamina: Stamina
    gold: Gold
    experience: Experience
    consumable: Dict[str, int]
    star_money: StarMoney
    coin: Dict[str, str]
    hero_fragment: Dict[str, int]

    @staticmethod
    def parse(item: Dict) -> 'Reward':
        return Reward(
            stamina=Stamina(item.get('stamina', 0)),
            gold=Gold(item.get('gold', 0)),
            experience=Experience(item.get('experience', 0)),
            consumable=item.get('consumable', {}),
            star_money=StarMoney(item.get('starmoney', 0)),
            coin=item.get('coin', {}),
            hero_fragment=item.get('fragmentHero', {}),
        )


class Quest(NamedTuple):
    id: QuestID
    state: QuestState
    progress: int
    reward: Reward

    @staticmethod
    def parse(item: Dict) -> 'Quest':
        return Quest(
            id=QuestID(item['id']),
            state=QuestState(item['state']),
            progress=item['progress'],
            reward=Reward.parse(item['reward']),
        )


class Letter(NamedTuple):
    id: str

    @staticmethod
    def parse(item: Dict) -> 'Letter':
        return Letter(id=item['id'])


class Hero(NamedTuple):
    id: HeroID
    level: int
    color: int
    star: int

    @staticmethod
    def parse(item: Dict) -> 'Hero':
        return Hero(id=HeroID(item['id']), level=item['level'], color=item['color'], star=item['star'])


class ArenaEnemy(NamedTuple):
    user_id: UserID
    place: str
    heroes: List[Hero]
    power: str
    user: User

    @staticmethod
    def parse(item: Dict) -> 'ArenaEnemy':
        return ArenaEnemy(
            user_id=UserID(item['userId']),
            place=item['place'],
            heroes=list(map(Hero.parse, item['heroes'])),
            power=item['power'],
            user=User.parse(item['user']),
        )

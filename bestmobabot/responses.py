from datetime import timedelta, timezone
from typing import Dict, NamedTuple

from bestmobabot.types import *


class UserInfo(NamedTuple):
    account_id: str
    name: str
    time_zone: timezone

    @staticmethod
    def parse(item: Dict) -> 'UserInfo':
        return UserInfo(
            account_id=item['accountId'],
            name=item['name'],
            time_zone=timezone(timedelta(hours=item['timeZone'])),
        )


class Expedition(NamedTuple):
    id: ExpeditionId
    status: int

    @staticmethod
    def parse(item: Dict) -> 'Expedition':
        return Expedition(
            id=ExpeditionId(item['id']),
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
    id: QuestId
    state: QuestState
    progress: int
    reward: Reward

    @staticmethod
    def parse(item: Dict) -> 'Quest':
        return Quest(
            id=QuestId(item['id']),
            state=QuestState(item['state']),
            progress=item['progress'],
            reward=Reward.parse(item['reward']),
        )


class Letter(NamedTuple):
    id: str

    @staticmethod
    def parse(item: Dict) -> 'Letter':
        return Letter(id=item['id'])

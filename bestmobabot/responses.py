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
    id: int
    status: int

    @staticmethod
    def parse(item: Dict) -> 'Expedition':
        return Expedition(
            id=item['id'],
            status=ExpeditionStatus(item['status']),
        )


class Reward(NamedTuple):
    stamina: int
    gold: int
    experience: int
    consumable: Dict[str, int]
    starmoney: int
    coin: Dict[str, str]

    @staticmethod
    def parse(item: Dict) -> 'Reward':
        return Reward(
            stamina=item.get('stamina', 0),
            gold=item.get('gold', 0),
            experience=item.get('experience', 0),
            consumable=item.get('consumable', {}),
            starmoney=item.get('starmoney', 0),
            coin=item.get('coin', {}),
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

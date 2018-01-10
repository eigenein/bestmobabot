from datetime import timedelta, timezone, tzinfo
from typing import Any, Dict, List, NamedTuple, Optional

from bestmobabot.logger import logger
from bestmobabot.types import *  # FIXME


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
    id: UserID
    name: str
    tz: tzinfo
    clan_id: ClanID
    item: Dict

    @staticmethod
    def parse(item: Dict) -> 'User':
        return User(
            item=item,
            id=str(item['id']),
            name=item['name'],
            tz=timezone(timedelta(hours=item.get('timeZone', 0))),
            clan_id=item.get('clanId'),
        )

    def is_from_clan(self, clan_id: Optional[str]) -> bool:
        return clan_id and self.clan_id and self.clan_id == clan_id


class Expedition(NamedTuple):
    id: ExpeditionID
    status: int

    @staticmethod
    def parse(item: Dict) -> 'Expedition':
        return Expedition(
            id=str(item['id']),
            status=ExpeditionStatus(item['status']),
        )


class Reward(NamedTuple):
    stamina: Stamina
    gold: Gold
    experience: Experience
    consumable: Dict[str, int]
    star_money: StarMoney
    coin: Dict[str, str]
    hero_fragment: Dict[HeroID, int]
    artifact_fragment: Dict[str, int]

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
            artifact_fragment=item.get('fragmentArtifact', {}),
        )


class Quest(NamedTuple):
    id: QuestID
    state: QuestState
    progress: int
    reward: Reward

    @staticmethod
    def parse(item: Dict) -> 'Quest':
        return Quest(
            id=str(item['id']),
            state=QuestState(item['state']),
            progress=item['progress'],
            reward=Reward.parse(item['reward']),
        )


Quests = List[Quest]


class Letter(NamedTuple):
    id: LetterID

    @staticmethod
    def parse(item: Dict) -> 'Letter':
        return Letter(id=str(item['id']))


class Hero(NamedTuple):
    id: HeroID
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


class ArenaEnemy(NamedTuple):
    user_id: UserID
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
    battles: List['Battle']

    @staticmethod
    def parse(item: Dict) -> 'ArenaResult':
        return ArenaResult(
            win=item['win'],
            battles=list(map(Battle.parse, item['battles'])),
        )


class Battle(NamedTuple):
    win: bool
    stars: int
    old_place: str
    new_place: str

    @staticmethod
    def parse(item: Dict) -> 'Battle':
        result = item['result']
        return Battle(
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

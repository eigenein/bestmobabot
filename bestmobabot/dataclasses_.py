from typing import Dict, List, Set

from loguru import logger
from pydantic import BaseModel

from bestmobabot import resources


class Reward(BaseModel):
    artifact_fragment: Dict[str, int] = {}
    coin: Dict[str, str] = {}
    consumable: Dict[str, int] = {}
    experience: int = 0
    gear: Dict[str, int] = {}
    gear_fragment: Dict[str, int] = {}
    gold: int = 0
    hero_fragment: Dict[str, int] = {}
    scroll_fragment: Dict[str, int] = {}
    stamina: int = 0
    star_money: int = 0
    titan_artifact_fragment: Dict[str, int] = {}
    tower_point: int = 0

    class Config:
        fields = {
            'artifact_fragment': 'fragmentArtifact',
            'gear_fragment': 'fragmentGear',
            'hero_fragment': 'fragmentHero',
            'scroll_fragment': 'fragmentScroll',
            'star_money': 'starmoney',
            'titan_artifact_fragment': 'fragmentTitanArtifact',
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
            logger.info(f'{self.stamina} × stamina.')
        if self.gold:
            logger.info(f'{self.gold} × gold.')
        if self.experience:
            logger.info(f'{self.experience} × experience.')
        for consumable_id, value in self.consumable.items():
            logger.info(f'{value} × «{resources.consumable_name(consumable_id)}» consumable.')
        if self.star_money:
            logger.info(f'{self.star_money} × star money.')
        for coin_id, value in self.coin.items():
            logger.info(f'{value} × «{resources.coin_name(coin_id)}» coin.')
        for hero_id, value in self.hero_fragment.items():
            logger.info(f'{value} × «{resources.hero_name(hero_id)}» hero fragment.')
        for artifact_id, value in self.artifact_fragment.items():
            logger.info(f'{value} × «{resources.artifact_name(artifact_id)}» artifact fragment.')
        for gear_id, value in self.gear_fragment.items():
            logger.info(f'{value} × «{resources.gear_name(gear_id)}» gear fragment.')
        for gear_id, value in self.gear.items():
            logger.info(f'{value} × «{resources.gear_name(gear_id)}» gear.')
        for scroll_id, value in self.scroll_fragment.items():
            logger.info(f'{value} × «{resources.scroll_name(scroll_id)}» scroll fragment.')
        for artifact_id, value in self.titan_artifact_fragment.items():
            logger.info(f'{value} × «{resources.titan_artifact_name(artifact_id)}» titan artifact fragment.')


class MissionEnemyDrop(BaseModel):
    reward: Reward


class MissionEnemy(BaseModel):
    drops: List[MissionEnemyDrop] = []

    class Config:
        fields = {'drops': 'drop'}


class MissionWave(BaseModel):
    enemies: List[MissionEnemy]


class MissionMode(BaseModel):
    waves: List[MissionWave]


class Mission(BaseModel):
    id: str
    is_heroic: bool
    normal_mode: MissionMode

    class Config:
        fields = {'is_heroic': 'isHeroic', 'normal_mode': 'normalMode'}


class Library(BaseModel):
    missions: Dict[str, Mission]

    class Config:
        fields = {'missions': 'mission'}

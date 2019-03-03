from enum import Enum


class BattleType(Enum):
    ARENA = 'arena'
    GRAND = 'grand'


class HeroesJSMode(Enum):
    TITAN = 'titan'
    TOWER = 'tower'


class TowerFloorType(Enum):
    BATTLE = 'battle'
    BUFF = 'buff'
    CHEST = 'chest'


class DungeonFloorType(Enum):
    BATTLE = 'battle'


class DungeonDefenderType(Enum):
    EARTH = 'earth'
    FIRE = 'fire'
    HERO = 'hero'
    NEUTRAL = 'neutral'
    WATER = 'water'

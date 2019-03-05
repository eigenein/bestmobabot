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


class DungeonUnitType(Enum):
    EARTH = 'earth'
    FIRE = 'fire'
    HERO = 'hero'
    NEUTRAL = 'neutral'
    WATER = 'water'


class LibraryTitanElement(Enum):
    EARTH = 'earth'
    FIRE = 'fire'
    WATER = 'water'


class LibraryTitanType(Enum):
    MELEE = 'melee'
    SUPPORT = 'support'
    RANGE = 'range'
    ULTRA = 'ultra'

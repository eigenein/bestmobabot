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
    UNKNOWN = 'unknown'

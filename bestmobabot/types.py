"""
Game API parameter types.
"""

from enum import Enum
from typing import NewType

BossID = NewType('BossID', str)
ClanID = NewType('ClanID', str)
ConsumableID = NewType('ConsumableID', str)
ExpeditionID = NewType('ExpeditionID', str)
ExpeditionStatus = NewType('ExpeditionStatus', int)
Experience = NewType('Experience', int)
Gold = NewType('Gold', int)
HeroID = NewType('HeroID', str)
LetterID = NewType('LetterID', str)
MissionID = NewType('MissionID', str)
QuestID = NewType('QuestID', str)
QuestState = NewType('QuestState', int)
ReplayID = NewType('ReplayID', str)
ShopID = NewType('ShopID', str)
SlotID = NewType('SlotID', str)
Stamina = NewType('Stamina', int)
StarMoney = NewType('StarMoney', int)
UserID = NewType('UserID', str)


class BattleType(Enum):
    ARENA = 'arena'
    GRAND = 'grand'


__all__ = [
    'BossID',
    'ClanID',
    'ConsumableID',
    'ExpeditionID',
    'ExpeditionStatus',
    'Experience',
    'Gold',
    'HeroID',
    'LetterID',
    'MissionID',
    'QuestID',
    'QuestState',
    'ReplayID',
    'ShopID',
    'SlotID',
    'Stamina',
    'StarMoney',
    'UserID',
    'BattleType',
]

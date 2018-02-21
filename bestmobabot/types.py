"""
Game API parameter types.
"""

from typing import Iterable, NewType

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
Stamina = NewType('Stamina', int)
StarMoney = NewType('StarMoney', int)
UserID = NewType('UserID', str)

HeroIDs = Iterable[HeroID]

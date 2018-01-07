from datetime import timedelta

from bestmobabot import types


EXPEDITION_COLLECT_REWARD = types.ExpeditionStatus(2)
EXPEDITION_FINISHED = types.ExpeditionStatus(3)

QUEST_IN_PROGRESS = types.QuestState(1)
QUEST_COLLECT_REWARD = types.QuestState(2)

DAY = timedelta(days=1)

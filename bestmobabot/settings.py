from __future__ import annotations

import os
from datetime import timedelta
from typing import List, Optional, Set, Type, TypeVar

import click
import yaml
from pydantic import BaseModel, ValidationError, confloat, conint, validator

from bestmobabot import constants


class VKSettings(BaseModel):
    email: str
    password: str
    access_token: str  # VK.com API access token


class TelegramSettings(BaseModel):
    token: str  # Telegram bot authentication token
    chat_id: str  # Telegram chat ID


class ArenaSettings(BaseModel):
    # Shared settings.
    schedule_offset: timedelta = timedelta()  # arena task schedule offset
    friendly_clans: Set[str] = []  # names or clan IDs which must be skipped during enemy search
    early_stop: confloat(ge=0.0, le=1.0) = 0.95  # minimal win probability to stop enemy search
    last_battles: conint(ge=1) = constants.MODEL_N_LAST_BATTLES  # use last N battles for training

    # Normal arena.
    normal_max_pages: conint(ge=1) = 15  # maximal number of pages during normal enemy search
    normal_generations_count_down: conint(ge=1) = 25
    normal_generate_solutions: conint(ge=1) = 100
    normal_keep_solutions: conint(ge=1) = 50

    # Grand arena.
    grand_max_pages: conint(ge=1) = 15  # maximal number of pages during grand enemy search
    grand_generations_count_down: conint(ge=1) = 50  # maximum number of GA iterations without any improvement
    grand_generate_solutions: conint(ge=1) = 500
    grand_keep_solutions: conint(ge=1) = 50
    randomize_grand_defenders: bool = False


class EnchantRuneSettings(BaseModel):
    hero_id: str
    tier: str


# noinspection PyMethodParameters
class BotSettings(BaseModel):
    debug: bool = False
    no_experience: bool = False  # don't farm experience quests
    is_trainer: bool = False  # train the model
    raid_missions: Set[str] = []  # mission names to raid
    shops: Set[str] = []  # bought item names
    friend_ids: List[str] = []  # friend IDs for gifts
    enchant_rune: Optional[EnchantRuneSettings] = None
    arena: ArenaSettings

    @validator('raid_missions', each_item=True)
    def lower_raids(cls, value: str) -> str:
        return value.lower()

    @validator('shops', each_item=True)
    def lower_shops(cls, value: str) -> str:
        return value.lower()


# TODO: unit tests.
class Settings(BaseModel):
    vk: VKSettings
    bot: BotSettings
    telegram: Optional[TelegramSettings]


class SettingsFileParamType(click.ParamType):
    name = 'filename'

    TModel = TypeVar('TModel', bound=BaseModel)

    def __init__(self, model: Type[TModel]):
        self.model_class = model
        self.file_param = click.File()

    def convert(self, value, param, ctx) -> TModel:
        fp = self.file_param.convert(value, param, ctx)
        try:
            raw = yaml.load(fp, Loader=yaml.FullLoader)
        except yaml.YAMLError as e:
            self.fail(f'{os.linesep}{e}', param, ctx)
        try:
            # noinspection PyCallingNonCallable
            return self.model_class.parse_obj(raw)
        except ValidationError as e:
            self.fail(str(e), param, ctx)

import os
from datetime import timedelta
from typing import List, Set, Type, TypeVar

import click
import yaml
from pydantic import BaseModel, ValidationError, confloat, conint, validator

from bestmobabot import constants


class VKSettings(BaseModel):
    remixsid: str  # VK.com remixsid cookie
    access_token: str  # VK.com API access token


class ArenaSettings(BaseModel):
    skip_clans: Set[str] = []  # names or clan IDs which must be skipped during enemy search
    early_stop: confloat(ge=0.0, le=1.0) = 0.95  # minimal win probability to stop enemy search
    schedule_offset: timedelta = timedelta()  # arena task schedule offset
    teams_limit: conint(ge=1) = 20000  # number of the most powerful teams tested
    grand_generations_cool_down: conint(ge=1) = 25  # maximum number of GA iterations without any improvement
    max_pages: conint(ge=1) = 15  # maximal number of pages during enemy search
    max_grand_pages: conint(ge=1) = 15  # maximal number of pages during grand enemy search
    randomize_grand_defenders: bool = False
    grand_generate_solutions: conint(ge=1) = 1250
    grand_keep_solutions: conint(ge=1) = 250
    last_battles: conint(ge=1) = constants.MODEL_N_LAST_BATTLES  # use last N battles for training


# noinspection PyMethodParameters
class BotSettings(BaseModel):
    no_experience: bool = False  # don't farm experience quests
    is_trainer: bool = False  # train the model
    raid_missions: Set[str] = []  # mission names to raid
    shops: Set[str] = []  # bought item names
    friend_ids: List[str] = []  # friend IDs for gifts
    arena: ArenaSettings

    @validator('raid_missions')
    def lower_raids(cls, value: str) -> str:
        return value.lower()

    @validator('shops')
    def lower_shops(cls, value: str) -> str:
        return value.lower()


class Settings(BaseModel):
    vk: VKSettings
    bot: BotSettings


class SettingsFileParamType(click.ParamType):
    name = 'filename'

    TModel = TypeVar('TModel', bound=BaseModel)

    def __init__(self, model: Type[TModel]):
        self.model_class = model
        self.file_param = click.File()

    def convert(self, value, param, ctx) -> TModel:
        fp = self.file_param.convert(value, param, ctx)
        try:
            raw = yaml.load(fp)
        except yaml.YAMLError as e:
            self.fail(f'{os.linesep}{e}', param, ctx)
        try:
            # noinspection PyCallingNonCallable
            return self.model_class.parse_obj(raw)
        except ValidationError as e:
            self.fail(str(e), param, ctx)

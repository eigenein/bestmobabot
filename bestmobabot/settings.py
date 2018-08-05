import os
from datetime import timedelta
from typing import List, Optional, Set, Type, TypeVar

import click
import yaml
from pydantic import BaseModel, ValidationError, validator


class VKSettings(BaseModel):
    remixsid: str  # VK.com remixsid cookie
    access_token: str  # VK.com API access token


class ArenaSettings(BaseModel):
    skip_clans: Set[str] = []  # names or clan IDs which must be skipped during enemy search
    early_stop: float = 0.95  # minimal win probability to stop enemy search
    schedule_offset: timedelta = timedelta()  # arena task schedule offset
    teams_limit: int = 20000  # number of the most powerful teams tested
    grand_generations: int = 25  # number of grand arena GA iterations
    max_pages: int = 15  # maximal number of pages during enemy search
    max_grand_pages: int = 15  # maximal number of pages during grand enemy search
    hyper_params: Optional[dict] = None  # hyper-parameters of the predictive model

    # noinspection PyMethodParameters
    @validator('early_stop')
    def validate_early_stop(cls, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError('incorrect probability, must be between 0 and 1')
        return value


class ShopSettings(BaseModel):
    shop_id: str  # shop ID
    slot_id: str  # slot ID


class BotSettings(BaseModel):
    no_experience: bool = False  # don't farm experience quests
    is_trainer: bool = False  # train the model
    raids: Set[str] = []  # mission IDs to raid
    shops: List[ShopSettings] = []  # bought items
    friend_ids: List[str] = []  # friend IDs for gifts
    arena: ArenaSettings


class Settings(BaseModel):
    vk: VKSettings
    bot: BotSettings


class SettingsFileParamType(click.ParamType):
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
            return self.model_class(**(raw if isinstance(raw, dict) else {}))
        except ValidationError as e:
            self.fail(str(e), param, ctx)

from __future__ import annotations

from contextlib import AbstractContextManager, suppress
from typing import Any, Optional

from loguru import logger
from requests import Session

from bestmobabot import constants
from bestmobabot.settings import TelegramSettings


class Telegram:
    def __init__(self, session: Session, settings: TelegramSettings):
        self.session = session
        self.token = settings.token
        self.chat_id = settings.chat_id

    def send_message(self, text: str) -> int:
        return self.call('sendMessage', {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'Markdown',
        })['message_id']

    def edit_message_text(self, message_id: int, text: str):
        self.call('editMessageText', {
            'chat_id': self.chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'Markdown',
        })

    def call(self, method: str, json: Any) -> Any:
        response = self.session.post(
            f'https://api.telegram.org/bot{self.token}/{method}',
            json=json,
            timeout=constants.API_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()
        if not result.get('ok'):
            logger.error('Error: {}', result.get('description', 'no description'))
        return result['result']


class Notifier(AbstractContextManager):
    def __init__(self, telegram: Optional[Telegram]):
        self.telegram = telegram
        self.message_id: Optional[int] = None

    def __enter__(self):
        self.reset()

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def reset(self):
        self.message_id = None

    def notify(self, text: str):
        if self.telegram:
            logger.trace('Message ID: {}.', self.message_id)
            with suppress(Exception):
                if self.message_id is not None:
                    self.telegram.edit_message_text(self.message_id, text)
                else:
                    self.message_id = self.telegram.send_message(text)

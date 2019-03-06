from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, List, Optional

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


class TelegramLogger(AbstractContextManager):
    def __init__(self, telegram: Optional[Telegram]):
        self.telegram = telegram
        self.lines: List[str] = []

    def __enter__(self) -> TelegramLogger:
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()

    def append(self, *lines: str) -> TelegramLogger:
        if self.telegram:
            self.lines.extend(lines)
        return self

    def flush(self) -> TelegramLogger:
        if not self.telegram or not self.lines:
            return self
        try:
            self.telegram.send_message('\n'.join(self.lines))
        except Exception as e:
            logger.opt(exception=e).warning('Telegram API error.')
        self.lines.clear()
        return self

"""
VK.com API wrapper.
"""

import contextlib
import re
from typing import Iterable

import requests
from loguru import logger

from bestmobabot import constants
from bestmobabot.settings import Settings


class VK(contextlib.AbstractContextManager):
    URL = 'https://api.vk.com/method/wall.get'
    GIFT_RE = re.compile(r'gift_id=(\w+)')
    VK_CC_RE = re.compile(r'https://vk.cc/\w+')

    def __init__(self, settings: Settings):
        self.session = requests.Session()
        self.params = {
            'access_token': settings.vk.access_token,
            'owner_id': '-116039030',
            'count': '5',
            'v': '5.92',
        }

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.__exit__(exc_type, exc_val, exc_tb)

    def find_gifts(self) -> Iterable[str]:
        logger.info('Checking VK.com gifts…')

        with self.session.get(self.URL, params=self.params, timeout=constants.API_TIMEOUT) as response:
            logger.info('Status: {}.', response.status_code)
            response.raise_for_status()
            payload = response.json()

        for item in payload['response']['items']:
            yield from self.GIFT_RE.findall(item['text'])
            for url in self.VK_CC_RE.findall(item['text']):
                # HEAD is not supported by VK.com.
                with self.session.get(url, stream=True) as response:
                    yield from self.GIFT_RE.findall(response.url)
            for attachment in item['attachments']:
                if attachment['type'] == 'link':
                    yield from self.GIFT_RE.findall(attachment['link']['url'])

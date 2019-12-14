"""
VK.com API wrapper.
"""

import re
from typing import Iterable

from loguru import logger
from requests import Session

from bestmobabot import constants
from bestmobabot.settings import Settings


class VK:
    URL = 'https://api.vk.com/method/wall.get'
    GIFT_ID_RE = re.compile(r'gift_id=(\w+)')
    VK_CC_RE = re.compile(r'https://vk.cc/\w+')

    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.params = {
            'access_token': settings.vk.access_token,
            'owner_id': '-116039030',
            'count': '5',
            'v': '5.92',
        }

    def find_gifts(self) -> Iterable[str]:
        logger.info('Checking VK.com gifts…')

        with self.session.get(self.URL, params=self.params, timeout=constants.API_TIMEOUT) as response:
            logger.info('Get wall: {}.', response.status_code)
            response.raise_for_status()
            payload = response.json()

        for item in payload['response']['items']:
            yield from self.GIFT_ID_RE.findall(item['text'])
            for url in self.VK_CC_RE.findall(item['text']):
                # HEAD is unsupported by VK.com. Use streaming to obtain just the headers.
                with self.session.get(url, stream=True, timeout=constants.API_TIMEOUT) as response:
                    logger.info('Get {}: {}.', url, response.status_code)
                    yield from self.GIFT_ID_RE.findall(response.url)
            for attachment in item['attachments']:
                if attachment['type'] == 'link':
                    yield from self.GIFT_ID_RE.findall(attachment['link']['url'])

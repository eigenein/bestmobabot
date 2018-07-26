from functools import lru_cache

import requests

from bestmobabot import constants
from bestmobabot.logging_ import logger

session = requests.Session()


@lru_cache(maxsize=None)
def get_ip():
    try:
        with session.get(constants.IP_URL) as response:
            response.raise_for_status()
            return response.text
    except requests.RequestException:
        return '127.0.0.1'


def send_event(*, category: str, action: str, user_id: str):
    try:
        with session.post(constants.ANALYTICS_URL, data={
            'v': '1',
            'tid': constants.ANALYTICS_TID,
            't': 'event',
            'ec': category,
            'ea': action,
            'el': user_id,
            'cid': user_id,
            'ni': '1',
            'cd1': constants.VERSION,
            'cd2': get_ip(),
        }) as response:
            response.raise_for_status()
    except requests.RequestException as ex:
        logger.warning('😱 Failed to send the event.', exc_info=ex)

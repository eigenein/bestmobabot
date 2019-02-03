import itertools
from functools import lru_cache
from hashlib import sha1
from pathlib import Path

import requests
from loguru import logger

import bestmobabot
from bestmobabot import constants

session = requests.Session()


@lru_cache(maxsize=None)
def get_version() -> str:
    return sha1(bytes(itertools.chain.from_iterable(
        path.open('rb').read()
        for path in sorted(Path(bestmobabot.__file__).parent.glob('**/*.py'))
    ))).hexdigest()[-8:]


@lru_cache(maxsize=None)
def get_ip() -> str:
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
            'cd1': get_version(),
            'cd2': get_ip(),
        }, timeout=constants.API_TIMEOUT) as response:
            response.raise_for_status()
    except requests.RequestException as ex:
        logger.warning('😱 Failed to send the event.', exc_info=ex)

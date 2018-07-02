import requests

from bestmobabot.logging_ import logger

URL = 'https://www.google-analytics.com/collect'
TID = 'UA-65034198-7'

session = requests.Session()


def send_event(*, category: str, action: str, user_id: str):
    try:
        with session.post(URL, data={
            'v': '1',
            'tid': TID,
            't': 'event',
            'ec': category,
            'ea': action,
            'el': user_id,
            'cid': user_id,
            'ni': '1',
        }) as response:
            response.raise_for_status()
    except Exception as ex:
        logger.warning('😱 Failed to send the event.', exc_info=ex)

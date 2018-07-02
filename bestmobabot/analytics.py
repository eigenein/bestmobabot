import requests

from bestmobabot.logger import logger

URL = 'https://www.google-analytics.com/collect'
TID = 'UA-65034198-7'
EC = 'bestmobabot'

session = requests.Session()


def send_event(*, action: str, user_id: str):
    try:
        with session.post(URL, data={'v': 1, 'tid': TID, 't': 'event', 'ec': EC, 'ea': action, 'el': user_id, 'cid': user_id}) as response:
            response.raise_for_status()
    except Exception as ex:
        logger.warning('😱 Failed to send the event.', exc_info=ex)

from __future__ import annotations

from datetime import datetime, time

from pytest import mark

from bestmobabot.scheduler import Task


@mark.parametrize('last_executed_at, now', [
    # Last executed before the earliest time.
    (datetime.fromisoformat('2019-02-24T08:59:59+01:00'), datetime.fromisoformat('2019-02-24T09:00:00+01:00')),
])
def test_between_positive(last_executed_at: datetime, now: datetime):
    assert Task(name='') \
        .between(time(hour=9), time(hour=12)) \
        .is_pending(last_executed_at, now)


@mark.parametrize('last_executed_at, now', [
    # Last executed right after the earliest time.
    (datetime.fromisoformat('2019-02-24T09:00:00+01:00'), datetime.fromisoformat('2019-02-24T09:01:00+01:00')),
])
def test_between_negative(last_executed_at: datetime, now: datetime):
    assert not Task(name='') \
        .between(time(hour=9), time(hour=12)) \
        .is_pending(last_executed_at, now)

import pytest

from bestmobabot.database import Database


def test_get_missing():
    with pytest.raises(KeyError):
        Database(':memory:').__getitem__('missing_key')


def test_exists():
    db = Database(':memory:')
    db['foo'] = 42
    assert 'foo' in db


def test_not_exists():
    assert 'missing_key' not in Database(':memory:')


def test_set():
    db = Database(':memory:')
    db['foo'] = 42
    assert db['foo'] == 42


def test_set_replace():
    db = Database(':memory:')
    db['foo'] = 42
    db['foo'] = 43
    assert db['foo'] == 43


def test_get_by_prefix():
    db = Database(':memory:')
    db['foo:qux'] = 42
    db['foo:quux'] = 43
    assert list(db.get_by_prefix('foo')) == [('foo:qux', 42), ('foo:quux', 43)]

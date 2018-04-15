from bestmobabot.database import Database


def test_get_missing():
    assert Database(':memory:').get_by_key('missing_index', 'missing_key') is None


def test_default():
    assert Database(':memory:').get_by_key('missing_index', 'missing_key', default=42) == 42


def test_exists():
    db = Database(':memory:')
    db.set('index', 'a', 42)
    assert db.exists('index', 'a')


def test_not_exists():
    assert not Database(':memory:').exists('missing_index', 'missing_key')


def test_set():
    db = Database(':memory:')
    db.set('index', 'a', 42)
    assert db.get_by_key('index', 'a') == 42


def test_set_replace():
    db = Database(':memory:')
    db.set('index', 'a', 42)
    db.set('index', 'a', 43)
    assert list(db.get_by_index('index')) == [('a', 43)]


def test_custom_dumps_loads():
    db = Database(':memory:')
    db.set('index', 'a', 'trololo', dumps=str)
    assert db.get_by_key('index', 'a', loads=str) == 'trololo'

from bestmobabot.database import Database


def test_get_missing():
    assert Database(':memory:').get_by_key('missing_key') is None


def test_default():
    assert Database(':memory:').get_by_key('missing_key', default=42) == 42


def test_exists():
    db = Database(':memory:')
    db.set('foo', 42)
    assert db.exists('foo')


def test_not_exists():
    assert not Database(':memory:').exists('missing_key')


def test_set():
    db = Database(':memory:')
    db.set('foo', 42)
    assert db.get_by_key('foo') == 42


def test_set_replace():
    db = Database(':memory:')
    db.set('foo', 42)
    db.set('foo', 43)
    assert db.get_by_key('foo') == 43


def test_get_by_prefix():
    db = Database(':memory:')
    db.set('foo:qux', 42)
    db.set('foo:quux', 43)
    assert list(db.get_by_prefix('foo')) == [('foo:qux', 42), ('foo:quux', 43)]


def test_custom_dumps_loads():
    db = Database(':memory:')
    db.set('foo', 'trololo', dumps=str)
    assert db.get_by_key('foo', loads=str) == 'trololo'

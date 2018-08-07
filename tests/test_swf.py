from typing import Iterable

import pytest

from bestmobabot.swf import pack_bits


@pytest.mark.parametrize('initial_value, bits, expected', [
    (0, [1, 0, 0], 4),
    (-1, [1, 0, 0], -4),
])
def test_pack_bits(initial_value: int, bits: Iterable[int], expected: int):
    assert pack_bits(initial_value, bits) == expected

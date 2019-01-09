"""
More `itertools`.
"""

from __future__ import annotations

import math
from typing import Any, Iterable, Iterator, List, TypeVar

from loguru import logger

T = TypeVar('T')


class CountDown(Iterator[T]):
    """
    Limits iteration number unless `reset` is called.
    """

    def __init__(self, iterable: Iterable[T], n_iterations: int):
        self.iterator = iter(iterable)
        self.n_iterations = n_iterations
        self.iterations_left = n_iterations
        self.is_fresh = True

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        if not self.iterations_left:
            raise StopIteration
        self.iterations_left -= 1
        self.is_fresh = False
        return next(self.iterator)

    def __int__(self) -> int:
        return self.iterations_left

    def reset(self):
        self.iterations_left = self.n_iterations
        self.is_fresh = True


def secretary_max(items: Iterable[T], n: int, early_stop: Any = None) -> T:
    """
    Select best item while lazily iterating over the items.
    https://en.wikipedia.org/wiki/Secretary_problem#Deriving_the_optimal_policy
    """
    r = int(n / math.e) + 1

    max_item = None

    for i, item in enumerate(items, start=1):
        # Check early stop condition.
        if early_stop is not None and item >= early_stop:
            logger.trace('Early stop.')
            return item
        # If it's the last item, just return it.
        if i == n:
            logger.trace('Last item.')
            return item
        # Otherwise, check if the item is better than previous ones.
        if max_item is None or item >= max_item:
            if i >= r:
                # Better than (r - 1) previous ones, return it.
                logger.trace('Better than {} previous ones.', r - 1)
                return item
            # Otherwise, update the best key.
            max_item = item

    raise RuntimeError('unreachable code')


def slices(n: int, length: int) -> List[slice]:
    """
    Make a list of continuous slices. E.g. `[slice(0, 2), slice(2, 4), slice(4, 6)]`.
    """
    return [slice(i * length, (i + 1) * length) for i in range(n)]

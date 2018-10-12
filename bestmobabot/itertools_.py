from __future__ import annotations

from typing import Iterable, Iterator, TypeVar

T = TypeVar('T')


class CoolDown(Iterator[T]):
    def __init__(self, iterable: Iterable[T], interval: int):
        self.iterator = iter(iterable)
        self.interval = interval
        self.iterations_left = interval
        self.is_fresh = True

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        if not self.iterations_left:
            raise StopIteration
        self.iterations_left -= 1
        self.is_fresh = False
        return next(self.iterator)

    def reset(self):
        self.iterations_left = self.interval
        self.is_fresh = True

import itertools

from typing import TypeVar, Iterable

T = TypeVar("T")


def flatten(array: Iterable[Iterable[T]]) -> list[T]:
    """Flattens two nested iterables into a single list containing all items sequentially."""
    return list(itertools.chain.from_iterable(array))

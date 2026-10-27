from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")


def find_match(
    query: str, candidates: Iterable[T], name: Callable[[T], str]
) -> T | None:
    needle = query.strip().lower()
    if not needle:
        return None
    items = [(name(item).lower(), item) for item in candidates]
    for accepts in (
        lambda label: label == needle,
        lambda label: label.startswith(needle),
        lambda label: any(word.startswith(needle) for word in label.split()),
        lambda label: needle in label,
    ):
        for label, item in items:
            if accepts(label):
                return item
    return None

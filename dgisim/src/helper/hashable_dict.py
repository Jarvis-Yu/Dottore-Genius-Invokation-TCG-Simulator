from typing import Dict, Any
from typing_extensions import override


class HashableDict(dict):
    def __add__(self, other: Dict[Any, int]):
        keys = set(self.keys()).union(other.keys())
        return HashableDict(
            [(key, self.get(key, 0) + other.get(key, 0)) for key in keys]
        )

    def __sub__(self, other: Dict[Any, int]):
        keys = set(self.keys()).union(other.keys())
        return HashableDict(
            [(key, self.get(key, 0) - other.get(key, 0)) for key in keys]
        )

    def __hash__(self) -> int:  # type: ignore
        return hash(frozenset(self.items()))

from typing import Dict, Any

class HashableDict(dict):
    def __add__(self, other: Dict[Any, int]):
        return HashableDict(
            [(key, self[key] + other.get(key, 0)) for key in self]
        )

    def __sub__(self, other: Dict[Any, int]):
        return HashableDict(
            [(key, self[key] - other.get(key, 0)) for key in self]
        )

    def __hash__(self) -> int:
        return hash(frozenset(self.items()))
from typing import Dict, Any

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

    def __hash__(self) -> int:
        return hash(frozenset(self.items()))
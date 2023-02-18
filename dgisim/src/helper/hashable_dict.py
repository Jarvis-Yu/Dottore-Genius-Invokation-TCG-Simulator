class HashableDict(dict):
    def __hash__(self) -> int:
        return hash(frozenset(self.items()))
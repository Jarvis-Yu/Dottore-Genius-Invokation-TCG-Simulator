from __future__ import annotations
from typing import Dict, Any
from typing_extensions import override


class HashableDict(dict):
    """
    Inheritates dict but implements __hash__().

    In order to safely use __hash__(), there's a boolean property _frozen,
    determining whether the HashableDict is safe to hash and accept further
    modifications. The default value of _frozen is True.

    If you want to create the HashableDict, make some modifications and then
    freeze it, add a keyword argument frozen=False when initializing, and call
    .freeze() later.

    You cannot call any setter, deleter or hash method of a frozen HashableDict.
    If you do so, Exception will be raised.
    """

    def __init__(self, *args, frozen=True, **kwargs):
        """
        Used in the same way as dict.__init__().

        from_dict() is preferred when trying to copy a HashableDict than __init__().
        """
        super().__init__(*args, **kwargs)
        self._frozen = frozen

    def freeze(self) -> None:
        """ Freeze this HashableDict to prevent further changes and enable hash. """
        if self._frozen:
            return
        self._frozen = True

    def _unfreeze(self) -> None:
        """
        ONLY CALL THIS WHEN YOU KNOW WHAT YOU ARE DOING!!!

        A frozen HashableDict could be shared by multiple references thinking
        they have different HashableDicts, modifying this one may cause unexpected
        behaviour elsewhere.
        """
        # use a trick to bypass overriden __setattr__() avoiding exception
        object.__setattr__(self, "_frozen", False)

    def frozen(self) -> bool:
        if hasattr(self, "_frozen"):
            return self._frozen
        return False

    def __setattr__(self, *args, **kwargs):
        if self.frozen():
            raise Exception("Calling __setattr__() to a frozen HashableDict!")
        super().__setattr__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        if self.frozen():
            raise Exception("Calling __setitem__() to a frozen HashableDict!")
        super().__setitem__(*args, **kwargs)

    def __delattr__(self, *args, **kwargs):
        if self.frozen():
            raise Exception("Calling __delattr__() to a frozen HashableDict!")
        super().__delattr__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        if self.frozen():
            raise Exception("Calling __delitem__() to a frozen HashableDict!")
        super().__delitem__(*args, **kwargs)

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
        """ Exception is raised if the HashableDict is not frozen. """
        if not self.frozen():
            raise Exception("Calling __hash__() to a non-frozen HashableDict!")
        return hash(frozenset(self.items()))

    @classmethod
    def from_dict(cls, d: dict) -> HashableDict:
        """
        This method is preferred when trying to copy a HashableDict than __init__()
        """
        if isinstance(d, HashableDict) and d.frozen():
            return d
        else:
            return HashableDict(d)

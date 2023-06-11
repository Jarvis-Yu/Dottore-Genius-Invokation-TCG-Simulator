from __future__ import annotations
from typing import TypeVar, Optional

_T = TypeVar('_T')

def just(optional_val: Optional[_T], backup: Optional[_T]=None) -> _T:
    """
    Removes Optional and get value directly
    Throws exception if it is indeed None
    """
    if optional_val is None:
        if backup is None:
            raise Exception("Trying to just None")
        else:
            return backup
    return optional_val

BIG_INT = 0x7fffffff

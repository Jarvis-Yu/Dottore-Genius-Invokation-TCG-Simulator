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

def case_val(condition: bool, first: _T, second: _T) -> _T:
    """ if condition is True; then return first; else return second """
    return first if condition else second

BIG_INT = 0x7fffffff

from __future__ import annotations
from typing import TypeVar, Optional

T = TypeVar('T')

def just(optional_val: Optional[T]) -> T:
    """
    Removes Optional and get value directly
    Throws exception if it is indeed None
    """
    if optional_val is None:
        raise Exception("Trying to just None")
    return optional_val
from __future__ import annotations
from dataclasses import fields
from enum import Enum
from inspect import isclass
from typing import Any, TypeVar

__all__ = [
    "BIG_INT",
    "case_val",
    "classproperty",
    "dataclass_repr",
    "is_subclass",
    "just",
    "safe_issubclass",
]

_T = TypeVar('_T')

BIG_INT = 0x7fffffff


class _CachedClassProperty:
    class _Null(Enum):
        NULL = 0

    def __init__(self, fget):
        self._fget = fget
        self._cache = _CachedClassProperty._Null.NULL

    def __get__(self, obj, klass=None):
        if self._cache is not _CachedClassProperty._Null.NULL:
            return self._cache
        if klass is None:
            klass = type(obj)
        self._cache = self._fget.__get__(obj, klass)()
        return self._cache


class _HackeyCachedClassProperty(_CachedClassProperty):
    def __init__(self, fget):
        self._fget = fget

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        ret_val = self._fget.__get__(obj, klass)()
        setattr(klass, self._fget.__name__, ret_val)
        return ret_val


def cached_classproperty(func) -> _CachedClassProperty:
    if not isinstance(func, classmethod):
        func = classmethod(func)

    return _HackeyCachedClassProperty(func)
    # return _CachedClassProperty(func)


def case_val(condition: bool, first: _T, second: _T) -> _T:
    """ if condition is True; then return first; else return second """
    return first if condition else second


class _ClassProperty:
    def __init__(self, fget):
        self._fget = fget

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self._fget.__get__(obj, klass)()


def classproperty(func) -> _ClassProperty:
    """ This version of classproperty cache the first result. """
    # credit: https://stackoverflow.com/a/5191224
    if not isinstance(func, classmethod):
        func = classmethod(func)

    return _ClassProperty(func)


def dataclass_repr(self) -> str:
    def field_val_to_str(field_val: Any) -> str:
        if isclass(field_val):
            return field_val.__name__
        if isinstance(field_val, Enum):
            return field_val.name
        return repr(field_val)

    cls_fields = fields(self)
    paired_fields = (
        f"{field.name}={field_val_to_str(self.__getattribute__(field.name))}"
        for field in cls_fields
    )
    return f"{self.__class__.__name__}({', '.join(paired_fields)})"


def is_instance_or_subclass(item: type | object, parent: type) -> bool:
    """ :returns: True if item is an instance of parent or a subclass of parent. """
    return isinstance(item, parent) or safe_issubclass(item, parent)

def is_subclass(cls: type, parent: type) -> bool:
    """
    :returns: True if cls is a subclass of parent
    """
    assert isclass(cls), f"{cls} is not a class"
    return issubclass(cls, parent)


def just(optional_val: None | _T, backup: None | _T = None) -> _T:
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


def safe_issubclass(cls: type | object, parent: type) -> bool:
    """
    :returns: False if cls is not a subclass of parent or is not a class.
    """
    return isclass(cls) and issubclass(cls, parent)

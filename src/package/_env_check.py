# mypy: ignore-errors
import sys

if sys.version_info < (3, 10):
    raise RuntimeError("Package dgisim requires Python 3.10+")

__all__ = []
from __future__ import absolute_import

import uuid
from typing import Any, Iterable, List


def to_uuid(*args: List[Any]) -> str:
    s = str(uuid.uuid5(uuid.NAMESPACE_DNS, ""))
    for a in args:
        for x in _get_strs(a):
            s = str(uuid.uuid5(uuid.NAMESPACE_DNS, s + x))
    return s


def _get_strs(obj: Any) -> Iterable[str]:
    if obj is None:
        yield ""
    elif isinstance(obj, dict):
        for k, v in obj.items():
            for x in _get_strs(k):
                yield x
            for x in _get_strs(v):
                yield x
    elif not isinstance(obj, str) and isinstance(obj, Iterable):
        for k in obj:
            for x in _get_strs(k):
                yield x
    else:
        yield str(type(obj))
        yield str(obj)

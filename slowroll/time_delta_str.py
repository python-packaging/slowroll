import re
from datetime import timedelta

UNITS = {
    "d": "days",
    "h": "hours",
    "m": "minutes",
    "s": "seconds",
    "ms": "milliseconds",
}

ARG_RE = re.compile(r"(-?[0-9.]+)\s*(ms|d|h|m|s)\s*")  # N.b. "ms" comes first


def delta_parser(s: str) -> timedelta:
    kwargs = {}
    for n, unit in ARG_RE.findall(s):
        kwarg = UNITS[unit]
        assert kwarg not in kwargs
        kwargs[kwarg] = float(n)

    assert ARG_RE.sub("", s.strip()) == "", f"String {s!r} was not entirely time deltas"

    return timedelta(**kwargs)

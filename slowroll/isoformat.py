from datetime import datetime, timezone

UTC_FORMATS = (
    "%Y-%m-%d %H:%MZ",
    "%Y-%m-%d %H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S.%fZ",
)


def datetime_fromisoformat(s: str) -> datetime:
    # This could just use datetime.fromisoformat which correctly even sets the
    # tzinfo when you include Z suffix, but that only works on 3.11+
    for f in UTC_FORMATS:
        try:
            return datetime.strptime(s, f).replace(tzinfo=timezone.utc)
        except Exception:
            pass

    raise Exception(f"Could not parse {s!r} as any known format")

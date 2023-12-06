import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Tuple, Union
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .isoformat import datetime_fromisoformat

from .time_delta_str import delta_parser

LOG = logging.getLogger(__name__)


def _default_fetch(
    url: str, etag: Optional[str]
) -> Union[Tuple[str, str], Tuple[None, None]]:
    """
    Retrieves a url with etag checking.  Return values are either

    (data, etag)
    or
    None, None (meaning not modified)
    """
    # TODO should probably handle retries and/or redirects too.
    # TODO should probably check server time to verify we are "close enough"
    r = Request(url)
    if etag:
        r.add_header("If-None-Match", etag)
    try:
        resp = urlopen(r)
    except HTTPError as e:
        if e.status == 304:
            return None, None
        else:
            raise Exception(f"Unknown status {e.status}: {e.read()!r}")
    else:
        return resp.read(), resp.headers["ETag"]


def _default_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _default_hasher(hash_key: str) -> int:
    h = hashlib.sha1(hash_key.encode())
    # 32-bit numeric position in the range
    n = int.from_bytes(h.digest()[-4:], "big")
    return n


class SlowrollConfig:
    def __init__(
        self,
        url: str,
        local_cache_name: str,
        fetch_cb: Optional[
            Callable[[str, Optional[str]], Union[Tuple[str, str], Tuple[None, None]]]
        ] = None,
        now_cb: Optional[Callable[[], datetime]] = None,
        hasher: Optional[Callable[[str], int]] = None,
    ):
        self.url = url
        self.local_cache_name = local_cache_name
        self.fetch_cb = fetch_cb or _default_fetch
        self.now_cb = now_cb or _default_now
        self.hasher = hasher or _default_hasher

    def get_value(
        self, section: str, key: str, hash_key: str, default: Any = None
    ) -> Any:
        """
        If this key is found in the slowroll config, look up its value at the
        current time.
        """
        config = self.get_config()
        one_config = config.get(section, {}).get(key, {})
        if not one_config:
            return default
        # TODO perhaps .interpolate someday
        return self.decide(hash_key, one_config)

    def get_config(self) -> Dict[str, Dict[str, Any]]:
        """
        A typical config looks something like

        {
            "rollouts": {
                "some-cli": {
                    "stable": "1.0",
                    "new": "1.1a",
                    "start_pct": 0,
                    "end_pct": 100,
                    "duration": "1h",
                    "end_time": "2023-01-01 00:00Z",
                    "early_adopters": ["alice", "bob"]
                }
            }
        }
        """
        # TODO store local_cache_name in the appropriate XDG dir, along with the
        # etag from last fetch.
        data, etag = self.fetch_cb(self.url, None)
        assert data is not None
        config: Dict[str, Dict[str, Any]] = json.loads(data)
        return config

    def decide(self, hash_key: str, config: Dict[str, Any]) -> Any:
        """
        Returns either 'stable' or 'new' key, depending on current time.  The
        values can be anything, but are expected to be strings.
        """
        if "new" not in config:
            return config["stable"]

        if hash_key in config.get("early_adopters", ()):
            return config["new"]

        end_time = datetime_fromisoformat(config["end_time"])
        # TODO more robust validation (including a separate method), and don't
        # use assert for runtime checking like this.
        assert end_time.tzinfo == timezone.utc
        duration = delta_parser(config["duration"])
        start_time = end_time - duration

        n = self.hasher(hash_key)

        my_scalar_position = n / 2**32
        start_pct = config.get("start_pct", 0)
        start_scalar_position = start_pct / 100
        end_pct = config.get("end_pct", 100)
        assert end_pct > start_pct
        end_scalar_position = end_pct / 100

        now = self.now_cb()
        assert now.tzinfo == timezone.utc
        my_time = start_time + (duration * (my_scalar_position - start_scalar_position))

        LOG.debug(
            "start_time=%s @ %s, end_time=%s @ %s",
            start_time,
            start_scalar_position,
            end_time,
            end_scalar_position,
        )
        LOG.debug("  my_time=%s @ %s, now=%s", my_time, my_scalar_position, now)

        if now >= my_time:
            return config["new"]
        else:
            return config["stable"]

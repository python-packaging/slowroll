import json
import unittest
from typing import Optional, Tuple

from ..api import _default_fetch, SlowrollConfig
from ..isoformat import datetime_fromisoformat

FAKE_CONFIG = {
    "roll": {
        "foo": {
            "start_pct": 0,
            "end_pct": 100,
            "end_time": "2010-01-01 01:00:00Z",
            "duration": "1h",
            "stable": "STABLE",
            "new": "NEW",
            "early_adopters": ["zoran"],
        },
    },
}


class SlowrollTest(unittest.TestCase):
    def test_default_fetch(self) -> None:
        data, etag = _default_fetch(
            "http://timhatch.com/projects/http-tests/sequence_100.txt", None
        )
        assert data is not None
        self.assertEqual(b"1\n2\n", data[:4])
        assert etag is not None
        new_data, new_etag = _default_fetch(
            "http://timhatch.com/projects/http-tests/sequence_100.txt", etag
        )
        assert new_data is None, new_etag is None

    def test_default_fetch_error(self) -> None:
        with self.assertRaisesRegex(
            Exception, r"Unknown status 512: b'Gzip: nope\\nResponse code: 512'"
        ):
            _default_fetch(
                "http://timhatch.com/projects/http-tests/response/?code=512", None
            )

    def test_slowrollconfig(self) -> None:
        def cb(url: str, etag: Optional[str] = None) -> Tuple[str, str]:
            return json.dumps(FAKE_CONFIG), "e1a6"

        now = datetime_fromisoformat("2010-01-01 00:00Z")
        c = SlowrollConfig(
            "https://example.com/", "roll", cb, lambda: now, lambda x: 2**31
        )
        # near start_time
        self.assertEqual("STABLE", c.get_value("roll", "foo", "z"))
        # early_adopters
        self.assertEqual("NEW", c.get_value("roll", "foo", "zoran"))

        # just started
        now = datetime_fromisoformat("2010-01-01 00:01Z")
        self.assertEqual("STABLE", c.get_value("roll", "foo", "z"))
        # just over half
        now = datetime_fromisoformat("2010-01-01 00:31Z")
        self.assertEqual("NEW", c.get_value("roll", "foo", "z"))
        # near end_time
        now = datetime_fromisoformat("2010-01-01 01:00Z")
        self.assertEqual("NEW", c.get_value("roll", "foo", "z"))
        # after end_time
        now = datetime_fromisoformat("2010-01-01 01:01Z")
        self.assertEqual("NEW", c.get_value("roll", "foo", "z"))

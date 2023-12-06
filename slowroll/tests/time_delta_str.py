import unittest
from datetime import timedelta

from ..time_delta_str import delta_parser


class TimeDeltaStrParserTest(unittest.TestCase):
    def test_basic(self) -> None:
        self.assertEqual(timedelta(microseconds=1000), delta_parser("1ms"))
        self.assertEqual(timedelta(microseconds=1000), delta_parser("1  ms  "))

        self.assertEqual(timedelta(seconds=-1), delta_parser("-1s"))
        self.assertEqual(timedelta(seconds=1), delta_parser("1s"))
        self.assertEqual(timedelta(seconds=1), delta_parser("1  s  "))

        self.assertEqual(timedelta(seconds=3600), delta_parser("1h"))
        self.assertEqual(timedelta(seconds=3600), delta_parser("1  h  "))

    def test_zero(self) -> None:
        self.assertEqual(timedelta(), delta_parser(""))
        self.assertEqual(timedelta(), delta_parser(" "))

    def test_failures(self) -> None:
        with self.assertRaises(AssertionError):
            delta_parser("1z")

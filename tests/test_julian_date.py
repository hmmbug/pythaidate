# -*- coding: utf-8 -*-

from .context import pythaidate
# from .data import PKN_TEST_DATA, KEY_AD, KEY_JU, KEY_JDN

import unittest

ju = pythaidate.calendars.julian_date


class JulianDateTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_to_jdn(self):
        test_val = 1000
        res = ju.to_jdn(test_val)
        assert res == test_val

    def test_from_jdn(self):
        test_val = 1000
        res = ju.from_jdn(test_val)
        assert res == test_val

    def test_parse(self):
        for v in [1000, 1000.5, "1000.5"]:
            exp = float(v)
            res = ju.parse(v)
            assert exp == res


if __name__ == '__main__':
    unittest.main()

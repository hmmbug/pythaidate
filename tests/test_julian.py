# -*- coding: utf-8 -*-

from .context import pythaidate
from .data import TEST_DATA

import unittest

ju = pythaidate.calendars.julian


class JulianTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_to_jdn(self):
        for item in TEST_DATA:
            year, month, day = item['JU'].split('-')
            result = ju.to_jdn(year, month, day)
            assert result == item['JDN'], "Error: %s %s %s" % (
                item['JU'], item['JDN'], result)

    def test_from_jdn(self):
        for item in TEST_DATA:
            jdn = item['JDN']
            res = ju.from_jdn(jdn)
            assert res == item['JU'], "Error: %s %s %s" % (
                item['JU'], item['JDN'], res)

    def test_parse(self):
        for item in TEST_DATA:
            test = item['JU']
            exp = item['JDN']
            res = ju.parse(test)
            assert res == exp, "Error: test:%s exp:%s res:%s" % (
                test, exp, res)


class JulianThaiDateTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_calendar_parsers(self):
        ptd = pythaidate.ThaiDate
        formats = ptd.list_formats()
        for f in formats:
            for item in TEST_DATA:
                test = item['JU']
                dt = ptd.from_julian(test)
                result = dt.format("julian")
                assert test == result, "test:%s result:%s" % (
                    test, result)


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-

from .context import pythaidate
from .data import TEST_DATA

import unittest

ts = pythaidate.calendars.thai_solar


class ThaiSolarTestSuite(unittest.TestCase):

    def test_to_jdn(self):
        for item in TEST_DATA:
            year, month, day = item['BE'].split('-')
            result = ts.to_jdn(year, month, day)
            assert result == item['JDN'], "Error: %s %s %s" % (
                item['BE'], item['JDN'], result)

    def test_from_jdn(self):
        for item in TEST_DATA:
            jdn = item['JDN']
            res = ts.from_jdn(jdn)
            assert res == item['BE'], "Error: BE:%s test:%s res:%s" % (
                item['BE'], item['JDN'], res)

    def test_parse(self):
        for item in TEST_DATA:
            test = item['BE']
            exp = item['JDN']
            res = ts.parse(test)
            assert res == exp, "Error: test:%s exp:%s res:%s" % (
                test, exp, res)


class ThaiSolarThaiDateTestSuite(unittest.TestCase):

    def test_calendar_parsers(self):
        ptd = pythaidate.ThaiDate
        formats = ptd.list_formats()
        for f in formats:
            for item in TEST_DATA:
                test = item['BE']
                dt = ptd.from_gregorian(test)
                result = dt.format("gregorian")
                assert test == result, "test:%s result:%s" % (
                    test, result)


if __name__ == '__main__':
    unittest.main()

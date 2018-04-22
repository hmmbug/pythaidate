"""Gregorian test."""

from .context import pythaidate
from .data import TEST_DATA

import unittest

gr = pythaidate.calendars.gregorian


class GregorianTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_to_jdn(self):
        for item in TEST_DATA:
            year, month, day = item['CE'].split('-')
            result = gr.to_jdn(year, month, day)
            assert result == item['JDN'], "Error: %s %s %s" % (
                item['CE'], item['JDN'], result)

    def test_from_jdn(self):
        for item in TEST_DATA:
            jdn = item['JDN']
            res = gr.from_jdn(jdn)
            assert res == item['CE'], "Error: %s %s %s" % (
                item['CE'], item['JDN'], res)

    def test_parse(self):
        for item in TEST_DATA:
            test = item['CE']
            exp = item['JDN']
            res = gr.parse(test)
            assert res == exp, "Error: test:%s exp:%s res:%s" % (
                test, exp, res)


class GregorianThaiDateTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_calendar_parsers(self):
        ptd = pythaidate.ThaiDate
        formats = ptd.list_formats()
        for f in formats:
            for item in TEST_DATA:
                test = item['CE']
                dt = ptd.from_gregorian(test)
                result = dt.format("gregorian")
                assert test == result, "test:%s result:%s" % (
                    test, result)


if __name__ == '__main__':
    unittest.main()

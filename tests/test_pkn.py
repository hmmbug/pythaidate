# -*- coding: utf-8 -*-

from .context import pythaidate
from .data import TEST_DATA

import unittest

pkn = pythaidate.calendars.pkn


class pknTestSuite(unittest.TestCase):
    """PKN test cases."""

    def test_pkn_from_jdn(self):
        for item in TEST_DATA:
            if item['CE'] >= '1736-01-28':
                result = pkn.from_jdn(item['JDN'] + 0.5)
                assert result["text_long"] == item['PKN_LONG'], \
                    "\n Gen: %s\nTest: %s" % (
                        result["text_long"], item['PKN_LONG']
                    )

                result = pkn.from_jdn(item['JDN'] + 0.5)
                assert result["text_short"] == item['PKN_SHORT'], \
                    "\n Gen: %s\nTest: %s" % (
                        result["text_short"], item['PKN_SHORT']
                    )
            else:
                with self.assertRaises(ValueError):
                    result = pkn.from_jdn(item['JDN'])

        else:
            assert True

    def test_jdn_to_jdn(self):
        for item in TEST_DATA:
            if item['PKN_SHORT'] is None:
                continue
            pkn_test = item['PKN_SHORT'].replace("-", " ").replace(":", " ")
            pkn_test = [1] + [int(i) for i in pkn_test.split()]
            exp = item['JDN']
            result = pkn.to_jdn(*pkn_test)
            assert exp == result, \
                "\n Test:%s  Res:%s  Exp:%s" % (pkn_test, result, exp)

        with self.assertRaises(ValueError):
            pkn.to_jdn(0, 1, 1, 1, 1, 1, 1)

    def test_to_jdn_invalid(self):
        # check for out-of-range errors
        assert pkn._validate_pkn(0, 1, 1, 1, 1, 1, 1) is False
        assert pkn._validate_pkn(5, 1, 1, 1, 1, 1, 1) is False
        assert pkn._validate_pkn(1, 0, 1, 1, 1, 1, 1) is False
        assert pkn._validate_pkn(1, 19, 1, 1, 1, 1, 1) is False
        assert pkn._validate_pkn(1, 1, 0, 1, 1, 1, 1) is False
        assert pkn._validate_pkn(1, 1, 1, 0, 1, 1, 1) is False
        assert pkn._validate_pkn(1, 1, 1, 1, 0, 1, 1) is False
        assert pkn._validate_pkn(1, 1, 1, 1, 1, 0, 1) is False
        assert pkn._validate_pkn(1, 1, 1, 1, 1, 1, 0) is False

    def test_pkn_parse(self):
        for item in TEST_DATA:
            pkn_short = item['PKN_SHORT']  # without cycle prefix
            if pkn_short is None:
                with self.assertRaises(ValueError):
                    pkn.parse(pkn_short)

            else:
                result = pkn.parse(pkn_short)
                assert item['JDN'] == result, \
                    "Parse: SHORT (wo/prefix) %s %s %s" % (
                        item['CE'], item['JDN'], result)

                result = pkn.parse("1:"+pkn_short)  # w/cycle prefix
                assert item['JDN'] == result, \
                    "Parse: SHORT (w/prefix) %s" % (item['CE'],)

                result = pkn.parse(item['PKN_LONG'])
                assert item['JDN'] == result, \
                    "Parse: LONG %s" % (item['CE'],)

                result = pkn.parse(item['JDN'])
                assert item['JDN'] == result, \
                    "Parse: JDN %s" % (item['JDN'],)

    def test_pkn_parse_invalid(self):
        pkn_test = "NO MATCH"
        with self.assertRaises(ValueError):
            pkn.parse(pkn_test)


if __name__ == '__main__':
    unittest.main()

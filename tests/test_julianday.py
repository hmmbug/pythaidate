import json
import unittest
import os
import pathlib
from datetime import date

this_path = pathlib.Path(__file__).parent.resolve()

from pythaidate import julianday

with open(os.path.join(this_path, "data/julian.json")) as fh:
    TESTDATA = json.load(fh)


def get_ymd(t):
    return t["year"], t["month"], t["day"]


class Test_JulianDay(unittest.TestCase):

    def test_compare_julian_to_testdata(self):
        for i in TESTDATA:
            dt0 = date(*get_ymd(i))
            dt1 = julianday.julianday_to_date(i["jd"])
            self.assertEqual(dt0, dt1, (dt0, dt1))

    def test_convert_to_date_and_back(self):
        for i in TESTDATA:
            dt = date(*get_ymd(i))
            jd = julianday.date_to_julianday(dt)
            self.assertEqual(i["jd"], jd, (i, jd))

if __name__ == '__main__':
    unittest.main()

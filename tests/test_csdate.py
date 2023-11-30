from datetime import date, timedelta
import json
import unittest
import os
import pathlib
import random

import logging

from pythaidate import CsDate, julianday
from pythaidate.constants import CS_JULIAN_DAY_OFFSET

random.seed()
this_path = pathlib.Path(__file__).parent.resolve()

for datafile in ("cs.json", "cs.min.json"):
    datafile = os.path.join(this_path, "data", datafile)
    if os.path.exists(datafile):
        break
else:
    raise FileNotFoundError("CS data file not found.")

with open(datafile) as fh:
    TESTDATA = json.load(fh)


MIN_YEAR = 0  # 638 AD
MAX_YEAR = 1462  # 2100 AD
MAX_YEAR = 2362  # 3000 AD
RUN_PERCENT = 10
if os.environ.get("RUN_PERCENT"):
    RUN_PERCENT = int(os.environ.get("RUN_PERCENT"))
    if RUN_PERCENT > 100:
        RUN_PERCENT = 100


class Test_CsDate(unittest.TestCase):

    def random_dates(self, min_year=MIN_YEAR, max_year=MAX_YEAR, sample_rate_pc=None):
        if sample_rate_pc is None:
            sample_rate_pc = RUN_PERCENT
        for y in range(min_year, max_year):
            yd = CsDate.fromyd(year=y, days=0)
            year_days = yd.days_in_year
            for d in range(year_days):
                if random.randint(1, 100) > sample_rate_pc:
                    continue
                yield y, d

    def test_example_dates(self):
        tests = (
            # Gislen/Eade, JAHH 22(3), 417-430 (2019)
            { "jd": 2337769, "cs_year": 1050, "cs_month": 8,  "cs_day": 1,  },
            { "jd": 2337872, "cs_year": 1050, "cs_month": 11, "cs_day": 15, },
            { "jd": 2337919, "cs_year": 1050, "cs_month": 1,  "cs_day": 3,  },
            { "jd": 2337924, "cs_year": 1050, "cs_month": 1,  "cs_day": 8,  },
            # misc
            { "jd": 2392478, "cs_year": 1200, "cs_month": 5,  "cs_day": 19, },  # NYD
            { "jd": 2392815, "cs_year": 1200, "cs_month": 15, "cs_day": 1,  },  # Caitra2 1
            { "jd": 2392844, "cs_year": 1201, "cs_month": 6,  "cs_day": 1,  },  # NYD
            { "jd": 2393199, "cs_year": 1201, "cs_month": 15, "cs_day": 1,  },  # Caitra2 1
            { "jd": 2392934, "cs_year": 1201, "cs_month": 88, "cs_day": 2,  },  # 88 1
            # 800 year exceptions
            { "jd": 2049500, "cs_year": 260, "cs_month": 15,  "cs_day": 9,  },
            { "jd": 2341707, "cs_year": 1060, "cs_month": 15,  "cs_day": 11,  },
            { "jd": 2633914, "cs_year": 1860, "cs_month": 15,  "cs_day": 13,  },
            { "jd": 2926121, "cs_year": 2660, "cs_month": 15,  "cs_day": 15,  },
        )
        for t in tests:
            year = t["cs_year"]
            month = t["cs_month"]
            day = t["cs_day"]
            if month == 15 or month == 16:
                month -= 10
            y0 = CsDate.fromjulianday(t["jd"])
            logging.debug("y0.jd:%s %s-%s-%s", y0.julianday, y0.year, y0.month, y0.day)
            y1 = CsDate(year, month, day)
            logging.debug("y1.jd:%s %s-%s-%s", y1.julianday, y1.year, y1.month, y1.day)
            self.assertEqual(y0, y1, (t["jd"], y0.julianday, y1.julianday, y0.julianday - y1.julianday))
            self.assertEqual(
                (y0.year, y0.month_raw, y0.day), (t["cs_year"], t["cs_month"], t["cs_day"]),
                (t["jd"], y0._hashable(), (t["cs_year"], t["cs_month"], t["cs_day"]))
            )
            self.assertEqual(
                (y1.year, y1.month_raw, y1.day), (t["cs_year"], t["cs_month"], t["cs_day"]),
                (t["jd"], y1._hashable(), (t["cs_year"], t["cs_month"], t["cs_day"]))
            )

    def test_compare_yd_ymd(self):
        for y, d in self.random_dates(max_year=2100):
            logging.debug("- ----------------------------")
            yd = CsDate.fromyd(y, d)
            logging.debug("yd: %s", yd)
            # td = TESTDATA[yd.horakhun - 1]
            # cs_month = 5 if td["cs_month"] == "C" else 6
            # self.assertEqual((yd.year, yd.month, yd.day), (td["cs_year"], cs_month, td["cs_day"]),
            #                  (yd.horakhun, td))
            ymd = CsDate(yd.year, yd.month, yd.day)
            logging.debug("ymd: %s", ymd)
            self.assertEqual(yd, ymd, 
                "y_d(y:{:04d} d:{}) {}\nymd(y:{:04d} m:{} d:{}) {}".format(
                    y, d, yd._hashable(),
                    yd.year, yd.month, yd.day, ymd._hashable(),
                )
            )

    def test_yd_to_horakhun(self):
        for t in TESTDATA:
            cs = CsDate.fromyd(year=t["cs_year"], days=0)
            self.assertEqual(cs.horakhun, t["cs_hk"])

    def test_comparison_operations(self):
        y0 = CsDate.fromyd(year=1000, days=0)
        y1 = CsDate.fromyd(year=1001, days=0)
        self.assertGreater(y1, y0)
        self.assertGreaterEqual(y1, y0)
        self.assertLess(y0, y1)
        self.assertLessEqual(y0, y1)
        self.assertEqual(y0, y0)

    def test_comparison_operations_dates(self):
        cs = CsDate(655, 5, 18)  # AD 1293-03-27
        d0 = date(1200, 1, 1)
        d1 = date(1293, 3, 27)
        d2 = date(1300, 1, 1)
        self.assertLess(d0, cs, (julianday.date_to_julianday(d0), cs.julianday))
        self.assertLessEqual(cs, d1)
        self.assertEqual(cs, d1)
        self.assertGreaterEqual(cs, d1)
        self.assertGreater(d2, cs)

    def test_comparison_operations_exceptions(self):
        cs = CsDate(655, 5, 18)  # AD 1293-03-27
        with self.assertRaises(TypeError):
            cs < "Fail <"
        with self.assertRaises(TypeError):
            cs <= "Fail <="
        self.assertFalse(cs == "Fail")
        with self.assertRaises(TypeError):
            cs >= "Fail >="
        with self.assertRaises(TypeError):
            cs > "Fail >"

    def test_replace(self):
        y = CsDate(1200, 5, 19)
        r = y.replace(year=1201, month=6, day=20)
        self.assertEqual(r.year, 1201)
        self.assertEqual(r.month, 6)
        self.assertEqual(r.day, 20)

    def test_weekday(self):
        y = CsDate(1200, 5, 19)
        self.assertEqual(y.weekday(), 4)
        self.assertEqual(y.isoweekday(), 5)
        self.assertEqual(y.csweekday(), 6)

    def test_cscalendar(self):
        y = CsDate(1200, 5, 19)
        nt = y.cscalendar()
        self.assertEqual(nt.year, y.year)
        self.assertEqual(nt.month, y.month)
        self.assertEqual(nt.day, y.day)

    def test_csformat(self):
        for y, d in self.random_dates():
            y0 = CsDate.fromyd(year=y, days=d)
            s = y0.csformat()
            y1 = CsDate.fromcsformat(s)
            self.assertEqual(y0, y1), (y0, s, y1)

    def test_fromjulianday(self):
        for y, d in self.random_dates():
            y0 = CsDate.fromyd(year=y, days=d)
            y1 = CsDate.fromjulianday(y0.julianday)
            self.assertEqual(y0, y1, 
                (y, d, 
                y0.julianday, y0._hashable(),
                y1.julianday, y1._hashable()
            ))

    def test_fromtimestamp(self):
        cs = CsDate.fromtimestamp(946758689)
        dt = date(2000, 1, 1)
        self.assertEqual(cs.julianday, dt.julianday)

    def test_add_timedelta(self):
        for y, d in self.random_dates():
            r = random.randint(0, 500)
            logging.debug("- ----------------------------")
            y0 = CsDate.fromyd(year=y, days=d)
            logging.debug("y0.jd:%s", y0.julianday)
            logging.debug("r:%s", r)
            td = timedelta(days=r)
            y1 = y0 + td
            logging.debug("y1.jd:%s", y1.julianday)
            logging.debug(
                "y0:{:d} + {:d} = {:d}  |  y1:{:d} (diff:{:d} d+r={:d})".format(
                     y0.julianday, r, y0.julianday + r, 
                     y1.julianday, 
                     y0.julianday + r - y1.julianday, r + d
                )
            )
            self.assertEqual(y0.julianday + r, y1.julianday,
                "y0:{:d} + {:d} = {:d}  |  y1:{:d} (diff:{:d} d+r={:d})".format(
                     y0.julianday, r, y0.julianday + r,
                     y1.julianday, 
                     y0.julianday + r - y1.julianday, r + d
                )
            )

    def test_add_typeerror(self):
        cs = CsDate.fromyd(year=1000, days=0)
        with self.assertRaises(TypeError):
            cs + None

    def test_subtract_timedelta(self):
        for y, d in self.random_dates(min_year=200, max_year=1000):
            y0 = CsDate.fromyd(year=y, days=d)
            r = random.randint(0, 1000)
            td = timedelta(days=r)
            y1 = y0 - td
            self.assertEqual(y1.julianday, y0.julianday - r, 
                             (y0.julianday, "-", r, "!=", y1.julianday, "diff:", y0.julianday - r - y1.julianday,
                              (y0.year, y0.month, y0.day), (y1.year, y1.month, y1.day)))

    def test_subtract_dates(self):
        count = 0
        while True:
            d1 = CsDate.fromyd(year=random.randint(0, 1500), days=random.randint(0, 355))
            d2 = CsDate.fromyd(year=random.randint(0, 1500), days=random.randint(0, 355))
            if d1 == d2:
                continue
            a, b = sorted([d1, d2])
            result = b - a
            self.assertEqual(result.days, b.julianday - a.julianday)
            count += 1
            if count == 1000:
                break

        # test with date object
        cs = CsDate(655, 5, 18)  # AD 1293-03-27
        dt = date(1293, 3, 20)
        self.assertEqual(cs - dt, timedelta(days=7))


    def test_today(self):
        t1 = julianday.today()
        t2 = CsDate.today()
        self.assertEqual(t1, t2.julianday)

    def test_naksatr(self):
        TESTS = (
            {"cs":[1152, 5, 1], "ns":"ปีจอ"},
            {"cs":[1338, 10, 18], "ns":"ปีมะโรง"},
        )
        for t in TESTS:
            c = CsDate(*t["cs"])
            self.assertEqual(c.yearnaksatr, t["ns"])

    # ################################################################################

    # def test_chart_19_years(self):
    #     group_size = 19
    #     output = [[]]
    #     for y in range(0, 1462):
    #         c = Chulasakarat(year=y, days=0)
    #         if c.leap_day:
    #             output[-1].append("D")
    #         elif c.leap_month:
    #             output[-1].append("M")
    #         else:
    #             output[-1].append(".")
    #         if len(output[-1]) == group_size:
    #             output.append([])
    #     y = 0
    #     for i in output:
    #         cal = " ".join(i)
    #         count_d = 0
    #         count_m = 0
    #         for c in i:
    #             if c == "M":
    #                 count_m += 1
    #             elif c == "D":
    #                 count_d += 1
    #         print("{:4d}  {:37s}  d:{} m:{}".format(
    #             y, cal, count_d, count_m
    #         ))
    #         y += group_size

if __name__ == '__main__':
    unittest.main()

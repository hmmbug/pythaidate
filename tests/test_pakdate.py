from datetime import date, timedelta
import json
import unittest
import os
import pathlib
import random

import logging

from pythaidate import PakDate, CsDate, julianday
from pythaidate.constants import PAK_JULIAN_DAY_OFFSET

RUN_PERCENT = 10
if os.environ.get("RUN_PERCENT"):
    RUN_PERCENT = int(os.environ.get("RUN_PERCENT"))
    if RUN_PERCENT > 100:
        RUN_PERCENT = 100


for datafile in ("pak.data", "pak.min.data"):
    datafile = os.path.join(pathlib.Path(__file__).parent.resolve(), "data", datafile)
    if os.path.exists(datafile):
        break
else:
    raise FileNotFoundError("Pak data file not found.")

random.seed()

def read_test_date(sample=1, minjd=None):
    data = []
    with open(datafile) as fh:
        for ln in fh:
            if random.random() > sample:
                continue
            i = ln.rstrip().split(" ")
            y, m, d = i[4].split("-")
            e = {
                "pakcode": i[0],
                "jd": int(i[1][3:]),
                "hk": int(i[2][3:]),
                "masak": int(i[3][6:]),
                "year": int(y),
                "month": int(m),
                "day": int(d),
            }
            if minjd and e["jd"] < minjd:
                continue
            if e["jd"] > 2644223:
                # test data is erroreous beyond this point
                break
            data.append(e)
    return data

TESTDATA = read_test_date(sample=RUN_PERCENT/100)


class Test_PakDate(unittest.TestCase):

    def test_jd_pre_epoch(self):
        with self.assertRaises(ValueError):
            # pre-epoch jd
            p = PakDate(jd=PAK_JULIAN_DAY_OFFSET - 5)

    def test_jd_to_pakcode(self):
        for t in TESTDATA:
            p = PakDate(jd=t["jd"])
            self.assertEqual(t["pakcode"], p.pakcode, (t, p.debug()))

    def test_pakcode_to_jd(self):
        for t in TESTDATA:
            p = PakDate(pakcode=t["pakcode"])
            self.assertEqual(p.julianday, t["jd"], (p.debug(), t))
            self.assertEqual(p.horakhun, t["hk"])

    def test_date_to_pakcode(self):
        for t in TESTDATA:
            d = date(t["year"], t["month"], t["day"])
            p = PakDate(date=d)
            self.assertEqual(t["pakcode"], p.pakcode, (t, p.debug()))

    def test_adhoc(self):
        data = [
            { "jd":2454103, "ad":"2007-01-02", "pakcode":"1-7:2:2:4:5:13"},  # hk 98956 - invalid pakcode? 7:2:2:5:1:14 -> 7:2:2:4:5:13
            { "jd":2458526, "ad":"2019-02-11", "cs":"1380-03-07", "pakcode":"1-7:5:3:2:2:7"},
            { "jd": 2628291, "pakcode": "1-17:10:6:3:4:15", "hk": 273144, "masak": 18499, "year": 2483, "month": 11, "day": 30},
            { "jd": 2460257, "pakcode": "1-7:6:4:2:4:10"},
            { "jd": 2749834, "pakcode": "2-7:6:4:2:4:10"},  # above pakcode + 1 cycle            
        ]
        for t in data:
            p = PakDate(jd=t["jd"])
            if "ad" in t:
                ad = date(*julianday.from_julianday(p.julianday)).isoformat()
                self.assertEqual(t["ad"], ad)
            if "cs" in t:
                cs = CsDate.from_julianday(p.julianday)
                self.assertEqual(t["cs"], cs.csformatymd())
            if "pakcode" in t:
                self.assertEqual(t["pakcode"], p.pakcode)

    def test_pakcode_to_date(self):
        for t in TESTDATA:
            p = PakDate(pakcode=t["pakcode"])
            dtp = date(*julianday.from_julianday(p.julianday)).isoformat()
            dtt = "{:4d}-{:02d}-{:02d}".format(t["year"], t["month"], t["day"])
            self.assertEqual(dtt, dtp, (t, p.debug()))

    def test_pakcode(self):
        for t in TESTDATA:
            p = PakDate(jd=t["hk"] + PAK_JULIAN_DAY_OFFSET)
            self.assertEqual(p.pakcode, t["pakcode"])

    def test_pakkhagen(self):
        TESTS = (
            (1, 1),
            (38878, 2634),
            (81517, 5521),
        )
        for hk, pkg in TESTS:
            p = PakDate(jd=hk + PAK_JULIAN_DAY_OFFSET)
            self.assertEqual(pkg, p.pakkhagen, (hk, pkg, p.pakkhagen))

    def test_pakabbr(self):
        TESTS = (
            ("๑ก๑ก๑", 1),
            ("๓ห๔ก๑", 38878),
            ("๖ก๓ฅจ", 81517),
        )
        for abbr, hk in TESTS:
            p = PakDate(jd=hk + PAK_JULIAN_DAY_OFFSET)
            self.assertEqual(abbr, p.pakabbr, (hk, abbr, p.pakabbr))

    def test_str(self):
        TESTS = (
            ("มหาสัมพยุหะ ๗ จุลพยุหะ ๖ มหาสมุหะ ๔ จุลวรรค ๓ มหาปักข์ ๑ ขึ้น ๕ ค่ำ (ปักข์ถ้วน)", 105119),
            ("มหาสัมพยุหะ ๖ จุลพยุหะ ๑ มหาสมุหะ ๓ มหาวรรค ๔ มหาปักข์ ๑ ขึ้น ๑๐ ค่ำ (ปักข์ถ้วน)", 81529),
            ("มหาสัมพยุหะ ๖ จุลพยุหะ ๑ มหาสมุหะ ๓ จุลวรรค ๓ จุลปักข์ ๔ แรม ๑๒ ค่ำ (ปักข์ขาด)", 81517),
        )
        for s, hk in TESTS:
            p = PakDate(jd=hk + PAK_JULIAN_DAY_OFFSET)
            self.assertEqual(str(p), s)

    def test_comparison_operations(self):
        y0 = PakDate(jd=2454103)
        y1 = PakDate(jd=2458526)
        self.assertLess(y0, y1)
        self.assertLessEqual(y0, y0)
        self.assertEqual(y0, y0)
        self.assertGreater(y1, y0)
        self.assertGreaterEqual(y1, y1)

    def test_comparison_operations_dates(self):
        p0 = PakDate(jd=2454102)
        p1 = PakDate(jd=2454103)
        p2 = PakDate(jd=2454104)
        y0 = julianday.julianday_to_date(2454102)
        y1 = julianday.julianday_to_date(2454103)
        y2 = julianday.julianday_to_date(2454104)
        self.assertLess(y0, p1)
        self.assertLessEqual(p0, y1)
        self.assertEqual(p1, y1)
        self.assertGreaterEqual(p2, y1)
        self.assertGreater(p2, y1)

    def test_weekday(self):
        y = PakDate(jd=2454103)
        self.assertEqual(y.weekday(), 3)
        self.assertEqual(y.isoweekday(), 4)

    def test_add_timedelta(self):
        for jd in [random.randint(2454000, 2454999) for _ in range(200)]:
            p0 = PakDate(jd=jd)
            r = random.randint(0, 1000)
            td = timedelta(days=r)
            p1 = p0 + td
            self.assertEqual(p0.julianday + r, p1.julianday)

    def test_add_dates(self):
        pass

    def test_add_typeerror(self):
        y = PakDate(jd=2454103)
        with self.assertRaises(TypeError):
            y + None

    def test_subtract_timedelta(self):
        for jd in [random.randint(2454000, 2454999) for _ in range(200)]:
            p0 = PakDate(jd=jd)
            r = random.randint(0, 1000)
            td = timedelta(days=r)
            p1 = p0 - td
            self.assertEqual(p0.julianday - r, p1.julianday)

    def test_subtract_dates(self):
        count = 0
        while True:
            d1 = PakDate(jd=2454000 + random.randint(0, 999))
            d2 = PakDate(jd=2454000 + random.randint(0, 999))
            if d1 == d2:
                continue
            a, b = sorted([d1, d2])
            result = b - a
            self.assertEqual(result.days, b.julianday - a.julianday)
            count += 1
            if count == 1000:
                break

    def test_today(self):
        t1 = julianday.today()
        t2 = PakDate.today()
        self.assertEqual(t1, t2.julianday)

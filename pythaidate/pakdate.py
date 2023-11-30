from datetime import date, timedelta
import logging

from io import StringIO
import math
from pprint import pprint
import sys

from . import julianday
from .constants import PAK_JULIAN_DAY_OFFSET, PAK_DAYS_IN_CYCLE
from .helpers import thai_string_width, digit_arabic_to_thai

__all__ = (
    "PakDate",
)

layout = [
    # 0 -> จุล~, 1 -> มหา~
    # ปักขคณนา
    [   [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0 ] ],
    # สัมพยุหะ
    [   [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ],
        [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ] ],
    # พยุหะ
    [   [ 1, 1, 1, 1, 1, 1, 0 ],
        [ 1, 1, 1, 1, 1, 0 ] ],
    # สมุหะ
    [   [ 0, 0, 0, 1 ],
        [ 0, 0, 1 ] ],
    # วรรค
    [   [ 1, 1, 1, 1, 0 ],
        [ 1, 1, 1, 0 ] ],
]


class PakDate:

    def __init__(self, jd=None, pakcode=None, date=None):
        # assert jd is not None or pakcode is not None or date is not None
        self.__julianday = None
        self.__horakhun = None
        self.__pakkhagen = None
        self.__cycle = None
        self.__data = [0, 0, 0, 0, 0, 0]
        self.__pos = [None, None, None, None, None, None]
        self.__pakabbr = None

        if jd:
            self.__convert_julianday(jd)

        elif pakcode:
            self.__convert_pakcode(pakcode)

        elif date:
            jd = julianday.date_to_julianday(date)
            self.__convert_julianday(jd)

    @classmethod
    def today(cls):
        """Return today as Pak date."""
        return cls(jd=julianday.today())

    @classmethod
    def fromjulianday(cls, jd):
        """Class method for Julian Day Number conversion."""
        return cls(jd=jd)

    # @classmethod
    # def frompakcode(cls, pakcode):
    #     """Return Pak object from format string (x-a:b:c:d:e:f)."""
    #     return cls(pakcode=pakcode)

    def __convert_julianday(self, jd):
        """Convert from Julian Day Number."""
        def div(a, b):
            c = 0
            while True:
                if b >= a:
                    return c + 1, a
                a -= b
                c += 1

        def _adjust(row, prefix, col):
            logging.debug("_adjust_1(%s, %s, %s)", row, 1-prefix, col-1)
            if col > len(layout[row][1-prefix]):
                rtn = None
            else:
                rtn = layout[row][1-prefix][col-1]
            logging.debug("_adjust_1(%s, %s, %s) -> %s", row, 1-prefix, col-1, rtn)
            return rtn

        self.__julianday = jd
        self.__horakhun = jd - PAK_JULIAN_DAY_OFFSET
        if self.__horakhun <= 0:
            raise ValueError("Invalid Pakkhakhananaa range.")

        days = self.__horakhun % PAK_DAYS_IN_CYCLE
        if days == 0:
            days = PAK_DAYS_IN_CYCLE
        self.__cycle = math.ceil(self.__horakhun / PAK_DAYS_IN_CYCLE)

        # ปักขคณนา row
        self.__data[0], rem = div(days, 16168)
        self.__pos[0] = (0, self.__data[0]-1)
        mahachula = layout[0][0][self.__data[0]-1]
        logging.debug("0 data:%s, mc:%s", self.__data, self.__pos)

        # สัมพยุหะ, พยุหะ, สมุหะ, วรรค rows
        for row, divisor in ((1, 1447), (2, 251), (3, 59), (4, 15)):
            self.__data[row], rem = div(rem, divisor)
            mahachula1 = _adjust(row, mahachula, self.__data[row])
            # logging.debug("L: row:%s div:%s -> d[r]:%s rem:%s | mc:%s mc1:%s", row, divisor, self.__data[row], rem, mc, mc1)
            if mahachula1 is None:
                # the row position is too large - decrement it by one and add
                # the divisor back on to rem for the next iteration. Do the
                # adjustment again and it should be correct.
                self.__data[row] -= 1
                rem += divisor
                mahachula1 = _adjust(row, mahachula, self.__data[row])
            self.__pos[row] = (1-mahachula, self.__data[row]-1)  # display_pattern[row][self.__mahachula[row]][mc-1]
            # logging.debug("L: %s data:%s, mc:%s", row, self.__data, self.__pos)
            mahachula = mahachula1

        # วัน (ค่ำ)
        self.__data[5] = rem
        self.__pos[5] = (mahachula, self.__data[5]-1)  # display_pattern[row][self.__mahachula[4]][mc-1]
        logging.debug("F: %s %s %s", self.__cycle, self.__data, self.__pos)

    def __convert_pakcode(self, s):
        """Convert a Pak string (x-a:b:c:d:e:f) to a state object."""
        cyc, pak = s.split("-")
        cyc = int(cyc)
        assert cyc > 0, ValueError("Invalid Pak string.")
        a, b, c, d, e, f = map(int, pak.split(":"))
        jd = (e - 1) * 15 + f
        jd = (d - 1) * 59 + jd
        jd = (c - 1) * 251 + jd
        jd = (b - 1) * 1447 + jd
        jd = (a - 1) * 16168 + jd
        jd += (cyc - 1) * PAK_DAYS_IN_CYCLE
        jd += 2355147
        self.__convert_julianday(jd)

    @property
    def julianday(self):
        # if self.__julianday is None:
        #     self.__julianday = self.horakhun + PAK_JULIAN_DAY_OFFSET
        return self.__julianday

    @property
    def horakhun(self):
        """
        Days since the Pakkhakhananaa epoch (1736-01-28 A.D., 2279-01-28 B.E.).(Thai: หรคุฌ)
        """
        # if self.__horakhun is None:
        #     self.__horakhun = (self.__data[0] - 1) * 16168 + \
        #                       (self.__data[1] - 1) * 1447 + \
        #                       (self.__data[2] - 1) * 251 + \
        #                       (self.__data[3] - 1) * 59 + \
        #                       (self.__data[4] - 1) * 15 + \
        #                       self.__data[5]
        return self.__horakhun

    @property
    def pakkhagen(self):
        """
        Number of lunar (14/15) day weeks since the epoch. (Thai: ปักขเกณฑ์)
        """
        if self.__pakkhagen is None:
            self.__pakkhagen = (self.__cycle - 1) * 19612 + \
                               (self.__data[0] - 1) * 1095 + \
                               (self.__data[1] - 1) * 98 + \
                               (self.__data[2] - 1) * 17 + \
                               (self.__data[3] - 1) * 4 + \
                               self.__data[4]
        return self.__pakkhagen

    @property
    def pakcode(self):
        return "{:d}-{:d}:{:d}:{:d}:{:d}:{:d}:{:d}".format(self.__cycle, *self.__data)

    @property
    def pakabbr(self):
        """
        Returns a string in "เลขใช้บอกปักข์" format
        """
        def _digit1(d):
            return d // 10 if d > 9 else d

        def _digit2(d):
            return d % 10 if d > 9 else " "

        def _ctrans(c):
            return c if c == " " else "กขฅจหฉษฐฬฮ"[c-1]

        def _ntrans(c):
            return c if c == " " else "๐๑๒๓๔๕๖๗๘๙"[c]

        if self.__pakabbr is None:
            s1, s2 = [], []
            for i in range(5):
                v = self.__data[i]
                mahachula, col = self.__pos[i]
                if layout[i][mahachula][col] == 0:
                    s1.append(_ctrans(_digit1(v)))
                    s2.append(_ctrans(_digit2(v)))
                else:
                    s1.append(_ntrans(_digit1(v)))
                    s2.append(_ntrans(_digit2(v)))
            self.__pakabbr = "".join(s1) + "\n" + "".join(s2)
        return self.__pakabbr.rstrip()

    @property
    def iswaxing(self):
        return self.pakkhagen % 2 == 0

    @property
    def iswaning(self):
        return self.pakkhagen % 2 == 1

    def weekday(self):
        return self.__horakhun % 7 - 1

    def isoweekday(self):
        return self.__horakhun % 7

    def debug(self):
        return {
            "pakcode": self.pakcode,
            "jd": self.__julianday,
            "hk": self.__horakhun,
            "pakkhagen": self.__pakkhagen,
        }

    def pakboard(self, fh=None):
        def _display():
            def _stringify(b):
                max_prefix_len = max(map(lambda x: thai_string_width(x[0]), board))
                for r in board:
                    numspaces = max_prefix_len - thai_string_width(r[0])
                    r[0] = r[0] + " " * numspaces
                return max_prefix_len

            max_prefix_len = _stringify(board)
            blank = " " * (max_prefix_len - 1)
            headings = digit_arabic_to_thai(" ".join(["{:>2d}".format(i) for i in range(1, 19)]))
            print(blank + "  " + headings, file=fh)
            for i, r in enumerate(board):
                content = []
                for c in r[1:]:
                    fmt = "\033[;7m{:>2s}\033[0;0m" if c & 0x80 else "{:>2s}"
                    if i < 9:
                        c = "ม" if c & 0x7F == 1 else "จ"
                    else:
                        c = digit_arabic_to_thai(str(c & 0x7f))
                    content.append(fmt.format(c))
                print("{:s} {:s}".format(r[0], " ".join(content)), file=fh)
            print(" ".join([
                blank, " ",
                "รอบที่", digit_arabic_to_thai(self.__cycle), " ",
                "หรคุณปักขคณนา", digit_arabic_to_thai(self.horakhun), " ",
                "ปักขเกณฑ์", digit_arabic_to_thai(self.pakkhagen)
            ]), file=fh)

        if fh is None:
            fh = sys.stdout

        # setup board
        board = [
            ["ปักขคณนา", *layout[0][0]],
            ["มหาสัมพยุหะ", *layout[1][0]],
            ["จุลสัมพยุหะ", *layout[1][1]],
            ["มหาพยุหะ", *layout[2][0]],
            ["จุลพยุหะ", *layout[2][1]],
            ["มหาสมุหะ", *layout[3][0]],
            ["จุลสมุหะ", *layout[3][1]],
            ["มหาวรรค", *layout[4][0]],
            ["จุลวรรค", *layout[4][1]],
            ["มหาปักข์", *list(range(1,16))],
            ["จุลปักข์", *list(range(1,15))],
        ]

        # highlight row items
        for i in range(6):
            mahachula, col = self.__pos[i]
            row = 0 if i == 0 else i * 2 - 1 + mahachula
            board[row][col+1] += 0x80  # Set MSB to 1 as a "selected" flag
        _display()

    def __str__(self):
        # มหาสัมพยุหะ 6 จุลพยุหะ 5 จุลสมุหะ 6 จุลวรรค 2 จุลปักข์ 4 ขึ้น 3 ค่ำ (ปักข์ขาด / ปักข์ถ้วน)
        output = []
        next_row = 0
        for i, label in enumerate(("สัมพยุหะ", "พยุหะ", "สมุหะ", "วรรค", "ปักข์")):
            val = layout[i][next_row][self.__data[i]-1]
            output += [("มหา" if val else "จุล") + label, str(self.__data[i])]
            next_row = 1 - val
        output += ["ขึ้น" if self.iswaxing else "แรม",
                   str(self.__data[5]),
                   "ค่ำ",
                   "(" + ("ปักข์ขาด" if next_row else "ปักข์ถ้วน") + ")"]
        return digit_arabic_to_thai(" ".join(output))

    def __lt__(self, other):
        if hasattr(other, "julianday"):
            return self.julianday < other.julianday
        elif isinstance(other, date):
            return self.julianday < julianday.to_julianday(other.year, other.month, other.day)
        return NotImplemented

    def __le__(self, other):
        if hasattr(other, "julianday"):
            return self.julianday <= other.julianday
        elif isinstance(other, date):
            return self.julianday <= julianday.to_julianday(other.year, other.month, other.day)
        return NotImplemented

    def __eq__(self, other):
        if hasattr(other, "julianday"):
            return self.julianday == other.julianday
        elif isinstance(other, date):
            return self.julianday == julianday.to_julianday(other.year, other.month, other.day)
        return NotImplemented

    def __ge__(self, other):
        if hasattr(other, "julianday"):
            return self.julianday >= other.julianday
        elif isinstance(other, date):
            return self.julianday >= julianday.to_julianday(other.year, other.month, other.day)
        return NotImplemented

    def __gt__(self, other):
        if hasattr(other, "julianday"):
            return self.julianday > other.julianday
        elif isinstance(other, date):
            return self.julianday > julianday.to_julianday(other.year, other.month, other.day)
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, timedelta):
            return PakDate.fromjulianday(self.julianday + other.days)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return self + timedelta(-other.days)
        elif hasattr(other, "julianday"):
            return timedelta(days=self.julianday - other.julianday)
        elif isinstance(other, date):
            other_jd = julianday.to_julianday(other.year, other.month, other.day)
            return timedelta(days=self.julianday - other_jd)
        return NotImplemented

    def debug_reset(self):  # pragma: no cover
        self.__horakhun = None
        self.__julianday = None
        self.__pakkhagen = None
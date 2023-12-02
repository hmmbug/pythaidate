import logging
from collections import namedtuple
from datetime import date, timedelta

from .constants import (
    DAYS_IN_800_YEARS,
    TIME_UNITS_IN_1_DAY,
    EPOCH_OFFSET,
    UCCAPON_CONSTANT,
    APOGEE_ROTATION_DAYS,
    WEEKDAYS,
    CS_JULIAN_DAY_OFFSET,
    CAL_TYPE_DAY_COUNTS,
    CS_MIN_JULIANDAY,
    CS_UNIX_EPOCH_OFFSET,
)

from .lsyear import LSYear
from .helpers import digit_arabic_to_thai, digit_thai_to_arabic
from . import julianday

__all__ = (
    "CsDate",
    # "CsCalendarDate"
)

CsCalendarDate = namedtuple("CsCalendarDate", ["year", "month", "day"])

# Month offsets
MONTH_SUK = 4
MONTH_KT = 5
MONTH_CM = 6

MONTH_CUMULATIVE_DAYS = {
    "A": (0, 29, 59, 88, 118, 147, 177, 206, 236, 265, 295, 324, 354, 383),
    "B": (0, 29, 59, 89, 119, 148, 178, 207, 237, 266, 296, 325, 355, 384),
    "C": (0, 29, 59, 88, 118, 148, 177, 207, 236, 266, 295, 325, 354, 384),
}
# LUNAR_MONTHS = (0, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 8, 88, 5, 6)
LUNAR_MONTHS = (
    0,
    5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4,
    8, 88, 15, 16
)

MONTH_POSITION_AB = (None, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 15, 16)
MONTH_POSITION_C = (None, 5, 6, 7, 8, 88, 9, 10, 11, 12, 1, 2, 3, 4, 15, 16)

YEAR_NAKSATR = [None, "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง",
                "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน"]


class CsDate:

    def __init__(self, year: int, month: int=None, day: int=None,
                 month_style: int = MONTH_SUK):
        logging.debug("args year:%s month:%s day:%s, month_style:%s",
                      year, month, day, month_style)
        self.__year = year
        self.__month = month
        self.__day = day  # day of month
        self.__days = None  # days elapsed in year
        self.__month_style = month_style  # Sukothai, Chiang Mai, Keng Tung
        self.__init_ymd()
        self.__calculate()
        logging.debug("final y:%s m:%s d:%s days:%s",
                      self.__year, self.__month, self.__day, self.__days)

    def __init_ymd(self):
        """
        Initialise from year, month and day args.
        """
        self.__year0 = self.calculate_year0(self.__year)
        # logging.debug("offset_days:%d", self.__year0.offset_days)

        date_offset = None
        if self.__month == 5:
            date_offset = self.__day
        elif self.__month == 6:
            date_offset = 29 + self.__day

        MP = MONTH_POSITION_C if self.__year0.cal_type == "C" else MONTH_POSITION_AB
        tmonth = MP.index(self.__month)
        if date_offset and date_offset < self.__year0.offset_days:
            # this is a month 5 or 6 date at end of the year
            tmonth += 13 if self.__year0.cal_type == "C" else 12
            # shift month number to end of the index in LUNAR_MONTHS[]
            self.__month += 10
        self.__days = MONTH_CUMULATIVE_DAYS[self.__year0.cal_type][tmonth-1] + self.__day - self.__year0.offset_days
        logging.debug("ymd: y:%s m:%s d:%s days:%s cal_type:%s tmonth:%s",
                      self.__year, self.__month, self.__day,
                      self.__days, self.__year0.cal_type, tmonth)

    def __calculate(self):
        # horakhun: The number of elapsed days since epoch plus days since New Year's Day (Thai: หรคุฌ)
        self.__horakhun = (self.__year * DAYS_IN_800_YEARS + EPOCH_OFFSET) // TIME_UNITS_IN_1_DAY + 1 + self.__days
        assert self.julianday >= CS_MIN_JULIANDAY  # check for pre-epoch dates

        # kammabucapon: A quantity that gives the excess of solar days over whole solar days (Thai: กัมมัขผล)
        self.__kamma = TIME_UNITS_IN_1_DAY - (self.__year * DAYS_IN_800_YEARS + EPOCH_OFFSET) % TIME_UNITS_IN_1_DAY

        # uccapon: The measure of the position of the Moon's apogee. It increases by one unit a day to
        # a maximum of 3232 (Thai: อุจจพล)
        self.__uccapon = (self.__horakhun + UCCAPON_CONSTANT) % APOGEE_ROTATION_DAYS

        # avoman: The excess of lunar days over solar days in units of 1/692 of a lunar day modulus 692.
        # It increases by 11 units each solar day. It is used to determine when to add intercalary days
        # in the calendar (Thai: อวมาน)
        self.__avoman = (self.__horakhun * 11 + 650) % 692
        if self.__avoman == 0:
            self.__avoman = 692

        # masaken: Number of lunar months since the epoch (Thai: มาสเกฌฑ์)
        avoman_div = ((self.__horakhun + self.days) * 11 + 650) // 692
        self.__masaken = (avoman_div + self.__horakhun) // 30

        # tithi: a lunar day, equal to 1/30th of a synodic month (Thai: ดิถี)
        quot = (self.__horakhun * 11 + 650) // 692
        self.__tithi = (quot + self.__horakhun) % 30

        # self.avomanExtra = (self.horakhun * 11 + 650) % 692
        logging.debug("horakhun:%s kamma:%s quot:%s tt:%s", self.__horakhun, self.__kamma, quot, self.__tithi)

    @staticmethod
    def calculate_year0(year: int):
        y = [
            LSYear(year - 2),
            LSYear(year - 1),
            LSYear(year),
            LSYear(year + 1),
            LSYear(year + 2),
        ]
        # logging.debug("[0] year0[].caltype:%s", "".join([i.cal_type for i in y]))

        for i in (0, 1, 2, 3, 4):
            if y[2].tithi == 24 and y[3].tithi == 6:
                # where tithi of this year is 24 and next year is 6, set all years to C-type
                # adjust next_nyd weekday
                y[i].cal_type = "C"
                y[i].next_nyd = (y[i].next_nyd + 2) % 7
        # logging.debug("[1] year0[].caltype:%s", "".join([i.cal_type for i in y]))

        # Adjust c-type years where a intercalary day and month coincide. This can't happen
        # in the Thai calendar (unlike the Burmese) so we decide if the intercalary day is moved
        # to the previous or next year. This is done by ensuring a correct sequence of weekdays
        # from one year to the next.
        for i in (1, 2, 3):
            if y[i].cal_type == "c":
                j = 1 if y[i].nyd == y[i-1].next_nyd else -1
                y[i+j].cal_type = "B"
                y[i+j].next_nyd = (y[i+j].next_nyd + 1) % 7
                # if y[i].nyd != y[i-1].next_nyd:
                #     y[i-1].cal_type = "B"
                #     y[i-1].next_nyd = (y[i-1].next_nyd + 1) % 7
                # else:
                #     y[i+1].cal_type = "B"
                #     y[i+1].next_nyd = (y[i+1].next_nyd + 1) % 7
        # logging.debug("[2] year0[].caltype:%s", "".join([i.cal_type for i in y]))

        for i in (1, 2, 3):
            if y[i-1].next_nyd != y[i].nyd and y[i].next_nyd != y[i+1].nyd:
                y[i].offset = True
                y[i].langsak += 1
                y[i].nyd = (y[i].nyd + 6) % 7
                y[i].next_nyd = (y[i].next_nyd + 6) % 7

        # housekeeping - elabal any remaining c-type years as C-type; add day count too
        for i in (0, 1, 2, 3, 4):
            if y[i].cal_type == "c":
                y[i].cal_type = "C"
            y[i].caldays = CAL_TYPE_DAY_COUNTS[y[i].cal_type]
        # logging.debug("[F] year0[].caltype:%s", "".join([i.cal_type for i in y]))

        # Determine month/day of new year
        y[2].first_month = "C"  # as per Eade, C=>Caitra, V=>Vaisakha
        y[2].first_day = y[2].langsak
        y[2].offset_days = y[2].langsak  # no.days offset from Caitra 1st
        if y[2].offset_days < (6 + int(y[2].offset)):
            y[2].first_month = "V"
            y[2].first_day = y[2].offset_days
            y[2].offset_days += 29
        return y[2]

    @staticmethod
    def find_date(cal: str, days: int):
        """
        Given a calendar type (A, B, C) and number of days since new years day,
        return the month and day component of a date, derived from lookup tables.
        """
        logging.debug("cal:%s days:%s", cal, days)
        vals = {
            "A": (
                (383, 16), (354, 15), (324, 12), (295, 11), (265, 10), (236, 9),
                (206, 8), (177, 7), (147, 6), (118, 5), (88, 4), (59, 3), (29, 2),
            ),
            "B": (
                (384, 16), (355, 15), (325, 12), (296, 11), (266, 10), (237, 9),
                (207, 8), (178, 7), (148, 6), (119, 5), (89, 4), (59, 3), (29, 2),
            ),
            "C": (
                (384, 15), (354, 12), (325, 11), (295, 10), (266, 9), (236, 8),
                (207, 7), (177, 6), (148, 5), (118, 14), (88, 13), (59, 3), (29, 2),
            ),
        }
        assert cal in vals.keys(), ValueError("Cal {} not found".format(cal))

        for a, b in vals[cal]:
            if days > a:
                days -= a
                logging.debug("solution: (a:%s b:%s) month:%s day:%s",
                              a, b, LUNAR_MONTHS[b], days)
                month = LUNAR_MONTHS[b]
                break
            month = LUNAR_MONTHS[1]
        else:
            logging.debug("default: month:%s (%s) day:%s", 1, LUNAR_MONTHS[1], days)
        return month, days

    @classmethod
    def today(cls):
        """
        Return today as CS date.
        """
        jd = julianday.today()
        logging.debug("jd:%s", jd)
        return cls.fromjulianday(jd)

    @classmethod
    def fromyd(cls, year: int, days: int):
        """
        Return a Chulasakarat object from a year and days since new years day.
        """
        logging.debug("start: year:%s days:%s", year, days)
        year0 = cls.calculate_year0(year)
        days_in_year = 365 + int(year0.leapday)
        while days > days_in_year:  # zero-indexed
            year += 1
            days -= days_in_year
            year0 = cls.calculate_year0(year)
            days_in_year = 365 + int(year0.leapday)
            logging.debug("days >= %s: year:%s days:%s", 364 + int(year0.leapday), year, days)

        # logging.debug("year0 langsak:%s offset_days:%s", year0.langsak, year0.offset_days)
        month, day = cls.find_date(year0.cal_type, year0.offset_days + days)
        logging.debug("year:%s month:%s day:%s", year, month, day)
        return cls(year, month, day)

    @classmethod
    def fromjulianday(cls, jd: int):
        """
        Return a Chulasakarat object from a Julian Day Number.
        """
        hk = jd - CS_JULIAN_DAY_OFFSET
        year = (hk * 800 - 373) // 292207
        if hk % 292207 == 95333:
            # Every 800 years (292207 days), on the last day of the solar leap
            # year coinciding with an adhkimas lunar year, this jd->year
            # formula will be off by one day pushing the year forward by one
            # and the days count to -1.
            year -= 1
            days = 365
            logging.debug("800 year kamma adjustment")
        else:
            year0 = cls.calculate_year0(year)
            days = hk - year0.horakhun
        # logging.debug("kamma:%s", year0.kammabucapon)
        # logging.debug("jd:%s year:%s days:%s cal_type:%s hk0:%s", jd, year, days, year0.cal_type, year0.horakhun)
        logging.debug("jd:%s year:%s days:%s", jd, year, days)
        return cls.fromyd(year=year, days=days)

    from_julianday = fromjulianday

    @classmethod
    def fromtimestamp(cls, ts):
        """
        Return a Chulasakarat object from a UNIX timestamp.
        """
        jd = ts // (24 * 60 * 60) + CS_UNIX_EPOCH_OFFSET
        return cls.fromjulianday(jd)

    @property
    def julianday(self):
        """
        Return the Julian Day Number of this CS date.
        """
        return self.__horakhun + CS_JULIAN_DAY_OFFSET

    @property
    def horakhun(self):
        return self.__horakhun

    @property
    def kammabucapon(self):
        return self.__kamma

    @property
    def masaken(self):
        return self.__masaken

    @property
    def uccapon(self):
        return self.__uccapon

    @property
    def avoman(self):
        return self.__avoman

    @property
    def tithi(self):
        return self.__tithi

    @property
    def year(self):
        return self.__year

    @property
    def month(self):
        if self.__month == 15 or self.__month == 16:
            return self.__month - 10
        return self.__month

    @property
    def month_raw(self):
        return self.__month

    @property
    def day(self):
        return self.__day

    @property
    def days(self):
        return self.__days

    @property
    def solar_leap_year(self):
        return self.__year0.leapday

    @property
    def leap_day(self):
        return self.__year0.cal_type == 'B'

    @property
    def leap_month(self):
        return self.__year0.cal_type == 'C'

    @property
    def days_in_year(self):
        if self.__year0.cal_type == "A":
            return 354
        elif self.__year0.cal_type == "B":
            return 355
        elif self.__year0.cal_type == "C":
            return 384

    def replace(self, year=None, month=None, day=None):
        logging.debug("year:%s month%s day:%s", year, month, day)
        y = year if year else self.year
        m = month if month else self.month
        d = day if day else self.day
        logging.debug("year:%s month%s day:%s", y, m, d)
        return CsDate(y, m, d)

    def csweekday(self):
        return self.__horakhun % 7

    def weekday(self):
        return self.csweekday() - 2

    def isoweekday(self):
        return self.csweekday() - 1

    @property
    def yearnaksatr(self):
        idx = (self.year + 11) % 12
        if idx == 0:
            idx = 12
        return "ปี" + YEAR_NAKSATR[idx]

    def csformat(self):
        phase = "ขึ้น" if self.day <= 15 else "แรม"
        day = self.day if self.day <= 15 else self.day - 15
        s = "{:s} เดือน {:s} {:s} {:s} ค่ำ {:s} จ.ศ.{:s}".format(
            WEEKDAYS[self.csweekday()],
            digit_arabic_to_thai(self.month),
            phase,
            digit_arabic_to_thai(day),
            self.yearnaksatr,
            digit_arabic_to_thai(self.year)
        )
        s = digit_arabic_to_thai(s)
        return s

    def csformatymd(self):
        """
        Return string in YYYY-MM-DD format.
        """
        return "{:4d}-{:02d}-{:02d}".format(self.year, self.month, self.day)

    @classmethod
    def fromcsformat(self, s):
        s = digit_thai_to_arabic(s)
        weekday, _, month, phase, day, _, _, year = s.split()
        year = int(year.replace("จ.ศ.", ""))
        month = int(month)
        day = int(day)
        if phase == "แรม":
            day += 15
        return CsDate(year, month, day)

    def cscalendar(self):
        return CsCalendarDate(self.year, self.month, self.day)

    def __str__(self):
        return self.csformat()

    def __int__(self):
        """Convert to int by returning the Julian Day Number."""
        return self.julianday

    def _hashable(self):
        return (
            self.__year,
            self.__month,
            self.__day,
            self.__days,
            self.__horakhun,
            self.__kamma,
            self.__tithi,
            self.__year0.cal_type,
        )

    def __hash__(self):  # pragma: no cover
        return hash(self._hashable())

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
            return CsDate.fromjulianday(self.julianday + other.days)
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

    def debug(self):  # pragma: no cover
        return {
            "cp": self.__year0,
            "horakhun": self.__horakhun,
            "kamma": self.__kamma,
            # "avomanExtra": self.avomanExtra,
            "tt": self.__tithi,
            "year": self.__year,
            "month": self.__month,
            "day": self.__day,
            "days": self.__days,
            "cal_type": self.__year0.cal_type,
            "month_style": self.__month_style,
            "year0.langsak": self.__year0.langsak,
            "year0.offset": self.__year0.offset,
        }
"""
Julian Day functions.

Julian day convertor:
https://core2.gsfc.nasa.gov/time/julian.html
"""

import math
from datetime import date


def to_julianday(year, month, day):
    """
    Convert year, month, day to Julian Day.
    Based on: https://gist.github.com/jiffyclub/1294443
    """
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    
    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
        (year == 1582 and month < 10) or
        (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)
    
    C = math.trunc((365.25 * yearp) - 0.75) if yearp < 0 else math.trunc(365.25 * yearp)
    D = math.trunc(30.6001 * (monthp + 1))
    return int(B + C + D + day + 1720994.5 + 0.5)


def from_julianday(jd):
    """
    Return year, month, day from a Julian day number.
    Based on: https://gist.github.com/jiffyclub/1294443
    """
    # jd = jd + 0.5
    F, I = math.modf(jd)
    I = int(I)
    A = math.trunc((I - 1867216.25)/36524.25)
    B = (I + 1 + A - math.trunc(A / 4.)) if I > 2299160 else I
    C = B + 1524 
    D = math.trunc((C - 122.1) / 365.25)
    E = math.trunc(365.25 * D)
    G = math.trunc((C - E) / 30.6001) 
    days = C - E + F - math.trunc(30.6001 * G)
    month = (G - 1) if G < 13.5 else (G - 13)
    year = (D - 4716) if month > 2.5 else (D - 4715)
    return year, month, int(days) 


def today():  # pragma: no cover
    """Return today's Julian Day."""
    return date_to_julianday(date.today())


def date_to_julianday(d):
    """Return Julian Day Number from Date object."""
    if hasattr(d, "julianday"):
        return int(d.julianday)
    assert isinstance(d, date)
    return to_julianday(d.year, d.month, d.day)

def julianday_to_date(jd):
    """Return a date object for the given Julian Day NUmber."""
    return date(*from_julianday(jd))
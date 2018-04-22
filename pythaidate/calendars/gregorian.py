"""Gregorian calendar functions."""

import jdcal


def to_jdn(year, month, day):
    """
    Convert Gregorian Date to Julian Date Number.

    :param year: (int) Year
    :param month: (int) Month
    :param day: (int) Day
    :return: Julian Date Number
    """
    mjd_0, mjd_jd2000 = jdcal.gcal2jd(year, month, day)
    return mjd_0 + mjd_jd2000


def from_jdn(jdn):
    """
    Conver Julian Date Number to Gregorian Date.

    :param jdn: Julian Date Number.
    :return: Gregorian Date as string (YYYY-MM-DD)
    """
    d = jdcal.jd2gcal(jdcal.MJD_0, jdn - jdcal.MJD_0)
    return "%d-%02d-%02d" % (d[0], d[1], d[2])


def parse(s):
    """
    Parse Gregorian date string (YYYY-MM-DD).

    :param s: Date string (YYYY-MM-DD)
    :returns: Julian date number
    """
    year, month, day = s.split('-')
    jdn = to_jdn(int(year), int(month), int(day))
    return jdn

"""Modern Thai Solar Calendar."""

import jdcal

# GCAL_1941_01_01 = 2429996.0
#
# EQUIVS = {
#     # Thai Date: (Greg Date, JDN)
#     (2443,  9, 30): ((1900,  1,  1), 2415021.0),
#     (2483,  9, 30): ((1940, 12, 31), 2429995.0),
#     (2484,  1,  1): ((1941,  1,  1), 2429996.0),
#     (2543,  1,  1): ((2000,  1,  1), 2451545.0),
# }


def to_jdn(year, month, day):
    """
    Convert modern Thai Solar calendar to Gregorian Common Era.

    :param year: Thai Solar year
    :param month: Thai Solar month
    :param day: Thai Solar day
    :return: Tuple of integers (year, month, day)

    References:
    - https://th.wikipedia.org/wiki/ปฏิทินไทย#การเทียบปีกับปฏิทินอื่น
    """
    year = int(year)
    month = int(month)
    day = int(day)

    # first, adjust the date to Gregorian Common Era
    if year >= 2484:
        year -= 543

    elif year == 2483 and 1 <= month <= 9:
        year -= 543
        # month += 3

    elif year == 2483 and 10 >= month <= 12:
        raise ValueError("Invalid date: Months 10-12 didn't exist in 2483 BE")

    else:  # year < 2483-10
        if month <= 9:
            year -= 543
            # month += 3
        else:
            year -= 542
            # month -= 8

    # convert to JDN, same as in Gregorian/Julian calendars...
    # print("to_jdn:", year, month, day)
    mjd_0, mjd_jd2000 = jdcal.gcal2jd(year, month, day)
    return mjd_0 + mjd_jd2000


def from_jdn(jdn):
    """
    Conver Julian Date Number to Julian Date.

    :param jdn: Julian Date Number.
    :return: Modern Thai Solar Date as string (YYYY-MM-DD)
    """
    # convert to Gregorian Common Era
    year, month, day, frac = jdcal.jd2gcal(jdcal.MJD_0, jdn - jdcal.MJD_0)

    if year >= 1941:
        year += 543

    elif year == 1940 and month >= 4:
        year += 543
        # month -= 3

    else:  # year <= 1940
        year += 543
        # month += 8

    # return Modern Thai Solar date
    return "%d-%02d-%02d" % (year, month, day)


def parse(s):
    """
    Parse date string (YYYY-MM-DD).

    :param s: Date string (YYYY-MM-DD)
    :returns: Julian date number
    """
    year, month, day = s.split('-')
    jdn = to_jdn(int(year), int(month), int(day))
    return jdn

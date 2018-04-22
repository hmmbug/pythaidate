# -*- coding: utf8 -*-

# Based very, very loosely on code by นายไพศาล เตชจารุวงศ์

import math
import re

RE_PKN_SHORT = re.compile(
    r'((?P<cycle>\d):)?(?P<a>\d+)-(?P<b>\d+)-(?P<c>\d)-(?P<d>\d)-(?P<e>\d):(?P<f>\d+)',  # NOQA
    re.UNICODE
)
RE_PKN_LONG = re.compile(
    r'[\u0E00-\u0E7F]+\s+(?P<a>\d+)\s+[\u0E00-\u0E7F]+\s+(?P<b>\d+)\s+[\u0E00-\u0E7F]+\s+(?P<c>\d)\s+[\u0E00-\u0E7F]+\s+(?P<d>\d)\s+[\u0E00-\u0E7F]+\s+(?P<e>\d)\s+[\u0E00-\u0E7F]+\s+(?P<f>\d+)',  # NOQA
    re.UNICODE
)

A = 0b0000  # A
B1, B2 = 0b0010, 0b0011  # B1, B2
C1, C2 = 0b0100, 0b0101  # C1, C2
D1, D2 = 0b0110, 0b0111  # D1, D2
E1, E2 = 0b1000, 0b1001  # E1, E2
F1, F2 = 15, 14

PKN_ROWS = {
    A: "ปักขคณนา",
    B1: "มหาสัมพยุหะ",
    B2: "จุลสัมพยุหะ",
    C1: "มหาพยุหะ",
    C2: "จุลพยุหะ",
    D1: "มหาสมุหะ",
    D2: "จุลสมุหะ",
    E1: "มหาวรรค",
    E2: "จุลวรรค",
    F1: "มหาปักข์",
    F2: "จุลปักข์",
}

PKN_GROUPS = {
    A: [B1] * 17 + [B2],
    B1: [C2] * 10 + [C1],
    B2: [C2] * 9 + [C1],
    C1: [D1] * 6 + [D2],
    C2: [D1] * 5 + [D2],
    D1: [E2] * 3 + [E1],
    D2: [E2] * 2 + [E1],
    E1: [F1] * 4 + [F2],
    E2: [F1] * 3 + [F2],
}


def from_jdn(jd):
    """
    Convert a Julian Date to a PKN dictionary.

    :param jd: Julian Date Number
    :returns: PKN dictionary
        jd: Original Julian Date Number
        data: data,
        text_long: pkn_long,
        text_short: pkn_short,
        tithi_max: tithi_max,
        tithi_type: tithi_type,
        ปักขเกณฑ": pkn_total,
        phase: pkn_phase,
    """
    assert isinstance(jd, (float, int))
    if jd < 2355148:
        raise ValueError('Invalid JDN', jd)

    jd_r = round(jd)
    days = jd if jd_r < 2355148 else jd_r - 2355148 + 1

    cycle = math.ceil(days / 289577)

    days = days % 289577
    if days == 0:
        days = 289577

    data = [
        ("รอบ", cycle),
    ]

    # สัมพยุหะ
    a = math.ceil(days / 16168)
    if a > 18:
        a = 18
    AA = PKN_GROUPS[A][a-1]
    data.append(("ปักขคณนา", a, PKN_ROWS[AA]))

    # พยุหะ
    b = math.ceil((days - (a - 1) * 16168) / 1447)
    if AA == B1:
        if b > 11:
            b = 11
        BB = PKN_GROUPS[B1][b-1]
        data.append(("มหาสัมพยุหะ", b, PKN_ROWS[BB]))
    else:
        if b > 10:
            b = 10
        BB = PKN_GROUPS[B2][b-1]
        data.append(("จุลสัมพยุหะ", b, PKN_ROWS[BB]))

    # สมุหะ
    c = math.ceil((days - (a - 1) * 16168 - (b - 1) * 1447) / 251)
    if BB == C1:
        if c > 7:
            c = 7
        CC = PKN_GROUPS[C1][c-1]
        data.append(("มหาพยุหะ", c, PKN_ROWS[CC]))
    else:
        if c > 6:
            c = 6
        CC = PKN_GROUPS[C2][c-1]
        data.append(("จุลสัมพยุหะ", c, PKN_ROWS[CC]))

    # วรรค
    d = math.ceil((days - (a - 1) * 16168 - (b - 1)
                   * 1447 - (c - 1) * 251) / 59)
    if CC == D1:
        if d > 4:
            d = 4
        DD = PKN_GROUPS[D1][d-1]
        data.append(("มหาสมุหะ", d, PKN_ROWS[DD]))
    else:
        if d > 3:
            d = 3
        DD = PKN_GROUPS[D2][d-1]
        data.append(("จุลสมุหะ", d, PKN_ROWS[DD]))

    # ประเภทปักษ์
    e = math.ceil((days - (a - 1) * 16168 - (b - 1) *
                   1447 - (c - 1) * 251 - (d - 1) * 59) / 15)
    if DD == E1:
        if e > 5:
            e = 5
        EE = PKN_GROUPS[E1][e-1]
        data.append(("มหาวรรค", e, PKN_ROWS[EE]))
    else:
        if e > 4:
            e = 4
        EE = PKN_GROUPS[E2][e-1]
        data.append(("จุลวรรค", e, PKN_ROWS[EE]))

    # ดิถี
    f = (days - (a - 1) * 16168 - (b - 1) * 1447 -
         (c - 1) * 251 - (d - 1) * 59 - (e - 1) * 15)
    data.append(("วันทางจันทรคติ", f))
    if EE == F1:
        tithi_max = F1
        tithi_type = "ปักข์ถ้วน"
    else:
        tithi_max = F2
        tithi_type = "ปักข์ขาด"
    if f == 0 or f > tithi_max:
        raise ValueError("วันทางจันทรคติ invalid")

    pkn_total = (cycle - 1) * 19612 + (a - 1) * 1095 + \
        (b - 1) * 98 + (c - 1) * 17 + (d - 1) * 4 + e
    pkn_phase = "แรม" if pkn_total % 2 else "ขึ้น"

    pkn_long = "%s %s %s %s %s %s %s %s %s %s %s %s ค่ำ (%s)" % (
        PKN_ROWS[AA], a,
        PKN_ROWS[BB], b,
        PKN_ROWS[CC], c,
        PKN_ROWS[DD], d,
        PKN_ROWS[EE], e,
        pkn_phase, f, tithi_type
    )
    pkn_short = "%d-%d-%d-%d-%d:%d" % (a, b, c, d, e, f)

    pkn = {
        "jd": jd,
        "data": data,
        "text_long": pkn_long,
        "text_short": pkn_short,
        "tithi_max": tithi_max,
        "tithi_type": tithi_type,
        "ปักขเกณฑ์": pkn_total,
        "phase": pkn_phase,
        # วันพระธรรมยุติ
    }
    return pkn


def to_jdn(cycle, a, b, c, d, e, f):
    # A has 289577         ปักขคณนา 1 รอบ
    # B1 has 16168 days    มหาสัมพยุหะ
    # C2 has 1447 days     จุลสัมพยุหะ
    # D1 has 251 days      มหาสมุหะ
    # E2 has 59 days       จุลวรรค
    # F1 has 15 days       มหาปักษ์
    if not _validate_pkn(cycle, a, b, c, d, e, f):
        raise ValueError("Invalid PKN")
    days = (cycle - 1) * 289577 + (a - 1) * 16168 + (b - 1) * \
        1447 + (c - 1) * 251 + (d - 1) * 59 + (e - 1) * 15 + f

    # subtract 0.5 days to account for JDN starting at midday
    jd = float(2355148 + days - 1) - 0.5
    return jd


def _validate_pkn(cycle, a, b, c, d, e, f):
    if cycle < 1 or cycle > 4 or \
            a < 1 or a > 18 or b < 1 or c < 1 or d < 1 or e < 1 or f < 1:
        return False

    AA = PKN_GROUPS[A][a-1]
    if AA == B1:
        if b > 11:
            return False
        BB = PKN_GROUPS[B1][b-1]
    else:
        if b > 10:
            return False
        BB = PKN_GROUPS[B2][b-1]

    if BB == C1:
        if c > 7:
            return False
        CC = PKN_GROUPS[C1][c-1]
    else:
        if c > 6:
            return False
        CC = PKN_GROUPS[C2][c-1]

    if CC == D1:
        if d > 4:
            return False
        DD = PKN_GROUPS[D1][d-1]
    else:
        if d > 3:
            return False
        DD = PKN_GROUPS[D2][d-1]

    if DD == E1:
        if e > 5:
            return False
        EE = PKN_GROUPS[E1][e-1]
    else:
        if e > 4:
            return False
        EE = PKN_GROUPS[E2][e-1]

    f_max = F1 if EE == F1 else F2
    if f == 0 or f > f_max:
        return False

    return True


def parse(s):
    """
    Parse PKN string.

    :param s: Integer, long or short format:
        '7-4-6-1-1:4'
        '1:7-4-6-1-1:4'
        'มหาสัมพยุหะ 7 จุลพยุหะ 4 จุลสมุหะ 6 จุลวรรค 1 มหาปักข์ 1 ขึ้น 4 ค่ำ (ปักข์ถ้วน)'
        Integer is assumed to be a Julian Date Number
    :returns: Julian date number
    """
    if s is None:
        raise ValueError('Invalid input')
    elif isinstance(s, (int, float)):
        return s  # assume it's a Julian date number

    cycle = 0
    m = RE_PKN_SHORT.match(s)
    if m:
        cycle = int(m.group("cycle")) if m.group("cycle") else 1
    else:
        m = RE_PKN_LONG.match(s)
        if m:
            cycle = 1

    if not cycle:
        raise ValueError("PKN string not found")

    a = int(m.group("a"))
    b = int(m.group("b"))
    c = int(m.group("c"))
    d = int(m.group("d"))
    e = int(m.group("e"))
    f = int(m.group("f"))
    return to_jdn(cycle, a, b, c, d, e, f)

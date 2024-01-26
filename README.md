# pythaidate: Thai Calendar Systems for Python

![PyPI - License](https://img.shields.io/pypi/l/pythaidate)
![PyPI - Version](https://img.shields.io/pypi/v/pythaidate)

Thailand has used several calendar systems during its history and some are still in use today. This library provides `datetime.date`-like classes for working with the Thai lunisolar calendar of the Chulasakarat Era (จุลศักราช) and the lunar Pakkhakhananaa calendar (ปฏิทินปักขคณนา).

# Installation

```
$ python3 -m pip install pythaidate
```

# Examples

## `CsDate`: Chulasakarat Date

`CsDate` objects can be created from a year, month, day triple, like a `datetime.date` object. They represent the Thai lunisolar calendar with the epoch of 22nd March 638 AD. Months should be specified in Sukothai number format (eg. 5 is the first month). The example here specifies month 1 which, according to Sukothai numbering, is the 9th month in the year (although the 10th month in a year with intercalary month). Intercalary months (อธิกมาส) are specified as 88.

```
>>> from pythaidate import CsDate
>>> cs = CsDate(1361, 1, 24)
>>> cs.year, cs.month, cs.day
(1361, 1, 24)
```

The `days` property gives the zero-indexed count of days since new years day.
```
>>> cs.days
260
```

The `horakhun` (หรคุฌ) property gives the days since the epoch and `julianday` gives the Julian Day Number, useful for converting between calendar formats.
```
>>> cs.horakhun
497378
>>> cs.julianday
2451545
```

Other properties show the internal calculation values:
* `kammabucapon`: (กัมมัขผล) the excess of solar days over whole solar days
* `masaken`: (มาสเกฌฑ์) The number of lunar months since the epoch
* `uccapon`: (อุจจพล) The measure of the position of the Moon's apogee (furthest distance from the Earth). It increases by one unit a day to a maximum of 3232.
* `avoman`: (อวมาน) The excess of lunar days over solar days in units of 1/692 of a lunar day modulus 692, increasing by 11 units each solar day. It is used to determine when to add intercalary days in the calendar
* `tithi`: (ดิถี) a lunar day, equal to 1/30th of a synodic month

The year and day count since new years day can also be used to create a `CsDate` object with the `fromyd` class method:
```
>>> cs = CsDate.fromyd(1361, 260)
>>> cs.julianday
2451545
```

Similarly, a `CsDate` object can be created from the Julian Day Number:
```
>>> cs = CsDate.fromjulianday(2451545)
>>> cs.year, cs.month, cs.day
(1361, 1, 24)
```

A `CsDate` can be displayed as text with `.csformat()` or by converting the object to a string:
```
>>> cs.csformat()
'วันเสาร์ เดือน ๑ แรม ๙ ค่ำ ปีเถาะ จ.ศ.๑๓๖๑'
>>> str(cs)
'วันเสาร์ เดือน ๑ แรม ๙ ค่ำ ปีเถาะ จ.ศ.๑๓๖๑'
```

`CsDate` objects have 3 properties for intercalations and a day count:
* `solar_leap_year`: for the solar leap year (อธิกสุรทิน)
* `leap_day`: for the lunar intercalary day (อธิกวาร)
* `leap_month`: for the lunar intercalary month (อธิกมาส)
* `days_in_year`: returns the number of days in the year. This will be one of:
    * 354: no intercalations (ปกติมาส ปกติวาร)
    * 355: intercalary month, no intercalary day (ปกติมาส อธิกวาร)
    * 384: no intercalary month, intercalary day (อธิกมาส ปกติวาร)

In the Thai lunisolar calendar system a year can only have either zero or one intercalations. There can't be both an intercalary day (อธิกวาร) and month (อธิกมาส) in the same year.
```
>>> cs.solar_leap_year
False
>>> cs.leap_day
False
>>> cs.leap_month
True
>>> cs.days_in_year
384
```

## `PakDate`: Pakkhakhananaa Date

Create a `PakDate` object from a pakcode. The `1-` prefix is the cycle number (1-indexed), followed by the ปักขคณนา, สัมพยุหะ, พยุหะ, สมุหะ, วรรค and day of moon phase. The Pakkhakhananaa cycle repeats every 289,577 days.
```
>>> from pythaidate import PakDate
>>> p = PakDate(pakcode="1-6:11:5:2:2:10")
>>> p.horakhun
96398
>>> p.julianday
2451545
>>> p.iswanphra
False
```
Note that the `horakhun` value from Pakkhakhananaa lunar and (Chulasakarat era) lunisolar calendars are not compatible as they represent day count since the epoch of each calendar. For comparisons use `julianday` instead. `iswanphra` has an alias `issabbath`.

The Pakkhakhananaa code and abbreviations are available:
```
>>> p.pakcode
'1-6:11:5:2:2:10'
>>> print(p.pakabbr)
๖๑๕ข๒
 ๑
```

Pakkhakhananaa can be created from a `datetime.date` object:
```
>>> from datetime import date
>>> from pythaidate import PakDate
>>> p = PakDate(date=date(2000, 1, 1))
>>> p.julianday
2451545
```
...and from Julian Day Number:
```
>>> from pythaidate import PakDate
>>> p = PakDate(jd=2451545)
>>> p.julianday
2451545
>>> p.pakcode
'1-6:11:5:2:2:10'
```
`pakboard()` will display an ASCII Pakkhakhananaa board (กระดานปักขคณนา) and (best viewed with a fixed-width font):
```
>>> p.pakboard()
           ๑  ๒  ๓  ๔  ๕  ๖  ๗  ๘  ๙ ๑๐ ๑๑ ๑๒ ๑๓ ๑๔ ๑๕ ๑๖ ๑๗ ๑๘
ปักขคณนา    ม  ม  ม  ม  ม  ม  ม  ม  ม  ม  ม  ม  ม  ม  ม  ม  ม  จ
มหาสัมพยุหะ  จ  จ  จ  จ  จ  จ  จ  จ  จ  จ  ม
จุลสัมพยุหะ   จ  จ  จ  จ  จ  จ  จ  จ  จ  ม
มหาพยุหะ    ม  ม  ม  ม  ม  ม  จ
จุลพยุหะ     ม  ม  ม  ม  ม  จ
มหาสมุหะ    จ  จ  จ  ม
จุลสมุหะ     จ  จ  ม
มหาวรรค    ม  ม  ม  ม  จ
จุลวรรค     ม  ม  ม  จ
มหาปักข์     ๑  ๒  ๓  ๔  ๕  ๖  ๗  ๘  ๙ ๑๐ ๑๑ ๑๒ ๑๓ ๑๔ ๑๕
จุลปักข์      ๑  ๒  ๓  ๔  ๕  ๖  ๗  ๘  ๙ ๑๐ ๑๑ ๑๒ ๑๓ ๑๔
           รอบที่ ๑   หรคุณปักขคณนา ๙๖๓๙๘   ปักขเกณฑ์ ๖๕๒๙
```

## Julian Day Number (JDN) helpers

* `to_julianday(year, month, day)`: Returns JDN from a year, month, day triple
* `from_julianday(jd)`: Returns a year, month, day triple from a JDN
* `today()`: returns JDN for today
* `date_to_julianday(d)`: converts `datetime.date` object or other object with a `julianday` property to JDN
* `julianday_to_date(jd)`: converts JDN to a `datetime.date` object

## `pythaidate.date`: A `datetime.date` subclass

`pythaidate.date` is a simple subclass of `datetime.date` with an added `.julianday` property:

```
>>> from pythaidate import date
>>> d = date(2000, 1, 1)
>>> d.julianday
2451545
```

# Limitations

## General

* Tested and supported on Python 3.8 - 3.12.

## Chulasakarat Era Lunisolar Calendar

* The determination of which years are intercalary has been a somewhat subjective process and changed over the centuries, along with regional variations too. This library produces 7 intercalary months per 19 year period and 11 intercalary days per 57 years. This maintains the overall "pace" of the calendar but there may be slight short-term deviations from other calendars. But don't worry, those other calendars are just as wrong too - there's no definitive reference calendar.
* Currently only supports Sukothai-style month numbering (eg. first month of the year is month 5)
* `strftime` and `strptime` are not implemented

# Selected References

## Thai

* หลวงวิศาลดรุณกร (อั้น สาริกบุตร) (1997) คัมภีร์โหราศาสตร์ไทย มาตรฐาน ฉบับสมบูรณ์. Thailand: ศรีปัญญา, สนพ.

* [ความรู้เรื่องปักขคณนา ตําราการคํานวณปฏิทินทางจันทรคติ](https://archive.org/details/unset0000unse_d6m6). (1999). Thailand: มูลนิธิมหามกุฏราชวิทยาลัยฯ.

## English

* Eade, J.C. (2018). The Calendrical Systems of Mainland South-East Asia. Netherlands: Brill.
* Gislén L., Eade, J.C. (2019). The Calendars of Southeast Asia 2: Burma, Thailand, Laos and Cambodia. Journal of Astronomical History and Heritage, 22(3).

## French

* Faraut, F. G. (1910). [Astronomie cambodgienne](https://archive.org/details/farraut0astonomiecambodgienne). Vietnam: Imprimerie F.-H. Schneider.

* Billard, R. L'Astronomie Indienne. Investigation des Textes Sanskrits et des Donnees Numeriques. Paris: Ecole francaise d'extreme-orient. (1971).

# Other Resources

* [NASA's Julian Day Number Calculator](https://core2.gsfc.nasa.gov/time/julian.html)
* [ปฏิทินปักขคณนา.com](https://xn--12ccg5bxauoekd6vraqb.com/)

# Contributors

* Mark Hollow <dev {at} hmmbug.com> (Project Owner)

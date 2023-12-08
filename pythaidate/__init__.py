import os
import datetime

from .csdate import CsDate
from .pakdate import PakDate

from .julianday import to_julianday, from_julianday

__ALL__ = (
    "date",
    "CsDate",
    "PakDate",
)


class date(datetime.date):
    "pythaidate date class."

    def __new__(cls, year, month, day):
        dt = datetime.date.__new__(cls, year, month, day)
        return dt

    @property
    def julianday(self):
        "Returns the Julian Day Number of the date."
        return to_julianday(self.year, self.month, self.day)
import os
import datetime

from .csdate import CsDate
from .pakdate import PakDate

from .julianday import to_julianday

__ALL__ = (
    "CsDate",
    "PakDate",
)

if os.environ.get("PYTHAIDATE_NO_MONKEYPATCH") is None:
    # If PYTHAIDATE_NO_MONKEYPATCH is not set, monkey patch date objects to 
    # have a julianday property.
    datetime._date = datetime.date

    class _date(datetime._date):
        @property
        def julianday(self):
            "Returns the Julian Day Number of the date."
            return to_julianday(self.year, self.month, self.day)

    datetime.date = _date
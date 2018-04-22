"""Common."""
# -*- coding: utf-8 -*-

from .calendars import julian, gregorian, julian_date, pkn, thai_solar

FORMATS = {
    "gregorian": gregorian,
    "julian": julian,
    "julian_date": julian_date,
    "jdn": julian_date,
    "pakkakanana": pkn,
    "pkn": pkn,
    "thai_solar": thai_solar,
    # "python": None,
}


class ThaiDate(object):

    def __init__(self, jdn):
        """
        ThaiDate class.

        :param jdn: Julian Date (double)
        """
        self._jdn = jdn

    def format(self, format, **kwargs):
        """
        Return as the specified format.

        :param format: (string) Era name or abbreviation.
            Supported formats:
                julian_date, jdn: Julian Date
                pakkakanana, pkn: ปักษคณนา
                chulasakarat, cs: Chulasakarat (จุลศักราช)
                python: Python Date object
        :param kwargs: Additional key/value pairs to be passed to the
            formatter.
        :returns: era object # TODO
        """
        formatter = FORMATS.get(format, None)
        if not formatter:
            raise KeyError("Format not implemented: %s" % (format,))

        formatted = formatter.from_jdn(self._jdn)
        return formatted

    @classmethod
    def parse(cls, calendar_type, *args, **kwargs):
        calmod = FORMATS[calendar_type]
        return cls(calmod.parse(*args, **kwargs))

    # calendar conversion helpers...

    @classmethod
    def from_gregorian(cls, *args, **kwargs):
        return cls.parse("gregorian", *args, **kwargs)

    @classmethod
    def from_julian(cls, *args, **kwargs):
        return cls.parse("julian", *args, **kwargs)

    @classmethod
    def from_julian_date(cls, *args, **kwargs):
        return cls.parse("julian_date", *args, **kwargs)

    @classmethod
    def from_pakkakanana(cls, *args, **kwargs):
        return cls.parse("pakkakanana", *args, **kwargs)

    @classmethod
    def from_thai_solar(cls, *args, **kwargs):
        return cls.parse("thai_solar", *args, **kwargs)

    # aliases
    from_jdn = from_julian_date
    from_pkn = from_pakkakanana

    @staticmethod
    def list_formats():
        """
        List available formats.

        :return: List of formats.
        """
        return FORMATS.keys()


# hmmm... could try dynamically adding the from_* methods, something like
# the following, but need to get arund the lambda function late bindings
# somehow. Will leave this for another day...

# try:
#     _imported_already  # NOQA
# except:
#     # Monkey patch dynamic class methods
#     for cal in FORMATS.keys():
#         setattr(ThaiDate, 'from_'+cal, classmethod(
#             lambda cls, *args, **kwargs: cls.parse(FORMATS[cal],
#                                                    *args, **kwargs)
#         ))
#     _imported_already = True

# -*- coding: utf-8 -*-

from .context import pythaidate

import unittest


class BaseTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_instantiate(self):
        ptd = pythaidate.ThaiDate(0)
        assert isinstance(ptd, pythaidate.ThaiDate)

    def test_list_formats(self):
        formats = pythaidate.ThaiDate.list_formats()
        assert len(formats) > 0, "empty formats list"
        for f in formats:
            assert isinstance(f, str)

    def test_monkey_patch_methods(self):
        ptd = pythaidate.ThaiDate
        formats = ptd.list_formats()
        for f in formats:
            assert hasattr(ptd, "from_" + f)


if __name__ == '__main__':
    unittest.main()

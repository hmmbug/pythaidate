import unittest
from datetime import date

import pythaidate


class Test_Misc(unittest.TestCase):

    def test_monkeypatch(self):
        d = date(2000, 1, 1)
        self.assertTrue(hasattr(d, "julianday"))

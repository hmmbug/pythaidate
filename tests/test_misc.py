import unittest

import pythaidate


class Test_Misc(unittest.TestCase):

    def test_date(self):
        d = pythaidate.date(2000, 1, 1)
        self.assertTrue(hasattr(d, "julianday"))
        self.assertEqual(d.julianday, 2451545)

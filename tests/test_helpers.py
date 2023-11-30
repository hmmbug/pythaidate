import unittest

from pythaidate import helpers

THAI_ARABIC_TESTS = (
    ("๐๑๒", "012"),
    ("๑๒๓", "123"),
    ("๒๓๔", "234"),
    ("๓๔๕", "345"),
    ("๔๕๖", "456"),
    ("๕๖๗", "567"),
    ("๖๗๘", "678"),
    ("๗๘๙", "789"),
)

THAI_WIDTH_TESTS = (
    ("มาร์ค", 4),
    ("ปฏิทิน", 4),
    ("จันทรคติ", 6),
    ("ไทย", 3),
)

class Test_Helpers(unittest.TestCase):

    def test_digit_thai_to_arabic(self):
        for t, a in THAI_ARABIC_TESTS:
            result = helpers.digit_thai_to_arabic(t)
            self.assertEqual(a, result, "Failed: "+str((t, a))+" result:"+result)

            # with non-digit chars
            input = "test " + t + " test"
            expected = "test " + a + " test"
            result = helpers.digit_thai_to_arabic(input)
            self.assertEqual(expected, result, "Failed: "+str((input, expected))+" result:"+result)

    def test_digit_arabic_to_thai(self):
        for t, a in THAI_ARABIC_TESTS:
            # straight conversion
            result = helpers.digit_arabic_to_thai(a)
            self.assertEqual(t, result, "Failed: "+str((t, a))+" result:"+result)

            # int conversion (no leading zeroes)
            input = int(a)
            expected = t.lstrip("๐")
            result = helpers.digit_arabic_to_thai(input)
            self.assertEqual(expected, result, "Failed: "+str((input, expected))+" result:"+result)

            # with non-digit chars
            input = "test " + a + " test"
            expected = "test " + t + " test"
            result = helpers.digit_arabic_to_thai(input)
            self.assertEqual(expected, result, "Failed: "+str((input, expected))+" result:"+result)

    def test_thai_string_width(self):
        for s, w in THAI_WIDTH_TESTS:
            result = helpers.thai_string_width(s)
            self.assertEqual(w, result, "Failed: "+s+" result:"+str(result)+" expected:"+str(w))

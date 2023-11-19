__ALL__ = (
    "digit_thai_to_arabic",
    "digit_arabic_to_thai",
    "thai_string_width",
)

__digits_arabic_thai = {
    "0": "๐",
    "1": "๑",
    "2": "๒",
    "3": "๓",
    "4": "๔",
    "5": "๕",
    "6": "๖",
    "7": "๗",
    "8": "๘",
    "9": "๙",
}

__digits_thai_arabic = {
    "๐": "0",
    "๑": "1",
    "๒": "2",
    "๓": "3",
    "๔": "4",
    "๕": "5",
    "๖": "6",
    "๗": "7",
    "๘": "8",
    "๙": "9",
}

__thai_central_chars = "ผปแอทมใฝฉฮฬฦฟหกดเาสวงฤฆฏโฌษศซๆไำพะรนยบลฃ๐ฎฑธณฯญฐฅๅ๑๒ภ๓ถ๔฿ค๕ต๖จ๗ข๘ช๙"

def digit_thai_to_arabic(s) -> str:
    result = []
    for c in s:
        if c in __digits_thai_arabic:
            result.append(__digits_thai_arabic[c])
        else:
            result.append(c)
    return "".join(result)


def digit_arabic_to_thai(s: str) -> str:
    if isinstance(s, int):
        # leading zeros won't be preserved
        s = str(s)
    result = []
    for c in s:
        if c in __digits_arabic_thai:
            result.append(__digits_arabic_thai[c])
        else:
            result.append(c)
    return "".join(result)


def thai_string_width(s):
    count = 0
    for c in s:
        if c in __thai_central_chars:
            count += 1
    return count
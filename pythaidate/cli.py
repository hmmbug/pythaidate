from .csdate import CsDate
from .pakdate import PakDate


def cstoday():
    "Prints today's date."
    cs = CsDate.today()
    print(cs)


def paktoday():
    "Prints today's Pakkhakhananaa board."
    p = PakDate.today()
    p.pakboard()
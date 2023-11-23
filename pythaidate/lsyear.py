from .constants import (
    DAYS_IN_800_YEARS, 
    TIME_UNITS_IN_1_DAY, 
    EPOCH_OFFSET, 
    UCCABALA_CONSTANT,
    APOGEE_ROTATION_DAYS,
    CAL_TYPE_DAY_COUNTS,
)


class LSYear:
    """
    A lightweight class representing a lunisolar year on new year's day.
    """
    
    def __init__(self, year: int):
        self.offset = False  # adjusted later
        self.year = year

        # this year
        self.horakhun = (year * DAYS_IN_800_YEARS + EPOCH_OFFSET) // TIME_UNITS_IN_1_DAY + 1
        self.kammabucala = TIME_UNITS_IN_1_DAY - (year * DAYS_IN_800_YEARS + EPOCH_OFFSET) % TIME_UNITS_IN_1_DAY
        # ucc_i = (2611 + self.ahargana) // APOGEE_ROTATION_DAYS
        self.uccabala = (UCCABALA_CONSTANT + self.horakhun)  % APOGEE_ROTATION_DAYS
        avo_quot = (self.horakhun * 11 + 650) // 692
        self.avoman = (self.horakhun * 11 + 650) % 692
        if self.avoman == 0:
            self.avoman = 692
        self.masaken = (avo_quot + self.horakhun) // 30
        self.tithi = (avo_quot + self.horakhun) % 30
        if self.avoman == 692:
            self.tithi -= 1
        # rest_quot = self.horakhun // 7
        self.weekday = self.horakhun % 7

        # next year
        horakhun1 = ((year + 1) * DAYS_IN_800_YEARS + EPOCH_OFFSET) // TIME_UNITS_IN_1_DAY + 1
        quot1 = (horakhun1 * 11 + 650) // 692
        # avo1 = (ahargana1 * 11 + 650) % 692
        # mas1 = (quot1 + ahargana1) // 30
        tithi1 = (quot1 + horakhun1) % 30

        # Faraut, pg 28
        self.langsak = max(1, self.tithi)
        self.nyd = self.langsak
        if self.nyd < 6:
            self.nyd += 29
        self.nyd = (self.weekday - self.nyd + 1 + 35) % 7

        # is there a solar year leap day?
        self.leapday = self.kammabucala <= 207

        # A: normal year, 354 days
        # B: leap day, 355 days
        # C: leap month, 384 days
        self.cal_type = 'A'  # normal year
        if self.tithi > 24 or self.tithi < 6:
            self.cal_type = 'C'  # leap month
        if self.tithi == 25 and tithi1 == 5:
            self.cal_type = 'A'
        if (self.leapday and self.avoman <= 126) or (not self.leapday and self.avoman <= 137):
            self.cal_type = 'B' if self.cal_type != 'C' else 'c'

        # start of next year
        if self.cal_type == 'A':
            self.next_nyd = (self.nyd + 4) % 7
        elif self.cal_type == 'B':
            self.next_nyd = (self.nyd + 5) % 7
        elif self.cal_type == 'C' or self.cal_type == 'c':
            self.next_nyd = (self.nyd + 6) % 7
        self.caldays = CAL_TYPE_DAY_COUNTS[self.cal_type]

    def dump(self):  # pragma: no cover
        s = "horakhun:{:d} kamma:{:d} ucca:{:d} avoman:{:d} mas:{:d} tithi:{:d} day:{:d} nyd:{:d} " + \
            "next_nyd:{:d} langsak:{:d} bissext:{:d} offset:{:d} cal:{:s}"
        return s.format(
            self.horakhun,
            self.kammabucala,
            self.uccabala,
            self.avoman,
            self.masaken,
            self.tithi,
            self.weekday,
            self.nyd,
            self.next_nyd,
            self.langsak,
            int(self.leapday),
            int(self.offset),
            self.cal_type
        )
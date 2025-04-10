from datetime import time
from enum import IntEnum


class Period(IntEnum):
    TWENTY_TO_TWO = 1
    HALF_PAST_TWO = 2
    TWENTY_PAST_THREE = 3
    TEN_PAST_FOUR = 4
    FIVE_O_CLOCK = 5
    TEN_TO_SIX = 6
    TWENTY_TO_SEVEN = 7
    HALF_PAST_SEVEN = 8
    TWENTY_PAST_EIGHT = 9
    TEN_PAST_NINE = 10

    @classmethod
    def from_time(cls, actual: time) -> "Period":
        match True:
            case _ if actual < time(13, 40):
                return cls.TWENTY_TO_TWO
            case _ if actual < time(14, 30):
                return cls.HALF_PAST_TWO
            case _ if actual < time(15, 20):
                return cls.TWENTY_PAST_THREE
            case _ if actual < time(16, 10):
                return cls.TEN_PAST_FOUR
            case _ if actual < time(17, 0):
                return cls.FIVE_O_CLOCK
            case _ if actual < time(17, 50):
                return cls.TEN_TO_SIX
            case _ if actual < time(18, 40):
                return cls.TWENTY_TO_SEVEN
            case _ if actual < time(19, 30):
                return cls.HALF_PAST_SEVEN
            case _ if actual < time(20, 20):
                return cls.TWENTY_PAST_EIGHT
            case _:
                return cls.TEN_PAST_NINE

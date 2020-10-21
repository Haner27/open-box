MILLISECOND = 1
SECOND = MILLISECOND * 1000
MINUTE = SECOND *60
HOUR = MINUTE * 60
DAY = HOUR * 24
MONTH = DAY * 30
YEAR = DAY * 365


class LimitRate:
    def __init__(self, times: int, intervals: int):
        self.__times = times
        self.__intervals = intervals
        self.__rate = self.cal_rate(times, intervals)

    @property
    def times(self):
        return self.__times

    @property
    def intervals(self):
        return self.__intervals

    @property
    def rate(self):
        return self.__rate

    def __str__(self):
        return '<LimitRate: {} times/ms>'.format(self.__rate)

    @staticmethod
    def cal_rate(times: int, intervals: int):
        if intervals == 0:
            return times
        return times / intervals

    def __mul__(self, other):
        return self.__rate * other
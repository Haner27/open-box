import time

from open_box.track import Tracker


class User:
    def __init__(self, name, age, gender, tracker):
        self.__tracker = tracker
        self.__name = name
        self.__age = age
        self.__gender = gender

    @property
    def load_name(self):
        self.__tracker.mark('loading name')
        time.sleep(1)
        return self.__name

    def load_age(self, time_age):
        self.__tracker.mark('loading age')
        time.sleep(1)
        return self.__age + time_age

    @classmethod
    def load_gender(cls, prefix, tracker):
        tracker.mark('loading gender')
        time.sleep(1)
        return cls.__name__ + prefix + 'male'

    @staticmethod
    def calculate(a, b, tracker):
        with tracker.span('calculate'):
            time.sleep(1)
            return a + b

    def load_user(self):
        name = self.load_name
        age = self.load_age(time_age=100)
        gender = self.__class__.load_gender('SEX:', self.__tracker)
        sum_num = self.calculate(100, 100, self.__tracker)
        self.__tracker.finish()
        print(self.__tracker.output())
        return {
            'name': name,
            'age': age,
            'gender': gender,
            'sum': sum_num,
        }


def func(x, y):
    tracker = Tracker('func tracker')
    tracker.mark('x + y')
    z = x + y
    time.sleep(1)

    tracker.mark('x * z')
    m = x * z
    time.sleep(1)

    with tracker.span('y * z'):
        n = y * z
        time.sleep(1)

    tracker.mark('m * n / 2')
    t = m * n / 2
    time.sleep(2)

    tracker.finish()
    print(tracker.output())
    return t
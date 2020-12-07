import inspect
import sys
import time

from examples.track.test import User, func
from open_box.track import Tracker


def func2(x, y):
    with Tracker('func2 tracker') as tracker:
        z = x + y
        time.sleep(3)
    print(tracker.output())
    return z


if __name__ == '__main__':
    func(2, 2)
    # func2(2, 2)
    # tracker = Tracker("UserTracker")
    # u = User('han', 28, 'male', tracker)
    # print(u.load_user())
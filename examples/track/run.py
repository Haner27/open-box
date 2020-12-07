import inspect
import sys
import time

from examples.track.test import User, func
from open_box.track import Tracker


if __name__ == '__main__':
    # func(2, 2)
    tracker = Tracker("UserTracker")
    u = User('han', 28, 'male', tracker)
    print(u.load_user())
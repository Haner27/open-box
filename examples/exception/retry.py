from open_box.exception.retry import retry


@retry(attempts=3, interval=1)
def retry_func():
    a = 1 / 0
    return a


if __name__ == '__main__':
    retry_func()

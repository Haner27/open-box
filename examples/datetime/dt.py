from open_box.datetime import *

dt = now()
ts = timestamp()
print('now: ', dt)
print('today: ', today())
print('yesterday: ', yesterday())
print('timestamp: ', ts)
print('from_timestamp: ', from_timestamp(ts))
print('to_timestamp: ', to_timestamp(dt))
print('format_datetime: ', format_datetime(dt))
print('to_datetime: ', to_datetime('1992-03-14 21:45:10'))
print(
    'covert_message_duration_text: ',
    covert_message_duration_text(dt - timedelta(seconds=20)),
    covert_message_duration_text(dt - timedelta(minutes=28, seconds=10)),
    covert_message_duration_text(dt - timedelta(hours=7, minutes=28, seconds=10)),
    covert_message_duration_text(dt - timedelta(days=1, hours=7, minutes=28, seconds=10)),
    covert_message_duration_text(dt - timedelta(days=2, hours=7, minutes=28, seconds=10)),
)
print(
    'covert_duration_text: ',
    covert_duration_text(4235, with_unit=False),
    covert_duration_text(4235),
    covert_duration_text(89023, with_unit=False),
    covert_duration_text(89023),
)


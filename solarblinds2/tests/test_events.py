import datetime
from solarblinds2.events import get_next_sun_event_time_and_type
from unittest import mock
import astral
import solarblinds2.config


def test_get_next_sun_event_time_and_type_happy() -> None:
    observer = astral.Observer()

    now = datetime.datetime(year=2000, month=1, day=1, hour=0, tzinfo=datetime.timezone.utc)
    date, type = get_next_sun_event_time_and_type(observer, now)
    assert date == datetime.datetime(2000, 1, 1, 8, 5, 57, 311165, tzinfo=datetime.timezone.utc)
    assert type == solarblinds2.config.EventType.SUNRISE

    now = datetime.datetime(year=2000, month=1, day=1, hour=12, tzinfo=datetime.timezone.utc)
    date, type = get_next_sun_event_time_and_type(observer, now)
    assert date == datetime.datetime(2000, 1, 1, 16, 0, 49, 698951, tzinfo=datetime.timezone.utc)
    assert type == solarblinds2.config.EventType.SUNSET


def test_get_next_sun_event_time_and_type_close_to_event() -> None:
    observer = astral.Observer()

    now = datetime.datetime(2000, 1, 1, 8, 5, 57, 311165 - 1, tzinfo=datetime.timezone.utc)
    date, type = get_next_sun_event_time_and_type(observer, now)
    assert date == datetime.datetime(2000, 1, 1, 8, 5, 57, 311165, tzinfo=datetime.timezone.utc)
    assert type == solarblinds2.config.EventType.SUNRISE

    now = datetime.datetime(2000, 1, 1, 8, 5, 57, 311165, tzinfo=datetime.timezone.utc)
    date, type = get_next_sun_event_time_and_type(observer, now)
    assert date == datetime.datetime(2000, 1, 1, 16, 0, 49, 698951, tzinfo=datetime.timezone.utc)
    assert type == solarblinds2.config.EventType.SUNSET

    now = datetime.datetime(2000, 1, 1, 8, 5, 57, 311165 + 1, tzinfo=datetime.timezone.utc)
    date, type = get_next_sun_event_time_and_type(observer, now)
    assert date == datetime.datetime(2000, 1, 1, 16, 0, 49, 698951, tzinfo=datetime.timezone.utc)
    assert type == solarblinds2.config.EventType.SUNSET


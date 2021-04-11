import datetime
import typing

import astral
import astral.sun

import solarblinds2.config as config


def get_next_sun_event_time_and_type(
    observer: astral.Observer, now: typing.Optional[datetime.datetime] = None
) -> typing.Tuple[datetime.datetime, config.EventType]:
    now = now or datetime.datetime.now(datetime.timezone.utc)

    next_sunrise = astral.sun.sunrise(observer, now.date())
    if next_sunrise <= now:
        next_sunrise = astral.sun.sunrise(observer, now.date() + datetime.timedelta(days=1))

    next_sunset = astral.sun.sunset(observer, now.date())
    if next_sunset <= now:
        next_sunset = astral.sun.sunset(observer, now.date() + datetime.timedelta(days=1))

    if next_sunrise < next_sunset:
        next_event_time = next_sunrise
        next_event_type = config.EventType.SUNRISE
    else:
        next_event_time = next_sunset
        next_event_type = config.EventType.SUNSET

    return next_event_time, next_event_type

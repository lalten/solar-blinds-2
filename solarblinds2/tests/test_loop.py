import datetime
from unittest import mock

import astral
import solarblinds2
import solarblinds2.config as config


class MockTime:
    def __init__(self, start_time: datetime.datetime) -> None:
        self.time = start_time.timestamp()

    def __call__(self) -> float:
        self.time += 1.0
        return self.time


@mock.patch("time.time", MockTime(datetime.datetime.now()))
@mock.patch("time.sleep", mock.Mock())
@mock.patch("solarblinds2.Solarblinds2._get_session_by_login", mock.Mock())
@mock.patch("solarblinds2.Solarblinds2._is_running", mock.Mock(side_effect=[True] * 5 + [False]))
@mock.patch("solarblinds2.Solarblinds2._do_command")
def test_loop(do_command_mock: mock.MagicMock) -> None:
    mock_config = mock.Mock()
    mock_config.observer = astral.Observer()
    mock_config.events = {
        config.EventType.SUNRISE: config.Event(datetime.timedelta(), [config.CommandData(1, 0, 0, 0)]),
        config.EventType.SUNSET: config.Event(datetime.timedelta(), [config.CommandData(2, 0, 0, 0)]),
    }
    sb = solarblinds2.Solarblinds2(mock_config)

    sb.run()

    do_command_mock.assert_has_calls(
        [
            mock.call(config.CommandData(pid=1, oid=0, did=0, value=0)),
            mock.call(config.CommandData(pid=2, oid=0, did=0, value=0)),
            mock.call(config.CommandData(pid=1, oid=0, did=0, value=0)),
            mock.call(config.CommandData(pid=2, oid=0, did=0, value=0)),
            mock.call(config.CommandData(pid=1, oid=0, did=0, value=0)),
        ]
    )

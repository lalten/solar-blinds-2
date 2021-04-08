from dataclasses import dataclass
import typing
import datetime
import enum
import pathlib
import astral
import astral.sun
import yaml


@dataclass(frozen=True)
class ConnectionData:
    server: str


@dataclass(frozen=True)
class LoginData:
    username: str
    password: str


@dataclass(frozen=True)
class CommandData:
    pid: int  # BACObjectPropertyRef
    oid: int  # BACObjectPropertyRef
    did: int  # BACObject
    value: int


@dataclass(frozen=True)
class Event:
    delay: datetime.timedelta
    commands: typing.List[CommandData]


class EventType(enum.Enum):
    SUNRISE = enum.auto()
    SUNSET = enum.auto()


@dataclass(frozen=True)
class Configuration:
    connection: ConnectionData
    login: LoginData
    observer: astral.Observer
    events: typing.Dict[EventType, Event]


def load_config(config_file: typing.Union[str, pathlib.Path]) -> Configuration:
    with open(config_file) as f:
        config = yaml.safe_load(f)["configuration"]
    config["connection"] = ConnectionData(**config["connection"])
    config["login"] = LoginData(**config["login"])
    config["observer"] = astral.Observer(**config["observer"])
    config["events"] = {
        EventType[key]: Event(
            delay=datetime.timedelta(seconds=event["delay_s"]),
            commands=[CommandData(**command) for command in event["commands"]],
        )
        for key, event in config["events"].items()
    }
    return Configuration(**config)

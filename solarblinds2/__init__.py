#!/usr/bin/env python3

import datetime
import json
import logging
import pathlib
from solarblinds2.events import get_next_sun_event_time_and_type
import typing
from dataclasses import asdict

import time
import click
import requests

import solarblinds2.config as config


def pause_until(wakeup: datetime.datetime) -> None:
    while True:
        now = datetime.datetime.now(tz=wakeup.tzinfo)
        diff = (wakeup - now).total_seconds()
        if diff <= 0:
            break
        time.sleep(diff / 2)


class Solarblinds2:
    def __init__(self, config: config.Configuration) -> None:
        self._config = config
        self._session = self._get_session_by_login()

    def _is_running(self) -> bool:
        return True

    def _get_session_by_login(self) -> requests.Session:
        session = requests.Session()
        request = session.post(self._config.connection.server + "/login", data=asdict(self._config.login))
        request.raise_for_status()
        if "Your login failed" in request.text:
            raise RuntimeError("Login failed.")
        logging.debug("=".join(session.cookies.items()[0]))
        return session

    def _do_command(self, command: config.CommandData) -> None:
        try:
            self._do_command_with_current_session(command)
        except (RuntimeError, json.decoder.JSONDecodeError, requests.exceptions.ConnectionError) as exc:
            logging.debug("Command failed: %s, trying with new session.", exc)
            self._session = self._get_session_by_login()
            self._do_command_with_current_session(command)

    def _do_command_with_current_session(self, command: config.CommandData) -> None:
        request = self._session.get(self._config.connection.server + "/ajaxjson/bac/setValue", params=asdict(command))
        request.raise_for_status()
        json = request.json()
        if "status" not in json or json["status"] != "ok":
            raise RuntimeError(f"Command failed: {json}")
        logging.debug(json)

    def _get_next_wakeup_and_event(
        self, next_wakeup: datetime.datetime
    ) -> typing.Tuple[datetime.datetime, datetime.datetime, config.Event]:
        now = datetime.datetime.now(datetime.timezone.utc)
        check_time = max(now, next_wakeup)
        next_event_time, next_event_type = get_next_sun_event_time_and_type(self._config.observer, check_time)
        next_event = self._config.events[next_event_type]
        next_wakeup = next_event_time + next_event.delay
        next_check_time = next_event_time
        return next_wakeup, next_check_time, next_event

    def run(self) -> None:
        next_check_time = datetime.datetime.now(datetime.timezone.utc)
        while self._is_running():
            next_wakeup, next_check_time, next_event = self._get_next_wakeup_and_event(next_check_time)
            logging.info("Pause until %s at %s. Next check is at %s", next_event, next_wakeup, next_check_time)
            pause_until(next_wakeup)
            for command in next_event.commands:
                self._do_command(command)


@click.command()
@click.option("--debug", is_flag=True, default=False)
@click.option(
    "--config_file",
    type=click.Path(exists=True),
    default=str(pathlib.Path.home() / ".solarblinds2/config.yaml"),
)
def cli(debug: bool, config_file: str):
    if debug:
        logging.basicConfig(level=logging.DEBUG, format=f"[%(asctime)s] {logging.BASIC_FORMAT}")
    logging.debug("Loading configuration from %s", config_file)
    configuration = config.load_config(config_file)
    Solarblinds2(configuration).run()


if __name__ == "__main__":
    cli()

import re
from datetime import date
from pathlib import Path
from typing import Iterable

from .. import log

READING_REGEX = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})_(?P<serial>\w+)_(?P<value>\d+(?:-\d+)?)"
)


class Reading:
    def __init__(self) -> None:
        self._date: date | None = None
        self._serial: str | None = None
        self._value: float | None = None

    @staticmethod
    def from_string(string: str) -> "Reading | None":
        match = READING_REGEX.search(string)

        if match is None:
            return None

        r = Reading()

        try:
            r.date = date.fromisoformat(match["date"])
            r.serial = match["serial"]
            r.value = match["value"]

        except Exception as e:
            log.warn("cannot parse reading: {}".format(e))
            return None

        return r

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value: date | str):
        if isinstance(value, str):
            value = date.fromisoformat(value)
        self._date = value

    @property
    def serial(self):
        return self._serial

    @serial.setter
    def serial(self, value: str):
        self._serial = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: float | int | str):
        if isinstance(value, str):
            value = float(value.replace("-", "."))
        elif isinstance(value, int):
            value = float(value)
        self._value = value

    def __str__(self) -> str:
        return f"{self.date}, {self.serial}, {self.value}"

    def __repr__(self) -> str:
        return str(self)


class Readings:
    def __init__(self) -> None:
        self.readings = list[Reading]

    @staticmethod
    def from_files(files: Iterable[Path]):
        rs = Readings()
        rs.readings = [
            r for f in files if (r := Reading.from_string(f.name)) is not None
        ]

        return rs

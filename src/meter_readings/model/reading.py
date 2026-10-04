import re
from collections.abc import Iterable
from datetime import date, timedelta
from pathlib import Path

from .. import log

READING_REGEX = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})_(?P<serial>\w+)_(?P<value>\d+(?:-\d+)?)"
)


class Reading:
    def __init__(self) -> None:
        self._date: date = date.min
        self._serial: str = ""
        self._value: float = -1

    @staticmethod
    def from_string(
        string: str, allowed_serials: list[str] | None = None
    ) -> Reading | None:
        match = READING_REGEX.search(string)

        if match is None:
            return None

        r = Reading()

        try:
            serial = match["serial"]

            if allowed_serials is not None and serial not in allowed_serials:
                log.warning(f"unknown serial: {serial}")
                return None

            r.serial = serial
            r.date = date.fromisoformat(match["date"])
            r.value = match["value"]

        except Exception as e:
            log.warning(f"cannot parse reading: {e}")
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
    def value(self, value: float | str):
        if isinstance(value, str):
            value = float(value.replace("-", "."))
        elif isinstance(value, int):
            value = float(value)
        self._value = value

    def __str__(self) -> str:
        return f"{self.date}, {self.serial}, {self.value}"

    def __repr__(self) -> str:
        return str(self)


class SerialReadings:
    def __init__(self, serial: str) -> None:
        self.serial: str = serial
        self.readings: list[Reading] = []

    def latest(self) -> Reading | None:
        return max(self.readings, key=lambda r: r.date)

    def history(
        self, start: date | None = None, days: int = 0, weeks: int = 0, years: int = 0
    ):
        if start is None:
            if not (latest := self.latest()):
                return None

            start = latest.date

        entry = start - timedelta(days=days, weeks=weeks)
        entry.replace(year=entry.year - years)

        return min(self.readings, key=lambda r: abs(r.date - entry))

    def weekly(self):
        days = 7
        mean_dur = 28

        return self._stats(days, mean_dur)

    def monthly(self):
        days = 28
        mean_dur = 364

        return self._stats(days, mean_dur)

    def yearly(self):
        days = 364
        mean_dur = 1000

        return self._stats(days, mean_dur)

    def _stats(self, stat_days: int, stat_mean_days: int):
        diff = None
        trend = None
        mean = None
        mean_diff = None

        latest = self.latest()
        if latest:

            before = self.history(days=stat_days)
            if before:
                diff = diff_values(before, latest, stat_days)

                # Calculate trend
                before_before = self.history(start=before.date, days=stat_days)
                if before_before:

                    diff_before = diff_values(before_before, before, stat_days)
                    trend = diff - diff_before

                # Calculte mean for duration
                mean_before = self.history(days=stat_mean_days)
                if mean_before:
                    mean = diff_values(mean_before, latest, days=stat_days)
                    mean_diff = diff - mean

        return diff, trend, mean, mean_diff


def diff_values(start: Reading, end: Reading, days: int):
    if end.date == start.date:
        return 0

    return (end.value - start.value) / (end.date - start.date).days * days


class Readings:
    def __init__(self) -> None:
        self.readings: list[Reading] = []

    def __len__(self):
        return len(self.readings)

    @staticmethod
    def from_files(files: Iterable[Path], allowed_serials: list[str] | None = None):
        rs = Readings()
        rs.readings = [
            r
            for f in files
            if (r := Reading.from_string(f.name, allowed_serials)) is not None
        ]

        return rs

    def group_by_serial(self):
        res: dict[str, SerialReadings] = {}

        for r in self.readings:
            if r.serial is None:
                continue

            if r.serial not in res:
                res[r.serial] = SerialReadings(r.serial)

            res[r.serial].readings.append(r)

        return res

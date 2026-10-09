from collections.abc import Iterable
from datetime import date, timedelta
from pathlib import Path

from .reading import Reading


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

                if diff:
                    # Calculate trend
                    before_before = self.history(start=before.date, days=stat_days)
                    if before_before:

                        diff_before = diff_values(before_before, before, stat_days)
                        trend = diff - diff_before if diff_before else None

                    # Calculte mean for duration
                    mean_before = self.history(days=stat_mean_days)
                    if mean_before:
                        mean = diff_values(mean_before, latest, days=stat_days)
                        mean_diff = diff - mean if mean else None

        return diff, trend, mean, mean_diff


def diff_values(start: Reading, end: Reading, days: int):
    if end.date == start.date:
        return None

    return (end.value - start.value) / (end.date - start.date).days * days


class Readings:
    def __init__(self) -> None:
        self.readings: list[Reading] = []

    def __len__(self):
        return len(self.readings)

    @staticmethod
    def from_files(files: Iterable[Path], allowed_serials: list[str] | None = None):
        if allowed_serials is None:
            allowed_serials = []

        rs = Readings()
        rs.readings = [
            r
            for f in files
            if (r := Reading.from_file_name(f.name)) is not None
            and r.serial in allowed_serials
        ]

        return rs

    def group_by_serial(self):
        res: dict[str, SerialReadings] = {}

        for r in self.readings:

            if r.serial not in res:
                res[r.serial] = SerialReadings(r.serial)

            res[r.serial].readings.append(r)

        return res

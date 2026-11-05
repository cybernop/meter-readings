import datetime as dt

from .record import Record


class SerialRecords:
    def __init__(self, serial: str) -> None:
        self.serial: str = serial
        self.readings: list[Record] = []

    def latest(self) -> Record | None:
        return max(self.readings, key=lambda r: r.date)

    def history(
        self,
        start: dt.date | None = None,
        days: int = 0,
        weeks: int = 0,
        # years: int = 0,
    ):
        if start is None:
            if not (latest := self.latest()):
                return None

            start = latest.date

        entry = start - dt.timedelta(days=days, weeks=weeks)
        # entry.replace(year=entry.year - years)

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

    def __len__(self) -> int:
        return len(self.readings)


def diff_values(start: Record, end: Record, days: int):
    if end.date == start.date:
        return None

    return (end.value - start.value) / (end.date - start.date).days * days

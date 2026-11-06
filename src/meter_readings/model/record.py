import datetime as dt
import re
from pathlib import Path
from typing import Self

from pydantic import BaseModel

FILE_NAME_REGEX = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})_(?P<serial>\w+)(-(?P<id>\d-\d-\d))?_(?P<value>\d+(?:-\d+)?)"
)


class Record(BaseModel):
    """
    Model for a single meter reading
    """

    date: dt.date
    serial: str
    id: str | None = None
    value: float

    def dumps(self):
        return self.model_dump_json(indent=4, exclude_none=True)

    def write(self, file: Path):
        _ = file.write_text(self.dumps(), "utf-8")

    @staticmethod
    def from_file_name(name: str):
        """
        Parse the data from `name`
        """
        match = FILE_NAME_REGEX.search(name)

        if not match:
            return None

        data = match.groupdict()

        if value := data.get("value"):
            data["value"] = value.replace("-", ".")

        reading = Record.model_validate(data)
        return reading

    @staticmethod
    def read(file: Path):
        content = file.read_text("utf-8")
        return Record.model_validate_json(content)

    def file_name(self) -> str:
        """
        Create a file name that contains the same data
        """
        value = str(self.value).replace(".", "-").removesuffix("-0")
        name = f"{self.date!s}_{self.serial}{'-' + self.id if self.id else ''}_{value}"
        return name

    def __sub__(self, other: Self) -> float:
        """
        Normalized difference between records by days
        """
        if other.date == self.date:
            return 0.0

        return (self.value - other.value) / (self.date - other.date).days


class Records:
    def __init__(self, records: list[Record] | None = None) -> None:
        self.entries: list[Record] = records if records else []

    def __len__(self) -> int:
        return len(self.entries)

    def group_by_serial(self):
        """
        Group entries by serial

        Returns a list of `SerialRecords`. Each entry represents a serial number
        in the records and has the entries grouped.
        """
        res: dict[str, SerialRecords] = {}

        for r in self.entries:

            if r.serial not in res:
                res[r.serial] = SerialRecords(r.serial)

            res[r.serial].entries.append(r)

        return list(res.values())


class SerialRecords:
    def __init__(self, serial: str, records: list[Record] | None = None) -> None:
        self.serial: str = serial
        self.entries: list[Record] = records or []

    def latest(self) -> Record | None:
        """
        Get the entry with the latest date.
        """
        return max(self.entries, key=lambda r: r.date)

    def history(
        self,
        start: dt.date | None = None,
        days: int = 0,
        weeks: int = 0,
        years: int = 0,
    ):
        """
        Get a historic entry with the given time difference

        The reference date is defined by `start` or if not specified by the
        latest entry. The date is shifted back by `days`, `weeks` and `years`.
        The entry most close to the shifted date is returned.
        """
        if start is None:
            if not (latest := self.latest()):
                return None

            start = latest.date

        entry = start - dt.timedelta(days=days, weeks=weeks)
        entry = entry.replace(year=entry.year - years)

        return min(self.entries, key=lambda r: abs(r.date - entry))

    def weekly(self):
        days = 7
        mean_dur = 28

        return self._stats(days, mean_dur)

    def monthly(self):
        days = 30
        mean_dur = 365

        return self._stats(days, mean_dur)

    def yearly(self):
        days = 365
        mean_dur = 1000

        return self._stats(days, mean_dur)

    def _stats(self, stat_days: int, stat_mean_days: int):
        """
        Calculates statistics based on the provided time period(s)

        `diff`: Difference over the time period between the latest entry and the one `stat_days` before
        `trend`: Change from the previous to the current time period
        `mean`: Mean over `stat_mean_days`
        `mean_diff`: Difference between the mean and the difference over the current peroid
        """

        stat = RecordsStatistic(stat_days)

        latest = self.latest()
        before = self.history(days=stat_days)
        stat.calc_diff(before, latest)

        before_before = self.history(
            start=before.date if before else None, days=stat_days
        )
        stat.calc_trend(before_before, before)

        mean_before = self.history(days=stat_mean_days)
        stat.calc_mean(mean_before, latest)

        return stat

    def __len__(self) -> int:
        return len(self.entries)


class RecordsStatistic:
    def __init__(self, scaling: float = 1.0) -> None:
        self._diff: float | None = None
        self._trend: float | None = None
        self._mean: float | None = None
        self._mean_diff: float | None = None
        self.scaling: float = scaling

    @property
    def diff(self):
        return self._diff * self.scaling if self._diff else None

    def calc_diff(self, before: Record | None, latest: Record | None):
        if before and latest:
            self._diff = latest - before

    @property
    def trend(self):
        return self._trend * self.scaling if self._trend else None

    def calc_trend(self, before_before: Record | None, before: Record | None):
        if self._diff and before_before and before:
            self._trend = self._diff - (before_before - before)

    @property
    def mean(self):
        return self._mean * self.scaling if self._mean else None

    def calc_mean(self, before: Record | None, latest: Record | None):
        if before and latest:
            self._mean = latest - before

    @property
    def mean_diff(self):
        if self._diff and self._mean:
            return (self._diff - self._mean) * self.scaling

        else:
            return None

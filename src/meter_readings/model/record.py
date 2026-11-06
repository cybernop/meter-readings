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

    def __sub__(self, other: Self):
        """
        Normalized difference between records by days
        """
        if other.date == self.date:
            return 0.0

        return (self.value - other.value) / (self.date - other.date).days

import re
from datetime import date

from pydantic import BaseModel

FILE_NAME_REGEX = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})_((?P<serial>\w+)(-(?P<id>\d-\d-\d))?_(?P<value>\d+(?:-\d+)?))?"
)


class Reading(BaseModel):
    date: date
    serial: str | None = None
    id: str | None = None
    value: float | None = None

    @staticmethod
    def from_file_name(name: str):
        match = FILE_NAME_REGEX.search(name)

        if not match:
            return None

        data = match.groupdict()

        if value := data.get("value"):
            data["value"] = value.replace("-", ".")

        reading = Reading.model_validate(data)
        return reading

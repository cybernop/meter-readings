import re

from ..model.reading_ import Reading

FILE_NAME_REGEX = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})_((?P<serial>\w+)(-(?P<id>\d-\d-\d))?_(?P<value>\d+(?:-\d+)?))?"
)


def reading_from(name: str):
    match = FILE_NAME_REGEX.search(name)

    if not match:
        return None

    data = match.groupdict()

    if value := data.get("value"):
        data["value"] = value.replace("-", ".")

    reading = Reading.model_validate(data)
    return reading

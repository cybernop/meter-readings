from pathlib import Path

from pydantic import ValidationError

from ..errors import FileAlreadyExistsError, ReadingInvalidError
from ..model.reading import Reading


def migrate(file: Path) -> Path | None:
    """
    Migrate the file name based data to data files.

    If `file` contains correct data in its file name, a data file with the same stem is created
    and the file returned. `None` is returned otherwise.
    """
    file_name = file.stem

    try:
        reading = Reading.from_file_name(file_name)

    except ValidationError as e:
        raise ReadingInvalidError(f"error while  parsing from file name '{file!s}'", e)

    if not reading:
        return

    output_file = file.with_suffix(".json")

    if output_file.exists():
        raise FileAlreadyExistsError(
            f"migration failed: data file {output_file!s} already exists"
        )

    reading.write(output_file)

    return output_file


def get_data_file(file: Path) -> Path | None:
    """
    Get the data file if exists
    """
    data_file = file.with_suffix(".json")

    return data_file if data_file.exists() else None

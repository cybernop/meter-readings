from pathlib import Path

from pydantic import ValidationError

from ..errors import FileAlreadyExistsError, ReadingInvalidError
from ..io import file
from ..model.reading import Record

IMG_SUFFIXES = [".jpg", ".jpeg", ".png"]


def read_records(directory: Path | str) -> list[Record]:
    """
    Read the records from a directory

    Get the records for all image files. The data for each record is read from
    the corresponding data file with the same name. If the data file does not
    already exist, a migration is done, that tries to pull the data from the
    file name.
    """
    readings: list[Record] = []
    for f in Path(directory).expanduser().iterdir():
        if f.suffix.lower() in IMG_SUFFIXES:
            if (data_file := file.get_data_file(f)) is None:
                data_file = file.migrate(f)

            if data_file is None:
                continue

            readings.append(Record.read(data_file))

    return readings


def migrate(file: Path) -> Path | None:
    """
    Migrate the file name based data to data files.

    If `file` contains correct data in its file name, a data file with the same stem is created
    and the file returned. `None` is returned otherwise.
    """
    file_name = file.stem

    try:
        reading = Record.from_file_name(file_name)

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
    return data_file if data_file.exists() else None

import re
from datetime import date as datetime_date
from pathlib import Path

from pydantic import ValidationError

from .. import log
from ..errors import FileAlreadyExistsError, ReadDirectoryNotExist, ReadingInvalidError
from ..model.reading import Record

IMG_SUFFIXES = [".jpg", ".jpeg", ".png"]
DATE_REGEX = re.compile(
    r"((?:19|20)\d{2}-?(?:0\d|1(?:0|1|2))-?(?:(?:0|1|2)\d|3(?:0|1)))"
)


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
            if (data_file := get_data_file(f)) is None:
                data_file = migrate(f)

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


def move_with_date(input_dir: Path, output_dir: Path):
    """
    Move files while adding that date to the file name

    If date could not be determined, the file will not be moved.
    """

    print("\nAdd date")

    input_dir = input_dir.expanduser().absolute()
    output_dir = output_dir.expanduser().absolute()

    if not input_dir.exists():
        raise ReadDirectoryNotExist(f"input dir `{input_dir}` does not exist")

    if not output_dir.exists():
        log.info(f"output dir `{output_dir}` does not exist, creating")
        output_dir.mkdir(parents=True)

    log.info(f"Input dir: {input_dir}")
    log.info(f"Output dir: {output_dir}")

    rename: dict[Path, list[tuple[int, Path]]] = {}
    for file in input_dir.iterdir():
        if file.suffix.lower() not in IMG_SUFFIXES:
            log.warning(f"skipping `{file}`, wrong extension")
            continue

        if (date_match := DATE_REGEX.search(file.name)) is None:
            log.warning(f"date not found in `{file}`, skipping")
            continue

        date = datetime_date.fromisoformat(date_match.group(0))

        new_file = output_dir / (date.isoformat() + ".jpg")

        if new_file not in rename:
            rename[new_file] = []

        file_indices = [i for i, _ in rename[new_file]]
        count = 0
        while with_suffix(new_file, count).exists() or count in file_indices:
            count += 1

        rename[new_file].append((count, file))

    if len(rename) == 0:
        log.info("no files found..\n")
        return

    print("\nRename:")
    for new_file, file_list in rename.items():
        for i, file in file_list:
            print(f"{file.name} -> {with_suffix(new_file, i).name}")
            _ = file.move(with_suffix(new_file, i))

    log.info("done..\n")


def with_suffix(file: Path, suffix_nr: int):
    return file.with_stem(f"{file.stem}_{suffix_nr:02}")

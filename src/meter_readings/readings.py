from pathlib import Path

from . import log
from .model.reading import READING_REGEX, Readings


def get_readings(input_dir: Path):
    print("\nGet Readings")

    input_dir = input_dir.expanduser().absolute()

    log.info(f"got {len(list(input_dir.iterdir()))} files")

    not_matching = [
        f
        for f in input_dir.iterdir()
        if f.is_file() and READING_REGEX.search(f.name) is None
    ]
    log.info(f"{len(not_matching)} not matching readings pattern")

    readings = Readings.from_files(input_dir.iterdir())
    log.info(f"got {len(readings)}")

    return readings

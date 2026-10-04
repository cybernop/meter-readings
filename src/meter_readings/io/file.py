from pathlib import Path

from ..model.reading import Reading


def migrate(file: Path):
    """
    Migrate the file name based data to data files.

    If `file` contains correct data in its file name, a data file with the same stem is created
    and the file returned. `None` is returned otherwise.
    """
    file_name = file.stem
    reading = Reading.from_file_name(file_name)

    if not reading:
        return

    output_file = file.with_suffix(".json")

    # TODO: move writing to reading model
    _ = output_file.write_text(reading.model_dump_json(indent=4), "utf-8")

    return output_file

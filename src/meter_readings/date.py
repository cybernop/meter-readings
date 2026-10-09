import re
from datetime import date as datetime_date
from pathlib import Path

from . import log
from .helpers import confirm

date_regex = re.compile(
    r"((?:19|20)\d{2}-?(?:0\d|1(?:0|1|2))-?(?:(?:0|1|2)\d|3(?:0|1)))"
)


def add_date(input_dir: Path, output_dir: Path):

    print("\nAdd date")

    input_dir = input_dir.expanduser().absolute()
    output_dir = output_dir.expanduser().absolute()

    if not input_dir.exists():
        raise Exception(f"input dir `{input_dir}` does not exist")

    if not output_dir.exists():
        log.info(f"output dir `{output_dir}` does not exist, creating")
        output_dir.mkdir(parents=True)

    log.info(f"Input dir: {input_dir}")
    log.info(f"Dated dir: {output_dir}")

    rename: dict[Path, list[tuple[int, Path]]] = {}
    for file in input_dir.iterdir():
        if file.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            log.warn(f"skipping `{file}`, wrong extension")
            continue

        if (date_match := date_regex.search(file.name)) is None:
            log.warn(f"date not found in `{file}`, skipping")
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

    print("\nWould rename:")
    for new_file, file_list in rename.items():
        for i, file in file_list:
            print(f"{file.name} -> {with_suffix(new_file, i).name}")

    if confirm("Proceed?"):
        for new_file, file_list in rename.items():
            for i, file in file_list:
                file.move(with_suffix(new_file, i))

        log.info("done..\n")


def with_suffix(file: Path, suffix_nr: int):
    return file.with_stem(f"{file.stem}_{suffix_nr:02}")

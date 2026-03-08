import re
from datetime import date as datetime_date
from pathlib import Path

from . import log

date_regex = re.compile(
    r"((?:19|20)\d{2}-?(?:0\d|1(?:0|1|2))-?(?:(?:0|1|2)\d|3(?:0|1)))"
)


def add_date(input_dir: Path, output_dir: Path):

    print("\nadd date")

    input_dir = input_dir.expanduser().absolute()
    output_dir = output_dir.expanduser().absolute()

    if not input_dir.exists():
        raise Exception("input dir `{}` does not exist".format(input_dir))

    if not output_dir.exists():
        log.info("output dir `{}` does not exist, creating".format(output_dir))
        output_dir.mkdir(parents=True)

    log.info("read files from `{}`".format(input_dir))
    log.info("move dated files to `{}`".format(output_dir))
    for file in input_dir.iterdir():
        if file.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            log.warn("skipping `{}`, wrong extension".format(file))
            continue

        if (date_match := date_regex.search(file.name)) is None:
            log.warn("date not found in `{}`, skipping".format(file))
            continue

        date = datetime_date.fromisoformat(date_match.group(0))

        new_file = output_dir / "{}_{}".format(date, file.name)

        log.info("adding date `{}` -> `{}`".format(file.name, new_file.name))
        file.move(new_file)

    print("\n")

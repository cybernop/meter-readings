import json
from pathlib import Path
from tempfile import TemporaryDirectory

from meter_readings.io import file


def test_migrate_correct_file_name():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234"

    file_name = f"{date_str}_{serial_str}_{value_str}"
    wanted = {
        "date": date_str,
        "serial": serial_str,
        "value": float(value_str),
    }

    with TemporaryDirectory() as temp_dir:
        input = Path(temp_dir) / (file_name + ".txt")
        output = file.migrate(input)

        assert output
        assert output.exists()
        assert input.parent == output.parent
        assert input.stem == output.stem

        result = json.loads(output.read_text())  # pyright: ignore[reportAny]
        assert wanted == result


def test_migrate_incorrect_file_name():
    file_name = "foobar"

    with TemporaryDirectory() as temp_dir:
        input = Path(temp_dir) / (file_name + ".txt")
        output = file.migrate(input)

        assert output is None
        assert not input.with_suffix(".json").exists()

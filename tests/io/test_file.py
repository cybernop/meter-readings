import json
from pathlib import Path
from tempfile import TemporaryDirectory

from meter_readings.errors import FileAlreadyExistsError
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


def test_migrate_already_exists():
    file_name = "2026-01-01_ABC1234GH_1234"

    with TemporaryDirectory() as temp_dir:
        input = Path(temp_dir) / (file_name + ".txt")
        input.with_suffix(".json").touch()

        try:
            _ = file.migrate(input)

        except FileAlreadyExistsError:
            pass

        else:
            assert False


def test_migrate_incorrect_file_name():
    file_name = "foobar"

    with TemporaryDirectory() as temp_dir:
        input = Path(temp_dir) / (file_name + ".txt")
        output = file.migrate(input)

        assert output is None
        assert not input.with_suffix(".json").exists()


def test_get_data_file():
    file_name = "2026-01-01_ABC1234GH_1234"

    with TemporaryDirectory() as temp_dir:
        input = Path(temp_dir) / (file_name + ".txt")

        assert file.get_data_file(input) is None

        input.with_suffix(".json").touch()
        assert file.get_data_file(input) is not None

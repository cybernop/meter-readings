import json
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from meter_readings.errors import FileAlreadyExistsError
from meter_readings.io import file
from meter_readings.model.reading import Reading


def test_read_records_single():
    wanted = Reading(
        date=date.fromisoformat("2026-01-01"),
        serial="ABC1234GH",
        value=1234,
    )

    with TemporaryDirectory() as tmp_dir:
        file_name = wanted.file_name()
        (Path(tmp_dir) / (file_name + ".png")).touch()
        wanted.write(Path(tmp_dir) / (file_name + ".json"))

        result = file.read_records(tmp_dir)

        assert len(result) == 1
        assert wanted == result[0]


def test_read_records_multiple():
    wanted = [
        Reading(
            date=date.fromisoformat("2026-01-01"),
            serial="ABC1234GH",
            value=1234,
        ),
        Reading(
            date=date.fromisoformat("2026-01-02"),
            serial="ABC1234GH",
            value=1235,
        ),
    ]

    with TemporaryDirectory() as tmp_dir:
        for w in wanted:
            file_name = w.file_name()
            (Path(tmp_dir) / (file_name + ".png")).touch()
            w.write(Path(tmp_dir) / (file_name + ".json"))

        result = file.read_records(tmp_dir)

    wanted = sorted(wanted, key=lambda x: x.date)
    result = sorted(result, key=lambda x: x.date)

    assert len(result) == 2
    assert wanted[0] == result[0]
    assert wanted[1] == result[1]


def test_read_records_migrate():
    wanted = Reading(
        date=date.fromisoformat("2026-01-01"),
        serial="ABC1234GH",
        value=1234,
    )

    with TemporaryDirectory() as tmp_dir:
        file_name = wanted.file_name()
        (Path(tmp_dir) / (file_name + ".png")).touch()
        assert not (Path(tmp_dir) / (file_name + ".json")).exists()

        result = file.read_records(tmp_dir)

        assert (Path(tmp_dir) / (file_name + ".json")).exists()
        assert len(result) == 1
        assert wanted == result[0]


def test_read_records_migrate_not_possible():
    with TemporaryDirectory() as tmp_dir:
        file_name = "foobar"

        (Path(tmp_dir) / (file_name + ".png")).touch()
        assert not (Path(tmp_dir) / (file_name + ".json")).exists()

        result = file.read_records(tmp_dir)
        assert not (Path(tmp_dir) / (file_name + ".json")).exists()
        assert len(result) == 0


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

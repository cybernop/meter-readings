import json
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from meter_readings.model.reading import Record


def test_from_file_name_only_date():
    date_str = "2026-01-01"

    input = f"{date_str}_1"

    result = Record.from_file_name(input)
    assert result is None


def test_from_file_name_serial_numerical_and_value_integer():
    date_str = "2026-01-01"
    serial_str = "123456789"
    value_str = "1234"

    input = f"{date_str}_{serial_str}_{value_str}"
    wanted = Record(
        date=date.fromisoformat(date_str), serial=serial_str, value=float(value_str)
    )

    result = Record.from_file_name(input)
    assert wanted == result


def test_from_file_name_serial_alphanumerical_and_value_float():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234-567"

    input = f"{date_str}_{serial_str}_{value_str}"
    wanted = Record(
        date=date.fromisoformat(date_str),
        serial=serial_str,
        value=float(value_str.replace("-", ".")),
    )

    result = Record.from_file_name(input)
    assert wanted == result


def test_from_file_name_serial_numerical_and_value_integer_with_id():
    date_str = "2026-01-01"
    serial_str = "123456789"
    id_str = "1-8-0"
    value_str = "1234"

    input = f"{date_str}_{serial_str}-{id_str}_{value_str}"
    wanted = Record(
        date=date.fromisoformat(date_str),
        serial=serial_str,
        id=id_str,
        value=float(value_str),
    )

    result = Record.from_file_name(input)
    assert wanted == result


def test_file_name():
    date_str = "2026-01-01"
    serial_str = "123456789"
    value_str = "1234"

    input = Record(
        date=date.fromisoformat(date_str), serial=serial_str, value=float(value_str)
    )
    wanted = f"{date_str}_{serial_str}_{value_str}"

    result = input.file_name()
    assert wanted == result


def test_file_name_with_id():
    date_str = "2026-01-01"
    serial_str = "123456789"
    id_str = "1-8-0"
    value_str = "1234"

    input = Record(
        date=date.fromisoformat(date_str),
        serial=serial_str,
        id=id_str,
        value=float(value_str),
    )
    wanted = f"{date_str}_{serial_str}-{id_str}_{value_str}"

    result = input.file_name()
    assert wanted == result


def test_filename_to_filename():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234-567"

    input = f"{date_str}_{serial_str}_{value_str}"

    reading = Record.from_file_name(input)
    assert reading

    result = reading.file_name()
    assert input == result


def test_filename_to_filename_int():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234"

    input = f"{date_str}_{serial_str}_{value_str}"

    reading = Record.from_file_name(input)
    assert reading

    result = reading.file_name()
    assert input == result


def test_reading_to_reading():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234-567"

    input = Record(
        date=date.fromisoformat(date_str),
        serial=serial_str,
        value=float(value_str.replace("-", ".")),
    )

    file_name = input.file_name()
    result = Record.from_file_name(file_name)
    assert input == result


def test_read():
    input = {
        "date": "2026-01-01",
        "serial": "123456789",
        "value": 1234,
    }

    with TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "file.json"
        _ = tmp_file.write_text(json.dumps(input))

        result = Record.read(tmp_file)

    assert input == json.loads(result.model_dump_json(exclude_none=True))


def test_write():
    input = Record(
        date=date.fromisoformat("2026-01-01"), serial="123456789", value=1234
    )

    with TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "file.json"

        input.write(tmp_file)
        result = Record.model_validate_json(tmp_file.read_text("utf-8"))

    assert input == result


def test_read_write():
    input = {
        "date": "2026-01-01",
        "serial": "123456789",
        "value": 1234,
    }

    with TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "file.json"
        _ = tmp_file.write_text(json.dumps(input))

        tmp = Record.read(tmp_file)
        _ = tmp.write(tmp_file)

        result = json.loads(tmp_file.read_text("utf-8"))  # pyright: ignore[reportAny]

    assert input == result


def test_write_read():
    input = Record(
        date=date.fromisoformat("2026-01-01"), serial="123456789", value=1234
    )

    with TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "file.json"

        _ = input.write(tmp_file)
        result = Record.read(tmp_file)

    assert input == result

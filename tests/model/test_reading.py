from datetime import date

from meter_readings.model.reading import Reading


def test_from_file_name_only_date():
    date_str = "2026-01-01"

    input = f"{date_str}_1"

    result = Reading.from_file_name(input)
    assert result is None


def test_from_file_name_serial_numerical_and_value_integer():
    date_str = "2026-01-01"
    serial_str = "123456789"
    value_str = "1234"

    input = f"{date_str}_{serial_str}_{value_str}"
    wanted = Reading(
        date=date.fromisoformat(date_str), serial=serial_str, value=float(value_str)
    )

    result = Reading.from_file_name(input)
    assert wanted == result


def test_from_file_name_serial_alphanumerical_and_value_float():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234-567"

    input = f"{date_str}_{serial_str}_{value_str}"
    wanted = Reading(
        date=date.fromisoformat(date_str),
        serial=serial_str,
        value=float(value_str.replace("-", ".")),
    )

    result = Reading.from_file_name(input)
    assert wanted == result


def test_from_file_name_serial_numerical_and_value_integer_with_id():
    date_str = "2026-01-01"
    serial_str = "123456789"
    id_str = "1-8-0"
    value_str = "1234"

    input = f"{date_str}_{serial_str}-{id_str}_{value_str}"
    wanted = Reading(
        date=date.fromisoformat(date_str),
        serial=serial_str,
        id=id_str,
        value=float(value_str),
    )

    result = Reading.from_file_name(input)
    assert wanted == result


def test_file_name():
    date_str = "2026-01-01"
    serial_str = "123456789"
    value_str = "1234"

    input = Reading(
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

    input = Reading(
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

    reading = Reading.from_file_name(input)
    assert reading

    result = reading.file_name()
    assert input == result


def test_filename_to_filename_int():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234"

    input = f"{date_str}_{serial_str}_{value_str}"

    reading = Reading.from_file_name(input)
    assert reading

    result = reading.file_name()
    assert input == result


def test_reading_to_reading():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234-567"

    input = Reading(
        date=date.fromisoformat(date_str),
        serial=serial_str,
        value=float(value_str.replace("-", ".")),
    )

    file_name = input.file_name()
    result = Reading.from_file_name(file_name)
    assert input == result

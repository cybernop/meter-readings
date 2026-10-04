from datetime import date

from meter_readings.model.reading import Reading


def test_reading_from_file_name_only_date():
    date_str = "2026-01-01"

    input = f"{date_str}_1"
    wanted = Reading(date=date.fromisoformat(date_str))

    result = Reading.from_file_name(input)
    assert wanted == result


def test_reading_from_file_name_serial_numerical_and_value_integer():
    date_str = "2026-01-01"
    serial_str = "123456789"
    value_str = "1234"

    input = f"{date_str}_{serial_str}_{value_str}"
    wanted = Reading(
        date=date.fromisoformat(date_str), serial=serial_str, value=float(value_str)
    )

    result = Reading.from_file_name(input)
    assert wanted == result


def test_reading_from_file_name_serial_alphanumerical_and_value_float():
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


def test_reading_from_file_name_serial_numerical_and_value_integer_with_id():
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

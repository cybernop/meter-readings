import datetime as dt
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from pytest import approx

from meter_readings.model.record import Record, Records, RecordsStatistic, SerialRecords


def test_record_from_file_name_only_date():
    date_str = "2026-01-01"

    input = f"{date_str}_1"

    result = Record.from_file_name(input)
    assert result is None


def test_record_from_file_name_serial_numerical_and_value_integer():
    date_str = "2026-01-01"
    serial_str = "123456789"
    value_str = "1234"

    input = f"{date_str}_{serial_str}_{value_str}"
    wanted = Record(
        date=dt.date.fromisoformat(date_str), serial=serial_str, value=float(value_str)
    )

    result = Record.from_file_name(input)
    assert wanted == result


def test_record_from_file_name_serial_alphanumerical_and_value_float():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234-567"

    input = f"{date_str}_{serial_str}_{value_str}"
    wanted = Record(
        date=dt.date.fromisoformat(date_str),
        serial=serial_str,
        value=float(value_str.replace("-", ".")),
    )

    result = Record.from_file_name(input)
    assert wanted == result


def test_record_from_file_name_serial_numerical_and_value_integer_with_id():
    date_str = "2026-01-01"
    serial_str = "123456789"
    id_str = "1-8-0"
    value_str = "1234"

    input = f"{date_str}_{serial_str}-{id_str}_{value_str}"
    wanted = Record(
        date=dt.date.fromisoformat(date_str),
        serial=serial_str,
        id=id_str,
        value=float(value_str),
    )

    result = Record.from_file_name(input)
    assert wanted == result


def test_record_file_name():
    date_str = "2026-01-01"
    serial_str = "123456789"
    value_str = "1234"

    input = Record(
        date=dt.date.fromisoformat(date_str), serial=serial_str, value=float(value_str)
    )
    wanted = f"{date_str}_{serial_str}_{value_str}"

    result = input.file_name()
    assert wanted == result


def test_record_file_name_with_id():
    date_str = "2026-01-01"
    serial_str = "123456789"
    id_str = "1-8-0"
    value_str = "1234"

    input = Record(
        date=dt.date.fromisoformat(date_str),
        serial=serial_str,
        id=id_str,
        value=float(value_str),
    )
    wanted = f"{date_str}_{serial_str}-{id_str}_{value_str}"

    result = input.file_name()
    assert wanted == result


def test_record_filename_to_filename():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234-567"

    input = f"{date_str}_{serial_str}_{value_str}"

    reading = Record.from_file_name(input)
    assert reading

    result = reading.file_name()
    assert input == result


def test_record_filename_to_filename_int():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234"

    input = f"{date_str}_{serial_str}_{value_str}"

    reading = Record.from_file_name(input)
    assert reading

    result = reading.file_name()
    assert input == result


def test_record_reading_to_reading():
    date_str = "2026-01-01"
    serial_str = "ABC1234GH"
    value_str = "1234-567"

    input = Record(
        date=dt.date.fromisoformat(date_str),
        serial=serial_str,
        value=float(value_str.replace("-", ".")),
    )

    file_name = input.file_name()
    result = Record.from_file_name(file_name)
    assert input == result


def test_record_read():
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


def test_record_write():
    input = Record(
        date=dt.date.fromisoformat("2026-01-01"), serial="123456789", value=1234
    )

    with TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "file.json"

        input.write(tmp_file)
        result = Record.model_validate_json(tmp_file.read_text("utf-8"))

    assert input == result


def test_record_read_write():
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


def test_record_write_read():
    input = Record(
        date=dt.date.fromisoformat("2026-01-01"), serial="123456789", value=1234
    )

    with TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "file.json"

        _ = input.write(tmp_file)
        result = Record.read(tmp_file)

    assert input == result


def test_record_sub_diff_date():
    first = Record(
        date=dt.date.fromisoformat("2026-01-01"), serial="123456789", value=1
    )

    second = Record(
        date=dt.date.fromisoformat("2026-01-07"), serial="123456789", value=7
    )

    diff = second - first
    assert 1 == diff


def test_record_sub_same_date():
    first = Record(
        date=dt.date.fromisoformat("2026-01-01"), serial="123456789", value=0
    )

    second = Record(
        date=dt.date.fromisoformat("2026-01-01"), serial="123456789", value=7
    )

    diff = second - first
    assert 0 == diff


def test_records_same_serial():

    input = [
        Record(
            date=dt.date.fromisoformat("2026-01-01"),
            serial="123456789",
            value=1234,
        ),
        Record(
            date=dt.date.fromisoformat("2026-01-02"),
            serial="123456789",
            value=1235,
        ),
    ]

    records = Records(input)

    assert 2 == len(records)

    groups = records.group_by_serial()
    assert 1 == len(groups)
    assert 2 == len(groups[0])


def test_records_different_serial():

    input = [
        Record(
            date=dt.date.fromisoformat("2026-01-01"),
            serial="123456789",
            value=1234,
        ),
        Record(
            date=dt.date.fromisoformat("2026-01-01"),
            serial="123456780",
            value=1235,
        ),
    ]

    records = Records(input)

    assert 2 == len(records)

    groups = records.group_by_serial()
    assert 2 == len(groups)
    assert 1 == len(groups[0])
    assert 1 == len(groups[1])


def test_serial_records_latest_serial_records_sorted():
    serial = "123456789"

    input = [
        Record(
            date=dt.date.fromisoformat("2026-01-01"),
            serial=serial,
            value=1234,
        ),
        Record(
            date=dt.date.fromisoformat("2026-01-02"),
            serial=serial,
            value=1235,
        ),
    ]

    records = SerialRecords(serial, input)
    latest = records.latest()

    assert latest is not None
    assert 2 == latest.date.day


def test_serial_records_latest_serial_records_unsorted():
    serial = "123456789"

    input = [
        Record(
            date=dt.date.fromisoformat("2026-01-02"),
            serial=serial,
            value=1235,
        ),
        Record(
            date=dt.date.fromisoformat("2026-01-01"),
            serial=serial,
            value=1234,
        ),
    ]

    records = SerialRecords(serial, input)
    latest = records.latest()

    assert latest is not None
    assert 2 == latest.date.day


def test_serial_records_history_day():
    serial = "123456789"

    input = [
        Record(
            date=dt.date.fromisoformat("2026-01-01"),
            serial=serial,
            value=1234,
        ),
        Record(
            date=dt.date.fromisoformat("2026-01-02"),
            serial=serial,
            value=1235,
        ),
        Record(
            date=dt.date.fromisoformat("2026-01-03"),
            serial=serial,
            value=1235,
        ),
    ]

    records = SerialRecords(serial, input)

    entry = records.history(days=1)
    assert entry is not None
    assert dt.date(year=2026, month=1, day=2) == entry.date

    entry = records.history(days=2)
    assert entry is not None
    assert dt.date(year=2026, month=1, day=1) == entry.date

    entry = records.history(start=dt.date.fromisoformat("2026-01-02"), days=1)
    assert entry is not None
    assert dt.date(year=2026, month=1, day=1) == entry.date


def test_serial_records_history_week():
    serial = "123456789"

    input = [
        Record(
            date=dt.date.fromisoformat("2026-01-01"),
            serial=serial,
            value=1234,
        ),
        Record(
            date=dt.date.fromisoformat("2026-01-02"),
            serial=serial,
            value=1235,
        ),
        Record(
            date=dt.date.fromisoformat("2026-01-03"),
            serial=serial,
            value=1235,
        ),
        Record(
            date=dt.date.fromisoformat("2026-01-09"),
            serial=serial,
            value=1235,
        ),
    ]

    records = SerialRecords(serial, input)

    entry = records.history(weeks=1)
    assert entry is not None
    assert dt.date(year=2026, month=1, day=2) == entry.date


def test_serial_records_history_year():
    serial = "123456789"

    input = [
        Record(
            date=dt.date.fromisoformat("2026-01-01"),
            serial=serial,
            value=1234,
        ),
        Record(
            date=dt.date.fromisoformat("2026-01-02"),
            serial=serial,
            value=1235,
        ),
        Record(
            date=dt.date.fromisoformat("2026-01-03"),
            serial=serial,
            value=1235,
        ),
        Record(
            date=dt.date.fromisoformat("2027-01-02"),
            serial=serial,
            value=1235,
        ),
    ]

    records = SerialRecords(serial, input)

    entry = records.history(years=1)
    assert entry is not None
    assert dt.date(year=2026, month=1, day=2) == entry.date


def test_serial_records_weekly():
    serial = "123456789"
    ref_date = dt.date.fromisoformat("2026-01-01")

    input = [
        Record(
            date=ref_date,
            serial=serial,
            value=40,
        ),
        Record(
            date=ref_date - dt.timedelta(weeks=1),
            serial=serial,
            value=30,
        ),
        Record(
            date=ref_date - dt.timedelta(weeks=2),
            serial=serial,
            value=25,
        ),
        Record(
            date=ref_date - dt.timedelta(weeks=4),
            serial=serial,
            value=10,
        ),
    ]

    records = SerialRecords(serial, input)

    stat = records.weekly()

    assert approx(10) == stat.diff
    assert approx(5) == stat.trend
    assert approx(7.5) == stat.mean
    assert approx(2.5) == stat.mean_diff


def test_serial_records_monthly():
    serial = "123456789"
    ref_date = dt.date.fromisoformat("2026-01-01")

    input = [
        Record(
            date=ref_date,
            serial=serial,
            value=40,
        ),
        Record(
            date=ref_date - dt.timedelta(days=30),
            serial=serial,
            value=30,
        ),
        Record(
            date=ref_date - dt.timedelta(days=60),
            serial=serial,
            value=25,
        ),
        Record(
            date=ref_date - dt.timedelta(days=360),
            serial=serial,
            value=10,
        ),
    ]

    records = SerialRecords(serial, input)

    stat = records.monthly()

    assert approx(10) == stat.diff
    assert approx(5) == stat.trend
    assert approx(2.5) == stat.mean
    assert approx(7.5) == stat.mean_diff


def test_serial_records_yearly():
    serial = "123456789"
    ref_date = dt.date.fromisoformat("2026-01-01")

    input = [
        Record(
            date=ref_date,
            serial=serial,
            value=40,
        ),
        Record(
            date=ref_date - dt.timedelta(days=365),
            serial=serial,
            value=30,
        ),
        Record(
            date=ref_date - dt.timedelta(days=365 * 2),
            serial=serial,
            value=25,
        ),
        Record(
            date=ref_date - dt.timedelta(days=1000),
            serial=serial,
            value=12.59,
        ),
    ]

    records = SerialRecords(serial, input)

    stat = records.yearly()

    assert approx(10) == stat.diff
    assert approx(5) == stat.trend
    assert approx(10, abs=0.01) == stat.mean
    assert approx(0, abs=0.01) == stat.mean_diff


def test_records_statistic():
    serial = "123456789"
    mean_before = Record(
        date=dt.date.fromisoformat("2026-02-18"),
        serial=serial,
        value=10,
    )
    before_before = Record(
        date=dt.date.fromisoformat("2026-02-23"),
        serial=serial,
        value=65,
    )
    before = Record(
        date=dt.date.fromisoformat("2026-02-24"),
        serial=serial,
        value=70,
    )
    latest = Record(
        date=dt.date.fromisoformat("2026-02-25"),
        serial=serial,
        value=80,
    )

    stat = RecordsStatistic()

    assert stat.diff is None
    assert stat.trend is None
    assert stat.mean is None
    assert stat.mean_diff is None

    stat.calc_diff(before, latest)
    assert 10 == stat.diff

    stat.calc_trend(before_before, before)
    assert 5 == stat.trend

    stat.calc_mean(mean_before, latest)
    assert 10 == stat.mean

    assert 0 == stat.mean_diff

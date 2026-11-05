import datetime as dt

from meter_readings.model.record import Record
from meter_readings.model.serial_records import SerialRecords


def test_latest_sorted():
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
    assert latest.date.day == 2


def test_latest_unsorted():
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
    assert latest.date.day == 2


def test_history_day():
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
    assert entry.date == dt.date(year=2026, month=1, day=2)

    entry = records.history(days=2)
    assert entry is not None
    assert entry.date == dt.date(year=2026, month=1, day=1)
    entry = records.history(start=dt.date.fromisoformat("2026-01-02"), days=1)
    assert entry is not None
    assert entry.date == dt.date(year=2026, month=1, day=1)


def test_history_week():
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
    assert entry.date == dt.date(year=2026, month=1, day=2)


def test_history_year():
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
    assert entry.date == dt.date(year=2026, month=1, day=2)


# TODO: tests for stats for weekly, monthly and yearly

import datetime as dt

from meter_readings.model.record import Record
from meter_readings.model.records import Records


def test_same_serial():

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

    assert len(records) == 2

    groups = records.group_by_serial()
    assert len(groups) == 1
    assert len(groups[0]) == 2


def test_different_serial():

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

    assert len(records) == 2

    groups = records.group_by_serial()
    assert len(groups) == 2
    assert len(groups[0]) == 1
    assert len(groups[1]) == 1

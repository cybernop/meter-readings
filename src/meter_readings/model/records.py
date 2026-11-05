from .record import Record
from .serial_records import SerialRecords


class Records:
    def __init__(self, records: list[Record] | None = None) -> None:
        self.readings: list[Record] = records if records else []

    def __len__(self) -> int:
        return len(self.readings)

    def group_by_serial(self) -> list[SerialRecords]:
        res: dict[str, SerialRecords] = {}

        for r in self.readings:

            if r.serial not in res:
                res[r.serial] = SerialRecords(r.serial)

            res[r.serial].readings.append(r)

        return list(res.values())

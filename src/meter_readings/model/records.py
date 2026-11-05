from .record import Record
from .serial_records import SerialRecords


class Records:
    def __init__(self, records: list[Record] | None = None) -> None:
        self.entries: list[Record] = records if records else []

    def __len__(self) -> int:
        return len(self.entries)

    def group_by_serial(self) -> list[SerialRecords]:
        """
        Group entries by serial

        Returns a list of `SerialRecords`. Each entry represents a serial number
        in the records and has the entries grouped.
        """
        res: dict[str, SerialRecords] = {}

        for r in self.entries:

            if r.serial not in res:
                res[r.serial] = SerialRecords(r.serial)

            res[r.serial].entries.append(r)

        return list(res.values())

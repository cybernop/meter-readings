from pathlib import Path

from .io.file import move_with_date, read_records
from .model.serial_records import SerialRecords


def cli(input_folder: Path, data_folder: Path, output_dir: Path):
    move_with_date(input_folder, data_folder)
    records = read_records(data_folder)
    render_grouped_readings(
        records.group_by_serial(allowed_serials), serial_map, output_dir
    )
    # TODO: extract meter's number
    # TODO: extract meter reading
    # TODO: read information into table file
    # TODO: print latest trends
    # TODO: (optional) generate graph


def render_grouped_readings(
    readings: dict[str, SerialRecords], serials: dict[str, str], output_dir: Path
):
    lines = generate_stats(readings, serials)

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # Write stats
    (output_dir / "stats.txt").write_text("\n".join(lines), "utf-8")

    print("\nPrint Readings\n")
    for line in lines:
        print(line)


def generate_stats(readings: dict[str, SerialRecords], serials: dict[str, str]):
    lines: list[str] = []
    for s, sr in readings.items():
        line = f"{serials[s]} ({s})"
        lines.append(line)
        lines.append("=" * len(line))

        latest = sr.latest()
        if latest:
            lines.append(f"Latest: {latest.date}, {latest.value}")
            for f in ["weekly", "monthly", "yearly"]:
                diff, trend, mean, mean_diff = sr.__getattribute__(f)()
                lines.append(
                    f"{f}:\t{'\t' if len(f) < 7 else ''}{diff:.2f} ({trend:.2f})\tmean: {mean:.2f} ({mean_diff:.2f})"
                )

        lines.append("")

    return lines

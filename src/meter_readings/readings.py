from pathlib import Path

from . import log
from .model.reading import READING_REGEX, Readings, SerialReadings


def get_readings(input_dir: Path, allowed_serials: list[str] | None = None):
    print("\nGet Readings")

    input_dir = input_dir.expanduser().absolute()

    log.info(f"got {len(list(input_dir.iterdir()))} files")

    not_matching = [
        f
        for f in input_dir.iterdir()
        if f.is_file() and READING_REGEX.search(f.name) is None
    ]
    log.info(f"{len(not_matching)} not matching readings pattern")

    readings = Readings.from_files(input_dir.iterdir(), allowed_serials)
    log.info(f"got {len(readings)}\n")

    return readings


def render_grouped_readings(
    readings: dict[str, SerialReadings], serials: dict[str, str], output_dir: Path
):
    lines = generate_stats(readings, serials)

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # Write stats
    (output_dir / "stats.txt").write_text("\n".join(lines), "utf-8")

    print("\nPrint Readings\n")
    for line in lines:
        print(line)


def generate_stats(readings: dict[str, SerialReadings], serials: dict[str, str]):
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

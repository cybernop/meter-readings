from pathlib import Path

from .date import add_date
from .model.config import Config


def main():
    config = Path(
        "/home/cybernop/share/appartment/2025_23558_Am-Gueterbahnhof/Verbrauch/readings-config.yaml"
    )

    config = Config.from_yaml(config)

    add_date(config.folders.input, config.folders.dated)
    print("test")

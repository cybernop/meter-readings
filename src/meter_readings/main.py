from argparse import ArgumentParser
from pathlib import Path

from .date import add_date
from .model.config import Config


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "--config", required=True, type=Path, help="Path to the config file"
    )

    args = arg_parser.parse_args()

    config = Config.from_yaml(args.config)

    add_date(config.folders.input, config.folders.dated)

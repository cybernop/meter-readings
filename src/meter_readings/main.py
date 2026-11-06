import os
from argparse import ArgumentParser
from pathlib import Path

from .cli import cli
from .model.config import Config


def main():
    arg_parser = ArgumentParser()
    _ = arg_parser.add_argument(
        "--config", required=True, type=Path, help="Path to the config file"
    )

    args = arg_parser.parse_args()

    config = Config.from_yaml(args.config)

    os.chdir(args.config.parent)

    cli(
        config.folders.input,
        config.folders.dated,
        args.config.parent,
        list(config.serials.keys()),
    )

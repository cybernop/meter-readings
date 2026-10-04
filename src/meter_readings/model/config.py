from pathlib import Path

import yaml
from pydantic import BaseModel


class FoldersConfig(BaseModel):
    input: Path
    dated: Path


class Config(BaseModel):
    folders: FoldersConfig
    serials: dict[str, str]

    @staticmethod
    def from_yaml(file: Path):
        if not file.exists():
            raise Exception(f"Config file `{file}` does not exist")

        content = yaml.safe_load(file.read_text(encoding="utf-8"))

        return Config.model_validate(content)

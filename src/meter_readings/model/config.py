from pathlib import Path

import yaml
from pydantic import BaseModel


class FoldersConfig(BaseModel):
    input: Path
    dated: Path


class Config(BaseModel):
    folders: FoldersConfig

    @staticmethod
    def from_yaml(file: Path):
        if not file.exists():
            raise Exception("Config file `{}` does not exist".format(file))

        content = yaml.safe_load(file.read_text(encoding="utf-8"))

        return Config.model_validate(content)

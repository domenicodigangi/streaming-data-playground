import os
from pathlib import Path

import yaml

CONFIG_DIR = Path(os.path.dirname(__file__)).parent.parent.parent / "conf"


def load_config_yaml(file_name: str) -> dict:
    with open(CONFIG_DIR / file_name, 'r') as file:
        return yaml.safe_load(file)

import logging
import os
from pathlib import Path

import yaml

from simulator.core.setup_logger import setup_logger

logger = setup_logger(__name__, level=logging.INFO)
CONFIG_DIR = Path(os.path.dirname(__file__)).parent.parent.parent / "conf"


def load_config_yaml(file_name: str) -> dict:
    conf_file = CONFIG_DIR / file_name
    logger.info("Loading config file: %s", conf_file)
    with open(conf_file, 'r') as file:
        return yaml.safe_load(file)

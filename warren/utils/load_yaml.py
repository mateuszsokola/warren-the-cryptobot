import yaml
import sys

from warren.utils.logger import logger


def load_yaml(file: str):
    with open(file, "r") as stream:
        try:
            content = yaml.safe_load(stream)
            return content
        except yaml.YAMLError as exc:
            logger.error(f"Couldn't read {file} file", exc)
            sys.exit()

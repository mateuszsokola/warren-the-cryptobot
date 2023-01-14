import json
import sys

from warren.utils.logger import logger


def load_contract_abi(
    contract_name: str,
    root_dir: str = "artifacts",
) -> dict:
    try:
        file_path = f"{root_dir}/{contract_name}"
        with open(file_path) as f:
            return json.load(f)["abi"]
    except FileNotFoundError:
        logger.error(f"Interface ABI `{contract_name}`.json not found in {root_dir}")
        sys.exit()

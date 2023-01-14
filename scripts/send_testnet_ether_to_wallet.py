import json
from brownie import accounts

from warren.core.setup_wizard import SetupWizard


# 20 Ether
ETHER_AMOUNT = 20 * 10**18


def main():
    config_path = SetupWizard.default_config_path()
    geth_file = SetupWizard.geth_file_path(config_path)
    with open(geth_file, "r") as f:
        account = accounts[0]
        data = json.load(f)
        account.transfer(data["address"], ETHER_AMOUNT)

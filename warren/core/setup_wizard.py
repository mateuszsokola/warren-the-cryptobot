import json
import os

from eth_account.signers.local import LocalAccount
from typing import List
from web3 import Web3, HTTPProvider

from warren.core.database import Database
from warren.models.option import OptionDto
from warren.utils.home_dir import home_dir


default_project_dir = ".warren-the-cryptobot"


class SetupWizard:
    @staticmethod
    def default_config_path():
        default_name = f"{home_dir()}/{default_project_dir}"

        return default_name

    @staticmethod
    def verify_ethereum_api(eth_api_url: str):
        try:
            web3 = Web3(HTTPProvider(eth_api_url))
            web3.eth.get_block("latest")
            return True
        except:
            return False

    @staticmethod
    def generate_new_wallet(eth_api_url: str, passphrase: str = "") -> str:
        web3 = Web3(HTTPProvider(eth_api_url))
        account_file: LocalAccount = web3.eth.account.create()

        return account_file.encrypt(passphrase)

    @staticmethod
    def create_geth_file_in_config_dir(
        encrypted_wallet: str, config_path: str, file_name: str = "geth_account"
    ):
        SetupWizard.create_config_dir_if_needed(config_path)

        geth_account_path = f"{config_path}/{file_name}"
        with open(geth_account_path, "w") as account_file:
            account_file.write(json.dumps(encrypted_wallet))

    @staticmethod
    def create_database_in_config_dir(
        option_list: List[OptionDto], config_path: str, file_name: str = "database.dat"
    ):
        SetupWizard.create_config_dir_if_needed(config_path)

        database_file = f"{config_path}/{file_name}"
        database = Database(database_file=database_file)

        for option in option_list:
            database.create_option(option=option)

    @staticmethod
    def create_config_dir_if_needed(config_path: str):
        if os.path.exists(config_path) == False:
            os.mkdir(config_path, 0o700)

    @staticmethod
    def verify_config_path(config_path: str):
        if os.path.exists(config_path) == False:
            return False

        return True

    @staticmethod
    def geth_file_path(config_path: str, file_name: str = "geth_account"):
        geth_file = f"{config_path}/{file_name}"
        if os.path.exists(geth_file) == False:
            return None

        return geth_file

    @staticmethod
    def database_file_path(config_path: str, file_name: str = "database.dat"):
        database_file = f"{config_path}/{file_name}"
        if os.path.exists(database_file) == False:
            return None

        return database_file

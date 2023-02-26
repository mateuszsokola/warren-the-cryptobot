from typing import Dict
from warren.core.database import Database
from warren.models.option import OptionDto
from warren.models.option_name import OptionName


class ConfigManager:
    options: Dict[OptionName, str] = {}

    def __init__(self, database: Database):
        self.database = database
        self._load_options()

    def set_option(self, option: OptionDto):
        self.database.insert_or_replace_option(option)

    def _load_options(self):
        for option in self.database.list_options():
            self.options[option.option_name] = option.option_value

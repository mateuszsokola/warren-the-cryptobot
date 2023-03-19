from web3 import Web3

# from warren.core.database import Database
# from warren.managers.config_manager import ConfigManager
from oracle.models.base_model import BaseModel


class Service(BaseModel):
    async_web3: Web3
    web3: Web3
    # config: ConfigManager
    # database: Database

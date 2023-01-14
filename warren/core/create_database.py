from warren.core.database import Database
from warren.core.setup_wizard import SetupWizard


def create_database(config_path: str) -> Database:
    database_file = SetupWizard.database_file_path(config_path)
    database = Database(database_file=database_file)

    return database
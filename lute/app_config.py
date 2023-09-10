"""
App configuration.
"""

import os
import yaml

class AppConfig:
    """
    Configuration wrapper around yaml file.
    """

    def __init__(self, config_file_path):
        """
        Load the required configuration file.
        """
        self.config = self.__load_config(config_file_path)

    def __load_config(self, config_file_path):
        """
        Load and validate the config file.
        """
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"Config file not found at {config_file_path}")

        with open(config_file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

        if not isinstance(config, dict):
            raise ValueError("Invalid configuration format. Expected a dictionary.")

        if 'DBNAME' not in config:
            raise ValueError("Config file must have 'DBNAME'")

        return config

    @property
    def datapath(self):
        """
        Path to user data / app data.  If not present in the
        dictionary, falls back to platformdirs user_data_dir.
        """
        return self.config.get('DATAPATH', 'default')

    @property
    def dbname(self):
        """Database name."""
        return self.config.get('DBNAME')

    @property
    def sqliteconn(self):
        """sqlite connection string."""
        return f'sqlite:///{self.dbname}'

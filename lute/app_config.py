"""
App configuration.
"""

import os
import yaml
from platformdirs import PlatformDirs

class AppConfig:
    """
    Configuration wrapper around yaml file.
    """

    def __init__(self, config_file_path):
        """
        Load the required configuration file.
        """
        self.__load_config(config_file_path)


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

        self.__db_name = config.get('DBNAME')
        self.__data_path = config.get('DATAPATH', None)
        if self.__data_path is None:
            self.__data_path = self.__get_appdata_dir()

        return config


    def __get_appdata_dir(self):
        "Get user's appdata directory from platformdirs."
        dirs = PlatformDirs("Lute3", "Lute3")
        return dirs.user_data_dir


    @property
    def datapath(self):
        """
        Path to user data / app data.  If not present in the
        dictionary, falls back to platformdirs user_data_dir.
        """
        return self.__data_path


    @property
    def dbname(self):
        "Database name."
        return self.__db_name


    @property
    def sqliteconn(self):
        "Full sqlite connection string."
        fullpath = os.path.join(self.datapath, self.dbname)
        return f'sqlite:///{fullpath}'

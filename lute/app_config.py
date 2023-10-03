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
        self._load_config(config_file_path)


    def _load_config(self, config_file_path):
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

        if 'ENV' not in config:
            raise ValueError("Config file must have 'ENV'")

        env = config.get('ENV')
        if env not in [ 'prod', 'dev']:
            raise ValueError(f"Invalid ENV {env}, can only be prod or dev.")
        self._env = env

        self._db_name = config.get('DBNAME')
        self._data_path = config.get('DATAPATH', None)
        if self._data_path is None:
            self._data_path = self._get_appdata_dir()

        return config


    def _get_appdata_dir(self):
        "Get user's appdata directory from platformdirs."
        dirs = PlatformDirs("Lute3", "Lute3")
        return dirs.user_data_dir


    @property
    def env(self):
        "App environment (dev or prod)."
        return self._env


    @property
    def datapath(self):
        """
        Path to user data / app data.  If not present in the
        dictionary, falls back to platformdirs user_data_dir.
        """
        return self._data_path


    @property
    def dbname(self):
        "Database name."
        return self._db_name


    @property
    def dbfilename(self):
        "Full database file name and path."
        return os.path.join(self.datapath, self.dbname)


    @property
    def sqliteconnstring(self):
        "Full sqlite connection string."
        return f'sqlite:///{self.dbfilename}'

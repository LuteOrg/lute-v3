"""
App config tests
"""

import pytest
import yaml

from lute.app_config import AppConfig


def test_valid_config(tmp_path):
    config_file = tmp_path / 'valid_config.yaml'
    config_data = {'DBNAME': 'my_db', 'DATAPATH': 'data_path'}
    
    with open(config_file, 'w') as file:
        yaml.dump(config_data, file)

    app_config = AppConfig(config_file)
    assert app_config.datapath == 'data_path'
    assert app_config.sqliteconn == 'sqlite:///data_path/my_db'


def test_missing_dbname_throws(tmp_path):
    config_file = tmp_path / 'missing_dbname.yaml'
    config_data = {'DATAPATH': 'data_path'}

    with open(config_file, 'w') as file:
        yaml.dump(config_data, file)

    with pytest.raises(ValueError, match="Config file must have 'DBNAME'"):
        AppConfig(config_file)


def test_system_specific_datapath_returned_if_DATAPATH_not_specified(tmp_path):
    config_file = tmp_path / 'default_datapath.yaml'
    config_data = {'DBNAME': 'my_db'}

    with open(config_file, 'w') as file:
        yaml.dump(config_data, file)

    app_config = AppConfig(config_file)

    # Can't test the exact path returned, it will vary by system.
    # Could monkeypatch/dependency inject, but too much hassle.
    assert 'Lute3' in app_config.datapath


def test_invalid_yaml_throws(tmp_path):
    config_file = tmp_path / 'invalid_yaml.yaml'
    with open(config_file, 'w') as file:
        file.write("invalid_yaml")

    with pytest.raises(ValueError, match="Invalid configuration format. Expected a dictionary."):
        AppConfig(config_file)


def test_nonexistent_config_file_throws(tmp_path):
    config_file = tmp_path / 'nonexistent_config.yaml'
    
    with pytest.raises(FileNotFoundError, match=f"Config file not found at {config_file}"):
        AppConfig(config_file)

"""
App config tests
"""

import pytest
import yaml

from lute.config.app_config import AppConfig


def write_file(config_file, config_data):
    "Write config file."
    if "ENV" not in config_data:
        config_data["ENV"] = "dev"
    with open(config_file, "w", encoding="utf-8") as file:
        yaml.dump(config_data, file)


def test_valid_config(tmp_path):
    "Valid path and config is ok."
    config_file = tmp_path / "valid_config.yaml"
    config_data = {"DBNAME": "my_db", "DATAPATH": "data_path"}
    write_file(config_file, config_data)

    app_config = AppConfig(config_file)
    assert app_config.datapath == "data_path"
    assert app_config.sqliteconnstring == "sqlite:///data_path/my_db"
    assert app_config.env == "dev"


def test_ENV_required(tmp_path):
    "Throws otherwise."
    config_file = tmp_path / "valid_config.yaml"
    config_data = {"DBNAME": "my_db", "DATAPATH": "data_path"}
    with open(config_file, "w", encoding="utf-8") as file:
        yaml.dump(config_data, file)
    with pytest.raises(ValueError, match="ENV must be prod or dev, was None."):
        AppConfig(config_file)


def test_missing_dbname_throws(tmp_path):
    """
    File must contain DBNAME.  Testing/dev environment will have
    test_lute.db, prod will have an actual filename.
    """
    config_file = tmp_path / "missing_dbname.yaml"
    config_data = {"DATAPATH": "data_path"}
    write_file(config_file, config_data)

    with pytest.raises(ValueError, match="Config file must have 'DBNAME'"):
        AppConfig(config_file)


def test_system_specific_datapath_returned_if_DATAPATH_not_specified(tmp_path):
    """
    Using library to get platform-specific paths.  Tests will
    hardcode the appropriate system path.
    """
    config_file = tmp_path / "default_datapath.yaml"
    config_data = {"DBNAME": "my_db"}
    write_file(config_file, config_data)

    app_config = AppConfig(config_file)

    # Can't test the exact path returned, it will vary by system.
    # Could monkeypatch/dependency inject, but too much hassle.
    assert "Lute3" in app_config.datapath


def test_env_can_only_be_prod_or_dev(tmp_path):
    """
    Throws error if not prod or dev.
    """
    config_file = tmp_path / "default_datapath.yaml"
    config_data = {"DBNAME": "my_db", "ENV": "blah"}
    write_file(config_file, config_data)

    with pytest.raises(ValueError, match="ENV must be prod or dev, was blah."):
        AppConfig(config_file)


def test_invalid_yaml_throws(tmp_path):
    "File must be valid."
    config_file = tmp_path / "invalid_yaml.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        f.write("bad_data")

    with pytest.raises(Exception):
        AppConfig(config_file)


def test_nonexistent_config_file_throws(tmp_path):
    """
    File must exist!  During packaging, a file will be generated
    in the config folder.
    """
    config_file = tmp_path / "nonexistent_config.yaml"
    with pytest.raises(FileNotFoundError, match="No such file"):
        AppConfig(config_file)

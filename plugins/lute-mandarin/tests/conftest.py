"""
Common fixtures used by many tests.
"""

import os
import yaml
import pytest


from lute.parse.registry import init_parser_plugins

from lute.models.language import Language


def pytest_sessionstart(session):  # pylint: disable=unused-argument
    """
    Initialize parser list
    """
    init_parser_plugins()


def _get_test_language():
    """
    Retrieve the language definition file for testing ths plugin from definition.yaml
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    definition_file = os.path.join(thisdir, "..", "definition.yaml")
    with open(definition_file, "r", encoding="utf-8") as df:
        d = yaml.safe_load(df)
    lang = Language.from_dict(d)
    return lang


@pytest.fixture(name="mandarin_chinese")
def fixture_mandarin_chinese():
    return _get_test_language()

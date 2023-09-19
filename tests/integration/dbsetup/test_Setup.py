"""
DB setup tests using fake baseline, migration files.
"""

from lute.dbsetup.setup import Setup

def test_happy_path_no_existing_database():
    """
    If no db exists, setup should:
    - create the db using the baseline
    - run any migrations
    - no backup created
    """

    assert 1 == 2

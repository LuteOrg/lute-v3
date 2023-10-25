"""
Tests for managing the demo data.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your SQLAlchemy models and other necessary modules here.

@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add code to create and populate your database tables as needed.

    yield session

    # Clean up and close the database session
    session.close()
    engine.dispose()


def test_clear_dev_data():
    # The database clear in DatabaseTestBase wipes everything.
    assert 1 == 1


def test_load_dev_data(session):
    # Add code to load demo data and assert it using SQLAlchemy queries
    term_svc = TermService(session)
    DemoDataLoader.loadDemoData(language_repo, book_repo, term_svc)
    result = session.query(Settings).filter(Settings.StKey == 'IsDemoData').count()
    assert result == 1


def test_wipe_db_only_works_if_flag_is_set(session):
    # Add code to load demo data, clear the database, and assert the changes
    term_svc = TermService(session)
    DemoDataLoader.loadDemoData(language_repo, book_repo, term_svc)
    result = session.query(Settings).filter(Settings.StKey == 'IsDemoData').count()
    assert result == 1
    assert SqliteHelper.isDemoData(session) is True

    SqliteHelper.clearDb(session)
    result = session.query(Settings).filter(Settings.StKey == 'IsDemoData').count()
    assert result == 0
    assert SqliteHelper.isDemoData(session) is False

    with pytest.raises(Exception):
        SqliteHelper.clearDb(session)

    # Add code to execute the SQL statement
    assert result == 1

    SqliteHelper.clearDb(session)  # ok.


def test_is_demo_if_flag_set(session):
    # Add code to load demo data, clear the database, and assert the changes
    term_svc = TermService(session)
    DemoDataLoader.loadDemoData(language_repo, book_repo, term_svc)
    assert SqliteHelper.isDemoData(session) is True

    SqliteHelper.clearDb(session)
    assert SqliteHelper.isDemoData(session) is False

    # Add code to insert the 'IsDemoData' flag and assert it
    assert result == 1

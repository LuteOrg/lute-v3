"""
Tests for managing the demo data.
"""

from lute.db import db
from lute.db.demo import contains_demo_data, remove_flag


def test_new_db_is_demo(app_context):
    "New db created from the baseline has the demo flag set."
    assert contains_demo_data() is True, 'new db contains demo.'


def test_removing_flag_means_not_demo(app_context):
    "Unsetting the flag means the db is not a demo."
    remove_flag()
    assert contains_demo_data() is False, 'not a demo.'

### def test_wipe_db_only_works_if_flag_is_set(session):
###     # Add code to load demo data, clear the database, and assert the changes
###     term_svc = TermService(session)
###     DemoDataLoader.loadDemoData(language_repo, book_repo, term_svc)
###     result = session.query(Settings).filter(Settings.StKey == 'IsDemoData').count()
###     assert result == 1
###     assert SqliteHelper.isDemoData(session) is True
### 
###     SqliteHelper.clearDb(session)
###     result = session.query(Settings).filter(Settings.StKey == 'IsDemoData').count()
###     assert result == 0
###     assert SqliteHelper.isDemoData(session) is False
### 
###     with pytest.raises(Exception):
###         SqliteHelper.clearDb(session)
### 
###     # Add code to execute the SQL statement
###     assert result == 1
### 
###     SqliteHelper.clearDb(session)  # ok.
### 
### 
### def test_is_demo_if_flag_set(session):
###     # Add code to load demo data, clear the database, and assert the changes
###     term_svc = TermService(session)
###     DemoDataLoader.loadDemoData(language_repo, book_repo, term_svc)
###     assert SqliteHelper.isDemoData(session) is True
### 
###     SqliteHelper.clearDb(session)
###     assert SqliteHelper.isDemoData(session) is False
### 
###     # Add code to insert the 'IsDemoData' flag and assert it
###     assert result == 1


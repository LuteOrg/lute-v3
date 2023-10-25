"""
Functions to manage demo database.

Lute db comes pre-loaded with some demo data.  User can view Tutorial,
wipe data, etc.

The db settings table contains a record, StKey = 'IsDemoData', if the
data is demo.
"""

def contains_demo_data():
    return True

def remove_flag():
    pass

def delete_all_data():
    pass

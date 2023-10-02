"""
Language model tests - getting, saving, etc.

Low value but ensure that the db mapping is correct.
"""

def test_demo_has_preloaded_languages(_demo_db):
    """
    When users get the initial demo, it has English, French, etc,
    pre-defined.
    """
    a = 1
    assert a == 2, 'todo'

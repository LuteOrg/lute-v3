"""
Dummy tests to ensure imports etc work.
"""

from lute.startspike.spike import SimpleTest

def test_add():
    """
    Dummy test.
    """
    simpletest = SimpleTest()
    print('hello there')
    assert simpletest.add(2, 3) == 5

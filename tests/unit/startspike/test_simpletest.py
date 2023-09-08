"""
Dummy tests to ensure imports etc work.
"""

import pytest
from lute.startspike.spike import SimpleTest

# from lute.zztestbootstrap import SimpleTest

def test_add():
    """
    Dummy test.
    """
    simpletest = SimpleTest()
    print('hello there')
    assert simpletest.add(2, 3) == 5

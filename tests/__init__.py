"""
Register pytest to get assert rewrites.
"""

import pytest

pytest.register_assert_rewrite("tests.dbasserts")

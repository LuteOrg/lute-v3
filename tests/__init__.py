"""
Register pytest to get assert rewrites.
"""

import pytest

pytest.register_assert_rewrite("tests.dbasserts")
pytest.register_assert_rewrite("tests.utils")

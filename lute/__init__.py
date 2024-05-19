"""
Version info.

Lute follows the version numbers at
https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers

e.g.

3.0.0a1.dev1
3.0.0a1
3.0.0b1
3.0.0

The version needs to be included in Lute itself, because Lute displays
it in the application version screen.

Flit pulls into the pyproject.toml using "dynamic".
"""

__version__ = "3.4.1"

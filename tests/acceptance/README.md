# Web tests with pytest-splinter

Ref https://pytest-splinter.readthedocs.io/en/3.3.2/#example

## How to run the tests

From root:

`inv accept`

This starts the test server and then runs the tests in a subproc.

## Ignored by default

The tests/acceptance/ folder is _ignored_ in the .pytest.ini,
because these tests a) are slow, and b) require a running Lute
server.

Ignoring lets us run `pytest` and have all of the fast things
executed.
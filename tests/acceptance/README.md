# Web tests with playwright

Ref https://playwright.dev/python/docs/intro

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
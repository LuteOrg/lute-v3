Feature files and step definitions.  Using pytest-bdd for execution.

ref https://pytest-bdd.readthedocs.io/en/latest/

These are run with the regular `inv test` call from root dir.

Can filter the test by "python-snake-ifying" the scenario name, eg Scenario "No period at end of text" becomes:

```
tests/features/test_rendering.py::test_no_period_at_end_of_text
```

So filter with:

```
inv test -a "-k test_no_period_at_end_of_text"
```

See the test names with eg

```
pytest -vv -k tests/features/test_rendering.py

...
tests/features/test_rendering.py::test_smoke_test <- ... PASSED ...
...
tests/features/test_rendering.py::test_no_period_at_end_of_text <- ...
...
```
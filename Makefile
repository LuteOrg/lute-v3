# Makefile for Python tasks.

# Run tests only.  export some ARGS before using if you want to filter tests.
test:
	python -m pytest tests/ $(ARGS)

# Test all (no args) and lint
testall: lint
	python -m pytest tests/

# Run tests and show print() messages
testprint:
	python -m pytest -s tests/ $(ARGS)

# Generate test coverage report, excluding the tests from the report
coverage:
	coverage run -m pytest tests/
	coverage report --omit="*/test*"

# Coverage with html report to see missing lines.
coveragehtml:
	coverage html --omit="*/test*"
	open htmlcov/index.html

lint:
	pylint lute/ tests/

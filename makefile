.PHONY: everything commit test test-nocov format format-check lint

everything: commit test lint

commit:
	pre-commit run --all-files

test:
	pytest --cov=krnl_helper --cov-report=term-missing

test-nocov:
	pytest

format:
	pycln .
	isort .
	black .

format-check:
	pycln --check .
	isort --check .
	black --check .

lint:
	pylint krnl_helper
	mypy krnl_helper

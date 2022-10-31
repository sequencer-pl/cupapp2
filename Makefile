.PHONY: install
install:
	poetry install

.PHONY: tests
tests:
	poetry run cupapp2/manage.py test cupapp2/tests/


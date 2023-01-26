pc:
	poetry run pre-commit run -a

mypy:
	poetry run mypy pymage_size/

install:
	poetry install
	poetry run pre-commit install

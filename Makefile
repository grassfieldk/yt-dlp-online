.PHONY: dev run install format check

install:
	pip install -r requirements.txt

dev:
	.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run:
	.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

format:
	.venv/bin/ruff format .

check:
	.venv/bin/ruff check --fix .

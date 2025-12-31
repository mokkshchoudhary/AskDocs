.PHONY: dev worker test lint setup up down

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	celery -A app.workers.celery_app worker --loglevel=info

test:
	pytest -v

lint:
	ruff check .
	black --check .

setup:
	pip install -e .[dev]

up:
	docker-compose up -d

down:
	docker-compose down

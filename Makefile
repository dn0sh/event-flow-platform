up:
	docker compose --env-file .env -f docker/docker-compose.yml up -d --build

down:
	docker compose --env-file .env -f docker/docker-compose.yml down

logs:
	docker compose --env-file .env -f docker/docker-compose.yml logs -f --tail=200

test:
	pytest

test-cov:
	pytest --cov=src --cov-report=term-missing --cov-fail-under=85

lint:
	black --check .
	isort --check-only .
	flake8 src tests
	mypy src

format:
	black .
	isort .

migrate:
	python scripts/migrate.py

seed:
	python scripts/seed_data.py

load-test:
	locust -f scripts/load_test.py

benchmark:
	python scripts/benchmark.py

docs:
	@echo "Docs are in ./docs"

version-bump:
	@echo "Use semantic versioning MAJOR.MINOR.PATCH"

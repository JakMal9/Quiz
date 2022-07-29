.DEFAULT_GOAL:=help

help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

build: ## Build docker environment
	docker-compose build

start: ## Start the environment in the background
	docker-compose up -d

logs: ## Display logs from containers
	docker-compose logs --tail 100 -f

stop: ## Stop the environment
	docker-compose stop

bash: ## Go to the backend container
	docker-compose exec quiz_app bash

psql: ## Go to the db and make SQL queries
	docker-compose exec db psql -U quiz_app

rebuild: ## Rebuild docker images
	docker-compose rm --force
	docker-compose build --no-cache

test: ## Run unittests
	docker-compose exec quiz_app pytest

black: ## Run black
	docker-compose exec quiz_app black .

sort-imports: ## Run isort
	docker-compose exec quiz_app isort .

black-check: ## Check black
	docker-compose exec quiz_app black --check .

migration: ## Create migrations
	docker-compose exec quiz_app  python manage.py makemigrations

migrate: ## Migrate
	docker-compose exec quiz_app  python manage.py migrate

populate-database: ## Populate database with fake data
	docker-compose exec quiz_app  python manage.py populate_database

.DEFAULT_GOAL := help

# if target is "logs", extract anything after that as command line args, not targets
ifeq (logs,$(firstword $(MAKECMDGOALS)))
  # grab words after the first two (make logs)
  LOGS_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # and turn them into do-nothing targets so Make does not try to use them
  $(eval $(LOGS_ARGS):;@:)
endif

DOCKERFILE=docker/mercury-core-local/Dockerfile
IMAGE_NAME=local/mercury-core
COMPOSE_FILE=docker/docker-compose-fullstack.yaml
PROJECT_NAME=mercury

DC_FLAGS=-f $(COMPOSE_FILE) -p $(PROJECT_NAME)
MERCURY_SERVICES=mercury-backend-queue mercury-backend-worker mercury-backend mercury-inventory mercury-log mercury-rpc

build: ## Build mercury-core-local image
	docker build -t $(IMAGE_NAME) -f $(DOCKERFILE) .

up:  ## Up all services
	docker-compose $(DC_FLAGS) up -d

down: ## Down all services (including Mongo and Redis)
	docker-compose $(DC_FLAGS) down

kill-mercury: ## Kills mercury services only (not Mongo or Redis)
	docker-compose $(DC_FLAGS) kill $(MERCURY_SERVICES)

logs: ## Logs: All or specify one or more specific services to tail (ex: make logs mongodb mercury-inventory)
	docker-compose $(DC_FLAGS) logs -f $(LOGS_ARGS)

logs-backend: ## Logs: Tails mercury-backend service only
	docker-compose $(DC_FLAGS) logs -f mercury-backend

logs-mercury: ## Logs: Tails all mercury services
	docker-compose $(DC_FLAGS) logs -f $(MERCURY_SERVICES)

ps: ## docker-compose ps
	docker-compose $(DC_FLAGS) ps

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) |  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

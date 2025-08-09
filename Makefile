# MCP Pokemon Server Makefile
# Provides convenient commands for managing the Docker-based development environment

# Colors for output
RED    := \033[0;31m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
NC     := \033[0m

# Default target
.DEFAULT_GOAL := help

# Check if Docker is running
.PHONY: check-docker
check-docker:
	@if ! docker info > /dev/null 2>&1; then \
		printf "$(RED)[ERROR]$(NC) Docker is not running. Please start Docker and try again.\n"; \
		exit 1; \
	fi

# Build targets
.PHONY: build-prod
build-prod: check-docker ## Build production Docker image
	@printf "$(BLUE)[INFO]$(NC) Building production Docker image...\n"
	@docker build -t mcp-pokemon-server:latest .
	@printf "$(GREEN)[SUCCESS]$(NC) Production image built successfully!\n"

.PHONY: build-dev
build-dev: check-docker ## Build development Docker image
	@printf "$(BLUE)[INFO]$(NC) Building development Docker image...\n"
	@docker build -f Dockerfile.dev -t mcp-pokemon-server:dev .
	@printf "$(GREEN)[SUCCESS]$(NC) Development image built successfully!\n"

.PHONY: build
build: build-dev ## Build development image (default build target)

# Run targets
.PHONY: run-prod
run-prod: check-docker ## Start production container
	@printf "$(BLUE)[INFO]$(NC) Starting production container...\n"
	@docker-compose up -d
	@printf "$(GREEN)[SUCCESS]$(NC) Production container started!\n"
	@printf "$(BLUE)[INFO]$(NC) Server should be available at http://localhost:8000\n"

.PHONY: run-dev
run-dev: check-docker ## Start development container
	@printf "$(BLUE)[INFO]$(NC) Starting development container...\n"
	@docker-compose -f docker-compose.dev.yml up

.PHONY: run
run: run-dev ## Start development container (default run target)

.PHONY: up
up: run-dev ## Alias for run-dev

# Stop targets
.PHONY: stop
stop: check-docker ## Stop all containers
	@printf "$(BLUE)[INFO]$(NC) Stopping containers...\n"
	@docker-compose down || true
	@docker-compose -f docker-compose.dev.yml down || true
	@printf "$(GREEN)[SUCCESS]$(NC) Containers stopped!\n"

.PHONY: down
down: stop ## Alias for stop

# Log targets
.PHONY: logs
logs: check-docker ## Show production logs
	@printf "$(BLUE)[INFO]$(NC) Showing production logs...\n"
	@docker-compose logs -f

.PHONY: logs-dev
logs-dev: check-docker ## Show development logs
	@printf "$(BLUE)[INFO]$(NC) Showing development logs...\n"
	@docker-compose -f docker-compose.dev.yml logs -f

# Test targets
.PHONY: test
test: check-docker ## Run tests in development container
	@printf "$(BLUE)[INFO]$(NC) Running tests in development container...\n"
	@docker-compose -f docker-compose.dev.yml exec mcp-pokemon-server-dev pytest

.PHONY: test-local
test-local: ## Run tests locally (without Docker)
	@printf "$(BLUE)[INFO]$(NC) Running tests locally...\n"
	@python -m pytest tests/

# Code quality targets
.PHONY: lint
lint: check-docker ## Run ruff linter checks
	@printf "$(BLUE)[INFO]$(NC) Running ruff linter checks...\n"
	@docker run --rm -v "$(PWD)":/app -w /app mcp-pokemon-server:dev ruff check .

.PHONY: lint-fix
lint-fix: check-docker ## Run ruff linter and fix auto-fixable issues
	@printf "$(BLUE)[INFO]$(NC) Running ruff linter with auto-fix...\n"
	@docker run --rm -v "$(PWD)":/app -w /app mcp-pokemon-server:dev ruff check . --fix

.PHONY: format
format: check-docker ## Format code with ruff
	@printf "$(BLUE)[INFO]$(NC) Formatting code with ruff...\n"
	@docker run --rm -v "$(PWD)":/app -w /app mcp-pokemon-server:dev ruff format .

.PHONY: format-check
format-check: check-docker ## Check code formatting without making changes
	@printf "$(BLUE)[INFO]$(NC) Checking code formatting...\n"
	@docker run --rm -v "$(PWD)":/app -w /app mcp-pokemon-server:dev ruff format . --check

.PHONY: type-check
type-check: check-docker ## Run mypy type checking
	@printf "$(BLUE)[INFO]$(NC) Running mypy type checking...\n"
	@docker run --rm -v "$(PWD)":/app -w /app mcp-pokemon-server:dev mypy src/

.PHONY: quality
quality: lint type-check ## Run all code quality checks (lint + type check)
	@printf "$(GREEN)[SUCCESS]$(NC) All code quality checks completed!\n"

.PHONY: quality-fix
quality-fix: lint-fix format ## Fix linting issues and format code
	@printf "$(GREEN)[SUCCESS]$(NC) Code quality fixes applied!\n"

# Shell targets
.PHONY: shell
shell: check-docker ## Open shell in production container
	@printf "$(BLUE)[INFO]$(NC) Opening shell in production container...\n"
	@docker-compose exec mcp-pokemon-server /bin/bash

.PHONY: shell-dev
shell-dev: check-docker ## Open shell in development container
	@printf "$(BLUE)[INFO]$(NC) Opening shell in development container...\n"
	@docker-compose -f docker-compose.dev.yml exec mcp-pokemon-server-dev /bin/bash

# Status and monitoring
.PHONY: status
status: check-docker ## Show container status
	@printf "$(BLUE)[INFO]$(NC) Container status:\n"
	@docker-compose ps
	@echo
	@printf "$(BLUE)[INFO]$(NC) Development container status:\n"
	@docker-compose -f docker-compose.dev.yml ps

.PHONY: ps
ps: status ## Alias for status

# Cleanup targets
.PHONY: cleanup
cleanup: check-docker ## Clean up Docker resources (interactive)
	@printf "$(YELLOW)[WARNING]$(NC) This will remove all stopped containers, unused networks, and dangling images.\n"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ] || (echo "Cleanup cancelled." && exit 1)
	@printf "$(BLUE)[INFO]$(NC) Cleaning up Docker resources...\n"
	@docker system prune -f
	@printf "$(GREEN)[SUCCESS]$(NC) Cleanup completed!\n"

.PHONY: clean
clean: stop ## Stop containers and clean up
	@printf "$(BLUE)[INFO]$(NC) Cleaning up containers and images...\n"
	@docker-compose down --rmi local --volumes --remove-orphans || true
	@docker-compose -f docker-compose.dev.yml down --rmi local --volumes --remove-orphans || true
	@printf "$(GREEN)[SUCCESS]$(NC) Cleanup completed!\n"

# Development workflow targets
.PHONY: dev
dev: build-dev run-dev ## Build and run development environment

.PHONY: prod
prod: build-prod run-prod ## Build and run production environment

.PHONY: restart
restart: stop run-dev ## Restart development container

.PHONY: restart-prod
restart-prod: stop run-prod ## Restart production container

# Health check
.PHONY: health
health: ## Check if the server is responding
	@printf "$(BLUE)[INFO]$(NC) Checking server health...\n"
	@curl -f http://localhost:8000/mcp || printf "$(RED)[ERROR]$(NC) Server is not responding\n"

# Install dependencies locally
.PHONY: install
install: ## Install Python dependencies locally
	@printf "$(BLUE)[INFO]$(NC) Installing Python dependencies...\n"
	@pip install -e .
	@printf "$(GREEN)[SUCCESS]$(NC) Dependencies installed!\n"

.PHONY: install-dev
install-dev: ## Install development dependencies locally
	@printf "$(BLUE)[INFO]$(NC) Installing development dependencies...\n"
	@pip install -e ".[dev]"
	@printf "$(GREEN)[SUCCESS]$(NC) Development dependencies installed!\n"

# Help target
.PHONY: help
help: ## Show this help message
	@echo "MCP Pokemon Server - Development Commands"
	@echo ""
	@echo "Usage: make [TARGET]"
	@echo ""
	@echo "Build Commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /Build/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Run Commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /Start|run|up/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Stop Commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /Stop|stop|down/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Development Commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /test|shell|dev|install/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Code Quality Commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /lint|format|type-check|quality/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Monitoring Commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /logs|status|health/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Cleanup Commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /clean|Clean/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Workflow Commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && /restart|Build and run|environment/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Examples:"
	@printf "  $(BLUE)make dev$(NC)              # Build and run development environment\n"
	@printf "  $(BLUE)make logs-dev$(NC)         # Show development logs\n"
	@printf "  $(BLUE)make test$(NC)             # Run tests in container\n"
	@printf "  $(BLUE)make shell-dev$(NC)        # Open shell in dev container\n"
	@printf "  $(BLUE)make restart$(NC)          # Restart development environment\n"
	@printf "  $(BLUE)make clean$(NC)            # Stop and clean everything\n"
	@printf "  $(BLUE)make lint$(NC)             # Check code with ruff linter\n"
	@printf "  $(BLUE)make lint-fix$(NC)         # Fix auto-fixable linting issues\n"
	@printf "  $(BLUE)make format$(NC)           # Format code with ruff\n"
	@printf "  $(BLUE)make quality$(NC)          # Run all code quality checks\n"

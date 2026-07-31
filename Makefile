.DEFAULT_GOAL := help

UV := uv run

.PHONY: help install install-pipeline format lint typecheck test test-fast check build clean

help: ## Muestra comandos disponibles
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instala paquete y herramientas de desarrollo
	uv sync --extra dev

install-pipeline: ## Instala desarrollo y Cutadapt para procesar FASTQ
	uv sync --extra dev --extra preprocess

format: ## Formatea código Python
	$(UV) ruff format src tests

lint: ## Ejecuta linter sin modificar archivos
	$(UV) ruff check src tests

typecheck: ## Ejecuta type checker
	$(UV) ty check src

test: ## Ejecuta tests con cobertura
	$(UV) pytest

test-fast: ## Ejecuta tests sin reporte adicional
	$(UV) pytest -q

check: lint typecheck test ## Ejecuta todas las verificaciones de CI

build: ## Construye wheel y sdist
	uv build

clean: ## Elimina artefactos locales regenerables
	rm -rf .coverage .pytest_cache .ruff_cache .ty .mypy_cache build dist htmlcov
	find src tests -type d -name __pycache__ -prune -exec rm -rf {} +

init:
	@[ -f model_endpoints.yml ] && echo "model_endpoints.yml already exists." || (cp model_endpoints_template.yml model_endpoints.yml && echo "model_endpoints.yml created. Please fill it with your API keys.")
	@[ -f .env ] && echo ".env already exists." || (cp .env.example .env && echo ".env created.")
	@echo "Project initialized."

install:
	uv sync

dev-install:
	uv sync --all-extras

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

fix:
	uv run ruff check --fix .

run-example:
	uv run python examples/math_forge/run.py

jupyter:
	uv run jupyter lab --port=8888 --no-browser

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

update:
	uv lock --upgrade

export-requirements:
	uv export --no-hashes --format requirements-txt --output-file requirements.txt

build:
	docker build -t ebiose .

run:
	docker run -it --env-file .env -v ./model_endpoints.yml:/app/model_endpoints.yml -v ./data:/app/data -v ./examples:/app/examples ebiose

.PHONY: init install dev-install test lint format fix run-example jupyter clean update export-requirements build run

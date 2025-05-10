#!/bin/bash

# Script to run tests and linting in Docker for multiple Python versions
# Supports both docker run and docker compose

set -e

# Log Docker and Docker Compose versions
echo "Docker version: $(docker --version)"
echo "Docker Compose version: $(docker compose version)"

# Python versions to test
PYTHON_VERSIONS=("3.8" "3.9" "3.10")

# Project directory
PROJECT_DIR="$(pwd)"

# Mode selection (docker or compose)
MODE="${1:-docker}"

if [ "$MODE" = "compose" ]; then
    echo "Running tests and linting with docker compose..."

    for PY_VERSION in "${PYTHON_VERSIONS[@]}"; do
        echo "Testing with Python ${PY_VERSION}..."

        # Run tests
        echo "Running pytest..."
        docker compose run --rm test-py${PY_VERSION//./}

        # Run flake8
        echo "Running flake8..."
        docker compose run --rm test-py${PY_VERSION//./} \
            flake8 . --max-line-length=120 --extend-exclude=.venv,.git

        # Run isort
        echo "Running isort..."
        docker compose run --rm test-py${PY_VERSION//./} \
            isort --check-only --diff --profile=black --line-length=120 .

        # Run black
        echo "Running black..."
        docker compose run --rm test-py${PY_VERSION//./} \
            black --check --diff --line-length=120 .

        echo "Completed testing with Python ${PY_VERSION}"
    done

    # Clean up compose services
    docker compose down
else
    echo "Running tests and linting with docker run..."

    for PY_VERSION in "${PYTHON_VERSIONS[@]}"; do
        echo "Testing with Python ${PY_VERSION}..."

        # Build Docker image
        docker build --build-arg PYTHON_VERSION=${PY_VERSION} -t flattentool/test:${PY_VERSION} .

        # Run tests
        echo "Running pytest..."
        docker run --rm -v "${PROJECT_DIR}:/app" flattentool/test:${PY_VERSION} \
            pytest tests/test_flatten.py --cov=src/flatten_tool/flatten --cov-report=xml

        # Run flake8
        echo "Running flake8..."
        docker run --rm -v "${PROJECT_DIR}:/app" flattentool/test:${PY_VERSION} \
            flake8 . --max-line-length=120 --extend-exclude=.venv,.git

        # Run isort
        echo "Running isort..."
        docker run --rm -v "${PROJECT_DIR}:/app" flattentool/test:${PY_VERSION} \
            isort --check-only --diff --profile=black --line-length=120 .

        # Run black
        echo "Running black..."
        docker run --rm -v "${PROJECT_DIR}:/app" flattentool/test:${PY_VERSION} \
            black --check --diff --line-length=120 .

        echo "Completed testing with Python ${PY_VERSION}"
    done
fi

echo "All tests and linting completed successfully!"
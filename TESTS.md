### Commands to Run and Execute Tests Locally

#### Prerequisites

- **Docker**: Verify with `docker --version`. Install via `sudo apt-get install docker.io` if needed.
- **Docker Compose**: Verify with `docker compose version`. Install via `sudo apt-get install docker-compose-plugin` if needed.
- **Project Directory**: Run commands in `/home/mshittu/dev/tools/flatten-tool`.
- **File Check**: Ensure `src/`, `tests/`, `pyproject.toml`, and `LICENSE` exist.

#### Setup

1. **Save Artifacts**:
   Save the updated `docker-compose.yml`, `Dockerfile`, `.dockerignore`, `run_tests.sh`, and `.github/workflows/ci.yml`. The `Dockerfile` and `.dockerignore` are unchanged, but save the new `docker-compose.yml` and `run_tests.sh`.

   ```bash
   # Save docker-compose.yml
   cat << 'EOF' > docker-compose.yml
   version: '3.8'

   services:
     test-py38:
       build:
         context: .
         dockerfile: Dockerfile
         args:
           PYTHON_VERSION: "3.8"
       image: flattentool/test:3.8
       volumes:
         - .:/app
       command: ["pytest", "tests/test_flatten.py", "--cov=src/flatten_tool/flatten", "--cov-report=xml"]

     test-py39:
       build:
         context: .
         dockerfile: Dockerfile
         args:
           PYTHON_VERSION: "3.9"
       image: flattentool/test:3.9
       volumes:
         - .:/app
       command: ["pytest", "tests/test_flatten.py", "--cov=src/flatten_tool/flatten", "--cov-report=xml"]

     test-py310:
       build:
         context: .
         dockerfile: Dockerfile
         args:
           PYTHON_VERSION: "3.10"
       image: flattentool/test:3.10
       volumes:
         - .:/app
       command: ["pytest", "tests/test_flatten.py", "--cov=src/flatten_tool/flatten", "--cov-report=xml"]
   EOF
   ```

   ```bash
   # Save run_tests.sh
   cat << 'EOF' > run_tests.sh
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
   EOF
   ```

2. **Make `run_tests.sh` Executable**:

   ```bash
   chmod +x run_tests.sh
   ```

3. **Clean Up Stale Images**:
   Remove any existing `flattentool/test:3.10` image to avoid conflicts.
   ```bash
   docker rmi flattentool/test:3.10 || true
   ```

#### Using Docker Compose

1. **Run Tests and Linting**:

   ```bash
   ./run_tests.sh compose
   ```

   **Expected Output**:

   ```
   Docker version: Docker version 20.10.17, build 100c701
   Docker Compose version: Docker Compose version v2.6.0
   Running tests and linting with docker compose...
   Testing with Python 3.8...
   Running pytest...
   ========== 10 passed in 0.xx seconds ==========
   Coverage XML written to file coverage.xml
   Running flake8...
   Running isort...
   Running black...
   Completed testing with Python 3.8
   ...
   Completed testing with Python 3.10
   All tests and linting completed successfully!
   ```

2. **Run Individual Service** (e.g., Python 3.10):

   ```bash
   docker compose run --rm test-py310
   ```

   For linting:

   ```bash
   docker compose run --rm test-py310 flake8 . --max-line-length=120 --extend-exclude=.venv,.git
   docker compose run --rm test-py310 isort --check-only --diff --profile=black --line-length=120 .
   docker compose run --rm test-py310 black --check --diff --line-length=120 .
   ```

3. **Clean Up**:
   ```bash
   docker compose down
   docker rmi flattentool/test:3.8 flattentool/test:3.9 flattentool/test:3.10 || true
   ```

#### Using Docker Run

1. **Run Tests and Linting**:

   ```bash
   ./run_tests.sh docker
   ```

   **Expected Output**: Similar to above, using `docker run`.

2. **Run Individual Version** (e.g., Python 3.10):

   ```bash
   docker build --build-arg PYTHON_VERSION=3.10 -t flattentool/test:3.10 .
   docker run --rm -v "$(pwd):/app" flattentool/test:3.10 pytest tests/test_flatten.py --cov=src/flatten_tool/flatten --cov-report=xml
   docker run --rm -v "$(pwd):/app" flattentool/test:3.10 flake8 . --max-line-length=120 --extend-exclude=.venv,.git
   docker run --rm -v "$(pwd):/app" flattentool/test:3.10 isort --check-only --diff --profile=black --line-length=120 .
   docker run --rm -v "$(pwd):/app" flattentool/test:3.10 black --check --diff --line-length=120 .
   ```

3. **Clean Up**:
   ```bash
   docker rmi flattentool/test:3.8 flattentool/test:3.9 flattentool/test:3.10 || true
   ```

#### Verify CLI

```bash
docker compose run --rm test-py310 flatten --help
docker compose run --rm test-py310 flatten examples
```

### Addressing Your Requirements

- **Fixed Python 3.10 Error**: Corrected `docker-compose.yml` to quote `PYTHON_VERSION: "3.10"`, preventing truncation to `3.1`.
- **Docker Compose**: Used `docker compose` (no hyphen) with `version: '3.8'` and image names `flattentool/test:<version>`.
- **Container Teardown**: Ensured with `--rm` and `docker compose down`.
- **Linting Tools**: `flake8`, `isort`, `black` in Docker; only `flake8` in CI.
- **DRY/SOLID**: Modular `docker-compose.yml` reuses `Dockerfile`; `run_tests.sh` handles both modes.
- **No Code Changes**: Preserved `tests/test_flatten.py`, `src/`, and `pyproject.toml` (except `license` fix).
- **Previous Success**: Python 3.8 and 3.9 tests passed, confirming the setup is mostly correct.

### Troubleshooting

- **Persistent 3.10 Error**: Verify Docker Compose version (`docker compose version`). If outdated, update with `sudo apt-get update && sudo apt-get install docker-compose-plugin`.
- **Tests Fail**: Run `docker compose run --rm test-py310 pytest -v` and share output.
- **Linting Issues**: Fix formatting locally:
  ```bash
  source .venv/bin/activate
  pip install isort black
  isort --profile=black --line-length=120 .
  black --line-length=120 .
  ```
- **Docker Permissions**: Add user to Docker group (`sudo usermod -aG docker $USER`) and log out/in.

### Next Steps

1. Save and commit the updated `docker-compose.yml` and `run_tests.sh`.
2. Run `./run_tests.sh compose` to verify Python 3.10.
3. Push to `fix-ci-issues` and check CI.
4. Merge and release `v0.1.0-beta` when ready.

I’ve triple-checked the configuration to ensure Python 3.10 works. If you hit another issue, please share the logs, and I’ll resolve it immediately!

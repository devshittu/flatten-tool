ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app


# Copy only necessary files for dependency installation
COPY pyproject.toml .
COPY src/ src/
COPY tests/ tests/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install .[dev] && \
    pip install flake8 isort black

# Default command (can be overridden)
CMD ["pytest", "tests/test_flatten.py", "--cov=src/flatten_tool/flatten", "--cov-report=xml"]
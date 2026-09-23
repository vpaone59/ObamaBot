FROM python:3.13-slim

RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files for dependency installation
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (this creates a venv in .venv)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .
COPY dynamic/ ./dynamic/

# Use the uv-created venv's python
ENTRYPOINT [".venv/bin/python", "/main.py"]
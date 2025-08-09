FROM python:3.12-slim

RUN apt-get update && apt-get install -y sqlite3

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies with uv
RUN uv pip install --system -r requirements.txt

# Copy the rest of the application
COPY . .

EXPOSE 8080

ENTRYPOINT ["python", "main.py"]
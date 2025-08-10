FROM python:3.12-slim

RUN apt-get update && apt-get install -y sqlite3

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies with uv
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

EXPOSE 8080

ENTRYPOINT ["python", "main.py"]
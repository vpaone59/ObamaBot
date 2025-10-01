FROM python:3.12-slim

RUN apt-get update && apt-get install -y sqlite3

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/

ENTRYPOINT ["python", "/app/main.py"]
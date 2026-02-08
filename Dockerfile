FROM python:3.13-slim

RUN apt-get update && apt-get install -y sqlite3

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY dynamic/ ./dynamic/

ENTRYPOINT ["python", "/main.py"]
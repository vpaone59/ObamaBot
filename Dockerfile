FROM python:3.11-slim

RUN apt-get update && apt-get install -y sqlite3

WORKDIR /app

COPY . .

RUN pip3 install --upgrade pip setuptools==70.0.0
RUN pip3 install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["python", "main.py"]
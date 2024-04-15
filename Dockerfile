FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y sqlite3

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
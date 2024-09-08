FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y sqlite3

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

RUN chmod +x entrypoint.sh

# Set the environment variable for the log file path
ENV LOG_FILE_PATH=/app/logs

# Create the directory and set read/write permissions
RUN mkdir -p $LOG_FILE_PATH && chmod 777 $LOG_FILE_PATH

# Expose port 8080 for Cloud Run
EXPOSE 8080

ENTRYPOINT ["./entrypoint.sh"]
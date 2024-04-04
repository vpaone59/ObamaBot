# ObamaBot
ObamaBot - Vincent Paone

A general purpose Discord Bot. Contains Cogs specific to ObamaBot and other special Guilds/Servers.
Migrating to discordpy 2.0 --- https://discordpy.readthedocs.io/en/latest/migrating.html

## Running locally without Docker:
Must have a Discord Bot Token ready. Place Token in the SAMPLE.env file. Rename SAMPLE.env file to ".env" (without quotes).
requires Python3.8 >=

pip install -r requirements.txt
python main.py

## Running with Docker:
I recommend setting up the logging file map in the docker-compose.yml. You can update the left file path with the one on your host system.
    ~\Documents\logs\ObamaBot\bot.log:/logs/bot.log 

Optionally setup the SQLite database path on your host system.
    ~\Documents\DB\obama.db:/app/database/obama.db

### To build the container and then run it
docker build . -t obama-bot
docker run -d obama-bot

### Run with docker-compose.yml
docker compose up --build -d
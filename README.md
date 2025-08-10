# ObamaBot
ObamaBot - by Vincent Paone

A general purpose Discord Bot with some fun interactions. Used as a base to learn Python and have some fun with my friends.

## Important Prerequisite Setup Before Running (DO NOT SKIP)
- You **must** have a Discord Bot Token https://discord.com/developers/applications.

- Requires Python3.11 >=

Setup your environment file with the required variables.
```
cp SAMPLE.env .env
```

Required Environment variables (the bot will not run without these):
- ```DISCORD_TOKEN```: your application's token from https://discord.com/developers/applications
- ```PREFIX```: whatever character or string you want to signify the start of a command. The default is set to ```'!'```. I.e, ```'!ping'```

All other environment variables are optional depending on which extension/Cog you want to use.

## Running locally without Docker
Install requirements and run the bot
```
pip install -r requirements.txt
python main.py
```

You can view logs for the bot in ```ObamaBot/logs/bot.log```

## Running with Docker
I recommend setting up the logging file map in ```docker-compose.yml```. This will bind ```/app/logs``` in the container to the location you choose so you can access the container logs from your host machine.

Optionally, you can map the SQLite database from the container to your host machine for easier access to the database.

In ```docker-compose.yml```:
```
volumes:
    ~\Documents\logs\ObamaBot\bot.log:/app/logs/bot.log
    ~\Documents\database\obamabot.db:/app/database/obamabot.db
```

Build and run the container with docker compose:
```
docker compose up --build -d
```

Optional, build and run in two steps:
```
docker build -t your_container_name .

docker run -e DISCORD_TOKEN= -e PREFIX= -d your_container_name
```
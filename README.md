# ObamaBot
ObamaBot - by Vincent Paone

A general purpose Discord Bot with some fun interactions. Used as a base to learn Python and have some fun with my friends.
Migrating to discordpy 2.0 --- https://discordpy.readthedocs.io/en/latest/migrating.html

## !Important Prerequisite Setup Before Running
Must have a Discord Bot Token https://discord.com/developers/applications.
Requires Python3.8 >=
Setup your environment file with the required variables.
```cp SAMPLE.env .env```

```DISCORD_TOKEN``` and ```PREFIX``` are the only non-optional environment variables that must be added in order for the bot to function. All other environment variables are optional depending on which Cog you want to use.
- DISCORD_TOKEN will be your application's token from https://discord.com/developers/applications
- PREFIX will be whatever character or string you want to signify the start of a command. The default is set to '!'. I.e, '!ping'

## Running locally without Docker
### If you're running Python >= 3.12 you might need to manually install setuptools.
```
pip install setuptools 
```

### Install requirements and run the bot
```
pip install -r requirements.txt
python main.py
```

You can view logs for the bot in ObamaBot/logs/bot.log

## Running with Docker
I recommend setting up the logging file map in ```docker-compose.yml```. This will allow you to easily access the bot's log file from your host machine.
You can update the file path on the lefthand side with the one on your host system. The file path on the right reflects the path to inside the container.
Optionally, you can map the SQLite database from the container to your host machine for easier access to the database.

```
volumes:
    ~\Documents\logs\ObamaBot\bot.log:/app/logs/bot.log
    ~\Documents\database\obamabot.db:/app/database/obamabot.db
```

### Build and then start the container
```
docker build -t your_container_name .

docker run -e DISCORD_TOKEN= -e PREFIX= -d your_container_name
```

## Running with docker compose
```
docker compose up --build -d
```

### Troubleshooting Docker
entrypoint.sh:
    If Docker is complaining about entrypoint.sh like ```python3-obamabot  | exec ./entrypoint.sh: no such file or directory``` then you need to convert entrypoint.sh from CRLF to LF so the script is recognized on the linux system.

## To push to a Google Artifacts Repository
Download and install Google Cloud CLI and Docker

```
docker tag {image_name} {repo_url/{image_name:{tag}}}

docker push {repo_url/{image_name:{tag}}}
```
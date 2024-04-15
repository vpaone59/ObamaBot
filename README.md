# ObamaBot
ObamaBot - Vincent Paone

A general purpose Discord Bot. Contains Cogs specific to ObamaBot and other special Guilds/Servers.
Migrating to discordpy 2.0 --- https://discordpy.readthedocs.io/en/latest/migrating.html

## Running locally without Docker:
Must have a Discord Bot Token ready. Place Token in the SAMPLE.env file. Rename SAMPLE.env file to ".env" (without quotes).
requires Python3.8 >=

### If you're running Python >= 3.12 you might need to manually install setuptools.
```
pip install setuptools 
```

### Activate a virtual environment
```
pip install -r requirements.txt
python main.py
```

## Running with Docker:
I recommend setting up the logging file map in the docker-compose.yml. You can update the left file path with the one on your host system. Optionally you can map the SQLite database from the container to your host machine.
!!! These files must exist on the host system. They will not be created automatically.

```
volumes:
    ~\Documents\code\logs\ObamaBot\bot.log:/app/logs/bot.log
    ~\Documents\code\database\obamabot.db:/app/database/obamabot.db
```


### To build the container and then run it
```
docker build . -t obama-bot

docker run -d obama-bot
```

### Run with docker-compose.yml
```
docker compose up --build -d
```

## To push to Google Artifacts Repository
Download and install Google Cloud CLI and Docker

```
docker tag {image_name} {repo_url/{image_name:{tag}}}

docker push {repo_url/{image_name:{tag}}}
```

## Troubleshooting
entrypoint.sh:
    If Docker is complaining about entrypoint.sh like ```python3-obamabot  | exec ./entrypoint.sh: no such file or directory``` then you need to convert entrypoint.sh from CRLF to LF so the script is recognized on the linux system.
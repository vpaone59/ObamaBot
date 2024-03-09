# ObamaBot
ObamaBot - Vincent Paone

A general purpose Discord Bot. Contains Cogs specific to ObamaBot and other special Guilds/Servers.

## Running locally without Docker:
### requires Python3.8 >=
### https://discordpy.readthedocs.io/en/latest/migrating.html
pip install -r requirements.txt

Must have a Discord Bot Token ready. Place Token in the SAMPLE.env file. Rename SAMPLE.env file to ".env" (without quotes).

python (or python3) main.py

## Running with Docker:
### When running with Docker you cannot have any code that accesses USB elements. I've found that the container will not start at all if camcap.py is included in the Cogs.
### You also cannot access any services that are running on the host machine with this simple configuration. The counter.py Cog will not work correctly with MySQL Server running on the host system and not within the same Docker container or another container on the same network.
Build the container
docker build . -t obama-bot --no-cache

Run the container (-d for detached mode to not take over the current shell session)
docker run -d obama-bot
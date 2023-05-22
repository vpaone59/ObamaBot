# ObamaBot
ObamaBot - Vincent Paone

A general purpose Discord Bot. Contains Cogs specific to ObamaBot and other special Guilds/Servers.

## Running locally without Docker:
### requires Python3.8 >=
### https://discordpy.readthedocs.io/en/latest/migrating.html
pip install -r requirements.txt

Must have a Discord Bot Token ready. Place Token in the SAMPLE.env file. Rename SAMPLE.env file to ".env" (without quotes).

python (or python3) ObamaBot.py

## Running with Docker:
### When running with Docker you cannot have any code that accesses USB elements. I've found that the container will not start at all if camcap.py is included in the Cogs.
Build the container
docker build . -t ObamaBot --no-cache

Run the container (-d for detached mode to not take over the current shell session)
docker run -d ObamaBot
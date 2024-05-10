#!/bin/bash

# Run the SQL script using SQLite
sqlite3 ./database/obamabot.db < ./database/init_create.sql
echo "database created at -> ./database/"

# Run the bot
python3 main.py
echo "Bot started -> python3 main.py"
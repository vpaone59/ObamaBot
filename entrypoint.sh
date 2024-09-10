#!/bin/bash

echo "Program is starting..."
echo "Checking if the database file exists..."

# Check if the database file exists
if [ -f "./database/obamabot.db" ]; then
    echo "Database file already exists at -> ./database/obamabot.db"
else
    echo "Database file does not exist. Creating database..."

    # Create the database file
    touch ./database/obamabot.db
    echo "Database file created at -> ./database/obamabot.db"
    
    # Create the tables
    sqlite3 ./database/obamabot.db < ./database/init_create.sql
    echo "Tables created in the database"
fi

# Run the bot
echo "Starting the bot..."
python3 main.py
echo "Bot started -> python3 main.py"
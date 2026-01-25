#!/bin/bash

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Installing dependencies..."
./venv/bin/pip install -q -r requirements.txt

echo "Starting services..."

./venv/bin/python api.py &
API_PID=$!
echo "Dashboard running at http://localhost:8080"

sleep 2

./venv/bin/python bot.py &
BOT_PID=$!
echo "Bot started"

trap "kill $API_PID $BOT_PID 2>/dev/null" EXIT

wait

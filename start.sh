#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "🔹 Starting Telegram Bot with Dashboard"
echo "ℹ️  Dashboard port is defined in config.py"

if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
./venv/bin/pip install -q -r requirements.txt

echo "🚀 Starting API (Dashboard)..."
./venv/bin/python api.py &
API_PID=$!

sleep 2

echo "🌐 Dashboard is running (check PORT in config.py)"

echo "🤖 Starting Telegram Bot..."
./venv/bin/python bot.py &
BOT_PID=$!
echo "✅ Bot is running"

trap "kill $API_PID $BOT_PID 2>/dev/null" EXIT
wait

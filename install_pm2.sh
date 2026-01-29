#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "🔧 Installing pm2 setup for Telegram Bot"

# Check Node.js
if ! command -v node >/dev/null 2>&1; then
    echo "❌ Node.js is not installed."
    echo "👉 Install Node.js first: https://nodejs.org/"
    exit 1
fi

# Install pm2 if not installed
if ! command -v pm2 >/dev/null 2>&1; then
    echo "📦 Installing pm2..."
    npm install -g pm2
else
    echo "✅ pm2 already installed"
fi

# Python venv
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing Python dependencies..."
./venv/bin/pip install -r requirements.txt

echo "🚀 Starting services with pm2..."

pm2 start api.py \
  --name telegram-dashboard \
  --interpreter ./venv/bin/python

pm2 start bot.py \
  --name telegram-bot \
  --interpreter ./venv/bin/python

pm2 save

echo "✅ pm2 setup complete"
echo "🌐 Dashboard port is defined in config.py"
echo "📌 Use 'pm2 status' to check services"

# Telegram Morning Bot

A Telegram bot that sends scheduled messages to multiple contacts with weather alerts.

## Features

- **Multiple contacts** - Each contact has their own schedule, messages, and settings
- **Flexible scheduling** - Set different times for each day of the week
- **Weather alerts** - Automatic warnings for cold, heat, and rain
- **Web dashboard** - Easy configuration through browser interface
- **Raspberry Pi ready** - Single script to run everything

## Setup

1. Get Telegram API credentials from https://my.telegram.org

2. Copy example configs:
```bash
cp config.example.py config.py
cp config.example.json config.json
```

3. Edit `config.py` with your credentials:
```python
API_ID = 'your_api_id'
API_HASH = 'your_api_hash'
PHONE = '+your_phone_number'
```

3. Run the bot:
```bash
chmod +x start.sh
./start.sh
```

4. On first run, enter the verification code sent to your Telegram

5. Open http://localhost:8080 to configure contacts and schedules

## Files

- `bot.py` - Main bot logic
- `api.py` - Web dashboard server
- `config.py` - Telegram API credentials (not in git)
- `config.json` - Contacts and schedules
- `index.html` - Dashboard interface
- `start.sh` - Startup script

## Dashboard

The web dashboard at http://localhost:8080 allows you to:

- Add/remove contacts
- Enable/disable contacts
- Set schedule for each day
- Add custom messages
- Configure weather alerts per contact

## Weather Alerts

Each contact can have weather alerts enabled with custom thresholds:

- Cold temperature warning
- Heat temperature warning
- Rain probability warning
- Custom messages for each condition

Weather data is fetched from Open-Meteo API (free, no key required).

## Running on Raspberry Pi

```bash
# Clone the repo
git clone <your-repo-url>
cd telegram-bot

# Make executable and run
chmod +x start.sh
./start.sh
```

To run on startup, add to crontab:
```bash
crontab -e
# Add this line:
@reboot /home/pi/telegram-bot/start.sh
```

## License

MIT

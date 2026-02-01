# Pretend-To-Care Bot

> Version 1.1.0

Too lazy to text "good morning" to people? Same. Now also too lazy to check crypto prices yourself.

## What's this?

A bot that pretends to be you and sends messages to people on your behalf. Because:
- You're too lazy to type "good morning" every day
- You keep forgetting to text people
- You want to look caring without actually doing anything
- Bonus: it can warn them about weather too (you're so thoughtful!)
- Double bonus: it watches crypto prices so you don't have to stare at charts at 3am

Set it up once, forget it forever. Your friends think you're the sweetest person alive. You're actually still asleep. And somehow also a crypto analyst.

## Features

- **Multiple contacts** - Annoy everyone you love with scheduled messages
- **Per-day scheduling** - Different times for weekdays vs lazy weekends
- **Anti-repeat messages** - Won't send the same message twice in a row (unlike your ex)
- **Weather alerts** - "Take a jacket" but automated (cold/heat/rain)
- **Crypto price alerts** - Because FOMO never sleeps (price targets, % changes, repeat mode)
- **Auto-reconnect** - Bot reconnects to Telegram if connection drops (it cares more than you do)
- **Real-time Telegram status** - Green = bot is alive, Red = time to panic
- **Help button (?)** - Explains how crypto alerts work, since you'll forget
- **Dark mode dashboard** - Because we're not savages
- **RU/EN support** - Dashboard works in Russian and English
- **Masonry layout** - Cards don't push each other around like siblings
- **Configurable port** - Change it in config.py
- **Activity logs** - Watch your bot pretend to be you
- **Raspberry Pi friendly** - Set it and forget it

## Quick Start

```bash
# 1. Get your Telegram API keys from https://my.telegram.org
#    (Yes, you need to do this. No, there's no way around it.)

# 2. Copy the example configs
cp config.example.py config.py
cp config.example.json config.json

# 3. Edit config.py with your credentials
nano config.py

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run it!
chmod +x start.sh
./start.sh

# 6. Enter the Telegram verification code when prompted
# 7. Open http://localhost:8080 and add your contacts
# 8. Profit!
```

## Dashboard

Open `http://localhost:8080` after starting the bot.

Here you can:
- Add people to your morning greeting list
- Set up schedules (sleep in on Sundays!)
- Write custom messages (be creative!)
- Configure weather alerts (cold/hot/rainy warnings)
- Set up crypto price alerts per contact
- Click the **?** button to understand how crypto alerts actually work
- Watch the logs to make sure it's actually working
- See Telegram connection status in real-time

## Weather Alerts

The bot checks weather and can warn about:
- **Cold** - "Bundle up!" when it's below your threshold
- **Heat** - "Stay hydrated!" when it's scorching
- **Rain** - "Take an umbrella!" when rain is likely

Uses Open-Meteo API - free, no API key needed.

## Crypto Alerts

The bot checks crypto prices every 60 seconds and can alert about:
- **Price above/below** - "BTC hit $100k!" (finally)
- **24h change %** - "ETH dropped 10%!" (time to panic or buy the dip)
- **Repeat mode** - Keeps bugging you every time it moves another X% from the last alert

Uses CoinGecko API - free, no API key needed. Supports 30+ coins (BTC, ETH, SOL, DOGE, PEPE... yes, PEPE).

Format: `BTC $98,500 (+3.2%)`

Smart deduplication: alerts fire once, reset when condition stops being true, fire again when it triggers next time. Your phone won't explode.

## Running 24/7 on Raspberry Pi

```bash
# Add to crontab for autostart
crontab -e

# Add this line:
@reboot /home/pi/telegram-bot/start.sh
```

Now your Pi is a dedicated good-morning-and-also-crypto-panic machine.

## File Structure

```
├── dashboard/
│   ├── index.html       - The pretty face (dashboard UI)
│   ├── styles.css       - The looks (dashboard styling)
│   ├── i18n.js          - The translator (language loader)
│   └── i18n/
│       ├── ru.js        - Russian translations
│       └── en.js        - English translations
├── bot.py               - The brain (messages, weather, crypto)
├── api.py               - The dashboard server (Flask API)
├── config.py            - Your secrets (don't commit this!)
├── config.json          - Your contacts and settings (auto-created)
├── config.example.json  - Example config (commit-safe)
├── requirements.txt     - Python dependencies
├── status.json          - Bot heartbeat (auto-generated)
├── logs.json            - Activity history (auto-generated)
└── start.sh             - One script to rule them all
```

## Tech Stack

- **Telethon** - Telegram client library
- **Flask** - Lightweight web server
- **Open-Meteo** - Free weather API
- **CoinGecko** - Free crypto price API
- **Vanilla JS** - No frameworks, no problems

## License

MIT - Do whatever you want with it.

---

Made with mass lack of sleep, mass amount of coffee, and an unhealthy obsession with crypto charts.

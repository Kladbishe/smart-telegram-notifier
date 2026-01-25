# Pretend-To-Care Bot

> Version 1.0.0

Too lazy to text "good morning" to people? Same.

## What's this?

A bot that pretends to be you and sends messages to people on your behalf. Because:
- You're too lazy to type "good morning" every day
- You keep forgetting to text people
- You want to look caring without actually doing anything
- Bonus: it can warn them about weather too (you're so thoughtful!)

Set it up once, forget it forever. Your friends think you're the sweetest person alive. You're actually still asleep.

## Features

- **Multiple contacts** - Annoy everyone you love with scheduled messages
- **Per-day scheduling** - Different times for weekdays vs lazy weekends
- **Weather alerts** - "Take a jacket" but automated (cold/heat/rain)
- **Real-time Telegram status** - Green = bot is alive, Red = time to panic
- **Dark mode dashboard** - Because we're not savages
- **RU/EN support** - Dashboard works in Russian and English
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

# 4. Run it!
chmod +x start.sh
./start.sh

# 5. Enter the Telegram verification code when prompted
# 6. Open http://localhost:8080 and add your contacts
# 7. Profit!
```

## Dashboard

Open `http://localhost:8080` after starting the bot.

Here you can:
- Add people to your morning greeting list
- Set up schedules (sleep in on Sundays!)
- Write custom messages (be creative!)
- Configure weather alerts (cold/hot/rainy warnings)
- Watch the logs to make sure it's actually working
- See Telegram connection status in real-time

## Weather Alerts

The bot checks weather and can warn about:
- **Cold** - "Bundle up!" when it's below your threshold
- **Heat** - "Stay hydrated!" when it's scorching
- **Rain** - "Take an umbrella!" when rain is likely

Uses Open-Meteo API - free, no API key needed.

## Running 24/7 on Raspberry Pi

```bash
# Add to crontab for autostart
crontab -e

# Add this line:
@reboot /home/pi/telegram-bot/start.sh
```

Now your Pi is a dedicated good-morning machine.

## File Structure

```
├── dashboard/
│   ├── index.html   - The pretty face (dashboard UI)
│   ├── styles.css   - The looks (dashboard styling)
│   └── i18n.js      - The translator (RU/EN translations)
├── bot.py           - The brain (sends messages, checks weather)
├── api.py           - The dashboard server (Flask API)
├── config.py        - Your secrets (don't commit this!)
├── config.json      - Your contacts and settings (auto-created)
├── status.json      - Bot heartbeat (auto-generated)
├── logs.json        - Activity history (auto-generated)
└── start.sh         - One script to rule them all
```

## Tech Stack

- **Telethon** - Telegram client library
- **Flask** - Lightweight web server
- **Open-Meteo** - Free weather API
- **Vanilla JS** - No frameworks, no problems

## License

MIT - Do whatever you want with it.

---

Made with mass lack of sleep and mass amount of coffee.

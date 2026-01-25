import asyncio
import json
import random
import urllib.request
from datetime import datetime, timedelta
from telethon import TelegramClient
from config import API_ID, API_HASH, PHONE

CONFIG_FILE = "config.json"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

GEOCODE_API = "https://geocoding-api.open-meteo.com/v1/search"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_coordinates(city):
    try:
        url = f"{GEOCODE_API}?name={city}&count=1"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("results"):
                r = data["results"][0]
                return r["latitude"], r["longitude"]
    except:
        pass
    return 32.0853, 34.7818

def get_weather(city, settings):
    lat, lon = get_coordinates(city)
    url = f"{WEATHER_API}?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability,apparent_temperature&forecast_days=1"

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        hourly = data.get("hourly", {})
        temps = hourly.get("temperature_2m", [])[7:22]
        apparent = hourly.get("apparent_temperature", [])[7:22]
        rain_prob = hourly.get("precipitation_probability", [])[7:22]

        if not temps:
            return None

        min_temp = min(temps)
        max_temp = max(temps)
        min_apparent = min(apparent) if apparent else min_temp
        max_rain = max(rain_prob) if rain_prob else 0

        alerts = []

        if min_apparent < settings.get("cold_threshold", 15):
            alerts.append(settings.get("cold_message", "It's cold today!"))

        if max_temp > settings.get("heat_threshold", 30):
            alerts.append(settings.get("heat_message", "It's hot today!"))

        if max_rain >= settings.get("rain_threshold", 60):
            alerts.append(settings.get("rain_message", "Take an umbrella!"))

        if not alerts:
            return None

        return f"Weather {min_temp:.0f}-{max_temp:.0f}C\n" + "\n".join(alerts)

    except Exception as e:
        print(f"Weather error: {e}")
        return None

def get_today_send_time(schedule):
    now = datetime.now()
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_name = days[now.weekday()]
    day_schedule = schedule.get(day_name, {})

    if not day_schedule.get("enabled"):
        return None

    time_str = day_schedule.get("time", "09:00")
    hour, minute = map(int, time_str.split(":"))
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

async def run_bot():
    client = TelegramClient('session_name', API_ID, API_HASH)
    await client.start(phone=PHONE)
    print("Bot connected to Telegram")

    sent_today = {}

    while True:
        config = load_config()
        now = datetime.now()

        for contact in config.get("contacts", []):
            if not contact.get("enabled"):
                continue

            contact_id = contact.get("id")
            phone = contact.get("phone")

            if not phone:
                continue

            send_time = get_today_send_time(contact.get("schedule", {}))

            if not send_time:
                continue

            today_key = f"{contact_id}_{now.date()}"

            if today_key in sent_today:
                continue

            if now >= send_time and now < send_time + timedelta(minutes=1):
                try:
                    messages = contact.get("messages", [])
                    if messages:
                        msg = random.choice(messages)
                        await client.send_message(phone, msg)
                        print(f"Sent to {contact.get('name')}: {msg}")

                    weather_settings = contact.get("weather", {})
                    if weather_settings.get("enabled"):
                        city = weather_settings.get("city", "Tel Aviv")
                        weather_msg = get_weather(city, weather_settings)
                        if weather_msg:
                            await client.send_message(phone, weather_msg)
                            print(f"Sent weather to {contact.get('name')}")

                    sent_today[today_key] = True

                except Exception as e:
                    print(f"Error sending to {contact.get('name')}: {e}")

        old_keys = [k for k in sent_today if k.split("_")[1] != str(now.date())]
        for k in old_keys:
            del sent_today[k]

        await asyncio.sleep(10)

if __name__ == "__main__":
    print("Starting Telegram Bot...")
    asyncio.run(run_bot())

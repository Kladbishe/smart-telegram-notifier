import asyncio
import json
import random
import ssl
import urllib.request
import certifi
from datetime import datetime, timedelta
from telethon import TelegramClient
from config import API_ID, API_HASH, PHONE

CONFIG_FILE = "config.json"
LOGS_FILE = "logs.json"
STATUS_FILE = "status.json"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"
GEOCODE_API = "https://geocoding-api.open-meteo.com/v1/search"
COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"
MAX_LOGS = 100
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

SYMBOL_TO_COINGECKO = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "xrp": "ripple",
    "sol": "solana",
    "ada": "cardano",
    "doge": "dogecoin",
    "dot": "polkadot",
    "matic": "matic-network",
    "pol": "matic-network",
    "avax": "avalanche-2",
    "link": "chainlink",
    "shib": "shiba-inu",
    "ltc": "litecoin",
    "bch": "bitcoin-cash",
    "uni": "uniswap",
    "xlm": "stellar",
    "atom": "cosmos",
    "near": "near",
    "apt": "aptos",
    "sui": "sui",
    "ton": "the-open-network",
    "trx": "tron",
    "bnb": "binancecoin",
    "etc": "ethereum-classic",
    "fil": "filecoin",
    "vet": "vechain",
    "algo": "algorand",
    "icp": "internet-computer",
    "arb": "arbitrum",
    "op": "optimism",
    "pepe": "pepe",
    "usdt": "tether",
    "usdc": "usd-coin",
}

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def update_status(connected):
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump({
                "connected": connected,
                "timestamp": datetime.now().isoformat()
            }, f)
    except:
        pass

def add_log(log_type, message, contact=None):
    try:
        try:
            with open(LOGS_FILE, "r") as f:
                logs = json.load(f)
        except:
            logs = []

        logs.insert(0, {
            "time": datetime.now().strftime("%H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": log_type,
            "message": message,
            "contact": contact
        })

        logs = logs[:MAX_LOGS]

        with open(LOGS_FILE, "w") as f:
            json.dump(logs, f, ensure_ascii=False)
    except:
        pass

def get_coordinates(city):
    try:
        url = f"{GEOCODE_API}?name={city}&count=1"
        with urllib.request.urlopen(url, timeout=10, context=SSL_CTX) as resp:
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
        with urllib.request.urlopen(url, timeout=10, context=SSL_CTX) as resp:
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

        if min_temp < settings.get("cold_threshold", 15):
            alerts.append(settings.get("cold_message") or "одевайся потеплее")

        if max_temp > settings.get("heat_threshold", 30):
            alerts.append(settings.get("heat_message") or "будет жарко")

        if max_rain >= settings.get("rain_threshold", 60):
            alerts.append(settings.get("rain_message") or "возможно будет дождь")

        if not alerts:
            return None

        return f"{min_temp:.0f}-{max_temp:.0f}°С, " + ", ".join(alerts)

    except Exception as e:
        print(f"Weather error: {e}")
        return None

def get_crypto_prices(coin_ids):
    if not coin_ids:
        return None
    ids_str = ",".join(coin_ids)
    url = f"{COINGECKO_API}?ids={ids_str}&vs_currencies=usd&include_24hr_change=true"
    try:
        with urllib.request.urlopen(url, timeout=15, context=SSL_CTX) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Crypto API error: {e}")
        return None

def format_crypto_alert(symbol, price, change_24h):
    sign = "+" if change_24h >= 0 else ""
    return f"{symbol} ${price:,.0f} ({sign}{change_24h:.1f}%)"

def check_crypto_alerts(crypto_config, prices, alert_state, contact_id=""):
    if not prices:
        return []
    triggered = []
    for coin in crypto_config.get("coins", []):
        symbol = coin.get("symbol", "").upper()
        coin_id = SYMBOL_TO_COINGECKO.get(symbol.lower())
        if not coin_id:
            continue
        coin_data = prices.get(coin_id)
        if not coin_data:
            continue
        price = coin_data.get("usd", 0)
        change = coin_data.get("usd_24h_change", 0) or 0
        for alert in coin.get("alerts", []):
            if not alert.get("enabled"):
                continue
            alert_type = alert["type"]
            alert_value = alert["value"]
            state_key = f"{contact_id}_{coin_id}_{alert_type}_{alert_value}"
            condition_met = False
            if alert_type == "price_above":
                condition_met = price >= alert_value
            elif alert_type == "price_below":
                condition_met = price <= alert_value
            elif alert_type == "change_above":
                condition_met = change >= alert_value
            elif alert_type == "change_below":
                condition_met = change <= -alert_value
            if condition_met:
                prev = alert_state.get(state_key)
                if prev is None:
                    if alert.get("repeat") and alert_type.startswith("change"):
                        alert_state[state_key] = price
                    else:
                        alert_state[state_key] = True
                    triggered.append({
                        "coin_id": coin_id,
                        "message": format_crypto_alert(symbol, price, change)
                    })
                elif alert.get("repeat"):
                    if alert_type.startswith("change") and isinstance(prev, (int, float)):
                        pct = ((price - prev) / prev) * 100 if prev else 0
                        fire = (alert_type == "change_above" and pct >= alert_value) or \
                               (alert_type == "change_below" and pct <= -alert_value)
                        if fire:
                            alert_state[state_key] = price
                            triggered.append({
                                "coin_id": coin_id,
                                "message": format_crypto_alert(symbol, price, change)
                            })
                    else:
                        triggered.append({
                            "coin_id": coin_id,
                            "message": format_crypto_alert(symbol, price, change)
                        })
            else:
                alert_state.pop(state_key, None)
    return triggered

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
    add_log("info", "Bot connected to Telegram")
    update_status(True)

    sent_today = {}
    last_messages = {}
    last_connection_check = datetime.now()
    last_crypto_check = datetime.min
    crypto_alert_state = {}

    while True:
        try:
            now = datetime.now()
            if (now - last_connection_check).total_seconds() >= 43200:
                last_connection_check = now
                if not client.is_connected():
                    print("Disconnected, reconnecting...")
                    add_log("info", "Reconnecting to Telegram...")
                    await client.connect()
                    if not await client.is_user_authorized():
                        await client.start(phone=PHONE)
                    print("Reconnected to Telegram")
                    add_log("info", "Reconnected to Telegram")

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
                            last = last_messages.get(contact_id)
                            if len(messages) > 1 and last in messages:
                                choices = [m for m in messages if m != last]
                            else:
                                choices = messages
                            msg = random.choice(choices)
                            await client.send_message(phone, msg)
                            last_messages[contact_id] = msg
                            print(f"Sent to {contact.get('name')}: {msg}")
                            add_log("sent", msg, contact.get('name'))

                        weather_settings = contact.get("weather", {})
                        if weather_settings.get("enabled"):
                            city = weather_settings.get("city", "Tel Aviv")
                            weather_msg = get_weather(city, weather_settings)
                            if weather_msg:
                                await client.send_message(phone, weather_msg)
                                print(f"Sent weather to {contact.get('name')}")
                                add_log("weather", weather_msg, contact.get('name'))

                        sent_today[today_key] = True

                    except Exception as e:
                        print(f"Error sending to {contact.get('name')}: {e}")
                        add_log("error", str(e), contact.get('name'))

            old_keys = [k for k in sent_today if k.split("_")[1] != str(now.date())]
            for k in old_keys:
                del sent_today[k]

            # Crypto price alerts (per-contact)
            if (now - last_crypto_check).total_seconds() >= 60:
                last_crypto_check = now
                all_coin_ids = set()
                for contact in config.get("contacts", []):
                    if not contact.get("enabled"):
                        continue
                    c_crypto = contact.get("crypto", {})
                    if not c_crypto.get("enabled"):
                        continue
                    for coin in c_crypto.get("coins", []):
                        coin_id = SYMBOL_TO_COINGECKO.get(coin.get("symbol", "").lower())
                        if coin_id:
                            all_coin_ids.add(coin_id)

                if all_coin_ids:
                    prices = get_crypto_prices(list(all_coin_ids))
                    if prices:
                        for contact in config.get("contacts", []):
                            if not contact.get("enabled"):
                                continue
                            c_crypto = contact.get("crypto", {})
                            if not c_crypto.get("enabled"):
                                continue
                            contact_id = contact.get("id")
                            alerts = check_crypto_alerts(c_crypto, prices, crypto_alert_state, contact_id)
                            for alert in alerts:
                                try:
                                    await client.send_message(contact["phone"], alert["message"])
                                    add_log("crypto", alert["message"], contact.get("name"))
                                except Exception as e:
                                    print(f"Crypto send error: {e}")

            update_status(client.is_connected())

        except ConnectionError:
            print("Connection lost, will retry...")
            add_log("error", "Connection lost, retrying...")
            update_status(False)

        await asyncio.sleep(10)

if __name__ == "__main__":
    print("Starting Telegram Bot...")
    add_log("info", "Bot starting...")
    asyncio.run(run_bot())

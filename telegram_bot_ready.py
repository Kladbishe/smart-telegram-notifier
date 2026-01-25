import asyncio
from datetime import datetime, time
from telethon import TelegramClient
import random
import urllib.request
import json

from config import (
    API_ID, API_HASH, PHONE, RECIPIENT, MESSAGES,
    LATITUDE, LONGITUDE, COLD_THRESHOLD, RAIN_PROBABILITY_THRESHOLD
)

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# Время отправки (24-часовой формат)
SEND_TIME = time(6,30)


def get_weather_alert():
    """Проверяет погоду и возвращает предупреждение если нужно"""
    url = f"{WEATHER_API_URL}?latitude={LATITUDE}&longitude={LONGITUDE}&hourly=temperature_2m,precipitation,rain,precipitation_probability,apparent_temperature&forecast_days=1"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status != 200:
                return None
            data = json.loads(response.read().decode())

        hourly = data.get("hourly", {})
        temperatures = hourly.get("temperature_2m", [])
        apparent_temps = hourly.get("apparent_temperature", [])
        rain = hourly.get("rain", [])
        precipitation_prob = hourly.get("precipitation_probability", [])

        # Анализируем данные на дневное время (7:00 - 22:00)
        day_temps = temperatures[7:22]
        day_apparent = apparent_temps[7:22]
        day_rain = rain[7:22]
        day_prob = precipitation_prob[7:22]

        min_temp = min(day_temps) if day_temps else None
        max_temp = max(day_temps) if day_temps else None
        min_apparent = min(day_apparent) if day_apparent else None
        total_rain = sum(day_rain) if day_rain else 0
        max_rain_prob = max(day_prob) if day_prob else 0

        alerts = []

        # Проверяем холод
        if min_apparent and min_apparent < COLD_THRESHOLD:
            alerts.append(f"🥶 будет холодно!")

        # Проверяем дождь
        if total_rain > 0:
            alerts.append(f"🌧 Сегодня будет дождь")
        elif max_rain_prob >= RAIN_PROBABILITY_THRESHOLD:
            alerts.append(f"☔ Вероятность дождя {max_rain_prob}% — возьми зонтик!")

        if not alerts:
            return None

        # Формируем сообщение
        weather_msg = f"🌡 Сегодня температура {min_temp:.0f}°C — {max_temp:.0f}°C\n"
        weather_msg += "\n".join(alerts)

        return weather_msg

    except Exception as e:
        print(f"❌ Ошибка получения погоды: {e}")
        return None


async def send_daily_message():
    """Отправляет ежедневное сообщение"""
    client = TelegramClient('session_name', API_ID, API_HASH)
    
    await client.start(phone=PHONE)
    print("✅ Успешно подключились к Telegram!")
    
    while True:
        now = datetime.now()
        current_time = now.time()
        
        # Вычисляем время до следующей отправки
        if current_time < SEND_TIME:
            # Отправка сегодня
            next_send = datetime.combine(now.date(), SEND_TIME)
        else:
            # Отправка завтра
            next_send = datetime.combine(now.date(), SEND_TIME)
            next_send = next_send.replace(day=next_send.day + 1)
        
        # Ждём до времени отправки
        wait_seconds = (next_send - now).total_seconds()
        print(f"⏰ Следующее сообщение будет отправлено в {next_send.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏳ Ожидание {wait_seconds/3600:.1f} часов...")
        
        await asyncio.sleep(wait_seconds)
        
        # Отправляем сообщение
        try:
            message = random.choice(MESSAGES)
            await client.send_message(RECIPIENT, message)
            print(f"✉️ Сообщение отправлено: {message}")

            # Проверяем погоду и отправляем предупреждение если нужно
            weather_alert = get_weather_alert()
            if weather_alert:
                await client.send_message(RECIPIENT, weather_alert)
                print(f"🌤 Отправлено предупреждение о погоде")
        except Exception as e:
            print(f"❌ Ошибка при отправке: {e}")
        
        # Ждём 60 секунд чтобы не отправить дважды
        await asyncio.sleep(60)

if __name__ == '__main__':
    print("🤖 Бот запущен!")
    print("📱 Будут отправляться сообщения от вашего аккаунта")
    print("=" * 50)
    asyncio.run(send_daily_message())

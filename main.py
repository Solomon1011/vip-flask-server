import os
import requests
from telegram import Bot

# === TELEGRAM SETTINGS ===
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
APP_URL = os.environ.get("APP_URL")  # Your Flask app URL

if not TOKEN or not CHANNEL_ID or not APP_URL:
    raise Exception("Telegram token, channel ID, or APP_URL is missing!")

bot = Bot(token=TOKEN)

# === FETCH TODAY'S TIPS FROM APP ===
try:
    response = requests.get(f"{APP_URL}/api/today_tips", timeout=10)
    data = response.json()
    today_free_tips = data.get("free", [])
    today_vip_tips = data.get("vip", [])

except Exception as e:
    print("❌ Error fetching tips from app:", e)
    today_free_tips = []
    today_vip_tips = []

# === SEND TO TELEGRAM ===
try:
    if today_free_tips:
        free_message = "📌 Free Tips Today:\n" + "\n".join(today_free_tips)
        bot.send_message(chat_id=CHANNEL_ID, text=free_message)

    vip_message = "🔒 VIP Tips Today: Subscribe in the app to unlock!"
    bot.send_message(chat_id=CHANNEL_ID, text=vip_message)

    print("✅ Telegram post sent successfully!")

except Exception as e:
    print("❌ Error sending message to Telegram:", e)
    raise e

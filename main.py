import os
import requests
from telegram import Bot

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
APP_URL = os.environ.get("APP_URL")  # your app URL

bot = Bot(token=TOKEN)

# Fetch Free & VIP tips
tips = requests.get(f"{APP_URL}/api/today_tips").json()
today_free_tips = tips.get("free", [])
today_vip_tips = tips.get("vip", [])

# Fetch VIP results
results = requests.get(f"{APP_URL}/api/vip_results").json()
vip_results = results.get("results", [])

# Send messages to Telegram
if today_free_tips:
    bot.send_message(chat_id=CHANNEL_ID, text="📌 Free Tips Today:\n" + "\n".join(today_free_tips))

bot.send_message(chat_id=CHANNEL_ID, text="🔒 VIP Tips Today: Subscribe in the app to unlock!")

if vip_results:
    bot.send_message(chat_id=CHANNEL_ID, text="🏆 VIP Results:\n" + "\n".join(vip_results))

print("✅ Telegram post sent successfully!")

import os
from telegram import Bot

# === TELEGRAM BOT SETTINGS ===
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

if not TOKEN or not CHANNEL_ID:
    raise Exception("Telegram bot token or channel ID not set in secrets!")

bot = Bot(token=TOKEN)

# === TODAY'S TIPS ===
# Replace these with your app's daily tips arrays if needed
today_free_tips = [
    "Arsenal vs Chelsea 2:1",
    "Barcelona vs Sevilla 1:0",
    "Bayern vs Dortmund 3:2"
]

today_vip_tips = [
    "Real Madrid vs Atletico 2:1",
    "Liverpool vs Man City 1:1"
]

try:
    # Send Free Tips
    free_message = "📌 Free Tips Today:\n" + "\n".join(today_free_tips)
    bot.send_message(chat_id=CHANNEL_ID, text=free_message)

    # Send VIP locked message
    vip_message = "🔒 VIP Tips Today: Subscribe in the app to unlock!"
    bot.send_message(chat_id=CHANNEL_ID, text=vip_message)

    print("✅ Telegram post sent successfully!")

except Exception as e:
    print("❌ Error sending to Telegram:", e)
    raise e


import os
from telegram import Bot

# -------------------------------
# Initialize bot from GitHub Secrets
# -------------------------------
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
channel_id = os.environ.get("TELEGRAM_CHANNEL_ID")

if not bot_token or not channel_id:
    raise ValueError("Telegram bot token or channel ID not set in environment variables!")

bot = Bot(token=bot_token)

# -------------------------------
# TODAY'S TIPS
# -------------------------------
today_free_tips = [
    "Arsenal vs Chelsea 2:1",
    "Barcelona vs Sevilla 1:0",
    "Bayern vs Dortmund 3:2"
]

today_vip_tips = [
    "Real Madrid vs Atletico 2:1",
    "Liverpool vs Man City 1:1"
]

# -------------------------------
# SEND TO TELEGRAM
# -------------------------------
try:
    # Free Tips
    free_message = "📌 Free Tips Today:\n" + "\n".join(today_free_tips)
    bot.send_message(chat_id=channel_id, text=free_message)

    # VIP Tips (locked)
    vip_message = "🔒 VIP Tips Today: (Subscribe to unlock in the app!)"
    bot.send_message(chat_id=channel_id, text=vip_message)

    print("✅ Telegram post sent successfully!")

except Exception as e:
    print("❌ Error sending to Telegram:", e)

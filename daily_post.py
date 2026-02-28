import os
from telegram import Bot

# Initialize bot
bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
channel_id = os.environ["TELEGRAM_CHANNEL_ID"]

# === TODAY'S TIPS ===
# Replace these with your real arrays if needed
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
    bot.send_message(chat_id=channel_id, text=free_message)

    # Send VIP locked message
    vip_message = "🔒 VIP Tips Today: (Subscribe to unlock in the app!)"
    bot.send_message(chat_id=channel_id, text=vip_message)

    print("✅ Telegram post sent successfully!")

except Exception as e:
    print("❌ Error sending to Telegram:", e)

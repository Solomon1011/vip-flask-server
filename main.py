import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

free_tips = [
    ["Arsenal vs Chelsea 2:1", "Barcelona vs Sevilla 1:0", "Bayern vs Dortmund 3:2"],
    ["Man U vs Liverpool 1:2", "Real Madrid vs Valencia 3:1", "PSG vs Lyon 2:2"],
    ["Juventus vs Inter 1:1", "Atletico vs Sevilla 2:0", "Dortmund vs Bayern 1:3"]
]

index = datetime.utcnow().day % len(free_tips)
today = free_tips[index]

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(url, json={
    "chat_id": CHANNEL_ID,
    "text": "📌 Free Tips Today:\n" + "\n".join(today)
})

print("DONE")

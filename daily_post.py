from datetime import datetime
import requests
import os

FREE_TIPS = [
    ["Arsenal vs Chelsea 2:1", "Barcelona vs Sevilla 1:0", "Bayern vs Dortmund 3:2"],
    ["Man U vs Liverpool 1:2", "Real Madrid vs Valencia 3:1", "PSG vs Lyon 2:2"],
    ["Juventus vs Inter 1:1", "Atletico vs Sevilla 2:0", "Dortmund vs Bayern 1:3"]
]

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHANNEL_ID, "text": text})

index = datetime.now().day % len(FREE_TIPS)
send("📌 Free Tips Today:\n" + "\n".join(FREE_TIPS[index]))
send("🔒 VIP Tips Today\nSubscribe in the app to unlock")

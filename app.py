
from flask import Flask, render_template
from datetime import datetime
import threading
import time
import requests
import os

app = Flask(__name__)

# -------------------------------
# DAILY TIPS DATA
# -------------------------------

free_tips_list = [
    ["Arsenal vs Chelsea 2:1", "Barcelona vs Sevilla 1:0", "Bayern vs Dortmund 3:2"],
    ["Man U vs Liverpool 1:2", "Real Madrid vs Valencia 3:1", "PSG vs Lyon 2:2"],
    ["Juventus vs Inter 1:1", "Atletico vs Sevilla 2:0", "Dortmund vs Bayern 1:3"]
]

vip_tips_list = [
    ["Real Madrid vs Atletico 2:1", "Liverpool vs Man City 1:1"],
    ["Barcelona vs Real Sociedad 3:1", "Chelsea vs Tottenham 2:1"],
    ["Bayern vs Dortmund 2:2", "Juventus vs Napoli 1:0"]
]

today_free_tips = []
today_vip_tips = []
vip_results_today = []

# -------------------------------
# TELEGRAM SETTINGS (ENV VARS)
# -------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# -------------------------------
# FUNCTION TO UPDATE TIPS DAILY AT 9AM
# -------------------------------
def update_daily_tips():
    global today_free_tips, today_vip_tips, vip_results_today

    while True:
        now = datetime.now()

        if now.hour == 9 and now.minute == 0:
            index = now.day % len(free_tips_list)
            today_free_tips = free_tips_list[index]
            today_vip_tips = vip_tips_list[index]
            vip_results_today = [tip + " ✅" for tip in today_vip_tips]

            print("Daily tips updated")

            # Telegram posting
            send_telegram_message(
                "📌 Free Tips Today:\n" + "\n".join(today_free_tips)
            )
            send_telegram_message(
                "🔒 VIP Tips Today\nSubscribe in the app to unlock"
            )

            time.sleep(60)

        time.sleep(20)

# Start scheduler thread
threading.Thread(target=update_daily_tips, daemon=True).start()

# -------------------------------
# ROUTES
# -------------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/free")
def free():
    return render_template("free.html", tips=today_free_tips)

@app.route("/subscribe")
def subscribe():
    return render_template("vip.html", tips=today_vip_tips)

@app.route("/vip_results")
def vip_results():
    return render_template("vip_results.html", results=vip_results_today)

# -------------------------------
# START SERVER
# -------------------------------
if __name__ == "__main__":
    index = datetime.now().day % len(free_tips_list)
    today_free_tips = free_tips_list[index]
    today_vip_tips = vip_tips_list[index]
    vip_results_today = [tip + " ✅" for tip in today_vip_tips]

    app.run()

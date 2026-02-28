from flask import Flask, render_template, jsonify
from datetime import datetime
import threading
import time
import requests
import os

app = Flask(__name__)

# -------------------------------
# STORAGE FOR DAILY TIPS
# -------------------------------
today_free_tips = []
today_vip_tips = []
vip_results_today = []

# -------------------------------
# ENV VARIABLES
# -------------------------------
API_KEY = os.getenv("YOUR_API_KEY")  # your live match API key
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def fetch_today_matches():
    """Fetch today's matches from API"""
    if not API_KEY:
        print("API_KEY not set, using fallback tips")
        return [
            "Arsenal vs Chelsea 2:1",
            "Barcelona vs Sevilla 1:0",
            "Bayern vs Dortmund 3:2"
        ], [
            "Real Madrid vs Atletico 2:1",
            "Liverpool vs Man City 1:1"
        ]
    try:
        url = f"https://api.example.com/matches/today?api_key={API_KEY}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        free_tips = []
        vip_tips = []
        for match in data.get("matches", []):
            free_tips.append(f"{match['home']} vs {match['away']} {match['free_score']}")
            vip_tips.append(f"{match['home']} vs {match['away']} {match['vip_score']}")
        return free_tips, vip_tips
    except Exception as e:
        print("Error fetching matches:", e)
        # fallback hardcoded tips
        return [
            "Arsenal vs Chelsea 2:1",
            "Barcelona vs Sevilla 1:0",
            "Bayern vs Dortmund 3:2"
        ], [
            "Real Madrid vs Atletico 2:1",
            "Liverpool vs Man City 1:1"
        ]

def send_telegram_message(text):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
        print("Telegram message sent!")
    except Exception as e:
        print("Telegram error:", e)

# -------------------------------
# FUNCTION TO UPDATE DAILY TIPS
# -------------------------------
def update_daily_tips():
    global today_free_tips, today_vip_tips, vip_results_today
    while True:
        now = datetime.now()
        if now.hour == 9 and now.minute == 0:  # run at 9 AM
            today_free_tips, today_vip_tips = fetch_today_matches()
            vip_results_today = [tip + " ✅" for tip in today_vip_tips]

            print("Daily tips updated!")

            # Optional: post to Telegram
            send_telegram_message("📌 Free Tips Today:\n" + "\n".join(today_free_tips))
            send_telegram_message("🔒 VIP Tips Today\nSubscribe in the app to unlock")
            send_telegram_message("📈 VIP Results:\n" + "\n".join(vip_results_today))

            time.sleep(60)  # avoid multiple triggers within same minute
        time.sleep(20)

# Start scheduler in a background thread
threading.Thread(target=update_daily_tips, daemon=True).start()

# -------------------------------
# ROUTES (WEB PAGES)
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
# API ROUTES (OPTIONAL)
# -------------------------------
@app.route("/api/today_tips")
def api_today_tips():
    return {"free": today_free_tips, "vip": today_vip_tips}

@app.route("/api/vip_results")
def api_vip_results():
    return {"results": vip_results_today}

# -------------------------------
# START SERVER
# -------------------------------
if __name__ == "__main__":
    today_free_tips, today_vip_tips = fetch_today_matches()
    vip_results_today = [tip + " ✅" for tip in today_vip_tips]
    app.run()

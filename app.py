from flask import Flask, render_template, jsonify
from datetime import datetime
import threading
import time
import requests
import os

app = Flask(__name__)

# -------------------------------
# STORAGE
# -------------------------------
today_free_tips = []
today_vip_tips = []
vip_results_today = []

# -------------------------------
# ENV VARIABLES
# -------------------------------
API_KEY = os.getenv("API_FOOTBALL_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

API_URL = "https://v3.football.api-sports.io/fixtures"

# -------------------------------
# FETCH TODAY MATCHES (UTC SAFE)
# -------------------------------
def fetch_today_matches():
    global today_free_tips, today_vip_tips, vip_results_today

    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")

        headers = {
            "x-apisports-key": API_KEY
        }

        response = requests.get(
            f"{API_URL}?date={today}",
            headers=headers,
            timeout=15
        )

        data = response.json()
        free = []
        vip = []

        for fixture in data.get("response", []):
            teams = fixture["teams"]
            home = teams["home"]["name"]
            away = teams["away"]["name"]

            # simple placeholder prediction
            free.append(f"{home} vs {away} 1:0")
            vip.append(f"{home} vs {away} 2:1")

        today_free_tips = free
        today_vip_tips = vip
        vip_results_today = [tip + " ✅" for tip in vip]

        print("✅ Matches updated:", today)

        send_telegram_message("📌 Free Tips Today:\n" + "\n".join(today_free_tips[:5]))
        send_telegram_message("🔒 VIP Tips available in app")

    except Exception as e:
        print("❌ API error:", e)

# -------------------------------
# TELEGRAM
# -------------------------------
def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

# -------------------------------
# DAILY AUTO UPDATE (SAFE LOOP)
# -------------------------------
def scheduler():
    last_run = None

    while True:
        now = datetime.utcnow()
        today = now.strftime("%Y-%m-%d")

        if now.hour == 9 and last_run != today:
            fetch_today_matches()
            last_run = today

        time.sleep(60)

threading.Thread(target=scheduler, daemon=True).start()

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
# API
# -------------------------------
@app.route("/api/today_tips")
def api_today_tips():
    return jsonify({
        "free": today_free_tips,
        "vip": today_vip_tips
    })

# -------------------------------
# START
# -------------------------------
if __name__ == "__main__":
    fetch_today_matches()
    app.run()

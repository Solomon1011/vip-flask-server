from flask import Flask, render_template, jsonify
from datetime import datetime
import threading
import time
import requests
import os

app = Flask(__name__)

# -------------------------------
# STORAGE FOR TODAY'S TIPS
# -------------------------------
today_free_tips = []
today_vip_tips = []
vip_results_today = []

# -------------------------------
# TELEGRAM & LIVE MATCH API SETTINGS
# -------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
LIVE_API_KEY = os.getenv("YOUR_API_KEY")
LIVE_API_URL = "https://api.example.com/matches/today"  # Replace with your API endpoint

# -------------------------------
# FETCH TODAY'S MATCHES FROM API
# -------------------------------
def fetch_today_matches():
    global today_free_tips, today_vip_tips, vip_results_today
    try:
        response = requests.get(f"{LIVE_API_URL}?api_key={LIVE_API_KEY}", timeout=10)
        response.raise_for_status()
        data = response.json()
        free_tips = []
        vip_tips = []

        for match in data.get("matches", []):
            free_tips.append(f"{match['home']} vs {match['away']} {match['free_score']}")
            vip_tips.append(f"{match['home']} vs {match['away']} {match['vip_score']}")

        today_free_tips = free_tips
        today_vip_tips = vip_tips
        vip_results_today = [tip + " ✅" for tip in vip_tips]

        print("[INFO] Today's matches updated from API")

        # Optional: post to Telegram immediately
        send_telegram_message("📌 Free Tips Today:\n" + "\n".join(today_free_tips))
        send_telegram_message("🔒 VIP Tips Today\nSubscribe in the app to unlock")
        send_telegram_message("📈 VIP Results:\n" + "\n".join(vip_results_today))

    except Exception as e:
        print("[ERROR] Fetching matches failed:", e)
        # fallback hardcoded tips if API fails
        today_free_tips[:] = [
            "Arsenal vs Chelsea 2:1",
            "Barcelona vs Sevilla 1:0",
            "Bayern vs Dortmund 3:2"
        ]
        today_vip_tips[:] = [
            "Real Madrid vs Atletico 2:1",
            "Liverpool vs Man City 1:1"
        ]
        vip_results_today[:] = [tip + " ✅" for tip in today_vip_tips]

# -------------------------------
# SEND MESSAGE TO TELEGRAM
# -------------------------------
def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("Telegram not configured")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
        print("[INFO] Telegram message sent")
    except Exception as e:
        print("[ERROR] Telegram:", e)

# -------------------------------
# DAILY SCHEDULER THREAD
# -------------------------------
def daily_update_scheduler():
    while True:
        now = datetime.now()
        # Update at 9:00 AM every day
        if now.hour == 9 and now.minute == 0:
            fetch_today_matches()
            time.sleep(60)  # prevent multiple triggers within same minute
        time.sleep(20)

threading.Thread(target=daily_update_scheduler, daemon=True).start()

# -------------------------------
# WEB ROUTES
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
# API ENDPOINTS (optional)
# -------------------------------
@app.route("/api/today_tips")
def api_today_tips():
    return jsonify({
        "free": today_free_tips,
        "vip": today_vip_tips
    })

@app.route("/api/vip_results")
def api_vip_results():
    return jsonify({
        "results": vip_results_today
    })

# -------------------------------
# START SERVER
# -------------------------------
if __name__ == "__main__":
    fetch_today_matches()  # fetch immediately on start
    app.run(debug=True)

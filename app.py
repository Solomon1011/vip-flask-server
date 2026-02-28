from flask import Flask, render_template, jsonify
from datetime import datetime
import threading
import time
import requests
import os

app = Flask(__name__)

# -------------------------------
# DAILY TIPS (FALLBACK DATA)
# -------------------------------
# Used ONLY if API fails

free_tips_list = [
    ["Arsenal vs Chelsea", "Barcelona vs Sevilla", "Bayern vs Dortmund"],
    ["Man U vs Liverpool", "Real Madrid vs Valencia", "PSG vs Lyon"],
    ["Juventus vs Inter", "Atletico vs Sevilla", "Dortmund vs Bayern"]
]

vip_tips_list = [
    ["Real Madrid vs Atletico", "Liverpool vs Man City"],
    ["Barcelona vs Sociedad", "Chelsea vs Tottenham"],
    ["Bayern vs Dortmund", "Juventus vs Napoli"]
]

today_free_tips = []
today_vip_tips = []
vip_results_today = []

# -------------------------------
# TELEGRAM SETTINGS
# -------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "text": text}

    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

# -------------------------------
# FETCH REAL MATCHES FROM INTERNET
# -------------------------------
def fetch_today_matches(limit=5):
    api_key = os.getenv("FOOTBALL_API_KEY")

    if not api_key:
        print("FOOTBALL_API_KEY not set – using fallback")
        return []

    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?date={today}"
    headers = {"x-apisports-key": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
    except Exception as e:
        print("API error:", e)
        return []

    matches = []
    for game in data.get("response", [])[:limit]:
        home = game["teams"]["home"]["name"]
        away = game["teams"]["away"]["name"]
        matches.append(f"{home} vs {away}")

    return matches

# -------------------------------
# FUNCTION TO UPDATE TIPS DAILY
# -------------------------------
def update_daily_tips():
    global today_free_tips, today_vip_tips, vip_results_today

    while True:
        now = datetime.now()

        if now.hour == 9 and now.minute == 0:
            print("Updating daily tips...")

            free_matches = fetch_today_matches(5)
            vip_matches = fetch_today_matches(3)

            # If API fails, use fallback lists
            if not free_matches:
                index = now.day % len(free_tips_list)
                free_matches = free_tips_list[index]

            if not vip_matches:
                index = now.day % len(vip_tips_list)
                vip_matches = vip_tips_list[index]

            today_free_tips = free_matches
            today_vip_tips = vip_matches
            vip_results_today = [m + " ✅" for m in today_vip_tips]

            # Telegram (optional)
            send_telegram_message(
                "📌 Free Tips Today:\n" + "\n".join(today_free_tips)
            )
            send_telegram_message(
                "🔒 VIP Tips Today\nSubscribe in the app to unlock"
            )

            time.sleep(60)

        time.sleep(20)

# Start background scheduler
threading.Thread(target=update_daily_tips, daemon=True).start()

# -------------------------------
# ROUTES (WEB)
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
# API ROUTES (FOR TELEGRAM BOT)
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
    # Initial load on startup
    free = fetch_today_matches(5)
    vip = fetch_today_matches(3)

    if not free:
        index = datetime.now().day % len(free_tips_list)
        free = free_tips_list[index]

    if not vip:
        index = datetime.now().day % len(vip_tips_list)
        vip = vip_tips_list[index]

    today_free_tips = free
    today_vip_tips = vip
    vip_results_today = [m + " ✅" for m in vip]

    app.run()

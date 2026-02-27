from flask import Flask, render_template, redirect, url_for
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

# -------------------------------
# DAILY TIPS DATA
# -------------------------------

# Free Tips: 3 correct scores
free_tips_list = [
    ["Arsenal vs Chelsea 2:1", "Barcelona vs Sevilla 1:0", "Bayern vs Dortmund 3:2"],
    ["Man U vs Liverpool 1:2", "Real Madrid vs Valencia 3:1", "PSG vs Lyon 2:2"],
    ["Juventus vs Inter 1:1", "Atletico vs Sevilla 2:0", "Dortmund vs Bayern 1:3"]
]

# VIP Tips: 2 correct scores
vip_tips_list = [
    ["Real Madrid vs Atletico 2:1", "Liverpool vs Man City 1:1"],
    ["Barcelona vs Real Sociedad 3:1", "Chelsea vs Tottenham 2:1"],
    ["Bayern vs Dortmund 2:2", "Juventus vs Napoli 1:0"]
]

# Storage for today's tips
today_free_tips = []
today_vip_tips = []

# -------------------------------
# FUNCTION TO UPDATE TIPS DAILY AT 9AM
# -------------------------------
def update_daily_tips():
    global today_free_tips, today_vip_tips
    while True:
        now = datetime.now()
        # If it's exactly 9 AM
        if now.hour == 9 and now.minute == 0:
            index = now.day % len(free_tips_list)
            today_free_tips = free_tips_list[index]
            today_vip_tips = vip_tips_list[index]
            print(f"[{datetime.now()}] Today's tips updated!")
            time.sleep(60)  # Wait to avoid multiple triggers within the same minute
        time.sleep(20)

# Start the scheduler in a background thread
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

if __name__ == "__main__":
    # Initialize today's tips immediately on startup
    today_index = datetime.now().day % len(free_tips_list)
    today_free_tips = free_tips_list[today_index]
    today_vip_tips = vip_tips_list[today_index]
    app.run(debug=True)

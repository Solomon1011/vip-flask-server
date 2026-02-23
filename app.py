from flask import Flask, render_template, redirect, request, session, jsonify
import os
import json
import random
import requests
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ==========================
# LOAD USERS
# ==========================
def load_users():
    with open("users.json") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# ==========================
# HOME PAGE
# ==========================
@app.route("/")
def home():
    return render_template("index.html")

# ==========================
# FREE PREDICTIONS
# ==========================
@app.route("/free")
def free():
    match = random.choice([
        "Arsenal vs Chelsea - 1:1",
        "Barcelona vs Girona - 2:1",
        "Inter vs Milan - 1:0",
        "PSG vs Monaco - 3:1"
    ])
    return f"<h2>🔥 Free Prediction</h2><p>{match}</p>"

# ==========================
# LOGIN SYSTEM
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        data = load_users()
        for user in data["users"]:
            if user["username"] == username and user["password"] == password:
                if user["vip"] and datetime.strptime(user["expiry"], "%Y-%m-%d") > datetime.now():
                    session["user"] = username
                    return redirect("/vip")
                else:
                    return "VIP expired. Please subscribe."

        return "Invalid login"

    return '''
    <h2>VIP Login</h2>
    <form method="POST">
        <input name="username" placeholder="Username"><br><br>
        <input name="password" type="password" placeholder="Password"><br><br>
        <button type="submit">Login</button>
    </form>
    '''

# ==========================
# VIP PAGE
# ==========================
@app.route("/vip")
def vip():
    if "user" not in session:
        return redirect("/login")

    match = random.choice([
        "VIP: Arsenal vs Chelsea - 2:0",
        "VIP: Real Madrid vs Sevilla - 3:1",
        "VIP: Man City vs Liverpool - 2:1"
    ])

    return f"<h2>👑 VIP Prediction</h2><p>{match}</p>"

# ==========================
# PAYSTACK PAYMENT
# ==========================
@app.route("/pay")
def pay():
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET')}",
        "Content-Type": "application/json"
    }

    data = {
        "email": "customer@email.com",
        "amount": 500000  # 5000 NGN
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()

# ==========================
# TELEGRAM AUTO POST
# ==========================
def daily_prediction():
    match = random.choice([
        "VIP: Arsenal vs Chelsea - 2:0",
        "VIP: Real Madrid vs Sevilla - 3:1"
    ])

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = "@daily_correct_score1"

    if token:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": match}
        )

scheduler = BackgroundScheduler()
scheduler.add_job(daily_prediction, "cron", hour=9)
scheduler.start()

# ==========================
# LOGOUT
# ==========================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ==========================
# RUN SERVER
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

from flask import Flask, request, redirect, session
import requests
import random
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = "supersecret"

# -------------------------------
# USERS DATABASE FUNCTIONS
# -------------------------------
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {"users":[]}

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

def is_vip(username):
    users = load_users()["users"]
    for u in users:
        if u["username"] == username:
            if u["vip"] and datetime.strptime(u["expiry"], "%Y-%m-%d") >= datetime.today():
                return True
    return False

# -------------------------------
# GLOBAL PREDICTIONS
# -------------------------------
free_tip = "Loading..."
vip_match = "Loading..."
vip_score = "Loading..."

# -------------------------------
# HOME PAGE
# -------------------------------
@app.route("/")
def home():
    return """
    <h1>SOLO CORRECT SCORE</h1>
    <h3>Select Plan</h3>
    <a href='/free'>Free Tips</a><br><br>
    <a href='/vip'>VIP Match</a><br><br>
    <a href='https://wa.me/2349018025267'>Customer Service</a><br><br>
    <a href='https://t.me/daily_correct_score1'>Join Telegram</a>
    """

# -------------------------------
# FREE TIPS PAGE
# -------------------------------
@app.route("/free")
def free():
    return f"<h2>FREE MATCH</h2><p>{free_tip}</p>"

# -------------------------------
# VIP LOGIN PAGE
# -------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = load_users()["users"]
        for u in users:
            if u["username"] == username and u["password"] == password:
                session["username"] = username
                return redirect("/vip")
        return "Invalid username or password"
    return '''
    <h2>Login</h2>
    <form method="post">
      Username: <input name="username"><br><br>
      Password: <input name="password" type="password"><br><br>
      <button type="submit">Login</button>
    </form>
    '''

# -------------------------------
# VIP PAGE (PROTECTED)
# -------------------------------
@app.route("/vip")
def vip():
    if "username" not in session:
        return redirect("/login")
    if not is_vip(session["username"]):
        return "You are not a VIP or your subscription expired. Contact admin."
    
    return f"<h1>{vip_match}</h1><h2>{vip_score}</h2>"

# -------------------------------
# GENERATE DAILY MATCH
# -------------------------------
@app.route("/generate")
def generate():
    global free_tip, vip_match, vip_score

    teams = ["Arsenal vs Chelsea", "Barcelona vs Madrid", "Man U vs Liverpool"]
    scores = ["1-0", "2-1", "2-0", "3-1"]

    free_tip = random.choice(teams)
    vip_match = random.choice(teams)
    vip_score = random.choice(scores)

    message = f"VIP MATCH:\n{vip_match}\nCorrect Score: {vip_score}"

    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHANNEL = "@daily_correct_score1"

    if TELEGRAM_BOT_TOKEN:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(telegram_url, data={
            "chat_id": TELEGRAM_CHANNEL,
            "text": message
        })

    return "Match Generated & Posted"

# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

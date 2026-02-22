from flask import Flask
import random
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

free_tip = "Loading..."
vip_match = "Loading..."
vip_score = "Loading..."

@app.route("/")
def home():
    return """
    <h1>SOLO CORRECT SCORE</h1>
    <a href='/free'>Free Tips</a><br><br>
    <a href='/vip'>VIP Match</a><br><br>
    <a href='https://wa.me/2349018025267'>Customer Service</a><br><br>
    <a href='https://t.me/daily_correct_score1'>Join Telegram</a>
    """

@app.route("/free")
def free():
    return f"<h2>FREE MATCH</h2><p>{free_tip}</p>"

@app.route("/vip")
def vip():
    return f"<h1>{vip_match}</h1><h2>{vip_score}</h2>"

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

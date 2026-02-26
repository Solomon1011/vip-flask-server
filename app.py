from flask import Flask, render_template, redirect, request
import json
from datetime import datetime

app = Flask(__name__)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- FREE ----------------
@app.route("/free")
def free():
    with open("tips.json") as f:
        data = json.load(f)
    return render_template("free.html", tips=data["free"])

# ---------------- SUBSCRIBE ----------------
@app.route("/subscribe")
def subscribe():
    return render_template("subscribe.html")

# ---------------- VIP (TEST VERSION) ----------------
@app.route("/vip")
def vip():
    with open("tips.json") as f:
        data = json.load(f)
    return render_template("vip.html", tips=data["vip"])

if __name__ == "__main__":
    app.run()

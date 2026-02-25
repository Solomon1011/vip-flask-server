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
    tips = [
        {"match": "Arsenal vs Chelsea", "tip": "Over 2.5 Goals"}
    ]
    return render_template("free.html", tips=tips)

# ---------------- SUBSCRIBE ----------------
@app.route("/subscribe")
def subscribe():
    return render_template("subscribe.html")

# ---------------- VIP (TEST VERSION) ----------------
@app.route("/vip")
def vip():
    return render_template("vip.html")

if __name__ == "__main__":
    app.run()

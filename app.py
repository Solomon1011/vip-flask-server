import os
import requests
from flask import jsonify, session
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
    if not session.get("vip"):
        return redirect("/subscribe")

    with open("tips.json") as f:
        data = json.load(f)

    return render_template("vip.html", tips=data["vip"])

if __name__ == "__main__":
    app.run()
@app.route("/verify-payment/<reference>")
def verify_payment(reference):
    secret = os.getenv("PAYSTACK_SECRET_KEY")

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {secret}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    if data["status"] and data["data"]["status"] == "success":
        session["vip"] = True
        return redirect("/vip")

    return "Payment failed"

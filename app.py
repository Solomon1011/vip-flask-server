import os
import json
from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import requests

app = Flask(__name__, template_folder="templates", static_folder="static")

PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")

# -----------------------------
# HOME
# -----------------------------

@app.route("/")
def home():
    return render_template("home.html")

# -----------------------------
# FREE PAGE
# -----------------------------

@app.route("/free")
def free():
    return render_template("free.html")

# -----------------------------
# SUBSCRIBE PAGE
# -----------------------------

@app.route("/subscribe-plan")
def subscribe_plan():
    return render_template("subscribe.html")

# -----------------------------
# PAYSTACK PAYMENT
# -----------------------------

@app.route("/subscribe/<plan>")
def subscribe(plan):

    amount = 0

    if plan == "weekly":
        amount = 75500   # ₦755
    elif plan == "monthly":
        amount = 275500  # ₦2755
    else:
        return "Invalid plan"

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": "customer@email.com",  # temporary demo email
        "amount": amount
    }

    response = requests.post(url, json=data, headers=headers).json()

    if response.get("status"):
        return redirect(response["data"]["authorization_url"])
    else:
        return "Payment initialization failed"

# -----------------------------
# WEBHOOK (OPTIONAL)
# -----------------------------

@app.route("/paystack/webhook", methods=["POST"])
def webhook():
    return "", 200


if __name__ == "__main__":
    app.run()

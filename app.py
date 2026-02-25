import os
import json
import requests
from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime, timedelta

app = Flask(__name__)

PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")

USERS_FILE = "users.json"

# ---------------- HOME (redirect to subscribe) ----------------
@app.route("/")
def home():
    return redirect(url_for("subscribe"))

# ---------------- SUBSCRIBE PAGE ----------------
@app.route("/subscribe")
def subscribe():
    return render_template("subscribe.html")

# ---------------- VERIFY PAYMENT ----------------
@app.route("/verify/<reference>")
def verify(reference):
    try:
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
        response = requests.get(url, headers=headers).json()

        if response.get("status") and response["data"]["status"] == "success":
            email = response["data"]["customer"]["email"]

            # Save VIP user (7 days)
            expiry = datetime.now() + timedelta(days=7)
            save_user(email, expiry)

            return redirect(url_for("vip", email=email))
        else:
            return "Payment verification failed."

    except Exception as e:
        return f"Error verifying payment: {str(e)}"

# ---------------- SAVE USER ----------------
def save_user(email, expiry):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    except:
        users = []

    users = [u for u in users if u["email"] != email]
    users.append({
        "email": email,
        "expiry": expiry.strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- VIP PAGE ----------------
@app.route("/vip")
def vip():
    email = request.args.get("email")

    if not email:
        return redirect(url_for("subscribe"))

    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    except:
        users = []

    user = next((u for u in users if u["email"] == email), None)

    if not user:
        return redirect(url_for("subscribe"))

    expiry = datetime.strptime(user["expiry"], "%Y-%m-%d %H:%M:%S")

    if datetime.now() > expiry:
        return "Your VIP subscription has expired."

    vip_tips = [
        {"match": "Man City vs Liverpool", "tip": "Both Teams To Score"},
        {"match": "Barcelona vs Atletico", "tip": "Over 3.5 Goals"}
    ]

    return render_template("vip.html", tips=vip_tips)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()

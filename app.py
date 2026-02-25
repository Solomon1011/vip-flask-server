
import os
import json
import requests
from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime, timedelta

app = Flask(__name__)

# Paystack keys from environment variables
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY")

USERS_FILE = "users.json"  # Stores subscribers

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- FREE TIPS ----------------
@app.route("/free")
def free():
    free_tips = [
        {"match": "Arsenal vs Chelsea", "tip": "Over 2.5 Goals"},
        {"match": "Real Madrid vs Sevilla", "tip": "Real Madrid Win"}
    ]
    return render_template("free.html", tips=free_tips)

# ---------------- SUBSCRIBE PAGE ----------------
@app.route("/subscribe-plan")
def subscribe_plan():
    return render_template("subscribe.html", public_key=PAYSTACK_PUBLIC_KEY)

# ---------------- VERIFY PAYMENT ----------------
@app.route("/verify/<reference>")
def verify(reference):
    try:
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
        response = requests.get(url, headers=headers).json()

        if response.get("status") and response["data"]["status"] == "success":
            email = response["data"]["customer"]["email"]
            amount = response["data"]["amount"]

            if amount == 745000:
                plan = "weekly"
            elif amount == 2755000:
                plan = "monthly"
            else:
                return "Invalid payment amount"

            # Save user subscription
            save_user(email, plan)

            return redirect(url_for("vip", email=email))

        return "Payment not verified"
    except Exception as e:
        return f"Error verifying payment: {str(e)}"

# ---------------- SAVE USER ----------------
def save_user(email, plan):
    expiry = None
    if plan == "weekly":
        expiry = datetime.now() + timedelta(days=7)
    elif plan == "monthly":
        expiry = datetime.now() + timedelta(days=30)

    user_data = {
        "email": email,
        "plan": plan,
        "expiry": expiry.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    except:
        users = []

    # Remove old entry for same email
    users = [u for u in users if u["email"] != email]

    users.append(user_data)

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- CHECK SUBSCRIPTION ----------------
def has_active_subscription(email):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    except:
        return False

    for user in users:
        if user["email"] == email:
            expiry = datetime.strptime(user["expiry"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() < expiry:
                return True

    return False

# ---------------- VIP ----------------
@app.route("/vip")
def vip():
    try:
        email = request.args.get("email")

        if not email:
            return redirect(url_for("subscribe_plan"))

        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        except:
            users = []

        user = None
        for u in users:
            if u["email"] == email:
                user = u
                break

        if not user:
            return redirect(url_for("subscribe_plan"))

        expiry = datetime.strptime(user["expiry"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expiry:
            return "Your VIP subscription has expired. <a href='/subscribe-plan'>Subscribe again</a>"

        vip_tips = [
            {"match": "Man City vs Liverpool", "tip": "Both Teams Score"},
            {"match": "Barcelona vs Atletico", "tip": "Over 3.5 Goals"}
        ]

        return render_template("vip.html", tips=vip_tips)

    except Exception as e:
        return f"An error occurred: {str(e)}"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)

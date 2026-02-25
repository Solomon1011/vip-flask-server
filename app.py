import os
import json
from flask import Flask, render_template, redirect, request, url_for
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY")

USERS_FILE = "users.json"

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

    users.append(user_data)

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ---------------- CHECK ACCESS ----------------
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


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- SUBSCRIBE PAGE ----------------
@app.route("/subscribe-plan")
def subscribe_plan():
    return render_template("subscribe.html", public_key=PAYSTACK_PUBLIC_KEY)


# ---------------- VERIFY PAYMENT ----------------
@app.route("/verify/<reference>")
def verify(reference):

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}

    response = requests.get(url, headers=headers).json()

    if response["data"]["status"] == "success":

        email = response["data"]["customer"]["email"]
        amount = response["data"]["amount"]

        # determine plan from amount
        if amount == 745000:
            plan = "weekly"
        elif amount == 2755000:
            plan = "monthly"
        else:
            return "Invalid payment amount"

        save_user(email, plan)

        return redirect(url_for("vip"))

    return "Payment not verified"


# ---------------- VIP ----------------
@app.route("/vip")
def vip():

    email = request.args.get("email")

    if not email:
        return redirect(url_for("subscribe_plan"))

    if not has_active_subscription(email):
        return redirect(url_for("subscribe_plan"))

    return render_template("vip.html")


if __name__ == "__main__":
    app.run()

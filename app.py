from flask import Flask, render_template, request, redirect, session, url_for
import requests
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"

PAYSTACK_SECRET_KEY = "YOUR_PAYSTACK_SECRET_KEY"
BASE_URL = "https://your-render-url.onrender.com"

USERS_FILE = "users.json"


# -----------------------
# Helper Functions
# -----------------------

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({"users": []}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# -----------------------
# Routes
# -----------------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/free")
def free():
    return render_template("free.html")


# -----------------------
# Register
# -----------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        data = load_users()

        for user in data["users"]:
            if user["email"] == email:
                return "Email already registered"

        data["users"].append({
            "email": email,
            "password": password,
            "vip": False,
            "expiry": ""
        })

        save_users(data)
        session["user"] = email
        return redirect("/subscribe-plan")

    return render_template("register.html")


# -----------------------
# Login
# -----------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        data = load_users()

        for user in data["users"]:
            if user["email"] == email and user["password"] == password:
                session["user"] = email
                return redirect("/vip")

        return "Invalid login"

    return render_template("login.html")


# -----------------------
# VIP Page
# -----------------------

@app.route("/vip")
def vip():
    if "user" not in session:
        return redirect("/login")

    email = session["user"]
    data = load_users()

    for user in data["users"]:
        if user["email"] == email:
            if user["vip"] and datetime.strptime(user["expiry"], "%Y-%m-%d") > datetime.now():
                return render_template("vip.html")
            else:
                return redirect("/subscribe-plan")

    return redirect("/register")


# -----------------------
# Subscription Page
# -----------------------

@app.route("/subscribe-plan")
def subscribe_plan():
    if "user" not in session:
        return redirect("/register")

    return render_template("subscribe.html")


# -----------------------
# Paystack Payment
# -----------------------

@app.route("/subscribe/<plan>")
def subscribe(plan):
    if "user" not in session:
        return redirect("/register")

    email = session["user"]

    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    usd_to_ngn = 1000

    if plan == "weekly":
        amount = int(7.55 * usd_to_ngn * 100)
        days = 7
    elif plan == "monthly":
        amount = int(27.55 * usd_to_ngn * 100)
        days = 30
    else:
        return "Invalid plan"

    data = {
        "email": email,
        "amount": amount,
        "callback_url": f"{BASE_URL}/verify",
        "metadata": {
            "email": email,
            "days": days
        }
    }

    response = requests.post(url, json=data, headers=headers).json()

    if response.get("status"):
        return redirect(response["data"]["authorization_url"])
    else:
        return "Payment failed"


# -----------------------
# Verify Payment
# -----------------------

@app.route("/verify")
def verify():
    reference = request.args.get("reference")

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers).json()

    if response["data"]["status"] == "success":
        email = response["data"]["metadata"]["email"]
        days = response["data"]["metadata"]["days"]

        data = load_users()

        for user in data["users"]:
            if user["email"] == email:
                user["vip"] = True
                user["expiry"] = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        save_users(data)

        return redirect("/vip")

    return "Verification failed"


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

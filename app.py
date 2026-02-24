from flask import Flask, request, redirect, session
import requests
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"

PAYSTACK_SECRET_KEY = "YOUR_PAYSTACK_SECRET_KEY"

USERS_FILE = "users.json"


# -------------------------
# Helper Functions
# -------------------------

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({"users": []}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# -------------------------
# Homepage
# -------------------------

@app.route("/")
def home():
    return """
    <h1>🔥 SOLO PREDICTION APP 🔥</h1>
    <br>
    <a href='/free'>Free Tips</a><br><br>
    <a href='/vip'>VIP Match</a><br><br>
    <a href='https://wa.me/2349018025267'>WhatsApp</a><br><br>
    <a href='https://t.me/YOUR_TELEGRAM_LINK'>Telegram</a><br><br>
    """


# -------------------------
# Free Tips
# -------------------------

@app.route("/free")
def free():
    return """
    <h2>Free Tips</h2>
    <p>Barcelona vs Sevilla - Over 2.5</p>
    <a href='/'>Back Home</a>
    """


# -------------------------
# Register
# -------------------------

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

    return """
    <h2>Create Account</h2>
    <form method='POST'>
        <input type='email' name='email' placeholder='Enter Gmail' required><br><br>
        <input type='password' name='password' placeholder='Create Password' required><br><br>
        <button type='submit'>Sign Up</button>
    </form>
    """


# -------------------------
# Login
# -------------------------

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

    return """
    <h2>Login</h2>
    <form method='POST'>
        <input type='email' name='email' placeholder='Enter Gmail' required><br><br>
        <input type='password' name='password' placeholder='Password' required><br><br>
        <button type='submit'>Login</button>
    </form>
    """


# -------------------------
# VIP Page
# -------------------------

@app.route("/vip")
def vip():
    if "user" not in session:
        return redirect("/login")

    email = session["user"]
    data = load_users()

    for user in data["users"]:
        if user["email"] == email:
            if user["vip"] and datetime.strptime(user["expiry"], "%Y-%m-%d") > datetime.now():
                return """
                <h2>👑 VIP Predictions</h2>
                <p>Arsenal vs Chelsea - 2:0</p>
                <a href='/'>Back Home</a>
                """
            else:
                return redirect("/subscribe-plan")

    return redirect("/register")


# -------------------------
# Subscription Plans
# -------------------------

@app.route("/subscribe-plan")
def subscribe_plan():
    if "user" not in session:
        return redirect("/register")

    return """
    <h2>Select VIP Plan</h2>
    <a href='/subscribe/weekly'>Weekly - $7.55</a><br><br>
    <a href='/subscribe/monthly'>Monthly - $27.55</a>
    """


# -------------------------
# Paystack Payment
# -------------------------

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
        "callback_url": "https://your-app-url.onrender.com/verify",
        "metadata": {
            "email": email,
            "days": days
        }
    }

    response = requests.post(url, json=data, headers=headers).json()

    if response.get("status"):
        return redirect(response["data"]["authorization_url"])
    else:
        return "Payment initialization failed"


# -------------------------
# Verify Payment
# -------------------------

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

    return "Payment verification failed"


# -------------------------
# Logout
# -------------------------

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# -------------------------
# Run App
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)

import os
import json
from flask import Flask, render_template, request, redirect, session, url_for
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Paystack and Telegram environment
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")  # Set in Render env
TELEGRAM_CHANNEL = "@daily_correct_score1"

USERS_FILE = "users.json"

# Load or create users file
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({"users": []}, f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f)

# Free tip (static for demo)
free_tip = "Manchester United vs Chelsea: 2-1"

# ----------------------------------------
# Routes
# ----------------------------------------

@app.route("/")
def home():
    return render_template("home.html")

# Register user with Gmail
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        users = load_users()
        for u in users["users"]:
            if u["email"] == email:
                return "Email already registered"
        users["users"].append({"email": email, "vip_until": None})
        save_users(users)
        session["user"] = email
        return redirect(url_for("home"))
    return render_template("register.html")

# Login (simple)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        users = load_users()
        for u in users["users"]:
            if u["email"] == email:
                session["user"] = email
                return redirect(url_for("home"))
        return "Email not found. Please register."
    return render_template("login.html")

# Free Tips
@app.route("/free")
def free():
    return render_template("free.html", tip=free_tip)

# VIP Match
@app.route("/vip")
def vip():
    if "user" not in session:
        return redirect(url_for("login"))
    users = load_users()
    for u in users["users"]:
        if u["email"] == session["user"]:
            if u["vip_until"] and datetime.utcnow() < datetime.fromisoformat(u["vip_until"]):
                return render_template("vip.html", vip_match="Manchester United vs Chelsea: 2-1")
            else:
                return redirect(url_for("subscribe_plan"))
    return redirect(url_for("register"))

# Subscription Plan page
@app.route("/subscribe-plan")
def subscribe_plan():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("subscribe.html")

# Paystack payment route
@app.route("/subscribe/<plan>")
def subscribe(plan):
    if "user" not in session:
        return redirect(url_for("login"))
    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}", "Content-Type": "application/json"}
    amount = 0
    days = 0
    if plan=="weekly":
        amount = 75500  # NGN 755 (Paystack uses kobo)
        days = 7
    elif plan=="monthly":
        amount = 275500
        days = 30
    else:
        return "Invalid plan"
    data = {"email": session["user"], "amount": amount, "metadata": {"days":days}}
    response = requests.post(url, json=data, headers=headers).json()
    return redirect(response["data"]["authorization_url"])

# Webhook for Paystack (set webhook URL on Paystack dashboard)
@app.route("/paystack/webhook", methods=["POST"])
def paystack_webhook():
    event = request.json
    if event["event"] == "charge.success":
        email = event["data"]["customer"]["email"]
        days = event["data"]["metadata"]["days"]
        users = load_users()
        for u in users["users"]:
            if u["email"] == email:
                u["vip_until"] = (datetime.utcnow() + timedelta(days=days)).isoformat()
        save_users(users)
    return "", 200

if __name__ == "__main__":
    app.run()


import os
import json
from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime, timedelta
import requests

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "supersecretkey"

PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")

USERS_FILE = "users.json"

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({"users": []}, f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        users = load_users()
        for u in users["users"]:
            if u["email"] == email:
                return "Email already exists"
        users["users"].append({"email": email, "vip_until": None})
        save_users(users)
        session["user"] = email
        return redirect("/")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        users = load_users()
        for u in users["users"]:
            if u["email"] == email:
                session["user"] = email
                return redirect("/")
        return "User not found"
    return render_template("login.html")

@app.route("/free")
def free():
    return render_template("free.html")

@app.route("/vip")
def vip():
    if "user" not in session:
        return redirect("/login")
    users = load_users()
    for u in users["users"]:
        if u["email"] == session["user"]:
            if u["vip_until"] and datetime.utcnow() < datetime.fromisoformat(u["vip_until"]):
                return render_template("vip.html")
            else:
                return redirect("/subscribe-plan")
    return redirect("/")

@app.route("/subscribe-plan")
def subscribe_plan():
    return render_template("subscribe.html")

@app.route("/subscribe/<plan>")
def subscribe(plan):
    if "user" not in session:
        return redirect("/login")

    amount = 0
    days = 0

    if plan == "weekly":
        amount = 75500
        days = 7
    elif plan == "monthly":
        amount = 275500
        days = 30
    else:
        return "Invalid plan"

    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": session["user"],
        "amount": amount,
        "metadata": {"days": days}
    }

    response = requests.post(url, json=data, headers=headers).json()
    return redirect(response["data"]["authorization_url"])

@app.route("/paystack/webhook", methods=["POST"])
def webhook():
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

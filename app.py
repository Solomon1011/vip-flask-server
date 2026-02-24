
from flask import Flask, render_template, request, redirect, session
import os, json, requests
from datetime import datetime, timedelta
import threading, time

# ---------------------------
# APP SETUP
# ---------------------------
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Load environment variables
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")

# Users database file
USERS_FILE = "users.json"

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({"users":[]}, f)
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Post message to Telegram
def post_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHANNEL, "text": message}
    requests.post(url, json=payload)

# ---------------------------
# HOME PAGE
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------------------
# FREE PREDICTIONS
# ---------------------------
@app.route("/free")
def free():
    match = "Arsenal vs Chelsea - 1:1"
    return f"<h2>🔥 Free Prediction</h2><p>{match}</p>"

# ---------------------------
# LOGIN
# ---------------------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        data = load_users()
        for user in data["users"]:
            if user["username"] == username and user["password"] == password:
                # Check VIP expiry
                if user.get("vip") and datetime.strptime(user.get("expiry","2000-01-01"), "%Y-%m-%d") > datetime.now():
                    session["user"] = username
                    return redirect("/vip")
                else:
                    return "VIP expired. Please renew subscription."
        return "Invalid username or password"
    return '''
    <h2>VIP Login</h2>
    <form method="POST">
        <input name="username" placeholder="Username"><br><br>
        <input name="password" type="password" placeholder="Password"><br><br>
        <button type="submit">Login</button>
    </form>
    '''

# ---------------------------
# VIP PAGE
# ---------------------------
@app.route("/vip")
def vip():
    if "user" not in session:
        return redirect("/login")
    match = "VIP: Arsenal vs Chelsea - 2:0"
    # Post daily prediction to Telegram
    post_to_telegram(f"Daily VIP Prediction:\n{match}")
    return f"<h2>👑 VIP Prediction</h2><p>{match}</p>"

# ---------------------------
# SUBSCRIBE / PAYMENT ROUTE
# ---------------------------
@app.route("/subscribe/<username>/<plan>")
def subscribe(username, plan):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}", "Content-Type": "application/json"}
    if plan=="weekly":
        amount = 75500
        days = 7
    elif plan=="monthly":
        amount = 275500
        days = 30
    else:
        return "Invalid plan"
    data = {"email": f"{username}@gmail.com", "amount": amount, "metadata": {"username": username,"days":days}}
    response = requests.post(url, json=data, headers=headers).json()
    return redirect(response["data"]["authorization_url"])

# ---------------------------
# PAYSTACK WEBHOOK
# ---------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    event = request.json
    if event.get("event")=="charge.success":
        username = event["data"]["metadata"]["username"]
        days = int(event["data"]["metadata"]["days"])
        data = load_users()
        found = False
        for user in data["users"]:
            if user["username"]==username:
                user["vip"]=True
                current_expiry = datetime.strptime(user.get("expiry","2000-01-01"), "%Y-%m-%d")
                if current_expiry>datetime.now():
                    new_expiry = current_expiry + timedelta(days=days)
                else:
                    new_expiry = datetime.now() + timedelta(days=days)
                user["expiry"] = new_expiry.strftime("%Y-%m-%d")
                found=True
        if not found:
            data["users"].append({"username": username, "password":"default123", "vip":True, "expiry": (datetime.now()+timedelta(days=days)).strftime("%Y-%m-%d")})
        save_users(data)
    return "",200

# ---------------------------
# ADMIN DASHBOARD
# ---------------------------
@app.route("/admin")
def admin():
    data = load_users()
    html = "<h2>All Users</h2><table border=1 cellpadding=8><tr><th>Username</th><th>VIP</th><th>Expiry</th></tr>"
    for user in data["users"]:
        html += f"<tr><td>{user['username']}</td><td>{user.get('vip')}</td><td>{user.get('expiry')}</td></tr>"
    html += "</table>"
    return html

# ---------------------------
# LOGOUT
# ---------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ---------------------------
# RUN SERVER
# ---------------------------
if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)

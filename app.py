import json
from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime, timedelta
import requests
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")
USERS_FILE = "users.json"

# ---------------- SUBSCRIBE PAGE ----------------
@app.route("/subscribe-plan")
def subscribe_plan():
    return render_template("subscribe.html")

# ---------------- SAFE PAYSTACK VERIFY ----------------
@app.route("/verify/<reference>")
def verify(reference):
    try:
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
        r = requests.get(url, headers=headers)
        response = r.json()

        # Check payment success safely
        if isinstance(response, dict) and response.get("status") and response["data"]["status"] == "success":
            email = response["data"]["customer"]["email"]
            save_user(email)
            # Redirect directly to VIP page with email
            return redirect(url_for("vip", email=email))
        else:
            return "Payment failed or invalid response"

    except Exception as e:
        return f"Error verifying payment: {str(e)}"

# ---------------- SAVE VIP USER ----------------
def save_user(email):
    expiry = datetime.now() + timedelta(days=7)  # weekly plan
    user_data = {"email": email, "expiry": expiry.strftime("%Y-%m-%d %H:%M:%S")}

    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    except:
        users = []

    # remove old entry if exists
    users = [u for u in users if u["email"] != email]
    users.append(user_data)

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- VIP PAGE ----------------
@app.route("/vip")
def vip():
    email = request.args.get("email")
    if not email:
        return redirect(url_for("subscribe_plan"))

    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    except:
        users = []

    # check user exists
    user = next((u for u in users if u["email"] == email), None)
    if not user:
        return redirect(url_for("subscribe_plan"))

    # check expiry
    expiry = datetime.strptime(user["expiry"], "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expiry:
        return "Your VIP subscription has expired. <a href='/subscribe-plan'>Subscribe again</a>"

    # VIP Tips
    vip_tips = [
        {"match": "Man City vs Liverpool", "tip": "Both Teams Score"},
        {"match": "Barcelona vs Atletico", "tip": "Over 3.5 Goals"}
    ]

    return render_template("vip.html", tips=vip_tips)

if __name__ == "__main__":
    app.run(debug=True)

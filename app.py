import os
import json
import requests
from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime, timedelta

app = Flask(__name__)

# Paystack keys (set in Render environment)
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY")

USERS_FILE = "users.json"  # Stores VIP users


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
        import json
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
        r = requests.get(url, headers=headers)

        # Try to parse JSON safely
        try:
            response = r.json()
        except Exception as e:
            return f"Could not parse JSON from Paystack: {str(e)}\nRaw response: {r.text}"

        # DEBUG: print full response to logs
        print("Paystack Response:", json.dumps(response, indent=4))

        # Make sure it's a dict
        if not isinstance(response, dict):
            return f"Unexpected response format: {response}"

        # Check API status
        if not response.get("status"):
            return f"Payment verification failed: {response}"

        # Get 'data' safely
        data = response.get("data")
        if not isinstance(data, dict):
            return f"Invalid data format from Paystack: {data}"

        if data.get("status") != "success":
            return f"Payment not successful: {data}"

        # Get customer email safely
        customer = data.get("customer")
        if not isinstance(customer, dict):
            return f"Invalid customer info: {customer}"

        email = customer.get("email")
        amount = data.get("amount")

        if not email or not amount:
            return f"Missing email or amount: {data}"

        # Determine plan
        if amount == 745000:
            plan = "weekly"
        elif amount == 2755000:
            plan = "monthly"
        else:
            return f"Unknown amount: {amount}"

        # Save VIP user
        save_user(email, plan)

        # Redirect to VIP page
        return redirect(url_for("vip", email=email))

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

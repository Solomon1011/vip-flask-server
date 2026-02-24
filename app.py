import os
from flask import Flask, render_template, redirect, request, url_for
import requests

app = Flask(__name__, template_folder="templates", static_folder="static")

PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY")

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("home.html")

# ---------------- FREE MATCH ----------------

@app.route("/free")
def free():
    return render_template("free.html")

# ---------------- VIP PAGE ----------------

@app.route("/vip")
def vip():
    return render_template("vip.html")

# ---------------- SUBSCRIBE PAGE ----------------

@app.route("/subscribe-plan")
def subscribe_plan():
    return render_template("subscribe.html", public_key=PAYSTACK_PUBLIC_KEY)

# ---------------- VERIFY PAYMENT ----------------

@app.route("/verify/<reference>")
def verify(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers).json()

    if response["data"]["status"] == "success":
        return redirect("/vip")
    else:
        return "Payment not verified"

if __name__ == "__main__":
    app.run()

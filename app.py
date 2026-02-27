from flask import Flask, render_template
from datetime import datetime
import threading
import time
from telegram import Bot

app = Flask(__name__)

# -------------------------------
# DAILY TIPS DATA
# -------------------------------

# Free Tips: 3 correct scores
free_tips_list = [
    ["Arsenal vs Chelsea 2:1", "Barcelona vs Sevilla 1:0", "Bayern vs Dortmund 3:2"],
    ["Man U vs Liverpool 1:2", "Real Madrid vs Valencia 3:1", "PSG vs Lyon 2:2"],
    ["Juventus vs Inter 1:1", "Atletico vs Sevilla 2:0", "Dortmund vs Bayern 1:3"]
]

# VIP Tips: 2 correct scores
vip_tips_list = [
    ["Real Madrid vs Atletico 2:1", "Liverpool vs Man City 1:1"],
    ["Barcelona vs Real Sociedad 3:1", "Chelsea vs Tottenham 2:1"],
    ["Bayern vs Dortmund 2:2", "Juventus vs Napoli 1:0"]
]

# Storage for today's tips and VIP results
today_free_tips = []
today_vip_tips = []
vip_results_today = []

# -------------------------------
# TELEGRAM SETTINGS
# -------------------------------
TELEGRAM_BOT_TOKEN = "8632563857:AAFUx-Aj1n8wf2JWnvR9YeRVRpidnPfTJMY"       # Replace with your bot token
TELEGRAM_CHANNEL_ID = "@YourChannelName"    # Replace with your channel username
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# -------------------------------
# FUNCTION TO UPDATE TIPS DAILY AT 9AM
# -------------------------------
def update_daily_tips():
    global today_free_tips, today_vip_tips, vip_results_today
    while True:
        now = datetime.now()
        # Update tips at exactly 9 AM
        if now.hour == 9 and now.minute == 0:
            index = now.day % len(free_tips_list)
            today_free_tips = free_tips_list[index]
            today_vip_tips = vip_tips_list[index]

            # VIP results (all wins for demo)
            vip_results_today = [tip + " ✅" for tip in today_vip_tips]

            print(f"[{datetime.now()}] Today's tips and VIP results updated!")

            # -------------------------------
            # POST TO TELEGRAM
            # -------------------------------
            try:
                # Free Tips
                free_message = "📌 Free Tips Today:\n" + "\n".join(today_free_tips)
                bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=free_message)

                # VIP Tips (locked)
                vip_message = "🔒 VIP Tips Today: (Subscribe to unlock in the app!)"
                bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=vip_message)

            except Exception as e:
                print("Error sending to Telegram:", e)

            # Wait 60 seconds to prevent duplicate posts in the same minute
            time.sleep(60)
        time.sleep(20)

# Start scheduler in a background thread
threading.Thread(target=update_daily_tips, daemon=True).start()

# -------------------------------
# ROUTES
# -------------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/free")
def free():
    return render_template("free.html", tips=today_free_tips)

@app.route("/subscribe")
def subscribe():
    return render_template("vip.html", tips=today_vip_tips)

@app.route("/vip_results")
def vip_results():
    return render_template("vip_results.html", results=vip_results_today)

# -------------------------------
# START SERVER
# -------------------------------
if __name__ == "__main__":
    # Initialize today's tips immediately
    today_index = datetime.now().day % len(free_tips_list)
    today_free_tips = free_tips_list[today_index]
    today_vip_tips = vip_tips_list[today_index]
    vip_results_today = [tip + " ✅" for tip in today_vip_tips]

    app.run(debug=True)

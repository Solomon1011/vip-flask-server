
import os
import requests
from datetime import datetime

# -------------------------------
# ENV VARIABLES
# -------------------------------
API_KEY = os.getenv("YOUR_API_KEY")  # your live match API key on Render
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

if not API_KEY:
    print("❌ API_KEY not set!")
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
    print("❌ Telegram not configured!")

# -------------------------------
# FUNCTIONS
# -------------------------------
def fetch_today_matches():
    """Fetch today's matches from API"""
    url = f"https://api.example.com/matches/today?api_key={API_KEY}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        free_tips = []
        vip_tips = []
        for match in data.get("matches", []):
            free_tips.append(f"{match['home']} vs {match['away']} {match['free_score']}")
            vip_tips.append(f"{match['home']} vs {match['away']} {match['vip_score']}")
        return free_tips, vip_tips
    except Exception as e:
        print("❌ Error fetching matches:", e)
        # fallback to hardcoded
        free_tips = [
            "Arsenal vs Chelsea 2:1",
            "Barcelona vs Sevilla 1:0",
            "Bayern vs Dortmund 3:2"
        ]
        vip_tips = [
            "Real Madrid vs Atletico 2:1",
            "Liverpool vs Man City 1:1"
        ]
        return free_tips, vip_tips

def send_telegram_message(text):
    """Send message to Telegram channel"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text
    }
    try:
        requests.post(url, json=payload, timeout=10)
        print("✅ Telegram message sent!")
    except Exception as e:
        print("❌ Telegram error:", e)

# -------------------------------
# MAIN DAILY POST
# -------------------------------
if __name__ == "__main__":
    free_tips, vip_tips = fetch_today_matches()
    vip_results = [tip + " ✅" for tip in vip_tips]

    # Send messages
    send_telegram_message("📌 Free Tips Today:\n" + "\n".join(free_tips))
    send_telegram_message("🔒 VIP Tips Today (Subscribe in the app to unlock!)")
    send_telegram_message("📈 VIP Results:\n" + "\n".join(vip_results))

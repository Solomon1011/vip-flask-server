
import os
import requests
from datetime import datetime

# -------------------------------
# ENV VARIABLES (RENDER / GITHUB)
# -------------------------------
API_KEY = os.getenv("API_FOOTBALL_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

API_URL = "https://v3.football.api-sports.io/fixtures"

# -------------------------------
# FETCH TODAY MATCHES (UTC SAFE)
# -------------------------------
def fetch_today_matches():
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")

        headers = {
            "x-apisports-key": API_KEY
        }

        response = requests.get(
            f"{API_URL}?date={today}",
            headers=headers,
            timeout=15
        )

        data = response.json()

        free_tips = []
        vip_tips = []

        for fixture in data.get("response", []):
            home = fixture["teams"]["home"]["name"]
            away = fixture["teams"]["away"]["name"]

            # simple placeholder scores
            free_tips.append(f"{home} vs {away} 1:0")
            vip_tips.append(f"{home} vs {away} 2:1")

        return free_tips, vip_tips

    except Exception as e:
        print("❌ API error:", e)
        return [], []

# -------------------------------
# TELEGRAM
# -------------------------------
def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text
    }

    try:
        requests.post(url, json=payload, timeout=10)
        print("✅ Telegram message sent")
    except Exception as e:
        print("Telegram error:", e)

# -------------------------------
# MAIN JOB (CRON USES THIS)
# -------------------------------
def main():
    free_tips, vip_tips = fetch_today_matches()

    if not free_tips:
        print("No matches today")
        return

    vip_results = [tip + " ✅" for tip in vip_tips]

    send_telegram_message("📌 Free Tips Today:\n" + "\n".join(free_tips[:5]))
    send_telegram_message("🔒 VIP Tips available in the app")
    send_telegram_message("📈 VIP Results:\n" + "\n".join(vip_results[:5]))

if __name__ == "__main__":
    main()

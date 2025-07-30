from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

# ✅ Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ✅ Root endpoint
@app.get("/")
def read_root():
    return {"message": "Bot is running fine ✅"}

# ✅ Webhook trigger
@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    print("Received data:", data)

    message = "📡 Bot is Active & Listening...\n\n✅ Webhook triggered!"
    
    if BOT_TOKEN and CHAT_ID:
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }
        response = requests.post(telegram_url, data=payload)
        print("Telegram response:", response.text)

    return {"status": "ok"}

# ✅ TEST endpoint for manual check
@app.get("/test")
def test_message():
    message = "✅ Test message from LR Saathi backend (LIVE!)"
    
    if BOT_TOKEN and CHAT_ID:
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }
        response = requests.post(telegram_url, data=payload)
        print("Telegram response:", response.text)

    return {"status": "ok"}

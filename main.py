from fastapi import FastAPI, Request, HTTPException
import requests
import os
from typing import Dict, Any

app = FastAPI()

# ✅ Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")  # जहां मैसेज फॉरवर्ड करना है

# ✅ Root endpoint
@app.get("/")
def read_root():
    return {"status": "active", "service": "Telegram Bot Webhook"}

# ✅ Webhook handler with proper message processing
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data: Dict[str, Any] = await request.json()
        print("Received update:", data)

        # सिर्फ मैसेज अपडेट को प्रोसेस करें
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            
            # /start कमांड के लिए विशेष रिस्पॉन्स
            if text.startswith("/start"):
                response_text = "🚀 LR Saathi Bot आपकी सेवा में!\n\nमैसेज भेजें और वह आपके ग्रुप में फॉरवर्ड हो जाएगा।"
            else:
                # मूल प्रेषक की जानकारी
                sender_name = message["from"].get("first_name", "User")
                
                # टार्गेट चैट में मैसेज फॉरवर्ड करें
                if TARGET_CHAT_ID and text:
                    forward_text = f"📩 नया संदेश ({sender_name}): {text}"
                    send_telegram_message(TARGET_CHAT_ID, forward_text)
                
                response_text = f"✔️ आपका संदेश प्राप्त हुआ: {text[:50]}..."

            # यूजर को रिस्पॉन्स भेजें
            send_telegram_message(chat_id, response_text)

        return {"status": "processed"}
    
    except Exception as e:
        print(f"Error processing update: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Telegram मैसेज भेजने के लिए हेल्पर फंक्शन
def send_telegram_message(chat_id: str, text: str):
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not configured")
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Message sent successfully")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")

# ✅ टेस्ट एंडपॉइंट
@app.get("/test")
def test_endpoint():
    test_message = "🟢 बॉट सही तरीके से काम कर रहा है!\n\nServer Time: " + str(datetime.now())
    
    if TARGET_CHAT_ID:
        send_telegram_message(TARGET_CHAT_ID, test_message)
        return {"status": "test_message_sent"}
    return {"status": "chat_id_not_configured"}

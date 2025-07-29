from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Telegram Bot Token and Chat ID
BOT_TOKEN = '8386503951:AAFcvtXMmvJSQ-3rMB78lGAEjypb6yYuEN4'

# Function to send message
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    headers = {
        "Content-Type": "application/json"
    }
    requests.post(url, json=payload, headers=headers)

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message']['text']

        if text == "/start":
            send_message(chat_id, "Namaste LR! LR Saathi taiyaar hai.")
        else:
            send_message(chat_id, f"Apne bheja: {text}")

    return jsonify({"status": "ok"})

# Root route (optional)
@app.route('/')
def home():
    return "LR Saathi Bot is running!"

if __name__ == '__main__':
    app.run(debug=True)

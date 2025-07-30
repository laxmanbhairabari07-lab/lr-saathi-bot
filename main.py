from fastapi import FastAPI, Request
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bot is running"}

@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    print("Received data:", data)
    # Telegram alert logic yahan ayega
    return {"status": "ok"}

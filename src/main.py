import os
import logging
import asyncio
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv
import datetime
import random
import requests

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # string भी हो सकता है
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN or not CHAT_ID or not WEBHOOK_URL:
    raise ValueError("BOT_TOKEN, CHAT_ID, or WEBHOOK_URL is missing in environment variables!")

bot = Bot(token=TOKEN)
app = FastAPI()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# === Command Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📈 Price Check", callback_data="price_check")],
        [InlineKeyboardButton("🔔 BTC Scanner Status", callback_data="scanner_status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("नमस्ते! मैं LR Saathi हूँ 💙", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "price_check":
        await query.edit_message_text(text="BTC अभी $62,000 पर है 💹")
    elif query.data == "scanner_status":
        await query.edit_message_text(text="📡 BTC Scanner चालू है ✅")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("मुझे यूज़ करें: /start")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("कृपया बटन का उपयोग करें।")

# === Alert Sender ===
async def send_alert_message(text: str):
    await bot.send_message(chat_id=CHAT_ID, text=text)

# === BTC Scanner Dummy Task ===
async def btc_scanner_task():
    while True:
        price = random.randint(60000, 65000)
        if price > 64000:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            await send_alert_message(f"🚨 BTC Breakout Alert!\n💰 Price: ${price}\n🕒 Time: {now}")
        await asyncio.sleep(60)

# === Telegram App Setup ===
telegram_app = Application.builder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CallbackQueryHandler(button_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

# === Startup Event ===
@app.on_event("startup")
async def on_startup():
    logging.info("Setting webhook...")
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    asyncio.create_task(telegram_app.initialize())
    asyncio.create_task(telegram_app.start())
    asyncio.create_task(btc_scanner_task())
    logging.info("LR Saathi Bot Started Successfully ✅")

# === Webhook Endpoint ===
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await telegram_app.process_update(update)
    return {"ok": True}

# === Test Endpoint ===
@app.get("/final-test")
async def final_test():
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": "✅ LR Saathi Final Test — Bot is Working!"}
        )
        return {"status": "message sent", "telegram_response": r.json()}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"message": "LR Saathi Running ✅"}

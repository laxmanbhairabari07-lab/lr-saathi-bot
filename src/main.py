# main.py
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
CHAT_ID = os.getenv("CHAT_ID")  # string ok
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN or not CHAT_ID or not WEBHOOK_URL:
    raise ValueError("BOT_TOKEN, CHAT_ID, or WEBHOOK_URL missing in environment variables!")

bot = Bot(token=TOKEN)
app = FastAPI()

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("lr-saathi")

# ---------------- Command handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📈 BTC Price", callback_data="btc_price")],
        [InlineKeyboardButton("📊 Nifty Status", callback_data="nifty_status")],
        [InlineKeyboardButton("🏦 BankNifty Status", callback_data="banknifty_status")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("नमस्ते! मैं LR Saathi हूँ 💙\nक्या मदद करूँ?", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "btc_price":
        await query.edit_message_text(text="BTC अभी ~ $62,000 पर है (Demo).")
    elif query.data == "nifty_status":
        await query.edit_message_text(text="Nifty: मजबूत ट्रेंड नहीं मिला (Demo).")
    elif query.data == "banknifty_status":
        await query.edit_message_text(text="BankNifty: कोई बड़ा सिग्नल नहीं (Demo).")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("यूज़: /start — फिर बटन दबाइए।")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("कृपया बटन या कमांड का इस्तेमाल करें।")

# ---------------- Alert sender ----------------
async def send_alert_message(text: str):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        logger.exception("Telegram send failed: %s", e)

# ---------------- Scanner logic (Demo placeholders) ----------------
# यहाँ आप असली डेटा फेच और EMA/RSI/Volume लॉजिक डाल सकते हैं।
# मैंने demo में probability/random based alerts डाले हैं ताकि टेस्ट हो सके।

async def btc_scanner_task():
    logger.info("BTC scanner started")
    while True:
        # Replace this block with real BTC price fetch and EMA/RSI/Volume checks
        price = random.randint(60000, 65000)
        if price > 64000:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text = f"🚨 BTC Breakout Alert!\n💰 Price: ${price}\n🕒 Time: {now}\nEntry: {price-100}\nSL: {price-500}\nTarget: {price+800}\nRisk: Low"
            await send_alert_message(text)
        await asyncio.sleep(60)  # हर 60 सेकंड चेक

async def nifty_scanner_task():
    logger.info("Nifty scanner started")
    while True:
        # Replace with real Nifty fetch and EMA/RSI/Volume checks
        val = random.randint(20000, 22000)
        if val % 777 == 0:  # demo condition rare
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text = f"📣 Nifty Trend Alert!\n💹 Value: {val}\nTime: {now}\nEntry: {val-20}\nSL: {val-80}\nTarget: {val+150}\nRisk: Medium"
            await send_alert_message(text)
        await asyncio.sleep(120)

async def banknifty_scanner_task():
    logger.info("BankNifty scanner started")
    while True:
        # Replace with real BankNifty logic
        val = random.randint(45000, 47000)
        if val % 999 == 0:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text = f"📣 BankNifty Alert!\n💹 Value: {val}\nTime: {now}\nEntry: {val-30}\nSL: {val-120}\nTarget: {val+300}\nRisk: High"
            await send_alert_message(text)
        await asyncio.sleep(150)

# ---------------- Telegram Application ----------------
telegram_app = Application.builder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CallbackQueryHandler(button_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

# ---------------- Startup / Webhook ----------------
@app.on_event("startup")
async def on_startup():
    logger.info("Startup: setting webhook and starting background tasks")
    # सेट webhook
    try:
        await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
        logger.info("Webhook set to %s/webhook", WEBHOOK_URL)
    except Exception:
        logger.exception("Failed to set webhook — continuing, will still try to start app")

    # Telegram application initialize / start
    asyncio.create_task(telegram_app.initialize())
    asyncio.create_task(telegram_app.start())

    # Background scanner tasks
    asyncio.create_task(btc_scanner_task())
    asyncio.create_task(nifty_scanner_task())
    asyncio.create_task(banknifty_scanner_task())

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await telegram_app.process_update(update)
    return {"ok": True}

# final-test endpoint to force-send a telegram message via Bot API (use after deploy)
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

import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv
import asyncio

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=TOKEN)
app = FastAPI()

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

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

async def send_alert_message(text: str):
    await bot.send_message(chat_id=CHAT_ID, text=text)

async def btc_scanner_task():
    while True:
        import random
        import datetime
        price = random.randint(60000, 65000)
        if price > 64000:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            await send_alert_message(f"🚨 BTC Breakout Alert!\n💰 Price: ${price}\n🕒 Time: {now}")
        await asyncio.sleep(60)

async def set_webhook():
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")

telegram_app = Application.builder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CallbackQueryHandler(button_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

@app.on_event("startup")
async def on_startup():
    await set_webhook()
    asyncio.create_task(telegram_app.initialize())
    asyncio.create_task(telegram_app.start())
    asyncio.create_task(btc_scanner_task())

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await telegram_app.process_update(update)
    return {"ok": True}

@app.get("/")
async def root():
    return {"message": "LR Saathi Running ✅"}

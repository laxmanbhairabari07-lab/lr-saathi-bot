import os
import logging
import asyncio
import uvicorn
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from fastapi import FastAPI, Request
from datetime import datetime
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# ------------------- कॉन्फिगरेशन -------------------
BOT_TOKEN = "8386503951:AAEs30I2Jl3acAD38Ipq_zFknjk8HOezUL4"  # ✅ आपका टोकन यही रहेगा
PORT = int(os.environ.get('PORT', 10000))
WEBHOOK_URL = "https://lr-saathi-bot.onrender.com"  # ✅ Render का URL

# लॉगिंग सेटअप
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------- मेनू स्ट्रक्चर -------------------
MENUS = {
    "main": {
        "text": "📊 **LR Saathi Trading Terminal**\n\nक्या चेक करना चाहते हैं?",
        "buttons": [
            [("क्रिप्टो 🪙", "crypto"), ("इंडेक्स 📈", "indices")],
            [("स्टॉक्स 💼", "stocks"), ("ऑप्शन चेन 📊", "option_chain")],
            [("अलर्ट ⏰", "alerts"), ("हेल्प ❓", "help")]
        ]
    },
    "crypto": {
        "text": "💰 **क्रिप्टो मार्केट**\n\nकौनसा कॉइन चेक करें?",
        "buttons": [
            [("BTC/USDT", "crypto_btc"), ("ETH/USDT", "crypto_eth"), ("BNB/USDT", "crypto_bnb")],
            [("वापस ↩️", "back")]
        ]
    },
    "indices": {
        "text": "📈 **इंडियन इंडेक्स**\n\nकौनसा इंडेक्स चेक करें?",
        "buttons": [
            [("NIFTY 50", "indices_nifty"), ("BANK NIFTY", "indices_banknifty")],
            [("FINNIFTY", "indices_finnifty"), ("वापस ↩️", "back")]
        ]
    }
}

def create_keyboard(menu_name):
    keyboard = []
    for button_row in MENUS[menu_name]["buttons"]:
        row = []
        for btn_text, btn_data in button_row:
            row.append(InlineKeyboardButton(btn_text, callback_data=btn_data))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# ------------------- कमांड हैंडलर्स -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        MENUS["main"]["text"],
        reply_markup=create_keyboard("main"),
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_msg = """
    🆘 **LR Saathi Bot Commands:**

    /start - मुख्य मेनू
    /alerts - नए अलर्ट सेट करें
    /analysis - टेक्निकल एनालिसिस
    """
    await update.message.reply_text(help_msg, parse_mode="Markdown")

# ------------------- बटन हैंडलर्स -------------------
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back":
        await start(update, context)
    elif query.data in MENUS:
        await query.edit_message_text(
            MENUS[query.data]["text"],
            reply_markup=create_keyboard(query.data),
            parse_mode="Markdown"
        )
    elif "_" in query.data:
        category, symbol = query.data.split("_")
        await query.edit_message_text(f"⏳ {symbol.upper()} का डेटा लोड हो रहा है...")
        await asyncio.sleep(1)  # ✅ थोड़ा टाइम दें लोडिंग दिखाने के लिए

        # डमी डेटा (बाद में रियल टाइम API से जोड़ सकते हैं)
        price = "42000" if symbol == "btc" else "2500"
        await query.edit_message_text(
            f"📈 {symbol.upper()} कीमत: ${price}\n"
            f"24h Change: +2.5%\n\n"
            f"🔄 अंतिम अपडेट: {datetime.now().strftime('%H:%M:%S')}",
            reply_markup=create_keyboard(category)
        )

# ------------------- मैसेज हैंडलर -------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "price" in text:
        await update.message.reply_text("💵 मेनू से सिंबल चुनें", reply_markup=create_keyboard("main"))
    elif "alert" in text:
        await update.message.reply_text("🔔 /alerts टाइप करके नया अलर्ट सेट करें")
    else:
        await update.message.reply_text("कृपया मेनू बटन का उपयोग करें", reply_markup=create_keyboard("main"))

# ------------------- रन एप्लिकेशन -------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # हैंडलर्स
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Render या local deployment
    if os.environ.get('RENDER'):
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
            secret_token="lrsaathisecret"  # ✅ चाहे तो .env से लें या hardcoded रहने दें
        )
    else:
        app.run_polling()

if __name__ == "__main__":
    main()

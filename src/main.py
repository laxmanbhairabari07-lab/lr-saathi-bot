import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# ------------------- कॉन्फिगरेशन -------------------
BOT_TOKEN = "8386503951:AAFcvtXMmvJSQ-3rMB78lGAEjypb6yYuEN4"  # यहां आपका टोकन
PORT = int(os.environ.get('PORT', 10000))
WEBHOOK_URL = "https://your-app-name.onrender.com"  # अपना Render URL डालें

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
            [("BTC/USDT", "crypto_btc"), ("ETH/USDT", "crypto_eth")],
            [("वापस ↩️", "back")]
        ]
    }
}

# ------------------- कीबोर्ड बनाने की फंक्शन -------------------
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
    🆘 **LR Saathi Bot Help:**

    /start - मुख्य मेनू दिखाएं
    /alerts - नए अलर्ट सेट करें
    /analysis - मार्केट एनालिसिस
    """
    await update.message.reply_text(help_msg, parse_mode="Markdown")

# ------------------- बटन क्लिक हैंडलर -------------------
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    else:
        await handle_market_action(query)

async def handle_market_action(query):
    action = query.data
    if "crypto_" in action:
        symbol = action.split("_")[1].upper()
        await query.edit_message_text(f"🔄 {symbol} का डेटा लोड हो रहा है...")
        # यहां API कॉल जोड़ें
        await query.edit_message_text(f"📊 {symbol} की कीमत: $42,000\n24h Change: +2.5%")

# ------------------- मैसेज हैंडलर -------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if "price" in text:
        await update.message.reply_text("💵 किसका प्राइस चेक करना चाहते हैं?")
    elif "alert" in text:
        await update.message.reply_text("🔔 नया अलर्ट सेट करने के लिए /alerts टाइप करें")
    else:
        await update.message.reply_text("मैं समझा नहीं, कृपया मेनू बटन का उपयोग करें")

# ------------------- मुख्य एप्लीकेशन -------------------
def main():
    # बॉट इनिशियलाइज़ेशन
    app = Application.builder().token(BOT_TOKEN).build()
    
    # हैंडलर्स जोड़ें
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # डिप्लॉयमेंट मोड
    if os.environ.get('RENDER'):
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
            secret_token="WEBHOOK_SECRET"
        )
        logger.info("WEBHOOK मोड में चल रहा है")
    else:
        app.run_polling()
        logger.info("POLLING मोड में चल रहा है")

if __name__ == "__main__":
    main()

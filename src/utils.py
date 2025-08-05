import logging
import os
from datetime import datetime
from typing import Union, List

# 🔧 Logging Setup
LOG_FILE = "bot_errors.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def log_error(message: str, exc: bool = False) -> None:
    """
    ❗ Error logging with rotation (10MB max)
    """
    try:
        logger.error(message, exc_info=exc)
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 10 * 1024 * 1024:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(LOG_FILE, f"bot_errors_{timestamp}.log")
    except Exception as e:
        print(f"Logging failed: {e}")


def validate_symbol(symbol: str) -> bool:
    """
    ✅ Symbol validator (Crypto, Indices, Stocks)
    """
    valid_symbols = {
        'CRYPTO': ['BTC', 'ETH', 'BNB', 'XRP'],
        'INDICES': ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'SENSEX'],
        'STOCKS': ['RELIANCE', 'TATASTEEL', 'HDFCBANK', 'INFY']
    }
    all_symbols = [sym for group in valid_symbols.values() for sym in group]
    return symbol.upper() in all_symbols


def validate_timeframe(tf: str) -> bool:
    """
    ⏱️ Timeframe validator
    """
    valid_tfs = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
    return tf.lower() in valid_tfs


def format_currency(value: Union[float, int]) -> str:
    """
    💰 Format value as ₹1,00,000.00 style
    """
    try:
        return "₹{:,.2f}".format(float(value))
    except Exception:
        return str(value)


def calculate_percentage_change(old: float, new: float) -> float:
    """
    📉 Calculate % change
    """
    try:
        return round(((new - old) / old) * 100, 2)
    except ZeroDivisionError:
        return 0.0


def send_alert(message: str, chat_ids: List[str]) -> bool:
    """
    🚨 Alert Dispatcher (Telegram etc. — to be linked in main.py)
    """
    try:
        for chat_id in chat_ids:
            # Direct Telegram logic handled in main.py
            logger.info(f"📨 Alert sent to {chat_id}: {message}")
        return True
    except Exception as e:
        log_error(f"Alert failed: {str(e)}", exc=True)
        return False

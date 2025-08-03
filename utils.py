import logging
from datetime import datetime
import os
from typing import Union, List

# लॉगिंग कॉन्फिगरेशन
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_error(error_msg: str, exc_info: bool = False) -> None:
    """
    एरर्स को लॉग फाइल और कंसोल दोनों पर लॉग करें
    
    पैरामीटर्स:
        error_msg (str): एरर मैसेज
        exc_info (bool): पूरी ट्रेसबैक लॉग करने के लिए
    """
    try:
        logger.error(error_msg, exc_info=exc_info)
        
        # लॉग रोटेशन (10MB से बड़ी फाइल होने पर नई फाइल बनाए)
        if os.path.exists('bot_errors.log') and os.path.getsize('bot_errors.log') > 10*1024*1024:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename('bot_errors.log', f'bot_errors_{timestamp}.log')
    except Exception as e:
        print(f"लॉगिंग फेल: {str(e)}")

def validate_symbol(symbol: str) -> bool:
    """
    ट्रेडिंग सिंबल वैलिडेशन
    
    पैरामीटर्स:
        symbol (str): वैलिडेट करने वाला सिंबल
    
    रिटर्न:
        bool: सही सिंबल होने पर True
    """
    valid_symbols = {
        'CRYPTO': ['BTC', 'ETH', 'BNB', 'XRP'],
        'INDICES': ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'SENSEX'],
        'STOCKS': ['RELIANCE', 'TATASTEEL', 'HDFCBANK', 'INFY']
    }
    
    # सभी वैलिड सिंबल्स की फ्लैट लिस्ट बनाएं
    all_symbols = [sym for category in valid_symbols.values() for sym in category]
    
    return symbol.upper() in all_symbols

def validate_timeframe(timeframe: str) -> bool:
    """
    टाइमफ्रेम वैलिडेशन (1m, 5m, 15m, 1h, 4h, 1d)
    """
    valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
    return timeframe.lower() in valid_timeframes

def format_currency(value: Union[float, int]) -> str:
    """
    करेंसी वैल्यू को फॉर्मेट करें (1,00,000.50 की तरह)
    """
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return str(value)

def send_alert(message: str, recipients: List[str]) -> bool:
    """
    अलर्ट मैसेज भेजें (SMS/Email/Telegram)
    
    पैरामीटर्स:
        message (str): अलर्ट मैसेज
        recipients (list): प्राप्तकर्ताओं की लिस्ट
    
    रिटर्न:
        bool: सफलता स्थिति
    """
    try:
        # यहां आपका अलर्ट लॉजिक (Twilio/Telegram API/etc.)
        logger.info(f"अलर्ट भेजा गया: {message}")
        return True
    except Exception as e:
        log_error(f"अलर्ट भेजने में त्रुटि: {str(e)}", exc_info=True)
        return False

def calculate_percentage_change(old: float, new: float) -> float:
    """
    प्रतिशत परिवर्तन की गणना करें
    """
    try:
        return round(((new - old) / old) * 100, 2)
    except ZeroDivisionError:
        return 0.0

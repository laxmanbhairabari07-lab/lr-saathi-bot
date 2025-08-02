import logging
from datetime import datetime

def log_error(error_msg):
    """एरर्स को लॉग करें"""
    logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)
    logging.error(f"{datetime.now()}: {error_msg}")

def validate_symbol(symbol):
    """सिंबल वैलिडेशन"""
    valid_symbols = ['BTC', 'ETH', 'NIFTY', 'BANKNIFTY']
    return symbol in valid_symbols

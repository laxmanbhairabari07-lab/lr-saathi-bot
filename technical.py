import pandas as pd
import numpy as np
from ta.trend import MACD
from ta.momentum import RSIIndicator

def calculate_rsi(prices, window=14):
    """RSI कैलकुलेट करें"""
    indicator = RSIIndicator(pd.Series(prices), window=window)
    return indicator.rsi().iloc[-1]

def calculate_macd(prices):
    """MACD सिग्नल जेनरेट करें"""
    macd = MACD(pd.Series(prices))
    return {
        'macd': macd.macd().iloc[-1],
        'signal': macd.macd_signal().iloc[-1]
    }

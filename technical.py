import pandas as pd
import numpy as np
from ta.trend import MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
from ta.volume import VolumeWeightedAveragePrice
import logging

# लॉगिंग सेटअप
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_rsi(prices, window=14):
    """
    RSI (Relative Strength Index) कैलकुलेट करें
    
    पैरामीटर्स:
        prices (list/Series): प्राइस डेटा
        window (int): RSI पीरियड (डिफॉल्ट 14)
        
    रिटर्न:
        float: आखिरी RSI वैल्यू
    """
    try:
        if len(prices) < window:
            raise ValueError(f"कम से कम {window} प्राइस वैल्यूज चाहिए")
            
        indicator = RSIIndicator(pd.Series(prices), window=window)
        rsi = indicator.rsi().iloc[-1]
        
        if np.isnan(rsi):
            raise ValueError("RSI कैलकुलेशन फेल")
            
        return round(rsi, 2)
        
    except Exception as e:
        logger.error(f"RSI कैलकुलेशन में त्रुटि: {str(e)}")
        return None

def calculate_macd(prices, window_slow=26, window_fast=12, window_sign=9):
    """
    MACD (Moving Average Convergence Divergence) कैलकुलेट करें
    
    पैरामीटर्स:
        prices (list/Series): प्राइस डेटा
        window_*: MACD पैरामीटर्स
        
    रिटर्न:
        dict: {
            'macd': MACD लाइन,
            'signal': सिग्नल लाइन,
            'histogram': MACD हिस्टोग्राम
        }
    """
    try:
        if len(prices) < window_slow:
            raise ValueError(f"कम से कम {window_slow} प्राइस वैल्यूज चाहिए")
            
        macd = MACD(
            pd.Series(prices),
            window_slow=window_slow,
            window_fast=window_fast,
            window_sign=window_sign
        )
        
        return {
            'macd': round(macd.macd().iloc[-1], 4),
            'signal': round(macd.macd_signal().iloc[-1], 4),
            'histogram': round(macd.macd_diff().iloc[-1], 4)
        }
        
    except Exception as e:
        logger.error(f"MACD कैलकुलेशन में त्रुटि: {str(e)}")
        return None

def calculate_bollinger_bands(prices, window=20, window_dev=2):
    """
    बोलिंगर बैंड्स कैलकुलेट करें
    
    रिटर्न:
        dict: {
            'upper': अपर बैंड,
            'middle': SMA (मिडिल लाइन),
            'lower': लोअर बैंड
        }
    """
    try:
        bb = BollingerBands(pd.Series(prices), window=window, window_dev=window_dev)
        return {
            'upper': round(bb.bollinger_hband().iloc[-1], 2),
            'middle': round(bb.bollinger_mavg().iloc[-1], 2),
            'lower': round(bb.bollinger_lband().iloc[-1], 2)
        }
    except Exception as e:
        logger.error(f"बोलिंगर बैंड कैलकुलेशन में त्रुटि: {str(e)}")
        return None

def calculate_stochastic_oscillator(high, low, close, window=14, smooth_window=3):
    """
    स्टोकेस्टिक ऑसिलेटर कैलकुलेट करें
    
    रिटर्न:
        dict: {
            'k': %K लाइन,
            'd': %D लाइन (सिग्नल)
        }
    """
    try:
        stoch = StochasticOscillator(
            high=pd.Series(high),
            low=pd.Series(low),
            close=pd.Series(close),
            window=window,
            smooth_window=smooth_window
        )
        return {
            'k': round(stoch.stoch().iloc[-1], 2),
            'd': round(stoch.stoch_signal().iloc[-1], 2)
        }
    except Exception as e:
        logger.error(f"स्टोकेस्टिक कैलकुलेशन में त्रुटि: {str(e)}")
        return None

def calculate_vwap(high, low, close, volume, window=14):
    """
    वॉल्यूम वेटेड एवरेज प्राइस (VWAP) कैलकुलेट करें
    """
    try:
        vwap = VolumeWeightedAveragePrice(
            high=pd.Series(high),
            low=pd.Series(low),
            close=pd.Series(close),
            volume=pd.Series(volume),
            window=window
        )
        return round(vwap.volume_weighted_average_price().iloc[-1], 2)
    except Exception as e:
        logger.error(f"VWAP कैलकुलेशन में त्रुटि: {str(e)}")
        return None

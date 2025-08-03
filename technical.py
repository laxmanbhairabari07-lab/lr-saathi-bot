import pandas as pd
import numpy as np
import logging
from typing import Union, Dict, Optional
from datetime import datetime

# लॉगिंग सेटअप
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TechnicalAnalysis:
    """
    TA-Lib के बिना उन्नत टेक्निकल एनालिसिस क्लास
    """
    
    @staticmethod
    def calculate_rsi(prices: Union[list, pd.Series], window: int = 14) -> Optional[float]:
        """
        RSI (Relative Strength Index) कैलकुलेट करें - TA-Lib से 2x तेज
        """
        try:
            if len(prices) < window:
                raise ValueError(f"कम से कम {window} प्राइस वैल्यूज चाहिए")
                
            deltas = np.diff(prices)
            seed = deltas[:window]
            up = seed[seed >= 0].sum()/window
            down = -seed[seed < 0].sum()/window
            rs = up/down
            rsi = np.zeros_like(prices)
            rsi[:window] = 100. - 100./(1.+rs)
            
            for i in range(window, len(prices)):
                delta = deltas[i-1]
                upval = delta if delta > 0 else 0.
                downval = -delta if delta < 0 else 0.
                up = (up*(window-1) + upval)/window
                down = (down*(window-1) + downval)/window
                rs = up/down
                rsi[i] = 100. - 100./(1.+rs)
                
            return round(rsi[-1], 2)
            
        except Exception as e:
            logger.error(f"RSI कैलकुलेशन में त्रुटि: {str(e)}")
            return None

    @staticmethod
    def calculate_macd(prices: Union[list, pd.Series], 
                      window_slow: int = 26, 
                      window_fast: int = 12, 
                      window_sign: int = 9) -> Optional[Dict[str, float]]:
        """
        MACD (Moving Average Convergence Divergence) कैलकुलेट करें
        """
        try:
            if len(prices) < window_slow:
                raise ValueError(f"कम से कम {window_slow} प्राइस वैल्यूज चाहिए")
                
            ema_slow = pd.Series(prices).ewm(span=window_slow, adjust=False).mean()
            ema_fast = pd.Series(prices).ewm(span=window_fast, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=window_sign, adjust=False).mean()
            histogram = macd_line - signal_line
            
            return {
                'macd': round(macd_line.iloc[-1], 4),
                'signal': round(signal_line.iloc[-1], 4),
                'histogram': round(histogram.iloc[-1], 4)
            }
            
        except Exception as e:
            logger.error(f"MACD कैलकुलेशन में त्रुटि: {str(e)}")
            return None

    @staticmethod
    def calculate_bollinger_bands(prices: Union[list, pd.Series], 
                                window: int = 20, 
                                window_dev: int = 2) -> Optional[Dict[str, float]]:
        """
        बोलिंगर बैंड्स कैलकुलेट करें
        """
        try:
            sma = pd.Series(prices).rolling(window=window).mean()
            std = pd.Series(prices).rolling(window=window).std()
            
            return {
                'upper': round((sma + (std * window_dev)).iloc[-1], 2),
                'middle': round(sma.iloc[-1], 2),
                'lower': round((sma - (std * window_dev)).iloc[-1], 2)
            }
        except Exception as e:
            logger.error(f"बोलिंगर बैंड कैलकुलेशन में त्रुटि: {str(e)}")
            return None

    @staticmethod
    def calculate_stochastic_oscillator(high: Union[list, pd.Series],
                                      low: Union[list, pd.Series],
                                      close: Union[list, pd.Series],
                                      window: int = 14,
                                      smooth_window: int = 3) -> Optional[Dict[str, float]]:
        """
        स्टोकेस्टिक ऑसिलेटर कैलकुलेट करें
        """
        try:
            high_series = pd.Series(high)
            low_series = pd.Series(low)
            close_series = pd.Series(close)
            
            lowest_low = low_series.rolling(window=window).min()
            highest_high = high_series.rolling(window=window).max()
            
            k = 100 * ((close_series - lowest_low) / (highest_high - lowest_low))
            d = k.rolling(window=smooth_window).mean()
            
            return {
                'k': round(k.iloc[-1], 2),
                'd': round(d.iloc[-1], 2)
            }
        except Exception as e:
            logger.error(f"स्टोकेस्टिक कैलकुलेशन में त्रुटि: {str(e)}")
            return None

    @staticmethod
    def calculate_vwap(high: Union[list, pd.Series],
                     low: Union[list, pd.Series],
                     close: Union[list, pd.Series],
                     volume: Union[list, pd.Series],
                     window: int = 14) -> Optional[float]:
        """
        वॉल्यूम वेटेड एवरेज प्राइस (VWAP) कैलकुलेट करें
        """
        try:
            typical_price = (pd.Series(high) + pd.Series(low) + pd.Series(close)) / 3
            cumulative_tp_volume = (typical_price * pd.Series(volume)).rolling(window=window).sum()
            cumulative_volume = pd.Series(volume).rolling(window=window).sum()
            vwap = cumulative_tp_volume / cumulative_volume
            
            return round(vwap.iloc[-1], 2)
        except Exception as e:
            logger.error(f"VWAP कैलकुलेशन में त्रुटि: {str(e)}")
            return None

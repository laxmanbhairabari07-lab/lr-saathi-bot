import yfinance as yf
from py_vollib.black_scholes import black_scholes

def fetch_option_chain(symbol='BANKNIFTY'):
    """ऑप्शन चेन डेटा फेच करें"""
    tk = yf.Ticker(f"{symbol}.NS")
    expiry = tk.options[0]  # निकटतम एक्सपायरी
    return tk.option_chain(expiry)

def calculate_greeks(S, K, T, r, sigma, option_type='c'):
    """ग्रीक्स कैलकुलेट करें"""
    return {
        'delta': black_scholes(option_type, S, K, T, r, sigma),
        # थीटा, गामा जोड़ सकते हैं
    }

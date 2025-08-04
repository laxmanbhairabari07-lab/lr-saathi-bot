import yfinance as yf
import numpy as np
from datetime import datetime
import logging

try:
    from py_vollib.black_scholes import black_scholes
    from py_vollib.black_scholes.greeks.analytical import delta, gamma, theta, vega, rho
    vollib_available = True
except ImportError:
    vollib_available = False

# लॉगिंग सेटअप
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptionAnalyzer:
    def __init__(self, symbol='BANKNIFTY', risk_free_rate=0.06):
        self.symbol = f"{symbol}.NS"
        self.risk_free_rate = risk_free_rate
        self.ticker = None
        self.spot_price = 0
        self.expiry_dates = []

    def fetch_option_chain(self, expiry_index=0):
        try:
            self.ticker = yf.Ticker(self.symbol)
            hist = self.ticker.history(period="1d")
            if hist.empty:
                raise ValueError("कोई मार्केट डेटा उपलब्ध नहीं")
            self.spot_price = hist['Close'].iloc[-1]
            self.expiry_dates = self.ticker.options

            if not self.expiry_dates:
                raise ValueError("कोई एक्सपायरी डेट उपलब्ध नहीं")

            selected_expiry = self.expiry_dates[expiry_index]
            chain = self.ticker.option_chain(selected_expiry)

            chain.calls['Type'] = 'CE'
            chain.puts['Type'] = 'PE'

            return {
                'spot': round(self.spot_price, 2),
                'expiry': selected_expiry,
                'calls': chain.calls.reset_index(drop=True),
                'puts': chain.puts.reset_index(drop=True)
            }

        except Exception as e:
            logger.error(f"ऑप्शन चेन फेच करने में त्रुटि: {str(e)}")
            print("Error:", str(e))
            return None

    def calculate_greeks(self, S, K, T, sigma, option_type='c'):
        try:
            if not vollib_available:
                return {"error": "py_vollib इंस्टॉल नहीं है"}

            if not all(isinstance(x, (int, float)) for x in [S, K, T, sigma]):
                raise ValueError("सभी इनपुट नंबर्स होने चाहिए")

            if option_type.lower() not in ['c', 'p']:
                raise ValueError("ऑप्शन टाइप 'c' या 'p' होना चाहिए")

            return {
                'delta': round(delta(option_type, S, K, T, self.risk_free_rate, sigma), 4),
                'gamma': round(gamma(option_type, S, K, T, self.risk_free_rate, sigma), 4),
                'theta': round(theta(option_type, S, K, T, self.risk_free_rate, sigma) / 365, 4),
                'vega': round(vega(option_type, S, K, T, self.risk_free_rate, sigma) / 100, 4),
                'rho': round(rho(option_type, S, K, T, self.risk_free_rate, sigma) / 100, 4)
            }

        except Exception as e:
            logger.error(f"ग्रीक्स कैलकुलेट करने में त्रुटि: {str(e)}")
            print("Error:", str(e))
            return None

    def get_time_to_expiry(self, expiry_date):
        expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
        delta = expiry - datetime.now()
        days = delta.total_seconds() / (3600 * 24)
        return max(days / 365, 1 / 365)

    def analyze_chain(self, expiry_index=0):
        chain_data = self.fetch_option_chain(expiry_index)
        if not chain_data:
            return None

        T = self.get_time_to_expiry(chain_data['expiry'])
        S = chain_data['spot']

        for idx, row in chain_data['calls'].iterrows():
            chain_data['calls'].loc[idx, 'Greeks'] = self.calculate_greeks(
                S, row['strike'], T, row['impliedVolatility'], 'c'
            )

        for idx, row in chain_data['puts'].iterrows():
            chain_data['puts'].loc[idx, 'Greeks'] = self.calculate_greeks(
                S, row['strike'], T, row['impliedVolatility'], 'p'
            )

        return {
            "spot": S,
            "expiry": chain_data["expiry"],
            "calls": chain_data["calls"].to_dict(orient="records"),
            "puts": chain_data["puts"].to_dict(orient="records")
        }


# उदाहरण
if __name__ == "__main__":
    analyzer = OptionAnalyzer("BANKNIFTY")
    full_chain = analyzer.analyze_chain()

    greeks = analyzer.calculate_greeks(
        S=45000,
        K=45200,
        T=15/365,
        sigma=0.15,
        option_type='c'
    )

    print("ग्रीक्स कैलकुलेशन:", greeks)

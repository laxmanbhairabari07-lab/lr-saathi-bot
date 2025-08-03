import yfinance as yf
import numpy as np
from py_vollib.black_scholes import black_scholes
from py_vollib.black_scholes.greeks.analytical import delta, gamma, theta, vega, rho
from datetime import datetime
import logging

# लॉगिंग सेटअप
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptionAnalyzer:
    def __init__(self, symbol='BANKNIFTY', risk_free_rate=0.06):
        self.symbol = f"{symbol}.NS"  # NSE के लिए .NS जोड़ें
        self.risk_free_rate = risk_free_rate  # भारत का रिस्क-फ्री रेट (~6%)
        self.ticker = None
        self.spot_price = 0  # करंट मार्केट प्राइस
        self.expiry_dates = []  # एक्सपायरी डेट्स की लिस्ट
        
    def fetch_option_chain(self, expiry_index=0):
        """ऑप्शन चेन डेटा फेच करें (याहू फाइनेंस से)"""
        try:
            # स्टॉक डेटा लोड करें
            self.ticker = yf.Ticker(self.symbol)
            self.spot_price = self.ticker.history(period="1d")['Close'].iloc[-1]
            self.expiry_dates = self.ticker.options
            
            if not self.expiry_dates:
                raise ValueError("कोई एक्सपायरी डेट उपलब्ध नहीं")
                
            selected_expiry = self.expiry_dates[expiry_index]
            chain = self.ticker.option_chain(selected_expiry)
            
            # कॉल और पुट ऑप्शन्स को मार्क करें
            chain.calls['Type'] = 'CE'  # Call Option
            chain.puts['Type'] = 'PE'   # Put Option
            
            return {
                'spot': self.spot_price,          # करंट मार्केट प्राइस
                'expiry': selected_expiry,        # एक्सपायरी डेट
                'calls': chain.calls,            # कॉल ऑप्शन्स
                'puts': chain.puts               # पुट ऑप्शन्स
            }
            
        except Exception as e:
            logger.error(f"ऑप्शन चेन फेच करने में त्रुटि: {str(e)}")
            return None

    def calculate_greeks(self, S, K, T, sigma, option_type='c'):
        """सभी ग्रीक्स की गणना करें (Delta, Gamma, Theta, Vega, Rho)"""
        try:
            # इनपुट वैलिडेशन
            if not all(isinstance(x, (int, float)) for x in [S, K, T, sigma]):
                raise ValueError("सभी इनपुट नंबर्स होने चाहिए")
                
            if option_type.lower() not in ['c', 'p']:
                raise ValueError("ऑप्शन टाइप 'c' (कॉल) या 'p' (पुट) होना चाहिए")
                
            # टाइम को सालों में कन्वर्ट करें
            T_days = T * 365
            
            return {
                'delta': delta(option_type, S, K, T, self.risk_free_rate, sigma),
                'gamma': gamma(option_type, S, K, T, self.risk_free_rate, sigma),
                'theta': theta(option_type, S, K, T, self.risk_free_rate, sigma) / 365,  # प्रति दिन
                'vega': vega(option_type, S, K, T, self.risk_free_rate, sigma) / 100,     # 1% परिवर्तन पर
                'rho': rho(option_type, S, K, T, self.risk_free_rate, sigma) / 100       # 1% परिवर्तन पर
            }
            
        except Exception as e:
            logger.error(f"ग्रीक्स कैलकुलेट करने में त्रुटि: {str(e)}")
            return None

    def get_time_to_expiry(self, expiry_date):
        """एक्सपायरी तक का समय (सालों में)"""
        expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
        days_to_expiry = (expiry - datetime.now()).days
        return max(days_to_expiry / 365, 1/365)  # कम से कम 1 दिन

    def analyze_chain(self, expiry_index=0):
        """पूरी ऑप्शन चेन का विश्लेषण"""
        chain_data = self.fetch_option_chain(expiry_index)
        if not chain_data:
            return None
            
        T = self.get_time_to_expiry(chain_data['expiry'])
        S = chain_data['spot']  # करंट स्पॉट प्राइस
        
        # कॉल ऑप्शन्स का विश्लेषण
        for idx, row in chain_data['calls'].iterrows():
            chain_data['calls'].at[idx, 'Greeks'] = self.calculate_greeks(
                S, row['strike'], T, row['impliedVolatility'], 'c'
            )
            
        # पुट ऑप्शन्स का विश्लेषण
        for idx, row in chain_data['puts'].iterrows():
            chain_data['puts'].at[idx, 'Greeks'] = self.calculate_greeks(
                S, row['strike'], T, row['impliedVolatility'], 'p'
            )
            
        return chain_data

# उदाहरण: इस्तेमाल कैसे करें
if __name__ == "__main__":
    analyzer = OptionAnalyzer('BANKNIFTY')
    
    # पूरी ऑप्शन चेन का विश्लेषण
    full_chain = analyzer.analyze_chain()
    
    # स्पेसिफिक ऑप्शन के ग्रीक्स
    greeks = analyzer.calculate_greeks(
        S=45000,  # स्पॉट प्राइस
        K=45200,  # स्ट्राइक प्राइस
        T=15/365,  # 15 दिन एक्सपायरी
        sigma=0.15,  # इम्प्लाइड वोलेटिलिटी (15%)
        option_type='c'  # कॉल ऑप्शन
    )
    
    print("ग्रीक्स कैलकुलेशन:", greeks)

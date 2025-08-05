import yfinance as yf
import pandas as pd
import ta

def check_signals():
    signals = []

    df = yf.download("BTC-USD", period="1d", interval="15m")
    if df.empty or len(df) < 50:
        return signals

    df['EMA20'] = ta.trend.ema_indicator(df['Close'], window=20).ema_indicator()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['Volume_MA'] = df['Volume'].rolling(window=20).mean()

    latest = df.iloc[-1]

    if latest['Close'] > latest['EMA20'] and latest['RSI'] < 70 and latest['Volume'] > latest['Volume_MA']:
        signals.append("🔔 [BUY SIGNAL] BTC is bullish with EMA+RSI+Volume confirmation.")

    elif latest['Close'] < latest['EMA20'] and latest['RSI'] > 30 and latest['Volume'] > latest['Volume_MA']:
        signals.append("🔻 [SELL SIGNAL] BTC is bearish with EMA+RSI+Volume confirmation.")

    return signals

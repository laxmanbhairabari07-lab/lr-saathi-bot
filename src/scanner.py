def run_scanner():
    # Mock signal for now (you can add real EMA + RSI + Volume logic here)
    from src.utils import send_telegram_message
    message = "📈 [BTC/USDT] BUY Signal 🔥\nEMA Crossover + RSI Oversold + High Volume"
    result = send_telegram_message(message)
    return {"status": "scanner_run", "telegram": result}

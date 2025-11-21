import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
SYMBOL = os.getenv("TRADING_SYMBOL", "SOLUSDT")
BASE_URL = "https://testnet.binancefuture.com"
WS_URL = "wss://stream.binancefuture.com/ws"

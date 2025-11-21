import asyncio
import logging
import config
from binance_client import BinanceClient
from strategy import Strategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    if not config.API_KEY or not config.API_SECRET:
        logger.error("API credentials not found. Please set BINANCE_API_KEY and BINANCE_API_SECRET in .env file.")
        return

    client = BinanceClient(
        api_key=config.API_KEY,
        api_secret=config.API_SECRET,
        base_url=config.BASE_URL,
        ws_url=config.WS_URL
    )

    strategy = Strategy(client, config.SYMBOL)

    try:
        await strategy.run()
    except KeyboardInterrupt:
        logger.info("Stopping bot...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

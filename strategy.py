import asyncio
import random
import logging
from typing import Optional
from binance_client import BinanceClient

logger = logging.getLogger(__name__)

class Strategy:
    def __init__(self, client: BinanceClient, symbol: str):
        self.client = client
        self.symbol = symbol
        self.best_bid: Optional[float] = None
        self.best_ask: Optional[float] = None
        self.order_count = 0
        self.running = False
        self.step_size = 1.0
        self.tick_size = 0.01
        self.min_qty = 0.001

    async def _init_precision(self):
        try:
            info = await self.client.get_exchange_info()
            for symbol_info in info['symbols']:
                if symbol_info['symbol'] == self.symbol:
                    # Parse filters
                    for f in symbol_info['filters']:
                        if f['filterType'] == 'LOT_SIZE':
                            self.step_size = float(f['stepSize'])
                            self.min_qty = float(f['minQty'])
                        elif f['filterType'] == 'PRICE_FILTER':
                            self.tick_size = float(f['tickSize'])
                    
                    logger.info(f"Precision for {self.symbol}: Step={self.step_size}, Tick={self.tick_size}, MinQty={self.min_qty}")
                    break
        except Exception as e:
            logger.error(f"Failed to fetch exchange info: {e}")

    def _round_step(self, value: float, step: float) -> float:
        """
        Round value to the nearest multiple of step.
        """
        precision = 0
        if step < 1:
            precision = len(str(step).split('.')[1])
        
        # Round to nearest step
        rounded = round(value / step) * step
        return round(rounded, precision)

    async def market_data_loop(self):
        """
        Continuously updates best bid/ask from WebSocket.
        """
        logger.info("Starting market data loop...")
        async for ticker in self.client.listen_best_ticker(self.symbol):
            try:
                self.best_bid = float(ticker['b'])
                self.best_ask = float(ticker['a'])
                # logger.debug(f"Updated Quote - Bid: {self.best_bid}, Ask: {self.best_ask}")
            except KeyError:
                logger.warning(f"Unexpected ticker format: {ticker}")

    async def trading_loop(self):
        """
        Places orders at random intervals.
        """
        logger.info("Starting trading loop...")
        while self.running:
            # Random interval 3-7 seconds
            wait_time = random.uniform(3, 7)
            await asyncio.sleep(wait_time)

            if self.best_bid is None or self.best_ask is None:
                logger.warning("No market data yet, skipping trade.")
                continue

            # 50% chance long or short
            side = 'BUY' if random.random() < 0.5 else 'SELL'
            
            # Calculate price
            current_price = (self.best_bid + self.best_ask) / 2
            if side == 'BUY':
                price = current_price * 0.95
            else:
                price = current_price * 1.05
            
            # Round price
            price = self._round_step(price, self.tick_size)

            # Calculate Quantity (Target 50 USDT per trade)
            target_usdt = 50.0
            raw_quantity = target_usdt / price
            
            # Ensure min qty
            if raw_quantity < self.min_qty:
                raw_quantity = self.min_qty

            # Round quantity
            quantity = self._round_step(raw_quantity, self.step_size)

            try:
                logger.info(f"Placing {side} order for {quantity} {self.symbol} at {price}")
                response = await self.client.place_order(self.symbol, side, quantity, price)
                logger.info(f"Order placed: {response.get('orderId')}")
                
                self.order_count += 1

                # Cancel all orders every 5 orders
                if self.order_count >= 5:
                    logger.info("5 orders placed. Cancelling all open orders...")
                    cancel_response = await self.client.cancel_all_orders(self.symbol)
                    logger.info(f"Orders cancelled: {cancel_response}")
                    self.order_count = 0

            except Exception as e:
                logger.error(f"Error in trading loop: {e}")

    async def run(self):
        self.running = True
        await self._init_precision()
        # Run market data and trading loops concurrently
        await asyncio.gather(
            self.market_data_loop(),
            self.trading_loop()
        )

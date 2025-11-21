import aiohttp
import hashlib
import hmac
import time
import json
import logging
import urllib.parse
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator

logger = logging.getLogger(__name__)

class BinanceClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str, ws_url: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.ws_url = ws_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_exchange_info(self) -> Dict[str, Any]:
        """
        Fetch exchange information (filters, limits).
        """
        return await self._request('GET', '/fapi/v1/exchangeInfo')

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def _get_signature(self, query_string: str) -> str:
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    async def _request(self, method: str, endpoint: str, params: Dict[str, Any] = None, signed: bool = False) -> Dict[str, Any]:
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}

        if signed:
            params['timestamp'] = int(time.time() * 1000)
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            # Encode params to query string
            query_string = urllib.parse.urlencode(params)
            signature = self._get_signature(query_string)
            # Append signature
            full_query = f"{query_string}&signature={signature}"
            url = f"{url}?{full_query}"
            # Clear params so aiohttp doesn't append them again
            params = None

        headers = {
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        async with session.request(method, url, headers=headers, params=params) as response:
            text = await response.text()
            if response.status >= 400:
                logger.error(f"API Error {response.status}: {text}")
                raise Exception(f"Binance API Error: {text}")
            return json.loads(text)

    async def place_order(self, symbol: str, side: str, quantity: float, price: float, order_type: str = 'LIMIT', time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Place a new order.
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'price': price,
            'timeInForce': time_in_force
        }
        return await self._request('POST', '/fapi/v1/order', params=params, signed=True)

    async def cancel_all_orders(self, symbol: str) -> Dict[str, Any]:
        """
        Cancel all open orders for a symbol.
        """
        params = {
            'symbol': symbol
        }
        return await self._request('DELETE', '/fapi/v1/allOpenOrders', params=params, signed=True)

    async def listen_best_ticker(self, symbol: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Connect to WebSocket and yield best bid/ask updates.
        """
        stream_url = f"{self.ws_url}/{symbol.lower()}@bookTicker"
        
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(stream_url) as ws:
                        logger.info(f"Connected to WebSocket: {stream_url}")
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                data = json.loads(msg.data)
                                yield data
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logger.error("WebSocket connection closed with error")
                                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    async def close(self):
        if self.session:
            await self.session.close()

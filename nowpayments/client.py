import aiohttp
from config import NOWPAYMENTS_API_KEY

BASE_URL = "https://api.nowpayments.io/v1"

async def _make_request(method: str, endpoint: str, **kwargs):
    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }
    
    if "headers" in kwargs:
        headers.update(kwargs.pop("headers"))
        
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}{endpoint}"
        async with session.request(method, url, headers=headers, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

async def create_payment(price_amount: float, pay_currency: str, order_id: str, order_description: str):
    payload = {
        "price_amount": price_amount,
        "price_currency": "usd",
        "pay_currency": pay_currency,
        "order_id": str(order_id),
        "order_description": order_description
    }
    return await _make_request("POST", "/payment", json=payload)

async def get_payment_status(payment_id: str):
    return await _make_request("GET", f"/payment/{payment_id}")
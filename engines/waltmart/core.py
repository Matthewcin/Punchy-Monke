import asyncio
import random

async def process_waltmart_card(card_data: str) -> dict:
    await asyncio.sleep(1.5)
    
    simulate_outcome = random.choice(["success", "user_error", "server_error"])
    
    return {
        "status": simulate_outcome,
        "raw_data": card_data,
        "engine": "waltmart"
    }
import asyncio
import random

async def process_mygcmall_card(card_data: str) -> dict:
    await asyncio.sleep(1.5)
    
    simulate_outcome = random.choice(["success", "user_error", "server_error"])
    
    return {
        "status": simulate_outcome,
        "raw_data": card_data,
        "engine": "mygcmall"
    }
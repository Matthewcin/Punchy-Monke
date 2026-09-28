import asyncio
import random

def passes_luhn_algorithm(card_number: str) -> bool:
    digits = [int(x) for x in card_number]
    odd_sum = sum(digits[-1::-2])
    even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
    return (odd_sum + even_sum) % 10 == 0

def validate_amex_format(cc: str) -> bool:
    if not cc.isdigit():
        return False
    if len(cc) not in [15, 16]:
        return False
    if not (cc.startswith('34') or cc.startswith('37')):
        return False
    if not passes_luhn_algorithm(cc):
        return False
    return True

async def process_amex_card(card_data: str) -> dict:
    cc = card_data.split(':')[0]
    
    if not validate_amex_format(cc):
        return {
            "status": "user_error",
            "raw_data": card_data,
            "engine": "amex"
        }

    await asyncio.sleep(1.5)
    simulate_outcome = random.choice(["success", "user_error", "server_error"])
    
    return {
        "status": simulate_outcome,
        "raw_data": card_data,
        "engine": "amex"
    }
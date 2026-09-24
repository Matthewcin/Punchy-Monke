from datetime import datetime
from config import VERSION

def get_start_message(user_first_name: str, telegram_id: int, user_data: dict) -> str:
    plan = user_data.get('plan_type', 'none') if user_data else 'none'
    expiry = user_data.get('subscription_expiry') if user_data else None
    
    days_left = "0"
    if expiry and expiry > datetime.now():
        delta = expiry - datetime.now()
        days_left = str(delta.days)
        
    if plan == 'lifetime':
        days_left = "∞"
        
    is_trial = "Yes" if user_data and user_data.get('has_used_trial') else "No"

    text = (
        "<b>Welcome to Punch Checker</b> 🥊\n"
        "The premier automated utility for verifying prepaid and gift card balances in real-time.\n\n"
        "<b>Our Supported Providers are:</b>\n"
        "• American Express\n"
        "• MyGiftCardMall\n"
        "• Walmart\n\n"
        "<i>Select an option below to manage your subscription or start checking.</i>"
    )
    return text
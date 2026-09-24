from datetime import datetime

def get_profile_message(user_first_name: str, telegram_id: int, user_data: dict, checks_count: int) -> str:
    plan = user_data.get('plan_type', 'none') if user_data else 'none'
    expiry = user_data.get('subscription_expiry') if user_data else None
    role = user_data.get('role', 'user') if user_data else 'user'
    total_days = user_data.get('total_days_purchased', 0) if user_data else 0
    
    days_left = "0"
    status = "Inactive"
    
    if expiry:
        if expiry > datetime.now():
            status = "Active"
            delta = expiry - datetime.now()
            days_left = str(delta.days)
        else:
            status = "Expired"
            
    if plan == 'lifetime':
        days_left = "∞"
        status = "Active"
        
    is_trial = "Yes" if user_data and user_data.get('has_used_trial') else "No"

    text = (
        "<b>👤 User Profile</b>\n\n"
        f"<b>Name:</b> {user_first_name}\n"
        f"<b>ID:</b> <code>{telegram_id}</code>\n"
        f"<b>Role:</b> {role.capitalize()}\n\n"
        f"<b>💎 Subscription Data</b>\n"
        f"Plan: {plan.capitalize()} ({status})\n"
        f"Days Left: {days_left}\n"
        f"Lifetime Days Purchased: {total_days}\n"
        f"Trial Used: {is_trial}\n\n"
        f"<b>📊 Statistics</b>\n"
        f"Total Checks: {checks_count}"
    )
    return text
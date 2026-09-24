from config import DEV_ID, ADMIN_IDS
from datetime import datetime

def get_user_role(telegram_id: int, user_data: dict) -> str:
    if telegram_id == DEV_ID:
        return "dev"
    if telegram_id in ADMIN_IDS:
        return "admin"
    
    if not user_data:
        return "none"
        
    role = user_data.get("role", "user")
    if role in ["admin", "dev"]:
        return role
        
    plan = user_data.get("plan_type", "none")
    expiry = user_data.get("subscription_expiry")
    
    if plan != "none":
        if expiry and expiry > datetime.now():
            return "active_user"
        elif plan == "lifetime":
            return "active_user"
        else:
            return "expired_user"
            
    return "none"
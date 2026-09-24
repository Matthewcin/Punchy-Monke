from datetime import datetime
from config import ADMIN_IDS, DEV_ID

def get_user_role(telegram_id: int, user_data: dict) -> str:
    if telegram_id == DEV_ID:
        return "dev"
    
    if telegram_id in ADMIN_IDS:
        return "admin"
        
    if not user_data or user_data.get('plan_type') == 'none':
        return "none"
        
    expiry = user_data.get('subscription_expiry')
    if expiry:
        if expiry > datetime.now():
            return "active_user"
        else:
            return "expired_user"
            
    return "none"
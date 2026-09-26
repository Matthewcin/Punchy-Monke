import hmac
import hashlib
import json
from config import NOWPAYMENTS_IPN_KEY

def verify_ipn_request(data: dict, signature: str) -> bool:
    if not signature or not NOWPAYMENTS_IPN_KEY:
        return False
        
    sorted_data = json.dumps(data, separators=(',', ':'), sort_keys=True)
    expected_signature = hmac.new(
        NOWPAYMENTS_IPN_KEY.encode(),
        sorted_data.encode(),
        hashlib.sha512
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)
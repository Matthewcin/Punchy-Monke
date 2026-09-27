def get_engine_selection_message() -> str:
    return "<b>Secure Engine Selection</b>\n\nPlease select the provider you want to check:"

def get_engine_prompt_message(engine_name: str) -> str:
    return (
        f"<b>{engine_name} Checker</b>\n\n"
        "Please enter card details in the format: <code>card_number:month:year:cvv</code> ....\n\n"
        "<i>Secure Engine: All inputs are processed in volatile memory and encrypted at rest. We maintain a strict zero-log policy for full card codes.</i>"
    )

def get_checking_message(count: int) -> str:
    return f"Checking {count} Card/s..."

def get_user_error_message(engine_name: str) -> str:
    return f"Invalid Format, Please check if your {engine_name} Giftcard is Correct"

def get_server_error_message(engine_name: str) -> str:
    return (
        f"Critical Error on Engine {engine_name}\n\n"
        "Our servers are currently experiencing issues with this provider. "
        "We have notified the administrators to fix it.\n\n"
        "1 extra day will be added to daily users once the error is fixed "
        "(and more than 1 day for non-daily users depending on the downtime)."
    )
def get_subscription_menu_message(plan: str, days_left: str) -> str:
    display_plan = plan.capitalize()
    if plan.startswith("custom_"):
        parts = plan.split("_")
        display_plan = f"Custom ({parts[2]} {parts[1].capitalize()})"
        
    text = (
        "<b>💎 Subscription Hub</b>\n\n"
        f"Current Plan: <b>{display_plan}</b>\n"
        f"Time Remaining: <b>{days_left}</b>\n\n"
        "Choose an option below to manage your subscription or redeem a code."
    )
    return text

def get_redeem_prompt_message() -> str:
    return "<b>🏷 Redeem Code</b>\n\nPlease enter your activation code below:"

def get_redeem_success_message(plan: str) -> str:
    return f"✅ <b>Code Redeemed Successfully!</b>\n\nYou have been granted the <b>{plan}</b> plan."

def get_redeem_error_message(reason: str) -> str:
    return f"❌ <b>Invalid Code</b>\n\nReason: {reason}\n\nPlease try again or go back to the menu."

def get_generate_code_prompt() -> str:
    return "<b>🛠 Generate Code</b>\n\nPlease select the plan type for the new code:"

def get_generate_uses_prompt(plan: str) -> str:
    return f"<b>🛠 Generate Code ({plan})</b>\n\nHow many users can redeem this code? (Send a number from 1 to 9999):"

def get_custom_duration_type_prompt() -> str:
    return "<b>🛠 Generate Custom Code</b>\n\nDo you want to set the duration in Hours or Days?"

def get_custom_duration_amount_prompt(unit: str) -> str:
    return f"<b>🛠 Generate Custom Code</b>\n\nHow many {unit.lower()} should this code grant? (Send a number):"

def get_generate_success_message(code: str, plan: str, uses: int) -> str:
    display_plan = plan.capitalize()
    if plan.startswith("custom_"):
        parts = plan.split("_")
        display_plan = f"Custom ({parts[2]} {parts[1].capitalize()})"
        
    return (
        "✅ <b>Code Generated!</b>\n\n"
        f"<b>Code:</b> <code>{code}</code>\n"
        f"<b>Plan:</b> {display_plan}\n"
        f"<b>Max Uses:</b> {uses}"
    )
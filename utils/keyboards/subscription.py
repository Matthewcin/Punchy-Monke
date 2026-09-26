from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_subscription_keyboard(has_active_plan: bool) -> InlineKeyboardMarkup:
    buttons = []
    
    if not has_active_plan:
        buttons.append([InlineKeyboardButton(text="🎁 Free Trial", callback_data="sub_free_trial")])
        
    buttons.append([InlineKeyboardButton(text="💳 Pay with Crypto", callback_data="sub_pay_crypto")])
    buttons.append([InlineKeyboardButton(text="🏷 Redeem Code", callback_data="sub_redeem_code")])
    buttons.append([InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_redeem_retry_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Retry", callback_data="sub_redeem_code")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_subscription")]
    ])

def get_crypto_plans_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Daily ($2)", callback_data="crypto_plan_daily")],
        [InlineKeyboardButton(text="Weekly ($10)", callback_data="crypto_plan_weekly")],
        [InlineKeyboardButton(text="Monthly ($30)", callback_data="crypto_plan_monthly")],
        [InlineKeyboardButton(text="Lifetime ($150)", callback_data="crypto_plan_lifetime")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_subscription")]
    ])

def get_crypto_currencies_keyboard(plan: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="LTC (Litecoin)", callback_data=f"crypto_pay_{plan}_ltc")],
        [InlineKeyboardButton(text="USDT (TRC20)", callback_data=f"crypto_pay_{plan}_usdttrc20")],
        [InlineKeyboardButton(text="TRX (Tron)", callback_data=f"crypto_pay_{plan}_trx")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="sub_pay_crypto")]
    ])

def get_payment_status_keyboard(payment_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Check Status", callback_data=f"crypto_check_{payment_id}")],
        [InlineKeyboardButton(text="🔙 Cancel & Go Back", callback_data="menu_subscription")]
    ])
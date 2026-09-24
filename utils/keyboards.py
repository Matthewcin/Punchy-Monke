from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard(role: str) -> InlineKeyboardMarkup:
    buttons = []

    if role in ["admin", "dev", "active_user", "expired_user"]:
        buttons.append([InlineKeyboardButton(text="💳 Check Gift Card", callback_data="menu_check")])
        buttons.append([
            InlineKeyboardButton(text="👤 Profile", callback_data="menu_profile"),
            InlineKeyboardButton(text="💎 Subscription", callback_data="menu_subscription"),
            InlineKeyboardButton(text="📦 Orders", callback_data="menu_orders")
        ])
        if role in ["admin", "dev"]:
            buttons.append([InlineKeyboardButton(text="📋 Latest Checks", callback_data="menu_latest_checks")])
            buttons.append([InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="menu_admin")])
            
    elif role == "none":
        buttons.append([InlineKeyboardButton(text="🎁 Free Trial", callback_data="menu_free_trial")])
        buttons.append([InlineKeyboardButton(text="💎 Subscription", callback_data="menu_subscription")])

    if role == "dev":
        buttons.append([InlineKeyboardButton(text="📝 Add Log", callback_data="dev_add_log")])
        buttons.append([InlineKeyboardButton(text="🤖 Bot Status", callback_data="dev_bot_status")])
        buttons.append([InlineKeyboardButton(text="🚧 Maintenance Mode", callback_data="dev_maintenance")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
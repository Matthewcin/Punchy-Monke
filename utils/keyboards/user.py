from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard(role: str, has_checks: bool, orders_emoji: str = "📦", has_orders: bool = False, has_used_trial: bool = False) -> InlineKeyboardMarkup:
    buttons = []

    if role in ["admin", "dev", "active_user", "expired_user"]:
        buttons.append([InlineKeyboardButton(text="💳 Check Gift Card", callback_data="menu_check")])
        
        if has_checks:
            buttons.append([InlineKeyboardButton(text="📋 Latest Checks", callback_data="menu_latest_checks")])
            
        buttons.append([
            InlineKeyboardButton(text="👤 Profile", callback_data="menu_profile"),
            InlineKeyboardButton(text="💎 Subscription", callback_data="menu_subscription"),
            InlineKeyboardButton(text=f"{orders_emoji} Orders", callback_data="menu_orders")
        ])
        
        if has_orders:
            buttons.append([InlineKeyboardButton(text="🎫 Support", callback_data="menu_support")])
        
        admin_dev_row = []
        if role in ["admin", "dev"]:
            admin_dev_row.append(InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="menu_admin"))
            
        if role == "dev":
            admin_dev_row.append(InlineKeyboardButton(text="👨‍💻 Dev Panel", callback_data="menu_dev"))
            
        if admin_dev_row:
            buttons.append(admin_dev_row)
            
    elif role == "none":
        if not has_used_trial:
            buttons.append([InlineKeyboardButton(text="🎁 Free Trial", callback_data="menu_free_trial")])
            
        if has_checks:
            buttons.append([InlineKeyboardButton(text="📋 Latest Checks", callback_data="menu_latest_checks")])
            
        buttons.append([
            InlineKeyboardButton(text="💎 Subscription", callback_data="menu_subscription"),
            InlineKeyboardButton(text=f"{orders_emoji} Orders", callback_data="menu_orders")
        ])
        
        if has_orders:
            buttons.append([InlineKeyboardButton(text="🎫 Support", callback_data="menu_support")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")]
    ])

def get_pagination_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    nav_buttons = []
    
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"checks_page_{current_page - 1}"))
    
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"checks_page_{current_page + 1}"))
        
    if nav_buttons:
        buttons.append(nav_buttons)
        
    buttons.append([InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_trial_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Claim 24h Trial", callback_data="free_trial_confirm")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="go_back")]
    ])
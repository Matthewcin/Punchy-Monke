from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard(role: str, has_checks: bool) -> InlineKeyboardMarkup:
    buttons = []

    if role in ["admin", "dev", "active_user", "expired_user"]:
        buttons.append([InlineKeyboardButton(text="💳 Check Gift Card", callback_data="menu_check")])
        buttons.append([
            InlineKeyboardButton(text="👤 Profile", callback_data="menu_profile"),
            InlineKeyboardButton(text="💎 Subscription", callback_data="menu_subscription"),
            InlineKeyboardButton(text="📦 Orders", callback_data="menu_orders")
        ])
        
        admin_dev_row = []
        if role in ["admin", "dev"]:
            if has_checks:
                buttons.append([InlineKeyboardButton(text="📋 Latest Checks", callback_data="menu_latest_checks")])
            admin_dev_row.append(InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="menu_admin"))
            
        if role == "dev":
            admin_dev_row.append(InlineKeyboardButton(text="👨‍💻 Dev Panel", callback_data="menu_dev"))
            
        if admin_dev_row:
            buttons.append(admin_dev_row)
            
    elif role == "none":
        buttons.append([InlineKeyboardButton(text="🎁 Free Trial", callback_data="menu_free_trial")])
        buttons.append([InlineKeyboardButton(text="💎 Subscription", callback_data="menu_subscription")])

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

def get_admin_panel_keyboard(role: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🐛 DevLogs", callback_data="admin_devlogs_page_1")]
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_dev_panel_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📝 Add Log", callback_data="dev_add_log")],
        [InlineKeyboardButton(text="🎭 Simulate Roles", callback_data="dev_simulate_roles")],
        [InlineKeyboardButton(text="🤖 Bot Status", callback_data="dev_bot_status")],
        [InlineKeyboardButton(text="🚧 Maintenance Mode", callback_data="dev_maintenance")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_role_simulation_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="👤 User (None)", callback_data="sim_role_none")],
        [InlineKeyboardButton(text="🟢 Active User", callback_data="sim_role_active_user")],
        [InlineKeyboardButton(text="🔴 Expired User", callback_data="sim_role_expired_user")],
        [InlineKeyboardButton(text="⚙️ Admin", callback_data="sim_role_admin")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_dev")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_devlog_dates_keyboard(dates, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    
    for record in dates:
        date_str = record['log_date'].strftime("%Y-%m-%d")
        buttons.append([InlineKeyboardButton(text=f"📅 {date_str} Log", callback_data=f"admin_devlog_view_{date_str}")])

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"admin_devlogs_page_{current_page - 1}"))
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"admin_devlogs_page_{current_page + 1}"))
        
    if nav_buttons:
        buttons.append(nav_buttons)
        
    buttons.append([InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_devlog_message_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Go Back to Logs", callback_data="admin_devlogs_page_1")],
        [InlineKeyboardButton(text="⚙️ Go Back to Admin Panel", callback_data="menu_admin")]
    ])
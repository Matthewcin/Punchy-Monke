from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_dev_panel_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📝 Add Log", callback_data="dev_add_log")],
        [InlineKeyboardButton(text="🤖 Bot Status", callback_data="dev_bot_status")],
        [InlineKeyboardButton(text="🚧 Maintenance Mode", callback_data="dev_maintenance")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")]
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

def get_maintenance_keyboard(is_active: bool) -> InlineKeyboardMarkup:
    status_btn = "🔴 Turn OFF" if is_active else "🟢 Turn ON"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=status_btn, callback_data="dev_maint_toggle")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_dev")]
    ])

def get_maintenance_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data="dev_maint_confirm_yes"),
            InlineKeyboardButton(text="❌ No", callback_data="dev_maint_confirm_no")
        ]
    ])
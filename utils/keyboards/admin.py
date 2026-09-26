from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_panel_keyboard(role: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🧾 Orders", callback_data="admin_check_orders"),
            InlineKeyboardButton(text="🛠 Codes", callback_data="admin_generate_code")
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="🎭 Roles", callback_data="admin_simulate_roles")
        ],
        [
            InlineKeyboardButton(text="🐛 DevLogs", callback_data="admin_devlogs_page_1")
        ],
        [
            InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_role_simulation_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="👤 User (None)", callback_data="sim_role_none")],
        [InlineKeyboardButton(text="🟢 Active User", callback_data="sim_role_active_user")],
        [InlineKeyboardButton(text="🔴 Expired User", callback_data="sim_role_expired_user")],
        [InlineKeyboardButton(text="⚙️ Admin", callback_data="sim_role_admin")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_admin")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_broadcast_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 All Users", callback_data="bc_target_all")],
        [InlineKeyboardButton(text="⏳ Expired Users", callback_data="bc_target_expired")],
        [InlineKeyboardButton(text="🪙 Users with Active Subscription", callback_data="bc_target_active")],
        [InlineKeyboardButton(text="🔒 New Users", callback_data="bc_target_new")],
        [InlineKeyboardButton(text="👑 Used Trial Users", callback_data="bc_target_trial")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_admin")]
    ])

def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data="bc_confirm_yes"),
            InlineKeyboardButton(text="❌ No", callback_data="bc_confirm_no")
        ]
    ])

def get_generate_code_plans_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Trial", callback_data="gen_plan_trial"), InlineKeyboardButton(text="Daily", callback_data="gen_plan_daily")],
        [InlineKeyboardButton(text="Weekly", callback_data="gen_plan_weekly"), InlineKeyboardButton(text="Monthly", callback_data="gen_plan_monthly")],
        [InlineKeyboardButton(text="Lifetime", callback_data="gen_plan_lifetime"), InlineKeyboardButton(text="Custom", callback_data="gen_plan_custom")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="menu_admin")]
    ])

def get_custom_duration_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Hours", callback_data="gen_custom_hours"), InlineKeyboardButton(text="Days", callback_data="gen_custom_days")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="admin_generate_code")]
    ])
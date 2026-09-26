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
        [InlineKeyboardButton(text="🐛 DevLogs", callback_data="admin_devlogs_page_1")],
        [InlineKeyboardButton(text="🎭 Simulate Roles", callback_data="admin_simulate_roles")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🛠 Generate Code", callback_data="admin_generate_code")]
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_dev_panel_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📝 Add Log", callback_data="dev_add_log")],
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
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_admin")]
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
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_user_orders_keyboard(orders: list, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    
    for o in orders:
        status = o['payment_status']
        if status in ['completed', 'finished']:
            emoji = "🟩"
        elif status in ['pending', 'waiting', 'confirming', 'sending']:
            emoji = "🟧"
        elif status in ['failed', 'expired', 'error', 'timeout']:
            emoji = "🟥"
        else:
            emoji = "🧾"
            
        btn_text = f"{emoji} {o['plan_purchased'].capitalize()} - ${o['amount']}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"user_order_view_{o['transaction_id']}")])

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"user_orders_page_{current_page - 1}"))
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"user_orders_page_{current_page + 1}"))
        
    if nav_buttons:
        buttons.append(nav_buttons)
        
    buttons.append([InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_user_order_view_keyboard(page: int, status: str = None, plan: str = None) -> InlineKeyboardMarkup:
    buttons = []
    
    if status in ['failed', 'expired', 'error', 'timeout'] and plan:
        buttons.append([InlineKeyboardButton(text="🔄 Retry Order", callback_data=f"crypto_plan_{plan}")])
        
    buttons.append([InlineKeyboardButton(text="🔙 Back to Orders", callback_data=f"user_orders_page_{page}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_orders_menu_keyboard(stats: dict) -> InlineKeyboardMarkup:
    c_count = stats['completed']['count']
    p_count = stats['pending']['count']
    f_count = stats['failed']['count']
    c_amt = stats['completed']['amount']
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🟩 Completed ({c_count}) | ${c_amt:.2f}", callback_data="admin_orders_completed_page_1")],
        [InlineKeyboardButton(text=f"🟧 Pending ({p_count})", callback_data="admin_orders_pending_page_1")],
        [InlineKeyboardButton(text=f"🟥 Failed/Errors ({f_count})", callback_data="admin_orders_failed_page_1")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_admin")]
    ])

def get_admin_orders_list_keyboard(status: str, orders: list, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    
    for o in orders:
        btn_text = f"TXID: {o['transaction_id'][:8]}... | {o['plan_purchased'].capitalize()}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"admin_order_view_{o['transaction_id']}")])

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"admin_orders_{status}_page_{current_page - 1}"))
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"admin_orders_{status}_page_{current_page + 1}"))
        
    if nav_buttons:
        buttons.append(nav_buttons)
        
    buttons.append([InlineKeyboardButton(text="🔙 Categories", callback_data="admin_check_orders")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_order_view_keyboard(status: str, page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to List", callback_data=f"admin_orders_{status}_page_{page}")]
    ])
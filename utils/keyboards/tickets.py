from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_support_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Create Ticket", callback_data="ticket_create_menu")],
        [InlineKeyboardButton(text="📚 My Tickets", callback_data="ticket_user_list_1")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")]
    ])

def get_support_categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Payment Issue", callback_data="ticket_new_payment")],
        [InlineKeyboardButton(text="🐛 Report a Bug", callback_data="ticket_new_bug")],
        [InlineKeyboardButton(text="❌ Error / Issue", callback_data="ticket_new_error")],
        [InlineKeyboardButton(text="❓ General Help", callback_data="ticket_new_help")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_support")]
    ])

def get_support_active_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁️ View Active Ticket", callback_data=f"ticket_user_view_{ticket_id}")],
        [InlineKeyboardButton(text="📚 Ticket History", callback_data="ticket_user_list_1")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")]
    ])

def get_ticket_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data="ticket_confirm_yes"),
            InlineKeyboardButton(text="❌ No", callback_data="ticket_confirm_no")
        ]
    ])

def get_user_tickets_list_keyboard(tickets: list, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    
    for t in tickets:
        status_emojis = {'unsolved': '🟧', 'readed': '🟦', 'replied': '🟪', 'solved': '🟩'}
        emoji = status_emojis.get(t['status'], '🎫')
        btn_text = f"{emoji} {t['ticket_type'].capitalize()} - #{t['ticket_id']}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"ticket_user_view_{t['ticket_id']}")])

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"ticket_user_list_{current_page - 1}"))
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"ticket_user_list_{current_page + 1}"))
        
    if nav_buttons:
        buttons.append(nav_buttons)
        
    buttons.append([InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_support")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_user_ticket_action_keyboard(ticket_id: int, status: str) -> InlineKeyboardMarkup:
    buttons = []
    if status == 'replied':
        buttons.append([InlineKeyboardButton(text="✍️ Reply to Admin", callback_data=f"ticket_user_reply_{ticket_id}")])
        buttons.append([InlineKeyboardButton(text="✅ Mark as Solved", callback_data=f"ticket_user_solve_{ticket_id}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 Go Back", callback_data="ticket_user_list_1")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_tickets_main_keyboard(stats: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 Payment Tickets ({stats.get('payment', 0)})", callback_data="admin_ticket_cat_payment_1")],
        [InlineKeyboardButton(text=f"🐛 Bug Tickets ({stats.get('bug', 0)})", callback_data="admin_ticket_cat_bug_1")],
        [InlineKeyboardButton(text=f"❌ Error Tickets ({stats.get('error', 0)})", callback_data="admin_ticket_cat_error_1")],
        [InlineKeyboardButton(text=f"❓ Help Tickets ({stats.get('help', 0)})", callback_data="admin_ticket_cat_help_1")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_admin")]
    ])

def get_admin_tickets_list_keyboard(ticket_type: str, tickets: list, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    
    for t in tickets:
        status_emojis = {'unsolved': '🟧', 'readed': '🟦', 'replied': '🟪'}
        emoji = status_emojis.get(t['status'], '🎫')
        btn_text = f"{emoji} ID: #{t['ticket_id']}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"admin_ticket_view_{t['ticket_id']}")])

    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"admin_ticket_cat_{ticket_type}_{current_page - 1}"))
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"admin_ticket_cat_{ticket_type}_{current_page + 1}"))
        
    if nav_buttons:
        buttons.append(nav_buttons)
        
    buttons.append([InlineKeyboardButton(text="🔙 Categories", callback_data="admin_check_tickets")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_ticket_action_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✍️ Reply Ticket", callback_data=f"admin_ticket_reply_{ticket_id}"),
            InlineKeyboardButton(text="👀 Mark as Read", callback_data=f"admin_ticket_read_{ticket_id}")
        ],
        [InlineKeyboardButton(text="🗑 Discard Ticket", callback_data=f"admin_ticket_discard_{ticket_id}")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="admin_check_tickets")]
    ])

def get_admin_discard_confirm_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data=f"admin_ticket_del_yes_{ticket_id}"),
            InlineKeyboardButton(text="❌ No", callback_data=f"admin_ticket_del_no_{ticket_id}")
        ]
    ])

def get_admin_reply_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data="admin_ticket_rep_yes"),
            InlineKeyboardButton(text="❌ No", callback_data="admin_ticket_rep_no")
        ]
    ])

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="menu_support")]
    ])
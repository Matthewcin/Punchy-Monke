from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_log_engines_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Amex", callback_data="logs_engine_amex")],
        [InlineKeyboardButton(text="Waltmart", callback_data="logs_engine_waltmart")],
        [InlineKeyboardButton(text="MyGiftCardMall", callback_data="logs_engine_mygcmall")],
        [InlineKeyboardButton(text="All Providers", callback_data="logs_engine_all")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")]
    ])

def get_batches_keyboard(batches: list, current_page: int, total_pages: int, provider: str) -> InlineKeyboardMarkup:
    buttons = []
    for b in batches:
        date_str = b['check_date'].strftime("%y/%m/%d")
        text = f"{b['provider']} | {date_str} | {b['total_cards']} Checked"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"view_batch_{b['batch_id']}_{provider}")])
    
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"batches_page_{provider}_{current_page - 1}"))
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"batches_page_{provider}_{current_page + 1}"))
        
    if nav_buttons:
        buttons.append(nav_buttons)
        
    buttons.append([InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_latest_checks")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_batch_view_keyboard(batch_id: str, success_count: int, provider: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ Success ({success_count})", callback_data="ignore_btn")],
        [InlineKeyboardButton(text="📥 Download Log", callback_data=f"download_batch_{batch_id}")],
        [InlineKeyboardButton(text="🔙 Back to Logs", callback_data=f"logs_engine_{provider}")]
    ])
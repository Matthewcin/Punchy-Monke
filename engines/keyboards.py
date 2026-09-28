from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_engines_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗽 Amex", callback_data="engine_select_amex")],
        [InlineKeyboardButton(text="🔆 Waltmart", callback_data="engine_select_waltmart")],
        [InlineKeyboardButton(text="🛍️ MyGiftCardMall", callback_data="engine_select_mygcmall")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="go_back")]
    ])

def get_checker_error_keyboard(engine: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄️ Retry", callback_data=f"engine_select_{engine}")],
        [InlineKeyboardButton(text="⛑️ Contact Support", callback_data="ticket_create_menu")],
        [InlineKeyboardButton(text="⚙️ Select Another Engine", callback_data="menu_check")]
    ])
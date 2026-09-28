import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repo_users import get_user
from database.repo_settings import get_setting, set_setting
from utils.roles import get_user_role

admin_modify_router = Router()

class AdminModifyState(StatesGroup):
    waiting_for_price = State()
    waiting_for_trial = State()

def get_modify_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Set Prices", callback_data="admin_modify_prices")],
        [InlineKeyboardButton(text="⏲ Set Trial Time", callback_data="admin_modify_trial")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="menu_admin")]
    ])

def get_modify_prices_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Daily", callback_data="admin_price_daily"),
         InlineKeyboardButton(text="Weekly", callback_data="admin_price_weekly")],
        [InlineKeyboardButton(text="Monthly", callback_data="admin_price_monthly"),
         InlineKeyboardButton(text="Lifetime", callback_data="admin_price_lifetime")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="admin_modify_menu")]
    ])

@admin_modify_router.callback_query(F.data == "admin_modify_menu")
async def cb_admin_modify_menu(callback: CallbackQuery, state: FSMContext, db_pool):
    await state.clear()
    user_data = await get_user(db_pool, callback.from_user.id)
    if get_user_role(callback.from_user.id, user_data) not in ["admin", "dev"]:
        return
        
    await callback.message.edit_text(
        "<b>Modify Bot Settings</b>\n\nSelect an option to modify:",
        reply_markup=get_modify_menu_keyboard()
    )

@admin_modify_router.callback_query(F.data == "admin_modify_prices")
async def cb_admin_modify_prices(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    if get_user_role(callback.from_user.id, user_data) not in ["admin", "dev"]:
        return
        
    await callback.message.edit_text(
        "<b>Set Plan Prices</b>\n\nSelect the plan you want to modify:",
        reply_markup=get_modify_prices_keyboard()
    )

@admin_modify_router.callback_query(F.data.startswith("admin_price_"))
async def cb_admin_price_select(callback: CallbackQuery, state: FSMContext, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    if get_user_role(callback.from_user.id, user_data) not in ["admin", "dev"]:
        return
        
    plan = callback.data.replace("admin_price_", "")
    current_price = await get_setting(db_pool, f"price_{plan}")
    current_price = current_price if current_price else "Not set"
    
    await state.update_data(modifying_plan=plan)
    await state.set_state(AdminModifyState.waiting_for_price)
    
    await callback.message.edit_text(
        f"<b>Modify {plan.capitalize()} Price</b>\n\nCurrent price: <code>{current_price}</code>\n\nEnter the new price (numbers only):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Cancel", callback_data="admin_modify_prices")]])
    )

@admin_modify_router.message(AdminModifyState.waiting_for_price)
async def process_new_price(message: Message, state: FSMContext, db_pool):
    data = await state.get_data()
    plan = data.get("modifying_plan")
    
    try:
        new_price = float(message.text)
    except ValueError:
        await message.answer("Invalid format. Please enter a valid number.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Cancel", callback_data="admin_modify_prices")]]))
        return
        
    await set_setting(db_pool, f"price_{plan}", str(new_price))
    await state.clear()
    
    await message.answer(
        f"Price for <b>{plan.capitalize()}</b> successfully updated to <code>{new_price}</code>.",
        reply_markup=get_modify_prices_keyboard()
    )

@admin_modify_router.callback_query(F.data == "admin_modify_trial")
async def cb_admin_modify_trial(callback: CallbackQuery, state: FSMContext, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    if get_user_role(callback.from_user.id, user_data) not in ["admin", "dev"]:
        return
        
    current_trial = await get_setting(db_pool, "trial_hours")
    current_trial = current_trial if current_trial else "24"
    await state.set_state(AdminModifyState.waiting_for_trial)
    
    await callback.message.edit_text(
        f"<b>Modify Trial Duration</b>\n\nCurrent duration: <code>{current_trial} hours</code>\n\nEnter the new duration in hours (e.g. 12, 24, 48):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Cancel", callback_data="admin_modify_menu")]])
    )

@admin_modify_router.message(AdminModifyState.waiting_for_trial)
async def process_new_trial(message: Message, state: FSMContext, db_pool):
    try:
        new_hours = int(message.text)
    except ValueError:
        await message.answer("Invalid format. Please enter a whole number (e.g. 24).", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Cancel", callback_data="admin_modify_menu")]]))
        return
        
    await set_setting(db_pool, "trial_hours", str(new_hours))
    await state.clear()
    
    await message.answer(
        f"Trial duration successfully updated to <code>{new_hours} hours</code>.",
        reply_markup=get_modify_menu_keyboard()
    )
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repo_users import get_user, grant_subscription
from database.repo_codes import get_code, check_user_redeemed, redeem_code_db
from utils.keyboards import get_subscription_keyboard, get_back_keyboard, get_redeem_retry_keyboard
from utils.messages.subscription import get_subscription_menu_message, get_redeem_prompt_message, get_redeem_success_message, get_redeem_error_message

sub_router = Router()

class RedeemState(StatesGroup):
    waiting_for_code = State()

@sub_router.callback_query(F.data == "menu_subscription")
async def cb_subscription_menu(callback: CallbackQuery, db_pool, state: FSMContext):
    await state.clear()
    user_data = await get_user(db_pool, callback.from_user.id)
    
    plan = user_data.get('plan_type', 'none') if user_data else 'none'
    expiry = user_data.get('subscription_expiry') if user_data else None
    
    days_left = "0"
    has_active = False
    
    if expiry and expiry > datetime.now():
        delta = expiry - datetime.now()
        days = delta.days
        hours = delta.seconds // 3600
        days_left = f"{days} Days ({hours} Hours)"
        has_active = True
        
    if plan == 'lifetime':
        days_left = "∞"
        has_active = True
        
    text = get_subscription_menu_message(plan, days_left)
    keyboard = get_subscription_keyboard(has_active)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@sub_router.callback_query(F.data == "sub_redeem_code")
async def cb_redeem_code_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RedeemState.waiting_for_code)
    text = get_redeem_prompt_message()
    await callback.message.edit_text(text, reply_markup=get_back_keyboard())

@sub_router.message(RedeemState.waiting_for_code)
async def process_redeem_code(message: Message, state: FSMContext, db_pool):
    code_input = message.text.strip()
    code_data = await get_code(db_pool, code_input)
    
    if not code_data:
        text = get_redeem_error_message("This code does not exist.")
        await message.answer(text, reply_markup=get_redeem_retry_keyboard())
        await state.clear()
        return
        
    if code_data['uses_count'] >= code_data['max_uses']:
        text = get_redeem_error_message("This code has reached its maximum uses.")
        await message.answer(text, reply_markup=get_redeem_retry_keyboard())
        await state.clear()
        return
        
    already_redeemed = await check_user_redeemed(db_pool, code_data['id'], message.from_user.id)
    if already_redeemed:
        text = get_redeem_error_message("You have already redeemed this exact code.")
        await message.answer(text, reply_markup=get_redeem_retry_keyboard())
        await state.clear()
        return

    plan_type = code_data['plan_type']
    days_to_grant = 0
    hours_to_grant = 0
    is_trial = False
    display_plan = plan_type.capitalize()
    
    if plan_type == 'trial':
        days_to_grant = 1
        is_trial = True
    elif plan_type == 'daily':
        days_to_grant = 1
    elif plan_type == 'weekly':
        days_to_grant = 7
    elif plan_type == 'monthly':
        days_to_grant = 30
    elif plan_type == 'lifetime':
        days_to_grant = 9999
    elif plan_type.startswith('custom_'):
        parts = plan_type.split('_')
        unit = parts[1]
        amount = int(parts[2])
        if unit == 'days':
            days_to_grant = amount
            display_plan = f"Custom ({amount} Days)"
        elif unit == 'hours':
            hours_to_grant = amount
            display_plan = f"Custom ({amount} Hours)"
            
    await redeem_code_db(db_pool, code_data['id'], message.from_user.id)
    await grant_subscription(db_pool, message.from_user.id, days_to_grant, plan_type, is_trial, hours_to_grant)
    
    text = get_redeem_success_message(display_plan)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Go Back to Menu", callback_data="menu_subscription")]
    ])
    
    await message.answer(text, reply_markup=keyboard)
    await state.clear()
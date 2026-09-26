from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repo_users import get_user, grant_subscription
from database.repo_codes import get_code, check_user_redeemed, redeem_code_db
from utils.keyboards import get_subscription_keyboard, get_back_keyboard, get_redeem_retry_keyboard, get_crypto_plans_keyboard, get_crypto_currencies_keyboard, get_payment_status_keyboard
from utils.messages.subscription import get_subscription_menu_message, get_redeem_prompt_message, get_redeem_success_message, get_redeem_error_message
from nowpayments.client import create_payment, get_payment_status

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

@sub_router.callback_query(F.data == "sub_pay_crypto")
async def cb_pay_crypto_plans(callback: CallbackQuery):
    text = "<b>🛒 Choose a Plan</b>\n\nSelect the subscription you want to purchase with Crypto:"
    await callback.message.edit_text(text, reply_markup=get_crypto_plans_keyboard())

@sub_router.callback_query(F.data.startswith("crypto_plan_"))
async def cb_pay_crypto_currency(callback: CallbackQuery):
    plan = callback.data.replace("crypto_plan_", "")
    text = f"<b>🛒 Plan: {plan.capitalize()}</b>\n\nSelect the cryptocurrency you want to pay with:"
    await callback.message.edit_text(text, reply_markup=get_crypto_currencies_keyboard(plan))

@sub_router.callback_query(F.data.startswith("crypto_pay_"))
async def cb_pay_crypto_generate(callback: CallbackQuery, db_pool):
    parts = callback.data.split("_")
    plan = parts[2]
    currency = parts[3]
    
    prices = {"daily": 2.0, "weekly": 10.0, "monthly": 30.0, "lifetime": 150.0}
    amount_usd = prices.get(plan, 2.0)
    
    await callback.message.edit_text("⏳ Generating payment invoice via NOWPayments...")
    
    order_id = f"{callback.from_user.id}_{plan}_{int(datetime.now().timestamp())}"
    order_description = f"Punchy Monke - {plan.capitalize()} Plan"
    
    try:
        resp = await create_payment(amount_usd, currency, order_id, order_description)
        
        pay_address = resp.get("pay_address")
        pay_amount = resp.get("pay_amount")
        payment_id = str(resp.get("payment_id"))
        
        if not pay_address:
            await callback.message.edit_text("❌ Error generating invoice. Please try again.", reply_markup=get_back_keyboard())
            return
            
        async with db_pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO payments (transaction_id, telegram_id, amount, plan_purchased, payment_status)
                VALUES ($1, $2, $3, $4, $5)
            ''', payment_id, callback.from_user.id, amount_usd, plan, 'pending')
            
        text = (
            "<b>🧾 Payment Invoice Generated</b>\n\n"
            f"<b>Plan:</b> {plan.capitalize()}\n"
            f"<b>Amount to send:</b> <code>{pay_amount}</code> <b>{currency.upper()}</b>\n"
            f"<b>Deposit Address:</b>\n<code>{pay_address}</code>\n\n"
            "<i>⚠️ Send the EXACT amount to the address above. Do not include network fees in the total. Click 'Check Status' after sending.</i>"
        )
        await callback.message.edit_text(text, reply_markup=get_payment_status_keyboard(payment_id))
        
    except Exception as e:
        await callback.message.edit_text(f"❌ API Error: {str(e)}", reply_markup=get_back_keyboard())

@sub_router.callback_query(F.data.startswith("crypto_check_"))
async def cb_pay_crypto_check(callback: CallbackQuery, db_pool):
    payment_id = callback.data.replace("crypto_check_", "")
    
    try:
        status_data = await get_payment_status(payment_id)
        current_status = status_data.get("payment_status", "unknown")
        
        if current_status in ["finished", "confirmed", "sending"]:
            async with db_pool.acquire() as conn:
                record = await conn.fetchrow('SELECT payment_status, plan_purchased FROM payments WHERE transaction_id = $1', payment_id)
                
                if record and record['payment_status'] != 'completed':
                    await conn.execute('UPDATE payments SET payment_status = $1 WHERE transaction_id = $2', 'completed', payment_id)
                    plan = record['plan_purchased']
                    
                    days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'lifetime': 9999}
                    days = days_map.get(plan, 0)
                    
                    await grant_subscription(db_pool, callback.from_user.id, days, plan, False, 0)
                    
                    text = f"✅ <b>Payment Completed!</b>\n\nYou have been granted the <b>{plan.capitalize()}</b> plan. Thank you!"
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back to Menu", callback_data="menu_subscription")]])
                    await callback.message.edit_text(text, reply_markup=kb)
                else:
                    await callback.answer("This payment has already been credited to your account.", show_alert=True)
        else:
            await callback.answer(f"Status: {current_status.upper()}. The network is still processing the transaction. Please wait...", show_alert=True)
            
    except Exception:
        await callback.answer("Unable to check status. Try again in a few seconds.", show_alert=True)
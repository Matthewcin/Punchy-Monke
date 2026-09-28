from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.repo_users import get_user
from database.repo_settings import get_setting
from utils.keyboards.user import get_trial_confirm_keyboard, get_back_keyboard

trial_router = Router()

@trial_router.callback_query(F.data == "menu_free_trial")
async def cb_menu_free_trial(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    
    if user_data.get('has_used_trial'):
        await callback.answer("You have already used your free trial.", show_alert=True)
        return
        
    trial_hours_str = await get_setting(db_pool, "trial_hours")
    trial_hours = int(trial_hours_str) if trial_hours_str else 24
        
    text = (
        "<b>Free Trial Claim</b>\n\n"
        "Are you sure you want to claim your free trial?\n\n"
        "<b>Important Details:</b>\n"
        f"• The trial lasts exactly {trial_hours} hours.\n"
        "• It can only be claimed once per account.\n"
        f"• Any checks performed during the trial will be <b>automatically deleted</b> after {trial_hours} hours and will not be saved permanently.\n\n"
        "Do you want to activate it now?"
    )
    
    await callback.message.edit_text(text, reply_markup=get_trial_confirm_keyboard())

@trial_router.callback_query(F.data == "free_trial_confirm")
async def cb_free_trial_confirm(callback: CallbackQuery, db_pool):
    user_data = await get_user(db_pool, callback.from_user.id)
    
    if user_data.get('has_used_trial'):
        await callback.answer("You have already used your free trial.", show_alert=True)
        return
        
    trial_hours_str = await get_setting(db_pool, "trial_hours")
    trial_hours = int(trial_hours_str) if trial_hours_str else 24
        
    async with db_pool.acquire() as conn:
        await conn.execute(f'''
            UPDATE users 
            SET role = 'active_user', 
                plan_type = 'trial', 
                has_used_trial = TRUE, 
                subscription_expiry = CURRENT_TIMESTAMP + INTERVAL '{trial_hours} hours'
            WHERE telegram_id = $1
        ''', callback.from_user.id)
        
    await callback.message.edit_text(
        f"<b>Trial Activated Successfully!</b>\n\n"
        f"You now have {trial_hours} hours of access to the Secure Engine.\n"
        "Remember that your check history will auto-delete after the trial period.",
        reply_markup=get_back_keyboard()
    )
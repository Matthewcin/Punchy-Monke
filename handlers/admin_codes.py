import random
import string
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repo_users import get_user
from database.repo_codes import create_code
from utils.roles import get_user_role
from utils.keyboards import get_generate_code_plans_keyboard, get_custom_duration_type_keyboard
from utils.messages.subscription import get_generate_code_prompt, get_generate_uses_prompt, get_generate_success_message, get_custom_duration_type_prompt, get_custom_duration_amount_prompt

admin_codes_router = Router()

class GenerateCodeState(StatesGroup):
    waiting_for_custom_amount = State()
    waiting_for_uses = State()

@admin_codes_router.callback_query(F.data == "admin_generate_code")
async def cb_admin_generate_code(callback: CallbackQuery, db_pool, state: FSMContext):
    await state.clear()
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role not in ["admin", "dev"]:
        return
        
    text = get_generate_code_prompt()
    keyboard = get_generate_code_plans_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_codes_router.callback_query(F.data.startswith("gen_plan_"))
async def cb_generate_plan_selected(callback: CallbackQuery, state: FSMContext, db_pool):
    plan_type = callback.data.replace("gen_plan_", "")
    
    if plan_type == "custom":
        text = get_custom_duration_type_prompt()
        keyboard = get_custom_duration_type_keyboard()
        await callback.message.edit_text(text, reply_markup=keyboard)
        return
        
    if plan_type == "trial":
        new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        await create_code(db_pool, new_code, plan_type, 1)
        text = get_generate_success_message(new_code, plan_type, 1)
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Admin", callback_data="menu_admin")]
        ])
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.clear()
        return

    await state.update_data(plan_type=plan_type)
    await state.set_state(GenerateCodeState.waiting_for_uses)
    
    text = get_generate_uses_prompt(plan_type.capitalize())
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="admin_generate_code")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_codes_router.callback_query(F.data.startswith("gen_custom_"))
async def cb_generate_custom_unit(callback: CallbackQuery, state: FSMContext):
    unit = callback.data.replace("gen_custom_", "")
    await state.update_data(custom_unit=unit)
    await state.set_state(GenerateCodeState.waiting_for_custom_amount)
    
    text = get_custom_duration_amount_prompt(unit.capitalize())
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="admin_generate_code")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@admin_codes_router.message(GenerateCodeState.waiting_for_custom_amount)
async def process_custom_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Please send a valid number.")
        return
        
    amount = int(message.text.strip())
    if amount < 1:
        await message.answer("❌ Number must be greater than 0.")
        return
        
    data = await state.get_data()
    unit = data['custom_unit']
    plan_type = f"custom_{unit}_{amount}"
    
    await state.update_data(plan_type=plan_type)
    await state.set_state(GenerateCodeState.waiting_for_uses)
    
    display_name = f"Custom ({amount} {unit.capitalize()})"
    text = get_generate_uses_prompt(display_name)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="admin_generate_code")]
    ])
    
    await message.answer(text, reply_markup=keyboard)

@admin_codes_router.message(GenerateCodeState.waiting_for_uses)
async def process_generate_uses(message: Message, state: FSMContext, db_pool):
    if not message.text.isdigit():
        await message.answer("❌ Please send a valid number.")
        return
        
    uses = int(message.text.strip())
    if uses < 1 or uses > 9999:
        await message.answer("❌ Number must be between 1 and 9999.")
        return
        
    data = await state.get_data()
    plan_type = data['plan_type']
    
    new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    
    await create_code(db_pool, new_code, plan_type, uses)
    
    text = get_generate_success_message(new_code, plan_type, uses)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Admin", callback_data="menu_admin")]
    ])
    
    await message.answer(text, reply_markup=keyboard)
    await state.clear()
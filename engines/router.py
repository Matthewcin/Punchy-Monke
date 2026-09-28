import asyncio
import re
import uuid
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repo_logs import add_check_log
from database.repo_users import get_user, get_all_users
from utils.roles import get_user_role
from utils.keyboards.user import get_back_keyboard
from engines.keyboards import get_engines_keyboard, get_checker_error_keyboard
from engines.messages import get_engine_selection_message, get_engine_prompt_message, get_user_error_message, get_server_error_message
from engines.amex.core import process_amex_card
from engines.waltmart.core import process_waltmart_card
from engines.mygcmall.core import process_mygcmall_card

engines_router = Router()

class CheckerState(StatesGroup):
    waiting_for_cards = State()

def extract_clean_card_data(line: str) -> str:
    match = re.search(r"(\d{15,16})[\s\|:/-]+(\d{1,2})[\s\|:/-]+(\d{2,4})[\s\|:/-]+(\d{3,4})", line)
    if match:
        cc, mm, yy, cvv = match.groups()
        mm = mm.zfill(2)
        if len(yy) == 2:
            yy = "20" + yy
        return f"{cc}:{mm}:{yy}:{cvv}"
    return ""

def get_progress_bar(current: int, total: int, length: int = 10) -> str:
    filled = int((current / total) * length)
    bar = "█" * filled + "░" * (length - filled)
    percent = int((current / total) * 100)
    return f"[{bar}] {percent}%"

@engines_router.callback_query(F.data == "menu_check")
async def cb_menu_check(callback: CallbackQuery, state: FSMContext, db_pool):
    await state.clear()
    user_data = await get_user(db_pool, callback.from_user.id)
    role = get_user_role(callback.from_user.id, user_data)
    
    if role not in ["admin", "dev", "active_user"]:
        await callback.answer("You need an active subscription to use the checker.", show_alert=True)
        return
        
    await callback.message.edit_text(get_engine_selection_message(), reply_markup=get_engines_keyboard())

@engines_router.callback_query(F.data.startswith("engine_select_"))
async def cb_engine_select(callback: CallbackQuery, state: FSMContext):
    engine_name = callback.data.replace("engine_select_", "")
    await state.update_data(current_engine=engine_name)
    await state.set_state(CheckerState.waiting_for_cards)
    await callback.message.edit_text(get_engine_prompt_message(engine_name.capitalize()), reply_markup=get_back_keyboard())

@engines_router.message(CheckerState.waiting_for_cards)
async def process_cards_input(message: Message, state: FSMContext, db_pool):
    data = await state.get_data()
    engine_name = data.get("current_engine")
    
    lines = message.text.strip().split("\n")
    valid_cards = []
    
    for line in lines:
        cleaned_card = extract_clean_card_data(line)
        if cleaned_card:
            valid_cards.append(cleaned_card)
            
    if not valid_cards:
        await message.answer(get_user_error_message(engine_name.capitalize()), reply_markup=get_checker_error_keyboard(engine_name))
        return
        
    processing_msg = await message.answer(f"Starting check for {len(valid_cards)} cards...\n{get_progress_bar(0, len(valid_cards))}")
    
    success_count = 0
    failed_count = 0
    batch_id = uuid.uuid4().hex[:10]
    
    user_data = await get_user(db_pool, message.from_user.id)
    is_trial = user_data.get('plan_type') == 'trial'
    
    for i, card in enumerate(valid_cards, 1):
        progress_bar = get_progress_bar(i, len(valid_cards))
        try:
            await processing_msg.edit_text(f"Checking {i}/{len(valid_cards)} Card/s...\n<code>{progress_bar}</code>")
        except Exception:
            pass
            
        if engine_name == "amex":
            result = await process_amex_card(card)
        elif engine_name == "waltmart":
            result = await process_waltmart_card(card)
        elif engine_name == "mygcmall":
            result = await process_mygcmall_card(card)
        else:
            return
        
        if result["status"] == "user_error":
            await add_check_log(db_pool, message.from_user.id, engine_name.capitalize(), "Declined/Invalid", card, is_trial, batch_id)
            failed_count += 1
            
        elif result["status"] == "server_error":
            admins = await get_all_users(db_pool)
            for u in admins:
                if u['role'] in ['admin', 'dev']:
                    try:
                        await message.bot.send_message(
                            u['telegram_id'], 
                            f"Critical Error on Engine {engine_name.capitalize()} reported by user {message.from_user.id}. Action required: Fix engine and add 1 day to daily users."
                        )
                    except Exception:
                        pass
            await processing_msg.edit_text(get_server_error_message(engine_name.capitalize()), reply_markup=get_back_keyboard())
            return
            
        elif result["status"] == "success":
            await add_check_log(db_pool, message.from_user.id, engine_name.capitalize(), "Success", card, is_trial, batch_id)
            success_count += 1
            
    await state.clear()
    
    final_text = (
        f"<b>Process Completed - {engine_name.capitalize()}</b>\n\n"
        f"Success, {success_count} Cards checked successfully\n"
        f"Failed Check: {failed_count}\n\n"
        f"<i>Cards Saved on Main Menu > Check Logs</i>"
    )
    
    await processing_msg.edit_text(final_text, reply_markup=get_back_keyboard())
import math
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from database.repo_logs import get_user_batches_paginated, get_user_batches_count, get_batch_details
from utils.keyboards.logs import get_batches_keyboard, get_batch_view_keyboard, get_log_engines_keyboard

logs_router = Router()

@logs_router.callback_query(F.data == "ignore_btn")
async def cb_ignore(callback: CallbackQuery):
    await callback.answer()

@logs_router.callback_query(F.data == "menu_latest_checks")
async def cb_menu_latest_checks(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>Select Engine Logs</b>\n\nChoose the provider to view your checking history:",
        reply_markup=get_log_engines_keyboard()
    )

@logs_router.callback_query(F.data.startswith("logs_engine_"))
async def cb_logs_engine_select(callback: CallbackQuery, db_pool):
    provider = callback.data.replace("logs_engine_", "")
    await show_batches_page(callback, db_pool, 1, provider)

@logs_router.callback_query(F.data.startswith("batches_page_"))
async def cb_batches_page(callback: CallbackQuery, db_pool):
    parts = callback.data.split("_")
    page = int(parts[-1])
    provider = parts[-2]
    await show_batches_page(callback, db_pool, page, provider)

async def show_batches_page(callback: CallbackQuery, db_pool, page: int, provider: str):
    limit = 5
    offset = (page - 1) * limit
    
    total_batches = await get_user_batches_count(db_pool, callback.from_user.id, provider)
    if total_batches == 0:
        await callback.answer("You have no logs available for this provider.", show_alert=True)
        return
        
    total_pages = math.ceil(total_batches / limit)
    batches = await get_user_batches_paginated(db_pool, callback.from_user.id, limit, offset, provider)
    
    provider_name = "All Providers" if provider == "all" else provider.capitalize()
    text = f"<b>Your Check Logs - {provider_name}</b>\n\nPage {page} of {total_pages}"
    
    await callback.message.edit_text(text, reply_markup=get_batches_keyboard(batches, page, total_pages, provider))

@logs_router.callback_query(F.data.startswith("view_batch_"))
async def cb_view_batch(callback: CallbackQuery, db_pool):
    parts = callback.data.replace("view_batch_", "").split("_")
    batch_id = parts[0]
    provider = parts[1] if len(parts) > 1 else "all"
    
    details = await get_batch_details(db_pool, callback.from_user.id, batch_id)
    
    if not details:
        await callback.answer("Log not found or expired.", show_alert=True)
        return
        
    success_count = sum(1 for d in details if d['result_status'] == 'Success')
    total_count = len(details)
    
    text = (
        f"<b>Batch Log Details</b>\n\n"
        f"<b>Total Checked:</b> {total_count}\n"
        f"<b>Successful:</b> {success_count}\n"
        f"<b>Failed/Declined:</b> {total_count - success_count}\n\n"
        f"<i>Click Download Log to get your decrypted cards in a text file.</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_batch_view_keyboard(batch_id, success_count, provider))

@logs_router.callback_query(F.data.startswith("download_batch_"))
async def cb_download_batch(callback: CallbackQuery, db_pool):
    batch_id = callback.data.replace("download_batch_", "")
    details = await get_batch_details(db_pool, callback.from_user.id, batch_id)
    
    if not details:
        await callback.answer("Log not found or expired.", show_alert=True)
        return
        
    file_content = "=== PUNCH CHECKER LOG ===\n\n"
    file_content += "SUCCESSFUL CARDS:\n"
    successes = [d for d in details if d['result_status'] == 'Success']
    for s in successes:
        file_content += f"{s['decrypted_data']}\n"
        
    file_content += "\nFAILED/DECLINED CARDS:\n"
    failures = [d for d in details if d['result_status'] != 'Success']
    for f in failures:
        file_content += f"{f['decrypted_data']} - {f['result_status']}\n"
        
    file_bytes = file_content.encode('utf-8')
    file = BufferedInputFile(file_bytes, filename=f"Log_{batch_id}.txt")
    
    await callback.message.answer_document(
        document=file,
        caption="Here is your decrypted log file. 🔐"
    )
    await callback.answer()
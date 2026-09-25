from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.repo_settings import get_setting
from database.repo_users import get_user
from utils.roles import get_user_role

class MaintenanceMiddleware(BaseMiddleware):
    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def __call__(self, handler, event, data):
        maintenance = await get_setting(self.db_pool, 'maintenance_mode')
        
        if maintenance == 'true':
            user_id = None
            if isinstance(event, Message):
                user_id = event.from_user.id
            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id
                
            if user_id:
                user_data = await get_user(self.db_pool, user_id)
                role = get_user_role(user_id, user_data)
                
                if role not in ['admin', 'dev']:
                    text = "🚧 <b>Maintenance Mode Active</b>\n\nThe bot is currently undergoing maintenance. Please try again later."
                    if isinstance(event, Message):
                        await event.answer(text)
                    elif isinstance(event, CallbackQuery):
                        await event.answer("Maintenance Mode Active. Please try again later.", show_alert=True)
                    return
        
        return await handler(event, data)
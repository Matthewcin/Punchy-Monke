from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class PrivateChatMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        chat = None
        if isinstance(event, Message):
            chat = event.chat
        elif isinstance(event, CallbackQuery) and event.message:
            chat = event.message.chat
            
        if chat and chat.type != "private":
            if isinstance(event, Message):
                try:
                    await event.answer("This bot can only be used in a private direct message. Please message me directly.")
                    await event.bot.leave_chat(chat.id)
                except Exception:
                    pass
            elif isinstance(event, CallbackQuery):
                try:
                    await event.answer("This bot can only be used in a private direct message.", show_alert=True)
                except Exception:
                    pass
            return
            
        return await handler(event, data)
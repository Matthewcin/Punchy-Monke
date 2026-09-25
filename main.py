import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web
from config import BOT_TOKEN
from database.db import get_pool, init_db
from utils.middleware import MaintenanceMiddleware
from handlers.user import user_router
from handlers.callbacks import callback_router
from handlers.profile import profile_router
from handlers.admin import admin_router
from handlers.dev import dev_router
from handlers.subscription import sub_router
from handlers.admin_codes import admin_codes_router

logging.basicConfig(level=logging.INFO)

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    pool = await get_pool()
    await init_db(pool)
    
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True
        )
    )
    
    dp = Dispatcher()
    dp["db_pool"] = pool
    
    dp.message.middleware(MaintenanceMiddleware(pool))
    dp.callback_query.middleware(MaintenanceMiddleware(pool))
    
    dp.include_router(user_router)
    dp.include_router(callback_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)
    dp.include_router(dev_router)
    dp.include_router(sub_router)
    dp.include_router(admin_codes_router)
    
    app = web.Application()
    app.router.add_get('/', handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    try:
        await asyncio.gather(
            site.start(),
            dp.start_polling(bot)
        )
    finally:
        await bot.session.close()
        await pool.close()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
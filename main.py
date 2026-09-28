import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from config import BOT_TOKEN
from database.db import get_pool, init_db
from database.repo_users import grant_subscription
from database.repo_logs import get_public_transparency_logs
from utils.middleware import MaintenanceMiddleware
from utils.private_chat import PrivateChatMiddleware

from handlers.user import user_router
from handlers.callbacks import callback_router
from handlers.profile import profile_router
from handlers.admin import admin_router
from handlers.dev import dev_router
from handlers.subscription import sub_router
from handlers.admin_codes import admin_codes_router
from handlers.orders import orders_router
from handlers.tickets import tickets_router
from handlers.admin_tickets import admin_tickets_router
from handlers.trial import trial_router
from handlers.admin_modify import admin_modify_router
from handlers.logs import logs_router
from engines.router import engines_router

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        link_preview_is_disabled=True
    )
)

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def handle_transparency(request):
    pool = request.app['db_pool']
    logs = await get_public_transparency_logs(pool, 50)
    
    html_content = "<html><head><title>Transparency Portal</title>"
    html_content += "<style>body{font-family:monospace; background:#000000; color:#00ff00; padding:20px;} table{border-collapse:collapse; width:100%;} th, td{border:1px solid #00ff00; padding:8px; text-align:left; word-break:break-all;}</style></head><body>"
    html_content += "<h2>Secure Engine - Live Transparency Portal</h2>"
    html_content += "<p>End-to-End Encrypted Data at Rest. Only encrypted blobs are stored in our database.</p>"
    html_content += "<table><tr><th>Log ID</th><th>Provider</th><th>Status</th><th>Encrypted Blob (AES)</th><th>Timestamp</th></tr>"
    
    for log in logs:
        html_content += f"<tr><td>{log['log_id']}</td><td>{log['provider']}</td><td>{log['result_status']}</td><td>{log['encrypted_data']}</td><td>{log['check_timestamp']}</td></tr>"
    
    html_content += "</table></body></html>"
    
    return web.Response(text=html_content, content_type='text/html')

async def handle_nowpayments_ipn(request):
    signature = request.headers.get('x-nowpayments-sig')
    if not signature:
        return web.Response(status=400)
        
    try:
        data = await request.json()
    except Exception:
        return web.Response(status=400)
        
    from nowpayments.ipn import verify_ipn_request
    if not verify_ipn_request(data, signature):
        return web.Response(status=403)
        
    payment_status = data.get('payment_status')
    payment_id = str(data.get('payment_id'))
    
    if payment_status in ['finished', 'confirmed', 'sending']:
        pool = request.app['db_pool']
        async with pool.acquire() as conn:
            record = await conn.fetchrow('SELECT telegram_id, plan_purchased, payment_status FROM payments WHERE transaction_id = $1', payment_id)
            
            if record and record['payment_status'] != 'completed':
                await conn.execute('UPDATE payments SET payment_status = $1 WHERE transaction_id = $2', 'completed', payment_id)
                
                plan = record['plan_purchased']
                telegram_id = record['telegram_id']
                
                days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'lifetime': 9999}
                days = days_map.get(plan, 0)
                
                await grant_subscription(pool, telegram_id, days, plan, False, 0)
                
                try:
                    await bot.send_message(
                        telegram_id,
                        f"Payment Confirmed!\n\nYour {plan.capitalize()} plan has been automatically activated via IPN."
                    )
                except Exception:
                    pass
                    
    return web.Response(text="OK")

async def main():
    pool = await get_pool()
    await init_db(pool)
    
    dp = Dispatcher()
    dp["db_pool"] = pool
    
    dp.message.middleware(PrivateChatMiddleware())
    dp.callback_query.middleware(PrivateChatMiddleware())
    
    dp.message.middleware(MaintenanceMiddleware(pool))
    dp.callback_query.middleware(MaintenanceMiddleware(pool))
    
    dp.include_router(user_router)
    dp.include_router(callback_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)
    dp.include_router(dev_router)
    dp.include_router(sub_router)
    dp.include_router(admin_codes_router)
    dp.include_router(orders_router)
    dp.include_router(tickets_router)
    dp.include_router(admin_tickets_router)
    dp.include_router(trial_router)
    dp.include_router(admin_modify_router)
    
    # Nuevos routers
    dp.include_router(engines_router)
    dp.include_router(logs_router)
    
    app = web.Application()
    app['db_pool'] = pool
    app.router.add_get('/', handle_ping)
    app.router.add_get('/transparency', handle_transparency)
    app.router.add_post('/api/ipn', handle_nowpayments_ipn)
    
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
from datetime import datetime, timedelta

async def add_user(pool, telegram_id, role='user'):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (telegram_id, role)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) DO NOTHING
        ''', telegram_id, role)

async def get_user(pool, telegram_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow('''
            SELECT * FROM users WHERE telegram_id = $1
        ''', telegram_id)

async def grant_subscription(pool, telegram_id, days, plan_name, is_trial=False):
    expiry = datetime.now() + timedelta(days=days)
    
    if days == 9999:
        expiry = datetime.now() + timedelta(days=36500)

    async with pool.acquire() as conn:
        if is_trial:
            await conn.execute('''
                UPDATE users 
                SET subscription_expiry = $1, has_used_trial = TRUE, plan_type = $3
                WHERE telegram_id = $2
            ''', expiry, telegram_id, plan_name)
        else:
            await conn.execute('''
                UPDATE users 
                SET subscription_expiry = $1, plan_type = $3
                WHERE telegram_id = $2
            ''', expiry, telegram_id, plan_name)
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

async def get_all_users(pool):
    async with pool.acquire() as conn:
        return await conn.fetch('SELECT telegram_id FROM users')

async def get_broadcast_users(pool, target_type: str):
    async with pool.acquire() as conn:
        if target_type == "all":
            return await conn.fetch('SELECT telegram_id FROM users')
        elif target_type == "expired":
            return await conn.fetch('''
                SELECT telegram_id FROM users 
                WHERE plan_type != 'none' 
                AND plan_type != 'lifetime' 
                AND subscription_expiry <= CURRENT_TIMESTAMP
            ''')
        elif target_type == "active":
            return await conn.fetch('''
                SELECT telegram_id FROM users 
                WHERE plan_type = 'lifetime' 
                OR subscription_expiry > CURRENT_TIMESTAMP
            ''')
        elif target_type == "new":
            return await conn.fetch('''
                SELECT telegram_id FROM users 
                WHERE has_used_trial = FALSE 
                AND total_days_purchased = 0
            ''')
        elif target_type == "trial":
            return await conn.fetch('''
                SELECT telegram_id FROM users 
                WHERE has_used_trial = TRUE 
                AND total_days_purchased = 0
            ''')
        return []

async def grant_subscription(pool, telegram_id, days, plan_name, is_trial=False):
    expiry = datetime.now() + timedelta(days=days)
    
    if days == 9999:
        expiry = datetime.now() + timedelta(days=36500)

    async with pool.acquire() as conn:
        if is_trial:
            await conn.execute('''
                UPDATE users 
                SET subscription_expiry = $1, has_used_trial = TRUE, plan_type = $3, total_days_purchased = total_days_purchased + $4
                WHERE telegram_id = $2
            ''', expiry, telegram_id, plan_name, days)
        else:
            await conn.execute('''
                UPDATE users 
                SET subscription_expiry = $1, plan_type = $3, total_days_purchased = total_days_purchased + $4
                WHERE telegram_id = $2
            ''', expiry, telegram_id, plan_name, days)
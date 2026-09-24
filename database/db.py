import asyncpg
from config import DB_URL
from datetime import datetime, timedelta

async def get_pool():
    return await asyncpg.create_pool(DB_URL)

async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                role VARCHAR(10) DEFAULT 'user',
                plan_type VARCHAR(20) DEFAULT 'none',
                subscription_expiry TIMESTAMP,
                has_used_trial BOOLEAN DEFAULT FALSE,
                checks_performed INT DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS check_logs (
                log_id SERIAL PRIMARY KEY,
                telegram_id BIGINT REFERENCES users(telegram_id),
                provider VARCHAR(50),
                result_status VARCHAR(50),
                check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS bot_settings (
                setting_key VARCHAR(50) PRIMARY KEY,
                setting_value VARCHAR(255)
            );

            CREATE TABLE IF NOT EXISTS payments (
                transaction_id VARCHAR(100) PRIMARY KEY,
                telegram_id BIGINT REFERENCES users(telegram_id),
                amount DECIMAL(10, 2),
                plan_purchased VARCHAR(20),
                payment_status VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

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
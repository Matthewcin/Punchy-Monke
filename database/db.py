import asyncpg
from config import DB_URL

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
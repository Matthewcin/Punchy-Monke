import asyncpg
from config import DB_URL

async def get_pool():
    return await asyncpg.create_pool(DB_URL, statement_cache_size=0)

async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                role VARCHAR(10) DEFAULT 'user'
            );

            ALTER TABLE users ADD COLUMN IF NOT EXISTS plan_type VARCHAR(20) DEFAULT 'none';
            ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_expiry TIMESTAMP;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS has_used_trial BOOLEAN DEFAULT FALSE;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS checks_performed INT DEFAULT 0;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS total_days_purchased INT DEFAULT 0;

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

            CREATE TABLE IF NOT EXISTS devlogs (
                log_id SERIAL PRIMARY KEY,
                log_date DATE DEFAULT CURRENT_DATE,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS payments (
                transaction_id VARCHAR(100) PRIMARY KEY,
                telegram_id BIGINT REFERENCES users(telegram_id),
                amount DECIMAL(10, 2),
                plan_purchased VARCHAR(20),
                payment_status VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            ALTER TABLE payments ADD COLUMN IF NOT EXISTS viewed BOOLEAN DEFAULT FALSE;

            CREATE TABLE IF NOT EXISTS codes (
                id SERIAL PRIMARY KEY,
                code VARCHAR(50) UNIQUE NOT NULL,
                plan_type VARCHAR(50) NOT NULL,
                max_uses INT DEFAULT 1,
                uses_count INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS code_redemptions (
                id SERIAL PRIMARY KEY,
                code_id INT REFERENCES codes(id),
                telegram_id BIGINT REFERENCES users(telegram_id),
                redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(code_id, telegram_id)
            );
        ''')
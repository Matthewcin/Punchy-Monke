from utils.security import encrypt_data, decrypt_data
from database.repo_settings import get_setting

async def get_trial_hours(pool) -> int:
    val = await get_setting(pool, "trial_hours")
    return int(val) if val else 24

async def get_user_checks_count(pool, telegram_id: int):
    hours = await get_trial_hours(pool)
    async with pool.acquire() as conn:
        await conn.execute(f"DELETE FROM check_logs WHERE is_trial = TRUE AND check_timestamp < NOW() - INTERVAL '{hours} hours'")
        return await conn.fetchval('SELECT COUNT(*) FROM check_logs WHERE telegram_id = $1', telegram_id)

async def get_user_batches_count(pool, telegram_id: int, provider: str = "all"):
    hours = await get_trial_hours(pool)
    async with pool.acquire() as conn:
        await conn.execute(f"DELETE FROM check_logs WHERE is_trial = TRUE AND check_timestamp < NOW() - INTERVAL '{hours} hours'")
        
        if provider and provider != "all":
            return await conn.fetchval('SELECT COUNT(DISTINCT batch_id) FROM check_logs WHERE telegram_id = $1 AND batch_id IS NOT NULL AND LOWER(provider) = LOWER($2)', telegram_id, provider)
        else:
            return await conn.fetchval('SELECT COUNT(DISTINCT batch_id) FROM check_logs WHERE telegram_id = $1 AND batch_id IS NOT NULL', telegram_id)

async def get_user_batches_paginated(pool, telegram_id: int, limit: int, offset: int, provider: str = "all"):
    async with pool.acquire() as conn:
        if provider and provider != "all":
            records = await conn.fetch('''
                SELECT batch_id, provider, MIN(check_timestamp) as check_date, 
                       COUNT(*) as total_cards, 
                       SUM(CASE WHEN result_status = 'Success' THEN 1 ELSE 0 END) as success_count
                FROM check_logs 
                WHERE telegram_id = $1 AND batch_id IS NOT NULL AND LOWER(provider) = LOWER($4)
                GROUP BY batch_id, provider 
                ORDER BY check_date DESC 
                LIMIT $2 OFFSET $3
            ''', telegram_id, limit, offset, provider)
        else:
            records = await conn.fetch('''
                SELECT batch_id, provider, MIN(check_timestamp) as check_date, 
                       COUNT(*) as total_cards, 
                       SUM(CASE WHEN result_status = 'Success' THEN 1 ELSE 0 END) as success_count
                FROM check_logs 
                WHERE telegram_id = $1 AND batch_id IS NOT NULL
                GROUP BY batch_id, provider 
                ORDER BY check_date DESC 
                LIMIT $2 OFFSET $3
            ''', telegram_id, limit, offset)
            
        return [dict(r) for r in records]

async def get_batch_details(pool, telegram_id: int, batch_id: str):
    async with pool.acquire() as conn:
        records = await conn.fetch('''
            SELECT result_status, encrypted_data 
            FROM check_logs 
            WHERE telegram_id = $1 AND batch_id = $2
        ''', telegram_id, batch_id)
        
        results = []
        for r in records:
            r_dict = dict(r)
            if r_dict.get('encrypted_data'):
                r_dict['decrypted_data'] = decrypt_data(r_dict['encrypted_data'])
            else:
                r_dict['decrypted_data'] = "No data"
            results.append(r_dict)
        return results

async def add_check_log(pool, telegram_id: int, provider: str, result_status: str, raw_data: str, is_trial: bool = False, batch_id: str = None):
    encrypted = encrypt_data(raw_data)
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO check_logs (telegram_id, provider, result_status, encrypted_data, is_trial, batch_id)
            VALUES ($1, $2, $3, $4, $5, $6)
        ''', telegram_id, provider, result_status, encrypted, is_trial, batch_id)

async def get_public_transparency_logs(pool, limit: int = 50):
    hours = await get_trial_hours(pool)
    async with pool.acquire() as conn:
        await conn.execute(f"DELETE FROM check_logs WHERE is_trial = TRUE AND check_timestamp < NOW() - INTERVAL '{hours} hours'")
        return await conn.fetch('''
            SELECT log_id, provider, result_status, encrypted_data, check_timestamp 
            FROM check_logs 
            ORDER BY check_timestamp DESC 
            LIMIT $1
        ''', limit)
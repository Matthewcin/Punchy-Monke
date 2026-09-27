from utils.security import encrypt_data, decrypt_data

async def get_user_checks_count(pool, telegram_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchval('SELECT COUNT(*) FROM check_logs WHERE telegram_id = $1', telegram_id)

async def get_user_checks_paginated(pool, telegram_id: int, limit: int, offset: int):
    async with pool.acquire() as conn:
        records = await conn.fetch('''
            SELECT * FROM check_logs 
            WHERE telegram_id = $1 
            ORDER BY check_timestamp DESC 
            LIMIT $2 OFFSET $3
        ''', telegram_id, limit, offset)
        
        results = []
        for r in records:
            r_dict = dict(r)
            if r_dict.get('encrypted_data'):
                r_dict['decrypted_data'] = decrypt_data(r_dict['encrypted_data'])
            else:
                r_dict['decrypted_data'] = "No data"
            results.append(r_dict)
        return results

async def add_check_log(pool, telegram_id: int, provider: str, result_status: str, raw_data: str):
    encrypted = encrypt_data(raw_data)
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO check_logs (telegram_id, provider, result_status, encrypted_data)
            VALUES ($1, $2, $3, $4)
        ''', telegram_id, provider, result_status, encrypted)

async def get_public_transparency_logs(pool, limit: int = 50):
    async with pool.acquire() as conn:
        return await conn.fetch('''
            SELECT log_id, provider, result_status, encrypted_data, check_timestamp 
            FROM check_logs 
            ORDER BY check_timestamp DESC 
            LIMIT $1
        ''', limit)
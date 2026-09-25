async def create_code(pool, code: str, plan_type: str, max_uses: int):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO codes (code, plan_type, max_uses)
            VALUES ($1, $2, $3)
        ''', code, plan_type, max_uses)

async def get_code(pool, code: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow('''
            SELECT * FROM codes WHERE code = $1
        ''', code)

async def check_user_redeemed(pool, code_id: int, telegram_id: int):
    async with pool.acquire() as conn:
        record = await conn.fetchrow('''
            SELECT id FROM code_redemptions WHERE code_id = $1 AND telegram_id = $2
        ''', code_id, telegram_id)
        return bool(record)

async def redeem_code_db(pool, code_id: int, telegram_id: int):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute('''
                INSERT INTO code_redemptions (code_id, telegram_id)
                VALUES ($1, $2)
            ''', code_id, telegram_id)
            await conn.execute('''
                UPDATE codes SET uses_count = uses_count + 1 WHERE id = $1
            ''', code_id)
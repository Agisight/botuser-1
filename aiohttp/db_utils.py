import asyncpg
from datetime import datetime, timedelta
pool = None
from decouple import config

POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')

async def init_db():
    global pool
    pool = await asyncpg.create_pool(f"postgresql://postgres:{POSTGRES_PASSWORD}@db:5432/postgres")
    # await create_tables()


async def add_user(bot_id, chat_id, first_name, last_name, username):
    async with pool.acquire() as conn:

        query = "INSERT INTO cabinet_botuser " \
                "(bot_id, chat_id, first_name, last_name, username, step, otpiska, date_in) " \
                "VALUES " \
                "($1, $2, $3, $4, $5, $6, $7, $8) " \
                "RETURNING *"

        result = await conn.fetch(query, bot_id, chat_id, first_name, last_name, username, None, False, datetime.today())

        if result:
            return result[0]
        return result


async def update_user(bot_id, chat_id, **kwargs):

    if not kwargs:
        return

    sql_str = ''
    var_number = 1
    vars = []

    for key in kwargs:

        sql_str += key + "=$%d," % var_number
        var_number += 1
        vars.append(kwargs[key])

    sql_query = "UPDATE cabinet_botuser SET %s WHERE bot_id = $%d AND chat_id = $%d" % (sql_str[0:-1], var_number, var_number + 1)
    vars.append(bot_id)
    vars.append(chat_id)

    async with pool.acquire() as conn:
        return await conn.fetch(sql_query, *vars)


async def get_settings():
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM cabinet_settings LIMIT 1')
        if not result:
            return []
        else:
            return result[0]


async def create_order(user_id, out_payment, in_payment, out_amount, in_amount, out_wallet, in_wallet, status, delta):
    async with pool.acquire() as conn:

        d = datetime.today()
        d_cancel = d + delta

        query = "INSERT INTO cabinet_order " \
                "(user_id, out_payment, in_payment, out_amount, in_amount, out_wallet, in_wallet, status, date_in, date_cancel) " \
                "VALUES " \
                "($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) " \
                "RETURNING *"
        result = await conn.fetch(query, user_id, out_payment, in_payment, out_amount, in_amount, out_wallet, in_wallet, status, d, d_cancel)

        if not result:
            return []
        else:
            return result[0]


async def get_order(order_id):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM cabinet_order WHERE id = $1', order_id)
        if result:
            return result[0]
        else:
            return []


async def get_order_by_wallet(out_wallet):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM cabinet_order WHERE out_wallet = $1', out_wallet)
        if result:
            return result[0]
        else:
            return []


async def update_order(order_id, **kwargs):

    if not kwargs:
        return

    sql_str = ''
    var_number = 1
    vars = []

    for key in kwargs:

        sql_str += key + "=$%d," % var_number
        var_number += 1
        vars.append(kwargs[key])

    sql_query = "UPDATE cabinet_order SET %s WHERE id = $%d" % (sql_str[0:-1], var_number)
    vars.append(order_id)

    async with pool.acquire() as conn:
        return await conn.fetch(sql_query, *vars)


# async def get_bot(bot_id):
#     async with pool.acquire() as conn:
#         result = await conn.fetch('SELECT t1.*, t2.is_active as profile_is_active, t2.partner_id, t3.is_active as partner_is_active, t3.podpiska_do as partner_podpiska_do '
#                                   'FROM bot_bot t1 '
#                                   'LEFT JOIN accounts_profile t2 ON t1.profile_id = t2.id '
#                                   'LEFT JOIN accounts_partnerprofile t3 ON t2.partner_id = t3.id '
#                                   'WHERE t1.id = $1', bot_id)
#
#         if result:
#             return result[0]
#         return result


async def get_bot(bot_token):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM cabinet_bot '
                                  'WHERE token = $1', bot_token)

        if result:
            return result[0]
        return result


async def update_bot(bot_id, **kwargs):

    if not kwargs:
        return

    sql_str = ''
    var_number = 1
    vars = []

    for key in kwargs:

        sql_str += key + "=$%d," % var_number
        var_number += 1
        vars.append(kwargs[key])

    sql_query = "UPDATE cabinet_bot SET %s WHERE id = $%d" % (sql_str[0:-1], var_number)
    vars.append(bot_id)

    async with pool.acquire() as conn:
        return await conn.fetch(sql_query, *vars)


async def get_user(bot_id, chat_id):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM cabinet_botuser WHERE bot_id = $1 AND chat_id = $2', bot_id, chat_id)
        if result:
            return result[0]
        return result


async def create_order(bot_id, user_id, order_text):
    async with pool.acquire() as conn:

        query = "INSERT INTO cabinet_order " \
                "(bot_id, bot_user_id, text, date_in) " \
                "VALUES " \
                "($1, $2, $3, $4)"

        await conn.fetch(query, bot_id, user_id, order_text, datetime.today())


async def add_mes_log(bot_id, bot_user_id, in_or_out, log, answer_whatsapp_api=None):
    async with pool.acquire() as conn:

        query = "INSERT INTO cabinet_messagelog " \
                "(bot_id, bot_user_id, in_or_out, log, answer_out_mes_request, date_in) " \
                "VALUES " \
                "($1, $2, $3, $4, $5, $6)"

        await conn.fetch(query, bot_id, bot_user_id, in_or_out, log, answer_whatsapp_api, datetime.today())

import asyncpg
from datetime import datetime, timedelta
pool = None
from decouple import config

POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')

async def init_db():
    global pool
    pool = await asyncpg.create_pool(f"postgresql://postgres:{POSTGRES_PASSWORD}@db:5432/postgres")


async def new_compaign():
    print('new_compaign')
    async with pool.acquire() as conn:
        result = await conn.fetch("SELECT * FROM cabinet_compaign WHERE status = 'created' limit 1")
        if result:
            return result[0]
        return result


async def set_old_compaign(id):
    print('set_old_compaign')
    async with pool.acquire() as conn:
        await conn.fetch("UPDATE cabinet_compaign SET is_new = 0 WHERE id = %s" % id)


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


async def update_compaign(compaign_id, **kwargs):

    if not kwargs:
        return

    sql_str = ''
    var_number = 1
    vars = []

    for key in kwargs:

        sql_str += key + "=$%d," % var_number
        var_number += 1
        vars.append(kwargs[key])

    sql_query = "UPDATE cabinet_compaign SET %s WHERE id = $%d" % (sql_str[0:-1], var_number)
    vars.append(compaign_id)

    async with pool.acquire() as conn:
        return await conn.fetch(sql_query, *vars)


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



async def get_bot(bot_id):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM cabinet_bot WHERE id = $1', bot_id)
        if result:
            return result[0]
        return result


async def get_old_podpiska_bots():
    async with pool.acquire() as conn:
        return await conn.fetch('SELECT * FROM cabinet_bot WHERE podpiska_do < $1', datetime.today())


async def get_compaign(compaign_id):
    async with pool.acquire() as conn:
        return await conn.fetch('SELECT * FROM cabinet_compaign WHERE id = $1', compaign_id)


async def get_part_users(bot, offset, limit):
    print('get_part_users %s %s' % (offset, limit))

    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM cabinet_botuser "
                                "WHERE bot_id = $1 "
                                "ORDER BY id ASC OFFSET $2 LIMIT $3", bot['id'], offset, limit)


async def get_users(bot, from_date_signup=None, to_date_signup=None):
    print('get_users')

    async with pool.acquire() as conn:

        if not from_date_signup or not to_date_signup:
            return await conn.fetch("SELECT * FROM cabinet_botuser "
                                    "WHERE bot_id = $1 "
                                    "ORDER BY id", bot['id'])

        else:
            return await conn.fetch("SELECT * FROM cabinet_botuser "
                                    "WHERE bot_id = $1 AND from_date_signup >= $2 AND to_date_signup <= $3 "
                                    "ORDER BY id", bot['id'], from_date_signup and to_date_signup)


async def get_activity(bot, user):

    async with pool.acquire() as conn:
        result = await conn.fetch("SELECT COUNT(*) FROM cabinet_messagelog "
                                  "WHERE bot_id = $1 AND bot_user_id = $2 AND in_or_out = 'out' "
                                  "AND date_in <= $3", bot['id'], user['id'], user['date_in'] + timedelta(days=1))
        return result[0]['count']

# !!! sql injection delay
async def get_users_for_delay(bot, received_compaign, delay):

    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM cabinet_botuser "
                                "WHERE bot_id = $1 "
                                "AND id NOT IN (SELECT id FROM cabinet_botuser WHERE phone = any($2::varchar[])) "
                                "AND date_in + INTERVAL '%s minutes' < $3 "
                                "ORDER BY id ASC" % delay,
                                bot['id'], received_compaign, datetime.today())

async def set_user_otpiska(chat_id):
    print('set_user_otpiska')
    async with pool.acquire() as conn:
        await conn.fetch("UPDATE cabinet_botuser SET otpiska = TRUE WHERE chat_id = %s" % chat_id)


async def get_bot_data(bot_id):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT data '
                                  'FROM cabinet_bot '
                                  'WHERE id = $1', bot_id)

        if result:
            return result[0]['data']
        return result

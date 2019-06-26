import asyncpg
from datetime import datetime, timedelta
pool = None
from decouple import config

POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')

async def init_db():
    global pool
    pool = await asyncpg.create_pool(f"postgresql://postgres:{POSTGRES_PASSWORD}@db:5432/postgres")
    # await create_tables()


async def add_user(bot_id, chat_id, name, phone, step):
    async with pool.acquire() as conn:

        query = "INSERT INTO bot_botuser " \
                "(bot_id, chat_id, name, phone, step, variables, date_in) " \
                "VALUES " \
                "($1, $2, $3, $4, $5, '{}', $6) " \
                "RETURNING *"

        result = await conn.fetch(query, bot_id, chat_id, name, phone, step, datetime.today())

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

    sql_query = "UPDATE bot_botuser SET %s WHERE bot_id = $%d AND chat_id = $%d" % (sql_str[0:-1], var_number, var_number + 1)
    vars.append(bot_id)
    vars.append(chat_id)

    async with pool.acquire() as conn:
        return await conn.fetch(sql_query, *vars)


async def get_user(bot_id, chat_id):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM bot_botuser WHERE bot_id = $1 AND chat_id = $2', bot_id, chat_id)
        if result:
            return result[0]
        return result


async def get_refcount(chat_id):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT count(*) FROM bot_botuser WHERE parent = %s' % chat_id)
        return result[0]["count"]


async def get_user_by_id(id):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM bot_botuser WHERE id = %s' % id)
        if not result:
            return []
        else:
            return result[0]


async def get_kurs():
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM bot_settings')
        if not result:
            return []
        else:
            return result[0]["kurs"]


async def get_settings():
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM bot_settings LIMIT 1')
        if not result:
            return []
        else:
            return result[0]


async def get_count_users():
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT count(*) FROM bot_botuser')
        if not result:
            return []
        else:
            return result[0]["count"]


async def get_summa():
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT sum(balance) FROM bot_botuser')
        if not result:
            return []
        else:
            return result[0]["sum"]


async def get_count_today_users(date):
    async with pool.acquire() as conn:
        result = await conn.fetch("SELECT count(*) FROM bot_botuser where DATE(date_in + interval '3 hours') = '%s'" % date)
        if not result:
            return []
        else:
            return result[0]["count"]


async def get_users(offset, limit):
    print('get_users %s %s' % (offset, limit))

    with open("error_compaign.txt", 'a+') as file:
        file.write('get_users %s %s\n' % (offset, limit))

    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM bot_botuser WHERE otpiska = FALSE ORDER BY id ASC OFFSET %s LIMIT %s" % (offset, limit))
        #return await conn.fetch("SELECT * FROM bot_botuser ORDER BY id ASC OFFSET %s LIMIT %s" % (offset, limit))


async def get_users_stat():
    res = []
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT count(*) FROM bot_botuser WHERE otpiska = FALSE')
        res.append(result[0]["count"])
        result = await conn.fetch('SELECT count(*) FROM bot_botuser WHERE otpiska = TRUE')
        res.append(result[0]["count"])
        return res


async def get_compaign(id):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM bot_compaign WHERE id = %s' % id)
        if not result:
            return []
        else:
            return result[0]


async def set_user_otpiska(chat_id):
    print('set_user_otpiska')
    async with pool.acquire() as conn:
        await conn.fetch("UPDATE bot_botuser SET otpiska = TRUE WHERE chat_id = %s" % chat_id)



async def new_compaign():
    print('new_compaign')
    async with pool.acquire() as conn:
        r = await conn.fetch("SELECT * FROM bot_compaign WHERE is_new = 1 limit 1")
        print(r)
        return r


async def set_old_compaign(id):
    print('set_old_compaign')
    async with pool.acquire() as conn:
        await conn.fetch("UPDATE bot_compaign SET is_new = 0 WHERE id = %s" % id)


async def add_history(user_id, history_type, summa, summa_crystal, payment_method, wallet, date_in, is_done, log=None):
    async with pool.acquire() as conn:
        query = "INSERT INTO bot_history (user_id, history_type, summa, summa_crystal, payment_method, wallet, date_in, is_done, log) VALUES ($1::bigint, $2::varchar, $3::real, $4::real, $5::varchar, $6::varchar, $7::timestamp, $8::boolean, $9::varchar) RETURNING *"
        await conn.fetch(query, user_id, history_type, summa, summa_crystal, payment_method, wallet, date_in, is_done, log)


async def get_history(user_id):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM bot_history WHERE user_id = %s AND is_done = TRUE' % user_id)
        if not result:
            return []
        else:
            return result


async def add_addition(user_id, summa, date_in):
    async with pool.acquire() as conn:
        query = "INSERT INTO bot_addition " \
                "(user_id, summa, date_in) " \
                "VALUES ($1::bigint, $2::real, $3"
        await conn.fetch(query, user_id, summa, date_in)


async def get_sum_additions():
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT sum(summa) FROM bot_addition')
        if not result:
            return 0
        else:
            return result[0]["sum"]


async def get_today_sum_additions(d):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT sum(summa) FROM bot_addition WHERE date_in = $1', d)
        if not result:
            return 0
        else:
            return result[0]["sum"]


async def get_last_trades():
    async with pool.acquire() as conn:
        return await conn.fetch('SELECT * FROM bot_trade ORDER BY id DESC LIMIT 3')


async def get_margin(obmen_type):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM bot_margin WHERE obmen_type = $1', obmen_type)
        if result:
            return result[0]
        else:
            return []


async def create_order(user_id, out_payment, in_payment, out_amount, in_amount, out_wallet, in_wallet, status, delta):
    async with pool.acquire() as conn:

        d = datetime.today()
        d_cancel = d + delta

        query = "INSERT INTO bot_order " \
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
        result = await conn.fetch('SELECT * FROM bot_order WHERE id = $1', order_id)
        if result:
            return result[0]
        else:
            return []


async def get_order_by_wallet(out_wallet):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM bot_order WHERE out_wallet = $1', out_wallet)
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

    sql_query = "UPDATE bot_order SET %s WHERE id = $%d" % (sql_str[0:-1], var_number)
    vars.append(order_id)

    async with pool.acquire() as conn:
        return await conn.fetch(sql_query, *vars)


async def get_bot(bot_id):
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT t1.*, t2.is_active as profile_is_active, t2.partner_id, t3.is_active as partner_is_active, t3.podpiska_do as partner_podpiska_do '
                                  'FROM bot_bot t1 '
                                  'LEFT JOIN accounts_profile t2 ON t1.profile_id = t2.id '
                                  'LEFT JOIN accounts_partnerprofile t3 ON t2.partner_id = t3.id '
                                  'WHERE t1.id = $1', bot_id)

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

    sql_query = "UPDATE bot_bot SET %s WHERE id = $%d" % (sql_str[0:-1], var_number)
    vars.append(bot_id)

    async with pool.acquire() as conn:
        return await conn.fetch(sql_query, *vars)


async def create_order(bot_id, user_id, order_text):
    async with pool.acquire() as conn:

        query = "INSERT INTO bot_order " \
                "(bot_id, bot_user_id, text, date_in) " \
                "VALUES " \
                "($1, $2, $3, $4)"

        await conn.fetch(query, bot_id, user_id, order_text, datetime.today())


async def add_mes_log(bot_id, bot_user_id, in_or_out, log, answer_whatsapp_api=None):
    async with pool.acquire() as conn:

        query = "INSERT INTO bot_messagelog " \
                "(bot_id, bot_user_id, in_or_out, log, answer_whatsapp_api, date_in) " \
                "VALUES " \
                "($1, $2, $3, $4, $5, $6)"

        await conn.fetch(query, bot_id, bot_user_id, in_or_out, log, answer_whatsapp_api, datetime.today())

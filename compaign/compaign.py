from aiohttp import ClientSession
import asyncio
from db_utils import *
import os, sys

import logging
logging.basicConfig(filename="/compaign/log.txt", level=logging.ERROR)

from dotenv import load_dotenv
load_dotenv('/compaign/main_config/.env')

import json

def get_filename(s):

    p1 = s.rfind('/')
    if p1 == -1:
        return 'file'

    s_ = s[p1 + 1:]

    p2 = s_.rfind('_')
    if p2 == -1:
        return 'file'

    return s_[p2 + 1:]


async def send_text_message(api_key, api_url, chat_id, text):

    try:

        async with ClientSession() as session:
            url = f"{api_url}/sendMessage?token={api_key}"
            data = {"chatId": chat_id,
                    "body": text}
            async with session.post(url, data=data) as resp:
                pass
                #print(resp.status)
                #print(await resp.text())

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("send_text_message {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


async def send_file_message(api_key, api_url, chat_id, file_url, filename):

    try:

        async with ClientSession() as session:
            url = f"{api_url}/sendFile?token={api_key}"
            data = {"chatId": chat_id,
                    "body": file_url,
                    "filename": filename}
            async with session.post(url, data=data) as resp:
                pass
                #print(resp.status)
                #print(await resp.text())

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("send_file_message {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


async def check_podpiska():
    while True:

        try:

            bots = await get_old_podpiska_bots()

            for bot in bots:
                await update_bot(bot['id'], podpiska_do=None)

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("sys.exc_info() : ", sys.exc_info())
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(e))
            logging.error("check_podpiska {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

        await asyncio.sleep(20)


async def check_compaign():
    while True:

        try:

            print('check_compaign')
            compaign = await new_compaign()
            if compaign:
                bot = await get_bot(compaign['bot_id'])
                asyncio.ensure_future(make_compaign(bot, compaign))

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("sys.exc_info() : ", sys.exc_info())
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(e))
            logging.error("check_compaign {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

        await asyncio.sleep(20)




def find_screen(screen_id, data):

    try:

        for column in data:
            for screen in column:
                if screen['id'] == screen_id:
                    return screen
        return None

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("find_screen {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


def find_menu_element_in_screen(screen):

    try:

        for element in screen['elements']:
            if element['type'] == 'menu':
                return element
        return None

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("find_menu_element_in_screen {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


async def make_compaign(bot, compaign):
    print('make_compaign')

    try:

        c = await get_compaign(compaign['id'])
        if not c:
            return

        await update_compaign(compaign['id'], is_done=True, status='in_progress')

        # limit = 100
        # offset = 0
        # offset += limit

        sleep_sec = 0.5
        if compaign['max_mes_per_hour']:
            sleep_sec = (60 * 60) / compaign['max_mes_per_hour']

        users = await get_users(bot, compaign['from_date_signup'], compaign['to_date_signup'])

        for user in users:

            if compaign['activity'] in ['cold', 'active', 'hot']:

                activity = await get_activity(bot, user)

                if compaign['activity'] == 'cold' and activity != 1:
                    continue
                elif compaign['activity'] == 'active' and activity not in [2, 3, 4]:
                    continue
                elif compaign['activity'] == 'hot' and activity < 5:
                    continue

            print(str(user["chat_id"]) + 'send')
            #if user["chat_id"] == "380635275370@c.us":
            await send_message(bot, user, compaign)

            if next_step:
                await update_user(bot['id'], user['chat_id'], step=next_step)

            await asyncio.sleep(sleep_sec)

        await update_compaign(compaign['id'], status='success')

    except Exception as e:

        await update_compaign(compaign['id'], status='error')

        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("make_compaign {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


async def send_message(bot, user, compaign):
    print('send_message')
    try:

        if compaign['file']:
            file_url = f"https://www.whatsbot.online/media{compaign['file']}"
            await send_file_message(bot['api_key'], bot['api_url'], user['chat_id'], file_url, get_filename(file_url))

        if compaign['text']:
            await send_text_message(bot['api_key'], bot['api_url'], user['chat_id'], compaign['text'])

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("compaign send_message {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

try:

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())

    # asyncio.ensure_future(check_compaign(), loop=loop)
    asyncio.ensure_future(check_podpiska(), loop=loop)

    loop.run_forever()

except KeyboardInterrupt:
    pass
finally:
    loop.stop()
    loop.close()

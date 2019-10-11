from aiohttp import ClientSession
import asyncio
from db_utils import *
import os, sys
from aiogram import Bot

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

        await asyncio.sleep(60)


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


async def make_compaign(bot, compaign):
    print('make_compaign')

    try:

        # c = await get_compaign(compaign['id'])
        # if not c:
        #     return

        await update_compaign(compaign['id'], status='in_progress')

        users = await get_users(bot)

        tg_bot = Bot(token=bot['token'])

        for user in users:

            print(str(user["chat_id"]) + 'send')
            #if user["chat_id"] == "380635275370@c.us":
            await send_message(tg_bot, user, compaign)

            # await asyncio.sleep(sleep_sec)

        await update_compaign(compaign['id'], status='success', is_done=True)

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

        if compaign['photo']:
            file_url = f"https://inbot24.ru/media/{compaign['photo']}"
            await bot.send_photo(user['chat_id'], file_url)

        if compaign['video']:
            file_url = f"https://inbot24.ru/media/{compaign['video']}"
            await bot.send_video(user['chat_id'], file_url)

        if compaign['text']:
            await bot.send_message(user['chat_id'], compaign['text'])

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

    asyncio.ensure_future(check_compaign(), loop=loop)
    asyncio.ensure_future(check_podpiska(), loop=loop)

    loop.run_forever()

except KeyboardInterrupt:
    pass
finally:
    loop.stop()
    loop.close()

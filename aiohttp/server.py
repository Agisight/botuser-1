from aiohttp import web, ClientSession
import asyncio
from db_utils import *
#from utils import *
import sys, os
import json
from datetime import datetime, timedelta
from aiogram import Bot, types
import re

import logging
logging.basicConfig(filename="/aiohttp/log.txt", level=logging.ERROR)

import requests

# TODO
# Проверка на зацикленность - вроде все работает
# возращать тип ошибки и сообщение и отпралять в самом конце а не там где она вылазит - это есть
# если ответ сервера не 200 и не ок тогда не переводить на след шаг


def is_digit(string):
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


def get_date_format():
    d = datetime.today()
    return f"{d.day}.{d.month}.{d.year}"



async def send_message(bot, user, mes):

    try:

        tg_bot = Bot(token=bot['token'])

        if mes['type'] == "text":

            if mes['text']:

                keyboard = None
                if 'keyboard' in mes:
                    if mes['keyboard']:
                        buttons = []
                        for button in mes['keyboard']:
                            buttons.append(types.KeyboardButton(text=button))
                        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2)
                        keyboard.add(*buttons)
                    else:
                        keyboard = types.ReplyKeyboardRemove()

                answer_tg_bot = await tg_bot.send_message(user['chat_id'], mes['text'], reply_markup=keyboard)

        elif mes['type'] == "photo":

            if mes['photo']:

                caption = mes['caption'] if mes['caption'] else None
                answer_tg_bot = await tg_bot.send_photo(user['chat_id'], mes['photo'], caption=caption)

        elif mes['type'] == "video":

            if mes['video']:

                caption = mes['caption'] if mes['caption'] else None
                answer_tg_bot = await tg_bot.send_video(user['chat_id'], mes['video'], caption=caption)

        print(answer_tg_bot)

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("send_message {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

    finally:

        await add_mes_log(bot['id'], user['id'], "out", json.dumps(mes), str(answer_tg_bot))


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


def find_element_in_screen(element_id, screen):

    try:

        for element in screen['elements']:
            if str(element['id']) == element_id:
                return element
        return None

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("find_element_in_screen {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


async def handle_next_screen(bot, user, next_screen_id, is_loop_check):
    print("handle_next_screen")
    try:

        data = json.loads(bot['data'])

        new_screen = find_screen(next_screen_id, data)
        if not new_screen:
            mes = {"type": "text", "text": "Ошибка! Нет информации в боте. Для того чтобы вернутся в начало, напишите /start"}
            await send_message(bot, user, mes)
            return None

        if not new_screen['elements']:
            mes = {"type": "text", "text": "Ошибка! Нет информации в боте. Для того чтобы вернутся в начало, напишите /start"}
            await send_message(bot, user, mes)
            return None

        if next_screen_id in is_loop_check:
            mes = {"type": "text", "text": "Ошибка! Бот зациклен. Для того чтобы вернутся в главное меню, напишите /start"}
            await send_message(bot, user, mes)
            return None

        is_loop_check += next_screen_id + "|"

        print(new_screen['elements'])

        for element in new_screen['elements']:

            print(element)

            if element['type'] == 'menu':

                mes = {"type": "text",
                       "text": element['data']['text'],
                       "keyboard": [button['text'] for button in element['data']['value']]}

                await send_message(bot, user, mes)

                return f"{next_screen_id}|{element['id']}"

            elif element['type'] == 'text':

                mes = {"type": "text",
                       "text": element['data']['text']}

                await send_message(bot, user, mes)

            elif element['type'] == 'image':

                mes = {"type": "photo",
                       "photo": element['data']['image'],
                       "caption": element['data']['text']}

                await send_message(bot, user, mes)

            elif element['type'] == 'video':

                mes = {"type": "video",
                       "video": element['data']['video'],
                       "caption": element['data']['text']}

                await send_message(bot, user, mes)

        # return f"{next_screen_id}|{element['id']}"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("handle_next_screen {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


async def handle_next_element(bot, user, screen, element_id, is_loop_check):
    print("handle_next_element")
    try:

        for i, element in enumerate(screen['elements']):
            if element['id'] == element_id:
                break
        else:
            mes = {"type": "text", "text": "Ошибка! Нет информации в боте. Для того чтобы вернутся в начало, напишите /start"}
            await send_message(bot, user, mes)
            return None

        if i >= len(screen['elements']) - 1:
            mes = {"type": "text", "text": "Ошибка! Нет информации в боте. Для того чтобы вернутся в начало, напишите /start"}
            await send_message(bot, user, mes)
            return None

        for element in screen['elements'][i+1:]:

            print(element)

            if element['type'] == 'menu':

                mes = {"type": "text",
                       "text": element['data']['text'],
                       "keyboard": [button['text'] for button in element['data']['value']]}

                await send_message(bot, user, mes)

                return f"{screen['id']}|{element['id']}"

            elif element['type'] == 'text':

                mes = {"type": "text",
                       "text": element['data']['text']}

                await send_message(bot, user, mes)

            elif element['type'] == 'image':

                mes = {"type": "photo",
                       "photo": element['data']['image'],
                       "caption": element['data']['text']}

                await send_message(bot, user, mes)

            elif element['type'] == 'video':

                mes = {"type": "video",
                       "video": element['data']['video'],
                       "caption": element['data']['text']}

                await send_message(bot, user, mes)

        # return f"{screen['id']}|{element['id']}"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("handle_next_element {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


async def handle_current_step(bot, user, update):

    print("handle_current_step")

    try:

        data = json.loads(bot['data'])

        step = user['step'].split('|')
        screen_id = step[0]
        element_id = step[1]

        #is_loop_check = screen_id + "|"
        is_loop_check = ""

        screen = find_screen(screen_id, data)
        # print('screen', screen)
        if not screen:
            mes = {"type": "text", "text": "Ошибка! Нет информации в боте. Для того чтобы вернутся в начало, напишите /start"}
            await send_message(bot, user, mes)
            return None

        element = find_element_in_screen(element_id, screen)
        # print('element', element)
        if not element:
            mes = {"type": "text", "text": "Ошибка! Нет информации в боте. Для того чтобы вернутся в начало, напишите /start"}
            await send_message(bot, user, mes)
            return None

        text = update['message']['text']

        if element['type'] == 'menu':

            for value in element['data']['value']:
                if value['text'] == text:
                #if text.lower() in [x.strip().lower() for x in value['text'].split('|') if x]:
                    next_screen_id = value['id']
                    return await handle_next_screen(bot, user, next_screen_id, is_loop_check)
            else:

                mes = {"type": "text",
                       "text": element['data']['fallback']}
                await send_message(bot, user, mes)

                return None

        elif element['type'] in ['text', 'geo', 'contact', 'image', 'file', 'order']:
            mes = {"type": "text", "text": "Для того чтобы вернутся в начало, напишите /start"}
            await send_message(bot, user, mes)
            return None

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("handle_current_step {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

    # mes = {"type": "text",
    #        "text": "Ошибка! Обратитесь в службу поддержки. Для того чтобы вернутся в начало, напишите /start"}
    # await send_message(bot, user, mes)
    # return None


async def handle_first_message(bot, user):
    print("handle_first_message")
    try:

        data = json.loads(bot['data'])

        if not data:
            mes = {"type": "text", "text": "Ошибка! Бот пустой. Напишите /start"}
            await send_message(bot, user, mes)
            return None

        for column in data:
            if column:
                break
        else:
            mes = {"type": "text", "text": "Ошибка! Бот пустой. Напишите /start"}
            await send_message(bot, user, mes)
            return None

        screen = column[0]

        if not screen['elements']:
            mes = {"type": "text", "text": "Ошибка! Стартовый экран пустой. Исправьте это и напишите /start"}
            await send_message(bot, user, mes)
            return None

        # if screen['elements'][0]['type'] == 'order':
        #     return None, "ERROR", "Ошибка! Элемент Заявка не может стоять первым элементом на стартовом экране. Исправьте это и напишите Старт"
        #
        # if screen['elements'][0]['type'] == 'rewind':
        #     return None, "ERROR", "Ошибка! Элемент Перемотка не может стоять первым элементом на стартовом экране. Исправьте это и напишите Старт"

        is_loop_check = screen['id'] + "|"

        for element in screen['elements']:

            next_step = f"{screen['id']}|{element['id']}"

            if element['type'] == 'menu':

                mes = {"type": "text",
                       "text": element['data']['text'],
                       "keyboard": [button['text'] for button in element['data']['value']]}

                await send_message(bot, user, mes)

                return next_step

            elif element['type'] == 'text':

                mes = {"type": "text",
                       "text": element['data']['text']}

                await send_message(bot, user, mes)

            elif element['type'] == 'image':

                mes = {"type": "photo",
                       "photo": element['data']['image'],
                       "caption": element['data']['text']}

                await send_message(bot, user, mes)

            elif element['type'] == 'video':

                mes = {"type": "video",
                       "video": element['data']['video'],
                       "caption": element['data']['text']}

                await send_message(bot, user, mes)

        # return next_step

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("handle_first_message {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


async def webhook(request):
    try:

        bot_token = request.match_info['bot_token']

        bot = await get_bot(bot_token)

        print(bot)

        # ---- проверка доступа ----

        if not bot['is_active']:
            return web.Response(text="OK")

        if bot['status'] == 'off':
            return web.Response(text="OK")

        # if bot['podpiska_do'] < datetime.today().date():
        #     return web.Response(text="OK")
        #
        # if not bot['is_active']:
        #     return web.Response(text="OK")
        # --------------------------

        update = await request.json()

        print(update)

        text = None
        chat_id = None

        if 'message' in update:

            username = update['message']['from'].get('username')
            first_name = update['message']['from'].get('first_name')
            last_name = update['message']['from'].get('last_name')

            if 'text' in update['message']:
                text = update['message']['text']
                chat_id = update["message"]["chat"]["id"]

            else:
                return web.Response(text="OK")

        else:
            return web.Response(text="OK")

        user = await get_user(bot['id'], chat_id)

        if not user:
            user = await add_user(bot['id'], chat_id, first_name, last_name, username)

        # Логирование вебхука
        await add_mes_log(bot['id'], user['id'], "in", json.dumps(update))

        # if text.lower() in [x.strip().lower() for x in bot['text_start'].split('|') if x]: # == "старт":
        if text.startswith('/start'):

            next_step = await handle_first_message(bot, user)

            if next_step:
                await update_user(bot['id'], chat_id, step=next_step)

        else:

            next_step = await handle_current_step(bot, user, update)

            if next_step:
                await update_user(bot['id'], chat_id, step=next_step)

        return web.Response(text="OK")

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("webhook {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

    return web.Response(text="OK")


loop = asyncio.get_event_loop()

app = web.Application(loop=loop)

app.router.add_post('/bot_webhook/{bot_token}/', webhook)

loop.run_until_complete(init_db())

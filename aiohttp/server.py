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

from dotenv import load_dotenv
load_dotenv('/aiohttp/main_config/.env')
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


def get_filename(s):

    p1 = s.rfind('/')
    if p1 == -1:
        return 'file'

    s_ = s[p1 + 1:]

    p2 = s_.rfind('_')
    if p2 == -1:
        return 'file'

    return s_[p2 + 1:]


async def send_email_message(email, text):

    async with ClientSession() as session:
        url = "https://api:33301cdd392322b4847c77eb1fa54df2-41a2adb4-83773917@api.mailgun.net/v3/whatsbot.online/messages"
        data = {"from": "Whatsbot <notify_order@whatsbot.online>",
                "to": [email],
                "subject": "[Whatsbot] Пришел новый заказ!",
                "text": text}
        async with session.post(url, data=data) as resp:
            ans = str(resp.status) + " " + (await resp.text())
            print(ans)


async def order_notify(bot, user, order_text):

    try:

        if bot['tg_notify']:

            try:
                mes = f"Пришла новая заявка!" \
                      f"\nИмя: {user['name']}" \
                      f"\nТелефон: {user['phone']}" \
                      f"\n\n{order_text}"
                await tg_bot.send_message(int(bot['tg_notify']), mes)
            except:
                pass

        if bot['email_notify']:

            text = f"Имя: {user['name']}" \
                   f"\nТелефон: {user['phone']}" \
                   f"\n\n{order_text}"

            await send_email_message(bot['email_notify'], text)

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("order_notify {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


async def send_message(bot, user, mes):

    try:

        tg_bot = Bot(token=bot['token'])

        if mes['type'] == "text":
            if mes['text']:
                keyboard = mes['keyboard'] if 'keyboard' in mes else None
                answer_tg_bot = await tg_bot.send_message(user['chat_id'], mes['text'], reply_markup=keyboard)
        elif mes['type'] == "photo":
            if mes['photo']:
                caption = mes['caption'] if mes['caption'] else None
                answer_tg_bot = await tg_bot.send_photo(user['chat_id'], mes['photo'], caption=caption)
        elif mes['type'] == "video":
            if mes['video']:
                caption = mes['caption'] if mes['caption'] else None
                answer_tg_bot = await tg_bot.send_video(user['chat_id'], mes['video'], caption=caption)

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("send_message {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

    finally:

        await add_mes_log(bot['id'], user['id'], "out", json.dumps(mes), json.dumps(answer_tg_bot))


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

        for element in new_screen['elements']:

            if element['type'] == 'menu':

                text = element['data']['text']

                if element['data']['value']:
                    buttons = []
                    for button in element['data']['value']:
                        buttons.append(types.KeyboardButton(text=button['text']))
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2)
                    keyboard.add(*buttons)
                else:
                    keyboard = types.ReplyKeyboardRemove()

                mes = {"type": "text",
                       "text": text,
                       "keyboard": keyboard}

                await send_message(bot, user, mes)

                return f"{next_screen_id}|{element['id']}"

            elif element['type'] == 'text':

                text = element['data']['text']
                mes = {"type": "text",
                       "text": text}

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

            # elif element['type'] == 'rewind':
            #
            #     next_screen_id = element['value']
            #     return await handle_next_screen(bot, user, next_screen_id, is_loop_check)
            #
            # elif element['type'] == 'pause':
            #
            #     await asyncio.sleep(element['value'])
            #
            # elif element['type'] == 'input':
            #
            #     mes = element['descr']
            #
            #     if element['variableType'] == 'date':
            #         mes = mes.replace("{format}", get_date_format())
            #     elif element['variableType'] == 'time':
            #         mes = mes.replace("{format}", "15:00")
            #
            #     await send_message(bot, user, mes)
            #
            #     return f"{next_screen_id}|{element['id']}", 'SUCCESS', None

            # elif element['type'] == 'geo':
            #
            #     latitude = element['value']['latitude']
            #     longitude = element['value']['longitude']
            #     address = element['value']['descr']
            #     await send_location(bot, user, latitude, longitude, address)
            #
            # elif element['type'] == 'contact':
            #
            #     contact_id = element['value'] + "@c.us"
            #
            #     await send_contact(bot, user, contact_id)

            # elif element['type'] == 'order':
            #
            #     order_text = element['value']['order']
            #     mes = element['value']['response']
            #
            #     variables = json.loads(user['variables'])
            #     for variable in variables:
            #         order_text = order_text.replace('{' + variable + '}', variables[variable])
            #
            #     await send_message(bot, user, mes)
            #
            #     await create_order(bot['id'], user['id'], order_text)
            #
            #     await order_notify(bot, user, order_text)

        return f"{next_screen_id}|{element['id']}"

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

            if element['type'] == 'menu':

                text = element['data']['text']

                if element['data']['value']:
                    buttons = []
                    for button in element['data']['value']:
                        buttons.append(types.KeyboardButton(text=button['text']))
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2)
                    keyboard.add(*buttons)
                else:
                    keyboard = types.ReplyKeyboardRemove()

                mes = {"type": "text",
                       "text": text,
                       "keyboard": keyboard}

                await send_message(bot, user, mes)

                return f"{screen['id']}|{element['id']}"

            elif element['type'] == 'text':

                text = element['data']['text']
                mes = {"type": "text",
                       "text": text}

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

            # elif element['type'] == 'rewind':
            #
            #     next_screen_id = element['value']
            #     return await handle_next_screen(bot, user, next_screen_id, is_loop_check)
            #
            # elif element['type'] == 'pause':
            #
            #     await asyncio.sleep(element['value'])
            #
            # elif element['type'] == 'input':
            #
            #     mes = element['descr']
            #
            #     if element['variableType'] == 'date':
            #         mes = mes.replace("{format}", get_date_format())
            #     elif element['variableType'] == 'time':
            #         mes = mes.replace("{format}", "15:00")
            #
            #     await send_message(bot, user, mes)
            #
            #     return f"{screen['id']}|{element['id']}", 'SUCCESS', None
            #
            # elif element['type'] == 'geo':
            #
            #     latitude = element['value']['latitude']
            #     longitude = element['value']['longitude']
            #     address = element['value']['descr']
            #     await send_location(bot, user, latitude, longitude, address)
            #
            # elif element['type'] == 'contact':
            #
            #     contact_id = element['value'] + "@c.us"
            #
            #     await send_contact(bot, user, contact_id)
            #
            # elif element['type'] == 'order':
            #
            #     user = await get_user(bot['id'], user['chat_id'])
            #
            #     order_text = element['value']['order']
            #     mes = element['value']['response']
            #
            #     variables = json.loads(user['variables'])
            #     for variable in variables:
            #         order_text = order_text.replace('{' + variable + '}', variables[variable])
            #
            #     await send_message(bot, user, mes)
            #
            #     await create_order(bot['id'], user['id'], order_text)
            #
            #     await order_notify(bot, user, order_text)

        return f"{screen['id']}|{element['id']}"

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
                       "text": element['fallback']}
                await send_message(bot, user, mes)

                return None

        # elif element['type'] == 'rewind':
        #
        #     next_screen_id = element['value']
        #     return await handle_next_screen(bot, user, next_screen_id, is_loop_check)
        #
        # elif element['type'] == 'pause':
        #
        #     await asyncio.sleep(element['value'])
        #
        # elif element['type'] == 'input':
        #
        #     if element['variableType'] == 'string':
        #
        #         pass
        #
        #     elif element['variableType'] == 'number':
        #
        #         if not is_digit(text):
        #
        #             if 'fallback' in element:
        #                 if element['fallback']:
        #                     return user['step'], "SUCCESS", element['fallback']
        #             return user['step'], "SUCCESS", "Введите пожалуйста числовое значение."
        #
        #     elif element['variableType'] == 'date':
        #
        #         d_str = text.replace(' ', '')
        #
        #         try:
        #             datetime.strptime(d_str, '%d.%m.%Y')
        #         except:
        #             if 'fallback' in element:
        #                 if element['fallback']:
        #                     return user['step'], "SUCCESS", element['fallback']
        #             return user['step'], "SUCCESS", f"Введите пожалуйста дату в формате {get_date_format()}"
        #
        #     elif element['variableType'] == 'time':
        #
        #         d_str = text.replace(' ', '')
        #
        #         try:
        #             datetime.strptime(d_str, '%H:%M')
        #         except:
        #             if 'fallback' in element:
        #                 if element['fallback']:
        #                     return user['step'], "SUCCESS", element['fallback']
        #             return user['step'], "SUCCESS", f"Введите пожалуйста время в формате 15:00"
        #
        #     elif element['variableType'] == 'email':
        #
        #         pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        #
        #         if not re.match(pattern, text):
        #
        #             if 'fallback' in element:
        #                 if element['fallback']:
        #                     return user['step'], "SUCCESS", element['fallback']
        #             return user['step'], "SUCCESS", "Введите пожалуйста корректное значение email."
        #
        #     elif element['variableType'] == 'phone':
        #
        #         phone_text = text.replace(' ', '').replace('+', '').replace('-', '').replace('(', '').replace(')', '')
        #
        #         if not is_digit(phone_text) or len(phone_text) < 10:
        #
        #             if 'fallback' in element:
        #                 if element['fallback']:
        #                     return user['step'], "SUCCESS", element['fallback']
        #             return user['step'], "SUCCESS", "Введите пожалуйста корректное значение номера телефона."
        #
        #     variables = json.loads(user['variables'])
        #     variables[element['value']] = text
        #     await update_user(bot['id'], user['chat_id'], variables=json.dumps(variables))
        #
        #     return await handle_next_element(bot, user, screen, element_id, is_loop_check)

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

    mes = {"type": "text",
           "text": "Ошибка! Обратитесь в службу поддержки. Для того чтобы вернутся в начало, напишите /start"}
    await send_message(bot, user, mes)
    return None


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

                text = element['data']['text']

                if element['data']['value']:
                    buttons = []
                    for button in element['data']['value']:
                        buttons.append(types.KeyboardButton(text=button['text']))
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2)
                    keyboard.add(*buttons)
                else:
                    keyboard = types.ReplyKeyboardRemove()

                mes = {"type": "text",
                       "text": text,
                       "keyboard": keyboard}

                await send_message(bot, user, mes)

                return next_step

            elif element['type'] == 'text':

                text = element['data']['text']
                mes = {"type": "text",
                       "text": text}

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

        return next_step

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


async def tg_webhook(request):
    try:

        update = await request.json()

        if 'callback_query' in update:
            chat_id = update["callback_query"]["from"]["id"]
            callback_data = update["callback_query"]["data"]
            message_id = update['callback_query']['message']['message_id']
            text = ''

        elif 'message' in update:

            if 'text' in update['message']:
                text = update['message']['text']
                chat_id = update["message"]["chat"]["id"]
                callback_data = ''

            else:
                return web.Response(text="OK")

        else:
            return web.Response(text="OK")

        await tg_bot.send_message(chat_id, f"Ваш айди для уведомлений: \n{chat_id}")

        return web.Response(text="OK")

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("tg_webhook {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

    return web.Response(text="OK")


loop = asyncio.get_event_loop()

app = web.Application(loop=loop)

app.router.add_post('/bot_webhook/{bot_token}/', webhook)

app.router.add_post('/tg_webhook', tg_webhook)

loop.run_until_complete(init_db())

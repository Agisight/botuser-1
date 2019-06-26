from aiohttp import web, ClientSession
import asyncio
from db_utils import *
#from utils import *
import sys, os
import json
from datetime import datetime, timedelta
from aiogram import Bot
import re
from amocrm_utils import *
from b24_utils import *

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

# {'messages': [{'id': 'false_380635275370@c.us_3EB0B3859E69E9FD6817', 'body': 'Тестовое сообщение', 'fromMe': False, 'author': '380635275370@c.us', 'time': 1541454647, 'chatId': '380635275370@c.us', 'messageNumber': 582, 'type': 'chat', 'senderName': 'Pete'}], 'instanceId': '11625'}


async def handle_next_screen(bot, user, next_screen_id, is_loop_check):
    print("handle_next_screen")
    try:

        data = json.loads(bot['data'])

        new_screen = find_screen(next_screen_id, data)
        if not new_screen:
            return None, "ERROR", "Ошибка! Экран не существует. Для того чтобы вернутся в главное меню, напишите Старт."

        if not new_screen['elements']:
            return None, "ERROR", "Ошибка! Нет Элементов на этом экране. Для того чтобы вернутся в главное меню, напишите Старт."

        if next_screen_id in is_loop_check:
            return None, "ERROR", "Ошибка! Бот зациклен. Для того чтобы вернутся в главное меню, напишите Старт"

        is_loop_check += next_screen_id + "|"

        for element in new_screen['elements']:

            if element['type'] == 'menu':

                mes = element['descr']

                if mes:
                    await send_message(bot, user, mes)

                return f"{next_screen_id}|{element['id']}", 'SUCCESS', None

            elif element['type'] == 'rewind':

                next_screen_id = element['value']
                return await handle_next_screen(bot, user, next_screen_id, is_loop_check)

            elif element['type'] == 'pause':

                await asyncio.sleep(element['value'])

            elif element['type'] == 'input':

                mes = element['descr']

                if element['variableType'] == 'date':
                    mes = mes.replace("{format}", get_date_format())
                elif element['variableType'] == 'time':
                    mes = mes.replace("{format}", "15:00")

                await send_message(bot, user, mes)

                return f"{next_screen_id}|{element['id']}", 'SUCCESS', None

            elif element['type'] == 'text':

                mes = element['value']

                await send_message(bot, user, mes)

            elif element['type'] == 'geo':

                latitude = element['value']['latitude']
                longitude = element['value']['longitude']
                address = element['value']['descr']
                await send_location(bot, user, latitude, longitude, address)

            elif element['type'] == 'contact':

                contact_id = element['value'] + "@c.us"

                await send_contact(bot, user, contact_id)

            elif element['type'] == 'image':

                await send_file(bot, user, element['value'], get_filename(element['value']), element['descr'])

            elif element['type'] == 'file':

                await send_file(bot, user, element['value'], get_filename(element['value']))

            elif element['type'] == 'order':

                order_text = element['value']['order']
                mes = element['value']['response']

                variables = json.loads(user['variables'])
                for variable in variables:
                    order_text = order_text.replace('{' + variable + '}', variables[variable])

                await send_message(bot, user, mes)

                await create_order(bot['id'], user['id'], order_text)

                await order_notify(bot, user, order_text)

        return f"{next_screen_id}|{element['id']}", 'SUCCESS', None

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
            return None, "ERROR", "Ошибка! Элемент на экране не существует. Для того чтобы вернутся в главное меню, напишите Старт"

        if i >= len(screen['elements']) - 1:
            return None, "ERROR", "Ошибка! Элемент на экране не существует. Для того чтобы вернутся в главное меню, напишите Старт"

        for element in screen['elements'][i+1:]:

            if element['type'] == 'menu':

                mes = element['descr']

                if mes:
                    await send_message(bot, user, mes)

                return f"{screen['id']}|{element['id']}", 'SUCCESS', None

            elif element['type'] == 'rewind':

                next_screen_id = element['value']
                return await handle_next_screen(bot, user, next_screen_id, is_loop_check)

            elif element['type'] == 'pause':

                await asyncio.sleep(element['value'])

            elif element['type'] == 'input':

                mes = element['descr']

                if element['variableType'] == 'date':
                    mes = mes.replace("{format}", get_date_format())
                elif element['variableType'] == 'time':
                    mes = mes.replace("{format}", "15:00")

                await send_message(bot, user, mes)

                return f"{screen['id']}|{element['id']}", 'SUCCESS', None

            elif element['type'] == 'text':

                mes = element['value']

                await send_message(bot, user, mes)

            elif element['type'] == 'geo':

                latitude = element['value']['latitude']
                longitude = element['value']['longitude']
                address = element['value']['descr']
                await send_location(bot, user, latitude, longitude, address)

            elif element['type'] == 'contact':

                contact_id = element['value'] + "@c.us"

                await send_contact(bot, user, contact_id)

            elif element['type'] == 'image':

                await send_file(bot, user, element['value'], get_filename(element['value']), element['descr'])

            elif element['type'] == 'file':

                await send_file(bot, user, element['value'], get_filename(element['value']))

            elif element['type'] == 'order':

                user = await get_user(bot['id'], user['chat_id'])

                order_text = element['value']['order']
                mes = element['value']['response']

                variables = json.loads(user['variables'])
                for variable in variables:
                    order_text = order_text.replace('{' + variable + '}', variables[variable])

                await send_message(bot, user, mes)

                await create_order(bot['id'], user['id'], order_text)

                await order_notify(bot, user, order_text)

        return f"{screen['id']}|{element['id']}", 'SUCCESS', None

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("handle_next_element {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


async def handle_current_step(bot, user, text):

    print("handle_current_step")

    try:

        data = json.loads(bot['data'])

        step = user['step'].split('|')
        screen_id = step[0]
        element_id = step[1]

        #is_loop_check = screen_id + "|"
        is_loop_check = ""

        screen = find_screen(screen_id, data)
        print('screen', screen)
        if not screen:
            return None, "ERROR", "Ошибка! Этого экрана уже не существует, Для того чтобы вернутся в главное меню, напишите Старт."

        element = find_element_in_screen(element_id, screen)
        print('element', element)
        if not element:
            return None, "ERROR", "Ошибка! Нет элементов на этом экране. Для того чтобы вернутся в главное меню, напишите Старт."

        if element['type'] == 'menu':

            for value in element['value']:
                #if value['text'] == text:
                if text.lower() in [x.strip().lower() for x in value['text'].split('|') if x]:
                    next_screen_id = value['id']
                    return await handle_next_screen(bot, user, next_screen_id, is_loop_check)
            else:
                if 'fallback' in element:
                    if element['fallback']:
                        return None, "ERROR", element['fallback']
                return None, "ERROR", "Выберите пункт меню из доступных вариантов."

        elif element['type'] == 'rewind':

            next_screen_id = element['value']
            return await handle_next_screen(bot, user, next_screen_id, is_loop_check)

        elif element['type'] == 'pause':

            await asyncio.sleep(element['value'])

        elif element['type'] == 'input':

            if element['variableType'] == 'string':

                pass

            elif element['variableType'] == 'number':

                if not is_digit(text):

                    if 'fallback' in element:
                        if element['fallback']:
                            return user['step'], "SUCCESS", element['fallback']
                    return user['step'], "SUCCESS", "Введите пожалуйста числовое значение."

            elif element['variableType'] == 'date':

                d_str = text.replace(' ', '')

                try:
                    datetime.strptime(d_str, '%d.%m.%Y')
                except:
                    if 'fallback' in element:
                        if element['fallback']:
                            return user['step'], "SUCCESS", element['fallback']
                    return user['step'], "SUCCESS", f"Введите пожалуйста дату в формате {get_date_format()}"

            elif element['variableType'] == 'time':

                d_str = text.replace(' ', '')

                try:
                    datetime.strptime(d_str, '%H:%M')
                except:
                    if 'fallback' in element:
                        if element['fallback']:
                            return user['step'], "SUCCESS", element['fallback']
                    return user['step'], "SUCCESS", f"Введите пожалуйста время в формате 15:00"

            elif element['variableType'] == 'email':

                pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

                if not re.match(pattern, text):

                    if 'fallback' in element:
                        if element['fallback']:
                            return user['step'], "SUCCESS", element['fallback']
                    return user['step'], "SUCCESS", "Введите пожалуйста корректное значение email."

            elif element['variableType'] == 'phone':

                phone_text = text.replace(' ', '').replace('+', '').replace('-', '').replace('(', '').replace(')', '')

                if not is_digit(phone_text) or len(phone_text) < 10:

                    if 'fallback' in element:
                        if element['fallback']:
                            return user['step'], "SUCCESS", element['fallback']
                    return user['step'], "SUCCESS", "Введите пожалуйста корректное значение номера телефона."

            variables = json.loads(user['variables'])
            variables[element['value']] = text
            await update_user(bot['id'], user['chat_id'], variables=json.dumps(variables))

            return await handle_next_element(bot, user, screen, element_id, is_loop_check)

        elif element['type'] == 'text':
            return None, "ERROR", "Для того чтобы вернутся в главное меню, напишите Старт"

        elif element['type'] == 'geo':
            return None, "ERROR", "Для того чтобы вернутся в главное меню, напишите Старт"

        elif element['type'] == 'contact':
            return None, "ERROR", "Для того чтобы вернутся в главное меню, напишите Старт"

        elif element['type'] == 'image':
            return None, "ERROR", "Для того чтобы вернутся в главное меню, напишите Старт"

        elif element['type'] == 'file':
            return None, "ERROR", "Для того чтобы вернутся в главное меню, напишите Старт"

        elif element['type'] == 'order':
            return None, "ERROR", "Для того чтобы вернутся в главное меню, напишите Старт"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("handle_current_step {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

    return None, "ERROR", "Ошибка! Обратитесь в службу поддержки. Для того чтобы вернутся в главное меню, напишите Старт."


async def handle_first_message(bot, user):
    print("handle_first_message")
    try:

        data = json.loads(bot['data'])

        if not data:
            return None, "ERROR", "Ошибка! Бот пустой. Исправьте это и напишите Старт"

        for column in data:
            if column:
                break
        else:
            return None, "ERROR", "Ошибка! Бот пустой. Исправьте это и напишите Старт"

        screen = column[0]

        if not screen['elements']:
            return None, "ERROR", "Ошибка! Стартовый экран пустой. Исправьте это и напишите Старт"

        if screen['elements'][0]['type'] == 'order':
            return None, "ERROR", "Ошибка! Элемент Заявка не может стоять первым элементом на стартовом экране. Исправьте это и напишите Старт"

        if screen['elements'][0]['type'] == 'rewind':
            return None, "ERROR", "Ошибка! Элемент Перемотка не может стоять первым элементом на стартовом экране. Исправьте это и напишите Старт"

        is_loop_check = screen['id'] + "|"

        for element in screen['elements']:

            if element['type'] == 'menu':

                mes = element['descr']

                if mes:
                    await send_message(bot, user, mes)

                return f"{screen['id']}|{element['id']}", "SUCCESS", None

            elif element['type'] == 'rewind':

                next_screen_id = element['value']
                return await handle_next_screen(bot, user, next_screen_id, is_loop_check)

            elif element['type'] == 'pause':

                await asyncio.sleep(element['value'])

            elif element['type'] == 'input':

                mes = element['descr']

                if element['variableType'] == 'date':
                    mes = mes.replace("{format}", get_date_format())
                elif element['variableType'] == 'time':
                    mes = mes.replace("{format}", "15:00")

                await send_message(bot, user, mes)

                return f"{screen}|{element['id']}", "SUCCESS", None

            elif element['type'] == 'text':

                mes = element['value']

                await send_message(bot, user, mes)

            elif element['type'] == 'geo':

                latitude = element['value']['latitude']
                longitude = element['value']['longitude']
                address = element['value']['descr']
                await send_location(bot, user, latitude, longitude, address)

            elif element['type'] == 'contact':

                contact_id = element['value'] + "@c.us"

                await send_contact(bot, user, contact_id)

            elif element['type'] == 'image':

                await send_file(bot, user, element['value'], get_filename(element['value']), element['descr'])

            elif element['type'] == 'file':

                await send_file(bot, user, element['value'], get_filename(element['value']))

            elif element['type'] == 'order':

                order_text = element['value']['order']
                mes = element['value']['response']

                await send_message(bot, user, mes)

                await create_order(bot['id'], user['id'], order_text)

                await order_notify(bot, user, order_text)

        return f"{screen['id']}|{element['id']}", "SUCCESS", None

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("handle_first_message {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


async def webhook(request):
    try:

        bot_id = int(request.match_info['bot_id'])

        bot = await get_bot(bot_id)

        # print(bot)

        # ---- проверка доступа ----
        if bot['podpiska_do'] < datetime.today().date():
            return web.Response(text="OK")

        if not bot['is_active']:
            return web.Response(text="OK")

        if not bot['is_ready_to_use']:
            return web.Response(text="OK")

        if not bot['profile_is_active']:
            return web.Response(text="OK")

        if bot['partner_id']:
            if bot['partner_podpiska_do'] < datetime.today().date():
                return web.Response(text="OK")

            if not bot['partner_is_active']:
                return web.Response(text="OK")
        # --------------------------

        update = await request.json()

        if 'ack' in update:
            return web.Response(text="OK")

        print(update)

        #for message in reversed(update["messages"]):
        for message in update["messages"][0:1]:

            if message["fromMe"]:
                return web.Response(text="OK")

            if "@g.us" in message["chatId"]:
                return web.Response(text="OK")

            if 'senderName' in message:
                name = message['senderName']
            else:
                name = "Имени нет"

            chat_id = message["author"]
            text = message["body"]

            user = await get_user(bot_id, chat_id)

            if not user:

                user = await add_user(bot_id, chat_id, name, chat_id[:-5], None)

                await add_mes_log(bot_id, user['id'], "in", json.dumps(update))

                next_step, status, mes = await handle_first_message(bot, user)

                if next_step:
                    await update_user(bot_id, chat_id, step=next_step)

                if status == "ERROR":
                    await send_message(bot, user, mes)

                # Интеграция CRM
                await amocrm(bot, name, chat_id[:-5])
                await bitrix24(bot, name, chat_id[:-5])

                return web.Response(text="OK")

            # Логирование вебхука #
            await add_mes_log(bot_id, user['id'], "in", json.dumps(update))
            #

            if text.lower() in [x.strip().lower() for x in bot['text_start'].split('|') if x]: # == "старт":

                next_step, status, mes = await handle_first_message(bot, user)

                if status == "ERROR":
                    await send_message(bot, user, mes)
                if next_step:
                    await update_user(bot_id, chat_id, step=next_step)

            else:

                next_step, status, mes = await handle_current_step(bot, user, text)
                if status == "ERROR":
                    await send_message(bot, user, mes)
                if status == "SUCCESS":
                    if mes:
                        await send_message(bot, user, mes)
                if next_step:
                    await update_user(bot_id, chat_id, step=next_step)

        return web.Response(text="OK")

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("webhook {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))
        # await bot.send_message(354691583, "{} {} {} \n {}".format(
        # exc_type, fname, exc_tb.tb_lineno, str(e)))

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


tg_bot = Bot(token=TG_API_TOKEN)

loop = asyncio.get_event_loop()

app = web.Application(loop=loop)

app.router.add_post('/bot_webhook/{bot_id}/', webhook)

app.router.add_post('/tg_webhook', tg_webhook)

loop.run_until_complete(init_db())

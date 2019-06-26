from aiohttp import ClientSession
import sys, os


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

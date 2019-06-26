import requests
import json

def b24_add_contact(domen_b24, b24_access_token, name, phone):

    try:

        metod = "crm.contact.add"

        url = f'https://{domen_b24}/rest/{metod}?FIELDS[NAME]={name}&FIELDS[PHONE][0][VALUE_TYPE]=WORK&FIELDS[PHONE][0][VALUE]={phone}&auth={b24_access_token}'
        print(url)
        r = requests.get(url)

        print(r.text)

        return json.loads(r.text)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("b24_add_contact {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))


def b24_add_lead(domen_b24, b24_access_token, name, phone):

    try:

        # https://blog.budagov.ru/bitrix24-sozdanie-lida-cherez-api/

        metod = "crm.lead.add"

        url = f'https://{domen_b24}/rest/{metod}?FIELDS[TITLE]=Новый лид из WhatsApp&FIELDS[NAME]={name}&FIELDS[STATUS_ID]=NEW&' \
            f'FIELDS[COMMENTS]=Новый лид из WhatsApp' \
            f'FIELDS[PHONE][0][VALUE_TYPE]=WORK&FIELDS[PHONE][0][VALUE]={phone}&auth={b24_access_token}&' \
            f'PARAMS[REGISTER_SONET_EVENT]=Y'
        print(url)
        r = requests.get(url)

        return json.loads(r.text)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("sys.exc_info() : ", sys.exc_info())
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        logging.error("b24_add_contact {} {} {} \n {}".format(exc_type, fname, exc_tb.tb_lineno, str(e)))

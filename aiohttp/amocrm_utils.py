import requests
import json
from time import time


def amocrm_auth(DOMEN, USER_LOGIN, USER_HASH):
    s = requests.Session()
    data = {'USER_LOGIN': USER_LOGIN,
            'USER_HASH': USER_HASH}
    r = s.post(f'https://{DOMEN}/private/api/auth.php', data=data)
    return s


def pipelines(s, id):

    headers = {'Accept': 'application/json'}

    url = 'https://lofthall.amocrm.ru/api/v2/pipelines'

    data = {'id': id}

    r = s.get(url, data=data, headers=headers)

    try:
        r_json = json.loads(r.text)
        print(r_json)
    except:
        return None


def get_contact(s, id):

    headers = {'Accept': 'application/json'}

    url = 'https://lofthall.amocrm.ru/api/v2/contacts'

    data = {'id': id}

    r = s.get(url, data=data, headers=headers)

    try:
        r_json = json.loads(r.text)
        print(r_json)
    except:
        return None


def get_lead(s, id):

    headers = {'Accept': 'application/json'}

    url = 'https://lofthall.amocrm.ru/api/v2/leads'

    data = {'id': id}

    r = s.get(url, data=data, headers=headers)

    try:
        r_json = json.loads(r.text)
        print(r_json)
    except:
        return None


def add_lead(s, DOMEN, contact_id):

    headers = {'Content-Type': 'application/json'}

    url = f'https://{DOMEN}/api/v2/leads'

    lead = {'name': 'Новая заявка из WhatsApp Bot-а',
            'created_at': int(time()),
            'sale': 0,
            'status_id': 1639474,
            # 'custom_fields': [
            #     {
            #       'id': '454117',
            #       'values': [
            #           {'value': '1044821'}
            #       ]
            #     }
            # ]
            }

    if contact_id:
        lead['contacts_id'] = [contact_id]

    data = {'add': [lead]}

    r = s.post(url, json=data, headers=headers)

    try:
        r_json = json.loads(r.text)
        print("add_lead", r_json)
        return r_json['_embedded']['items'][0]['id']
    except:
        return None


def add_note(s, lead_id, text):

    headers = {'Content-Type': 'application/json'}

    url = 'https://lofthall.amocrm.ru/api/v2/notes'

    note = {'element_id': lead_id,
            'element_type': 2,
            'text':  text,
            'note_type': 4
            }

    data = {'add': [note]}

    r = s.post(url, json=data, headers=headers)

    try:
        r_json = json.loads(r.text)
        print("add_note", r_json)
        return r_json['_embedded']['items'][0]['id']
    except:
        return None


def add_contact(s, DOMEN, name, phone):

    headers = {'Content-Type': 'application/json'}

    url = f'https://{DOMEN}/api/v2/contacts'

    contact = {'name': name,
               'created_at': int(time()),
               'custom_fields': [{'id': 501158,
                                  'name': 'Телефон',
                                  'values': [{'value': phone,
                                              'enum': '841252'}
                                             ]
                                  }
                                 ]
               }

    data = {'add': [contact]}

    r = s.post(url, json=data, headers=headers)

    try:
        r_json = json.loads(r.text)
        print("add_contact", r_json)
        return r_json['_embedded']['items'][0]['id']
    except:
        return None

#s = amocrm_auth()
#get_lead(s, 17537293)

#add_lead(s, 36371591)

# contacts_id = add_contact(s, 'тест2', '12345')
# add_lead(s, contacts_id)

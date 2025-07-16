import requests
import json
from dotenv import dotenv_values
# Переписать в ООП, добавить методы - авторизация, проверка сессии, вывод списка заказов на определенную дату от Гермеон, печать предварительных заявок

config = dotenv_values('.env')
url = 'https://api.dellin.ru/v3/auth/session_info.json'

headers = {'accept': 'application/json',
           'Content-Type': 'application/json'
}


data = {"appKey": config['DL_API_TOKEN'],
        "sessionID":"A1975D78-0A48-4D88-8477-DC18999CAB17"
        # "requestID":"55357415"
        }
json_data = json.dumps(data)
response = requests.post(url, headers=headers, data=json_data)

if response.status_code == 200:
    print("Авторизация успешна")
    print(response.text)

else:
    print("Ошибка авторизации")
    print(response)
    exit()